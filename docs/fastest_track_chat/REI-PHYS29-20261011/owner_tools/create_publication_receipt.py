#!/usr/bin/env python3
"""Record observed post-gate Git and local archive evidence without hash cycles."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent
def rd(p):return json.loads(p.read_bytes())
def rec(p):
    b=p.read_bytes();return {'path':p.relative_to(BASE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
package=rd(BASE/'phys29_finalization/FINAL_PACKAGE_RECEIPT.json')
git=rd(BASE/'phys29_publication_transport/GIT_VERIFICATION.json')
review=rd(ROOT/'independent/DECISION_REVIEW.json')
decision=review.get('decision',review.get('verdict'))
assert decision=='PROMOTE_SCOPED'
assert package['status']=='FINAL_PACKAGE_VERIFY_ONLY_PASS'
assert git['status']=='ADDITIVE_DOCS_VERIFIED'
summary=rd(ROOT/'report/PHYS29_RESULTS_SUMMARY.json')
receipt={'task':'REI-PHYS29-20261011','status':'RESEARCH_AND_AUTHORIZED_ADDITIVE_DOCS_COMPLETE_DELIVERY_PENDING',
 'written_utc':datetime.now(timezone.utc).isoformat(),'decision':decision,
 'review':rec(ROOT/'independent/DECISION_REVIEW.json'),'review_note':rec(ROOT/'independent/DECISION_REVIEW_KO.md'),
 'candidate_freeze':rec(ROOT/'evidence/CANDIDATE_FROZEN.json'),'closeout':rec(ROOT/'state/CLOSEOUT.json'),
 'archive':package['archive'],'final_package_verification':package,
 'git':git,'publication_manifest':rd(BASE/'phys29_publication_transport/PUBLICATION_MANIFEST.json'),
 'first_summary':summary['first_summary'],'replay':summary['replay'],'total_execution':summary['total_execution'],
 'protected':summary['protected'],'next':summary['next'],
 'remote_full_zip_restore_claim':False,'local_archive_restore_scientific_invocations':0,
 'cycle_policy':'This receipt is detached from candidate,archive and Git tree. Delivery ACK is a subsequent record; this receipt will not be mutated after save.',
 'delivery':{'status':'PENDING_ACTUAL_ORDERED_SAVE_ACK','all_saved_claim':False,
  'ordered_files':['PHYS29_REPORT_KO.md','REI_PHYS29_SMALL_WIDTH_SECOND_ORDER_DECOMPOSITION_20261011.zip','DECISION_REVIEW_KO.md','PHYS30_NEXT_HANDOFF_KO.md','PHYS29_SECOND_ORDER_DECOMPOSITION.png','PHYS29_RESULTS_SUMMARY.json','PHYS29_PUBLICATION_RECEIPT.json']}}
out=BASE/'PHYS29_PUBLICATION_RECEIPT.json';assert not out.exists()
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rec(out),ensure_ascii=False))
