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
        self.assertEqual((result['manifests'], result['shards']), (45, 49))
        self.assertGreater(result['ecosystems_checked'], 0)
        self.assertEqual(result['semantics'], 'not-qualified')

    def test_go_ecosystem_validation_rejects_the_legacy_label(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            models = root / 'semantic-packs/models'
            embedded = root / 'semantic-packs/embedded/go-module-pack'
            models.mkdir(parents=True)
            (embedded / 'shards').mkdir(parents=True)
            model = models / 'go-module-pack.json'
            manifest = embedded / 'manifest.json'

            model.write_text(json.dumps({'language': 'go', 'ecosystem': 'go-stdlib'}))
            manifest.write_text(json.dumps({'language': 'go', 'ecosystem': 'go-module'}))
            self.assertEqual(native.validate_ecosystems(root), 2)

            model.write_text(json.dumps({'language': 'go', 'ecosystem': 'go'}))
            with self.assertRaisesRegex(ValueError, "invalid ecosystem 'go'"):
                native.validate_ecosystems(root)

    def test_go_concurrency_errgroup_is_split_into_module_packs(self):
        expected = {
            'go-concurrency-errgroup': (
                'bifrost.go.concurrency.errgroup',
                'go.concurrency.errgroup',
            ),
            'go-concurrency-errgroup-declarations': (
                'bifrost.go.concurrency.errgroup-declarations',
                'go.concurrency.errgroup.declarations',
            ),
        }
        for directory, (pack_id, shard_id) in expected.items():
            manifest = json.loads(
                (ROOT / f'semantic-packs/embedded/{directory}/manifest.json').read_text()
            )
            model = json.loads(
                (ROOT / f'semantic-packs/models/{directory}.json').read_text()
            )
            self.assertEqual((manifest['pack_id'], manifest['version'], manifest['ecosystem']),
                             (pack_id, '1.0.0', 'go-module'))
            self.assertEqual((model['pack_id'], model['version'], model['ecosystem']),
                             (pack_id, '1.0.0', 'go-module'))
            self.assertEqual([item['shard_id'] for item in manifest['shards']], [shard_id])
            self.assertEqual([item['id'] for item in model['shards']], [shard_id])

        for directory in ('go-concurrency', 'go-concurrency-declarations'):
            manifest = json.loads(
                (ROOT / f'semantic-packs/embedded/{directory}/manifest.json').read_text()
            )
            self.assertEqual((manifest['version'], manifest['ecosystem']), ('2.0.0', 'go-stdlib'))
            self.assertTrue(all('errgroup' not in item['shard_id'] for item in manifest['shards']))

    def test_go_embed_pack_identity_and_content(self):
        manifest_path = ROOT / 'semantic-packs/embedded/go-stdlib-embed-declarations/manifest.json'
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest['pack_id'], 'bifrost.go.stdlib.embed-declarations')
        self.assertEqual((manifest['version'], manifest['ecosystem']), ('2.0.0', 'go-stdlib'))
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
        self.assertEqual(descriptor['content_sha256'], 'e4d9d98bc3bf03ed567b143b3fde7f25491924f0c21780ac2a488419cc9045e1')
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
