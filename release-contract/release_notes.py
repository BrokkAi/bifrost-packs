#!/usr/bin/env python3
"""Render actual manifest requirements as human-readable release notes."""
import argparse
from pathlib import Path
import release


def render(manifest):
    release.validate_manifest(manifest)
    if manifest['manifest_schema_version'] != 2:
        release.fail('unsupported-manifest-schema', 'new release notes require schema 2')
    lines = [f"{manifest['pack']['id']} {manifest['release_version']}", '',
             f"Source commit: `{manifest['source']['commit']}`.", '',
             'Compatibility requires release manifest schema 2 and these content formats:']
    for axis, versions in manifest['compatibility']['schemas'].items():
        if versions:
            lines.append(f"- `{axis}`: {', '.join(map(str, versions))}")
    lines.extend(['', 'Required semantic capabilities (contract version ' + str(manifest['compatibility']['capabilities']['contract_version']) + '):'])
    capabilities = manifest['compatibility']['capabilities']['required']
    lines.append(', '.join(f'`{capability}`' for capability in capabilities) if capabilities else 'None.')
    lines.extend(['', 'Exact pack release dependencies:'])
    dependencies = manifest['release_dependencies']
    lines.extend([f"- `{item['pack_id']}@{item['release_version']}` from {item['repository']}" for item in dependencies] or ['None.'])
    lines.extend(['', 'Bifrost engine SemVer is generation/testing provenance and is not a compatibility gate for this contract.', '',
                  f"Format/integrity evidence: {manifest['qualification']['integrity']['status']}.",
                  f"Behavior evidence: {manifest['qualification']['behavior']['status']}."])
    lines.extend(manifest['qualification']['behavior']['evidence'])
    lines.extend(['', 'Format compatibility does not establish complete analysis coverage or whole-language behavior qualification. Partial native content remains partial. Source rules require a consumer that supports source policy artifacts and this contract.'])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    manifest, _ = release.load_json(args.manifest)
    args.output.write_text(render(manifest))


if __name__ == '__main__':
    main()
