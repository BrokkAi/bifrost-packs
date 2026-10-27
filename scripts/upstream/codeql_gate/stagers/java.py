"""Stage Java CodeQL tests and their local stub artifacts."""
import csv
import errno
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from . import PreparedRoot
try:
    from ..core import GateError
except ImportError:
    from core import GateError


def _java_tokens(source):
    tokens = []
    index, line, column = 0, 1, 1

    def advance():
        nonlocal index, line, column
        char = source[index]
        index += 1
        if char == '\n':
            line, column = line + 1, 1
        elif char == '\r':
            if index < len(source) and source[index] == '\n':
                index += 1
            line, column = line + 1, 1
        else:
            column += 1
        return char

    while index < len(source):
        char = source[index]
        if char.isspace():
            advance()
            continue
        if source.startswith('//', index):
            while index < len(source) and source[index] not in '\r\n':
                advance()
            continue
        if source.startswith('/*', index):
            advance()
            advance()
            while index < len(source) and not source.startswith('*/', index):
                advance()
            if index < len(source):
                advance()
                advance()
            continue
        if source.startswith('"""', index):
            for _ in range(3):
                advance()
            while index < len(source) and not source.startswith('"""', index):
                if source[index] == '\\' and index + 1 < len(source):
                    advance()
                advance()
            if index < len(source):
                for _ in range(3):
                    advance()
            continue
        if char in ('"', "'"):
            quote = advance()
            while index < len(source):
                current = advance()
                if current == '\\' and index < len(source):
                    advance()
                elif current == quote:
                    break
            continue
        start = (line, column)
        if char.isalpha() or char in '_$':
            value = advance()
            while index < len(source) and (source[index].isalnum() or source[index] in '_$'):
                value += advance()
        elif source.startswith('...', index):
            value = ''.join(advance() for _ in range(3))
        else:
            value = advance()
        tokens.append((value, start, (line, column)))
    return tokens


def _main_string_array_parameter_spans(source):
    tokens = _java_tokens(source)
    spans = []
    for index, token in enumerate(tokens):
        if token[0] != 'main' or index + 1 >= len(tokens) or tokens[index + 1][0] != '(':
            continue
        if index == 0 or tokens[index - 1][0] in ('.', 'return', 'throw', 'new', '=', '->'):
            continue
        if not (tokens[index - 1][0].isidentifier() or tokens[index - 1][0] in (']', '>', '?')):
            continue
        depth, closing = 0, None
        for cursor in range(index + 1, len(tokens)):
            if tokens[cursor][0] == '(':
                depth += 1
            elif tokens[cursor][0] == ')':
                depth -= 1
                if depth == 0:
                    closing = cursor
                    break
        if closing is None or closing + 1 >= len(tokens):
            continue
        if tokens[closing + 1][0] not in ('{', ';', 'throws'):
            continue
        parameter = tokens[index + 2:closing]
        if not parameter or any(item[0] == ',' for item in parameter):
            continue
        parameter_start = parameter[0][1]
        if parameter[0][0] == 'final':
            parameter = parameter[1:]
        values = [item[0] for item in parameter]
        if values[:5] == ['java', '.', 'lang', '.', 'String']:
            type_tokens = 5
        elif values and values[0] == 'String':
            type_tokens = 1
        else:
            continue
        rest = values[type_tokens:]
        is_array = (len(rest) == 3 and rest[:2] == ['[', ']']
                    and parameter[-1][0].isidentifier())
        is_varargs = (len(rest) == 2 and rest[0] == '...'
                      and parameter[-1][0].isidentifier())
        is_postfix_array = (len(rest) == 3 and rest[0].isidentifier()
                            and rest[1:] == ['[', ']'])
        if is_array or is_varargs or is_postfix_array:
            spans.append((parameter_start, parameter[-1][2]))
    return spans


def _java_imports(source):
    tokens = _java_tokens(source)
    imports = []
    index = 0
    while index < len(tokens):
        if tokens[index][0] != 'import':
            index += 1
            continue
        index += 1
        if index < len(tokens) and tokens[index][0] == 'static':
            index += 1
        values = []
        while index < len(tokens) and tokens[index][0] != ';':
            values.append(tokens[index][0])
            index += 1
        if index < len(tokens):
            imports.append(''.join(values))
        index += 1
    return imports


