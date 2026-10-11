#!/usr/bin/env python3
"""Final identity/readback metadata only; no scientific module execution."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re
import stat

ROOT = Path('/workspace/scratch/603081e41728/phys30')
OUT = ROOT / 'independent/CANDIDATE_PRESERVATION_FINAL.json'


def identity(path, name=None):
    data = path.read_bytes()
    return dict(path=name or path.relative_to(ROOT).as_posix(), bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                mode=format(stat.S_IMODE(path.stat().st_mode), '04o'))


def main():
    if OUT.exists():
        raise FileExistsError('Preserve the original final preservation result')
    freeze_path = ROOT / 'evidence/CANDIDATE_FROZEN.json'
    freeze = json.loads(freeze_path.read_bytes())
    freeze_identity = identity(freeze_path)
    rows = []
    for expected in freeze['files']:
        path = ROOT / expected['path']
        actual = identity(path)
        matches = all(actual[key] == expected[key] for key in ('path','bytes','sha256','mode')) and not path.is_symlink()
        rows.append(dict(actual=actual, matches_frozen=matches))
    review_path = ROOT / 'independent/DECISION_REVIEW.json'
    review = json.loads(review_path.read_bytes())
    md_path = ROOT / 'independent/DECISION_REVIEW_KO.md'
    md = md_path.read_text()
    ledger = json.loads((ROOT / 'evidence/CLAIM_LEDGER.json').read_bytes())
    expected_claims = [row['id'] for row in ledger['theory_claims'] + ledger['numeric_and_implementation_claims']]
    observed_claims = [row['id'] for row in review['claim_decisions']]
    actual_kind_counts = dict(Counter(row['kind'] for row in review['claim_decisions']))
    future_receipts = {'CANDIDATE_PRESERVATION_FINAL.json','REVIEW_COMPLETION_RECEIPT.json'}
    local_links = []
    for target in re.findall(r'\]\(([^)]+)\)', md):
        if target.startswith(('http://','https://')):
            continue
        local_links.append(dict(target=target, present=(md_path.parent / target).exists(),
                                known_final_receipt=target in future_receipts))
    audit = json.loads((ROOT / 'independent/REVIEW_METADATA_AUDIT.json').read_bytes())
    gates = dict(
        freeze_GO_identity=freeze_identity['bytes'] == 25416 and freeze_identity['sha256'] == '5dd90996f30de50a2e9901345102a79b934cfb2384e77d19e9345fa2a001e05d' and freeze_identity['mode'] == '0644',
        all_123_candidate_files_preserved=len(rows) == 123 and all(row['matches_frozen'] for row in rows),
        primary_review_identity=identity(review_path)['sha256'] == 'd3290db160004687d2a79ce71453b83549112f2f491b2f2da0c7768ace06cdd0',
        primary_KO_identity=identity(md_path)['sha256'] == 'a759b3434bc6d7d83344e9e5e47737382990e094a5d474fef4afcd0850c513d6',
        all_24_claims_match_frozen_ledger=observed_claims == expected_claims and len(set(observed_claims)) == 24,
        kind_counts_match=actual_kind_counts == dict(derived_theory=19,proposal=1,numerical=3,implementation=1),
        scoped_decision=review['decision'] == 'PROMOTE_SCOPED' and review['fatal_issue_count'] == 0 and review['fatal_issues'] == [],
        own_science_counts_zero=all(value == 0 for value in review['reviewer_science_counts'].values()),
        all_claim_reasons_and_limits_present_in_KO=all(row['reason_ko'] in md and row['scope_limit_ko'] in md for row in review['claim_decisions']),
        local_links_present_or_final_receipt=all(row['present'] or row['known_final_receipt'] for row in local_links),
        no_unfilled_report_template_tokens=all(token not in md for token in ['@THEORY_TABLE@','@OTHER_TABLE@','@FAILURE_TABLE@','@NUMBER_TABLE@','@FIRST_TIME@','@REPLAY_TIME@']),
        prior_29_metadata_gates_pass=audit['status'] == 'METADATA_AUDIT_PASS' and len(audit['gates']) == 29 and all(audit['gates'].values()),
        next_proposal_not_run=review['next_step']['decision'] == 'RETAIN_PROPOSED_NOT_RUN' and review['next_step']['higher_order_answer_or_execution'] == 0,
        own_first_writer_failure_preserved=json.loads((ROOT/'independent/REVIEW_WRITE_EXECUTION.json').read_bytes())['actual_exit_code'] == 1,
        own_corrected_writer_actual_success=json.loads((ROOT/'independent/REVIEW_WRITE_FIXED_EXECUTION.json').read_bytes())['actual_exit_code'] == 0)
    result = dict(task='REI-PHYS30-20261011',reviewer='/root/phys30_decision',
        observed_utc=datetime.now(timezone.utc).isoformat(),
        status='CANDIDATE_PRESERVATION_PASS' if all(gates.values()) else 'PRESERVATION_FAILURE_PRESERVED',
        phase='AFTER_FINAL_REVIEW_WRITTEN_AND_PERSONALLY_READ_BACK',
        candidate_freeze=freeze_identity, candidate_file_count=len(rows),
        candidate_mismatch_count=sum(not row['matches_frozen'] for row in rows),
        candidate_rows=rows, gates=gates, failed_gates=[key for key,value in gates.items() if not value],
        final_review_files=[identity(review_path),identity(md_path)],
        readback=dict(JSON='Full final JSON displayed and read; the truncated TC30-15/16/17 interval was explicitly redisplayed in full.',
                      Korean_note='Full192-line final note displayed and read with no truncation.',
                      primary_actual_read_manifest='independent/REVIEW_READ_MANIFEST.json',
                      source_and_raw_evidence_not_reevaluated=True),
        claim_kind_counts=actual_kind_counts, local_link_checks=local_links,
        science_counts=review['reviewer_science_counts'],
        independence='Distinct NONBLIND role, same host/model/history; independent physical evidence credit0.',
        scope='Final bytes/SHA256/mode, schema and text-copy checks only. No new physical or algebra execution, no candidate mutation, no wider validation design.')
    with OUT.open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps(dict(status=result['status'],candidate_files=len(rows),mismatch_count=result['candidate_mismatch_count'],
        failed_gates=result['failed_gates'],gate_count=len(gates),output=identity(OUT),
        decision=review['decision'],fatal_issue_count=review['fatal_issue_count'],science_counts=review['reviewer_science_counts']),ensure_ascii=False))
    return 0 if all(gates.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
