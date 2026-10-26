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


def key(row):
    return row['path'], row['start']


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
        if section == 'testfailures' and stripped.strip('|').strip():
            failures.append(stripped)
        if section != 'select' or not stripped.startswith('|'):
            continue
        column = stripped.strip('|').split('|', 1)[0].strip()
        match = re.fullmatch(r'(.*):(\d+):(\d+):(\d+):(\d+)', column)
        if not match:
            raise GateError(f'invalid select location in {path}: {column}')
        rows.append({'path': relative_path(match[1]), 'start': int(match[2]),
                     'end': int(match[4]), 'column': int(match[3]),
                     'end_column': int(match[5])})
    return unique(rows), failures


def qlref_query(path):
    text = path.read_text().strip()
    for line in text.splitlines():
        if line.strip().startswith('query:'):
            return line.split(':', 1)[1].strip()
    return text


def load_oracle(test_dir, query_path, stager):
    refs = [p for p in sorted(test_dir.glob('*.qlref'))
            if qlref_query(p) == query_path or qlref_query(p).endswith('/' + query_path)]
    if not refs:
        raise GateError(f'no .qlref for {query_path} in {test_dir}')
    selected, failures = [], []
    for ref in refs:
        expected_file = ref.with_suffix('.expected')
        if not expected_file.is_file():
            raise GateError(f'missing expected file: {expected_file}')
        rows, unreliable = parse_expected(expected_file)
        selected.extend(rows)
        failures.extend(unreliable)
    inline = stager.inline_oracle(test_dir) if hasattr(stager, 'inline_oracle') else {}
    spurious, missing = unique(inline.get('spurious', [])), unique(inline.get('missing', []))
    overrides = {key(r) for r in spurious + missing}
    tags = unique(inline.get('inline_alert', []) + inline.get('inline_taint', []))
    selected, tags = unique(selected), unique(tags)
    sources = {'select': selected, **inline}
    disagreement = None
    if tags:
        a, b = {key(r) for r in selected}, {key(r) for r in tags}
        disagreement = {'select_only': [f'{p}:{n}' for p, n in sorted(a - b)],
                        'inline_only': [f'{p}:{n}' for p, n in sorted(b - a)]}
    return {'expected': [r for r in unique(selected + tags) if key(r) not in overrides],
            'spurious': spurious, 'missing': missing, 'oracle_sources': sources,
            'oracle_disagreement': disagreement, 'testFailures': failures}


