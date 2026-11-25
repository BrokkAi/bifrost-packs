"""Stage inert Rust qltest sources as one synthetic crate; never invoke Cargo."""
import hashlib
import re
import shutil
import tempfile
from pathlib import Path

from . import PreparedRoot
try:
    from core import GateError, add_inline_expectations
except ImportError:
    from ..core import GateError, add_inline_expectations


class RustStager:
    ql_endpoints = ()

    @staticmethod
    def model_in_catalog(row, catalogs):
        return row in catalogs

    def prepare(self, test_dir, codeql_root, cache_dir):
        test_dir, cache_dir = Path(test_dir), Path(cache_dir)
        files = sorted(test_dir.rglob('*.rs'))
        if not files:
            raise GateError(f'no Rust source files in {test_dir}')
        options = test_dir / 'options.yml'
        dependencies = self.dependencies(options)
        extensions = sorted(test_dir.glob('*.ext.yml'))
        digest = hashlib.sha256(b'rust-stager-v2\0' + str(test_dir.resolve()).encode())
        digest.update(options.read_bytes() if options.exists() else b'')
        for path in files:
            digest.update(path.relative_to(test_dir).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / digest.hexdigest()
        if not target.exists():
            temporary = Path(tempfile.mkdtemp(prefix='.rust-prepare-', dir=cache_dir))
            try:
                for path in files:
                    dest = temporary / path.relative_to(test_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)
                # Explicit path retains CodeQL locations; no source rewriting or dependency resolution.
                primary = next((p for p in files if p.name == 'lib.rs'), files[0])
                rel = primary.relative_to(test_dir).as_posix()
                (temporary / 'Cargo.toml').write_text(
                    '[package]\nname = "codeql_fixture"\nversion = "0.0.0"\nedition = "2021"\n'
                    f'[lib]\npath = "{rel}"\n'
                    + ('[dependencies]\n' + '\n'.join(dependencies) + '\n' if dependencies else ''))
                temporary.rename(target)
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        artifacts = tuple({'kind': 'codeql_model_extension', 'path': p.name}
                          for p in extensions)
        return PreparedRoot(target, tuple(p.relative_to(test_dir).as_posix() for p in files), artifacts)

    @staticmethod
    def dependencies(options):
        if not options.exists():
            return []
        entries = []
        in_dependencies = False
        for line in options.read_text().splitlines():
            if re.match(r'^qltest_dependencies:\s*$', line):
                in_dependencies = True
                continue
            if in_dependencies and line and not line[0].isspace():
                break
            if in_dependencies and line.strip() and not line.lstrip().startswith('#'):
                match = re.fullmatch(r'\s*-\s*([A-Za-z_][\w-]*)\s*=\s*(\{.*\}|"[^"]*")\s*', line)
                if not match:
                    raise GateError(f'unsupported qltest dependency declaration: {line}')
                entries.append(f'{match[1]} = {match[2]}')
        return entries

    def run_env(self, run_dir, prepared):
        return {'BIFROST_OPEN_PACKS_DISABLE': '1', 'CARGO_NET_OFFLINE': 'true',
                'CARGO_HOME': str(run_dir / 'cargo-home')}

    def extra_policy_files(self, prepared):
        return []

    def inline_oracle(self, test_dir, query_id):
        result = {'inline_alert': [], 'inline_taint': [], 'spurious': [], 'missing': []}
        # Lex comments while skipping ordinary, byte and raw strings; line comments
        # inside literals cannot become expectations. Block comments are ignored.
        tokens = re.compile(r'br(?P<bhash>#{0,255})"[\s\S]*?"(?P=bhash)|r(?P<hash>#{0,255})"[\s\S]*?"(?P=hash)|b?"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*')
        for path in sorted(Path(test_dir).rglob('*.rs')):
            source = path.read_text(errors='replace')
            for match in tokens.finditer(source):
                comment = match.group()
                if comment.startswith('//'):
                    line = source.count('\n', 0, match.start()) + 1
                    add_inline_expectations(result, {'path': path.relative_to(test_dir).as_posix(),
                                                     'start': line, 'end': line}, comment[2:],
                                            query_id, {'Alert': 'inline_alert', 'hasTaintFlow': 'inline_taint'})
        return result
