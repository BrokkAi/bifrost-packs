#!/usr/bin/env python3
"""Compare CodeQL SARIF and Bifrost JSON from the same repository revision."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import GateError, report_findings


def compare(sarif, report, mapping, repo_root=None):
    """Match repository-relative path and start line; never collapse basenames."""
    upstream = {rule: set() for rule in mapping}
    for run in sarif.get('runs', []):
        artifacts = run.get('artifacts', [])
        rules = run.get('tool', {}).get('driver', {}).get('rules', [])
        for result in run.get('results', []):
            rule = result.get('ruleId')
            if rule is None and 'ruleIndex' in result:
                rule = rules[result['ruleIndex']]['id']
            if rule not in mapping:
                continue
            for location in result.get('locations', []):
                physical = location['physicalLocation']
                artifact = physical['artifactLocation']
                if 'uri' not in artifact:
                    artifact = artifacts[artifact['index']]['location']
                uri = artifact['uri']
                parsed = urlparse(uri)
                if parsed.scheme not in ('', 'file'):
                    raise GateError(f'unsupported SARIF URI: {uri}')
                path = unquote(parsed.path)
                if artifact.get('uriBaseId') and not Path(path).is_absolute():
                    base = run.get('originalUriBaseIds', {}).get(artifact['uriBaseId'], {}).get('uri')
                    if base:
                        path = str(Path(unquote(urlparse(base).path)) / path)
                from core import relative_path
                path = relative_path(path, repo_root)
                if not path.endswith('_test.go'):
                    upstream[rule].add((path, physical['region']['startLine']))
    findings = report_findings(report, repo_root)
    out = {}
    for rule, policy in mapping.items():
        actual = {(f['path'], f['start']) for f in findings if f['policy_id'] == policy
                  and not f['path'].endswith('_test.go')}
        expected = upstream[rule]
        fmt = lambda values: [f'{p}:{n}' for p, n in sorted(values)]
        out[rule] = {'policy_id': policy, 'matched': fmt(expected & actual),
                     'codeql_only': fmt(expected - actual), 'bifrost_only': fmt(actual - expected)}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('codeql_sarif', type=Path)
    parser.add_argument('bifrost_json', type=Path)
    parser.add_argument('mapping', type=Path, help='JSON object: CodeQL rule ID -> Bifrost policy ID')
    parser.add_argument('--repo-root', type=Path, help='strip absolute paths under this repository root')
    parser.add_argument('--codeql-commit', required=True)
    parser.add_argument('--bifrost-commit', required=True)
    args = parser.parse_args()
    if args.codeql_commit != args.bifrost_commit:
        parser.error('reports must be for the same repository commit')
    result = compare(json.loads(args.codeql_sarif.read_text()), json.loads(args.bifrost_json.read_text()),
                     json.loads(args.mapping.read_text()), args.repo_root.resolve() if args.repo_root else None)
    print(json.dumps({'repository_commit': args.codeql_commit, 'rules': result}, indent=2))


if __name__ == '__main__':
    main()
