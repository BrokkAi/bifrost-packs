#!/usr/bin/env python3
"""Fail closed before publishing v2 metadata or unresolved release dependencies."""
import argparse
import json
from pathlib import Path
import sys

import release


def verify_publication(manifest, directory, dependencies=()):
    release.validate_manifest(manifest)
    if manifest['manifest_schema_version'] != 2:
        release.fail('unsupported-manifest-schema', 'new publication requires manifest schema 2')
    if manifest['qualification']['integrity']['status'] != 'verified':
        release.fail('integrity-error', 'publication requires verified format/integrity evidence')
    if manifest['qualification']['behavior']['status'] == 'failed':
        release.fail('integrity-error', 'publication refuses failed behavioral evidence')
    for artifact in manifest['artifacts']:
        release.verify_artifact(artifact, Path(directory) / artifact['name'])
    # Inspect actual native bytes as well as declarations; metadata cannot hide inner gates.
    from native_release import archive_files
    native_items = list(manifest['contents'])
    for artifact in manifest['artifacts']:
        if artifact['role'] != 'native':
            continue
        files = archive_files(Path(directory) / artifact['name'])
        for name, data in files.items():
            if not name.endswith('.json'):
                continue
            try:
                inner = json.loads(data)
            except (ValueError, UnicodeDecodeError):
                release.fail('integrity-error', f'invalid native JSON: {name}')
            if isinstance(inner, dict) and isinstance(inner.get('compatibility'), dict) and any(key in inner['compatibility'] for key in ('bifrost', 'engine')):
                native_items.append(dict(kind='semantic-model', identity=inner.get('pack_id', name), dependencies=[json.dumps(inner['compatibility'])]))
    from native_release import require_version_independent_native
    require_version_independent_native(native_items)
    indexed = {}
    for dependency in dependencies:
        release.validate_manifest(dependency)
        key = (dependency['pack']['repository'], dependency['pack']['id'], dependency['release_version'])
        if key in indexed and indexed[key] != dependency:
            release.fail('invalid-manifest', 'ambiguous publication dependency')
        indexed[key] = dependency
    for dependency in manifest['release_dependencies']:
        key = (dependency['repository'], dependency['pack_id'], dependency['release_version'])
        if key not in indexed:
            release.fail('no-compatible-release', f"publication requires verified exact dependency {dependency['pack_id']}@{dependency['release_version']} from {dependency['repository']}")
        selected = indexed[key]
        if selected.get('release_dependencies'):
            release.fail('no-compatible-release', 'nested publication dependencies require independent verification before publication')
        if selected['manifest_schema_version'] != 2 or selected['qualification']['integrity']['status'] != 'verified' or selected['qualification']['behavior']['status'] == 'failed':
            release.fail('no-compatible-release', 'publication dependency must use the verified v2 contract')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--dependency-manifest', type=Path, action='append', default=[])
    args = parser.parse_args()
    try:
        manifest, _ = release.load_json(args.manifest)
        dependencies = [release.load_json(path)[0] for path in args.dependency_manifest]
        verify_publication(manifest, args.directory, dependencies)
        print(json.dumps({'status': 'verified', 'release_version': manifest['release_version']}))
        return 0
    except release.ReleaseError as error:
        print(json.dumps({'error': error.code, 'message': str(error)}), file=sys.stderr)
        return release.ERROR_EXIT[error.code]
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': 'invalid-manifest', 'message': str(error)}), file=sys.stderr)
        return release.ERROR_EXIT['invalid-manifest']


if __name__ == '__main__':
    raise SystemExit(main())
