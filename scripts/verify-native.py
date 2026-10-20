#!/usr/bin/env python3
"""Check copied native shard byte integrity; this does not validate model semantics."""
import hashlib
import json
from pathlib import Path
import zlib


# Go labels are the activation ecosystems emitted by
# crates/bifrost-analysis/src/analyzer/go/dependency_discovery.rs.
# Other languages currently in this repository are explicit pass-throughs until
# their discovery labels are audited against the engine source.
DISCOVERY_ECOSYSTEMS = {
    'go': {'go-module', 'go-stdlib'},
}
ALLOWED_AS_IS_LANGUAGES = {
    'cpp',
    'csharp',
    'java',
    'javascript',
    'php',
    'python',
    'ruby',
    'rust',
    'scala',
    'typescript',
}


def validate_ecosystems(root: Path) -> int:
    """Check pack sources and manifests against the reviewed ecosystem map."""
    paths = sorted((root / 'semantic-packs/models').glob('*.json'))
    paths.extend(sorted((root / 'semantic-packs/embedded').glob('*/manifest.json')))
    checked = 0
    for path in paths:
        pack = json.loads(path.read_text())
        language = pack.get('language')
        ecosystem = pack.get('ecosystem')
        if language in DISCOVERY_ECOSYSTEMS:
            if ecosystem not in DISCOVERY_ECOSYSTEMS[language]:
                allowed = ', '.join(sorted(DISCOVERY_ECOSYSTEMS[language]))
                raise ValueError(
                    f'invalid ecosystem {ecosystem!r} for {language} pack {path}; '
                    f'engine discovery emits: {allowed}'
                )
        elif language not in ALLOWED_AS_IS_LANGUAGES:
            raise ValueError(
                f'no ecosystem validation policy for language {language!r} in {path}'
            )
        checked += 1
    if not paths:
        raise ValueError('no semantic pack sources or manifests')
    return checked


def verify(root: Path) -> dict:
    manifests = sorted((root / 'semantic-packs/embedded').glob('*/manifest.json'))
    ecosystem_count = validate_ecosystems(root)
    count = 0
    for path in manifests:
        manifest = json.loads(path.read_text())
        if manifest['schema_version'] not in range(2, 7):
            raise ValueError(f'unsupported native schema: {path}')
        shards = list((path.parent / 'shards').iterdir())
        claimed = set()
        for descriptor in manifest['shards']:
            candidates = [p for p in shards if p.name == descriptor['shard_id'] + ('.deflate' if descriptor['encoding'] == 'deflate' else '.json')]
            if len(candidates) != 1:
                raise ValueError(f'missing or ambiguous shard: {path}: {descriptor["shard_id"]}')
            shard = candidates[0]
            if shard.is_symlink() or not shard.is_file():
                raise ValueError(f'invalid shard path: {shard}')
            data = shard.read_bytes()
            if len(data) != descriptor['stored_size'] or hashlib.sha256(data).hexdigest() != descriptor['stored_sha256']:
                raise ValueError(f'stored shard integrity mismatch: {shard}')
            if descriptor['encoding'] == 'deflate':
                decoder = zlib.decompressobj(-15)
                raw = decoder.decompress(data, descriptor['raw_size'] + 1)
                if decoder.unconsumed_tail or decoder.unused_data or not decoder.eof:
                    raise ValueError(f'invalid compressed shard: {shard}')
            elif descriptor['encoding'] == 'raw':
                raw = data
            else:
                raise ValueError(f'unsupported shard encoding: {shard}')
            if len(raw) != descriptor['raw_size']:
                raise ValueError(f'raw shard size mismatch: {shard}')
            json.loads(raw)
            claimed.add(shard)
            count += 1
        if claimed != set(shards):
            raise ValueError(f'unlisted native shards: {path}')
    if not manifests:
        raise ValueError('no native manifests')
    return {
        'manifests': len(manifests),
        'shards': count,
        'ecosystems_checked': ecosystem_count,
        'outcome': 'byte-integrity-verified',
        'semantics': 'not-qualified',
    }


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), sort_keys=True))
