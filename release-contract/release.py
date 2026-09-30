#!/usr/bin/env python3
"""Shared, offline-first pack release contract. No engine defaults are changed."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name('manifest.schema.json')
SCHEMA_KEYS = ('policy_document', 'rql', 'builtin_catalog', 'policy_bundle', 'semantic_model_read', 'semantic_model_write', 'semantic_spec', 'release_index', 'runtime')
ERROR_EXIT = {'no-compatible-release': 2, 'invalid-manifest': 3, 'unsupported-manifest-schema': 4, 'incompatible-schema': 5, 'unavailable-credentials/network': 6, 'integrity-error': 7}


class ReleaseError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def fail(code, message):
    raise ReleaseError(code, message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail('invalid-manifest', f'duplicate JSON key: {key}')
            result[key] = value
        return result
    try:
        raw = Path(path).read_bytes()
        return json.loads(raw, object_pairs_hook=unique), raw
    except (OSError, ValueError) as error:
        fail('invalid-manifest', f'cannot read JSON {path}: {error}')


def _validate(value, schema, root, location='$'):
    """Validate the exact JSON Schema subset used by our canonical schema."""
    if '$ref' in schema:
        target = root
        for key in schema['$ref'].removeprefix('#/').split('/'):
            target = target[key]
        return _validate(value, target, root, location)
    if 'oneOf' in schema:
        valid = 0
        for branch in schema['oneOf']:
            try:
                _validate(value, branch, root, location)
                valid += 1
            except ReleaseError:
                pass
        if valid != 1:
            fail('invalid-manifest', f'{location}: expected one schema alternative')
        return
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    kind = schema.get('type')
    if kind and (not isinstance(value, types[kind]) or kind == 'integer' and isinstance(value, bool)):
        fail('invalid-manifest', f'{location}: expected {kind}')
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])):
        fail('invalid-manifest', f'{location}: invalid constant')
    if 'enum' in schema and value not in schema['enum']:
        fail('invalid-manifest', f'{location}: unsupported value')
    if kind == 'object':
        missing = set(schema.get('required', [])) - set(value)
        if missing:
            fail('invalid-manifest', f'{location}: missing {sorted(missing)}')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and set(value) - set(properties):
            fail('invalid-manifest', f'{location}: unknown fields {sorted(set(value)-set(properties))}')
        for key, child in value.items():
            if key in properties:
                _validate(child, properties[key], root, location + '.' + key)
    elif kind == 'array':
        if len(value) < schema.get('minItems', 0):
            fail('invalid-manifest', f'{location}: too few entries')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            fail('invalid-manifest', f'{location}: duplicate entries')
        for index, child in enumerate(value):
            _validate(child, schema['items'], root, f'{location}[{index}]')
    elif kind == 'string':
        if len(value) < schema.get('minLength', 0) or 'pattern' in schema and not re.fullmatch(schema['pattern'], value):
            fail('invalid-manifest', f'{location}: invalid string')
        if schema.get('format') == 'uri' and not value.startswith('https://'):
            fail('invalid-manifest', f'{location}: HTTPS URI required')
    elif kind == 'integer' and value < schema.get('minimum', value):
        fail('invalid-manifest', f'{location}: below minimum')


def semver(version):
    schema, _ = load_json(SCHEMA_PATH)
    _validate(version, schema['$defs']['semver'], schema)
    main = version.split('+', 1)[0]
    base, separator, pre = main.partition('-')
    identifiers = tuple((0, int(v)) if v.isdigit() else (1, v) for v in pre.split('.')) if separator else ()
    return (*map(int, base.split('.')), 0 if separator else 1, identifiers)


def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or any(p in ('', '.', '..') for p in value.split('/')):
        fail('invalid-manifest', f'unsafe relative path: {value!r}')
    return value


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        fail('invalid-manifest', 'manifest must be an object')
    if manifest.get('manifest_schema_version') != 1:
        fail('unsupported-manifest-schema', 'only release manifest schema 1 is supported')
    schema, _ = load_json(SCHEMA_PATH)
    _validate(manifest, schema, schema)
    if manifest['source']['repository'] != manifest['pack']['repository'] or manifest['source']['dirty']:
        fail('invalid-manifest', 'release source must be the clean pack repository commit')
    engine = manifest['compatibility']['engine']
    if semver(engine['min_inclusive']) >= semver(engine['max_exclusive']):
        fail('invalid-manifest', 'engine range is empty')
    required_caps = set(manifest['compatibility']['capabilities']['required'])
    declared_schemas = manifest['compatibility']['schemas']
    seen = set()
    for item in manifest['contents']:
        safe_path(item['path'])
        key = (item['kind'], item['identity'], item['path'])
        if key in seen:
            fail('invalid-manifest', 'duplicate content identity/path')
        seen.add(key)
        if not set(item['required_capabilities']) <= required_caps:
            fail('invalid-manifest', 'content capability missing from release requirements')
        if any(not set(values) <= set(declared_schemas[axis]) for axis, values in item['schemas'].items()):
            fail('invalid-manifest', 'content schema missing from release requirements')
    names = []
    for artifact in manifest['artifacts']:
        safe_path(artifact['name'])
        if '/' in artifact['name']:
            fail('invalid-manifest', 'artifact name must be a filename')
        names.append(artifact['name'])
    if len(set(names)) != len(names):
        fail('invalid-manifest', 'duplicate artifact filename')
    if manifest['qualification']['status'] == 'qualified' and not manifest['qualification']['evidence']:
        fail('invalid-manifest', 'qualified content requires evidence')
    return manifest


def validate_profile(profile):
    required = {'engine_version', 'build_identity', 'model_set_sha256', 'capability_contract_version', 'schemas', 'capabilities'}
    if not isinstance(profile, dict) or not required <= profile.keys():
        fail('invalid-manifest', 'engine profile requires exact build/model identity, schemas and capabilities')
    semver(profile['engine_version'])
    schema, _ = load_json(SCHEMA_PATH)
    _validate(profile['schemas'], schema['$defs']['schema-set'], schema)
    _validate(profile['capabilities'], schema['$defs']['string-set'], schema)
    if not isinstance(profile['build_identity'], str) or not profile['build_identity'] or not re.fullmatch('[0-9a-f]{64}', profile['model_set_sha256']):
        fail('invalid-manifest', 'engine build/model identity invalid')
    if type(profile['capability_contract_version']) is not int or profile['capability_contract_version'] != 1:
        fail('incompatible-schema', 'unsupported capability contract')
    return profile


def resolve_candidate(paths, profile, pack_id, channel='stable', version=None, commit=None, allow_unqualified=False):
    validate_profile(profile)
    if channel not in ('stable', 'prerelease'):
        fail('invalid-manifest', 'channel must be stable or prerelease')
    if version:
        semver(version)
    if commit and not re.fullmatch('[0-9a-f]{40}', commit):
        fail('invalid-manifest', 'commit pin must be a full SHA')
    eligible = []
    identities = {}
    schema_blocked = False
    for path in paths:
        manifest, raw = load_json(path)
        validate_manifest(manifest)
        if manifest['pack']['id'] != pack_id:
            continue
        current_version = manifest['release_version']
        if version and current_version != version or commit and manifest['source']['commit'] != commit:
            continue
        key = semver(current_version)
        if (key[3] == 1) != (channel == 'stable'):
            continue
        if key in identities and identities[key] != digest(raw):
            fail('invalid-manifest', 'ambiguous release versions with equal SemVer precedence')
        identities[key] = digest(raw)
        compatibility = manifest['compatibility']
        bounds = compatibility['engine']
        if not semver(bounds['min_inclusive']) <= semver(profile['engine_version']) < semver(bounds['max_exclusive']):
            continue
        caps = compatibility['capabilities']
        if caps['contract_version'] != profile['capability_contract_version'] or not set(caps['required']) <= set(profile['capabilities']):
            continue
        if any(not set(values) <= set(profile['schemas'][axis]) for axis, values in compatibility['schemas'].items()):
            schema_blocked = True
            continue
        if not allow_unqualified and (manifest['qualification']['status'] != 'qualified' or not any(a['role'] in ('native', 'policy') for a in manifest['artifacts'])):
            continue
        eligible.append((key, str(path), manifest, digest(raw)))
    if not eligible:
        fail('incompatible-schema' if schema_blocked else 'no-compatible-release', 'no release satisfies schemas, capabilities, engine range, channel, pins and qualification')
    return max(eligible, key=lambda item: (item[0], item[1]))


def verify_artifact(artifact, path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        fail('unavailable-credentials/network', f'artifact not available in verified cache: {artifact["name"]}')
    raw = path.read_bytes()
    if len(raw) != artifact['size_bytes'] or digest(raw) != artifact['sha256']:
        fail('integrity-error', f'artifact hash/size mismatch: {artifact["name"]}')
    return artifact


def resolve_release_set(paths, profile, pack_id, channel='stable', version=None, commit=None, allow_unqualified=False, visiting=()):
    candidate = resolve_candidate(paths, profile, pack_id, channel, version, commit, allow_unqualified)
    manifest = candidate[2]
    key = (pack_id, manifest['release_version'])
    if key in visiting:
        fail('invalid-manifest', 'cyclic release dependencies')
    result = [candidate]
    for dependency in manifest.get('release_dependencies', []):
        if dependency['repository'] != manifest['pack']['repository']:
            fail('no-compatible-release', 'dependency requires explicit discovery of another repository')
        dependency_channel = 'stable' if semver(dependency['release_version'])[3] else 'prerelease'
        result.extend(resolve_release_set(paths, profile, dependency['pack_id'], dependency_channel, dependency['release_version'], None, allow_unqualified, visiting + (key,)))
    return result


def select_release(paths, profile, pack_id, channel='stable', version=None, commit=None, cache_dir=None, allow_unqualified=False):
    candidates = resolve_release_set(paths, profile, pack_id, channel, version, commit, allow_unqualified)
    _, path, manifest, manifest_hash = candidates[0]
    dependencies = []
    for _, dependency_path, dependency_manifest, dependency_hash in candidates[1:]:
        for artifact in dependency_manifest['artifacts']:
            parent = Path(cache_dir) / artifact['sha256'] if cache_dir else Path(dependency_path).parent
            verify_artifact(artifact, parent / artifact['name'])
        dependencies.append(dict(pack_id=dependency_manifest['pack']['id'], release_version=dependency_manifest['release_version'], source_commit=dependency_manifest['source']['commit'], manifest_sha256=dependency_hash, artifacts=dependency_manifest['artifacts']))
    artifacts = []
    for artifact in manifest['artifacts']:
        parent = Path(cache_dir) / artifact['sha256'] if cache_dir else Path(path).parent
        verify_artifact(artifact, parent / artifact['name'])
        artifacts.append(artifact)
    return {'dependencies': dependencies, 'receipt_schema_version': 1, 'pack_id': pack_id, 'release_version': manifest['release_version'], 'source_commit': manifest['source']['commit'], 'manifest_sha256': manifest_hash, 'engine_profile': profile, 'qualification': manifest['qualification'], 'artifacts': artifacts}


def empty_schemas():
    return {key: [] for key in SCHEMA_KEYS}


def expected_tag(manifest):
    prefix = {'bifrost.public.rules': 'rules/', 'bifrost.public.packs': 'packs/'}.get(manifest['pack']['id'], '')
    return prefix + 'v' + manifest['release_version']


def public_contents(root, lock, component=None):
    entries = lock['files']
    expected = digest(''.join(f"{e['sha256']}  {e['path']}\n" for e in sorted(entries, key=lambda e: e['path'])).encode())
    if expected != lock['aggregate_sha256']:
        fail('integrity-error', 'content lock aggregate differs')
    locked = {}
    for entry in entries:
        path = safe_path(entry['path'])
        if path in locked:
            fail('invalid-manifest', 'duplicate locked path')
        if digest((root / path).read_bytes()) != entry['sha256']:
            fail('integrity-error', f'locked bytes differ: {path}')
        locked[path] = entry
    contents = []
    for path, entry in locked.items():
        if path.startswith('rules/') and path.endswith('/manifest.json'):
            native, _ = load_json(root / path)
            parent = path.rsplit('/', 1)[0]
            schemas = empty_schemas(); schemas['builtin_catalog'] = [native['schema_version']]
            contents.append(dict(kind='policy-pack', identity=native['id'], path=path, sha256=entry['sha256'], languages=sorted({v for p in native['policies'] for v in p['supported_languages']}), dependencies=[], schemas=schemas, required_capabilities=[]))
            for policy in native['policies']:
                policy_path = parent + '/' + safe_path(policy['path'])
                if policy_path not in locked:
                    fail('integrity-error', f'missing policy: {policy_path}')
                schemas = empty_schemas(); schemas['policy_document'] = [1]; schemas['rql'] = [1]
                contents.append(dict(kind='policy', identity=policy['id'], path=policy_path, sha256=locked[policy_path]['sha256'], languages=policy['supported_languages'], dependencies=policy.get('dependencies', []), schemas=schemas, required_capabilities=policy['required_capabilities'], authored_hash=policy['authored_hash'], resolved_semantic_hash=policy.get('resolved_semantic_hash')))
        elif path.startswith('semantic-packs/') and path.endswith('.json'):
            native, _ = load_json(root / path)
            if isinstance(native, dict) and {'pack_id', 'producer', 'shards', 'language'} <= native.keys():
                schemas = empty_schemas(); schemas['semantic_model_read'] = [native['schema_version']]
                dependencies = [json.dumps(native[k], sort_keys=True, separators=(',', ':')) for k in ('compatibility', 'provenance') if k in native]
                contents.append(dict(kind='semantic-model', identity=native['pack_id'], path=path, sha256=entry['sha256'], languages=[native['language']], dependencies=dependencies, schemas=schemas, required_capabilities=[], license=native.get('license', entry['license'])))
            elif isinstance(native, dict) and {'pack_id', 'artifact', 'kind'} <= native.keys():
                schemas = empty_schemas(); schemas['semantic_spec'] = [native['schema_version']]
                contents.append(dict(kind='semantic-spec', identity=native['pack_id'], path=path, sha256=entry['sha256'], languages=[], dependencies=[json.dumps(native['artifact'], sort_keys=True, separators=(',', ':'))], schemas=schemas, required_capabilities=[], license=entry['license']))
    if component is not None:
        kinds = {'rules': {'policy', 'policy-pack'}, 'packs': {'semantic-model', 'semantic-spec'}}
        if component not in kinds: fail('invalid-manifest', 'unknown release component')
        contents = [item for item in contents if item['kind'] in kinds[component]]
    return sorted(contents, key=lambda row: (row['kind'], row['identity'], row['path']))


def make_manifest(config, commit, contents, archive, origin=None):
    aggregate = empty_schemas()
    for item in contents:
        for axis, values in item['schemas'].items():
            aggregate[axis] = sorted(set(aggregate[axis]) | set(values))
    manifest = dict(manifest_schema_version=1, pack=dict(id=config['pack_id'], repository=config['repository'], visibility=config['visibility']), release_version=config['release_version'], source=dict(repository=config['repository'], commit=commit, dirty=False), compatibility=dict(engine=dict(min_inclusive=config['engine_min_inclusive'], max_exclusive=config['engine_max_exclusive']), schemas=aggregate, capabilities=dict(contract_version=1, required=sorted({v for item in contents for v in item['required_capabilities']}), provided=[])), contents=contents, artifacts=[dict(name=archive.name, sha256=digest(archive.read_bytes()), size_bytes=archive.stat().st_size, format='tar.gz' if archive.name.endswith('.tar.gz') else 'zip', role=config['artifact_role'])], qualification=dict(status='pending', evidence=[]))
    if config.get('release_dependencies'):
        manifest['release_dependencies'] = config['release_dependencies']
    if origin:
        manifest['content_origin'] = origin
    return validate_manifest(manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create'); create.add_argument('--root', type=Path, default=Path.cwd()); create.add_argument('--archive', type=Path, required=True); create.add_argument('--output', type=Path, required=True); create.add_argument('--config', type=Path, default=Path('release-config.json')); create.add_argument('--version')
    select = commands.add_parser('select'); select.add_argument('--engine-profile', type=Path, required=True); select.add_argument('--pack-id', required=True); select.add_argument('--channel', choices=['stable', 'prerelease'], default='stable'); select.add_argument('--version'); select.add_argument('--commit'); select.add_argument('--cache-dir', type=Path); select.add_argument('--allow-unqualified', action='store_true'); select.add_argument('--receipt', type=Path, required=True); select.add_argument('manifests', nargs='+', type=Path)
    verify = commands.add_parser('verify-artifact'); verify.add_argument('--manifest', type=Path, required=True); verify.add_argument('--artifact', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'create':
            root = args.root.resolve(); config, _ = load_json(args.config); lock, raw = load_json(root / 'content-lock.json')
            if args.version: config['release_version'] = args.version
            status = subprocess.run(['git', '-C', str(root), 'status', '--porcelain'], capture_output=True, text=True, check=True)
            if status.stdout.strip(): fail('invalid-manifest', 'release creation requires clean source checkout')
            commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
            origin = dict(repository=lock['source']['repository'], commit=lock['source']['revision'], lock_sha256=digest(raw))
            result = make_manifest(config, commit, public_contents(root, lock, config.get('component')), args.archive, origin)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        elif args.command == 'select':
            profile, _ = load_json(args.engine_profile)
            result = select_release(args.manifests, profile, args.pack_id, args.channel, args.version, args.commit, args.cache_dir, args.allow_unqualified)
            args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        else:
            manifest, _ = load_json(args.manifest); validate_manifest(manifest)
            artifact = next((a for a in manifest['artifacts'] if a['name'] == args.artifact.name), None)
            if artifact is None: fail('invalid-manifest', 'artifact not indexed')
            result = verify_artifact(artifact, args.artifact)
        print(json.dumps(result, sort_keys=True))
        return 0
    except ReleaseError as error:
        print(json.dumps({'error': error.code, 'message': str(error)}), file=sys.stderr)
        return ERROR_EXIT[error.code]
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({'error': 'invalid-manifest', 'message': str(error)}), file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