_JAVA_KEYWORDS = frozenset('abstract assert boolean break byte case catch char class const continue '
                           'default do double else enum extends final finally float for goto if '
                           'implements import instanceof int interface long native new package '
                           'private protected public return short static strictfp super switch '
                           'synchronized this throw throws transient try void volatile while '
                           'true false null _'.split())


def _valid_java_identifier(value):
    return value not in _JAVA_KEYWORDS and value.replace('$', 'a').isidentifier()


class JavaStager:
    # Class locations are pinned to CodeQL ae741615f3e178ce61289a651790dc67fcc18e19.
    # Keep this list limited to QL endpoints reviewed for catalog-only recall.
    ql_endpoints = (
        dict(id='spring-servlet-input-parameter', ql_class='SpringServletInputParameterSource',
             ql_module='semmle.code.java.dataflow.FlowSources',
             file='java/ql/lib/semmle/code/java/dataflow/FlowSources.qll',
             start_line=142, end_line=148, role='source',
             description='Spring request-mapping parameter source.'),
        dict(id='micronaut-http-input-parameter', ql_class='MicronautHttpInputParameterSource',
             ql_module='semmle.code.java.dataflow.FlowSources',
             file='java/ql/lib/semmle/code/java/dataflow/FlowSources.qll',
             start_line=184, end_line=190, role='source',
             description='Micronaut request parameter source.'),
        dict(id='spring-resttemplate-uri-variable', ql_class='SpringWebClientRestTemplateUriVariable',
             ql_module='semmle.code.java.frameworks.spring.SpringWebClient',
             file='java/ql/lib/semmle/code/java/frameworks/spring/SpringWebClient.qll',
             start_line=70, end_line=106, role='sink',
             description='Spring RestTemplate URI-variable sink.'),
        dict(id='dom4j-xpath-constructor', ql_class='DefaultXPathInjectionSink',
             ql_module='semmle.code.java.security.XPath',
             file='java/ql/lib/semmle/code/java/security/XPath.qll',
             start_line=17, end_line=28, role='sink',
             description='DefaultXPathInjectionSink, dom4j constructor branch. The sinkNode(this, "xpath-injection") branch is ordinary models-as-data and remains in scope as a printed MaD row.'),
    )

    @staticmethod
    def model_in_catalog(row, catalogs):
        # Exact printed rows preserve this language's signatures and access paths.
        return row in catalogs

    _jdk_packages_by_home = {}

    @classmethod
    def validate_ql_endpoints(cls, codeql_root):
        root = Path(codeql_root)
        for endpoint in cls.ql_endpoints:
            path = root / endpoint['file']
            if not path.is_file():
                raise GateError(f"QL endpoint allow-list file is missing: {endpoint['file']}")
            lines = path.read_text(errors='replace').splitlines()
            selected = lines[endpoint['start_line'] - 1:endpoint['end_line']]
            pattern = re.compile(r'\bclass\s+' + re.escape(endpoint['ql_class']) + r'\b')
            if not pattern.search('\n'.join(selected)):
                raise GateError(f"QL endpoint allow-list mismatch: {endpoint['id']} "
                                f"({endpoint['file']}:{endpoint['start_line']}-{endpoint['end_line']})")

    @staticmethod
    def is_main_string_array_parameter(test_dir, node):
        root = Path(test_dir).resolve()
        source = (root / node['path']).resolve()
        if not source.is_relative_to(root) or not source.is_file() or source.suffix != '.java':
            return False
        node_start = (node['line'], node['column'])
        node_end = (node.get('end_line', node['line']), node.get('end_column', node['column']))
        return any(start <= node_start <= end or node_start <= start <= node_end
                   for start, end in _main_string_array_parameter_spans(
                       source.read_text(errors='replace')))

    def __init__(self, java_home=None):
        raw_java_home = java_home or os.environ.get('JAVA_HOME')
        self.java_home = Path(raw_java_home).expanduser() if raw_java_home else None

    def prepare(self, test_dir, codeql_root, cache_dir):
        test_dir, codeql_root, cache_dir = Path(test_dir), Path(codeql_root), Path(cache_dir)
        stub_root = codeql_root / 'java/ql/test/stubs'
        coordinate_file = Path(__file__).with_name('java_stub_coordinates.tsv')
        with coordinate_file.open(newline='') as stream:
            coordinates = {row['stub_dir']: row for row in csv.DictReader(stream, delimiter='\t')}

        files = sorted(p for p in test_dir.rglob('*') if p.is_file()
                       and p.suffix not in ('.expected', '.qlref', '.ql')
                       and p.name != 'options')
        digest = hashlib.sha256(b'java-stager-v3\0' + str(test_dir.resolve()).encode())
        if self.java_home is not None:
            digest.update(str(self.java_home.resolve()).encode() + b'\0')
        for path in files:
            digest.update(path.relative_to(test_dir).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())

        stub_dirs = self._option_stub_dirs(test_dir, stub_root, coordinates)
        stub_sources = {stub: sorted(stub.rglob('*.java')) for stub in stub_dirs}
        stub_sources = {stub: sources for stub, sources in stub_sources.items() if sources}
        for stub, sources in stub_sources.items():
            digest.update(stub.name.encode() + b'\0')
            for source in sources:
                digest.update(source.relative_to(stub).as_posix().encode() + b'\0')
                digest.update(hashlib.sha256(source.read_bytes()).digest())
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / digest.hexdigest()
        fake_home = cache_dir / 'maven-home'
        if not target.exists():
            temporary = Path(tempfile.mkdtemp(prefix='.prepare-', dir=cache_dir))
            try:
                for path in files:
                    dest = temporary / path.relative_to(test_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)
                dependencies = [(coordinates[stub.name]['groupId'],
                                 coordinates[stub.name]['artifactId'],
                                 coordinates[stub.name]['version']) for stub in stub_sources]
                project = ET.Element('project')
                for tag, value in (('modelVersion', '4.0.0'), ('groupId', 'codeql.test'),
                                   ('artifactId', re.sub(r'[^A-Za-z0-9_.-]+', '-', test_dir.name).strip('-')),
                                   ('version', '1.0')):
                    ET.SubElement(project, tag).text = value
                deps = ET.SubElement(project, 'dependencies')
                for group, artifact, version in dependencies:
                    dep = ET.SubElement(deps, 'dependency')
                    for tag, value in (('groupId', group), ('artifactId', artifact),
                                       ('version', version), ('scope', 'compile')):
                        ET.SubElement(dep, tag).text = value
                ET.ElementTree(project).write(temporary / 'pom.xml', encoding='utf-8',
                                               xml_declaration=True)
                try:
                    temporary.rename(target)
                except OSError as exc:
                    if exc.errno not in (errno.EEXIST, errno.ENOTEMPTY) or not target.is_dir():
                        raise
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        # Artifact installation is deliberately checked on every call: a prepared-root
        # cache hit must not hide a partially cleaned fake Maven repository.
        if stub_sources:
            statuses = self._install_stubs(stub_sources, coordinates, cache_dir, fake_home, files, stub_root)
        else:
            statuses = {}
        if target.exists() and stub_sources:
            pom_path = target / 'pom.xml'
            pom = ET.parse(pom_path)
            project = pom.getroot()
            deps = project.find('dependencies')
            known = {(dep.findtext('groupId'), dep.findtext('artifactId'), dep.findtext('version'))
                     for dep in deps.findall('dependency')}
            for stub in stub_sources:
                row = coordinates[stub.name]
                coord = (row['groupId'], row['artifactId'], row['version'])
                if coord in known:
                    continue
                dep = ET.SubElement(deps, 'dependency')
                for tag, value in (('groupId', coord[0]), ('artifactId', coord[1]),
                                   ('version', coord[2]), ('scope', 'compile')):
                    ET.SubElement(dep, tag).text = value
            pom.write(pom_path, encoding='utf-8', xml_declaration=True)
        staged = tuple({key: row[key] for key in
                        ('groupId', 'artifactId', 'version', 'confidence', 'evidence')} |
                       {'stub_dir': stub.name} | statuses.get(stub, {'staging_status': 'no-sources'})
                       for stub in stub_sources for row in (coordinates[stub.name],))
        return PreparedRoot(target, tuple(p.relative_to(test_dir).as_posix()
                                          for p in files if p.suffix.lower() in ('.java', '.kt')),
                            staged)

    def _option_stub_dirs(self, test_dir, stub_root, coordinates):
        options = test_dir / 'options'
        if not options.is_file():
            return []
        dirs = []
        for raw in re.findall(r'\$\{testdir\}/([^\s:]+)', options.read_text(errors='replace')):
            stub = (test_dir / raw).resolve()
            if stub.parent != stub_root.resolve():
                continue
            if stub.name not in coordinates:
                raise GateError(f'no Java stub coordinate mapping for {stub.name}')
            if stub.is_dir() and stub not in dirs:
                dirs.append(stub)
        return dirs

    @staticmethod
    def _is_jdk_package(package, jdk_packages):
        return package in jdk_packages

    @staticmethod
    def _jar_files(base, stub_name, source_mode, package_roots):
        for file in sorted(base.rglob('*.java' if source_mode else '*.class')):
            relative = file.relative_to(base)
            if source_mode:
                if relative.parts[0] != stub_name:
                    continue
                relative = Path(*relative.parts[1:])
            elif not any(relative.as_posix() == package + '.class'
                         or relative.as_posix().startswith(package + '/')
                         for package in package_roots):
                continue
            yield file, relative

    def _install_stubs(self, stub_sources, coordinates, cache_dir, fake_home, test_files, stub_root):
        if self.java_home is None:
            raise ValueError('Java staging requires --java-home or JAVA_HOME')
        java_home = self.java_home.resolve()
        jdk_packages = self._jdk_packages(java_home)
        fingerprint = hashlib.sha256(b'java-stub-compile-v5\0' + str(java_home).encode())
        for package, modules in sorted(jdk_packages.items()):
            fingerprint.update(package.encode() + b'\0')
            fingerprint.update(','.join(sorted(modules)).encode() + b'\0')
        all_stub_sources = {root: sorted(root.rglob('*.java')) for root in sorted(stub_root.iterdir())
                            if root.is_dir()}
        package_roots = {}
        declared_package = {}
        for root, sources in all_stub_sources.items():
            for source in sources:
                match = re.search(r'^\s*package\s+([\w.]+)\s*;',
                                  source.read_text(errors='replace'), re.M)
                package = match.group(1) if match else ''
                declared_package[source] = package
                fingerprint.update(root.name.encode() + b'\0')
                fingerprint.update(source.relative_to(root).as_posix().encode() + b'\0')
                fingerprint.update(hashlib.sha256(source.read_bytes()).digest())
                if (package and _valid_java_identifier(source.stem)
                        and not self._is_jdk_package(package, jdk_packages)):
                    package_roots.setdefault(package, []).append(root)

        selected, package_for_source, dropped_jdk = {}, {}, {}
        duplicates, misplaced, skipped = [], [], []
        first_source_by_type = {}
        packages_by_stub = {}
        for stub, sources in list(stub_sources.items()):
            selected[stub], dropped_jdk[stub], packages_by_stub[stub] = [], [], set()
            for source in sources:
                relative = source.relative_to(stub)
                path_package = '.'.join(relative.parent.parts) if relative.parent.parts else ''
                package = declared_package[source]
                package_for_source[source] = package
                if not _valid_java_identifier(source.stem):
                    skipped.append((stub, source, 'file stem is not a valid Java identifier'))
                    continue
                type_name = '.'.join(part for part in (package, source.stem) if part)
                if package != path_package:
                    misplaced.append((stub, source, path_package, package))
                if self._is_jdk_package(package, jdk_packages):
                    dropped_jdk[stub].append((source, package, sorted(jdk_packages[package])))
                    continue
                previous = first_source_by_type.get(type_name)
                if previous:
                    duplicates.append((type_name, previous[0], previous[1], stub, source))
                    continue
                first_source_by_type[type_name] = (stub, source)
                selected[stub].append(source)
                if package:
                    packages_by_stub[stub].add(package)

        auxiliary_triggers = {}

        def add_auxiliary_root(root, package, triggering_diagnostic):
            if root in stub_sources:
                return False
            if root.name not in coordinates:
                raise GateError(f'no Java stub coordinate mapping for auxiliary root {root.name}')
            sources = all_stub_sources[root]
            stub_sources[root] = sources
            selected[root], dropped_jdk[root], packages_by_stub[root] = [], [], set()
            auxiliary_triggers[root] = (package, triggering_diagnostic)
            for source in sources:
                relative = source.relative_to(root)
                path_package = '.'.join(relative.parent.parts) if relative.parent.parts else ''
                declared = declared_package[source]
                package_for_source[source] = declared
                if not _valid_java_identifier(source.stem):
                    skipped.append((root, source, 'file stem is not a valid Java identifier'))
                    continue
                if declared != path_package:
                    misplaced.append((root, source, path_package, declared))
                if self._is_jdk_package(declared, jdk_packages):
                    dropped_jdk[root].append((source, declared, sorted(jdk_packages[declared])))
                    continue
                type_name = '.'.join(part for part in (declared, source.stem) if part)
                previous = first_source_by_type.get(type_name)
                if previous:
                    duplicates.append((type_name, previous[0], previous[1], root, source))
                    continue
                first_source_by_type[type_name] = (root, source)
                selected[root].append(source)
                if declared:
                    packages_by_stub[root].add(declared)
            return True

        artifact_cache = cache_dir / 'java-stubs' / fingerprint.hexdigest()
        work = artifact_cache / 'sources'
        compile_work = artifact_cache / 'compile-sources'
        class_root = artifact_cache / 'classes'
        artifact_cache.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(compile_work, ignore_errors=True)
        shutil.rmtree(class_root, ignore_errors=True)
        work.mkdir()
        compile_work.mkdir()
        class_root.mkdir()
        for stub, sources in stub_sources.items():
            for source in sources:
                destination = work / stub.name / source.relative_to(stub)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            for source in selected[stub]:
                destination = compile_work / stub.name / source.relative_to(stub)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

        javac = java_home / 'bin' / ('javac.exe' if os.name == 'nt' else 'javac')
        flags = ('-proc:none', '-nowarn', '-encoding', 'UTF-8', '--release', '21')
        coordinate_dirs = {}
        built, unstaged, diagnostics, compile_records = set(), set(), {}, []
        pending = list(stub_sources)
        while pending:
            next_pending = []
            built_this_pass = []
            added_auxiliary = []
            for stub in pending:
                sources = selected[stub]
                output = class_root / stub.name
                shutil.rmtree(output, ignore_errors=True)
                output.mkdir(parents=True)
                command = [str(javac), *flags]
                built_classpath = [str(coordinate_dirs[ready]) for ready in stub_sources if ready in built]
                if built_classpath:
                    command.extend(('-classpath', os.pathsep.join(built_classpath)))
                command.extend(('-d', str(output)))
                command.extend(str(compile_work / stub.name / source.relative_to(stub))
                               for source in sources)
                if sources:
                    proc = subprocess.run(command, capture_output=True, text=True)
                    output_text = proc.stdout + proc.stderr
                    compile_records.append(f"{stub.name}: javac exit={proc.returncode}\n{output_text}")
                    if proc.returncode:
                        next_pending.append(stub)
                        diagnostics[stub] = next((line.strip() for line in output_text.splitlines()
                                                  if ' error:' in line),
                                                 next((line.strip() for line in output_text.splitlines()
                                                       if line.strip()),
                                                      'javac failed without diagnostics'))
                        shutil.rmtree(output, ignore_errors=True)
                        for package in sorted(set(re.findall(
                                r'package ([\w.$]+) does not exist', output_text))):
                            if any(package in packages_by_stub[auxiliary]
                                   for auxiliary in auxiliary_triggers):
                                continue
                            candidates = [candidate for candidate in package_roots.get(package, ())
                                          if candidate not in stub_sources]
                            if not candidates:
                                continue
                            candidate = min(candidates,
                                            key=lambda path: (len(all_stub_sources[path]), path.name))
                            matching_diagnostic = next(
                                (line.strip() for line in output_text.splitlines()
                                 if f'package {package} does not exist' in line), diagnostics[stub])
                            if add_auxiliary_root(candidate, package, matching_diagnostic):
                                added_auxiliary.append(candidate)
                                for source in all_stub_sources[candidate]:
                                    destination = work / candidate.name / source.relative_to(candidate)
                                    destination.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(source, destination)
                                for source in selected[candidate]:
                                    destination = compile_work / candidate.name / source.relative_to(candidate)
                                    destination.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(source, destination)
                        continue
                    diagnostics.pop(stub, None)
                built.add(stub)
                built_this_pass.append(stub)
                coordinate_dirs[stub] = output
                row = coordinates[stub.name]
                coordinate_dir = (fake_home / '.m2/repository' /
                                  Path(*row['groupId'].split('.')) / row['artifactId'] / row['version'])
                coordinate_dir.mkdir(parents=True, exist_ok=True)
                jar = coordinate_dir / f"{row['artifactId']}-{row['version']}.jar"
                with zipfile.ZipFile(jar, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for file in sorted(output.rglob('*.class')):
                        archive.write(file, file.relative_to(output).as_posix())
                expected = {
                    '/'.join(part for part in (package_for_source[source].replace('.', '/'),
                                               source.stem + '.class') if part)
                    for source in sources
                }
                with zipfile.ZipFile(jar) as archive:
                    missing = sorted(expected - set(archive.namelist()))
                if missing:
                    jar.unlink(missing_ok=True)
                    jar.with_name(jar.name + '.fingerprint').unlink(missing_ok=True)
                    raise GateError(f'Java stub binary jar is missing expected classes for {stub.name}: {missing}')
                stamp = jar.with_name(jar.name + '.fingerprint')
                stamp.write_text(fingerprint.hexdigest() + '\n')
                coordinate_dirs[stub] = jar
            if not built_this_pass and not added_auxiliary:
                unstaged.update(next_pending)
                break
            pending = added_auxiliary + next_pending

        for stub in unstaged:
            row = coordinates[stub.name]
            coordinate_dir = (fake_home / '.m2/repository' /
                              Path(*row['groupId'].split('.')) / row['artifactId'] / row['version'])
            for suffix in ('.jar', '.jar.fingerprint'):
                (coordinate_dir / f"{row['artifactId']}-{row['version']}{suffix}").unlink(missing_ok=True)

        # Sources jars and Maven metadata remain available for every selected coordinate.
        statuses = {}
        for stub in stub_sources:
            row = coordinates[stub.name]
            group, artifact, version = row['groupId'], row['artifactId'], row['version']
            coordinate_dir = (fake_home / '.m2/repository' /
                              Path(*group.split('.')) / artifact / version)
            coordinate_dir.mkdir(parents=True, exist_ok=True)
            sources_jar = coordinate_dir / f'{artifact}-{version}-sources.jar'
            with zipfile.ZipFile(sources_jar, 'w', zipfile.ZIP_DEFLATED) as archive:
                for file, relative in self._jar_files(work, stub.name, True, ()):
                    archive.write(file, relative.as_posix())
            pom_path = coordinate_dir / f'{artifact}-{version}.pom'
            if not pom_path.is_file():
                pom = ET.Element('project')
                for tag, value in (('modelVersion', '4.0.0'), ('groupId', group),
                                   ('artifactId', artifact), ('version', version)):
                    ET.SubElement(pom, tag).text = value
                ET.ElementTree(pom).write(pom_path, encoding='utf-8', xml_declaration=True)
            statuses[stub] = {'staging_status': 'built' if stub in built else 'unstaged',
                              'staging_kind': 'auxiliary' if stub in auxiliary_triggers else 'options'}
            if stub in unstaged:
                statuses[stub]['staging_diagnostic'] = diagnostics[stub]
            if stub in auxiliary_triggers:
                package, diagnostic = auxiliary_triggers[stub]
                statuses[stub]['auxiliary_package'] = package
                statuses[stub]['auxiliary_trigger'] = diagnostic

        records = ['Dropped JDK-owned stub sources:']
        records.extend(f"  {stub.name}/{source.relative_to(stub).as_posix()} package={package or '(default)'} "
                       f"modules={','.join(owners)}"
                       for stub, rows in dropped_jdk.items() for source, package, owners in rows)
        records.append('Dropped duplicate stub types:')
        records.extend(f"  {name}: kept {first_stub.name}/{first_source.relative_to(first_stub).as_posix()}; "
                       f"dropped {stub.name}/{source.relative_to(stub).as_posix()}"
                       for name, first_stub, first_source, stub, source in duplicates)
        records.append('Sources whose package path disagrees with declaration:')
        records.extend(f"  {stub.name}/{source.relative_to(stub).as_posix()} path={path_package or '(default)'} "
                       f"declared={package or '(default)'}"
                       for stub, source, path_package, package in misplaced)
        records.append('Skipped sources with invalid Java file stems:')
        records.extend(f"  {stub.name}/{source.relative_to(stub).as_posix()}: {reason}"
                       for stub, source, reason in skipped)
        records.append('Auxiliary roots:')
        records.extend(f"  {stub.name}: package {package}; triggered by {diagnostic}"
                       for stub, (package, diagnostic) in auxiliary_triggers.items())
        records.extend(compile_records)
        records.extend(f"UNSTAGED {stub.name}: {diagnostics[stub]}" for stub in stub_sources if stub in unstaged)
        (artifact_cache / 'compile.txt').write_text('\n\n'.join(records) + '\n')

        unstaged_packages = set().union(*(packages_by_stub[stub] for stub in unstaged)) if unstaged else set()
        built_packages = set().union(*(packages_by_stub[stub] for stub in built)) if built else set()
        unavailable = unstaged_packages - built_packages
        import_errors = []
        for test_file in test_files:
            if test_file.suffix != '.java':
                continue
            for imported in _java_imports(test_file.read_text(errors='replace')):
                for package in sorted(unavailable, key=len, reverse=True):
                    if imported == package or imported.startswith(package + '.'):
                        owners = [stub.name for stub in stub_sources if stub in unstaged
                                  and package in packages_by_stub[stub]]
                        import_errors.append(f"{test_file.name}: import {imported} from unstaged stub roots {owners}")
                        break
        if import_errors:
            raise GateError('Java test imports packages available only from unstaged stubs:\n' +
                            '\n'.join(import_errors))
        return statuses

    def _jdk_packages(self, java_home):
        cache_key = str(java_home)
        if cache_key not in self._jdk_packages_by_home:
            java = java_home / 'bin' / ('java.exe' if os.name == 'nt' else 'java')
            jimage = java_home / 'bin' / ('jimage.exe' if os.name == 'nt' else 'jimage')
            modules = subprocess.run([str(java), '--list-modules'], check=True,
                                     capture_output=True, text=True).stdout
            module_names = {line.split('@', 1)[0] for line in modules.splitlines() if line.strip()}
            image = subprocess.run([str(jimage), 'list', str(java_home / 'lib/modules')], check=True,
                                   capture_output=True, text=True).stdout
            packages = {}
            current_module = None
            for line in image.splitlines():
                module_match = re.fullmatch(r'Module: ([^\s]+)', line.strip())
                if module_match:
                    current_module = module_match.group(1)
                    if current_module not in module_names:
                        raise ValueError(f'JDK image module is absent from --list-modules: {current_module}')
                    continue
                entry = line.strip()
                if current_module and entry.endswith('.class') and '/' in entry:
                    package = entry.rsplit('/', 1)[0].replace('/', '.')
                    packages.setdefault(package, set()).add(current_module)
            self._jdk_packages_by_home[cache_key] = packages
        return self._jdk_packages_by_home[cache_key]

    def run_env(self, run_dir, prepared):
        if self.java_home is None or not self.java_home.is_dir():
            raise ValueError('Java staging requires --java-home or JAVA_HOME')
        fake_home = prepared.root.parent / 'maven-home'
        return {'HOME': str(fake_home), 'USERPROFILE': str(fake_home),
                'JAVA_HOME': str(self.java_home), 'BIFROST_OPEN_PACKS_DISABLE': '1'}

    def extra_policy_files(self, prepared):
        return []
