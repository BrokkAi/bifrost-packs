#!/usr/bin/env python3
"""Attach bounded smoke evidence without claiming whole-pack qualification."""
import argparse
import json
from pathlib import Path
import release


def attach(manifest_path, evidence, output):
    manifest, _ = release.load_json(manifest_path)
    release.validate_manifest(manifest)
    smoke, raw = release.load_json(evidence / 'smoke.json')
    if manifest['manifest_schema_version'] != 2:
        release.fail('unsupported-manifest-schema', 'smoke attachment requires schema 2')
    policies = [item for item in manifest['contents'] if item['kind'] == 'policy' and item['identity'] == smoke['policy_id']]
    if len(policies) != 1 or policies[0]['authored_hash'] != smoke['policy_authored_hash']:
        release.fail('integrity-error', 'smoke policy differs from released policy')
    if smoke.get('status') != 'passed':
        release.fail('integrity-error', 'smoke did not pass')
    if {item['case'] for item in smoke['runs']} != {'positive', 'near-miss'} or len(smoke['runs']) != 2:
        release.fail('integrity-error', 'both positive and near-miss smoke evidence are required')
    for item in smoke['runs']:
        expected = 1 if item['case'] == 'positive' else 0
        if item.get('status') != 'passed' or not isinstance(item['completion'], dict) or item['completion'].get('type') != 'complete' or item['finding_count'] != expected or item['exit_code'] != expected:
            release.fail('integrity-error', 'smoke incomplete or unexpected findings')
        report_path = release.safe_path(item['raw_report'])
        report, report_bytes = release.load_json(evidence / report_path)
        if release.digest(report_bytes) != item['raw_report_sha256']:
            release.fail('integrity-error', 'smoke raw report hash differs')
        runs = report.get('runs', [])
        if (len(runs) != 1 or runs[0].get('policy_id') != smoke['policy_id']
                or runs[0].get('policy_hash') != smoke['policy_authored_hash']
                or not isinstance(runs[0].get('completion'), dict) or runs[0]['completion'].get('type') != 'complete'
                or len(runs[0].get('findings', [])) != expected
                or runs[0].get('diagnostics') != [] or report.get('diagnostics') != []):
            release.fail('integrity-error', 'smoke raw report is incomplete or differs')
        fixture = evidence / 'inputs' / (item['case'] + '.py')
        if release.digest(fixture.read_bytes()) != smoke['fixture_hashes'][item['case']]:
            release.fail('integrity-error', 'smoke fixture hash differs')
    policy_bytes = (evidence / 'inputs' / 'dynamic-evaluation.rqlp').read_bytes()
    if release.digest(policy_bytes) != policies[0]['sha256'] or release.digest(policy_bytes) != smoke['copied_policy_sha256']:
        release.fail('integrity-error', 'smoke policy bytes differ from released bytes')
    indexed = {item['name'] for item in manifest['artifacts']}
    for path in sorted(evidence.rglob('*')):
        if path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            release.fail('integrity-error', 'smoke evidence must contain regular files')
        relative = path.relative_to(evidence).as_posix()
        release.safe_path(relative)
        name = 'smoke-' + relative.replace('/', '--')
        if name in indexed:
            release.fail('invalid-manifest', 'duplicate smoke evidence asset')
        indexed.add(name)
        data = path.read_bytes()
        (output / name).write_bytes(data)
        artifact = dict(name=name, sha256=release.digest(data), size_bytes=len(data), format=path.suffix.removeprefix('.') or 'text', role='source')
        manifest['artifacts'].append(artifact)
        (output / (name + '.sha256')).write_text(artifact['sha256'] + '  ' + name + '\n')
    manifest['qualification']['behavior'] = dict(status='limited', evidence=[smoke['scope'], 'One Python policy: complete positive (one finding) and near-miss (zero findings). Full released policy/model behavior remains unqualified; indexed smoke files retain inputs, reports and executable identity.'])
    provenance = dict(manifest.get('provenance', {}))
    testing = list(provenance.get('testing', []))
    testing.append(dict(engine_version=smoke['engine_version'], build_identity='sha256:' + smoke['binary_sha256']))
    provenance['testing'] = testing
    manifest['provenance'] = provenance
    release.validate_manifest(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    attach(args.manifest, args.evidence, args.output)


if __name__ == '__main__':
    main()
