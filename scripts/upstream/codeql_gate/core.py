"""Oracle, report scoring and execution generalized from the Java parity gate."""
import csv
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


class GateError(ValueError):
    pass


PROBE_ID = 'bifrost.upstream-gate.analyzed-files'
CONFIG_PROBE_ID = 'bifrost.upstream-gate.configuration-files'
PROBE_IDS = (PROBE_ID, CONFIG_PROBE_ID)


def key(row):
    # A site known only by its end line never merges with a row starting there.
    return (row['path'], row['start']) + (('end',) if row.get('end_line_only') else ())


def site(row):
    return f"{row['path']}:{row['start']}"


def unique(rows):
    # Preserve the widest span when multiple CodeQL rows have one alert anchor.
    out = {}
    for row in rows:
        k = key(row)
        if k not in out or row['end'] > out[k]['end']:
            out[k] = row
    return sorted(out.values(), key=key)


def relative_path(raw, root=None):
    raw = raw.replace('\\', '/')
    path = Path(raw)
    if path.is_absolute():
        if root is None:
            raise GateError(f'absolute path without a root: {raw}')
        try:
            path = path.relative_to(root)
        except ValueError as exc:
            raise GateError(f'path outside test root: {raw}') from exc
    if '..' in path.parts:
        raise GateError(f'non-relative test path: {raw}')
    return path.as_posix()


def parse_expected(path):
    """Read only the first column of #select (or the headerless first section)."""
    rows, failures = [], []
    section = 'select'
    for line in Path(path).read_text(errors='replace').splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            section = stripped[1:].strip().lower()
            continue
        if stripped and not stripped.startswith('|') and section != 'testfailures':
            # qltest also emits bare relation headings (notably models).
            # A later section must never be interpreted as headerless select.
            section = stripped.lower()
            continue
        if section == 'testfailures' and stripped.strip('|').strip():
            failures.append(stripped)
        if section != 'select' or not stripped.startswith('|'):
            continue
        column = stripped.strip('|').split('|', 1)[0].strip()
        match = re.fullmatch(r'(.*):(\d+):(\d+):(\d+):(\d+)', column)
        if not match:
            raise GateError(f'invalid select location in {path}: {column}')
        row = {'path': relative_path(match[1]), 'start': int(match[2]),
               'end': int(match[4]), 'column': int(match[3]),
               'end_column': int(match[5])}
        if row['start'] == 0:
            # CodeQL locates an alert on a whole file as path:0:0:0:0.
            row['file_level'] = True
        rows.append(row)
    return unique(rows), failures


def qlref_query(path):
    text = path.read_text().strip()
    for line in text.splitlines():
        if line.strip().startswith('query:'):
            return line.split(':', 1)[1].strip()
    return text


def qlref_postprocess(path):
    """The `postprocess` entries of a .qlref: a scalar, a flow list or a block list."""
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        if not line.startswith('postprocess:'):
            continue
        value = line.split(':', 1)[1].strip()
        if value.startswith('['):
            return [item.strip() for item in value.strip('[]').split(',') if item.strip()]
        if value:
            return [value]
        entries = []
        for item in lines[index + 1:]:
            if not item.strip():
                continue
            # YAML allows the items indented or at column 0 under the key.
            if not item.strip().startswith('- '):
                break
            entries.append(item.strip()[2:].strip())
        return entries
    return []


def qlref_uses_inline_expectations(path):
    # qltest checks inline tags only for a query whose reference post-processes
    # its results with InlineExpectationsTestQuery; without it the .expected
    # file alone is the oracle, and tags in the directory belong to another query.
    return any(entry.endswith('InlineExpectationsTestQuery.ql') for entry in qlref_postprocess(path))


