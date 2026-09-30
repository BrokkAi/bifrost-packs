import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('native', ROOT / 'scripts/verify-native.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeIntegrityTests(unittest.TestCase):
    def test_copied_native_inventory(self):
        result = native.verify(ROOT)
        self.assertEqual((result['manifests'], result['shards']), (42, 48))
        self.assertEqual(result['semantics'], 'not-qualified')

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
