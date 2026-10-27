"""Pinned Java QL-class membership cache generation and validation."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

try:
    from .core import GateError
except ImportError:
    from core import GateError


CODEQL_COMMIT = 'ae741615f3e178ce61289a651790dc67fcc18e19'
CODEQL_CLI_VERSION = '2.27.3'
CODEQL_CLI_ARCHIVE_SHA256 = '845075a2fa2fdf72629adc6cbde6264691b698d1f294bd27f10c6b579cd750a4'
EXTRA_CLASSES = ('CliInput',)


def helper_query(ql_endpoints):
    classes = sorted({endpoint['ql_class'] for endpoint in ql_endpoints} | set(EXTRA_CLASSES))
    modules = sorted({endpoint['ql_module'] for endpoint in ql_endpoints})
    literals = ', '.join(f'"{name}"' for name in classes)
    return (
        'import semmle.code.java.dataflow.DataFlow\n'
        + ''.join(f'import {module}\n' for module in modules)
        + 'from DataFlow::Node n, string cls\n'
        + f'where cls = n.getAQlClass() and cls in [{literals}]\n'
        'select n.getLocation().getFile().getRelativePath(), '
        'n.getLocation().getStartLine(), n.getLocation().getStartColumn(), '
        'n.getLocation().getEndLine(), n.getLocation().getEndColumn(), cls\n'
    )


def helper_query_sha256(ql_endpoints):
    return hashlib.sha256(helper_query(ql_endpoints).encode()).hexdigest()


def cache_path(cache_root, test_dir):
    return Path(cache_root) / 'java' / f"{test_dir.replace('/', '--')}.json"


def verify_cli(cli):
    proc = subprocess.run([str(cli), 'version'], capture_output=True, text=True)
    if proc.returncode:
        raise GateError(f'CodeQL CLI version check failed: {proc.stderr.strip()}')
    expected = f'CodeQL command-line toolchain release {CODEQL_CLI_VERSION}.'
    if expected not in proc.stdout.splitlines():
        raise GateError(f'CodeQL CLI must be version {CODEQL_CLI_VERSION}')
    return CODEQL_CLI_VERSION


def _copy_tree(source, target):
    shutil.copytree(source, target, dirs_exist_ok=True)


def _copy_test_inputs(source, target):
    excluded = {'.ql', '.qlref', '.expected'}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if path.is_dir() or path.suffix in excluded:
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def _learned_rows(expected_file):
    rows = []
    for line in expected_file.read_text(errors='replace').splitlines():
        text = line.strip()
        if not text:
            continue
        if not (text.startswith('|') and text.endswith('|')):
            raise GateError(f'CodeQL helper produced non-row output: {text}')
        cells = [cell.strip() for cell in text[1:-1].split('|')]
        if len(cells) != 6:
            raise GateError(f'CodeQL helper produced an invalid row: {text}')
        path, start_line, start_column, end_line, end_column, ql_class = cells
        try:
            row = dict(path=Path(path.replace('\\', '/')).as_posix(),
                       start_line=int(start_line), start_column=int(start_column),
                       end_line=int(end_line), end_column=int(end_column), ql_class=ql_class)
        except ValueError as exc:
            raise GateError(f'CodeQL helper produced invalid coordinates: {text}') from exc
        rows.append(row)
    return [dict(items) for items in sorted({tuple(sorted(row.items())) for row in rows})]


def generate_cache(codeql_root, test_dir, cli, cache_root, scratch_root, ql_endpoints):
    codeql_root = Path(codeql_root).resolve()
    test_dir = Path(test_dir).resolve()
    if not test_dir.is_relative_to(codeql_root) or not test_dir.is_dir():
        raise GateError(f'QL-class test directory is outside checkout or missing: {test_dir}')
    relative_test_dir = test_dir.relative_to(codeql_root).as_posix()
    commit = subprocess.check_output(['git', '-C', str(codeql_root), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != CODEQL_COMMIT:
        raise GateError(f'QL-class cache generation requires CodeQL commit {CODEQL_COMMIT}, got {commit}')
    cli_version = verify_cli(cli)

    with tempfile.TemporaryDirectory(prefix='ql-classes-', dir=scratch_root) as temporary:
        workspace = Path(temporary)
        java_ql = workspace / 'java' / 'ql'
        test_pack = java_ql / 'test'
        source_test_pack = codeql_root / 'java/ql/test'
        _copy_tree(codeql_root / 'java/ql/lib', java_ql / 'lib')
        _copy_tree(codeql_root / 'shared', workspace / 'shared')
        _copy_tree(source_test_pack / 'stubs', test_pack / 'stubs')
        test_relative = Path(relative_test_dir).relative_to('java/ql/test')
        copied_test = test_pack / test_relative
        copied_test.mkdir(parents=True)
        _copy_test_inputs(test_dir, copied_test)

        (workspace / 'codeql-workspace.yml').write_text(
            'provide:\n  - "java/ql/lib/qlpack.yml"\n'
            '  - "java/ql/test/qlpack.yml"\n  - "shared/**/qlpack.yml"\n')
        (test_pack / 'qlpack.yml').write_text(
            'name: codeql/harness-endpoint-class-tests\nversion: 0.0.1\nextractor: java\n'
            'dependencies:\n  codeql/java-all: ${workspace}\ntests: .\n')
        helper = copied_test / 'BifrostEndpointClasses.ql'
        helper.write_text(helper_query(ql_endpoints))
        expected = helper.with_suffix('.expected')
        expected.write_text('\n')
        command = [str(cli), 'test', 'run', '--common-caches',
                   str(Path(scratch_root) / 'codeql-common-cache'),
                   '--no-default-compilation-cache', '--learn', '--search-path', str(codeql_root),
                   '--', str(helper)]
        proc = subprocess.run(['nice', '-n', '10', *command], capture_output=True, text=True,
                              timeout=1800)
        if proc.returncode:
            raise GateError(f'CodeQL QL-class test run failed ({proc.returncode}):\n'
                            f'{proc.stdout}\n{proc.stderr}')
        rows = _learned_rows(expected)

    payload = dict(codeql_commit=commit, cli_version=cli_version,
                   cli_archive_sha256=CODEQL_CLI_ARCHIVE_SHA256,
                   helper_query_sha256=helper_query_sha256(ql_endpoints),
                   test_dir=relative_test_dir, rows=rows)
    output = cache_path(cache_root, relative_test_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, sort_keys=True, separators=(',', ':')) + '\n')
    return output


def verify_checkout_revision(codeql_root, cache_commit):
    try:
        actual = subprocess.check_output(
            ['git', '-C', str(Path(codeql_root).resolve()), 'rev-parse', 'HEAD'],
            text=True, stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise GateError(f'cannot read CodeQL checkout HEAD: {detail}') from exc
    if actual != cache_commit:
        raise GateError(f'CodeQL checkout HEAD {actual} does not match QL-class cache commit {cache_commit}')


def verify_allowlist_files_clean(codeql_root, ql_endpoints):
    root = Path(codeql_root).resolve()
    files = sorted({endpoint['file'] for endpoint in ql_endpoints})
    try:
        proc = subprocess.run(['git', '-C', str(root), 'status', '--porcelain', '--', *files],
                              capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise GateError(f'cannot check CodeQL allow-list file status: {detail}') from exc
    if proc.stdout.strip():
        raise GateError('CodeQL allow-list class files have local changes')


def load_cache(cache_root, test_dir, ql_endpoints, codeql_root):
    path = cache_path(cache_root, test_dir)
    if not path.is_file():
        raise GateError(f'QL-class cache is missing for {test_dir}: {path.name}')
    try:
        cache = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise GateError(f'invalid QL-class cache for {test_dir}: {exc}') from exc
    expected = dict(codeql_commit=CODEQL_COMMIT, cli_version=CODEQL_CLI_VERSION,
                    cli_archive_sha256=CODEQL_CLI_ARCHIVE_SHA256,
                    helper_query_sha256=helper_query_sha256(ql_endpoints), test_dir=test_dir)
    for key, value in expected.items():
        if cache.get(key) != value:
            raise GateError(f'stale QL-class cache for {test_dir}: {key} does not match the pin')
    verify_checkout_revision(codeql_root, cache.get('codeql_commit'))
    verify_allowlist_files_clean(codeql_root, ql_endpoints)
    if not isinstance(cache.get('rows'), list):
        raise GateError(f'invalid QL-class cache rows for {test_dir}')
    row_keys = {'path', 'start_line', 'start_column', 'end_line', 'end_column', 'ql_class'}
    for row in cache['rows']:
        if (not isinstance(row, dict) or set(row) != row_keys or not isinstance(row['path'], str)
                or not row['path'] or PurePosixPath(row['path']).is_absolute()
                or '..' in PurePosixPath(row['path']).parts
                or not isinstance(row['ql_class'], str) or not row['ql_class']
                or any(not isinstance(row[key], int) or isinstance(row[key], bool) or row[key] < 1
                       for key in ('start_line', 'start_column', 'end_line', 'end_column'))):
            raise GateError(f'invalid QL-class cache row for {test_dir}')
    return cache
