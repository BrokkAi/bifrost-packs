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
    def test_pagination_tag_binding_and_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); archive=root/'pack.zip';archive.write_bytes(b'bytes')
            config=dict(pack_id='test.public', repository='https://github.com/test/public', visibility='public',release_version='1.0.0', engine_min_inclusive='0.11.0',engine_max_exclusive='0.13.0',artifact_role='source')
            manifest=release.make_manifest(config,'b'*40,[],archive)
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
