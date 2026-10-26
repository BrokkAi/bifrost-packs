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


class JavaStager:
    _jdk_packages_by_home = {}

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

        stub_dirs = []
        options = test_dir / 'options'
        if options.is_file():
            for raw in re.findall(r'\$\{testdir\}/([^\s:]+)', options.read_text(errors='replace')):
                stub = (test_dir / raw).resolve()
                if stub.is_dir() and stub not in stub_dirs:
                    stub_dirs.append(stub)
        stub_dirs = [p for p in stub_dirs if p.parent == stub_root.resolve()
                     and p.name in coordinates]
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
                dependencies = []
                if stub_sources:
                    dependencies = self._install_stubs(stub_sources, coordinates, cache_dir, fake_home)
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
        return PreparedRoot(target, tuple(p.relative_to(test_dir).as_posix()
                                          for p in files if p.suffix.lower() in ('.java', '.kt')))

    def _install_stubs(self, stub_sources, coordinates, cache_dir, fake_home):
        if self.java_home is None:
            raise ValueError('Java staging requires --java-home or JAVA_HOME')
        java_home = self.java_home.resolve()
        jdk_packages = self._jdk_packages(java_home)
        fingerprint = hashlib.sha256(b'java-stub-compile-v3\0' + str(java_home).encode())
        for package, modules in sorted(jdk_packages.items()):
            fingerprint.update(package.encode() + b'\0')
            fingerprint.update(','.join(sorted(modules)).encode() + b'\0')
        for stub, sources in sorted(stub_sources.items(), key=lambda item: item[0].name):
            fingerprint.update(stub.name.encode() + b'\0')
            for source in sources:
                fingerprint.update(source.relative_to(stub).as_posix().encode() + b'\0')
                fingerprint.update(hashlib.sha256(source.read_bytes()).digest())
        retained_sources, dropped_sources = {}, {}
        package_for_source = {}
        for stub, sources in stub_sources.items():
            retained_sources[stub], dropped_sources[stub] = set(), []
            for source in sources:
                match = re.search(r'^\s*package\s+([\w.]+)\s*;',
                                  source.read_text(errors='replace'), re.M)
                package = match.group(1) if match else ''
                package_for_source[source] = package
                owners = jdk_packages.get(package, ())
                if package == 'java' or package.startswith('java.') or owners:
                    dropped_sources[stub].append((source, package, sorted(owners)))
                else:
                    retained_sources[stub].add(source)
        artifact_cache = cache_dir / 'java-stubs' / fingerprint.hexdigest()
        work, compile_work, classes = (artifact_cache / 'sources',
                                       artifact_cache / 'compile-sources',
                                       artifact_cache / 'classes')
        if not classes.is_dir():
            artifact_cache.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(work, ignore_errors=True)
            shutil.rmtree(compile_work, ignore_errors=True)
            shutil.rmtree(classes, ignore_errors=True)
            work.mkdir()
            compile_work.mkdir()
            classes.mkdir()
            for stub, sources in stub_sources.items():
                for source in sources:
                    destination = work / stub.name / source.relative_to(stub)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                    if source in retained_sources[stub]:
                        compile_destination = compile_work / stub.name / source.relative_to(stub)
                        compile_destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, compile_destination)
            javac = java_home / 'bin' / ('javac.exe' if os.name == 'nt' else 'javac')
            compile_sources = sorted(compile_work.rglob('*.java'))
            attempts = [('-proc:none', '-nowarn', '-encoding', 'UTF-8', '--release', '21')]
            records = []
            records.append('Dropped JDK-owned stub sources:')
            for stub in sorted(dropped_sources, key=lambda path: path.name):
                if not dropped_sources[stub]:
                    records.append(f'  {stub.name}: none')
                for source, package, owners in dropped_sources[stub]:
                    records.append(f"  {stub.name}/{source.relative_to(stub).as_posix()} "
                                   f"package={package or '(default)'} modules={','.join(owners) or 'java.*'}")
            for flags in attempts:
                proc = subprocess.run([str(javac), *flags, '-d', str(classes), *map(str, compile_sources)],
                                      capture_output=True, text=True)
                records.append(f"$ javac {' '.join(flags)}\nexit={proc.returncode}\n{proc.stdout}{proc.stderr}")
                if proc.returncode == 0:
                    break
            (artifact_cache / 'compile.txt').write_text('\n\n'.join(records) + '\n')

        package_roots = {
            stub: {package_for_source[source].replace('.', '/') for source in sources
                   if package_for_source.get(source)}
            for stub, sources in retained_sources.items()
        }
        dependencies = []
        for stub in stub_sources:
            row = coordinates[stub.name]
            group, artifact, version = row['groupId'], row['artifactId'], row['version']
            destination = fake_home / '.m2/repository' / Path(*group.split('.')) / artifact / version
            destination.mkdir(parents=True, exist_ok=True)
            for suffix, base, source_mode in (('.jar', classes, False),
                                              ('-sources.jar', work, True)):
                jar = destination / f'{artifact}-{version}{suffix}'
                fd, temporary_name = tempfile.mkstemp(prefix=f'.{jar.name}.', dir=destination)
                os.close(fd)
                try:
                    with zipfile.ZipFile(temporary_name, 'w', zipfile.ZIP_DEFLATED) as archive:
                        for file in sorted(base.rglob('*.java' if source_mode else '*.class')):
                            relative = file.relative_to(base)
                            if source_mode:
                                if relative.parts[0] != stub.name:
                                    continue
                                relative = Path(*relative.parts[1:])
                            else:
                                if not any(relative.as_posix() == p + '.class'
                                           or relative.as_posix().startswith(p + '/')
                                           for p in package_roots[stub]):
                                    continue
                            archive.write(file, relative.as_posix())
                    os.replace(temporary_name, jar)
                finally:
                    Path(temporary_name).unlink(missing_ok=True)
            pom = ET.Element('project')
            for tag, value in (('modelVersion', '4.0.0'), ('groupId', group),
                               ('artifactId', artifact), ('version', version)):
                ET.SubElement(pom, tag).text = value
            ET.ElementTree(pom).write(destination / f'{artifact}-{version}.pom',
                                      encoding='utf-8', xml_declaration=True)
            dependencies.append((group, artifact, version))
        return dependencies

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
