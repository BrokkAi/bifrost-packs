"""Authored path-result fixtures exercise scoped recall for Java and Go."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
from scripts.upstream.codeql_gate.core import GateError, load_oracle, score, write_results
from scripts.upstream.codeql_gate.ql_classes import (CODEQL_CLI_ARCHIVE_SHA256, CODEQL_CLI_VERSION,
                                                     CODEQL_COMMIT, cache_path, helper_query_sha256,
                                                     load_cache, verify_allowlist_files_clean)
from scripts.upstream.codeql_gate.scoped import apply_scope, expected_scope, validate_attributions
from scripts.upstream.codeql_gate.stagers.go import GoStager
from scripts.upstream.codeql_gate.stagers.java import JavaStager

FIXTURES = Path(__file__).parent / 'fixtures/codeql_gate'
GATE = Path(__file__).resolve().parents[1] / 'scripts/upstream/codeql_gate/gate.py'
BOUNDARIES = FIXTURES / 'scoped-boundaries'
QL_CACHE_ROOT = FIXTURES / 'ql-classes'


def scoped_java_cache():
    return json.loads(cache_path(QL_CACHE_ROOT, 'scoped-java-ql').read_text())


def init_git_repo(root):
    subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
    subprocess.run(['git', '-C', str(root), 'config', 'user.email', 'test@example.invalid'], check=True)
    subprocess.run(['git', '-C', str(root), 'config', 'user.name', 'Test'], check=True)
    return root


def fake_cache_for_scope(scope, endpoint_id):
    item = next(item for item in JavaStager.ql_endpoints if item['id'] == endpoint_id)
    role = item['role']
    rows = []
    for paths in scope.values():
        for path in paths:
            node = path[f'{role}_node']
            if node:
                rows.append(dict(path=node['path'], start_line=node['line'],
                                 start_column=node['column'], end_line=node['end_line'],
                                 end_column=node['end_column'], ql_class=item['ql_class']))
    return dict(rows=rows)


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

    def test_allowlisted_ql_endpoint_is_attributed_per_route(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10', 'sample.java:20'], 'fp': [], 'errors': []}
        attributions = [dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                             attribution='framework-endpoint-absent',
                             ql_endpoint={'id': 'spring-servlet-input-parameter',
                                          'nodes': [dict(path='sample.java', line=1, column=1)]},
                             justification='Spring request parameter source is outside this catalog.')]
        apply_scope(result, oracle, attributions, JavaStager.ql_endpoints, scoped_java_cache())
        self.assertEqual(result['deferred_misses'], ['sample.java:10'])
        self.assertEqual(result['scoped_misses'], ['sample.java:20'])

    def test_ql_endpoint_unknown_id_and_node_errors(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        base = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                    attribution='framework-endpoint-absent',
                    justification='Reviewed framework endpoint.')
        for form, message in (
                ({'id': 'unknown', 'nodes': [dict(path='sample.java', line=1, column=1)]},
                 'unknown QL endpoint id'),
                ({'id': 'spring-servlet-input-parameter',
                  'nodes': [dict(path='sample.java', line=99, column=1)]},
                 'QL endpoint node is not on an alert path')):
            result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                      'fn': ['sample.java:10'], 'fp': [], 'errors': []}
            apply_scope(result, oracle, [dict(base, ql_endpoint=form)], JavaStager.ql_endpoints,
                        scoped_java_cache())
            self.assertEqual(result['verdict'], 'ERROR')
            self.assertIn(message, result['errors'][0])

    def test_valid_ql_node_plus_unused_node_is_an_error_verdict(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        attribution = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'spring-servlet-input-parameter',
                                        'nodes': [dict(path='sample.java', line=1, column=1),
                                                  dict(path='sample.java', line=999, column=1)]},
                           justification='Reviewed framework endpoint.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10'], 'fp': [], 'errors': []}
        apply_scope(result, oracle, [attribution], JavaStager.ql_endpoints, scoped_java_cache())
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertFalse(result['pass'])
        self.assertIn('not on an alert path', result['errors'][0])

    def test_partial_source_or_sink_mad_evidence_rejects_ql_deferral(self):
        cases = (
            ('unproven-source.expected', lambda row: row == 'Sink: stdlib',
             'spring-servlet-input-parameter', 'source_node', 'source_models'),
            ('unproven-sink.expected', lambda row: row == 'Source: stdlib',
             'dom4j-xpath-constructor', 'sink_node', 'sink_models'))
        by_id = {item['id']: item for item in JavaStager.ql_endpoints}
        for filename, contains, endpoint_id, node_key, models_key in cases:
            with self.subTest(filename=filename):
                scope = expected_scope(BOUNDARIES / filename, contains)
                path = scope['x.go:10'][0]
                self.assertFalse(path[node_key.replace('_node', '_known')])
                self.assertTrue(path[models_key])
                attribution = dict(test_dir='scoped-boundaries', path='x.go', line=10,
                                   attribution='framework-endpoint-absent',
                                   ql_endpoint={'id': endpoint_id, 'nodes': [path[node_key]]},
                                   justification='Do not accept partial MaD provenance as a QL endpoint.')
                result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                          'fn': ['x.go:10'], 'fp': [], 'errors': []}
                apply_scope(result, {'recall_scope': scope}, [attribution], JavaStager.ql_endpoints,
                            fake_cache_for_scope(scope, endpoint_id))
                self.assertEqual(result['verdict'], 'ERROR')
                self.assertFalse(result['deferred_misses'])
                self.assertIn('names a MaD endpoint', result['errors'][0])

    def test_cli_input_id_is_not_allowlisted(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        attribution = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'CliInput',
                                        'nodes': [dict(path='sample.java', line=1, column=1)]},
                           justification='CliInput is explicitly outside the deferrable allow-list.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10'], 'fp': [], 'errors': []}
        apply_scope(result, oracle, [attribution], JavaStager.ql_endpoints, scoped_java_cache())
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertIn('unknown QL endpoint id', result['errors'][0])

    def test_dom4j_xpath_mad_branch_cannot_be_attributed_as_ql(self):
        path = expected_scope(BOUNDARIES / 'unproven-sink.expected',
                              lambda row: row == 'Source: stdlib')['x.go:10'][0]
        attribution = dict(test_dir='scoped-boundaries', path='x.go', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'dom4j-xpath-constructor',
                                        'nodes': [path['sink_node']]},
                           justification='The ordinary XPath MaD branch remains in scope.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['x.go:10'], 'fp': [], 'errors': []}
        scope = {'x.go:10': [path]}
        apply_scope(result, {'recall_scope': scope}, [attribution], JavaStager.ql_endpoints,
                    fake_cache_for_scope(scope, 'dom4j-xpath-constructor'))
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertFalse(result['deferred_misses'])
        self.assertIn('names a MaD endpoint', result['errors'][0])

    def test_missing_and_stale_ql_class_caches_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(GateError, 'QL-class cache is missing'):
                load_cache(tmp, 'scoped-java-ql', JavaStager.ql_endpoints, tmp)
            source = cache_path(QL_CACHE_ROOT, 'scoped-java-ql')
            payload = json.loads(source.read_text())
            payload['cli_version'] = '2.27.2'
            destination = cache_path(tmp, 'scoped-java-ql')
            destination.parent.mkdir(parents=True)
            destination.write_text(json.dumps(payload))
            with self.assertRaisesRegex(GateError, 'stale QL-class cache'):
                load_cache(tmp, 'scoped-java-ql', JavaStager.ql_endpoints, tmp)

    def test_actual_checkout_head_mismatch_rejects_unchanged_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'codeql'
            root.mkdir()
            init_git_repo(root)
            marker = root / 'README'
            marker.write_text('different CodeQL checkout\n')
            subprocess.run(['git', '-C', str(root), 'add', 'README'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '--quiet', '-m', 'checkout'], check=True)
            cache = scoped_java_cache()
            self.assertEqual(cache['codeql_commit'], CODEQL_COMMIT)
            destination = cache_path(Path(tmp) / 'cache', 'scoped-java-ql')
            destination.parent.mkdir(parents=True)
            destination.write_text(json.dumps(cache))
            with self.assertRaisesRegex(GateError, 'CodeQL checkout HEAD .* does not match QL-class cache commit'):
                load_cache(Path(tmp) / 'cache', 'scoped-java-ql', JavaStager.ql_endpoints, root)

    def test_dirty_allowlisted_class_file_rejects_cache_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'codeql'
            root.mkdir()
            init_git_repo(root)
            for endpoint in JavaStager.ql_endpoints:
                path = root / endpoint['file']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'class {endpoint["ql_class"]} {{}}\n')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), 'commit', '--quiet', '-m', 'classes'], check=True)
            (root / JavaStager.ql_endpoints[0]['file']).write_text('class changed {}\n')
            with self.assertRaisesRegex(GateError, 'allow-list class files have local changes'):
                verify_allowlist_files_clean(root, JavaStager.ql_endpoints)

    def test_cached_class_mismatch_blocks_ql_deferral(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        attribution = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'spring-servlet-input-parameter',
                                        'nodes': [dict(path='sample.java', line=1, column=1)]},
                           justification='The class cache must corroborate the asserted id.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10'], 'fp': [], 'errors': []}
        cache = scoped_java_cache()
        cache['rows'] = [dict(row, ql_class='CliInput') if row['path'] == 'sample.java'
                         and row['start_line'] == 1 else row for row in cache['rows']]
        apply_scope(result, oracle, [attribution], JavaStager.ql_endpoints, cache)
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertIn('is not class SpringServletInputParameterSource', result['errors'][0])

    def test_main_string_array_parameter_spellings_are_blocked(self):
        spellings = ('String[] args', 'String... args', 'String args[]')
        for declaration in spellings:
            with self.subTest(declaration=declaration), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'Example.java'
                source = f'class Example {{ void main({declaration}) {{}} }}\n'
                path.write_text(source)
                column = source.index('String') + 1
                node = dict(path='Example.java', line=1, column=column,
                            end_line=1, end_column=column + len(declaration))
                self.assertTrue(JavaStager.is_main_string_array_parameter(tmp, node))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Example.java'
            source = 'class Example { void main(int args) {} }\n'
            path.write_text(source)
            node = dict(path='Example.java', line=1, column=source.index('int') + 1,
                        end_line=1, end_column=source.index(')') + 1)
            self.assertFalse(JavaStager.is_main_string_array_parameter(tmp, node))

    def test_main_string_array_node_is_blocked_during_scope_application(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = 'class Example { void main(String[] args) {} }\n'
            (Path(tmp) / 'Example.java').write_text(source)
            column = source.index('String') + 1
            node = dict(path='Example.java', line=1, column=column,
                        end_line=1, end_column=column + len('String[] args'))
            path = dict(included=True, source_models=[], sink_models=['Sink: model'],
                        absent_models=[], source_known=False, sink_known=True,
                        source_present=False, sink_present=True, source_node=node,
                        sink_node=dict(path='Example.java', line=1, column=1,
                                       end_line=1, end_column=2))
            attribution = dict(test_dir='sample', path='Example.java', line=1,
                               attribution='framework-endpoint-absent',
                               ql_endpoint={'id': 'spring-servlet-input-parameter',
                                            'nodes': [dict(path=node['path'], line=node['line'],
                                                           column=node['column'])]},
                               justification='Pin the main-parameter guard.')
            cache = dict(rows=[dict(path=node['path'], start_line=node['line'],
                                    start_column=node['column'], end_line=node['end_line'],
                                    end_column=node['end_column'],
                                    ql_class='SpringServletInputParameterSource')])
            result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                      'fn': ['Example.java:1'], 'fp': [], 'errors': []}
            apply_scope(result, {'recall_scope': {'Example.java:1': [path]}},
                        [attribution], JavaStager.ql_endpoints, cache, tmp,
                        JavaStager.is_main_string_array_parameter)
            self.assertEqual(result['verdict'], 'ERROR')
            self.assertIn('main String-array parameter', result['errors'][0])

    def test_deferred_ql_assertion_is_recorded_in_json_and_markdown(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        attribution = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'spring-servlet-input-parameter',
                                        'nodes': [dict(path='sample.java', line=1, column=1)]},
                           justification='Spring request source is outside this catalog.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10'], 'fp': [], 'errors': []}
        apply_scope(result, oracle, [attribution], JavaStager.ql_endpoints, scoped_java_cache())
        recorded = result['deferred_attributions'][0]
        self.assertEqual(recorded['ql_endpoint']['id'], 'spring-servlet-input-parameter')
        self.assertEqual(recorded['ql_endpoint']['ql_class'], 'SpringServletInputParameterSource')
        self.assertEqual(recorded['ql_endpoint']['nodes'], attribution['ql_endpoint']['nodes'])
        with tempfile.TemporaryDirectory() as tmp:
            write_results(Path(tmp), dict(
                result, query='example', oracle_sources={}, oracle_disagreement={},
                binary_sha256='digest', codeql_commit='commit', matched=[],
                false_positives=[], silent_misses=[], abstentions=[],
                spurious={'sites': [], 'findings': []}, missing={'sites': [], 'findings': []}))
            markdown = (Path(tmp) / 'result.md').read_text()
            self.assertIn('spring-servlet-input-parameter', markdown)
            self.assertIn('SpringServletInputParameterSource', markdown)
            self.assertIn('sample.java', markdown)

    def test_ql_endpoint_wrong_role_is_an_error(self):
        directory = FIXTURES / 'scoped-java-ql'
        oracle = load_oracle(directory, 'Example.ql', JavaStager(), 'example', set())
        attribution = dict(test_dir='scoped-java-ql', path='sample.java', line=10,
                           attribution='framework-endpoint-absent',
                           ql_endpoint={'id': 'spring-servlet-input-parameter',
                                        'nodes': [dict(path='sample.java', line=10, column=1)]},
                           justification='Reviewed framework endpoint.')
        result = {'verdict': 'MISS', 'pass': False, 'complete': True,
                  'fn': ['sample.java:10'], 'fp': [], 'errors': []}
        apply_scope(result, oracle, [attribution], JavaStager.ql_endpoints, scoped_java_cache())
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertIn('wrong role', result['errors'][0])

    def test_java_ql_endpoint_allowlist_detects_moved_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            endpoint = JavaStager.ql_endpoints[0]
            path = root / endpoint['file']
            path.parent.mkdir(parents=True)
            path.write_text('\n' * endpoint['end_line'] + 'class Moved {}\n')
            with self.assertRaisesRegex(GateError, 'allow-list mismatch'):
                JavaStager.validate_ql_endpoints(root)

    def test_cli_rejects_moved_java_ql_endpoint_with_setup_error(self):
        fake_root = FIXTURES / 'scoped-java-ql' / 'fake-codeql'
        command = [sys.executable, '-I', str(GATE), 'expected', 'example', '--language', 'java',
                   '--query-path', 'Example.ql', '--codeql-root', str(fake_root), '--test-dir', '.',
                   '--scope-catalogs', str(FIXTURES / 'scoped-java' / 'catalog.json')]
        proc = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('allow-list mismatch', proc.stderr)

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
        for justification in (None, '', '   '):
            entry = dict(entries[0], justification=justification)
            if justification is None:
                del entry['justification']
            with self.subTest(justification=justification):
                with self.assertRaisesRegex(GateError, 'requires .* justification'):
                    validate_attributions([entry])

    def boundary_result(self, scope, endpoint):
        result = {'verdict': 'EMPTY', 'pass': False, 'complete': True,
                  'fn': ['x.go:10'], 'fp': [], 'errors': []}
        attribution = dict(test_dir='scoped-boundaries', path='x.go', line=10,
                           attribution='framework-endpoint-absent', endpoint=endpoint,
                           justification='Named framework endpoint is absent from the catalog.')
        apply_scope(result, {'recall_scope': scope}, [attribution])
        return result

    def test_attribution_must_explain_both_routes_to_one_select(self):
        scope = expected_scope(BOUNDARIES / 'branch.expected', lambda row: row == 'Sink: stdlib')
        self.assertEqual(len(scope['x.go:10']), 1)
        self.assertFalse(scope['x.go:10'][0]['included'])
        self.assertEqual(scope['x.go:10'][0]['source_models'],
                         ['Source: framework.A', 'Source: framework.B'])
        for endpoint in ('Source: framework.A', 'Source: framework.B'):
            with self.subTest(endpoint=endpoint):
                result = self.boundary_result(scope, endpoint)
                self.assertFalse(result['pass'])
                self.assertEqual(result['deferred_misses'], [])
                self.assertEqual(result['scoped_misses'], ['x.go:10'])
                self.assertIn('does not explain every path', result['errors'][0])

    def test_unproven_alternative_endpoint_blocks_framework_deferral(self):
        for role, opposite in (('source', 'Sink'), ('sink', 'Source')):
            with self.subTest(role=role):
                scope = expected_scope(BOUNDARIES / f'unproven-{role}.expected',
                                       lambda row: row == f'{opposite}: stdlib')
                self.assertTrue(scope['x.go:10'][0]['included'])
                result = self.boundary_result(scope, f'{role.title()}: framework.A')
                self.assertFalse(result['pass'])
                self.assertEqual(result['deferred_misses'], [])
                self.assertEqual(result['scoped_misses'], ['x.go:10'])

    def test_source_spellings_and_node_proof_apply_to_every_route(self):
        original = (BOUNDARIES / 'branch.expected').read_text()
        for spelling in ('Src', 'Source'):
            with self.subTest(spelling=spelling), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'check.expected'
                # A common source model on both first edges permits deferral.
                text = original.replace('Source:MaD:2', f'{spelling}:MaD:1')
                text = text.replace('Src:MaD:1', f'{spelling}:MaD:1')
                path.write_text(text)
                scope = expected_scope(path, lambda row: row == 'Sink: stdlib')
                self.assertTrue(self.boundary_result(scope, 'Source: framework.A')['pass'])
                # Node evidence also proves a common endpoint on divergent edges.
                path.write_text(original + '\nnodes\n'
                                f'| x.go:1:1:1:2 | source | provenance | {spelling}:MaD:1 |\n')
                scope = expected_scope(path, lambda row: row == 'Sink: stdlib')
                self.assertTrue(self.boundary_result(scope, 'Source: framework.A')['pass'])

    def test_distinct_source_rows_at_one_alert_remain_independent(self):
        scope = expected_scope(BOUNDARIES / 'distinct-sources.expected',
                               lambda row: row == 'Sink: stdlib')
        self.assertEqual(len(scope['x.go:10']), 2)
        self.assertEqual([p['included'] for p in scope['x.go:10']], [False, True])
        self.assertTrue(self.boundary_result({'x.go:10': scope['x.go:10'][:1]},
                                            'Source: framework.A')['pass'])
        result = self.boundary_result(scope, 'Source: framework.A')
        self.assertFalse(result['pass'])
        self.assertEqual(result['scoped_misses'], ['x.go:10'])
        self.assertEqual(result['deferred_misses'], [])

    def test_model_numbering_is_independent_per_expected_file(self):
        catalogs = {'Source: stdlib', 'Sink: stdlib'}
        oracle = load_oracle(BOUNDARIES / 'numbering', 'Example.ql', GoStager(), 'example', catalogs)
        paths = oracle['recall_scope']['x.go:10']
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0]['source_models'], ['Source: framework.A'])
        self.assertEqual(paths[1]['source_models'], ['Source: stdlib'])
        self.assertEqual([p['included'] for p in paths], [False, True])
        result = self.boundary_result(oracle['recall_scope'], 'Source: framework.A')
        self.assertFalse(result['pass'])
        self.assertEqual(result['scoped_misses'], ['x.go:10'])

    def test_go_catalog_requires_every_printed_field_to_match(self):
        directory, _, _ = self.inputs('go')
        catalogs = set(json.loads((directory / 'catalog.json').read_text()))
        for row in catalogs:
            self.assertTrue(GoStager.model_in_catalog(row, catalogs))
            for index, field in enumerate(row.split(';')):
                with self.subTest(row=row, field=index):
                    fields = row.split(';')
                    fields[index] = field + 'x'
                    mismatch = ';'.join(fields)
                    self.assertFalse(GoStager.model_in_catalog(mismatch, catalogs))
                    with tempfile.TemporaryDirectory() as tmp:
                        path = Path(tmp) / 'check.expected'
                        path.write_text((directory / 'check.expected').read_text().replace(row, mismatch))
                        scope = expected_scope(path, lambda model: GoStager.model_in_catalog(model, catalogs))
                        self.assertFalse(scope['sample.go:10'][0]['included'])

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
