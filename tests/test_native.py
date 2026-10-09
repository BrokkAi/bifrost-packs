import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native', ROOT / 'scripts/verify-native.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeIntegrityTests(unittest.TestCase):
    def test_copied_native_inventory(self):
        result = native.verify(ROOT)
        self.assertEqual((result['manifests'], result['shards']), (43, 49))
        self.assertEqual(result['semantics'], 'not-qualified')

    def test_go_embed_pack_identity_and_content(self):
        manifest_path = ROOT / 'semantic-packs/embedded/go-stdlib-embed-declarations/manifest.json'
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest['pack_id'], 'bifrost.go.stdlib.embed-declarations')
        self.assertEqual(manifest['language'], 'go')
        self.assertEqual(manifest['provenance']['revision'], 'go1.26.0')
        self.assertEqual(manifest['license'], 'BSD-3-Clause')

        descriptor = manifest['shards'][0]
        self.assertEqual(descriptor['shard_id'], 'go.stdlib.embed.declarations')
        self.assertEqual(descriptor['record_count'], 3)
        shard_path = manifest_path.parent / 'shards' / (descriptor['shard_id'] + '.deflate')
        raw = zlib.decompress(shard_path.read_bytes(), -15)
        payload = json.loads(raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), descriptor['content_sha256'])
        self.assertEqual(descriptor['content_sha256'], 'd2d6e5060c5b3d7a1c608edbbd2a881ea55abda8b2c4ea5686003446925a6846')
        self.assertEqual(payload['pack_id'], manifest['pack_id'])
        self.assertEqual(payload['shard_id'], descriptor['shard_id'])
        self.assertEqual(
            {(entry['name'], entry['visibility']) for entry in payload['payload']['types']},
            {('embed', 'package'), ('embed.FS', 'public')},
        )
        self.assertEqual(payload['payload']['members'][0]['name'], 'Open')
        self.assertEqual(payload['payload']['members'][0]['locator']['symbol'], 'embed.FS.Open')
        model = json.loads(
            (ROOT / 'semantic-packs/models/go-stdlib-embed-declarations.json').read_text()
        )
        self.assertEqual(model['pack_id'], manifest['pack_id'])
        self.assertEqual(model['shards'][0]['id'], descriptor['shard_id'])
        self.assertEqual(model['shards'][0]['payload'], payload['payload'])

    def test_altered_shard_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / 'semantic-packs/embedded'
            shutil.copytree(ROOT / 'semantic-packs/embedded/python-process-inputs', destination / 'python-process-inputs')
            shard = next((destination / 'python-process-inputs/shards').iterdir())
            shard.write_bytes(shard.read_bytes() + b'corrupt')
            with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
                native.verify(root)

    def test_unlisted_shard_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / 'semantic-packs/embedded'
            shutil.copytree(ROOT / 'semantic-packs/embedded/python-process-inputs', destination / 'python-process-inputs')
            (destination / 'python-process-inputs/shards/extra.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'unlisted'):
                native.verify(root)
