import io
import json
from pathlib import Path
import subprocess
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

    @staticmethod
    def host_profile(*, schemas=None, routes=None):
        return dict(
            contract_version=1,
            schemas={'policy_bundle': [1]} if schemas is None else schemas,
            provided_routes=['premium-policy-zip'] if routes is None else routes,
        )

    def schema3_manifest(self, version='0.1.2', *, routes=None, host_schemas=None, dependencies=()):
        schemas = release.empty_schemas()
        schemas['policy_document'] = [1]
        schemas['rql'] = [1]
        content = dict(
            kind='policy',
            identity='test.policy',
            path='rules/test.rqlp',
            sha256='b' * 64,
            languages=['csharp'],
            dependencies=[],
            schemas=schemas,
            host_schemas={'policy_bundle': [1]} if host_schemas is None else host_schemas,
            required_capabilities=[],
        )
        config = dict(self.config, release_version=version, release_dependencies=list(dependencies))
        manifest = release.make_manifest(
            config,
            'c' * 40,
            [content],
            self.archive,
            manifest_schema_version=3,
            host_compatibility={
                'contract_version': 1,
                'schemas': {'policy_bundle': [1]},
                'required_routes': ['premium-policy-zip'] if routes is None else routes,
            },
        )
        manifest['qualification']['integrity'] = dict(status='verified', evidence=['fixture bytes checked'])
        return manifest

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

    def test_schema3_publication_requires_host_profile_and_checks_host_schema_and_route(self):
        manifest = self.schema3_manifest()
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root)
        self.assertEqual(caught.exception.code, 'no-compatible-release')
        self.assertIn('independent host profile', str(caught.exception))

        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(
                manifest, self.root, host_profile=self.host_profile(schemas={'policy_bundle': []})
            )
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        self.assertIn('host schema', str(caught.exception))

        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root, host_profile=self.host_profile(routes=[]))
        self.assertEqual(caught.exception.code, 'no-compatible-release')
        self.assertIn('host route', str(caught.exception))

    def test_schema3_host_profile_is_strict_and_engine_bundle_axis_cannot_replace_it(self):
        manifest = self.schema3_manifest()
        profile = self.host_profile()
        profile['extra'] = True
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root, host_profile=profile)
        self.assertEqual(caught.exception.code, 'invalid-manifest')

        # Even when the engine bundle axis claims schema 1, only a separate host
        # profile can satisfy the release's host policy-bundle requirement.
        manifest['contents'][0]['schemas']['policy_bundle'] = [1]
        manifest['compatibility']['schemas']['policy_bundle'] = [1]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(
                manifest, self.root, host_profile=self.host_profile(schemas={'policy_bundle': []})
            )
        self.assertEqual(caught.exception.code, 'incompatible-schema')

    def test_schema3_requires_verified_integrity_nonfailed_behavior_and_valid_artifact_bytes(self):
        manifest = self.schema3_manifest()
        manifest['qualification']['integrity'] = dict(status='pending', evidence=[])
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root, host_profile=self.host_profile())
        self.assertEqual(caught.exception.code, 'integrity-error')

        manifest['qualification']['integrity'] = dict(status='verified', evidence=['fixture bytes checked'])
        manifest['qualification']['behavior'] = dict(status='failed', evidence=['fixture failure'])
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root, host_profile=self.host_profile())
        self.assertEqual(caught.exception.code, 'integrity-error')

        manifest['qualification']['behavior'] = dict(status='pending', evidence=[])
        publication.verify_publication(manifest, self.root, host_profile=self.host_profile())
        self.archive.write_bytes(b'corrupt')
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(manifest, self.root, host_profile=self.host_profile())
        self.assertEqual(caught.exception.code, 'integrity-error')

    def test_schema3_malformed_content_host_union_is_rejected(self):
        manifest = self.schema3_manifest()
        manifest['contents'][0]['host_schemas']['policy_bundle'] = [2]
        manifest['host_compatibility']['schemas']['policy_bundle'] = [1, 2]
        with self.assertRaisesRegex(release.ReleaseError, 'host compatibility schemas must equal'):
            publication.verify_publication(manifest, self.root, host_profile=self.host_profile(schemas={'policy_bundle': [1, 2]}))

    def test_schema1_is_still_rejected_for_new_publication(self):
        legacy = json.loads(json.dumps(self.manifest))
        legacy['manifest_schema_version'] = 1
        legacy['compatibility']['engine'] = {'min_inclusive': '0.1.0', 'max_exclusive': '1.0.0'}
        legacy['qualification'] = {'status': 'qualified', 'evidence': ['historical qualification']}
        legacy.pop('release_dependencies')
        release.validate_manifest(legacy)
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(legacy, self.root)
        self.assertEqual(caught.exception.code, 'unsupported-manifest-schema')

    def test_schema3_publication_cli_accepts_an_explicit_host_profile(self):
        manifest = self.schema3_manifest()
        manifest_path = self.root / 'schema3.json'
        profile_path = self.root / 'host-profile.json'
        manifest_path.write_text(json.dumps(manifest))
        profile_path.write_text(json.dumps(self.host_profile()))
        result = subprocess.run(
            [
                sys.executable,
                str(Path(publication.__file__)),
                '--manifest', str(manifest_path),
                '--directory', str(self.root),
                '--host-profile', str(profile_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'verified')

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

    def test_schema3_exact_dependency_requires_same_host_profile_and_matching_identity(self):
        dependency = self.schema3_manifest('0.2.0')
        requirement = dict(
            pack_id=dependency['pack']['id'],
            repository=dependency['pack']['repository'],
            release_version=dependency['release_version'],
        )
        self.manifest['release_dependencies'] = [requirement]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(self.manifest, self.root, [dependency])
        self.assertEqual(caught.exception.code, 'no-compatible-release')
        self.assertIn('independent host profile', str(caught.exception))

        publication.verify_publication(
            self.manifest, self.root, [dependency], host_profile=self.host_profile()
        )

        wrong_version = self.schema3_manifest('0.2.1')
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(
                self.manifest, self.root, [wrong_version], host_profile=self.host_profile()
            )
        self.assertEqual(caught.exception.code, 'no-compatible-release')

        other_config = dict(self.config, repository='https://github.com/test/other', release_version='0.2.0')
        other_repository = release.make_manifest(
            other_config,
            'd' * 40,
            dependency['contents'],
            self.archive,
            manifest_schema_version=3,
            host_compatibility=dependency['host_compatibility'],
        )
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(
                self.manifest, self.root, [other_repository], host_profile=self.host_profile()
            )
        self.assertEqual(caught.exception.code, 'no-compatible-release')

    def test_schema3_dependency_with_nested_dependency_is_rejected(self):
        dependency = self.schema3_manifest('0.2.0')
        dependency['release_dependencies'] = [dict(
            pack_id='nested.packs',
            repository='https://github.com/test/nested',
            release_version='1.0.0',
        )]
        self.manifest['release_dependencies'] = [dict(
            pack_id=dependency['pack']['id'],
            repository=dependency['pack']['repository'],
            release_version=dependency['release_version'],
        )]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(
                self.manifest, self.root, [dependency], host_profile=self.host_profile()
            )
        self.assertEqual(caught.exception.code, 'no-compatible-release')
        self.assertIn('nested publication dependencies', str(caught.exception))

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

        schema3 = self.schema3_manifest()
        schema3['artifacts'] = [dict(
            name=native.name,
            sha256=release.digest(native.read_bytes()),
            size_bytes=native.stat().st_size,
            format='tar.gz',
            role='native',
        )]
        with self.assertRaises(release.ReleaseError) as caught:
            publication.verify_publication(schema3, self.root, host_profile=self.host_profile())
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        self.assertIn('native compatibility.bifrost', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
