import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'release-contract'))
import discover
import release


class DiscoveryTests(unittest.TestCase):
    def test_offline_v3_discovery_forwards_independent_host_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / 'pack.zip'
            archive.write_bytes(b'bytes')
            config = dict(
                pack_id='test.public',
                repository='https://github.com/test/public',
                visibility='public',
                release_version='1.0.0',
                artifact_role='source',
            )
            content = dict(
                kind='policy',
                identity='synthetic.policy',
                path='rules/synthetic.rqlp',
                sha256='c' * 64,
                languages=['python'],
                dependencies=[],
                schemas=release.empty_schemas(),
                host_schemas={'policy_bundle': [1]},
                required_capabilities=[],
            )
            manifest = release.make_manifest(
                config,
                'b' * 40,
                [content],
                archive,
                manifest_schema_version=3,
                host_compatibility={
                    'contract_version': 1,
                    'schemas': {'policy_bundle': [1]},
                    'required_routes': ['premium-policy-zip'],
                },
            )
            manifest['qualification'] = {
                'integrity': {'status': 'verified', 'evidence': ['archive hash verified']},
                'behavior': {'status': 'limited', 'evidence': ['synthetic route fixture']},
            }
            raw = json.dumps(manifest).encode()
            cached = root / 'test--public' / release.digest(raw)
            cached.mkdir(parents=True)
            (cached / 'pack-release.json').write_bytes(raw)
            artifact_cache = root / release.digest(archive.read_bytes())
            artifact_cache.mkdir()
            (artifact_cache / archive.name).write_bytes(archive.read_bytes())
            (root / 'test--public' / 'discovery.json').write_text(json.dumps({
                'repository': 'test/public',
                'visibility': 'public',
                'manifests': [{'sha256': release.digest(raw), 'commit': 'b' * 40, 'tag': 'v1.0.0'}],
                'assets': {},
            }))
            engine = root / 'engine.json'
            engine.write_text(json.dumps({
                'engine_version': '0.12.0',
                'build_identity': 'test-only-build',
                'model_set_sha256': 'a' * 64,
                'capability_contract_version': 1,
                'schemas': {key: [1] for key in release.SCHEMA_KEYS},
                'capabilities': [],
            }))
            host = root / 'host.json'
            host.write_text(json.dumps({
                'contract_version': 1,
                'schemas': {'policy_bundle': [1]},
                'provided_routes': ['premium-policy-zip'],
            }))
            receipt = root / 'receipt.json'
            argv = [
                'discover.py', '--repository', 'test/public', '--visibility', 'public',
                '--cache-dir', str(root), '--offline', '--engine-profile', str(engine),
                '--host-profile', str(host), '--pack-id', 'test.public', '--receipt', str(receipt),
            ]
            with patch.object(sys, 'argv', argv):
                self.assertEqual(discover.main(), 0)
            self.assertEqual(json.loads(receipt.read_text())['manifest_schema_version'], 3)

    def test_pagination_tag_binding_and_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); archive=root/'pack.zip';archive.write_bytes(b'bytes')
            config=dict(pack_id='test.public', repository='https://github.com/test/public', visibility='public',release_version='1.0.0', engine_min_inclusive='0.11.0',engine_max_exclusive='0.13.0',artifact_role='source')
            manifest=release.make_manifest(config,'b'*40,[],archive)
            manifest['qualification']={'integrity':{'status':'verified','evidence':['archive hash verified']},'behavior':{'status':'limited','evidence':['only format selection was checked']}}
            row=dict(tag_name='v1.0.0',draft=False,prerelease=False,assets=[dict(id=1,name='pack-release.json'),dict(id=2,name='pack.zip')])
            def fake(args):
                if '--paginate' in args:return json.dumps([[dict(row,draft=True)],[row]]).encode()
                if 'repos/test/public/releases/assets/1' in args:return json.dumps(manifest).encode()
                if 'repos/test/public/git/ref/tags/v1.0.0' in args:return json.dumps({'object':{'type':'commit','sha':'b'*40}}).encode()
                raise AssertionError(args)
            with patch.object(discover,'gh',side_effect=fake):
                paths,index=discover.enumerate_candidates('test/public','public',root)
            self.assertEqual(len(paths),1)
            with patch.object(discover,'gh',side_effect=AssertionError('offline network')):
                self.assertEqual(discover.enumerate_candidates('test/public','public',root,True)[0],paths)
            data=json.loads(paths[0].read_text());data['source']['commit']='c'*40;paths[0].write_text(json.dumps(data))
            with self.assertRaises(release.ReleaseError) as caught:discover.enumerate_candidates('test/public','public',root,True)
            self.assertEqual(caught.exception.code,'integrity-error')
            with patch.object(discover,'gh',side_effect=fake),patch.object(discover,'tag_commit',return_value='c'*40):
                with self.assertRaises(release.ReleaseError) as caught:discover.enumerate_candidates('test/public','public',root)
                self.assertEqual(caught.exception.code,'integrity-error')

    def test_private_credentials_and_network_typed(self):
        with tempfile.TemporaryDirectory() as directory,patch.dict('os.environ',{},clear=True),patch.object(discover.subprocess,'run') as run:
            run.return_value.returncode=1
            with self.assertRaises(release.ReleaseError) as caught:discover.enumerate_candidates('test/private','private',Path(directory))
            self.assertEqual(caught.exception.code,'unavailable-credentials/network')
            with self.assertRaises(release.ReleaseError) as caught:discover.gh(['repos/test/public/releases'])
            self.assertEqual(caught.exception.code,'unavailable-credentials/network')

    def test_no_release_manifest_is_invalid(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(discover,'gh',return_value=json.dumps([[dict(draft=False,tag_name='v1.0.0',assets=[])]]).encode()):
            with self.assertRaises(release.ReleaseError) as caught:discover.enumerate_candidates('test/public','public',Path(directory))
            self.assertEqual(caught.exception.code,'invalid-manifest')
