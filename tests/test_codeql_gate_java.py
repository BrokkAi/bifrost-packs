"""Java stager tests using authored temporary fixtures."""
import os
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.upstream.codeql_gate.stagers.java import JavaStager
from scripts.upstream.codeql_gate.core import GateError


def _javac_supports_release_21():
    """The stager compiles stubs with `--release 21`; an older javac rejects it."""
    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        return False
    javac = Path(java_home) / 'bin' / ('javac.exe' if os.name == 'nt' else 'javac')
    if not javac.is_file():
        return False
    proc = subprocess.run([str(javac), '--release', '21', '-version'], capture_output=True, text=True)
    return proc.returncode == 0


class JavaStagerTests(unittest.TestCase):
    def fixture(self, base, names=('HikariCP-3.4.5',)):
        codeql = base / 'codeql'
        test_dir = codeql / 'java/ql/test/query-tests/example'
        stub_root = codeql / 'java/ql/test/stubs'
        test_dir.mkdir(parents=True)
        for name in names:
            (stub_root / name).mkdir(parents=True)
        return codeql, test_dir, stub_root

    def test_options_colon_paths_and_unknown_coordinate(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base, ('HikariCP-3.4.5', 'validation-api-2.0.1.Final'))
            coordinates_file = Path(__file__).parents[1] / 'scripts/upstream/codeql_gate/stagers/java_stub_coordinates.tsv'
            import csv
            with coordinates_file.open(newline='') as stream:
                coordinates = {row['stub_dir']: row for row in csv.DictReader(stream, delimiter='\t')}
            test_dir.joinpath('options').write_text(
                '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5:'
                '${testdir}/../../stubs/validation-api-2.0.1.Final')
            stager = JavaStager()
            selected = stager._option_stub_dirs(test_dir, stub_root, coordinates)
            self.assertEqual([path.name for path in selected],
                             ['HikariCP-3.4.5', 'validation-api-2.0.1.Final'])
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/not-mapped')
            with self.assertRaisesRegex(ValueError, 'not-mapped'):
                stager._option_stub_dirs(test_dir, stub_root, coordinates)

    def test_jdk_package_exclusion_uses_synthetic_module_map(self):
        modules = {'java.lang': {'java.base'}, 'javax.crypto': {'java.base'}}
        self.assertTrue(JavaStager._is_jdk_package('java.lang', modules))
        self.assertTrue(JavaStager._is_jdk_package('javax.crypto', modules))
        self.assertFalse(JavaStager._is_jdk_package('javax.crypto.extra', modules))
        self.assertFalse(JavaStager._is_jdk_package('org.example', modules))

    def test_binary_jar_filter_keeps_only_owned_packages(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            classes = base / 'classes'
            for name in ('com/example/Keep.class', 'com/example/internal/AlsoKeep.class',
                         'org/other/Drop.class'):
                path = classes / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(name.encode())
            kept = list(JavaStager._jar_files(classes, 'stub', False, {'com/example'}))
            self.assertEqual([relative.as_posix() for _, relative in kept],
                             ['com/example/Keep.class', 'com/example/internal/AlsoKeep.class'])

    def test_prepared_root_cache_hit_reinstalls_missing_stub_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            stub = stub_root / 'HikariCP-3.4.5'
            source = stub / 'com/example/Stub.java'
            source.parent.mkdir(parents=True)
            source.write_text('package com.example; public class Stub {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home = base / 'jdk'
            java_home.mkdir()
            cache = base / 'cache'
            stager = JavaStager(java_home)

            def fake_javac(command, **_kwargs):
                output = Path(command[command.index('-d') + 1]) / 'com/example/Stub.class'
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b'class')
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
                first = stager.prepare(test_dir, codeql, cache)
                self.assertEqual(first.staged_artifacts[0]['confidence'], 'unknown')
                self.assertIn('do not establish a unique Maven artifact',
                              first.staged_artifacts[0]['evidence'])
                coordinate_dir = cache / 'maven-home/.m2/repository/codeql/stubs/HikariCP-3.4.5/0'
                artifacts = [coordinate_dir / name for name in
                             ('HikariCP-3.4.5-0.jar', 'HikariCP-3.4.5-0-sources.jar',
                              'HikariCP-3.4.5-0.pom')]
                self.assertTrue(all(path.is_file() for path in artifacts))
                with zipfile.ZipFile(artifacts[0]) as archive:
                    self.assertEqual(archive.namelist(), ['com/example/Stub.class'])
                artifacts[0].unlink()
                again = stager.prepare(test_dir, codeql, cache)
                self.assertEqual(first.root, again.root)
                self.assertTrue(artifacts[0].is_file())

    def test_stub_source_change_rebuilds_coordinate_jar(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            stub = stub_root / 'HikariCP-3.4.5'
            source = stub / 'com/example/Stub.java'
            source.parent.mkdir(parents=True)
            source.write_text('package com.example; public class Stub { int value = 1; }\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home = base / 'jdk'
            java_home.mkdir()
            cache = base / 'cache'
            stager = JavaStager(java_home)

            def fake_javac(command, **_kwargs):
                output = Path(command[command.index('-d') + 1]) / 'com/example/Stub.class'
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(Path(command[-1]).read_bytes())
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac) as javac:
                stager.prepare(test_dir, codeql, cache)
                jar = cache / 'maven-home/.m2/repository/codeql/stubs/HikariCP-3.4.5/0/HikariCP-3.4.5-0.jar'
                fingerprint_file = jar.with_name(jar.name + '.fingerprint')
                first_fingerprint = fingerprint_file.read_text()
                with zipfile.ZipFile(jar) as archive:
                    first_class = archive.read('com/example/Stub.class')

                source.write_text('package com.example; public class Stub { int value = 2; }\n')
                stager.prepare(test_dir, codeql, cache)

                self.assertEqual(javac.call_count, 2)
                self.assertNotEqual(fingerprint_file.read_text(), first_fingerprint)
                with zipfile.ZipFile(jar) as archive:
                    self.assertNotEqual(archive.read('com/example/Stub.class'), first_class)

    def test_duplicate_stub_type_first_in_options_wins_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base, ('HikariCP-3.4.5', 'validation-api-2.0.1.Final'))
            first = stub_root / 'HikariCP-3.4.5/com/example/Shared.java'
            second = stub_root / 'validation-api-2.0.1.Final/com/example/Shared.java'
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text('package com.example; public class Shared { int first; }\n')
            second.write_text('package com.example; public class Shared { int second; }\n')
            test_dir.joinpath('options').write_text(
                '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5:'
                '${testdir}/../../stubs/validation-api-2.0.1.Final')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)

            def fake_javac(command, **_kwargs):
                sources = [Path(value) for value in command if value.endswith('.java')]
                self.assertEqual(len(sources), 1)
                self.assertIn('first', sources[0].read_text())
                output = Path(command[command.index('-d') + 1]) / 'com/example/Shared.class'
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b'compiled-first')
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
                stager.prepare(test_dir, codeql, cache)
            record = next((cache / 'java-stubs').glob('*/compile.txt')).read_text()
            self.assertIn('com.example.Shared: kept HikariCP-3.4.5/com/example/Shared.java', record)
            self.assertIn('dropped validation-api-2.0.1.Final/com/example/Shared.java', record)
            first_jar = cache / 'maven-home/.m2/repository/codeql/stubs/HikariCP-3.4.5/0/HikariCP-3.4.5-0.jar'
            with zipfile.ZipFile(first_jar) as archive:
                self.assertIn('com/example/Shared.class', archive.namelist())

    def test_jdk_owned_stub_package_is_dropped_and_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/javax/crypto/Stub.java'
            source.parent.mkdir(parents=True)
            source.write_text('package javax.crypto; public class Stub {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            with patch.object(stager, '_jdk_packages', return_value={'javax.crypto': {'java.base'}}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run') as javac:
                stager.prepare(test_dir, codeql, cache)
                javac.assert_not_called()
            record = next((cache / 'java-stubs').glob('*/compile.txt')).read_text()
            self.assertIn('HikariCP-3.4.5/javax/crypto/Stub.java package=javax.crypto modules=java.base', record)

    def test_compile_failure_marks_root_unstaged_without_binary_jar(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/com/example/Bad.java'
            source.parent.mkdir(parents=True)
            source.write_text('package com.example; public class Bad {')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run',
                          return_value=SimpleNamespace(returncode=1, stdout='',
                                                      stderr='Bad.java:1: error: package nowhere.example does not exist')):
                prepared = stager.prepare(test_dir, codeql, cache)
            self.assertEqual(prepared.staged_artifacts[0]['staging_status'], 'unstaged')
            self.assertIn('package nowhere.example does not exist',
                          prepared.staged_artifacts[0]['staging_diagnostic'])
            self.assertFalse(list((cache / 'maven-home').rglob('HikariCP-3.4.5-0.jar')))
            self.assertFalse(list((cache / 'maven-home').rglob('HikariCP-3.4.5-0.jar.fingerprint')))
            self.assertTrue(list((cache / 'maven-home').rglob('HikariCP-3.4.5-0-sources.jar')))

    def test_broken_stub_root_does_not_block_unrelated_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base, ('HikariCP-3.4.5', 'validation-api-2.0.1.Final'))
            broken = stub_root / 'HikariCP-3.4.5/broken/Bad.java'
            healthy = stub_root / 'validation-api-2.0.1.Final/healthy/Good.java'
            broken.parent.mkdir(parents=True)
            healthy.parent.mkdir(parents=True)
            broken.write_text('package broken; public class Bad {}\n')
            healthy.write_text('package healthy; public class Good {}\n')
            test_dir.joinpath('options').write_text(
                '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5:'
                '${testdir}/../../stubs/validation-api-2.0.1.Final')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)

            def fake_javac(command, **_kwargs):
                source = Path(command[-1])
                if source.name == 'Bad.java':
                    return SimpleNamespace(returncode=1, stdout='', stderr='synthetic failure')
                output = Path(command[command.index('-d') + 1]) / 'healthy/Good.class'
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b'good')
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
                prepared = stager.prepare(test_dir, codeql, cache)
            statuses = {item['stub_dir']: item['staging_status'] for item in prepared.staged_artifacts}
            self.assertEqual(statuses, {'HikariCP-3.4.5': 'unstaged', 'validation-api-2.0.1.Final': 'built'})
            self.assertTrue(list((cache / 'maven-home').rglob('validation-api-2.0.1.Final.jar')))
            self.assertFalse(list((cache / 'maven-home').rglob('HikariCP-3.4.5-0.jar.fingerprint')))

    def test_dependency_root_builds_on_later_fixpoint_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base, ('HikariCP-3.4.5', 'validation-api-2.0.1.Final'))
            dependent = stub_root / 'HikariCP-3.4.5/consumer/Use.java'
            dependency = stub_root / 'validation-api-2.0.1.Final/library/Needed.java'
            dependent.parent.mkdir(parents=True)
            dependency.parent.mkdir(parents=True)
            dependent.write_text('package consumer; import library.Needed; public class Use {}\n')
            dependency.write_text('package library; public class Needed {}\n')
            test_dir.joinpath('options').write_text(
                '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5:'
                '${testdir}/../../stubs/validation-api-2.0.1.Final')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            calls = []

            def fake_javac(command, **_kwargs):
                source = Path(command[-1])
                calls.append((source.name, '-classpath' in command))
                if source.name == 'Use.java' and '-classpath' not in command:
                    return SimpleNamespace(returncode=1, stdout='', stderr='package library missing')
                output = Path(command[command.index('-d') + 1])
                relative = Path('consumer/Use.class' if source.name == 'Use.java' else 'library/Needed.class')
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'built')
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
                prepared = stager.prepare(test_dir, codeql, cache)
            self.assertEqual({item['staging_status'] for item in prepared.staged_artifacts}, {'built'})
            self.assertIn(('Use.java', False), calls)
            self.assertIn(('Use.java', True), calls)

    def test_import_from_unstaged_stub_package_fails_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/org/example/Broken.java'
            source.parent.mkdir(parents=True)
            source.write_text('package org.example; public class Broken {}\n')
            (test_dir / 'Use.java').write_text(
                'import org.example.Broken;\nimport static org.example.Broken.VALUE;\n'
                'import org.example.*;\nclass Use {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run',
                          return_value=SimpleNamespace(returncode=1, stdout='', stderr='bad stub')):
                with self.assertRaisesRegex(GateError, 'import org.example') as error:
                    stager.prepare(test_dir, codeql, cache)
            self.assertIn('unstaged stub roots', str(error.exception))
            self.assertIn('Broken', str(error.exception))

    def test_duplicate_key_uses_declared_package_for_misplaced_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base, ('HikariCP-3.4.5', 'validation-api-2.0.1.Final'))
            misplaced = stub_root / 'HikariCP-3.4.5/wrong/Shared.java'
            regular = stub_root / 'validation-api-2.0.1.Final/declared/Shared.java'
            misplaced.parent.mkdir(parents=True)
            regular.parent.mkdir(parents=True)
            misplaced.write_text('package declared; public class Shared {}\n')
            regular.write_text('package declared; public class Shared { int duplicate; }\n')
            test_dir.joinpath('options').write_text(
                '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5:'
                '${testdir}/../../stubs/validation-api-2.0.1.Final')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)

            def fake_javac(command, **_kwargs):
                source = Path(command[-1])
                self.assertIn('wrong/Shared.java', source.as_posix())
                self.assertNotIn('duplicate', source.read_text())
                output = Path(command[command.index('-d') + 1]) / 'declared/Shared.class'
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b'first')
                return SimpleNamespace(returncode=0, stdout='', stderr='')

            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
                stager.prepare(test_dir, codeql, cache)
            record = next((cache / 'java-stubs').glob('*/compile.txt')).read_text()
            self.assertIn('path=wrong declared=declared', record)
            self.assertIn('declared.Shared: kept HikariCP-3.4.5/wrong/Shared.java', record)
            self.assertIn('dropped validation-api-2.0.1.Final/declared/Shared.java', record)

    def test_invalid_java_file_stem_is_skipped_and_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/org/example/PublicType copy.java'
            source.parent.mkdir(parents=True)
            source.write_text('package org.example; public class PublicType {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run') as javac:
                prepared = stager.prepare(test_dir, codeql, cache)
                javac.assert_not_called()
            record = next((cache / 'java-stubs').glob('*/compile.txt')).read_text()
            self.assertIn('HikariCP-3.4.5/org/example/PublicType copy.java', record)
            self.assertIn('file stem is not a valid Java identifier', record)
            self.assertEqual(prepared.staged_artifacts[0]['staging_status'], 'built')

    def _prepare_missing_package_with_auxiliaries(self, base, candidates):
        names = ('HikariCP-3.4.5',)
        codeql, test_dir, stub_root = self.fixture(base, names)
        consumer = stub_root / names[0] / 'consumer/Use.java'
        consumer.parent.mkdir(parents=True)
        consumer.write_text('package consumer; import shared.api.Needed; public class Use {}\n')
        test_dir.joinpath('options').write_text(
            '--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
        for root_name, package_sources in candidates.items():
            for relative, text in package_sources.items():
                source = stub_root / root_name / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(text)
        java_home, cache = base / 'jdk', base / 'cache'
        java_home.mkdir()
        stager = JavaStager(java_home)

        def fake_javac(command, **_kwargs):
            sources = [Path(value) for value in command if value.endswith('.java')]
            if any(source.name == 'Use.java' for source in sources) and '-classpath' not in command:
                return SimpleNamespace(returncode=1, stdout='',
                                       stderr='Use.java:1: error: package shared.api does not exist')
            output = Path(command[command.index('-d') + 1])
            for source in sources:
                match = re.search(r'^\s*package\s+([\w.]+)\s*;', source.read_text(), re.M)
                package = match.group(1) if match else ''
                relative = Path(package.replace('.', '/')) / f'{source.stem}.class'
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'built')
            return SimpleNamespace(returncode=0, stdout='', stderr='')

        with patch.object(stager, '_jdk_packages', return_value={}), \
                patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run', side_effect=fake_javac):
            return stager.prepare(test_dir, codeql, cache)

    def test_missing_package_uses_smallest_declaring_auxiliary_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            prepared = self._prepare_missing_package_with_auxiliaries(Path(temporary), {
                'apache-hive': {
                    'shared/api/Needed.java': 'package shared.api; public class Needed {}\n',
                    'shared/api/Extra.java': 'package shared.api; public class Extra {}\n',
                },
                'javafx-web': {
                    'shared/api/Needed.java': 'package shared.api; public class Needed {}\n',
                },
            })
            auxiliaries = [item for item in prepared.staged_artifacts
                           if item.get('staging_kind') == 'auxiliary']
            self.assertEqual([item['stub_dir'] for item in auxiliaries], ['javafx-web'])
            self.assertEqual(auxiliaries[0]['auxiliary_package'], 'shared.api')
            self.assertIn('package shared.api does not exist', auxiliaries[0]['auxiliary_trigger'])

    def test_auxiliary_root_tie_breaks_by_name(self):
        with tempfile.TemporaryDirectory() as temporary:
            prepared = self._prepare_missing_package_with_auxiliaries(Path(temporary), {
                'apache-hive': {
                    'shared/api/Needed.java': 'package shared.api; public class Needed {}\n',
                },
                'apache-commons-logging-1.2': {
                    'shared/api/Needed.java': 'package shared.api; public class Needed {}\n',
                },
            })
            auxiliaries = [item for item in prepared.staged_artifacts
                           if item.get('staging_kind') == 'auxiliary']
            self.assertEqual([item['stub_dir'] for item in auxiliaries],
                             ['apache-commons-logging-1.2'])

    def test_binary_jar_missing_expected_class_is_setup_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/com/example/Stub.java'
            source.parent.mkdir(parents=True)
            source.write_text('package com.example; public class Stub {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            java_home, cache = base / 'jdk', base / 'cache'
            java_home.mkdir()
            stager = JavaStager(java_home)
            with patch.object(stager, '_jdk_packages', return_value={}), \
                    patch('scripts.upstream.codeql_gate.stagers.java.subprocess.run',
                          return_value=SimpleNamespace(returncode=0, stdout='', stderr='')):
                with self.assertRaisesRegex(GateError, 'missing expected classes'):
                    stager.prepare(test_dir, codeql, cache)
            self.assertFalse(list((cache / 'java-stubs').glob('*/compile.txt')))

    @unittest.skipUnless(_javac_supports_release_21(), 'requires JAVA_HOME with a JDK 21+ javac')
    def test_real_stub_compile_when_jdk_is_available(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test_dir, stub_root = self.fixture(base)
            source = stub_root / 'HikariCP-3.4.5/com/example/Stub.java'
            source.parent.mkdir(parents=True)
            source.write_text('package com.example; public class Stub {}\n')
            test_dir.joinpath('options').write_text('--javac-args -cp ${testdir}/../../stubs/HikariCP-3.4.5')
            prepared = JavaStager(os.environ['JAVA_HOME']).prepare(test_dir, codeql, base / 'cache')
            self.assertEqual(prepared.staged_artifacts[0]['stub_dir'], 'HikariCP-3.4.5')
            jar = base / 'cache/maven-home/.m2/repository/codeql/stubs/HikariCP-3.4.5/0/HikariCP-3.4.5-0.jar'
            with zipfile.ZipFile(jar) as archive:
                self.assertIn('com/example/Stub.class', archive.namelist())


if __name__ == '__main__':
    unittest.main()
