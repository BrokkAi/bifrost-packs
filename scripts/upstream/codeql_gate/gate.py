#!/usr/bin/env python3
"""Run with python3 -I scripts/upstream/codeql_gate/gate.py --help."""
import argparse
import json
import os
import sys
from pathlib import Path

# -I excludes the script directory; add only this repository's package root.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import GateError, execute, load_oracle
from scoped import validate_attributions
from stagers.go import GoStager
from stagers.java import JavaStager
from stagers.csharp import CSharpStager


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('expected', 'prepare', 'run', 'summary'))
    parser.add_argument('query', nargs='?')
    parser.add_argument('policy', nargs='?', type=Path)
    parser.add_argument('--language', choices=('go', 'java', 'csharp'), default='go')
    parser.add_argument('--codeql-root', type=Path, default=os.environ.get('CODEQL_ROOT'))
    parser.add_argument('--test-dir', action='append', type=Path, default=[], help='relative to CodeQL root; repeat for multi-dir queries')
    parser.add_argument('--query-path', help='query: value in .qlref; inferred from @id when omitted')
    parser.add_argument('--state-dir', type=Path,
                        default=Path(os.environ.get('CODEQL_GATE_STATE', '/tmp/codeql-gate')))
    parser.add_argument('--binary', type=Path, default=os.environ.get('BIFROST_BINARY'))
    parser.add_argument('--java-home', type=Path, default=os.environ.get('JAVA_HOME'),
                        help='JDK used to compile Java stubs (defaults to JAVA_HOME)')
    parser.add_argument('--dotnet-root', type=Path, default=os.environ.get('DOTNET_ROOT'))
    parser.add_argument('--nuget-packages', type=Path)
    parser.add_argument('--nuget-source', default='https://api.nuget.org/v3/index.json')
    parser.add_argument('--extra-policy', action='append', type=Path, default=[])
    parser.add_argument('--models', type=Path)
    parser.add_argument('--label', default='')
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--keep', action='store_true')
    parser.add_argument('--anchors', type=Path)
    parser.add_argument('--true-positives', type=Path)
    parser.add_argument('--scope-catalogs', action='append', type=Path,
                        help='JSON list of exact printed model rows; repeat to union catalogs')
    parser.add_argument('--scope-attributions', type=Path,
                        help='JSON list of reviewed out-of-subset miss attributions')
    args = parser.parse_args(argv)
    catalogs = None
    for path in args.scope_catalogs or []:
        rows = json.loads(path.read_text())
        if not isinstance(rows, list) or any(not isinstance(r, str) or not r.strip() for r in rows):
            raise GateError('scope catalogs must be JSON lists of nonempty printed model strings')
        catalogs = (catalogs or set()) | set(rows)
    args.scope_catalogs = catalogs
    args.scope_attributions = validate_attributions(
        json.loads(args.scope_attributions.read_text()) if args.scope_attributions else [])
    if args.scope_attributions and catalogs is None:
        raise GateError('--scope-attributions requires --scope-catalogs')
    args.state_dir = args.state_dir.resolve()
    if args.command == 'summary':
        latest = {}
        file = args.state_dir / 'results.tsv'
        for line in file.read_text().splitlines() if file.exists() else []:
            row = line.split('\t')
            if not args.label or row[3] == args.label:
                report = Path(row[10]) / 'result.json'
                if report.is_file():
                    validate_attributions(json.loads(report.read_text()).get('scope_attributions', []))
                latest[tuple(row[1:3])] = line
        print('\n'.join(latest.values()))
        return 0 if all(line.split('\t')[4] in ('EXACT', 'SCOPED-EXACT') for line in latest.values()) and latest else 1
    if not args.query or not args.codeql_root:
        parser.error('query and --codeql-root (or CODEQL_ROOT) are required')
    args.codeql_root = args.codeql_root.resolve()
    if args.language == 'csharp':
        stager = CSharpStager(args.dotnet_root, args.nuget_packages or args.state_dir / 'nuget-packages',
                              args.nuget_source)
    else:
        stager = GoStager() if args.language == 'go' else JavaStager(args.java_home)
    if hasattr(stager, 'validate_ql_endpoints'):
        stager.validate_ql_endpoints(args.codeql_root)
    query_path = args.query_path
    if not query_path:
        import re
        src = args.codeql_root / args.language / 'ql/src'
        matches = [p for p in src.rglob('*.ql')
                   if re.search(r'@id\s+' + re.escape(args.query) + r'\s', p.read_text(errors='replace'))]
        if len(matches) != 1:
            raise GateError('cannot resolve unique query @id; supply --query-path')
        query_path = matches[0].relative_to(src).as_posix()
    test_dirs = [(args.codeql_root / d).resolve() for d in args.test_dir]
    if not test_dirs:
        from core import qlref_query
        test_dirs = sorted({p.parent for p in (args.codeql_root / args.language / 'ql/test').rglob('*.qlref')
                            if qlref_query(p) == query_path or qlref_query(p).endswith('/' + query_path)})
    if not test_dirs:
        raise GateError('no test directories found')
    for directory in test_dirs:
        if not directory.is_relative_to(args.codeql_root) or not directory.is_dir():
            raise GateError(f'test directory is outside checkout or missing: {directory}')
    if args.command == 'expected':
        print(json.dumps([dict(test_dir=str(d.relative_to(args.codeql_root)),
                               **load_oracle(d, query_path, stager, args.query, args.scope_catalogs)) for d in test_dirs], indent=2))
        return 0
    if args.command == 'prepare':
        print(json.dumps([str(stager.prepare(d, args.codeql_root, args.state_dir / 'roots').root)
                          for d in test_dirs], indent=2))
        return 0
    if args.policy is None or args.binary is None:
        parser.error('run requires POLICY and --binary (or BIFROST_BINARY)')
    args.policy, args.binary = args.policy.resolve(), args.binary.resolve()
    args.extra_policy = [p.resolve() for p in args.extra_policy]
    if args.models:
        args.models = args.models.resolve()
    if args.timeout <= 0:
        raise GateError('timeout must be positive')
    args.anchors = json.loads(args.anchors.read_text()) if args.anchors else {}
    args.true_positives = json.loads(args.true_positives.read_text()) if args.true_positives else []
    for entry in args.true_positives:
        if not isinstance(entry.get('line'), int) or entry['line'] < 1 or not entry.get('path') or not entry.get('justification', '').strip():
            raise GateError('true positives require path, positive line and justification')
    results = [execute(args, directory, query_path, stager) for directory in test_dirs]
    combined = {'pass': all(r['pass'] for r in results), 'complete': all(r['complete'] for r in results)}
    for name in ('tp', 'fp', 'fn', 'silent_misses', 'abstentions'):
        combined[name] = [f"{r['test_dir']}/{s}" for r in results for s in r[name]]
    combined['verdict'] = ('ERROR' if any(r['verdict'] == 'ERROR' for r in results) else
                           ('SCOPED-EXACT' if args.scope_catalogs is not None else 'EXACT') if combined['pass'] else 'FAIL')
    if args.scope_catalogs is not None:
        combined['full_suite_verdict'] = ('ERROR' if any(r['full_suite_verdict'] == 'ERROR' for r in results)
                                          else 'EXACT' if all(r['full_suite_pass'] for r in results) else 'FAIL')
    print(json.dumps({'runs': results, 'combined': combined}, indent=2))
    return 0 if combined['pass'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (GateError, OSError, ValueError) as exc:
        print(json.dumps({'verdict': 'ERROR', 'pass': False, 'errors': [str(exc)]}), file=sys.stderr)
        sys.exit(2)
