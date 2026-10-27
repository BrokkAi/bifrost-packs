"""Language-independent recall scope from CodeQL's printed provenance graph."""
import re
from enum import Enum
from pathlib import Path

try:
    from .core import GateError
except ImportError:
    from core import GateError


class Attribution(str, Enum):
    FRAMEWORK_ENDPOINT_ABSENT = 'framework-endpoint-absent'
    FRAMEWORK_SUMMARY_STEP = 'framework-summary-step'
    SKIPPED_STDLIB_SUMMARY = 'skipped-stdlib-summary'
    QL_ONLY_LOGIC = 'ql-only-logic'


def validate_attributions(entries):
    if not isinstance(entries, list):
        raise GateError('scope attributions must be a JSON list')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise GateError('scope attribution must be an object')
        try:
            Attribution(entry.get('attribution'))
        except (ValueError, TypeError) as exc:
            raise GateError(f"invalid scope attribution: {entry.get('attribution')}") from exc
        if (not isinstance(entry.get('line'), int) or isinstance(entry['line'], bool)
                or entry['line'] < 0 or not isinstance(entry.get('path'), str)
                or not entry['path'] or not isinstance(entry.get('test_dir'), str)
                or not entry['test_dir'] or not isinstance(entry.get('justification'), str)
                or not entry['justification'].strip()):
            raise GateError('scope attribution requires test_dir, path, line and justification')
        identity = (entry['test_dir'], entry['path'], entry['line'])
        if identity in seen:
            raise GateError(f'duplicate scope attribution: {identity}')
        seen.add(identity)
        if entry['attribution'] == Attribution.FRAMEWORK_ENDPOINT_ABSENT:
            if not isinstance(entry.get('endpoint'), str) or not entry['endpoint'].strip():
                raise GateError('framework-endpoint-absent requires a named printed endpoint model')
    return entries