def report_findings(data, root=None):
    findings = []
    for run in data.get('runs', []):
        for finding in run.get('findings', []):
            primary = finding['primary']
            region = primary['region']
            start, end = region['start_line'], region['end_line']
            if not isinstance(start, int) or not isinstance(end, int) or not 0 < start <= end:
                raise GateError('invalid finding region')
            findings.append({'path': relative_path(primary['path'], root),
                             'start': start, 'end': end,
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


def score(data, oracle, *, root=None, exit_code=0, anchors=None, true_positives=(),
          analyzed_paths=(), required_policy_ids=()):
    runs = data.get('runs') or []
    errors = []
    if not runs:
        errors.append('missing runs')
    if any(r.get('completion', {}).get('type') == 'failed' for r in runs):
        errors.append('failed policy run')
    if exit_code not in (0, 1):  # CLI 1 is the normal findings exit status.
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
    incomplete_impacts = {'run_incomplete', 'run_unsupported', 'report_incomplete'}
    def bad_diagnostic(d):
        return (d.get('impact') in incomplete_impacts or
                d.get('impact') is None and any(s in str(d.get('code', '')).lower() for s in
                    ('empty_selection', 'unsupported', 'incomplete', 'unresolved', 'partial')))
    incomplete_diagnostics = [d for d in diagnostics if bad_diagnostic(d)]
    truncated = any(d.get('diagnostics_truncated') or d.get('obligations_truncated') or
                    d.get('work', {}).get('omitted_findings_lower_bound', 0) for d in [data] + runs)
    execution = data.get('execution', {})
    interrupted = bool(execution.get('termination') or execution.get('pending_policy_ids'))
    # A count smaller than the staged source inventory cannot certify analysis.
    source_paths = set(analyzed_paths) or {e['path'] for e in expected}
    coverage_unknown = any(r.get('work', {}).get('scanned_files', 0) < len(source_paths) for r in runs)
    complete = (bool(runs) and all(r.get('completion', {}).get('type') == 'complete' for r in runs)
                and not incomplete_diagnostics and not truncated and not interrupted
                and not coverage_unknown and not errors
                and all(f['completeness'].get('type', 'complete') == 'complete' for f in findings))
    def abstained(e):
        if coverage_unknown or truncated or interrupted or errors or not runs:
            return True
        if any(f['path'] == e['path'] and f['completeness'].get('type', 'complete') != 'complete'
               for f in findings):
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
        f"{result['query']}: {'PASS' if result['pass'] else result['verdict']}\n\n" + '\n'.join(rows) +
        f"\n\nComplete: {result['complete']}. Errors: {result['errors']}\n"
        f"\nOracle sources: {', '.join(f'{k}={len(v)}' for k, v in result['oracle_sources'].items())}.\n"
        f"Disagreement: {json.dumps(result['oracle_disagreement'])}\n"
        f"\nBinary SHA256: `{result['binary_sha256']}`\n"
        f"CodeQL commit: `{result['codeql_commit']}`\n")


def execute(args, test_dir, query_path, stager):
    oracle = load_oracle(test_dir, query_path, stager)
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
        timed_out = False
        with (run_dir / 'stdout.json').open('w') as stdout, (run_dir / 'stderr.txt').open('w') as stderr:
            process = subprocess.Popen(['nice', '-n', '10', *command], cwd=dest, env=env,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        rc = process.returncode
        (run_dir / 'exit-code.txt').write_text(str(rc) + '\n')
        parse_error = None
        try:
            data = json.loads((run_dir / 'stdout.json').read_text())
            if not isinstance(data, dict):
                raise GateError('report is not an object')
            result = score(data, oracle, root=dest, exit_code=rc,
                           anchors=args.anchors.get(args.query), true_positives=args.true_positives,
                           analyzed_paths=prepared.source_paths,
                           required_policy_ids=[r['policy_id'] for r in data.get('rules', [])])
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            parse_error = str(exc)
            result = score({}, oracle, exit_code=rc)
        if timed_out or parse_error:
            result.update(verdict='ERROR', complete=False, **{'pass': False})
            result['errors'].append('timeout' if timed_out else f'report parse failure: {parse_error}')
        result.update(query=args.query, query_ids=[args.query], test_dir=str(test_dir.relative_to(args.codeql_root)),
                      test_dirs=[str(test_dir.relative_to(args.codeql_root))], policy=str(args.policy),
                      extra_policies=list(map(str, args.extra_policy)), label=args.label,
                      binary_sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                      codeql_commit=subprocess.check_output(['git', '-C', str(args.codeql_root), 'rev-parse', 'HEAD'], text=True).strip(),
                      exit_code=rc, wall_seconds=round(time.monotonic() - started, 3), run_dir=str(run_dir), command=command)
        write_results(run_dir, result)
        with (args.state_dir / 'results.tsv').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            csv.writer(stream, delimiter='\t', lineterminator='\n').writerow([
                datetime.now(timezone.utc).isoformat(), args.query, str(args.policy), args.label,
                result['verdict'], len(result['tp']), len(result['fp']), len(result['fn']),
                result['completion_type'], result['wall_seconds'], str(run_dir)])
        return result
    finally:
        if not args.keep:
            for name in ('root', 'cache', 'xdg', 'semantic-pack-cache', 'home'):
                shutil.rmtree(run_dir / name, ignore_errors=True)