# CodeQL's inline expectation grammar (shared/util/codeql/util/test/
# InlineExpectationsTest.qll): a comment whose contents start with `$ ` holds
# expectations up to a `//` or `#` remark. Each `MISSING:` or `SPURIOUS:` opens
# a column that runs to the next one. A column holds `tag(,tag)*(=value)?`
# items separated by whitespace, and a tag may carry a bracketed query id, as
# in `Alert[go/command-injection]`.
_EXPECTATION_COMMENT = re.compile(r'\s*\$ ((?:[^/]|/[^/])*)(?:(//|#).*)?', re.S)
_EXPECTATION_TAG = r'[A-Za-z\-_](?:[A-Za-z\-_0-9]|\[[^\]\]]*\])*'
_EXPECTATION = re.compile(r'((?:{0})(?:\s*,\s*{0})*)(?:=((?:[bru]*"[^"]*"|[bru]*\'[^\']*\'|\S+)*))?'
                          .format(_EXPECTATION_TAG))
_COLUMN_NAME = re.compile(r'(MISSING|SPURIOUS):')


def inline_expectations(contents):
    """Yield (column, tag, qualifier) for each expectation in one comment's contents.

    `column` is None, 'MISSING' or 'SPURIOUS'; `qualifier` is the bracketed text
    of a tag such as `Alert[go/sql-injection]`, or None.
    """
    match = _EXPECTATION_COMMENT.fullmatch(contents)
    if not match:
        return
    content = match.group(1)
    marks = list(_COLUMN_NAME.finditer(content))
    columns = [(None, 0, marks[0].start() if marks else len(content))]
    columns += [(mark.group(1), mark.end(), marks[i + 1].start() if i + 1 < len(marks) else len(content))
                for i, mark in enumerate(marks)]
    for column, start, end in columns:
        for expectation in _EXPECTATION.finditer(content, start, end):
            for tag in re.split(r'\s*,\s*', expectation.group(1)):
                name, qualifier = re.fullmatch(r'([^\[]*)(?:\[(.*)\])?', tag, re.S).groups()
                yield column, name, qualifier


def add_inline_expectations(result, location, contents, query_id, alert_keys):
    """Add one comment's alert expectations for `query_id` to an inline oracle.

    `alert_keys` maps each tag that marks an alert to its oracle key, for example
    {'Alert': 'inline_alert'}; other tags (Source, Sink, RelatedLocation) add
    nothing. As in CodeQL, an unqualified tag applies to every query of the test
    directory and a tag qualified with another query's id is dropped.
    """
    for column, tag, qualifier in inline_expectations(contents):
        if tag in alert_keys and qualifier in (None, query_id):
            result[column.lower() if column else alert_keys[tag]].append(dict(location))


def load_oracle(test_dir, query_path, stager, query_id, scope_catalogs=None):
    refs = [p for p in sorted(test_dir.glob('*.qlref'))
            if qlref_query(p) == query_path or qlref_query(p).endswith('/' + query_path)]
    if not refs:
        raise GateError(f'no .qlref for {query_path} in {test_dir}')
    selected, failures = [], []
    recall_scope = {}
    for ref in refs:
        expected_file = ref.with_suffix('.expected')
        if not expected_file.is_file():
            raise GateError(f'missing expected file: {expected_file}')
        rows, unreliable = parse_expected(expected_file)
        if scope_catalogs is not None:
            try:
                from .scoped import expected_scope
            except ImportError:
                from scoped import expected_scope
            if not hasattr(stager, 'model_in_catalog'):
                raise GateError('stager does not supply catalog membership')
            scopes = expected_scope(expected_file, lambda row: stager.model_in_catalog(row, scope_catalogs))
            for anchor, paths in scopes.items():
                recall_scope.setdefault(anchor, []).extend(paths)
        selected.extend(rows)
        failures.extend(unreliable)
    inline = (stager.inline_oracle(test_dir, query_id)
              if hasattr(stager, 'inline_oracle') and any(map(qlref_uses_inline_expectations, refs))
              else {})
    selected = unique(selected)
    # CodeQL matches a tag on line L to a result whose END line is L
    # (InlineExpectationsTest.qll, onSameLine). A tag therefore names the
    # #select rows of its file that end on L; a tag with no such row is a site
    # known only by its end line, matched against a finding's end line.
    ending = {}
    for row in selected:
        ending.setdefault((row['path'], row['end']), []).append(row)
    def resolve(tags):
        return unique([row for tag in tags for row in
                       ending.get((tag['path'], tag['start']),
                                  [dict(tag, end=tag['start'], end_line_only=True)])])
    spurious, missing = resolve(inline.get('spurious', [])), resolve(inline.get('missing', []))
    overrides = {key(r) for r in spurious + missing}
    raw_tags = inline.get('inline_alert', []) + inline.get('inline_taint', [])
    tags = resolve(raw_tags)
    sources = {'select': selected, **inline}
    disagreement = None
    if raw_tags:
        tagged = {(t['path'], t['start']) for t in raw_tags + inline.get('spurious', [])}
        disagreement = {'select_only': [site(r) for r in selected if (r['path'], r['end']) not in tagged],
                        'inline_only': [site(r) for r in tags if r.get('end_line_only')]}
    return {'expected': [r for r in unique(selected + tags) if key(r) not in overrides],
            'spurious': spurious, 'missing': missing, 'oracle_sources': sources,
            'oracle_disagreement': disagreement, 'testFailures': failures,
            **({'recall_scope': recall_scope} if scope_catalogs is not None else {})}


