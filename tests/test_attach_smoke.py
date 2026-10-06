import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'release-contract'))
import attach_smoke
import release
import test_smoke
from scripts.smoke import run_smoke


class SmokeAttachmentTests(unittest.TestCase):
    def setUp(self):
        fixture = test_smoke.SmokeHarnessTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.evidence = fixture.root / 'evidence'
        self.summary = run_smoke(fixture.fake_binary, self.evidence, repository_root=fixture.repo)
        self.output = fixture.root / 'dist'
        self.output.mkdir()
        archive = self.output / 'rules.tar.gz'
        archive.write_bytes(b'fixture archive')
        schemas = release.empty_schemas()
        schemas['policy_document'] = schemas['rql'] = [1]
        policy = fixture.repo / 'rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp'
        contents = [dict(kind='policy', identity=self.summary['policy_id'], path='rules/dynamic-evaluation.rqlp', sha256=release.digest(policy.read_bytes()), authored_hash=self.summary['policy_authored_hash'], languages=['python'], dependencies=[], schemas=schemas, required_capabilities=[])]
        config = dict(pack_id='test.rules', repository='https://github.com/test/public', visibility='public', release_version='0.1.1', artifact_role='source')
        config['provenance'] = dict(engine_version='0.11.5', source_commit='c' * 40)
        self.manifest = release.make_manifest(config, 'a' * 40, contents, archive)
        self.path = self.output / 'pack-release.json'
        self.path.write_text(json.dumps(self.manifest))

    def test_complete_narrow_evidence_is_hashed_and_remains_limited(self):
        manifest = attach_smoke.attach(self.path, self.evidence, self.output)
        self.assertEqual(manifest['qualification']['behavior']['status'], 'limited')
        self.assertEqual(manifest['qualification']['integrity']['status'], 'pending')
        self.assertEqual(manifest['provenance']['testing'][0]['engine_version'], '9.8.7')
        self.assertEqual(manifest['provenance']['source_commit'], 'c' * 40)
        self.assertEqual(manifest['provenance']['engine_version'], '0.11.5')
        self.assertNotIn('engine', manifest['compatibility'])
        for artifact in manifest['artifacts']:
            release.verify_artifact(artifact, self.output / artifact['name'])

    def test_corrupt_raw_report_is_not_attached_as_success(self):
        (self.evidence / self.summary['runs'][0]['raw_report']).write_text('{}')
        with self.assertRaises(release.ReleaseError) as caught:
            attach_smoke.attach(self.path, self.evidence, self.output)
        self.assertEqual(caught.exception.code, 'integrity-error')

    def test_empty_evidence_is_preserved_in_reproducible_zip(self):
        empty = self.evidence / 'runs' / 'positive' / 'stderr.txt'
        empty.write_bytes(b'')
        expected = {p.relative_to(self.evidence).as_posix(): p.read_bytes()
                    for p in self.evidence.rglob('*') if p.is_file()}
        manifest = attach_smoke.attach(self.path, self.evidence, self.output)
        self.assertTrue(all(a['size_bytes'] > 0 for a in manifest['artifacts']))
        archive = self.output / 'smoke-evidence.zip'
        original = archive.read_bytes()
        with zipfile.ZipFile(archive) as evidence:
            self.assertEqual({name: evidence.read(name) for name in evidence.namelist()}, expected)
        self.path.write_text(json.dumps(self.manifest))
        attach_smoke.attach(self.path, self.evidence, self.output)
        self.assertEqual(archive.read_bytes(), original)

    def test_failed_summary_is_not_attached(self):
        self.summary['status'] = 'failed'
        (self.evidence / 'smoke.json').write_text(json.dumps(self.summary))
        with self.assertRaises(release.ReleaseError):
            attach_smoke.attach(self.path, self.evidence, self.output)


if __name__ == '__main__':
    unittest.main()
