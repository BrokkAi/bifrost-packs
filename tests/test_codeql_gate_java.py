"""Java stager tests using authored temporary fixtures."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.upstream.codeql_gate.stagers.java import JavaStager


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

    @unittest.skipUnless(
        os.environ.get('JAVA_HOME') and
        (Path(os.environ['JAVA_HOME']) / 'bin' / ('javac.exe' if os.name == 'nt' else 'javac')).is_file(),
        'requires JAVA_HOME with javac')
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
