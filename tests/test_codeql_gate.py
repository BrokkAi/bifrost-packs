"""Synthetic, authored fixtures only: never vendor upstream CodeQL test sources."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Upstream scripts are content-locked; importing tests must not add bytecode.
sys.dont_write_bytecode = True

from scripts.upstream.codeql_gate.core import (GateError, inline_expectations, load_oracle, parse_expected,
                                               report_analyzed_paths, score, write_results)
from scripts.upstream.codeql_gate.stagers.go import GoStager
from scripts.upstream.codeql_gate.compare_sarif import compare

FIXTURES = Path(__file__).parent / 'fixtures/codeql_gate'
GATE = Path(__file__).resolve().parents[1] / 'scripts/upstream/codeql_gate/gate.py'


def report(*locations, complete=True):
    return {'scope': {'analyzed_files': ['sample.go', 'sink.go', 'tagged.go', 'classes.go', 'block.go']},
            'runs': [{'policy_id': 'example', 'completion': {'type': 'complete'} if complete else {'type': 'proven_subset', 'codes': ['branch_relation_derivation_incomplete']},
                     'diagnostics': [], 'work': {'scanned_files': 1},
                     'findings': [{'primary': {'path': p, 'region': {'start_line': n, 'end_line': end}},
                                   'completeness': {'type': 'complete'}} for p, n, end in locations]}]}


class ResultTests(unittest.TestCase):
    def test_summary_completion_scores_and_records_model_provenance(self):
        data = json.loads((FIXTURES / 'summary-completion.json').read_text())
        oracle = {'expected': [{'path': 'sample.go', 'start': 1, 'end': 1},
                               {'path': 'sample.go', 'start': 3, 'end': 3}],
                  'spurious': [], 'missing': [], 'testFailures': [],
                  'oracle_sources': {}, 'oracle_disagreement': None}
        result = score(data, oracle)
        self.assertTrue(result['complete'])
        self.assertEqual(result['completion_kinds'], ['complete', 'proven_by_summary'])
        self.assertEqual(result['summary_counts'], {'verdicts': 1, 'true_positives': 1,
                                                    'false_positives': 1})
        summary_finding = next(f for f in result['findings'] if f['start'] == 1)
        self.assertEqual(summary_finding['completion_kind'], 'proven_by_summary')
        self.assertEqual(len(result['activated_packs']), 2)
        self.assertIn('version 1.2.3', result['activated_packs'][0]['reason'])
        self.assertEqual(result['activated_packs'][1]['version'], '1.2.3')
        self.assertEqual(result['verdict'], 'FP')
        with tempfile.TemporaryDirectory() as temporary:
            write_results(Path(temporary), dict(result, query='example', binary_sha256='digest',
                                                 codeql_commit='commit', errors=[]))
            payload = json.loads((Path(temporary) / 'result.json').read_text())
            self.assertEqual(payload['completion_kind'], 'mixed')
            self.assertEqual(payload['findings'][0]['completion_kind'], 'proven_by_summary')
            self.assertEqual(payload['activated_packs'][1]['version'], '1.2.3')
            markdown = (Path(temporary) / 'result.md').read_text()
            self.assertIn('Summary-backed counts:', markdown)
            self.assertIn('bifrost.example-summaries', markdown)

    def test_only_complete_and_summary_completion_are_scorable(self):
        oracle = {'expected': [], 'spurious': [], 'missing': [], 'testFailures': [],
                  'oracle_sources': {}, 'oracle_disagreement': None}
        for kind in ('partial', 'inconclusive', 'proven_subset', 'unsupported', 'not_run'):
            with self.subTest(kind=kind):
                result = score({'runs': [{'completion': {'type': kind}, 'findings': []}]}, oracle)
                self.assertFalse(result['complete'])
        result = score({'runs': [{'completion': {'type': 'complete'}, 'findings': []}]}, oracle)
        self.assertTrue(result['complete'])
        incomplete = score({'runs': [{'completion': {'type': 'proven_by_summary'}, 'findings': [
            {'primary': {'path': 'sample.go', 'region': {'start_line': 1, 'end_line': 1}},
             'completeness': {'type': 'incomplete'}}]}]}, oracle)
        self.assertFalse(incomplete['complete'])

    def test_java_stub_status_is_reported_in_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            result = dict(query='example', verdict='EXACT-INCOMPLETE', **{'pass': False}, complete=True,
                          matched=[], false_positives=[], silent_misses=[], abstentions=[],
                          spurious={'sites': [], 'findings': []}, missing={'sites': [], 'findings': []},
                          errors=[], oracle_sources={}, oracle_disagreement={}, binary_sha256='digest',
                          codeql_commit='commit', staged_artifacts=[{
                              'stub_dir': 'broken-stub', 'staging_status': 'unstaged',
                              'staging_diagnostic': 'broken.java:3: error: unresolved type'
                          }, {
                              'stub_dir': 'auxiliary-stub', 'staging_status': 'built',
                              'staging_kind': 'auxiliary', 'auxiliary_package': 'shared.api',
                              'auxiliary_trigger': 'Use.java:1: package shared.api does not exist'
                          }])
            write_results(run_dir, result)
            payload = json.loads((run_dir / 'result.json').read_text())
            markdown = (run_dir / 'result.md').read_text()
            self.assertEqual(payload['staged_artifacts'][0]['staging_status'], 'unstaged')
            self.assertIn('broken-stub', markdown)
            self.assertIn('broken.java:3: error: unresolved type', markdown)
            self.assertIn('auxiliary package `shared.api`', markdown)
            self.assertIn('package shared.api does not exist', markdown)


class OracleTests(unittest.TestCase):
    def oracle(self, name):
        return load_oracle(FIXTURES / name, 'Example.ql', GoStager(), 'example')

    def test_problem_first_section_only(self):
        self.assertEqual([r['start'] for r in self.oracle('problem')['expected']], [3])

    def test_path_problem_first_column_only(self):
        self.assertEqual(self.oracle('path')['expected'][0]['path'], 'sink.go')
        self.assertEqual(len(self.oracle('path')['expected']), 1)

    def test_bare_models_heading_stops_headerless_select(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'check.expected'
            path.write_text('| example.go:3:1:3:2 | alert |\nmodels\n| example.package | model |\n')
            rows, failures = parse_expected(path)
            self.assertEqual([(r['path'], r['start']) for r in rows], [('example.go', 3)])
            self.assertEqual(failures, [])

    def test_go_alerts_and_taint_ignore_path_ends_and_strings(self):
        oracle = self.oracle('inline')
        self.assertEqual([r['start'] for r in oracle['expected']], [3, 4, 5])
        self.assertEqual(oracle['oracle_disagreement']['inline_only'], ['tagged.go:4', 'tagged.go:5'])
        self.assertEqual(len(oracle['oracle_sources']['inline_taint']), 1)

    def test_qualified_tags_count_only_for_their_query(self):
        # Shaped like CodeQL's Go CWE-078 directory, where command-injection and
        # stored-command share one test directory and qualify their tags.
        def classes(query_path, query_id):
            oracle = load_oracle(FIXTURES / 'qualified', query_path, GoStager(), query_id)
            return [sorted(r['start'] for r in oracle[name]) for name in ('expected', 'missing', 'spurious')]
        self.assertEqual(classes('CommandInjection.ql', 'go/command-injection'), [[3, 5, 6], [7], []])
        self.assertEqual(classes('StoredCommand.ql', 'go/stored-command'), [[4, 5, 6, 7], [], [8]])

    def test_expectation_tag_lists_columns_and_remarks(self):
        def parse(contents):
            return list(inline_expectations(contents))
        self.assertEqual(parse(' $ Source Alert'), [(None, 'Source', None), (None, 'Alert', None)])
        self.assertEqual(parse(' $ Alert[go/a], Alert[go/b]=r1 Sink'),
                         [(None, 'Alert', 'go/a'), (None, 'Alert', 'go/b'), (None, 'Sink', None)])
        self.assertEqual(parse(' $ Alert MISSING: Alert[go/a] SPURIOUS: hasTaintFlow="x y" MISSING: Sink'),
                         [(None, 'Alert', None), ('MISSING', 'Alert', 'go/a'), ('SPURIOUS', 'hasTaintFlow', None),
                          ('MISSING', 'Sink', None)])
        self.assertEqual(parse(' $ Alert // remark $ Alert[go/a]'), [(None, 'Alert', None)])
        self.assertEqual(parse(' note $ Alert'), [])
        self.assertEqual(parse(' $Alert'), [])

    def test_inline_tags_name_the_result_ending_on_their_line(self):
        # CodeQL matches a tag to a result whose end line is the tag's line, so a
        # tag on a block's closing line names that #select row, not a second site.
        oracle = self.oracle('endline')
        self.assertEqual([(r['start'], bool(r.get('end_line_only'))) for r in oracle['expected']],
                         [(3, False), (14, True)])
        self.assertEqual([r['start'] for r in oracle['spurious']], [8])
        self.assertEqual(oracle['oracle_disagreement'], {'select_only': [], 'inline_only': ['block.go:14']})
        self.assertTrue(score(report(('block.go', 3, 6), ('block.go', 12, 14)), oracle)['pass'])
        result = score(report(('block.go', 3, 6), ('block.go', 8, 10), ('block.go', 13, 13)), oracle)
        self.assertEqual(result['false_positives'], ['block.go:13', 'block.go:8'])
        self.assertEqual(result['silent_misses'], ['block.go:14'])

    def test_inline_tags_count_only_for_post_processed_references(self):
        # qltest reads tags only for a reference that post-processes with
        # InlineExpectationsTestQuery; Plain.qlref's oracle is its .expected.
        def sites(query_path, query_id):
            oracle = load_oracle(FIXTURES / 'postprocess', query_path, GoStager(), query_id)
            return [r['start'] for r in oracle['expected']]
        self.assertEqual(sites('Tagged.ql', 'go/tagged'), [3])
        self.assertEqual(sites('Plain.ql', 'go/plain'), [5])
        # The post-process may be a block or flow list, with other entries around it.
        self.assertEqual(sites('List.ql', 'go/list'), [3])
        self.assertEqual(sites('Flow.ql', 'go/flow'), [3])
        self.assertEqual(sites('Other.ql', 'go/other'), [])
        self.assertEqual(sites('Flush.ql', 'go/flush'), [3])

    def test_file_level_alert_matches_a_whole_file_finding(self):
        root = FIXTURES / 'filelevel'
        oracle = load_oracle(root, 'Example.ql', GoStager(), 'example')
        size = (root / 'conf.xml').stat().st_size
        def run(start, end, first_line, last_line):
            return {'scope': {'analyzed_files': ['conf.xml']},
                    'runs': [{'policy_id': 'example', 'completion': {'type': 'complete'},
                              'diagnostics': [], 'work': {'scanned_files': 1},
                              'findings': [{'primary': {'path': 'conf.xml',
                                                        'byte_span': {'start': start, 'end': end},
                                                        'region': {'start_line': first_line,
                                                                   'end_line': last_line}},
                                            'completeness': {'type': 'complete'}}]}]}
        self.assertTrue(score(run(0, size, 1, 3), oracle, root=root)['pass'])
        partial = score(run(16, 30, 2, 2), oracle, root=root)
        self.assertEqual((partial['false_positives'], partial['silent_misses']), (['conf.xml:2'], ['conf.xml:0']))

    def test_missing_expected_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'check.qlref').write_text('query: Example.ql')
            with self.assertRaises(GateError):
                load_oracle(Path(d), 'Example.ql', GoStager(), 'example')

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

    def test_narrowed_selector_with_low_work_count_passes(self):
        data = report(('sample.go', 3, 3))
        data['runs'][0]['work']['scanned_files'] = 0
        self.assertTrue(score(data, self.oracle('problem'))['pass'])

    def test_unanalyzed_file_abstains_without_hiding_analyzed_misses(self):
        data = report()
        data['scope']['analyzed_files'] = ['tagged.go']
        # A large, duplicated selector work count cannot certify other.go.
        data['runs'][0]['work']['scanned_files'] = 1000
        oracle = self.oracle('inline')
        oracle['expected'].append({'path': 'other.go', 'start': 7, 'end': 7})
        result = score(data, oracle)
        self.assertEqual(result['abstentions'], ['other.go:7'])
        self.assertEqual(result['silent_misses'], ['tagged.go:3', 'tagged.go:4', 'tagged.go:5'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['unanalyzed_expected_files'], ['other.go'])

    def test_scope_inventory_uses_paths_not_completion_gap_scope(self):
        data = report()
        data.pop('scope')
        data['runs'][0]['completion'] = {'type': 'inconclusive', 'reasons': ['capability_incomplete'],
            'scope': {'type': 'files', 'files': ['sample.go'], 'truncated': False}}
        self.assertIsNone(report_analyzed_paths(data))
        data['runs'][0]['scope'] = {'analyzed_files': ['sample.go']}
        self.assertEqual(report_analyzed_paths(data), {'sample.go'})
        data['runs'][0]['scope']['analyzed_files_truncated'] = True
        self.assertIsNone(report_analyzed_paths(data))

    def test_missing_coverage_inventory_abstains(self):
        data = report()
        data.pop('scope')
        self.assertEqual(score(data, self.oracle('problem'))['abstentions'], ['sample.go:3'])

    def test_measured_finding_covers_configuration_file_absent_from_probe(self):
        data = report(('application.yml', 4, 4))
        data['scope']['analyzed_files'] = ['Main.java']
        oracle = {'expected': [{'path': 'application.yml', 'start': 4, 'end': 4}],
                  'spurious': [], 'missing': [], 'oracle_sources': {},
                  'oracle_disagreement': None, 'testFailures': []}
        result = score(data, oracle, analyzed_paths={'Main.java'})
        self.assertEqual(result['verdict'], 'EXACT')
        self.assertTrue(result['complete'])
        self.assertEqual(result['analyzed_files'], ['Main.java', 'application.yml'])

    def test_unmatched_alert_in_measured_finding_file_is_a_silent_miss(self):
        data = report(('application.yml', 4, 4))
        data['scope']['analyzed_files'] = ['Main.java']
        oracle = {'expected': [{'path': 'application.yml', 'start': 4, 'end': 4},
                               {'path': 'application.yml', 'start': 9, 'end': 9}],
                  'spurious': [], 'missing': [], 'oracle_sources': {},
                  'oracle_disagreement': None, 'testFailures': []}
        result = score(data, oracle, analyzed_paths={'Main.java'})
        self.assertEqual(result['silent_misses'], ['application.yml:9'])
        self.assertEqual(result['abstentions'], [])
        self.assertTrue(result['complete'])

    def test_configuration_probe_file_without_findings_has_silent_miss(self):
        data = report()
        oracle = {'expected': [{'path': 'application.yml', 'start': 4, 'end': 4}],
                  'spurious': [], 'missing': [], 'oracle_sources': {},
                  'oracle_disagreement': None, 'testFailures': []}
        result = score(data, oracle, analyzed_paths={'application.yml'})
        self.assertEqual(result['silent_misses'], ['application.yml:4'])
        self.assertEqual(result['abstentions'], [])
        self.assertTrue(result['complete'])

    def test_probe_findings_do_not_extend_measured_file_coverage(self):
        data = {'runs': [{'policy_id': 'bifrost.upstream-gate.analyzed-files',
                          'completion': {'type': 'complete'},
                          'findings': [{'primary': {'path': 'probe-only.java',
                                                    'region': {'start_line': 4, 'end_line': 4}}}]}]}
        oracle = {'expected': [{'path': 'application.yml', 'start': 4, 'end': 4}],
                  'spurious': [], 'missing': [], 'oracle_sources': {},
                  'oracle_disagreement': None, 'testFailures': []}
        result = score(data, oracle, analyzed_paths=set())
        self.assertNotIn('application.yml', result['analyzed_files'])
        self.assertEqual(result['abstentions'], ['application.yml:4'])

    def test_diagnostic_impacts_abstain_only_in_their_region(self):
        for impact in ('declared_non_exhaustive', 'finding_partial'):
            with self.subTest(impact=impact):
                data = report()
                data['runs'][0]['diagnostics'] = [{'impact': impact, 'severity': 'warning',
                    'primary': {'path': 'tagged.go', 'region': {'start_line': 3, 'end_line': 3}}}]
                result = score(data, self.oracle('inline'))
                self.assertEqual(result['abstentions'], ['tagged.go:3'])
                self.assertEqual(result['silent_misses'], ['tagged.go:4', 'tagged.go:5'])
                self.assertFalse(result['complete'])

    def test_partial_finding_does_not_hide_unrelated_silent_misses(self):
        data = report(('tagged.go', 3, 3))
        data['runs'][0]['findings'][0]['completeness'] = {'type': 'partial'}
        result = score(data, self.oracle('inline'))
        self.assertEqual(result['matched'], ['tagged.go:3'])
        self.assertEqual(result['silent_misses'], ['tagged.go:4', 'tagged.go:5'])
        self.assertEqual(result['abstentions'], [])
        self.assertFalse(result['complete'])


    def test_exit_two_with_valid_incomplete_report_is_scored(self):
        data = report(complete=False)
        result = score(data, self.oracle('problem'), exit_code=2)
        self.assertEqual(result['abstentions'], ['sample.go:3'])
        self.assertEqual(result['verdict'], 'EXACT-INCOMPLETE')
        self.assertEqual(result['errors'], [])
        self.assertFalse(result['pass'])
        for bad_execution in ({'termination': 'timeout'}, {'pending_policy_ids': ['example']}):
            with self.subTest(execution=bad_execution):
                data['execution'] = bad_execution
                self.assertEqual(score(data, self.oracle('problem'), exit_code=2)['verdict'], 'ERROR')
        data = report()
        data['runs'][0]['completion'] = {'type': 'failed'}
        self.assertEqual(score(data, self.oracle('problem'), exit_code=2)['verdict'], 'ERROR')
        self.assertEqual(score({}, self.oracle('problem'), exit_code=2)['verdict'], 'ERROR')
        self.assertEqual(score(report(), self.oracle('problem'), exit_code=3)['verdict'], 'ERROR')

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
             "print(json.dumps(" + repr({'scope': report()['scope'], 'rules': [{'policy_id': 'example'}, {'policy_id': 'extra'}],
                    'runs': report()['runs'] + report(('sample.go', 3, 3))['runs']}) + "))\n"))
        binary.chmod(0o755)
        policy = base / 'primary.rqlp'
        extra = base / 'extra.rqlp'
        policy.write_text('(policy)')
        extra.write_text('(policy)')
        # Give the second report run the second rule identity.
        binary.write_text(binary.read_text().replace("'policy_id': 'example', 'completion':", "'policy_id': 'extra', 'completion':", 1))
        if behavior in ('probe', 'probe_timeout', 'probe_incomplete'):
            # No analyzed-file scope: exercise the real core's separate probe.
            text = binary.read_text().replace(repr(report()['scope']), 'None')
            probe_report = report(('sample.go', 1, 1), complete=behavior != 'probe_incomplete')
            probe_report['runs'][0]['policy_id'] = 'bifrost.upstream-gate.analyzed-files'
            probe_report['runs'][0]['findings'][0]['primary']['region'] = None
            probe_report['runs'][0]['findings'][0]['completeness'] = {'type': 'partial', 'reasons': ['query_provenance_truncated']}
            config_probe_run = dict(probe_report['runs'][0],
                                    policy_id='bifrost.upstream-gate.configuration-files', findings=[])
            probe_report['runs'].append(config_probe_run)
            guard = "if any('__codeql_gate_analyzed_files.rqlp' in a or '__codeql_gate_configuration_files.rqlp' in a for a in sys.argv):\n"
            guard += " count=root.parent.parent.parent/'probe-count'\n"
            guard += " count.write_text(str(int(count.read_text())+1) if count.exists() else '1')\n"
            if behavior == 'probe_timeout':
                guard += ' time.sleep(30)\n'
            guard += ' print(json.dumps(' + repr(probe_report) + '))\n sys.exit(1)\n'
            text = text.replace("print(json.dumps(", guard + "print(json.dumps(", 1)
            binary.write_text(text)
        models = base / 'models'
        models.mkdir()
        (models / 'example.json').write_text('{}')
        command = [sys.executable, '-I', str(GATE), 'run', 'go/example', str(policy),
                   '--query-path', 'Example.ql', '--test-dir', str(test_dir), '--codeql-root', str(checkout),
                   '--binary', str(binary), '--state-dir', str(base / 'state'),
                   '--models', str(models), '--extra-policy', str(extra)]
        if behavior == 'timeout':
            command += ['--timeout', '0.1']
        elif behavior == 'probe_timeout':
            command += ['--timeout', '1']
        if keep:
            command += ['--keep']
        proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertTrue(proc.stdout, proc.stderr)
        result = json.loads(proc.stdout)['runs'][0]
        self.last_command = command
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

    def test_file_probe_cached_per_prepared_root_and_binary(self):
        proc, result, base = self.run_gate('probe')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(result['analyzed_files'], ['sample.go'])
        self.assertEqual(result['coverage']['source'], 'file_row_and_configuration_probes')
        self.assertFalse(result['coverage']['cache_hit'])
        self.assertEqual((base / 'state/probe-count').read_text(), '1')
        repeated = subprocess.run(self.last_command, capture_output=True, text=True, timeout=120)
        again = json.loads(repeated.stdout)['runs'][0]
        self.assertTrue(again['pass'])
        self.assertTrue(again['coverage']['cache_hit'])
        self.assertEqual((base / 'state/probe-count').read_text(), '1')
        probe = Path(result['run_dir']) / 'coverage-probe'
        self.assertTrue((probe / 'stdout.json').exists())
        self.assertFalse((probe / 'cache').exists())
        # A changed binary cannot reuse the old coverage inventory.
        binary = base / 'bifrost'
        binary.write_text(binary.read_text() + '\n# new binary identity\n')
        changed = subprocess.run(self.last_command, capture_output=True, text=True, timeout=120)
        self.assertFalse(json.loads(changed.stdout)['runs'][0]['coverage']['cache_hit'])
        self.assertEqual((base / 'state/probe-count').read_text(), '2')

    def test_incomplete_probe_cannot_certify_coverage(self):
        proc, result, _ = self.run_gate('probe_incomplete')
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertEqual(result['abstentions'], ['sample.go:3'])

    def test_probe_timeout_is_error(self):
        proc, result, _ = self.run_gate('probe_timeout')
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertEqual(result['abstentions'], ['sample.go:3'])

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