def report_findings(data, root=None):
    findings = []
    for run in data.get('runs', []):
        for finding in run.get('findings', []):
            primary = finding['primary']
            region = primary['region']
            start, end = region['start_line'], region['end_line']
            if not isinstance(start, int) or not isinstance(end, int) or not 0 < start <= end:
                raise GateError('invalid finding region')
            path = relative_path(primary['path'], root)
            span = primary.get('byte_span') or {}
            # Bifrost anchors a file-level finding on the whole file.
            whole_file = (root is not None and span.get('start') == 0
                          and span.get('end') == (Path(root) / path).stat().st_size)
            findings.append({'path': path, 'start': start, 'end': end, 'whole_file': whole_file,
                             'policy_id': run.get('policy_id') or finding.get('policy_id'),
                             'completeness': finding.get('completeness', {})})
    return findings


def diagnostic_groups(diagnostics):
    counts, messages, families = Counter(), {}, Counter()
    for diagnostic in diagnostics:
        family = diagnostic.get('family') or str(diagnostic.get('code', 'unknown'))
        families[family] += diagnostic.get('family_count', 1)
        low = str(diagnostic.get('code', '')).lower() + ' ' + diagnostic.get('message', '').lower()
        for name in ('empty_selection', 'partial', 'unresolved', 'unsupported', 'incomplete'):
            if name in low:
                counts[name] += 1
                messages.setdefault(name, []).append(diagnostic.get('message', ''))
    return dict(counts), {k: v[:5] for k, v in messages.items()}, dict(families)


def report_analyzed_paths(data, root=None):
    """Read an explicit analyzed-file inventory, never completion's gap scope.

    Current schema 6 only lists examined_procedures in a run scope, so it
    needs a probe. Accept an explicit analyzed_files scope when provided by
    a producer; a truncated or absent inventory cannot certify membership.
    """
    def inventory(scope):
        if (not isinstance(scope, dict) or 'analyzed_files' not in scope
                or scope.get('truncated') or scope.get('analyzed_files_truncated')):
            return None
        files = scope['analyzed_files']
        if not isinstance(files, list) or any(not isinstance(p, str) for p in files):
            raise GateError('scope.analyzed_files must be a list of paths')
        return {relative_path(p, root) for p in files}
    top = inventory(data.get('scope'))
    if top is not None:
        return top
    inventories = [inventory(r.get('scope')) for r in data.get('runs', [])]
    if not inventories or any(paths is None for paths in inventories):
        return None
    # Each policy run must have had the expected file available.
    return set.intersection(*inventories)


