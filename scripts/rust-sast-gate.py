#!/usr/bin/env python3
"""Qualify authored Rust SAST rules on isolated positive and near-miss crates."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RULES = ('unsound-send-sync-impl', 'callback-after-invalid-state')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error('output must be empty')
    environment = dict(os.environ, BIFROST_OPEN_PACKS_DISABLE='1',
                       BIFROST_PARALLELISM='1', RAYON_NUM_THREADS='1', JAVA_HOME='',
                       BIFROST_OPEN_POLICY_PACK_ROOT=str(ROOT / 'rules'))
    version = subprocess.run([str(binary), '--version'], capture_output=True, text=True,
                             check=True, timeout=30)
    (output / 'version.txt').write_text(version.stdout + version.stderr)
    summary = dict(binary=str(binary), binary_sha256=digest(binary),
                   version=version.stdout.strip(), qualification='focused integration build only',
                   released_engine_qualified=False, cases=[])
    manifest = json.loads((ROOT / 'rules/bifrost.security/manifest.json').read_text())
    identities = {p['id']: p for p in manifest['policies']}
    for rule in RULES:
        fixtures = ROOT / 'fixtures/policy/bifrost.security' / rule
        spec = json.loads((fixtures / 'expectations.json').read_text())
        policy = ROOT / 'rules/bifrost.security/policies/rust' / (rule + '.rqlp')
        for case in spec['cases']:
            run = output / rule / case['case']
            run.mkdir(parents=True)
            workspace = run / 'workspace'
            shutil.copytree(fixtures / case['case'], workspace)
            shutil.copyfile(policy, workspace / 'rule.rqlp')
            env = dict(environment, XDG_CACHE_HOME=str(run / 'xdg'),
                       BIFROST_CACHE_ROOT=str(run / 'cache'))
            command = [str(binary), '--root', str(workspace), '--no-builtin-policies',
                       '--policy-file', 'rule.rqlp', '--format', 'json',
                       '--fail-on', 'never', '--output', str(run / 'report.json')]
            record = dict(rule=rule, case=case['case'], expected_findings=case['findings'],
                          command=command, environment={k: env[k] for k in env if
                          k.startswith(('BIFROST_', 'XDG_CACHE', 'RAYON_')) or k == 'JAVA_HOME'},
                          policy_sha256=digest(policy), fixture_hashes={
                              str(p.relative_to(workspace)): digest(p)
                              for p in sorted(workspace.rglob('*')) if p.is_file()})
            try:
                completed = subprocess.run(command, cwd=workspace, env=env, capture_output=True,
                                           text=True, timeout=args.timeout)
                (run / 'stdout.txt').write_text(completed.stdout)
                (run / 'stderr.txt').write_text(completed.stderr)
                record['exit_code'] = completed.returncode
                if completed.returncode:
                    raise ValueError(f'engine exited {completed.returncode}')
                report = json.loads((run / 'report.json').read_text())
                runs = report.get('runs', [])
                if len(runs) != 1 or runs[0].get('policy_id') != spec['policy_id']:
                    raise ValueError('expected exactly one selected policy run')
                result = runs[0]
                findings = result.get('findings', [])
                record.update(completion=result.get('completion'), findings=findings,
                              finding_count=len(findings), policy_hash=result.get('policy_hash'),
                              report_sha256=digest(run / 'report.json'))
                if result.get('completion', {}).get('type') != 'complete':
                    raise ValueError('incomplete or unsupported run')
                record['diagnostics'] = result.get('diagnostics')
                diagnostics = report.get('diagnostics', []) + result.get('diagnostics', [])
                allowed_empty = case['findings'] == 0 and all(
                    d.get('code', {}).get('type') == 'empty_selection'
                    and d.get('impact') == 'advisory' and d.get('severity') == 'note'
                    for d in diagnostics)
                if diagnostics and not allowed_empty:
                    raise ValueError('analysis diagnostics present')
                if len(findings) != case['findings']:
                    raise ValueError(f"expected {case['findings']} findings, got {len(findings)}")
                expected_hash = identities[spec['policy_id']]['resolved_semantic_hash']
                if not expected_hash or result.get('policy_hash') != expected_hash:
                    raise ValueError('runtime semantic identity differs from manifest')
                for finding in findings:
                    if case.get('anchor_line') is not None and finding.get('primary', {}).get('region', {}).get('start_line') != case['anchor_line']:
                        raise ValueError('marker finding does not anchor on the impl header')
                    if finding.get('certainty', {}).get('type') not in ('definite', 'possible'):
                        raise ValueError('missing or invalid finding certainty')
                    if finding.get('policy_id') != spec['policy_id']:
                        raise ValueError('finding policy identity differs from request')
                    if finding.get('policy_hash') != expected_hash:
                        raise ValueError('finding semantic identity differs from manifest')
                    completeness = finding.get('completeness')
                    if completeness not in ('complete', {'type': 'complete'}):
                        raise ValueError(f'incomplete finding evidence: {completeness!r}')
                record['status'] = 'passed'
            except (ValueError, OSError, subprocess.TimeoutExpired) as error:
                record.update(status='failed', error=str(error))
            write(run / 'result.json', record)
            summary['cases'].append(record)
            print(rule, case['case'], record['status'], record.get('error', ''), flush=True)
            write(output / 'summary.json', summary)
    summary['passed'] = all(c['status'] == 'passed' for c in summary['cases'])
    write(output / 'summary.json', summary)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
