import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'release-contract'))
import release


def profile(engine_version='0.12.0', **overrides):
    result = dict(
        engine_version=engine_version,
        build_identity='test-only-build',
        model_set_sha256='a' * 64,
        capability_contract_version=1,
        schemas={key: [1, 2, 3, 4, 5, 6, 7] for key in release.SCHEMA_KEYS},
        capabilities=['structural-match'],
    )
    result.update(overrides)
    return result


def host_profile(**overrides):
    result = dict(
        contract_version=1,
        schemas={'policy_bundle': [1]},
        provided_routes=['premium-policy-zip'],
    )
    result.update(overrides)
    return result


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'pack.tar.gz'
        self.archive.write_bytes(b'content')
        self.config = dict(
            pack_id='test.public',
            repository='https://github.com/test/public',
            visibility='public',
            release_version='1.0.0',
            # These v1 settings are intentionally ignored by the v2 producer.
            engine_min_inclusive='0.11.0',
            engine_max_exclusive='0.13.0',
            artifact_role='policy',
        )

    def candidate(self, version, **kwargs):
        config = dict(self.config, release_version=version)
        manifest = release.make_manifest(config, 'b' * 40, [], self.archive)
        manifest['qualification'] = kwargs.get('qualification', {
            'integrity': {'status': 'verified', 'evidence': ['artifact hash verified']},
            'behavior': {'status': 'qualified', 'evidence': ['behavior fixture']},
        })
        manifest['compatibility']['capabilities']['required'] = kwargs.get('capabilities', [])
        if 'schema' in kwargs:
            manifest['compatibility']['schemas']['policy_document'] = [kwargs['schema']]
        if 'dependencies' in kwargs:
            manifest['release_dependencies'] = kwargs['dependencies']
        if 'role' in kwargs:
            manifest['artifacts'][0]['role'] = kwargs['role']
        path = self.root / (version + '.json')
        path.write_text(json.dumps(manifest))
        return path

    def v1_candidate(self, version, *, minimum='0.11.0', maximum='0.13.0', status='qualified', role='policy'):
        manifest = release.make_manifest(dict(self.config, release_version=version), 'b' * 40, [], self.archive)
        manifest['manifest_schema_version'] = 1
        manifest['compatibility']['engine'] = {'min_inclusive': minimum, 'max_exclusive': maximum}
        manifest['qualification'] = {'status': status, 'evidence': ['legacy evidence'] if status == 'qualified' else []}
        manifest['artifacts'][0]['role'] = role
        manifest.pop('release_dependencies', None)
        release.validate_manifest(manifest)
        path = self.root / ('v1-' + version + '.json')
        path.write_text(json.dumps(manifest))
        return path

    def v3_candidate(self, version='1.0.0', **kwargs):
        schemas = release.empty_schemas()
        schemas['policy_document'] = [1]
        schemas['rql'] = [1]
        content = dict(
            kind='policy',
            identity='synthetic.policy',
            path='rules/synthetic.rqlp',
            sha256='c' * 64,
            languages=['python'],
            dependencies=[],
            schemas=schemas,
            host_schemas={'policy_bundle': [1]},
            required_capabilities=[],
        )
        manifest = release.make_manifest(
            dict(self.config, release_version=version),
            'b' * 40,
            [content],
            self.archive,
            manifest_schema_version=3,
            host_compatibility={
                'contract_version': 1,
                'schemas': {'policy_bundle': [1]},
                'required_routes': ['premium-policy-zip'],
            },
        )
        manifest['qualification'] = kwargs.get('qualification', {
            'integrity': {'status': 'verified', 'evidence': ['artifact hash verified']},
            'behavior': {'status': 'qualified', 'evidence': ['positive and near-miss fixtures']},
        })
        path = self.root / ('v3-' + version + '.json')
        path.write_text(json.dumps(manifest))
        return path

    def test_v2_engine_versions_are_provenance_not_compatibility_gates(self):
        path = self.candidate('1.0.0')
        for engine_version in ('0.11.5', '0.12.0', '0.13.0-rc.1', '9.8.7'):
            with self.subTest(engine_version=engine_version):
                receipt = release.select_release([path], profile(engine_version), 'test.public')
                self.assertEqual(receipt['release_version'], '1.0.0')
                self.assertEqual(receipt['engine_profile']['engine_version'], engine_version)
                self.assertEqual(receipt['manifest_schema_version'], 2)
                self.assertEqual(receipt['receipt_schema_version'], 2)

    def test_filter_before_newest_by_schema_and_capability(self):
        old = self.candidate('1.0.0')
        future = self.candidate('2.0.0', schema=99)
        caps = self.candidate('3.0.0', capabilities=['unavailable'])
        receipt = release.select_release([caps, future, old], profile(), 'test.public')
        self.assertEqual(receipt['release_version'], '1.0.0')
        self.assertEqual(receipt['source_commit'], 'b' * 40)

    def test_channels_and_semver(self):
        candidates = [self.candidate(v) for v in ['1.9.0', '1.10.0', '2.0.0-rc.2', '2.0.0-rc.10']]
        self.assertEqual(release.select_release(candidates, profile(), 'test.public')['release_version'], '1.10.0')
        self.assertEqual(release.select_release(candidates, profile(), 'test.public', 'prerelease')['release_version'], '2.0.0-rc.10')

    def test_pins_and_offline_integrity(self):
        old = self.candidate('1.0.0')
        new = self.candidate('1.1.0')
        self.assertEqual(release.select_release([old, new], profile(), 'test.public', version='1.0.0')['release_version'], '1.0.0')
        self.archive.write_bytes(b'corrupt')
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([old], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'integrity-error')

    def test_missing_cache_and_no_compatible(self):
        path = self.candidate('1.0.0')
        self.archive.unlink()
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([path], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'unavailable-credentials/network')
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([path], profile(), 'test.public', commit='c' * 40)
        self.assertEqual(caught.exception.code, 'no-compatible-release')

    def test_schema_capability_and_manifest_version_diagnostics(self):
        path = self.candidate('1.0.0', schema=99)
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([path], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        self.assertIn('policy_document=99', str(caught.exception))
        rql = self.candidate('1.0.1')
        rql_manifest = json.loads(rql.read_text())
        rql_manifest['compatibility']['schemas']['rql'] = [99]
        rql.write_text(json.dumps(rql_manifest))
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([rql], profile(), 'test.public')
        self.assertEqual(caught.exception.code, 'incompatible-schema')
        self.assertIn('rql=99', str(caught.exception))
        manifest = json.loads(path.read_text())
        manifest['manifest_schema_version'] = 99
        with self.assertRaises(release.ReleaseError) as caught:
            release.validate_manifest(manifest)
        self.assertEqual(caught.exception.code, 'unsupported-manifest-schema')
        caps = self.candidate('1.1.0', capabilities=['missing-semantic-capability'])
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([caps], profile(), 'test.public')
        self.assertIn('missing required semantic capabilities', str(caught.exception))
        self.assertIn('missing-semantic-capability', str(caught.exception))

    def test_v2_integrity_gate_allow_unqualified_and_behavior_failures(self):
        pending = self.candidate('1.0.0', qualification={
            'integrity': {'status': 'pending', 'evidence': []},
            'behavior': {'status': 'pending', 'evidence': []},
        })
        with self.assertRaises(release.ReleaseError):
            release.select_release([pending], profile(), 'test.public')
        self.assertEqual(release.select_release([pending], profile(), 'test.public', allow_unqualified=True)['qualification']['integrity']['status'], 'pending')

        for status in ('failed',):
            for axis in ('integrity', 'behavior'):
                qualification = {
                    'integrity': {'status': 'verified', 'evidence': ['hashes checked']},
                    'behavior': {'status': 'limited', 'evidence': []},
                }
                qualification[axis] = {'status': status, 'evidence': ['failure observed']}
                path = self.candidate(f'1.0.{1 + (axis == "behavior")}', qualification=qualification)
                with self.subTest(axis=axis):
                    with self.assertRaises(release.ReleaseError):
                        release.select_release([path], profile(), 'test.public', allow_unqualified=True)

    def test_pending_and_limited_behavior_allow_source_artifacts(self):
        for status in ('pending', 'limited'):
            path = self.candidate('1.0.' + ('0' if status == 'pending' else '1'), role='source', qualification={
                'integrity': {'status': 'verified', 'evidence': ['archive and index verified']},
                'behavior': {'status': status, 'evidence': [] if status == 'pending' else ['partial behavior review']},
            })
            receipt = release.select_release([path], profile(), 'test.public')
            self.assertEqual(receipt['artifacts'][0]['role'], 'source')

    def test_v1_ranges_and_default_qualified_native_policy_gate_are_preserved(self):
        legacy_pending = self.v1_candidate('1.0.0', status='pending', role='policy')
        with self.assertRaises(release.ReleaseError):
            release.select_release([legacy_pending], profile('0.12.0'), 'test.public')
        self.assertEqual(release.select_release([legacy_pending], profile('0.12.0'), 'test.public', allow_unqualified=True)['manifest_schema_version'], 1)

        qualified_source = self.v1_candidate('1.1.0', status='qualified', role='source')
        with self.assertRaises(release.ReleaseError):
            release.select_release([qualified_source], profile('0.12.0'), 'test.public')
        outside_range = self.v1_candidate('1.2.0', minimum='0.13.0', maximum='0.14.0')
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([outside_range], profile('9.8.7'), 'test.public')
        self.assertIn('legacy engine range', str(caught.exception))
        qualified_policy = self.v1_candidate('1.3.0', role='policy')
        self.assertEqual(release.select_release([qualified_policy], profile('0.12.0'), 'test.public')['manifest_schema_version'], 1)

    def test_same_pack_identity_in_distinct_repositories_is_not_a_cycle(self):
        paths = []
        for owner, pack, dependencies in (
            ('root', 'test.public', [('test.shared', 'left')]),
            ('left', 'test.shared', [('test.shared', 'right')]),
            ('right', 'test.shared', []),
        ):
            repository = 'https://github.com/test/' + owner
            manifest = release.make_manifest(dict(self.config, repository=repository, pack_id=pack), 'b' * 40, [], self.archive)
            manifest['qualification']['integrity'] = dict(status='verified', evidence=['fixture checked'])
            manifest['release_dependencies'] = [dict(pack_id=dependency, release_version='1.0.0', repository='https://github.com/test/' + dependency_owner) for dependency, dependency_owner in dependencies]
            path = self.root / (owner + '.json')
            path.write_text(json.dumps(manifest))
            paths.append(path)
        resolved = release.resolve_release_set(paths, profile(), 'test.public')
        self.assertEqual([item[2]['pack']['repository'] for item in resolved], ['https://github.com/test/root', 'https://github.com/test/left', 'https://github.com/test/right'])

    def test_conflicting_transitive_dependencies_reject(self):
        paths = []
        repository = self.config['repository']
        for pack, version, requirements in (
            ('test.shared', '1.0.0', []), ('test.shared', '2.0.0', []),
            ('test.left', '1.0.0', [('test.shared', '1.0.0')]),
            ('test.right', '1.0.0', [('test.shared', '2.0.0')]),
            ('test.public', '1.0.0', [('test.left', '1.0.0'), ('test.right', '1.0.0')]),
        ):
            config = dict(self.config, pack_id=pack, release_version=version)
            manifest = release.make_manifest(config, 'b' * 40, [], self.archive)
            manifest['qualification']['integrity'] = dict(status='verified', evidence=['fixture checked'])
            manifest['release_dependencies'] = [dict(pack_id=dependency, release_version=pin, repository=repository) for dependency, pin in requirements]
            path = self.root / (pack + '-' + version + '.json')
            path.write_text(json.dumps(manifest))
            paths.append(path)
        with self.assertRaisesRegex(release.ReleaseError, 'conflicting exact dependency set'):
            release.resolve_release_set(paths, profile(), 'test.public')

    def test_v2_forbids_engine_ranges_and_requires_dependency_list(self):
        manifest = release.make_manifest(self.config, 'b' * 40, [], self.archive)
        manifest['compatibility']['engine'] = {'min_inclusive': '0.11.0', 'max_exclusive': '0.13.0'}
        with self.assertRaises(release.ReleaseError):
            release.validate_manifest(manifest)
        manifest.pop('compatibility')
        manifest['compatibility'] = {
            'schemas': release.empty_schemas(),
            'capabilities': {'contract_version': 1, 'required': [], 'provided': []},
        }
        manifest.pop('release_dependencies')
        with self.assertRaises(release.ReleaseError):
            release.validate_manifest(manifest)

    def test_v2_rejects_host_scope_without_changing_default_selection(self):
        manifest = release.make_manifest(self.config, 'b' * 40, [], self.archive)
        manifest['host_compatibility'] = {
            'contract_version': 1,
            'schemas': {'policy_bundle': [1]},
            'required_routes': ['premium-policy-zip'],
        }
        with self.assertRaises(release.ReleaseError):
            release.validate_manifest(manifest)
        self.assertEqual(release.select_release([self.candidate('1.0.0')], profile(), 'test.public')['manifest_schema_version'], 2)

    def test_v2_conflicting_dependency_versions_are_rejected(self):
        manifest = release.make_manifest(self.config, 'b' * 40, [], self.archive)
        manifest['release_dependencies'] = [
            {'pack_id': 'other.packs', 'release_version': '1.0.0', 'repository': 'https://github.com/test/packs'},
            {'pack_id': 'other.packs', 'release_version': '2.0.0', 'repository': 'https://github.com/test/packs'},
        ]
        with self.assertRaisesRegex(release.ReleaseError, 'conflicting exact release dependencies'):
            release.validate_manifest(manifest)

    def test_v2_provenance_is_explicit_and_validated(self):
        manifest = release.make_manifest(self.config, 'b' * 40, [], self.archive)
        self.assertNotIn('provenance', manifest)
        manifest['provenance'] = {'engine_version': '9.8.7', 'build_identity': 'engine-build', 'source_commit': 'c' * 40}
        release.validate_manifest(manifest)
        manifest['provenance']['source_commit'] = 'short'
        with self.assertRaises(release.ReleaseError):
            release.validate_manifest(manifest)

    def test_actual_copy_index_has_policy_hashes(self):
        lock = json.loads((ROOT / 'content-lock.json').read_text())
        contents = release.public_contents(ROOT, lock)
        policies = [row for row in contents if row['kind'] == 'policy']
        manifests = [json.loads(path.read_text()) for path in (ROOT / 'rules').glob('*/manifest.json')]
        self.assertEqual(len(policies), sum(len(manifest['policies']) for manifest in manifests))
        self.assertTrue(all(len(policy['authored_hash']) == 64 for policy in policies))
        release.make_manifest(dict(self.config, artifact_role='source'), 'b' * 40, contents, self.archive)

    def test_missing_profile_and_ambiguous_precedence(self):
        with self.assertRaises(release.ReleaseError):
            release.validate_profile({'engine_version': '0.12.0'})
        paths = [self.candidate('1.0.0+x'), self.candidate('1.0.0+y')]
        with self.assertRaises(release.ReleaseError):
            release.select_release(paths, profile(), 'test.public')

    def test_v3_keeps_engine_and_host_unions_separate(self):
        path = self.v3_candidate()
        manifest = json.loads(path.read_text())
        self.assertEqual(manifest['compatibility']['schemas']['policy_document'], [1])
        self.assertEqual(manifest['compatibility']['schemas']['policy_bundle'], [])
        self.assertEqual(manifest['contents'][0]['schemas']['policy_bundle'], [])
        self.assertEqual(manifest['host_compatibility']['schemas'], {'policy_bundle': [1]})
        self.assertEqual(manifest['contents'][0]['host_schemas'], {'policy_bundle': [1]})
        receipt = release.select_release([path], profile(), 'test.public', host_profile=host_profile())
        self.assertEqual(receipt['manifest_schema_version'], 3)
        self.assertEqual(receipt['host_profile'], host_profile())

    def test_v3_requires_independent_host_admission(self):
        path = self.v3_candidate()
        with self.assertRaisesRegex(release.ReleaseError, 'host profile is required'):
            release.select_release([path], profile(), 'test.public')
        for near_miss in (
            dict(host_profile(), schemas={'policy_bundle': []}),
            dict(host_profile(), provided_routes=[]),
        ):
            with self.subTest(host_profile=near_miss):
                with self.assertRaises(release.ReleaseError) as caught:
                    release.select_release([path], profile(), 'test.public', host_profile=near_miss)
                self.assertIn('host', str(caught.exception))
        for invalid_profile in (
            dict(host_profile(), schemas={'policy_bundle': [1], 'unknown_axis': []}),
            dict(host_profile(), provided_routes=['unsupported-route']),
            dict(host_profile(), unknown_key=True),
        ):
            with self.subTest(host_profile=invalid_profile):
                with self.assertRaises(release.ReleaseError):
                    release.select_release([path], profile(), 'test.public', host_profile=invalid_profile)

    def test_v3_host_contract_is_closed_and_union_bound(self):
        path = self.v3_candidate()
        manifest = json.loads(path.read_text())
        manifest['host_compatibility']['schemas']['policy_bundle'] = [1, 2]
        with self.assertRaisesRegex(release.ReleaseError, 'host compatibility schemas'):
            release.validate_manifest(manifest)

        for mutation in (
            lambda value: value['host_compatibility'].update(unknown_axis=[]),
            lambda value: value['host_compatibility'].__setitem__('required_routes', ['unsupported-route']),
            lambda value: value.__setitem__('manifest_schema_version', 4),
            lambda value: value['contents'][0]['host_schemas'].update(unknown_axis=[1]),
        ):
            candidate = json.loads(path.read_text())
            mutation(candidate)
            with self.subTest(candidate=candidate):
                with self.assertRaises(release.ReleaseError):
                    release.validate_manifest(candidate)

    def test_v3_producer_requires_explicit_host_scope(self):
        with self.assertRaises(release.ReleaseError):
            release.make_manifest(self.config, 'b' * 40, [], self.archive, manifest_schema_version=3)
        with self.assertRaises(release.ReleaseError):
            release.make_manifest(self.config, 'b' * 40, [], self.archive, host_compatibility=host_profile())


if __name__ == '__main__':
    unittest.main()
