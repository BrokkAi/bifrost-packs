"""Synthetic, authored fixtures only: never vendor upstream CodeQL test sources."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.upstream.codeql_gate.core import GateError, load_oracle, parse_expected, score
from scripts.upstream.codeql_gate.stagers.go import GoStager
from scripts.upstream.codeql_gate.compare_sarif import compare

FIXTURES = Path(__file__).parent / 'fixtures/codeql_gate'
GATE = Path(__file__).resolve().parents[1] / 'scripts/upstream/codeql_gate/gate.py'


def report(*locations, complete=True):
    return {'runs': [{'policy_id': 'example', 'completion': {'type': 'complete'} if complete else {'type': 'proven_subset', 'codes': ['branch_relation_derivation_incomplete']},
                     'diagnostics': [], 'work': {'scanned_files': 1},
                     'findings': [{'primary': {'path': p, 'region': {'start_line': n, 'end_line': end}},
                                   'completeness': {'type': 'complete'}} for p, n, end in locations]}]}


class OracleTests(unittest.TestCase):
    def oracle(self, name):
        return load_oracle(FIXTURES / name, 'Example.ql', GoStager())

    def test_problem_first_section_only(self):
        self.assertEqual([r['start'] for r in self.oracle('problem')['expected']], [3])

    def test_path_problem_first_column_only(self):
        self.assertEqual(self.oracle('path')['expected'][0]['path'], 'sink.go')
        self.assertEqual(len(self.oracle('path')['expected']), 1)

    def test_go_alerts_and_taint_ignore_path_ends_and_strings(self):
        oracle = self.oracle('inline')
        self.assertEqual([r['start'] for r in oracle['expected']], [3, 4, 5])
        self.assertEqual(oracle['oracle_disagreement']['inline_only'], ['tagged.go:4', 'tagged.go:5'])
        self.assertEqual(len(oracle['oracle_sources']['inline_taint']), 1)

    def test_missing_expected_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'check.qlref').write_text('query: Example.ql')
            with self.assertRaises(GateError):
                load_oracle(Path(d), 'Example.ql', GoStager())

    def test_testfailures_are_unreliable(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'check.expected'
            p.write_text('#select\n#testFailures\n| failure |\n')
            _, failures = parse_expected(p)
            self.assertTrue(failures)
            oracle = self.oracle('problem')
            oracle['testFailures'] = failures
            self.assertEqual(score(report(), oracle)['verdict'], 'ERROR')

    def test_strict_path_and_line_loose_overlap_does_not_pass(self):
        oracle = self.oracle('path')
        result = score(report(('sink.go', 4, 5)), oracle)
        self.assertFalse(result['pass'])
        self.assertEqual(result['silent_misses'], ['sink.go:3'])
        self.assertEqual(len(result['loose_matches']), 1)
        self.assertEqual(score(report(('nested/sink.go', 3, 4)), oracle)['tp'], [])

    def test_spurious_missing_classes(self):
        oracle = self.oracle('classes')
        result = score(report(('classes.go', 3, 3), ('classes.go', 4, 4), ('classes.go', 5, 5)), oracle)
        self.assertEqual(result['false_positives'], ['classes.go:4'])
        self.assertEqual(result['missing']['findings'], ['classes.go:5'])
        self.assertEqual(result['silent_misses'], [])
        clean = score(report(('classes.go', 3, 3)), oracle)
        self.assertTrue(clean['pass'])

    def test_incomplete_abstains(self):
        result = score(json.loads((FIXTURES / 'incomplete.json').read_text()), self.oracle('problem'))
        self.assertEqual(result['abstentions'], ['sample.go:3'])
        self.assertEqual(result['silent_misses'], [])
        self.assertFalse(result['pass'])

    def test_unknown_or_short_scanning_abstains(self):
        data = report()
        data['runs'][0]['work']['scanned_files'] = 0
        self.assertEqual(score(data, self.oracle('problem'))['abstentions'], ['sample.go:3'])

    def test_typed_file_scope_limits_abstentions(self):
        oracle = self.oracle('inline')
        data = report()
        data['runs'][0]['completion'] = {'type': 'inconclusive', 'reasons': ['capability_incomplete'],
            'scope': {'type': 'files', 'files': ['other.go'], 'truncated': False}}
        self.assertEqual(score(data, oracle)['silent_misses'], ['tagged.go:3', 'tagged.go:4', 'tagged.go:5'])
        self.assertFalse(score(data, oracle)['complete'])
        data['runs'][0]['completion']['scope']['truncated'] = True
        self.assertEqual(score(data, oracle)['abstentions'], ['tagged.go:3', 'tagged.go:4', 'tagged.go:5'])

    def test_advisory_empty_selection_remains_silent_miss(self):
        data = report()
        data['runs'][0]['diagnostics'] = [{'impact': 'advisory', 'code': {'type': 'empty_selection'},
            'severity': 'note', 'message': 'no groups'}]
        result = score(data, self.oracle('problem'))
        self.assertEqual(result['silent_misses'], ['sample.go:3'])
        self.assertTrue(result['complete'])
        self.assertEqual(result['diagnostics']['empty_selection'], 1)

    def test_complete_empty_silently_misses(self):
        self.assertEqual(score(report(), self.oracle('problem'))['silent_misses'], ['sample.go:3'])

    def test_union_all_report_runs(self):
        data = report()
        data['runs'].extend(report(('sample.go', 3, 3))['runs'])
        self.assertTrue(score(data, self.oracle('problem'))['pass'])

    def test_missing_runs_and_validation_errors(self):
        self.assertEqual(score({}, self.oracle('problem'))['verdict'], 'ERROR')
        data = report(('sample.go', 3, 3))
        data['diagnostics'] = [{'code': {'type': 'validation_failed'}, 'severity': 'error'}]
        self.assertEqual(score(data, self.oracle('problem'))['verdict'], 'ERROR')
        self.assertEqual(score(report(), self.oracle('problem'), required_policy_ids=['absent'])['verdict'], 'ERROR')

    def test_diagnostic_and_truncation_block_pass(self):
        data = report()
        data['runs'][0]['diagnostics'] = [{'impact': 'run_incomplete', 'primary': None}]
        self.assertEqual(score(data, self.oracle('problem'))['abstentions'], ['sample.go:3'])
        data = report(('sample.go', 3, 3))
        data['diagnostics_truncated'] = True
        self.assertFalse(score(data, self.oracle('problem'))['pass'])

    def test_explicit_anchors_and_true_positives(self):
        self.assertTrue(score(report(('sample.go', 5, 5)), self.oracle('problem'), anchors={'line_offset': 2})['pass'])
        data = report(('sample.go', 3, 3), ('other.go', 9, 9))
        self.assertTrue(score(data, self.oracle('problem'), true_positives=[{'path': 'other.go', 'line': 9, 'justification': 'reviewed'}])['pass'])


class StagingTests(unittest.TestCase):
    def test_preserves_module_vendor_and_tags_cache_content_addressed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'source'
            source.mkdir()
            (source / 'tag.go').write_text('//go:build special\npackage example\n')
            (source / 'go.mod').write_text('module example.test/fixture\n\ngo 1.20\n')
            (source / 'vendor').mkdir()
            (source / 'vendor/modules.txt').write_text('# pinned\n')
            (source / 'options').write_text('ignored')
            (source / 'test.expected').write_text('ignored')
            stager = GoStager()
            prepared = stager.prepare(source, base, base / 'roots')
            self.assertEqual((prepared.root / 'go.mod').read_bytes(), (source / 'go.mod').read_bytes())
            self.assertTrue((prepared.root / 'vendor/modules.txt').exists())
            self.assertFalse((prepared.root / 'options').exists())
            self.assertEqual(stager.run_env(base / 'run', prepared)['GOFLAGS'], '-mod=vendor')
            self.assertEqual(stager.prepare(source, base, base / 'roots'), prepared)
            (source / 'tag.go').write_text('package changed\n')
            self.assertNotEqual(stager.prepare(source, base, base / 'roots').root, prepared.root)

    def test_synthesized_module_and_private_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            stager = GoStager()
            prepared = stager.prepare(FIXTURES / 'problem', FIXTURES, Path(tmp))
            self.assertTrue((prepared.root / 'go.mod').exists())
            self.assertEqual(prepared.source_paths, ('sample.go',))


class SarifTests(unittest.TestCase):
    def test_compare_mapping_test_exclusion_and_paths(self):
        def alert(path, n):
            return {'ruleId': 'go/example', 'locations': [{'physicalLocation': {
                'artifactLocation': {'uri': path}, 'region': {'startLine': n}}}]}
        sarif = {'runs': [{'results': [alert('nested/sample.go', 3), alert('sample_test.go', 9), alert('other.go', 7)]}]}
        data = report(('nested/sample.go', 3, 3), ('sample_test.go', 9, 9), ('third.go', 5, 5))
        result = compare(sarif, data, {'go/example': 'example'})['go/example']
        self.assertEqual(result['matched'], ['nested/sample.go:3'])
        self.assertEqual(result['codeql_only'], ['other.go:7'])
        self.assertEqual(result['bifrost_only'], ['third.go:5'])


class ExecutionTests(unittest.TestCase):
    def run_gate(self, behavior='normal', keep=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        checkout = GATE.parents[3]
        test_dir = (FIXTURES / 'problem').resolve().relative_to(checkout)
        binary = base / 'bifrost'
        binary.write_text("#!/usr/bin/env python3\n" +
            "import json, os, pathlib, sys, time\n" +
            "root=pathlib.Path(sys.argv[sys.argv.index('--root')+1])\n" +
            "assert (root/'.bifrost/semantic-models/example.json').exists()\n" +
            "assert os.environ['BIFROST_WORKSPACE_SEMANTIC_MODELS']=='on'\n" +
            "assert os.environ['BIFROST_OPEN_PACKS_DISABLE']=='1'\n" +
            "assert os.environ['HOME'].startswith(str(root.parent))\n" +
            "assert os.environ['GOCACHE'].startswith(str(root.parent))\n" +
            "(pathlib.Path(os.environ['BIFROST_CACHE_ROOT'])).mkdir(parents=True, exist_ok=True)\n" +
            ("time.sleep(30)\n" if behavior == 'timeout' else '') +
            ("print('not json')\n" if behavior == 'malformed' else
             "print(json.dumps(" + repr({'rules': [{'policy_id': 'example'}, {'policy_id': 'extra'}],
                    'runs': report()['runs'] + report(('sample.go', 3, 3))['runs']}) + "))\n"))
        binary.chmod(0o755)
        policy = base / 'primary.rqlp'
        extra = base / 'extra.rqlp'
        policy.write_text('(policy)')
        extra.write_text('(policy)')
        # Give the second report run the second rule identity.
        binary.write_text(binary.read_text().replace("'policy_id': 'example', 'completion':", "'policy_id': 'extra', 'completion':", 1))
        models = base / 'models'
        models.mkdir()
        (models / 'example.json').write_text('{}')
        command = [sys.executable, '-I', str(GATE), 'run', 'go/example', str(policy),
                   '--query-path', 'Example.ql', '--test-dir', str(test_dir), '--codeql-root', str(checkout),
                   '--binary', str(binary), '--state-dir', str(base / 'state'),
                   '--models', str(models), '--extra-policy', str(extra)]
        if behavior == 'timeout':
            command += ['--timeout', '0.1']
        if keep:
            command += ['--keep']
        proc = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertTrue(proc.stdout, proc.stderr)
        result = json.loads(proc.stdout)['runs'][0]
        return proc, result, base

    def test_isolated_cli_models_bundles_and_cleanup(self):
        proc, result, base = self.run_gate()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(result['pass'])
        run = Path(result['run_dir'])
        self.assertTrue((run / 'stdout.json').exists())
        self.assertTrue((run / 'result.md').exists())
        self.assertFalse((run / 'root').exists())
        self.assertFalse((run / 'cache').exists())
        shared = next((base / 'state/roots').iterdir())
        self.assertFalse((shared / '.bifrost').exists())
        self.assertEqual(len(result['binary_sha256']), 64)
        self.assertEqual(len(result['codeql_commit']), 40)

    def test_keep_retains_private_root(self):
        _, result, _ = self.run_gate(keep=True)
        self.assertTrue((Path(result['run_dir']) / 'root/.bifrost/policies/extra.rqlp').exists())

    def test_timeout_is_error_and_cleans_root(self):
        proc, result, _ = self.run_gate('timeout')
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertIn('timeout', result['errors'])
        self.assertFalse((Path(result['run_dir']) / 'root').exists())

    def test_malformed_report_is_error(self):
        proc, result, _ = self.run_gate('malformed')
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result['verdict'], 'ERROR')


if __name__ == '__main__':
    unittest.main()
