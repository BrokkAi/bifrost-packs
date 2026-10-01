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


from native_release import native_contents, require_version_independent_native


def verify_archive_content(archive, expected_lock=None):
    """Verify archive members, the embedded lock and all locked content bytes."""
    actual = archive_files(archive)
    import tempfile
    import content as content_module

    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        for name, data in actual.items():
            target = stage / release.safe_path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        verified_lock = content_module.verify_content(stage)
    if expected_lock is not None and verified_lock != expected_lock:
        release.fail('integrity-error', 'archived content lock differs from the verified stage lock')
    return verified_lock


def verify_stage_archive(archive, stage, expected_lock=None):
    """Check a staged archive byte-for-byte, then verify its pinned content hashes."""
    actual = archive_files(archive)
    expected = {}
    for path in stage.rglob('*'):
        if path.is_symlink():
            release.fail('integrity-error', 'release stage contains a symlink')
        if path.is_file():
            expected[path.relative_to(stage).as_posix()] = path.read_bytes()
    if actual != expected:
        release.fail('integrity-error', 'archive members differ from the verified stage')
    try:
        archived_lock = json.loads(actual['content-lock.json'])
        if expected_lock is not None and archived_lock != expected_lock:
            release.fail('integrity-error', 'archived content lock differs from the verified stage lock')
        for entry in archived_lock['files']:
            data = actual[release.safe_path(entry['path'])]
            if release.digest(data) != entry['sha256']:
                release.fail('integrity-error', f"archived locked bytes differ: {entry['path']}")
        aggregate = ''.join(
            f"{entry['sha256']}  {entry['path']}\n"
            for entry in sorted(archived_lock['files'], key=lambda entry: entry['path'])
        )
        if release.digest(aggregate.encode()) != archived_lock['aggregate_sha256']:
            release.fail('integrity-error', 'archived content-lock aggregate differs')
    except (KeyError, TypeError, ValueError) as error:
        release.fail('integrity-error', f'archived content lock is invalid: {error}')


def qualify_integrity(manifest, evidence):
    manifest['qualification'] = dict(
        integrity=dict(status='verified', evidence=evidence),
        behavior=dict(status='pending', evidence=[
            'Full engine and semantic-model behavior qualification remains pending.',
        ]),
    )


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
                verify_stage_archive(archive, stage, lock)
                contents = release.public_contents(stage, lock, 'rules')
        else:
            if native is None: release.fail('invalid-manifest', 'baseline packs require --native-archive')
            archive = output / f"bifrost.public.packs-{version}-native.tar.gz"
            contents = native_contents(native, baseline)
            require_version_independent_native(contents)
            shutil.copyfile(native, archive); config['artifact_role'] = 'native'
            config['provenance'] = dict(
                engine_version=baseline['tag'].removeprefix('v'),
                source_commit=baseline['commit'],
            )
    else:
        archive = output / f"bifrost.public.{component}-{version}-source.tar.gz"
        content.build_bundle(archive, root, component)
        full_lock, raw = release.load_json(root / 'content-lock.json')
        prefixes = ('rules/', 'fixtures/policy/', 'licenses/') if component == 'rules' else ('semantic-packs/', 'fixtures/semantic/', 'scripts/upstream/', 'licenses/')
        lock = dict(full_lock, files=[entry for entry in full_lock['files'] if entry['path'].startswith(prefixes)])
        aggregate = ''.join(f"{entry['sha256']}  {entry['path']}\n" for entry in sorted(lock['files'], key=lambda entry: entry['path']))
        lock['aggregate_sha256'] = release.digest(aggregate.encode())
        origin = dict(repository=lock['source']['repository'], commit=lock['source']['revision'], lock_sha256=release.digest(raw))
        contents = release.public_contents(root, lock, component)
        verify_archive_content(archive, lock)
    if config.get('baseline') and component == 'rules':
        config['provenance'] = dict(
            engine_version=baseline['tag'].removeprefix('v'),
            source_commit=baseline['commit'],
        )
    manifest = release.make_manifest(config, commit, contents, archive, origin)
    if component == 'rules' and config.get('baseline'):
        qualify_integrity(manifest, [
            'Verified the pinned public Bifrost commit, exact 49-policy inventory, and per-file SHA-256 values.',
            'Verified the staged content lock, aggregate hash, and written archive members against the stage.',
        ])
    elif component == 'rules':
        qualify_integrity(manifest, [
            'Verified the checked-in authoring content lock and per-file SHA-256 values.',
            'Verified the filtered stream lock, aggregate hash, and written archive members against the selected stream.',
        ])
    else:
        qualify_integrity(manifest, [
            'Verified the pinned native archive checksum, archive inventory, SHA256SUMS, index schema version, manifest descriptors and identities, shard hashes and sizes, supported encodings, decompressed sizes, and JSON payloads.',
        ])
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
