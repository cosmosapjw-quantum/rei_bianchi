#!/usr/bin/env python3
"""Structural only: audit the D0 execution *projection*, not physical acceptance.

Does not validate source science, canonically count 88 nodes, alter history or
admit a new physical result. Run with `python scripts/validate_igm_spine.py`.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'docs/roadmap/REI_IGM_EXECUTION_SPINE_V1.json'
ALLOWED = {
    'historical_scoped_complete', 'candidate_requires_fresh_source_check',
    'hold', 'blocked_minimum_step', 'pending', 'external_pending', 'optional',
}


def validate(payload: dict) -> dict:
    errors: list[str] = []
    if payload.get('schema') != 'REI_IGM_EXECUTION_SPINE_V1':
        errors.append('unrecognized projection schema')
    if payload.get('classification') != 'operational roadmap projection, NOT the canonical 88-node roster':
        errors.append('the 15-node spine must not be relabelled as the canonical 88-node DAG')
    authority = payload.get('authority', {})
    if authority.get('canonical_88_node_roster_located_in_this_snapshot') is not False:
        errors.append('false claim that the complete 88-node roster was inspected')
    progress = payload.get('reported_progress', {})
    for key, expected_total in (('central', 88), ('working', 88), ('physical_fast', 7)):
        entry = progress.get(key, {})
        count, total = entry.get('completed'), entry.get('total')
        if not isinstance(count, int) or not isinstance(total, int) or not (0 <= count <= total) or total != expected_total:
            errors.append(f'invalid reported progress {key}')
        if not str(entry.get('verification', '')).startswith(('reported_', 'scoped_')):
            errors.append(f'{key} appears promoted without explicit canonical evidence')
    if progress.get('canonical_delta_this_audit') != 0:
        errors.append('a process audit cannot promote a physical canonical node')
    if payload.get('milestone_ids_are_not_actual_github_pr_numbers') is not True:
        errors.append('D0 milestone slots cannot be equated with GitHub PR numbers')
    nodes = payload.get('nodes', [])
    ids = [n.get('id') for n in nodes]
    if len(ids) != len(set(ids)) or None in ids:
        errors.append('duplicate or missing milestone id')
    index = {n.get('id'): n for n in nodes}
    for n in nodes:
        if n.get('status') not in ALLOWED:
            errors.append(f"unknown/hypothetically promoted status: {n.get('id')}")
        if n.get('scope') != 'roadmap_projection':
            errors.append(f"milestone {n.get('id')} has incorrect scope")
        for dep in n.get('depends_on', []):
            if dep not in index:
                errors.append(f"missing dependency: {n.get('id')} -> {dep}")
            if dep == n.get('id'):
                errors.append(f"self dependency: {dep}")
    colours: dict[str, int] = {}
    def visit(key: str) -> None:
        if colours.get(key) == 1:
            errors.append(f'cycle at {key}')
            return
        if colours.get(key) == 2 or key not in index:
            return
        colours[key] = 1
        for dep in index[key].get('depends_on', []):
            visit(dep)
        colours[key] = 2
    for key in ids:
        if isinstance(key, str):
            visit(key)
    chain = payload.get('critical_path', [])
    if not chain or len(chain) != len(set(chain)) or any(key not in index for key in chain):
        errors.append('critical path incomplete or repeated')
    else:
        for before, after in zip(chain, chain[1:]):
            if before not in index[after].get('depends_on', []):
                errors.append(f'broken critical-path edge: {before} -> {after}')
    candidate = payload.get('next_candidate_id')
    if candidate not in index:
        errors.append('no evidence-scoped next central target')
    else:
        node = index[candidate]
        state = node.get('status')
        if state not in ('candidate_requires_fresh_source_check', 'blocked_minimum_step'):
            errors.append('next central target lacks truthful runnable/blocked status')
        prior = node.get('observed_blocker')
        if state == 'blocked_minimum_step':
            if not isinstance(prior, dict):
                errors.append('blocked central target lacks pinned original failure witness')
            else:
                tick, total = prior.get('accepted_tick'), prior.get('total_ticks')
                limit = prior.get('inherited_local_error_limit')
                observations = prior.get('observed_logT_full_half_cross_image_errors')
                if not (type(tick) is int and type(total) is int and 0 < tick < total):
                    errors.append('blocked target missing valid frozen tick range')
                if not (isinstance(limit, (int,float)) and limit > 0 and
                        isinstance(observations, list) and len(observations) >= 1 and
                        all(isinstance(q.get('value'), (int,float)) and q['value'] > limit
                            for q in observations if isinstance(q,dict)) and
                        all(isinstance(q,dict) for q in observations)):
                    errors.append('blocked target failure witness inconsistent with inherited strict limit')
                if (prior.get('full_first_interval_accepted') is not False or
                        not prior.get('frozen_run_commit') or
                        not prior.get('archived_original_sha256')):
                    errors.append('blocked target lacks source-authentic unaccepted-run identity')
        if state == 'candidate_requires_fresh_source_check' and prior and not node.get('resolution_evidence'):
            errors.append('unresolved historical blocker cannot be silently relabelled ready')
    if candidate not in chain:
        errors.append('next central target lies outside the D0 critical path')
    aux = payload.get('auxiliary_science', [])
    for lane in aux:
        if lane.get('canonical_delta') != 0:
            errors.append(f"auxiliary {lane.get('id')} falsely increments central count")
        if lane.get('feeds') not in index:
            errors.append(f"auxiliary {lane.get('id')} has no existing science recipient")
        if lane.get('status') not in ('scoped_source_conditional', 'scoped_statistical_only'):
            errors.append(f"auxiliary {lane.get('id')} has unsupported admission")
    if errors:
        raise ValueError('; '.join(dict.fromkeys(errors)))
    return {'schema': payload['schema'], 'milestones': len(nodes), 'auxiliary_lanes': len(aux), 'critical_path_edges': len(chain)-1, 'canonical_delta': 0}


def main() -> None:
    report = validate(json.loads(PATH.read_text(encoding='utf-8')))
    print('REI IGM execution spine STRUCTURE PASS ' + json.dumps(report, sort_keys=True))
    print('PHYSICAL SCIENCE VALIDATION / 88-NODE ROSTER: NOT_PERFORMED')


if __name__ == '__main__':
    main()
