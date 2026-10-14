#!/usr/bin/env python3
"""Preserve119original files; add a narrowly corrected reviewed report, science0."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,difflib
ROOT=Path(__file__).resolve().parents[1]
def rec(rel):
    b=(ROOT/rel).read_bytes();return {'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,text):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_text(text)
freeze=json.loads((ROOT/'evidence/CANDIDATE_FROZEN.json').read_bytes())
for row in freeze['files']:assert rec(row['path'])==row
src='report/PHYS29_REPORT_KO.md';dest='report/reviewed/PHYS29_REPORT_KO.md'
original=(ROOT/src).read_text()
old='값에 맞는 단위 척도와 두 값의 크기 중 최대값으로 나눈 오차를 비교한다. 무차원·모멘트·근 계수 비교에는 해당 프로토콜의 `max(1, abs(a), abs(b))` 척도를 쓴다.'
new='차원이 있는 kernel·응답·편미분의 비교에서는 차이의 절댓값을 명시적으로 공급한 **고정 척도 S_j 또는 sigma 척도**로 나눈다. 이 경우 두 값의 크기와 최대값을 취하지 않는다. `scale=None`인 무차원·모멘트·근 계수 비교에만 `max(1, abs(a), abs(b))`를 쓴다. 상수 일치 확인은 별도로 공급한 `max(abs(a), abs(b))` 척도를 사용한다.'
assert original.count(old)==1
corrected=original.replace(old,new)
# The full reviewed report is one directory deeper; change links only.
def link(match):
    target=match.group(1)
    if target.startswith(('http://','https://','#')):return match.group(0)
    return ']('+('../'+target)+')'
corrected=re.sub(r'\]\(([^)]+)\)',link,corrected)
notice='> **검토 반영본.** 최종 검토에서 확인한 §7 오차 척도의 설명을 실제 동결 코드·프로토콜에 맞게 정정했다. 계산값·코드·입력·허용오차·238개 판정은 그대로다. [동결 원문](../PHYS29_REPORT_KO.md)과 [정정 기록](../../evidence/REPORT_CORRECTION.json)을 보존하며, 새 과학 실행은 없다.\n\n'
heading,rest=corrected.split('\n',1)
corrected=heading+'\n\n'+notice+rest.lstrip('\n')
write(dest,corrected)
patch=''.join(difflib.unified_diff(original.splitlines(True),corrected.splitlines(True),fromfile=src,tofile=dest))
write('evidence/REPORT_CORRECTION.patch',patch)
correction={'task':'REI-PHYS29-20261011','recorded_utc':datetime.now(timezone.utc).isoformat(),
 'status':'REVIEW_FINDING_ADDRESSED_BY_ADDITIVE_REVIEWED_COPY','finding_by':'/root/phys29_decision','edited_by':'/root',
 'scope':'One reporting sentence concerning denominator selection; explanatory header and depth-adjusted relative links only. No scientific result or gate criterion changed.',
 'actual_source_basis':'contributions/numerics/second_order_width.py close(): scale=max(ONE,abs(actual),abs(expected)) if scale is None else scale; error=abs(actual-expected)/scale',
 'old_wording':old,'corrected_wording':new,
 'original':rec(src),'reviewed':rec(dest),'diff':rec('evidence/REPORT_CORRECTION.patch'),
 'original_candidate_freeze':rec('evidence/CANDIDATE_FROZEN.json'),'all119original_payloads_unchanged':True,
 'scientific_main':0,'kernel_derivative_evaluations':0,'root_searches':0,'scientific_input_code_protocol_tolerance_raw_changes':0,
 'final_gate':'Distinct reviewer must consume the additive correction before decision. No final decision preclaimed.'}
write('evidence/REPORT_CORRECTION.json',json.dumps(correction,ensure_ascii=False,indent=2)+'\n')
write('START_HERE_KO.md','''# PHYS29 최종 보고서를 읽는 경로

사용자에게 전달하는 완전한 보고서는 [검토 반영 PHYS29_REPORT_KO.md](report/reviewed/PHYS29_REPORT_KO.md)다. 최초 동결 보고서의 오차 척도 설명 한 문장을 실제 코드와 사전 프로토콜에 맞게 바로잡았다. 원119개 후보 파일, 모든 수치·과학 코드·입력·허용오차·raw를 보존했다. 새 과학 실행은 없다.

[정정 기록](evidence/REPORT_CORRECTION.json)과 [원문 대비 diff](evidence/REPORT_CORRECTION.patch)가 수정 범위를 식별한다. 최종 판정은 [DECISION_REVIEW_KO.md](independent/DECISION_REVIEW_KO.md), 종료 상태는 [CLOSEOUT.json](state/CLOSEOUT.json)이다. 그 외 구성 설명은 [README_KO.md](README_KO.md)를 따른다. README가 가리키는 report/PHYS29_REPORT_KO.md는 보존한 최초 후보 원문이다.

Physical HOLD와 모든 보호 상태는 유지한다. PHYS30은 제안만 남겼고 실행하지 않았다.
''')
additions=['owner_tools/make_reviewed_report.py',dest,'evidence/REPORT_CORRECTION.patch','evidence/REPORT_CORRECTION.json','START_HERE_KO.md']
obj={'task':'REI-PHYS29-20261011','status':'ADDITIVE_REPORT_CORRECTION_FROZEN_FOR_FINAL_REVIEW',
 'frozen_utc':datetime.now(timezone.utc).isoformat(),'base_candidate':rec('evidence/CANDIDATE_FROZEN.json'),
 'base_file_count':119,'base_payloads_unchanged':True,'file_count':len(additions),'files':[rec(x) for x in additions],
 'canonical_user_report':dest,'scientific_executions':0,'scientific_code_protocol_raw_changes':0,
 'claim':'This addendum preserves the base freeze and records a report-only reviewer correction; final reviewer has not decided yet.'}
write('evidence/CANDIDATE_ADDENDUM_FROZEN.json',json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
for row in freeze['files']:assert rec(row['path'])==row
print(json.dumps({'reviewed':rec(dest),'addendum':rec('evidence/CANDIDATE_ADDENDUM_FROZEN.json'),'additional_bound_files':len(additions),'scientific_executions':0},ensure_ascii=False))
