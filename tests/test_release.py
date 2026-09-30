import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'release-contract'))
import release


def profile():
    return dict(engine_version='0.12.0', build_identity='test-only-build', model_set_sha256='a'*64, capability_contract_version=1, schemas={k: [1,2,3,4,5,6,7] for k in release.SCHEMA_KEYS}, capabilities=['structural-match'])


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.archive = self.root / 'pack.tar.gz'; self.archive.write_bytes(b'content')
        self.config = dict(pack_id='test.public', repository='https://github.com/test/public', visibility='public', release_version='1.0.0', engine_min_inclusive='0.11.0', engine_max_exclusive='0.13.0', artifact_role='policy')

    def candidate(self, version, **kwargs):
        config = dict(self.config, release_version=version)
        manifest = release.make_manifest(config, 'b'*40, [], self.archive)
        manifest['qualification'] = dict(status='qualified', evidence=['fixture-only'])
        manifest['compatibility']['capabilities']['required'] = kwargs.get('capabilities', [])
        if 'schema' in kwargs: manifest['compatibility']['schemas']['policy_document'] = [kwargs['schema']]
        if 'minimum' in kwargs: manifest['compatibility']['engine']['min_inclusive'] = kwargs['minimum']
        path = self.root / (version + '.json'); path.write_text(json.dumps(manifest)); return path

    def test_filter_before_newest(self):
        old = self.candidate('1.0.0'); future = self.candidate('2.0.0', minimum='0.12.1'); caps = self.candidate('3.0.0', capabilities=['unavailable'])
        receipt = release.select_release([caps, future, old], profile(), 'test.public')
        self.assertEqual(receipt['release_version'], '1.0.0'); self.assertEqual(receipt['source_commit'], 'b'*40)

    def test_channels_and_semver(self):
        candidates = [self.candidate(v) for v in ['1.9.0','1.10.0','2.0.0-rc.2','2.0.0-rc.10']]
        self.assertEqual(release.select_release(candidates, profile(), 'test.public')['release_version'], '1.10.0')
        self.assertEqual(release.select_release(candidates, profile(), 'test.public', 'prerelease')['release_version'], '2.0.0-rc.10')

    def test_pins_and_offline_integrity(self):
        old = self.candidate('1.0.0'); new = self.candidate('1.1.0')
        self.assertEqual(release.select_release([old,new], profile(), 'test.public', version='1.0.0')['release_version'], '1.0.0')
        self.archive.write_bytes(b'corrupt')
        with self.assertRaises(release.ReleaseError) as caught: release.select_release([old], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'integrity-error')

    def test_missing_cache_and_no_compatible(self):
        path = self.candidate('1.0.0'); self.archive.unlink()
        with self.assertRaises(release.ReleaseError) as caught: release.select_release([path], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'unavailable-credentials/network')
        with self.assertRaises(release.ReleaseError) as caught: release.select_release([path], profile(), 'test.public', commit='c'*40)
        self.assertEqual(caught.exception.code, 'no-compatible-release')

    def test_schema_and_invalid_manifest(self):
        path = self.candidate('1.0.0', schema=99)
        with self.assertRaises(release.ReleaseError) as caught: release.select_release([path], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        manifest = json.loads(path.read_text()); manifest['manifest_schema_version'] = 99
        with self.assertRaises(release.ReleaseError) as caught: release.validate_manifest(manifest)
        self.assertEqual(caught.exception.code, 'unsupported-manifest-schema')

    def test_source_pending_not_runtime_eligible(self):
        manifest = release.make_manifest(dict(self.config, artifact_role='source'), 'b'*40, [], self.archive)
        path = self.root/'source.json'; path.write_text(json.dumps(manifest))
        with self.assertRaises(release.ReleaseError): release.select_release([path], profile(), 'test.public')
        self.assertEqual(release.select_release([path], profile(), 'test.public', allow_unqualified=True)['qualification']['status'], 'pending')

    def test_actual_copy_index_has_policy_hashes(self):
        lock = json.loads((ROOT/'content-lock.json').read_text()); contents = release.public_contents(ROOT,lock)
        policies = [row for row in contents if row['kind']=='policy']
        manifests = [json.loads(p.read_text()) for p in (ROOT/'rules').glob('*/manifest.json')]
        self.assertEqual(len(policies),sum(len(p['policies']) for p in manifests))
        self.assertTrue(all(len(p['authored_hash'])==64 for p in policies))
        release.make_manifest(dict(self.config, artifact_role='source'), 'b'*40, contents,self.archive)

    def test_missing_profile_and_ambiguous_precedence(self):
        with self.assertRaises(release.ReleaseError): release.validate_profile({'engine_version':'0.12.0'})
        paths = [self.candidate('1.0.0+x'), self.candidate('1.0.0+y')]
        with self.assertRaises(release.ReleaseError): release.select_release(paths, profile(), 'test.public')

if __name__ == '__main__': unittest.main()
