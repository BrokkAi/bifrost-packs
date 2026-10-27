"""Authored path-result fixtures exercise scoped recall for Java and Go."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
from scripts.upstream.codeql_gate.core import GateError, load_oracle, score
from scripts.upstream.codeql_gate.scoped import apply_scope, expected_scope, validate_attributions
from scripts.upstream.codeql_gate.stagers.go import GoStager
from scripts.upstream.codeql_gate.stagers.java import JavaStager

FIXTURES = Path(__file__).parent / 'fixtures/codeql_gate'
GATE = Path(__file__).resolve().parents[1] / 'scripts/upstream/codeql_gate/gate.py'


class ScopedRecallTests(unittest.TestCase):
    def inputs(self, language):
        directory = FIXTURES / f'scoped-{language}'
        catalogs = set(json.loads((directory / 'catalog.json').read_text()))
        stager = GoStager() if language == 'go' else JavaStager()
        oracle = load_oracle(directory, 'Example.ql', stager, 'example', catalogs)
        attributions = json.loads((directory / 'attributions.json').read_text())
        return directory, oracle, attributions

    def result(self, language, lines, attribution=None, complete=True, true_positives=()):
        directory, oracle, attributions = self.inputs(language)
        name = 'sample.go' if language == 'go' else 'sample.java'
        data = {'scope': {'analyzed_files': [name]}, 'runs': [
            {'policy_id': 'example', 'completion': {'type': 'complete' if complete else 'inconclusive'},
             'findings': [{'primary': {'path': name, 'region': {'start_line': n, 'end_line': n}}}
                          for n in lines]}]}
        result = score(data, oracle, true_positives=true_positives)
        apply_scope(result, oracle, attributions if attribution is None else attribution)
        return result

    def test_catalog_match_and_reviewed_framework_miss_defer(self):
        for language in ('java', 'go'):
            with self.subTest(language=language):
                result = self.result(language, [10, 30])
                self.assertTrue(result['pass'])
                self.assertEqual(result['verdict'], 'SCOPED-EXACT')
                self.assertEqual(result['full_suite_verdict'], 'MISS')
                self.assertEqual(len(result['deferred_misses']), 1)
                self.assertFalse(result['scoped_misses'])
                self.assertTrue(self.result(language, [10, 20, 30], attribution=[])['pass'])

    def test_ql_endpoint_and_in_catalog_misses_block(self):
        for language in ('java', 'go'):
            for lines in ([10], [30]):
                with self.subTest(language=language, lines=lines):
                    result = self.result(language, lines)
                    self.assertFalse(result['pass'])
                    self.assertEqual(len(result['scoped_misses']), 1)

    def test_extra_is_scored_over_full_suite_and_can_be_reviewed(self):
        for language in ('java', 'go'):
            with self.subTest(language=language):
                result = self.result(language, [10, 30, 40])
                self.assertFalse(result['pass'])
                self.assertEqual(result['full_suite_verdict'], 'FP+MISS')
                self.assertEqual(len(result['fp']), 1)
                name = 'sample.go' if language == 'go' else 'sample.java'
                self.assertTrue(self.result(language, [10, 30, 40], true_positives=[
                    dict(path=name, line=40, justification='Reviewed additional defect')])['pass'])
                # A matched out-of-subset finding is an oracle match, never an extra.
                self.assertEqual(self.result(language, [10, 20, 30])['fp'], [])

    def test_attribution_required_and_only_endpoint_absence_defers(self):
        for language in ('java', 'go'):
            with self.subTest(language=language):
                self.assertEqual(self.result(language, [10, 30], attribution=[])['verdict'], 'ERROR')
                _, _, entries = self.inputs(language)
                for value in ('framework-summary-step', 'skipped-stdlib-summary', 'ql-only-logic'):
                    result = self.result(language, [10, 30], [dict(entries[0], attribution=value)])
                    self.assertFalse(result['pass'])
                    self.assertEqual(result['deferred_misses'], [])
                wrong = [dict(entries[0], endpoint='Sink: unrelated')]
                self.assertEqual(self.result(language, [10, 30], wrong)['verdict'], 'ERROR')
                self.assertFalse(self.result(language, [10, 30], complete=False)['pass'])

    def test_invalid_and_duplicate_attributions_refused(self):
        _, _, entries = self.inputs('go')
        with self.assertRaisesRegex(GateError, 'invalid scope attribution'):
            validate_attributions([dict(entries[0], attribution='framework-magic')])
        with self.assertRaisesRegex(GateError, 'duplicate scope attribution'):
            validate_attributions(entries * 2)

    def test_missing_models_refused_even_with_inline_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'check.qlref').write_text('query: Example.ql\n')
            (root / 'check.expected').write_text('#select\n| a.go:1:1:1:2 | alert |\n')
            with self.assertRaisesRegex(GateError, 'requires a models section'):
                load_oracle(root, 'Example.ql', GoStager(), 'example', set())

    def test_summary_provenance_is_not_an_endpoint(self):
        directory, oracle, _ = self.inputs('go')
        self.assertFalse(oracle['recall_scope']['sample.go:10'][0]['absent_models'])
        self.assertTrue(oracle['recall_scope']['sample.go:30'][0]['included'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'check.expected'
            text = (directory / 'check.expected').read_text().replace('Src:MaD:1', 'MaD:1')
            path.write_text(text)
            scopes = expected_scope(path, lambda row: False)
            self.assertTrue(all(p['included'] for paths in scopes.values() for p in paths))

    def test_alternative_ql_or_catalog_endpoint_cannot_be_deferred(self):
        directory, _, _ = self.inputs('go')
        original = (directory / 'check.expected').read_text()
        catalogs = set(json.loads((directory / 'catalog.json').read_text()))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'check.expected'
            # Two outgoing paths share the source/sink; only one proves Src.
            alternative = (
                '| sample.go:1:1:1:4 | source1 | sample.go:5:1:5:4 | middle | provenance |  |\n'
                '| sample.go:5:1:5:4 | middle | sample.go:10:1:10:4 | sink1 | provenance | Sink:MaD:2 |\n')
            text = original.replace('models\n', alternative + 'models\n')
            path.write_text(text)
            scopes = expected_scope(path, lambda row: row in catalogs)
            self.assertTrue(scopes['sample.go:10'][0]['included'])
            # Node-level Src provenance can establish the endpoint for both paths.
            path.write_text(text + '| sample.go:1:1:1:4 | source1 | provenance | Src:MaD:1 |\n')
            scopes = expected_scope(path, lambda row: row in catalogs)
            self.assertEqual(scopes['sample.go:10'][0]['source_models'], [next(
                row for row in catalogs if row.startswith('Source:'))])
            # An additional absent model on an otherwise catalog-backed endpoint
            # does not remove the catalog alternative from recall obligations.
            path.write_text(original.replace('Src:MaD:1 MaD:4 Sink:MaD:2',
                                             'Src:MaD:1 MaD:4 Sink:MaD:2 Sink:MaD:3'))
            scopes = expected_scope(path, lambda row: row in catalogs)
            self.assertTrue(scopes['sample.go:10'][0]['included'])

    def test_dangling_endpoint_provenance_is_error(self):
        directory, _, _ = self.inputs('go')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'check.expected'
            path.write_text((directory / 'check.expected').read_text().replace('Src:MaD:1', 'Src:MaD:99'))
            with self.assertRaisesRegex(GateError, 'absent model row'):
                expected_scope(path, lambda row: False)

    def test_inline_only_alerts_remain_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'check.qlref').write_text(
                'query: Example.ql\npostprocess: utils/test/InlineExpectationsTestQuery.ql\n')
            (root / 'check.expected').write_text('#select\nmodels\n')
            (root / 'sample.go').write_text('package example // $ Alert\n')
            oracle = load_oracle(root, 'Example.ql', GoStager(), 'example', set())
            result = score({'scope': {'analyzed_files': ['sample.go']}, 'runs': [
                {'completion': {'type': 'complete'}, 'findings': []}]}, oracle)
            apply_scope(result, oracle, [])
            self.assertEqual(result['scoped_misses'], ['sample.go:1'])
            self.assertFalse(result['pass'])

    def test_cli_run_summary_and_report_validation(self):
        directory, _, entries = self.inputs('go')
        checkout = GATE.parents[3]
        test_dir = directory.resolve().relative_to(checkout).as_posix()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            attribution = root / 'attributions.json'
            attribution.write_text(json.dumps([dict(entries[0], test_dir=test_dir)]))
            policy = root / 'example.rqlp'
            policy.write_text('(policy)')
            binary = root / 'bifrost'
            data = {'scope': {'analyzed_files': ['sample.go']}, 'runs': [
                {'policy_id': 'example', 'completion': {'type': 'complete'}, 'findings': [
                    {'primary': {'path': 'sample.go', 'region': {'start_line': n, 'end_line': n}}}
                    for n in (10, 30)]}]}
            binary.write_text('#!/usr/bin/env python3\nimport json\nprint(json.dumps(' + repr(data) + '))\n')
            binary.chmod(0o755)
            state = root / 'state'
            command = [sys.executable, '-I', str(GATE), 'run', 'example', str(policy),
                       '--query-path', 'Example.ql', '--codeql-root', str(checkout),
                       '--test-dir', test_dir, '--binary', str(binary), '--state-dir', str(state),
                       '--scope-catalogs', str(directory / 'catalog.json'),
                       '--scope-attributions', str(attribution)]
            proc = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            output = json.loads(proc.stdout)
            self.assertEqual(output['combined']['verdict'], 'SCOPED-EXACT')
            self.assertEqual(output['combined']['full_suite_verdict'], 'FAIL')
            result = output['runs'][0]
            markdown = (Path(result['run_dir']) / 'result.md').read_text()
            self.assertIn('SCOPED-EXACT; full suite: MISS', markdown)
            summary = [sys.executable, '-I', str(GATE), 'summary', '--state-dir', str(state)]
            proc = subprocess.run(summary, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('SCOPED-EXACT', proc.stdout)
            self.assertTrue(proc.stdout.rstrip().endswith('MISS'))
            result['scope_attributions'][0]['attribution'] = 'unknown'
            (Path(result['run_dir']) / 'result.json').write_text(json.dumps(result))
            proc = subprocess.run(summary, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('invalid scope attribution', proc.stderr)

    def test_cli_scoped_expected_and_invalid_attribution(self):
        directory, _, entries = self.inputs('go')
        command = [sys.executable, '-I', str(GATE), 'expected', 'example', '--query-path', 'Example.ql',
                   '--codeql-root', str(FIXTURES.resolve()), '--test-dir', directory.name,
                   '--scope-catalogs', str(directory / 'catalog.json')]
        proc = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('recall_scope', json.loads(proc.stdout)[0])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'attribution.json'
            path.write_text(json.dumps([dict(entries[0], attribution='invalid')]))
            proc = subprocess.run(command + ['--scope-attributions', str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('invalid scope attribution', proc.stderr)


if __name__ == '__main__':
    unittest.main()
