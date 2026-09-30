#!/usr/bin/env python3
"""Index independently generated native packs without inferring consumer compatibility."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zlib

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


def native_contents(archive, baseline=None, generator_version=None):
    if baseline is not None and release.digest(archive.read_bytes()) != baseline['native_sha256']:
        release.fail('integrity-error', 'published native archive checksum differs')
    files = archive_files(archive); prefix = 'bifrost-semantic-packs/'
    checksums = files[prefix + 'SHA256SUMS'].decode().splitlines()
    claimed = set()
    for line in checksums:
        sha, name = line.split('  ', 1); release.safe_path(name)
        path = prefix + name
        if path in claimed or path not in files or release.digest(files[path]) != sha:
            release.fail('integrity-error', 'native file checksum differs')
        claimed.add(path)
    if set(files) - claimed - {prefix + 'SHA256SUMS', prefix + 'measurements.json'}:
        release.fail('integrity-error', 'unlisted native archive file')
    index = json.loads(files[prefix + 'index.json'])
    expected_version = baseline['tag'][1:] if baseline is not None else generator_version
    if index['schema_version'] != 3 or not expected_version or index['generator']['version'] != expected_version:
        release.fail('integrity-error', 'native release index version differs')
    if not index['packs'] and not index['generated_productions']:
        release.fail('invalid-manifest', 'native bundle has no packs')
    contents = []
    for row in index['packs'] + index['generated_productions']:
        descriptor = row['manifest']; path = prefix + descriptor['path']; data = files[path]
        if release.digest(data) != descriptor['sha256'] or len(data) != descriptor['bytes']:
            release.fail('integrity-error', 'native manifest descriptor differs')
        manifest = json.loads(data)
        if (manifest['pack_id'], manifest['version'], manifest['language']) != (row['pack_id'], row['pack_version'], row['language']):
            release.fail('integrity-error', 'native identity differs')
        for shard in row['shards']:
            asset = shard['asset']; stored = files[prefix + asset['path']]
            if len(stored) != asset['bytes'] or release.digest(stored) != asset['sha256']:
                release.fail('integrity-error', 'native shard descriptor differs')
            if shard['encoding'] == 'deflate':
                decoder = zlib.decompressobj(-15)
                raw = decoder.decompress(stored, shard['raw_bytes'] + 1)
                if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                    release.fail('integrity-error', 'native compressed shard malformed')
            elif shard['encoding'] == 'raw':
                raw = stored
            else:
                release.fail('incompatible-schema', 'unsupported native shard encoding')
            if len(raw) != shard['raw_bytes']:
                release.fail('integrity-error', 'native shard raw size differs')
            json.loads(raw)
        schemas = release.empty_schemas(); schemas['semantic_model_read'] = [manifest['schema_version']]; schemas['release_index'] = [3]
        contents.append(dict(kind='semantic-model', identity=manifest['pack_id'], content_version=manifest['version'], completeness=manifest['completeness'], path=path, sha256=release.digest(data), languages=[manifest['language']], dependencies=[json.dumps(manifest['compatibility'], sort_keys=True)], schemas=schemas, required_capabilities=[], license=manifest['license']))
    return contents



def verify_receipt(root, config, archive, receipt_path, commit):
    import native_generation as generation
    plan_path = root / config.get('generation_config', 'native-generation.json')
    generator, config_bytes, jobs, recipes = generation._validate_config(root, plan_path)
    receipt, raw = release.load_json(receipt_path)
    if receipt['schema_version'] != 1 or receipt['source']['commit'] != commit:
        release.fail('integrity-error', 'generation source commit differs')
    plan = generation._input_plan_record(jobs, recipes)
    plan_hash = release.digest(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode())
    if (receipt['config_sha256'] != release.digest(config_bytes)
            or receipt['plan'] != plan or receipt['plan_sha256'] != plan_hash
            or receipt['generator'] != generator
            or receipt['archive']['sha256'] != release.digest(archive.read_bytes())):
        release.fail('integrity-error', 'generation inputs, tool or archive differ')
    if generator.get('build'):
        expected_build = dict(schema_version=1, generator_commit=generator['commit'],
                              source_archive_sha256=generator['asset_sha256'],
                              cargo_lock_sha256=generator['build']['cargo_lock_sha256'],
                              rust_toolchain=generator['build']['rust_toolchain'],
                              binary_sha256=receipt['binary_sha256'])
        if receipt.get('generator_build') != expected_build:
            release.fail('integrity-error', 'generator source build receipt differs')
    elif receipt['binary_sha256'] != generator['binary_sha256']:
        release.fail('integrity-error', 'generator executable differs')
    proof = receipt['reproducibility']
    if (proof['status'] != 'byte-identical-native-content'
            or proof['excluded_from_comparison'] != ['measurements.json']
            or len(proof['runs']) != 2
            or any(run['native_content_sha256'] != proof['native_content_sha256'] for run in proof['runs'])
            or receipt['qualification']['status'] != 'pending'):
        release.fail('integrity-error', 'native reproducibility evidence differs')
    files = archive_files(archive)
    prefix = 'bifrost-semantic-packs/'
    content_digest = hashlib.sha256()
    for path, data in sorted(files.items()):
        if not path.startswith(prefix):
            release.fail('integrity-error', 'native archive contains an unexpected root')
        name = path[len(prefix):]
        if name == 'measurements.json':
            continue
        encoded = name.encode()
        content_digest.update(len(encoded).to_bytes(8, 'big'))
        content_digest.update(encoded)
        content_digest.update(len(data).to_bytes(8, 'big'))
        content_digest.update(data)
    if content_digest.hexdigest() != proof['native_content_sha256']:
        release.fail('integrity-error', 'native content differs from reproduction evidence')
    measurements = []
    if len(proof['measurement_records']) != 2:
        release.fail('integrity-error', 'both original measurement records are required')
    for number, record in enumerate(proof['measurement_records'], 1):
        expected_path = f'measurements/run-{number}.json'
        if record['path'] != expected_path or record['run'] != f'run-{number}':
            release.fail('integrity-error', 'measurement record identity differs')
        path = receipt_path.parent / expected_path
        if path.is_symlink() or path.parent.is_symlink():
            release.fail('integrity-error', 'measurement records must be regular files')
        data = path.read_bytes()
        if (release.digest(data) != record['sha256']
                or record['sha256'] != proof['runs'][number - 1]['measurements_sha256']
                or record['included_in_archive'] != (number == 1)):
            release.fail('integrity-error', 'measurement bytes differ')
        if number == 1 and files[prefix + 'measurements.json'] != data:
            release.fail('integrity-error', 'archive must preserve first measurements unchanged')
        measurements.append((f'measurements-run-{number}.json', data))
    return receipt, raw, measurements


def build(root, config_path, archive, receipt_path, output, version=None):
    root = root.resolve()
    config, _ = release.load_json(config_path)
    if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip():
        release.fail('invalid-manifest', 'native release requires a clean source checkout')
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    receipt, receipt_bytes, measurements = verify_receipt(root, config, archive, receipt_path, commit)
    contents = native_contents(archive, generator_version=receipt['generator']['version'])
    if version:
        config['release_version'] = version
    release.semver(config['release_version'])
    config['artifact_role'] = 'native'
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{config['pack_id']}-{config['release_version']}-native.tar.gz"
    if target.resolve() == archive.resolve():
        release.fail('invalid-manifest', 'release output must differ from generation input')
    shutil.copyfile(archive, target)
    manifest = release.make_manifest(config, commit, contents, target)
    manifest['qualification']['evidence'] = [
        'Generated using the exact pinned tool; native verification and two-pass content comparison passed.',
        'Original timings retained separately; full consumer behavior qualification pending.'
    ]
    sidecars = [('generation.json', receipt_bytes), *measurements]
    for name, data in sidecars:
        (output / name).write_bytes(data)
        manifest['artifacts'].append(dict(name=name, sha256=release.digest(data), size_bytes=len(data), format='json', role='source'))
    release.validate_manifest(manifest)
    (output / 'pack-release.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    for item in manifest['artifacts']:
        (output / (item['name'] + '.sha256')).write_text(item['sha256'] + '  ' + item['name'] + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version')
    args = parser.parse_args()
    try:
        config = args.config if args.config.is_absolute() else args.root / args.config
        result = build(args.root, config, args.archive, args.receipt, args.output, args.version)
        print(json.dumps(dict(pack=result['pack'], artifacts=result['artifacts'], qualification=result['qualification'])))
        return 0
    except (release.ReleaseError, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f'native release failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