def expected_scope(path, contains):
    """Map alert sites to every printed source/sink path, before site collapse.

    A path node is (location, label), rather than location alone: CodeQL can
    print different access paths at the same expression. Summary provenance
    never supplies endpoint provenance.
    """
    sections = {}
    section = 'select'
    for line in Path(path).read_text(errors='replace').splitlines():
        text = line.strip()
        if not text:
            continue
        if not text.startswith('|'):
            section = text.lstrip('#').strip().lower()
            sections.setdefault(section, [])
        else:
            sections.setdefault(section, []).append([c.strip() for c in text[1:-1].split('|')])
    if 'models' not in sections:
        raise GateError(f'scoped recall requires a models section: {Path(path).name}')
    models = {}
    for cells in sections['models']:
        if len(cells) != 2 or not cells[0].isdigit() or cells[0] in models:
            raise GateError('invalid or duplicate numbered model row')
        models[cells[0]] = cells[1]
    edges, forward, backward = [], {}, {}
    node_provenance = {}
    for cells in sections.get('nodes', []):
        if len(cells) == 4 and cells[2] == 'provenance':
            node_provenance.setdefault(tuple(cells[:2]), []).append(cells[3])
    for cells in sections.get('edges', []):
        if len(cells) != 6:
            raise GateError('scoped recall requires printed path edges with node labels')
        start, end = tuple(cells[:2]), tuple(cells[2:4])
        forward.setdefault(start, set()).add(end)
        backward.setdefault(end, set()).add(start)
        edges.append((start, end, cells[5] if cells[4] == 'provenance' else ''))
    def reachable(start, graph):
        seen, pending = set(), [start]
        while pending:
            node = pending.pop()
            if node not in seen:
                seen.add(node)
                pending.extend(graph.get(node, ()))
        return seen
    def endpoint_models(provenances, role):
        ids = set()
        for provenance in provenances:
            ids.update(re.findall(r'(?<![\w:])' + role + r':MaD:(\d+)\b', provenance))
        if ids - models.keys():
            raise GateError('endpoint provenance references an absent model row')
        return sorted(models[i] for i in ids)
    def universal_endpoint_models(node, alternatives, role):
        # Node evidence applies to every route. Edge evidence must name the
        # same model on every first/last edge; a union would let an attribution
        # for one branch excuse another branch that never uses that endpoint.
        common = set(endpoint_models(node_provenance.get(node, ()), role))
        if alternatives:
            common.update(set.intersection(*(set(endpoint_models([p], role))
                                             for p in alternatives)))
        return common
    result = {}
    for cells in sections.get('select', []):
        location = re.fullmatch(r'(.*):(\d+):\d+:\d+:\d+', cells[0])
        if not location:
            raise GateError('invalid scoped select location')
        anchor = f'{location[1]}:{location[2]}'
        source_models, sink_models = [], []
        universal_source, universal_sink = set(), set()
        source_known = sink_known = False
        if len(cells) >= 6:
            source, sink = tuple(cells[2:4]), tuple(cells[4:6])
            after_source, before_sink = reachable(source, forward), reachable(sink, backward)
            src = list(node_provenance.get(source, ()))
            dst = list(node_provenance.get(sink, ()))
            source_edges, sink_edges = [], []
            for start, end, provenance in edges:
                if start == source and end in before_sink:
                    source_edges.append(provenance)
                    src.append(provenance)
                if end == sink and start in after_source:
                    sink_edges.append(provenance)
                    dst.append(provenance)
            source_models = endpoint_models(src, '(?:Src|Source)')
            sink_models = endpoint_models(dst, 'Sink')
            # Every alternative first/last edge must prove its endpoint unless
            # that endpoint's node itself proves it. Missing provenance on one
            # alternative cannot be hidden by MaD on a different path.
            source_known = bool(endpoint_models(node_provenance.get(source, ()), '(?:Src|Source)')) or (
                bool(source_edges) and all(endpoint_models([p], '(?:Src|Source)') for p in source_edges))
            sink_known = bool(endpoint_models(node_provenance.get(sink, ()), 'Sink')) or (
                bool(sink_edges) and all(endpoint_models([p], 'Sink') for p in sink_edges))
            universal_source = universal_endpoint_models(source, source_edges, '(?:Src|Source)')
            universal_sink = universal_endpoint_models(sink, sink_edges, 'Sink')
        source_present = any(contains(m) for m in source_models)
        sink_present = any(contains(m) for m in sink_models)
        # Only a wholly absent endpoint can explain scope exclusion. If an
        # endpoint has both standard-library and framework models, its modeled
        # standard-library alternative keeps the obligation in scope.
        absent = sorted((set() if source_present else universal_source)
                        | (set() if sink_present else universal_sink))
        included = not source_known or not sink_known or (source_present and sink_present)
        result.setdefault(anchor, []).append(dict(included=included, source_models=source_models,
                                                 sink_models=sink_models, absent_models=absent))
    return result


def apply_scope(result, oracle, attributions):
    """Retain the complete full-suite score and defer only reviewed endpoint misses."""
    validate_attributions(attributions)
    result['full_suite_verdict'] = result['verdict']
    result['full_suite_pass'] = result['pass']
    result['scope_attributions'] = attributions
    result['recall_scope'] = oracle['recall_scope']
    by_site = {f"{a['path']}:{a['line']}": a for a in attributions}
    deferred, blocked, errors = [], [], []
    for absent in result['fn']:
        paths = oracle['recall_scope'].get(absent, [])
        if not paths or any(p['included'] for p in paths):
            blocked.append(absent)
            continue
        attribution = by_site.get(absent)
        if attribution is None:
            errors.append(f'out-of-subset miss requires attribution: {absent}')
            blocked.append(absent)
        elif attribution['attribution'] != Attribution.FRAMEWORK_ENDPOINT_ABSENT:
            blocked.append(absent)
        elif not all(attribution['endpoint'] in p['absent_models'] for p in paths):
            errors.append(f'attributed endpoint does not explain every path at {absent}')
            blocked.append(absent)
        else:
            deferred.append(absent)
    result['deferred_misses'] = deferred
    result['scoped_misses'] = blocked
    result['errors'].extend(errors)
    result['pass'] = result['complete'] and not (blocked or result['fp'] or result['errors'])
    result['verdict'] = ('SCOPED-EXACT' if result['pass'] else 'ERROR' if result['errors']
                         else 'SCOPED-FAIL')
