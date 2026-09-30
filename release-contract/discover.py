#!/usr/bin/env python3
"""Explicit GitHub discovery, immutable tag validation and hash-addressed cache."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import release


def gh(arguments):
    result = subprocess.run(['gh', 'api', *arguments], capture_output=True, check=False)
    if result.returncode:
        release.fail('unavailable-credentials/network', 'GitHub API unavailable; check network and repository credentials')
    return result.stdout


def api(path):
    try:
        return json.loads(gh([path]))
    except ValueError:
        release.fail('invalid-manifest', 'GitHub API returned invalid JSON')


def tag_commit(repository, tag):
    from urllib.parse import quote
    obj = api(f'repos/{repository}/git/ref/tags/{quote(tag, safe="")}')['object']
    seen = set()
    while obj['type'] == 'tag':
        if obj['sha'] in seen or len(seen) > 8:
            release.fail('invalid-manifest', 'cyclic or excessive annotated tag chain')
        seen.add(obj['sha'])
        obj = api(f'repos/{repository}/git/tags/{obj["sha"]}')['object']
    if obj['type'] != 'commit':
        release.fail('invalid-manifest', 'release tag does not point to commit')
    return obj['sha']


def enumerate_candidates(repository, visibility, cache, offline=False):
    if not re.fullmatch('[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        release.fail('invalid-manifest', 'invalid repository coordinate')
    directory = Path(cache) / repository.replace('/', '--')
    index = directory / 'discovery.json'
    if offline:
        if not index.is_file():
            release.fail('unavailable-credentials/network', 'no cached discovery; explicit online refresh required')
        data, _ = release.load_json(index)
        if data['repository'] != repository or data['visibility'] != visibility:
            release.fail('invalid-manifest', 'cached discovery repository mismatch')
        paths = []
        for item in data['manifests']:
            path = directory / item['sha256'] / 'pack-release.json'
            manifest, raw = release.load_json(path)
            release.validate_manifest(manifest)
            if release.digest(raw) != item['sha256'] or manifest['source']['commit'] != item['commit']:
                release.fail('integrity-error', 'cached manifest changed')
            paths.append(path)
        return paths, data
    if visibility == 'private' and not (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')):
        auth = subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=False)
        if auth.returncode:
            release.fail('unavailable-credentials/network', 'private release discovery requires authenticated access')
    try:
        pages = json.loads(gh(['--paginate', '--slurp', f'repos/{repository}/releases?per_page=100']))
    except ValueError:
        release.fail('invalid-manifest', 'invalid release enumeration JSON')
    paths, manifests, asset_index = [], [], {}
    directory.mkdir(parents=True, exist_ok=True)
    for item in [row for page in pages for row in page]:
        if item['draft']:
            continue
        matches = [a for a in item['assets'] if a['name'] == 'pack-release.json']
        if len(matches) != 1:
            release.fail('invalid-manifest', f'release {item["tag_name"]} must contain one pack-release.json')
        raw = gh(['-H', 'Accept: application/octet-stream', f'repos/{repository}/releases/assets/{matches[0]["id"]}'])
        try:
            manifest = release.validate_manifest(json.loads(raw))
        except ValueError:
            release.fail('invalid-manifest', 'invalid release manifest JSON')
        if manifest['pack']['repository'] != 'https://github.com/' + repository or manifest['pack']['visibility'] != visibility:
            release.fail('invalid-manifest', 'manifest repository/visibility mismatch')
        if manifest['release_version'] != item['tag_name'].removeprefix('v') or (release.semver(manifest['release_version'])[3] == 0) != item['prerelease']:
            release.fail('invalid-manifest', 'release tag/channel does not match manifest')
        commit = tag_commit(repository, item['tag_name'])
        if manifest['source']['commit'] != commit:
            release.fail('integrity-error', 'release tag differs from manifest source commit')
        manifest_hash = release.digest(raw)
        path = directory / manifest_hash / 'pack-release.json'
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        manifests.append(dict(sha256=manifest_hash, commit=commit, tag=item['tag_name']))
        paths.append(path)
        for artifact in manifest['artifacts']:
            matches = [a for a in item['assets'] if a['name'] == artifact['name']]
            if len(matches) != 1:
                release.fail('invalid-manifest', 'indexed artifact missing/ambiguous')
            asset_index[artifact['sha256']] = matches[0]['id']
    data = dict(repository=repository, visibility=visibility, manifests=manifests, assets=asset_index)
    index.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    return paths, data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', required=True); p.add_argument('--visibility', choices=['public', 'private'], required=True); p.add_argument('--cache-dir', type=Path, required=True); p.add_argument('--offline', action='store_true'); p.add_argument('--engine-profile', type=Path, required=True); p.add_argument('--pack-id', required=True); p.add_argument('--channel', choices=['stable', 'prerelease'], default='stable'); p.add_argument('--version'); p.add_argument('--commit'); p.add_argument('--receipt', type=Path, required=True); p.add_argument('--allow-unqualified', action='store_true')
    args = p.parse_args()
    try:
        paths, index = enumerate_candidates(args.repository, args.visibility, args.cache_dir, args.offline)
        profile, _ = release.load_json(args.engine_profile)
        _, _, manifest, _ = release.resolve_candidate(paths, profile, args.pack_id, args.channel, args.version, args.commit, args.allow_unqualified)
        for artifact in manifest['artifacts']:
            destination = args.cache_dir / artifact['sha256'] / artifact['name']
            if not destination.is_file() and not args.offline:
                raw = gh(['-H', 'Accept: application/octet-stream', f'repos/{args.repository}/releases/assets/{index["assets"][artifact["sha256"]]}'])
                if release.digest(raw) != artifact['sha256'] or len(raw) != artifact['size_bytes']:
                    release.fail('integrity-error', 'downloaded artifact differs from manifest')
                destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw)
        result = release.select_release(paths, profile, args.pack_id, args.channel, args.version, args.commit, args.cache_dir, args.allow_unqualified)
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(json.dumps(result, sort_keys=True)); return 0
    except release.ReleaseError as error:
        print(json.dumps({'error': error.code, 'message': str(error)}), file=sys.stderr); return release.ERROR_EXIT[error.code]
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': 'invalid-manifest', 'message': str(error)}), file=sys.stderr); return 3


if __name__ == '__main__':
    raise SystemExit(main())