def score(data, oracle, *, root=None, exit_code=0, anchors=None, true_positives=(),
          analyzed_paths=None, required_policy_ids=()):
    runs = data.get('runs') or []
    errors = []
    if not runs:
        errors.append('missing runs')
    if any(r.get('completion', {}).get('type') == 'failed' for r in runs):
        errors.append('failed policy run')
    # CLI 1 means findings; 2 can mean a valid incomplete report. Trust that
    # report only if execution reached a terminal report without failed runs.
    execution = data.get('execution', {})
    valid_incomplete_exit = (exit_code == 2 and bool(runs)
                             and all(r.get('completion', {}).get('type') in
                                     {'complete', 'proven_subset', 'proven_by_summary',
                                      'inconclusive', 'not_run', 'unsupported'} for r in runs)
                             and not execution.get('termination')
                             and not execution.get('pending_policy_ids'))
    if exit_code not in (0, 1) and not valid_incomplete_exit:
        errors.append(f'binary exit {exit_code}')
    diagnostics = list(data.get('diagnostics', [])) + [d for r in runs for d in r.get('diagnostics', [])]
    if any(d.get('severity') == 'error' or 'validation' in str(d.get('code', '')).lower()
           for d in diagnostics):
        errors.append('policy validation or report error diagnostic')
    if set(required_policy_ids) - {r.get('policy_id') for r in runs}:
        errors.append('missing policy run')
    if oracle.get('testFailures'):
        errors.append('nonempty CodeQL testFailures')
    findings = report_findings(data, root)
    got = unique(findings)
    expected = oracle['expected']
    anchors = anchors or {}
    offset = anchors.get('line_offset', 0)
    relation = anchors.get('relation', 'start_line')
    if relation not in ('start_line', 'span_overlap') or not isinstance(offset, int):
        raise GateError('anchor requires integer line_offset and start_line/span_overlap relation')
    def matches(e, f):
        if e['path'] != f['path']:
            return False
        if e.get('file_level'):
            return f.get('whole_file', False)
        if e.get('end_line_only'):
            # An inline tag without a #select row gives only the end line.
            line = e['end'] + offset
            return f['end'] == line if relation == 'start_line' else f['start'] <= line <= f['end']
        return (e['start'] + offset == f['start'] if relation == 'start_line' else
                e['start'] + offset <= f['end'] and f['start'] <= e['end'] + offset)
    # Maximum one-to-one assignment avoids double counting with overlapping spans.
    owners = {}
    def assign(index, seen):
        for j, finding in enumerate(got):
            if j in seen or not matches(expected[index], finding):
                continue
            seen.add(j)
            if j not in owners or assign(owners[j], seen):
                owners[j] = index
                return True
        return False
    for index in range(len(expected)):
        assign(index, set())
    matched_indices = set(owners.values())
    matched = [site(e) for i, e in enumerate(expected) if i in matched_indices]
    loose = [{'expected': f"{e['path']}:{e['start']}-{e['end']}",
              'finding': f"{f['path']}:{f['start']}-{f['end']}"}
             for e in expected for f in got if e['path'] == f['path']
             and e['start'] <= f['end'] and f['start'] <= e['end'] and key(e) != key(f)]
    def listed(row, entries):
        return any(matches(e, row) for e in entries)
    allowed = [{'path': p['path'], 'start': p['line'], 'end': p['line']} for p in true_positives]
    spurious = [site(f) for f in got if listed(f, oracle['spurious'])]
    false_positives = sorted(set(spurious + [site(f) for j, f in enumerate(got)
                              if j not in owners and not listed(f, oracle['missing'])
                              and key(f) not in {key(p) for p in allowed}]))
    completion = next((r.get('completion', {}) for r in runs
                       if r.get('completion', {}).get('type') != 'complete'),
                      runs[0].get('completion', {}) if runs else {})
    incomplete_impacts = {'declared_non_exhaustive', 'finding_partial',
                          'run_incomplete', 'run_unsupported'}
    def bad_diagnostic(d):
        return (d.get('impact') in incomplete_impacts or
                d.get('impact') is None and any(s in str(d.get('code', '')).lower() for s in
                    ('empty_selection', 'unsupported', 'incomplete', 'unresolved', 'partial')))
    incomplete_diagnostics = [d for d in diagnostics if bad_diagnostic(d)]
    truncated = any(d.get('diagnostics_truncated') or d.get('obligations_truncated') or
                    d.get('work', {}).get('omitted_findings_lower_bound', 0) for d in [data] + runs)
    execution = data.get('execution', {})
    interrupted = bool(execution.get('termination') or execution.get('pending_policy_ids'))
    # Work counts sum selector activity and cannot establish file membership.
    # A measured-policy finding does establish that its file was analyzed, even
    # when the generic File-row probe cannot inventory that file type.
    source_paths = report_analyzed_paths(data, root) if analyzed_paths is None else set(analyzed_paths)
    finding_paths = {finding['path'] for finding in findings
                     if finding['policy_id'] not in PROBE_IDS}
    if source_paths is not None or finding_paths:
        source_paths = (source_paths or set()) | finding_paths
    unanalyzed_files = sorted({e['path'] for e in expected} - (source_paths or set()))
    coverage_unknown = bool(unanalyzed_files)
    complete = (bool(runs) and all(r.get('completion', {}).get('type') == 'complete' for r in runs)
                and not incomplete_diagnostics and not truncated and not interrupted
                and not coverage_unknown and not errors
                and all(f['completeness'].get('type', 'complete') == 'complete' for f in findings))
    def abstained(e):
        if e['path'] in unanalyzed_files or truncated or interrupted or errors or not runs:
            return True
        for run in runs:
            comp = run.get('completion', {})
            if comp.get('type') == 'complete':
                continue
            scope = comp.get('scope', {})
            # Only a nontruncated, nonempty typed Files scope promises that
            # misses outside these files have complete coverage.
            if (scope.get('type') != 'files' or scope.get('truncated', True)
                    or not scope.get('files')):
                return True
            if e['path'] in {relative_path(p, root) for p in scope['files']}:
                return True
        relevant = list(data.get('diagnostics', [])) + [d for r in runs
                    if r.get('completion', {}).get('type') == 'complete'
                    for d in r.get('diagnostics', [])]
        for d in (d for d in relevant if bad_diagnostic(d)):
            primary = d.get('primary')
            if not primary:
                return True
            if relative_path(primary['path'], root) == e['path']:
                region = primary.get('region')
                if not region or region['start_line'] <= e['start'] <= region['end_line']:
                    return True
        return False
    absent = [e for i, e in enumerate(expected) if i not in matched_indices]
    abstentions = [site(e) for e in absent if abstained(e)]
    silent = [site(e) for e in absent if not abstained(e)]
    verdict = ('ERROR' if errors else 'FP+MISS' if false_positives and silent else
               'FP' if false_positives else 'EMPTY' if silent and not got else
               'MISS' if silent else 'EXACT' if complete else 'EXACT-INCOMPLETE')
    passed = complete and not (false_positives or silent or abstentions or errors)
    dcounts, dmsgs, families = diagnostic_groups(diagnostics)
    return {'verdict': verdict, 'tp': matched, 'fp': false_positives,
            'fn': [site(e) for e in absent], 'loose_matches': loose,
            'completion': completion, 'completion_type': completion.get('type', 'no_runs'),
            'diagnostics': dcounts, 'diagnostic_messages': dmsgs, 'diagnostics_by_family': families,
            'expected': expected, 'findings': findings, 'matched': matched,
            'false_positives': false_positives, 'silent_misses': silent, 'abstentions': abstentions,
            'spurious': {'sites': oracle['spurious'], 'findings': spurious},
            'missing': {'sites': oracle['missing'], 'findings': [site(f) for f in got if listed(f, oracle['missing'])]},
            'oracle_sources': oracle['oracle_sources'], 'oracle_disagreement': oracle['oracle_disagreement'],
            'complete': complete, 'pass': passed, 'errors': errors, 'coverage_unknown': coverage_unknown,
            'analyzed_files': sorted(source_paths) if source_paths is not None else None,
            'unanalyzed_expected_files': unanalyzed_files,
            'anchors': anchors, 'true_positives': list(true_positives)}


