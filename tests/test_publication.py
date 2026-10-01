import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'release-contract'))
import publication
import release


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = self.root / 'rules.tar.gz'
        self.archive.write_bytes(b'publication integrity fixture')
        self.config = dict(pack_id='test.rules', repository='https://github.com/test/public', visibility='public', release_version='0.1.1', artifact_role='source')
        self.manifest = release.make_manifest(self.config, 'a' * 40, [], self.archive)
        self.manifest['qualification']['integrity'] = dict(status='verified', evidence=['fixture bytes checked'])

    def test_pending_behavior_does_not_block_verified_format(self):
        publication.verify_publication(self.manifest, self.root)

    def test_failed_behavior_and_corrupt_bytes_reject(self):
        self.manifest['qualification']['behavior'] = dict(status='failed', evidence=['fixture failure'])
        with self.assertRaises(release.ReleaseError):
            publication.verify_publication(self.manifest, self.root)
        self.manifest['qualification']['behavior']['status'] = 'pending'
        self.archive.write_bytes(b'corrupt')
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(self.manifest, self.root)
        self.assertEqual(caught.exception.code, 'integrity-error')

    def test_exact_dependency_repository_and_version_required(self):
        self.manifest['release_dependencies'] = [dict(pack_id='test.rules', repository=self.config['repository'], release_version='0.1.0')]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(self.manifest, self.root, [self.manifest])
        self.assertEqual(caught.exception.code, 'no-compatible-release')
        dependency = json.loads(json.dumps(self.manifest))
        dependency['release_version'] = '0.1.0'
        dependency['release_dependencies'] = []
        publication.verify_publication(self.manifest, self.root, [dependency])
        dependency['pack']['repository'] = dependency['source']['repository'] = 'https://github.com/test/other'
        with self.assertRaises(release.ReleaseError):
            publication.verify_publication(self.manifest, self.root, [dependency])

    def test_native_inner_engine_gate_cannot_be_hidden_by_release_metadata(self):
        native = self.root / 'native.tar.gz'
        data = json.dumps(dict(pack_id='test.native', compatibility=dict(bifrost='=0.12.0'))).encode()
        with tarfile.open(native, 'w:gz') as output:
            entry = tarfile.TarInfo('bifrost-semantic-packs/manifests/test.json')
            entry.size = len(data)
            output.addfile(entry, io.BytesIO(data))
        self.manifest['artifacts'] = [dict(name=native.name, sha256=release.digest(native.read_bytes()), size_bytes=native.stat().st_size, format='tar.gz', role='native')]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(self.manifest, self.root)
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        self.assertIn('native compatibility.bifrost', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
