#!/usr/bin/env python3
"""Build a component release; the initial baseline is pinned to public Bifrost bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zlib

import content
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'release-contract'))
import release


def archive_files(path):
    result = {}
    with tarfile.open(path) as archive:
        for member in archive:
            release.safe_path(member.name.rstrip('/'))
            if member.isdir():
                continue
            if not member.isfile() or member.name in result:
                release.fail('integrity-error', 'duplicate or nonregular archive member')
            result[member.name] = archive.extractfile(member).read()
    return result


def rules_stage(root, source, baseline, stage):
    files = archive_files(source)
    prefixes = {name.split('/')[0] for name in files}
    if len(prefixes) != 1:
        release.fail('integrity-error', 'source archive must have one root')
    prefix = next(iter(prefixes)) + '/'
    entries = baseline['rules']
    actual = {name[len(prefix):] for name in files if name.startswith(prefix + 'crates/bifrost-policy/policy-packs/')}
    if actual != {e['source_path'] for e in entries}:
        release.fail('integrity-error', 'baseline policy source inventory differs')
    for entry in entries:
        data = files[prefix + entry['source_path']]
        if release.digest(data) != entry['sha256']:
            release.fail('integrity-error', 'baseline policy bytes differ')
        target = stage / entry['path']; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    for name in ('LICENSE', 'NOTICE.md', 'README.md'):
        shutil.copyfile(root / name, stage / name)
    for name in ('scripts/smoke.py', 'scripts/content.py', 'tests/cases/dynamic-evaluation/positive.py', 'tests/cases/dynamic-evaluation/near-miss.py'):
        if (root / name).is_file():
            target = stage / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(root / name, target)
    lock, _ = release.load_json(root / 'content-lock.json')
    lock.update(source=dict(repository=baseline['repository'], revision=baseline['commit']), files=entries)
    lock['aggregate_sha256'] = release.digest(''.join(f"{e['sha256']}  {e['path']}\n" for e in entries).encode())
    (stage / 'content-lock.json').write_text(json.dumps(lock, indent=2) + '\n')
    return lock


from native_release import native_contents


def build(root, component, version, output, source=None, native=None):
    config, _ = release.load_json(root / f'release-config.{component}.json')
    config['release_version'] = version
    if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip():
        release.fail('invalid-manifest', 'release build requires clean source checkout')
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    output.mkdir(parents=True, exist_ok=True)
    if config.get('baseline'):
        baseline, raw = release.load_json(root / config['baseline'])
        origin = dict(repository=baseline['repository'], commit=baseline['commit'], lock_sha256=release.digest(raw))
        if component == 'rules':
            if source is None: release.fail('invalid-manifest', 'baseline rules require --source-archive')
            archive = output / f"bifrost.public.rules-{version}-source.tar.gz"
            with tempfile.TemporaryDirectory() as directory:
                stage = Path(directory); lock = rules_stage(root, source, baseline, stage)
                content.build_bundle(archive, stage)
                contents = release.public_contents(stage, lock, 'rules')
        else:
            if native is None: release.fail('invalid-manifest', 'baseline packs require --native-archive')
            archive = output / f"bifrost.public.packs-{version}-native.tar.gz"
            contents = native_contents(native, baseline)
            shutil.copyfile(native, archive); config['artifact_role'] = 'native'
    else:
        archive = output / f"bifrost.public.{component}-{version}-source.tar.gz"
        content.build_bundle(archive, root, component)
        lock, raw = release.load_json(root / 'content-lock.json')
        origin = dict(repository=lock['source']['repository'], commit=lock['source']['revision'], lock_sha256=release.digest(raw))
        contents = release.public_contents(root, lock, component)
    manifest = release.make_manifest(config, commit, contents, archive, origin)
    manifest['qualification']['evidence'] = ['Exact public Bifrost baseline bytes; archive and file integrity verified. Full behavior qualification pending.']
    release.validate_manifest(manifest)
    (output / 'pack-release.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    (output / (archive.name + '.sha256')).write_text(release.digest(archive.read_bytes()) + '  ' + archive.name + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=['rules', 'packs'], required=True)
    parser.add_argument('--version', required=True); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-archive', type=Path); parser.add_argument('--native-archive', type=Path)
    args = parser.parse_args()
    try:
        result = build(Path(__file__).resolve().parents[1], args.component, args.version, args.output.resolve(), args.source_archive, args.native_archive)
        print(json.dumps(dict(pack=result['pack'], release_version=result['release_version'], artifacts=result['artifacts'])))
    except (release.ReleaseError, content.ContentError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr); return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