def write_results(run_dir, result):
    (run_dir / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    rows = ['| Class | Sites |', '| --- | --- |']
    for name in ('matched', 'false_positives', 'silent_misses', 'abstentions'):
        rows.append(f"| {name} | {', '.join(result[name]) or '—'} |")
    for name in ('spurious', 'missing'):
        rows.append(f"| {name} sites | {', '.join(site(r) for r in result[name]['sites']) or '—'} |")
        rows.append(f"| {name} findings | {', '.join(result[name]['findings']) or '—'} |")
    (run_dir / 'result.md').write_text(
        f"{result['query']}: " +
        (result['verdict'] if 'full_suite_verdict' in result else
         'PASS' if result['pass'] else result['verdict']) +
        (f"; full suite: {result['full_suite_verdict']}" if 'full_suite_verdict' in result else '') +
        '\n\n' + '\n'.join(rows) +
        f"\n\nComplete: {result['complete']}. Errors: {result['errors']}\n"
        f"\nOracle sources: {', '.join(f'{k}={len(v)}' for k, v in result['oracle_sources'].items())}.\n"
        f"Disagreement: {json.dumps(result['oracle_disagreement'])}\n"
        f"\nBinary SHA256: `{result['binary_sha256']}`\n"
        f"CodeQL commit: `{result['codeql_commit']}`\n")


PROBE_POLICY = """(policy
  :schema-version 1
  :id "bifrost.upstream-gate.analyzed-files"
  :name "Upstream gate analyzed file inventory"
  :message "Analyzed file"
  :severity note
  :analysis (analysis
    :type match
    :selector (rql :schema-version 1
      (file-of (text/regex "(?s).*")))))
"""

CONFIG_PROBE_POLICY = """(policy
  :schema-version 1
  :id "bifrost.upstream-gate.configuration-files"
  :name "Upstream gate configuration file inventory"
  :message "Configuration fact inventory"
  :severity note
  :analysis (analysis
    :type match
    :selector (rql :schema-version 1
      (configuration-facts))))
"""


def invoke(command, root, env, output_dir, timeout):
    output_dir.mkdir(parents=True, exist_ok=True)
    timed_out = False
    with (output_dir / 'stdout.json').open('w') as stdout, (output_dir / 'stderr.txt').open('w') as stderr:
        process = subprocess.Popen(['nice', '-n', '10', *command], cwd=root, env=env,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    (output_dir / 'exit-code.txt').write_text(str(process.returncode) + '\n')
    return process.returncode, timed_out


def probe_analyzed_paths(args, prepared, stager, root, env, run_dir):
    """Probe source File rows and configuration facts for analyzed file paths.

    The universal text predicate selects source facts without a language/path
    restriction. FileOf deduplicates source facts to files. Configuration facts
    are selected directly because this binary does not allow FileOf to consume
    their domain. Probe findings never enter the measured policy's findings,
    diagnostics or scores.
    """
    digest = hashlib.sha256((PROBE_POLICY + CONFIG_PROBE_POLICY).encode())
    digest.update(str(prepared.root.resolve()).encode())
    digest.update(hashlib.sha256(args.binary.read_bytes()).digest())
    # Only variables that can change what the probe sees take part: the keys
    # the stager sets, toolchain and Bifrost settings, and PATH. Shell state
    # such as PWD, OLDPWD, SHLVL or `_` would only cause spurious cache misses.
    # Per-run values (paths under the run directory) are excluded as well.
    stager_keys = set(stager.run_env(run_dir, prepared))
    def relevant(name):
        return (name in stager_keys or name == 'PATH'
                or name.startswith(('GO', 'BIFROST_', 'JAVA', 'RAYON_')))
    stable_env = {k: v for k, v in env.items() if relevant(k) and str(run_dir) not in v}
    digest.update(json.dumps(stable_env, sort_keys=True).encode())
    models = root / '.bifrost/semantic-models'
    if models.exists():
        for path in sorted(p for p in models.rglob('*') if p.is_file()):
            digest.update(path.relative_to(models).as_posix().encode() + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    cache_dir = args.state_dir / 'coverage'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / (digest.hexdigest() + '.json')
    with cache_file.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if cache_file.exists():
            cached = json.loads(cache_file.read_text())
            return set(cached['analyzed_files']), dict(cached, cache_hit=True)
        policies = [
            (root / '.bifrost/policies' / '__codeql_gate_analyzed_files.rqlp', PROBE_POLICY),
            (root / '.bifrost/policies' / '__codeql_gate_configuration_files.rqlp', CONFIG_PROBE_POLICY),
        ]
        if any(policy.exists() for policy, _ in policies):
            raise GateError('policy basename reserved for analyzed-file probes')
        # Write the probe policies inside the try so a failure part-way through
        # setup still removes whatever was written; missing_ok keeps cleanup from
        # masking that failure.
        try:
            for policy, contents in policies:
                policy.write_text(contents)
            output = run_dir / 'coverage-probe'
            probe_env = dict(env)
            probe_env.update(HOME=str(output / 'home'), USERPROFILE=str(output / 'home'),
                             BIFROST_CACHE_ROOT=str(output / 'cache'),
                             BIFROST_SEMANTIC_PACK_CACHE_ROOT=str(output / 'semantic-pack-cache'),
                             XDG_CACHE_HOME=str(output / 'xdg'))
            probe_env.update(stager.run_env(output, prepared))
            (output / 'home').mkdir(parents=True)
            command = [str(args.binary), '--root', str(root), '--no-builtin-policies']
            for policy, _ in policies:
                command += ['--policy-file', policy.relative_to(root).as_posix()]
            command += ['--format', 'json']
            rc, timeout = invoke(command, root, probe_env, output, args.timeout)
            if timeout:
                raise GateError('analyzed-file probe timeout')
            data = json.loads((output / 'stdout.json').read_text())
            empty_oracle = {'expected': [], 'spurious': [], 'missing': [],
                            'oracle_sources': {}, 'oracle_disagreement': None}
            # Validate probe completion with findings removed, then read only
            # primary paths; never feed inventory rows to scoring.
            inventory = [f for r in data.get('runs', []) if r.get('policy_id') in PROBE_IDS
                         for f in r.get('findings', [])]
            status = dict(data, runs=[dict(r, findings=[]) for r in data.get('runs', [])])
            checked = score(status, empty_oracle, root=root, exit_code=rc,
                            analyzed_paths=(), required_policy_ids=PROBE_IDS)
            if not checked['complete']:
                raise GateError('analyzed-file probe did not complete; see coverage-probe logs')
            # Probe rows can have many facts per file. Membership needs only
            # their primary paths; run completion and omission checks certify
            # both inventories.
            paths = sorted({relative_path(f['primary']['path'], root) for f in inventory})
            evidence = {'source': 'file_row_and_configuration_probes', 'analyzed_files': paths,
                        'report': str(output / 'stdout.json'), 'cache_file': str(cache_file)}
            temporary = cache_file.with_suffix('.tmp')
            temporary.write_text(json.dumps(evidence, indent=2) + '\n')
            temporary.replace(cache_file)
            return set(paths), dict(evidence, cache_hit=False)
        finally:
            for policy, _ in policies:
                policy.unlink(missing_ok=True)


def execute(args, test_dir, query_path, stager):
    oracle = load_oracle(test_dir, query_path, stager, args.query,
                         getattr(args, 'scope_catalogs', None))
    prepared = stager.prepare(test_dir, args.codeql_root, args.state_dir / 'roots')
    runs_dir = args.state_dir / 'runs'
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix=re.sub(r'[^\w.-]', '-', args.query) + '-', dir=runs_dir))
    dest = run_dir / 'root'
    started = time.monotonic()
    try:
        shutil.copytree(prepared.root, dest)  # private copies: models/policies cannot mutate shared roots
        pdir = dest / '.bifrost/policies'
        pdir.mkdir(parents=True, exist_ok=True)
        policies = [args.policy, *args.extra_policy, *stager.extra_policy_files(prepared)]
        command = [str(args.binary), '--root', str(dest), '--no-builtin-policies']
        names = set()
        for policy in policies:
            if policy.name in names:
                raise GateError(f'duplicate policy basename: {policy.name}')
            names.add(policy.name)
            shutil.copy2(policy, pdir / policy.name)
            command += ['--policy-file', f'.bifrost/policies/{policy.name}']
        command += ['--format', 'json']
        if args.models:
            shutil.copytree(args.models, dest / '.bifrost/semantic-models', dirs_exist_ok=True)
        env = os.environ.copy()
        env.update(HOME=str(run_dir / 'home'), USERPROFILE=str(run_dir / 'home'),
                   BIFROST_CACHE_ROOT=str(run_dir / 'cache'),
                   BIFROST_SEMANTIC_PACK_CACHE_ROOT=str(run_dir / 'semantic-pack-cache'),
                   XDG_CACHE_HOME=str(run_dir / 'xdg'), BIFROST_OPEN_PACKS_DISABLE='1',
                   BIFROST_PARALLELISM='4', RAYON_NUM_THREADS='4')
        env.update(stager.run_env(run_dir, prepared))
        env['BIFROST_WORKSPACE_SEMANTIC_MODELS'] = 'on' if args.models else 'off'
        (run_dir / 'home').mkdir()
        rc, timed_out = invoke(command, dest, env, run_dir, args.timeout)
        parse_error = None
        try:
            data = json.loads((run_dir / 'stdout.json').read_text())
            if not isinstance(data, dict):
                raise GateError('report is not an object')
            analyzed = report_analyzed_paths(data, dest)
            coverage = {'source': 'report_scope'}
            if analyzed is None and oracle['expected'] and data.get('runs') and not timed_out:
                analyzed, coverage = probe_analyzed_paths(args, prepared, stager, dest, env, run_dir)
            result = score(data, oracle, root=dest, exit_code=rc,
                           anchors=args.anchors.get(args.query), true_positives=args.true_positives,
                           analyzed_paths=analyzed,
                           required_policy_ids=[r['policy_id'] for r in data.get('rules', [])])
            result['coverage'] = coverage
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            parse_error = str(exc)
            result = score({}, oracle, exit_code=rc)
        if timed_out or parse_error:
            result.update(verdict='ERROR', complete=False, **{'pass': False})
            result['errors'].append('timeout' if timed_out else f'report parse failure: {parse_error}')
        if 'recall_scope' in oracle:
            try:
                from .scoped import apply_scope
            except ImportError:
                from scoped import apply_scope
            test_name = test_dir.relative_to(args.codeql_root).as_posix()
            apply_scope(result, oracle, [a for a in args.scope_attributions if a['test_dir'] == test_name],
                        getattr(stager, 'ql_endpoints', ()))
            result['scope_catalogs'] = sorted(args.scope_catalogs)
        result.update(query=args.query, query_ids=[args.query], test_dir=str(test_dir.relative_to(args.codeql_root)),
                      test_dirs=[str(test_dir.relative_to(args.codeql_root))], policy=str(args.policy),
                      extra_policies=list(map(str, args.extra_policy)), label=args.label,
                      staged_artifacts=list(getattr(prepared, 'staged_artifacts', ())),
                      binary_sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                      codeql_commit=subprocess.check_output(['git', '-C', str(args.codeql_root), 'rev-parse', 'HEAD'], text=True).strip(),
                      exit_code=rc, wall_seconds=round(time.monotonic() - started, 3), run_dir=str(run_dir), command=command)
        write_results(run_dir, result)
        with (args.state_dir / 'results.tsv').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            csv.writer(stream, delimiter='\t', lineterminator='\n').writerow([
                datetime.now(timezone.utc).isoformat(), args.query, str(args.policy), args.label,
                result['verdict'], len(result['tp']), len(result['fp']), len(result['fn']),
                result['completion_type'], result['wall_seconds'], str(run_dir)] +
                ([result['full_suite_verdict']] if 'full_suite_verdict' in result else []))
        return result
    finally:
        if not args.keep:
            for base in (run_dir, run_dir / 'coverage-probe'):
                for name in ('root', 'cache', 'xdg', 'semantic-pack-cache', 'home'):
                    shutil.rmtree(base / name, ignore_errors=True)
