"""Restore real .NET projects for C# CodeQL tests; never inject stub sources."""
import errno
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from . import PreparedRoot
try:
    from core import GateError, add_inline_expectations
except ImportError:
    from ..core import GateError, add_inline_expectations


class CSharpStager:
    @staticmethod
    def model_in_catalog(row, catalogs):
        # Exact printed rows preserve this language's signatures and access paths.
        return row in catalogs

    def __init__(self, dotnet_root, nuget_packages, nuget_source):
        self.dotnet_root = Path(dotnet_root).resolve() if dotnet_root else None
        self.nuget_packages = Path(nuget_packages).resolve()
        self.nuget_source = nuget_source
        self._sdk_info = None

    def _environment(self, cache_dir):
        home = cache_dir / 'dotnet-home'
        home.mkdir(parents=True, exist_ok=True)
        return dict(os.environ, DOTNET_ROOT=str(self.dotnet_root), HOME=str(home),
                    USERPROFILE=str(home), DOTNET_CLI_HOME=str(home),
                    DOTNET_NOLOGO='1', DOTNET_CLI_TELEMETRY_OPTOUT='1',
                    DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1',
                    NUGET_PACKAGES=str(self.nuget_packages),
                    PATH=str(self.dotnet_root) + os.pathsep + os.environ.get('PATH', ''))

    def _sdk(self, cache_dir):
        if self._sdk_info is not None:
            return self._sdk_info
        dotnet = self.dotnet_root / ('dotnet.exe' if os.name == 'nt' else 'dotnet') if self.dotnet_root else None
        if dotnet is None or not dotnet.is_file():
            raise GateError('C# staging requires --dotnet-root with an SDK targeting net10.0')
        proc = subprocess.run([str(dotnet), '--version'], cwd=self.dotnet_root,
                              env=self._environment(cache_dir), capture_output=True, text=True)
        if proc.returncode:
            raise GateError(f'cannot select .NET SDK: {proc.stdout}{proc.stderr}')
        version = proc.stdout.strip()
        props = self.dotnet_root / 'sdk' / version / 'Microsoft.NETCoreSdk.BundledVersions.props'
        if not props.is_file():
            raise GateError(f'SDK {version} has no bundled targeting-pack metadata')
        frameworks = {}
        for entry in ET.parse(props).getroot().iter('KnownFrameworkReference'):
            if entry.get('TargetFramework') == 'net10.0':
                frameworks[entry.get('Include')] = (entry.get('TargetingPackName'),
                                                    entry.get('TargetingPackVersion'))
        if 'Microsoft.NETCore.App' not in frameworks:
            raise GateError(f'SDK {version} cannot target net10.0')
        self._sdk_info = dotnet, version, frameworks
        return self._sdk_info

    @staticmethod
    def _options(test_dir, codeql_root):
        options = test_dir / 'options'
        tokens = [token for line in options.read_text().splitlines()
                  if line.startswith('semmle-extractor-options:')
                  for token in line.partition(':')[2].split()] if options.is_file() else []
        stubs = (codeql_root / 'csharp/ql/test/resources/stubs').resolve()
        artifacts = []
        for token in tokens:
            if token in ('/nostdlib', '/noconfig', '--standalone'):
                artifacts.append(dict(token=token, kind='flag', id=token, version=None, status='found'))
                continue
            if token.startswith('/r:') and token.endswith('.dll'):
                artifacts.append(dict(token=token, kind='reference', id=token[3:],
                                      version=None, status='not_found'))
                continue
            project = token.startswith('--load-sources-from-project:')
            value = token.partition(':')[2] if project else token
            path = Path(value.replace('${testdir}', str(test_dir)))
            if not path.is_absolute():
                path = test_dir / path
            path = path.resolve()
            if project and path.is_relative_to(stubs):
                parts = path.relative_to(stubs).parts
                if len(parts) == 3 and parts[0] == '_frameworks' and parts[1] in (
                        'Microsoft.NETCore.App', 'Microsoft.AspNetCore.App') and parts[2] == parts[1] + '.csproj':
                    artifact = dict(token=token, kind='framework', id=parts[1], version=None, status='restored')
                elif len(parts) == 3 and parts[0] != '_frameworks' and parts[2] == parts[0] + '.csproj':
                    artifact = dict(token=token, kind='package', id=parts[0], version=parts[1], status='restored')
                else:
                    raise GateError(f'unrecognized C# option token: {token}')
            elif not project and path.suffix == '.cs' and path.is_relative_to(codeql_root):
                artifact = dict(token=token, kind='stub-package', id='CodeQL.Stub.' + path.stem,
                                version=None, status='restored', stub_path=path)
            else:
                raise GateError(f'unrecognized C# option token: {token}')
            if not path.is_file():
                raise GateError(f'C# option token names a missing file: {token}')
            artifacts.append(artifact)
        return tokens, artifacts

    @staticmethod
    def _project(path, references, assembly=None, version=None):
        project = ET.Element('Project', Sdk='Microsoft.NET.Sdk')
        props = ET.SubElement(project, 'PropertyGroup')
        for key, value in [('TargetFramework', 'net10.0'), ('AllowUnsafeBlocks', 'true'),
                           ('ImplicitUsings', 'disable'), ('TreatWarningsAsErrors', 'false')]:
            ET.SubElement(props, key).text = value
        if assembly is not None:
            for key, value in [('AssemblyName', assembly), ('PackageId', 'CodeQL.Stub.' + assembly),
                               ('Version', version)]:
                ET.SubElement(props, key).text = value
        group = ET.SubElement(project, 'ItemGroup')
        seen = set()
        for artifact in references:
            kind, name, selected_version = artifact['kind'], artifact['id'], artifact['version']
            if (kind, name, selected_version) in seen or artifact['status'] == 'compile_failed':
                continue
            seen.add((kind, name, selected_version))
            if kind == 'framework' and name != 'Microsoft.NETCore.App':
                ET.SubElement(group, 'FrameworkReference', Include=name)
            elif kind in ('package', 'stub-package'):
                ET.SubElement(group, 'PackageReference', Include=name, Version=f'[{selected_version}]')
        ET.ElementTree(project).write(path, encoding='utf-8', xml_declaration=True)

    def _config(self, path, feed=None):
        config = ET.Element('configuration')
        sources = ET.SubElement(config, 'packageSources')
        ET.SubElement(sources, 'clear')
        if feed is not None:
            ET.SubElement(sources, 'add', key='stubs', value=str(feed))
        ET.SubElement(sources, 'add', key='upstream', value=self.nuget_source)
        ET.ElementTree(config).write(path, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def _publish(temporary, target):
        try:
            temporary.rename(target)
        except OSError as exc:
            if exc.errno not in (errno.EEXIST, errno.ENOTEMPTY) or not target.is_dir():
                raise

    def _stub(self, artifact, cache_dir, dotnet, env):
        source = artifact['stub_path']
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        artifact['version'] = '0.0.0-sha.' + digest
        parent = cache_dir / 'stub-packages'
        parent.mkdir(exist_ok=True)
        target = parent / digest
        if not target.is_dir():
            temporary = Path(tempfile.mkdtemp(prefix='.stub-', dir=parent))
            try:
                shutil.copy2(source, temporary / source.name)
                self._project(temporary / 'Stub.csproj', [], source.stem, artifact['version'])
                self._config(temporary / 'NuGet.Config')
                proc = subprocess.run([str(dotnet), 'pack', 'Stub.csproj', '--output', 'feed',
                                       '-v', 'minimal'], cwd=temporary, env=env, capture_output=True, text=True)
                (temporary / 'compile.log').write_text(proc.stdout + proc.stderr)
                (temporary / 'status.json').write_text(json.dumps({
                    'id': artifact['id'], 'status': 'restored' if proc.returncode == 0 else 'compile_failed'}))
                self._publish(temporary, target)
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        status = json.loads((target / 'status.json').read_text())
        if status['id'] != artifact['id']:
            raise GateError('identical stub bytes have conflicting assembly names')
        artifact['status'] = status['status']
        artifact['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        artifact['compile_log'] = str(target / 'compile.log')
        if artifact['status'] == 'restored':
            feed = cache_dir / 'stub-feed'
            feed.mkdir(exist_ok=True)
            for package in (target / 'feed').glob('*.nupkg'):
                fd, pending = tempfile.mkstemp(prefix='.package-', dir=feed)
                os.close(fd)
                try:
                    shutil.copyfile(package, pending)
                    os.replace(pending, feed / package.name)
                finally:
                    Path(pending).unlink(missing_ok=True)

    def prepare(self, test_dir, codeql_root, cache_dir):
        test_dir, codeql_root, cache_dir = map(lambda p: Path(p).resolve(), (test_dir, codeql_root, cache_dir))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.nuget_packages.mkdir(parents=True, exist_ok=True)
        dotnet, sdk_version, frameworks = self._sdk(cache_dir)
        tokens, artifacts = self._options(test_dir, codeql_root)
        files = sorted(p for p in test_dir.rglob('*') if p.is_file()
                       and p.suffix not in ('.expected', '.qlref', '.ql') and p.name != 'options')
        digest = hashlib.sha256(b'csharp-stager-v2\0' + str(test_dir).encode())
        for path in files:
            digest.update(path.relative_to(test_dir).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        env = self._environment(cache_dir)
        for artifact in artifacts:
            if artifact['kind'] == 'stub-package':
                digest.update(artifact['stub_path'].read_bytes())
                self._stub(artifact, cache_dir, dotnet, env)
        digest.update(json.dumps([tokens, [(a['kind'], a['id'], a['version'], a['status']) for a in artifacts],
                                  sdk_version, frameworks, self.nuget_source], sort_keys=True).encode())
        target = cache_dir / digest.hexdigest()
        manifest = cache_dir / (digest.hexdigest() + '.artifacts.json')
        if not target.is_dir():
            temporary = Path(tempfile.mkdtemp(prefix='.prepare-', dir=cache_dir))
            try:
                for path in files:
                    dest = temporary / path.relative_to(test_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)
                ignore = temporary / '.gitignore'
                existing = ignore.read_text() if ignore.is_file() else ''
                ignore.write_text(existing + ('\n' if existing and not existing.endswith('\n') else '')
                                  + 'bin/\nobj/\n')
                self._project(temporary / 'CodeQLTest.csproj', artifacts)
                config = cache_dir / (temporary.name + '.NuGet.Config')
                feed = cache_dir / 'stub-feed' if any(a['kind'] == 'stub-package' and a['status'] == 'restored'
                                                       for a in artifacts) else None
                self._config(config, feed)
                proc = subprocess.run([str(dotnet), 'restore', 'CodeQLTest.csproj', '--configfile', str(config),
                                       '--packages', str(self.nuget_packages), '-v', 'minimal'],
                                      cwd=temporary, env=env, capture_output=True, text=True)
                # One log per attempt, so a concurrent preparation of the same
                # root cannot overwrite the log of a failed restore.
                log = cache_dir / (temporary.name + '.restore.log')
                log.write_text(proc.stdout + proc.stderr)
                if proc.returncode:
                    raise GateError(f'C# restore failed; see {log}')
                os.replace(log, cache_dir / (digest.hexdigest() + '.restore.log'))
                self._publish(temporary, target)
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        # Read receipts from the restored copy, even on a prepared-root cache hit.
        assets = json.loads((target / 'obj/project.assets.json').read_text())
        selected = assets['project']['frameworks']['net10.0'].get('frameworkReferences', {})
        packs = [frameworks[name] for name in selected if name in frameworks]
        for artifact in artifacts:
            if artifact['kind'] in ('package', 'stub-package') and artifact['status'] == 'restored':
                library = next((v for k, v in assets['libraries'].items()
                                if k.lower() == (artifact['id'] + '/' + artifact['version']).lower()), None)
                if library is None or not library.get('sha512'):
                    raise GateError(f'restore omitted package checksum: {artifact["id"]}')
                artifact['sha512'] = library['sha512']
            elif artifact['kind'] == 'reference':
                artifact['status'] = 'found' if any(
                    (self.dotnet_root / 'packs' / pack / version / 'ref/net10.0' / artifact['id']).is_file()
                    or (self.nuget_packages / pack.lower() / version / 'ref/net10.0' / artifact['id']).is_file()
                    for pack, version in packs) else 'not_found'
            elif artifact['kind'] == 'framework':
                artifact['version'] = frameworks[artifact['id']][1]
        receipt = [{k: v for k, v in a.items() if k != 'stub_path'} for a in artifacts]
        receipt.append(dict(kind='sdk', id='Microsoft.NET.Sdk', version=sdk_version, status='found'))
        receipt.extend(dict(kind='targeting-pack', id=name, version=version, status='restored')
                       for name, version in packs)
        manifest.write_text(json.dumps(receipt, indent=2) + '\n')
        return PreparedRoot(target, tuple(p.relative_to(test_dir).as_posix() for p in files
                                         if p.suffix.lower() in ('.cs', '.cshtml', '.razor')), tuple(receipt))

    def run_env(self, run_dir, prepared):
        return dict(DOTNET_ROOT=str(self.dotnet_root), NUGET_PACKAGES=str(self.nuget_packages),
                    DOTNET_CLI_HOME=str(run_dir / 'dotnet-home'), DOTNET_NOLOGO='1',
                    DOTNET_CLI_TELEMETRY_OPTOUT='1')

    def extra_policy_files(self, prepared):
        return []

    def inline_oracle(self, test_dir, query_id):
        result = {'inline_alert': [], 'spurious': [], 'missing': []}
        for path in sorted(Path(test_dir).rglob('*')):
            if not path.is_file():
                continue
            text = path.read_text(errors='replace')
            if path.suffix.lower() == '.cs':
                comments = csharp_comments(text)
            elif path.suffix.lower() in ('.config', '.csproj', '.props', '.xml'):
                comments = markup_comments(text, ('<!--', '-->'))
            elif path.suffix.lower() in ('.aspx', '.ascx', '.master', '.asmx', '.asax', '.ashx'):
                comments = markup_comments(text, ('<!--', '-->'), ('<%--', '--%>'))
            elif path.suffix.lower() in ('.cshtml', '.razor'):
                comments = razor_comments(text)
            else:
                continue
            for start, end, body in comments:
                add_inline_expectations(result, dict(path=path.relative_to(test_dir).as_posix(),
                                                    start=text.count('\n', 0, start) + 1,
                                                    end=text.count('\n', 0, end) + 1),
                                        body, query_id, {'Alert': 'inline_alert'})
        return result


def csharp_comments(text, start=0, bounded=False):
    """Yield real single-line trivia, with an explicit stack for nested literals.

    A bounded scan starts immediately after a Razor block's opening brace and
    returns its end offset. Interpolation holes are code: quoted values and
    nested interpolations in a hole must not terminate the enclosing string.
    """
    stack = [dict(mode='code', depth=1 if bounded else None)]
    i = start
    while i < len(text):
        frame = stack[-1]
        if frame['mode'] == 'code':
            if text.startswith('//', i):
                end = text.find('\n', i)
                if end < 0:
                    end = len(text)
                if not text.startswith('///', i):
                    yield i, max(i, end - 1), text[i + 2:end].strip()
                i = end
                continue
            if text.startswith('/*', i):
                end = text.find('*/', i + 2)
                i = len(text) if end < 0 else end + 2
                continue
            prefix = i
            dollars = 0
            verbatim = False
            if text[prefix] == '@':
                verbatim = True
                prefix += 1
            while prefix < len(text) and text[prefix] == '$':
                dollars += 1
                prefix += 1
            if prefix < len(text) and text[prefix] == '@' and not verbatim:
                verbatim = True
                prefix += 1
            if prefix < len(text) and text[prefix] == '"':
                quotes = 1
                while prefix + quotes < len(text) and text[prefix + quotes] == '"':
                    quotes += 1
                raw = quotes >= 3 and not verbatim
                delimiter = '"' * quotes if raw else '"'
                stack.append(dict(mode='string', delimiter=delimiter, verbatim=verbatim,
                                  dollars=dollars, raw=raw))
                i = prefix + len(delimiter)
                continue
            if text[i] == "'":
                stack.append(dict(mode='string', delimiter="'", verbatim=False,
                                  dollars=0, raw=False))
                i += 1
                continue
            if frame['depth'] is not None:
                if text[i] == '{':
                    frame['depth'] += 1
                elif text[i] == '}':
                    frame['depth'] -= 1
                    if frame['depth'] == 0:
                        stack.pop()
                        if not stack:
                            return i + 1
            i += 1
            continue
        delimiter = frame['delimiter']
        if not frame['raw'] and not frame['verbatim'] and text[i] == '\\':
            i += 2
        elif frame['verbatim'] and text.startswith('""', i):
            i += 2
        elif text.startswith(delimiter, i):
            stack.pop()
            i += len(delimiter)
        elif frame['dollars'] and text[i] == '{':
            run = 1
            while i + run < len(text) and text[i + run] == '{':
                run += 1
            if not frame['raw'] and run >= 2:
                i += 2
            elif run >= frame['dollars']:
                i += run
                stack.append(dict(mode='code', depth=1))
            else:
                i += run
        else:
            i += 1
    return i


def markup_comments(text, *delimiters):
    """Read XML/ASP comment bodies, skipping quoted attributes and CDATA."""
    i = 0
    in_tag = False
    while i < len(text):
        if in_tag and text[i] in ('"', "'"):
            end = text.find(text[i], i + 1)
            i = len(text) if end < 0 else end + 1
            continue
        comment = next(((opener, closer) for opener, closer in delimiters if text.startswith(opener, i)), None)
        if comment:
            opener, closer = comment
            end = text.find(closer, i + len(opener))
            if end < 0:
                return
            yield i, end + len(closer) - 1, text[i + len(opener):end]
            i = end + len(closer)
            continue
        special = next(((a, b) for a, b in (('<![CDATA[', ']]>'), ('<?', '?>'), ('<%', '%>'))
                        if text.startswith(a, i)), None)
        if special:
            end = text.find(special[1], i + len(special[0]))
            i = len(text) if end < 0 else end + len(special[1])
            continue
        if text[i] == '<':
            in_tag = True
        elif text[i] == '>':
            in_tag = False
        i += 1


def razor_comments(text):
    """Razor's explicit C# blocks carry mapped C# trivia, not ASP comments."""
    i = 0
    while i < len(text):
        ignored = next(((a, b) for a, b in (('@*', '*@'), ('<!--', '-->')) if text.startswith(a, i)), None)
        if ignored:
            end = text.find(ignored[1], i + len(ignored[0]))
            i = len(text) if end < 0 else end + len(ignored[1])
        elif text.startswith('@@', i):
            i += 2
        elif text.startswith('@{', i):
            i = yield from csharp_comments(text, i + 2, bounded=True)
        else:
            i += 1
