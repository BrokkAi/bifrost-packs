import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'release-contract'))
sys.path.insert(0, str(ROOT / 'tests'))
import native_generation
import native_release
import release
import test_baseline_release as baseline_fixture


class GeneratedReleaseTests(unittest.TestCase):
    def setUp(self):
        fixture = baseline_fixture.BaselineNativeContentsTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.archive, _ = fixture._native_archive()
        self.root = (fixture.root / 'repo').resolve()
        self.root.mkdir()
        self.commit = 'b' * 40
        (self.root / 'recipe.sh').write_text('#!/bin/bash\nexit 0\n')
        self.generator = dict(version='0.11.5', binary_sha256='a' * 64,
                              repository='https://github.com/BrokkAi/bifrost', commit='a' * 40,
                              asset='generator.tar.gz', asset_sha256='c' * 64)
        plan_config = dict(schema_version=1, generator=self.generator,
                           recipes=[dict(name='example', script='recipe.sh')])
        self.config_raw = (json.dumps(plan_config) + '\n').encode()
        (self.root / 'native-generation.json').write_bytes(self.config_raw)
        generator, _, jobs, recipes = native_generation._validate_config(self.root, self.root / 'native-generation.json')
        plan = native_generation._input_plan_record(jobs, recipes)
        files = native_release.archive_files(self.archive)
        digest = hashlib.sha256()
        for path, data in sorted(files.items()):
            name = path.removeprefix('bifrost-semantic-packs/')
            if name == 'measurements.json':
                continue
            encoded = name.encode()
            digest.update(len(encoded).to_bytes(8, 'big'))
            digest.update(encoded)
            digest.update(len(data).to_bytes(8, 'big'))
            digest.update(data)
        measurements = files['bifrost-semantic-packs/measurements.json']
        (fixture.root / 'measurements').mkdir()
        records, runs = [], []
        for n in (1, 2):
            name = f'measurements/run-{n}.json'
            data = measurements if n == 1 else b'{"source":"second observed timing"}\n'
            (fixture.root / name).write_bytes(data)
            records.append(dict(run=f'run-{n}', path=name, sha256=release.digest(data), included_in_archive=n == 1))
            runs.append(dict(id=f'run-{n}', native_content_sha256=digest.hexdigest(), measurements_sha256=release.digest(data)))
        self.receipt = dict(schema_version=1, source=dict(commit=self.commit),
                            config_sha256=release.digest(self.config_raw), plan=plan,
                            plan_sha256=release.digest(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode()),
                            generator=generator, binary_sha256=generator['binary_sha256'],
                            archive=dict(path='native.tar.gz', sha256=release.digest(self.archive.read_bytes())),
                            reproducibility=dict(status='byte-identical-native-content', excluded_from_comparison=['measurements.json'],
                                                 native_content_sha256=digest.hexdigest(), measurement_records=records, runs=runs),
                            qualification=dict(status='pending'))
        self.receipt_path = fixture.root / 'generation.json'
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.config = dict(pack_id='bifrost.public.packs', repository='https://github.com/test/packs', visibility='public',
                           release_version='1.0.0', engine_min_inclusive='0.12.0', engine_max_exclusive='0.14.0')
        self.config_path = self.root / 'release-config.packs.json'
        self.config_path.write_text(json.dumps(self.config))
        self.output = fixture.root / 'dist'

    def build(self):
        with patch.object(native_release.subprocess, 'check_output', side_effect=['', self.commit]):
            return native_release.build(self.root, self.config_path, self.archive, self.receipt_path, self.output)

    def test_older_generator_can_package_for_newer_consumer_without_claiming_qualification(self):
        manifest = self.build()
        self.assertEqual(manifest['compatibility']['engine']['min_inclusive'], '0.12.0')
        self.assertEqual(manifest['qualification']['status'], 'pending')
        path = self.output / 'pack-release.json'
        for version in ('0.12.0', '0.13.0'):
            profile = baseline_fixture._profile()
            profile['engine_version'] = version
            result = release.select_release([path], profile, 'bifrost.public.packs', allow_unqualified=True)
            self.assertEqual(result['release_version'], '1.0.0')
            with self.assertRaises(release.ReleaseError):
                release.select_release([path], profile, 'bifrost.public.packs')
        self.assertEqual(len(manifest['artifacts']), 4)
        for artifact in manifest['artifacts']:
            self.assertEqual(release.digest((self.output / artifact['name']).read_bytes()), artifact['sha256'])

    def test_wrong_source_commit_fails(self):
        self.receipt['source']['commit'] = 'd' * 40
        self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(release.ReleaseError, 'source commit'):
            self.build()

    def test_changed_recipe_fails(self):
        (self.root / 'recipe.sh').write_text('changed\n')
        with self.assertRaisesRegex(release.ReleaseError, 'inputs'):
            self.build()

    def test_changed_second_measurement_fails(self):
        (self.receipt_path.parent / 'measurements/run-2.json').write_text('changed')
        with self.assertRaisesRegex(release.ReleaseError, 'measurement bytes'):
            self.build()

    def test_altered_reproduction_content_digest_fails(self):
        self.receipt['reproducibility']['native_content_sha256'] = '0' * 64
        for run in self.receipt['reproducibility']['runs']:
            run['native_content_sha256'] = '0' * 64
        self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(release.ReleaseError, 'content differs'):
            self.build()

    def test_missing_required_consumer_schema_fails_selection(self):
        self.build()
        profile = baseline_fixture._profile()
        profile['engine_version'] = '0.13.0'
        profile['schemas']['release_index'] = []
        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release([self.output / 'pack-release.json'], profile, 'bifrost.public.packs', allow_unqualified=True)
        self.assertEqual(caught.exception.code, 'incompatible-schema')


if __name__ == '__main__':
    unittest.main()
