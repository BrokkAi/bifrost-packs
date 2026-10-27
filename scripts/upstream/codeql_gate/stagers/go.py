"""Stage Go query tests without changing build tags, modules or vendored inputs."""
import errno
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path

from . import PreparedRoot


class GoStager:
    def prepare(self, test_dir, codeql_root, cache_dir):
        test_dir, cache_dir = Path(test_dir), Path(cache_dir)
        files = sorted(p for p in test_dir.rglob('*') if p.is_file()
                       and p.suffix not in ('.expected', '.qlref', '.ql')
                       and p.name != 'options')
        digest = hashlib.sha256(b'go-stager-v1\0' + str(test_dir.resolve()).encode())
        for path in files:
            digest.update(path.relative_to(test_dir).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / digest.hexdigest()
        if not target.exists():
            temporary = Path(tempfile.mkdtemp(prefix='.prepare-', dir=cache_dir))
            try:
                for path in files:
                    dest = temporary / path.relative_to(test_dir)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)
                if not (temporary / 'go.mod').exists():
                    (temporary / 'go.mod').write_text('module codeql.test/fixture\n\ngo 1.18\n')
                try:
                    temporary.rename(target)
                except OSError as exc:
                    if exc.errno not in (errno.EEXIST, errno.ENOTEMPTY) or not target.is_dir():
                        raise
            finally:
                shutil.rmtree(temporary, ignore_errors=True)
        return PreparedRoot(target, tuple(p.relative_to(test_dir).as_posix()
                                          for p in files if p.suffix == '.go'))

    def run_env(self, run_dir, prepared):
        env = {'XDG_CACHE_HOME': str(run_dir / 'xdg'),
               'BIFROST_OPEN_PACKS_DISABLE': '1', 'BIFROST_PARALLELISM': '4',
               'GOCACHE': str(run_dir / 'cache' / 'go-build'),
               'GOMODCACHE': str(run_dir / 'cache' / 'go-mod'),
               'GOPROXY': 'off', 'GOSUMDB': 'off', 'GOTOOLCHAIN': 'local',
               'GOFLAGS': '-mod=vendor' if (prepared.root / 'vendor').is_dir() else ''}
        return env

    def extra_policy_files(self, prepared):
        return []

    def inline_oracle(self, test_dir):
        result = {'inline_alert': [], 'inline_taint': [], 'spurious': [], 'missing': []}
        # Lex strings/runes/raw strings and block comments before recognizing //.
        # This avoids treating source text such as `// $ Alert` as an annotation.
        tokens = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`[^`]*`|/\*[\s\S]*?\*/|//[^\n]*')
        for path in sorted(Path(test_dir).rglob('*.go')):
            text = path.read_text(errors='replace')
            for token in tokens.finditer(text):
                comment = token.group()
                if not comment.startswith('//'):
                    continue
                location = {'path': path.relative_to(test_dir).as_posix(),
                            'start': text.count('\n', 0, token.start()) + 1,
                            'end': text.count('\n', 0, token.start()) + 1}
                for tag in re.finditer(r'\$\s*(?:(SPURIOUS|MISSING):\s*)?(Alert(?:\[[^\]]*\])?|hasTaintFlow\s*=\s*"[^"]*")(?!\w)', comment):
                    kind = tag.group(1)
                    key = kind.lower() if kind else ('inline_taint' if tag.group(2).startswith('hasTaintFlow') else 'inline_alert')
                    result[key].append(dict(location))
        return result
