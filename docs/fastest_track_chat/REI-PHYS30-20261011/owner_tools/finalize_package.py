#!/usr/bin/env python3
"""Close the actual PHYS30 review and verify a single local archive restore."""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import hashlib,json,stat,zipfile
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent
TASK='REI-PHYS30-20261011';TOP='REI_PHYS30_SYMMETRIC_PROFILE_SECOND_ORDER_UNIVERSALITY_20261011'
def read(p):return json.loads(p.read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p,root=ROOT):
    b=p.read_bytes();return {'path':p.relative_to(root).as_posix(),'bytes':len(b),'sha256':sha(b)}
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def assert_row(row,root=ROOT):
    p=root/row['path'];r=rec(p,root)
    assert r['bytes']==row['bytes'] and r['sha256']==row['sha256'],row['path']
    if 'mode' in row:assert format(stat.S_IMODE(p.stat().st_mode),'04o')==row['mode']
    assert p.is_file() and not p.is_symlink()
review=read(ROOT/'independent/DECISION_REVIEW.json')
assert review['decision']=='PROMOTE_SCOPED' and review['fatal_issue_count']==0
freeze=read(ROOT/'evidence/CANDIDATE_FROZEN.json');assert freeze['file_count']==len(freeze['files'])
for row in freeze['files']:assert_row(row)
summary=read(ROOT/'report/PHYS30_RESULTS_SUMMARY.json')
assert summary['first_summary']['all_pass']
assert summary['first_summary']['passed']==summary['first_summary']['total_grouped_checks']
assert summary['replay']['byte_equal'] and summary['replay']['parsed_json_equal']
assert summary['total_execution']['new_main']==2
assert summary['total_execution']['new_physical_kernel_or_derivative_evaluations']==0
assert summary['total_execution']['new_physical_roots']==0
closed=datetime.now(timezone.utc).isoformat()
close={'task':TASK,'status':'RESEARCH_CLOSED_PROMOTE_SCOPED','closed_utc':closed,'decision':review['decision'],'fatal_issues':0,
 'authority':rec(ROOT/'independent/DECISION_REVIEW.json'),'decision_note':rec(ROOT/'independent/DECISION_REVIEW_KO.md'),
 'candidate_freeze':rec(ROOT/'evidence/CANDIDATE_FROZEN.json'),'all_candidate_payloads_preserved':len(freeze['files']),
 'first_summary':summary['first_summary'],'replay':summary['replay'],'total_execution':summary['total_execution'],
 'claim_scope':summary['claim_scope'],'protected':summary['protected'],'next':summary['next'],
 'publication':'Actual post-close archive/Git evidence and later delivery ACK are detached subsequent records; no success preclaim here.',
 'remote_full_zip_restore_claim':False}
write(ROOT/'state/CLOSEOUT.json',close)
state=f'''# PHYS30 연구 종료

RESEARCH_CLOSED_PROMOTE_SCOPED. 생성·검증 설계와 분리된 distinct NONBLIND 최종 판정은 independent/DECISION_REVIEW.json을 따른다. Fatal0.

고정 대칭 profile과 동일 중심 허용구간에서의 조건부 한쪽 C2 전개, c 불변성, d의 mu2 아핀 의존성을 유도하고 저장값 대수로 검증했다. 정확근 전제와 저장된 비영 A-level을 구별한다. 임의 유한폭의 동일근·전체 profile 순서·Taylor 나머지 상계·물리 허용은 승격하지 않았다.

실제 최초 cached-algebra main1회와 별도경로 replay1회, 합계2회다. 새 물리 kernel/derivative/root 및 old PHYS19–29 main/suite/import 모두0. 정확 profile moment와 A=1 quadratic toy는 원 raw의 별도 algebra counters를 따른다. 독립 물리 credit0.

Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime 변경0.

후보 payload {len(freeze['files'])}개를 보존했다. PHYS31은 PROPOSED / NOT_RUN. 종료UTC {closed}. 최종 ZIP·Git·전달은 실제 분리된 후속 영수증을 따른다.
'''
with (ROOT/'state/RESEARCH_STATE.md').open('x') as f:f.write(state)
payloads=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc']
assert all(not p.is_symlink() for p in payloads)
manifest={'task':TASK,'algorithm':'SHA-256','file_count':len(payloads),'files':[dict(rec(p),mode=format(stat.S_IMODE(p.stat().st_mode),'04o')) for p in payloads],'decision_authority':'independent/DECISION_REVIEW.json','self_excluded':True,'publication_receipt_detached':True}
write(ROOT/'MANIFEST.json',manifest)
archive=BASE/(TOP+'.zip');assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(payloads+[ROOT/'MANIFEST.json']):
        info=zipfile.ZipInfo(TOP+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(stat.S_IFREG|stat.S_IMODE(p.stat().st_mode))<<16
        z.writestr(info,p.read_bytes())
fresh=BASE/'phys30_final_archive_verify_only_20261011';assert not fresh.exists();fresh.mkdir()
with zipfile.ZipFile(archive) as z:
    expected={TOP+'/'+p.relative_to(ROOT).as_posix() for p in payloads+[ROOT/'MANIFEST.json']}
    names=z.namelist();assert len(names)==len(set(names))==len(expected) and set(names)==expected
    for i in z.infolist():
        p=PurePosixPath(i.filename);mode=i.external_attr>>16
        assert not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename and p.parts[0]==TOP and stat.S_ISREG(mode)
        dest=fresh/str(p);dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f:f.write(z.read(i))
        dest.chmod(stat.S_IMODE(mode))
restored=fresh/TOP
assert (restored/'MANIFEST.json').read_bytes()==(ROOT/'MANIFEST.json').read_bytes()
for row in manifest['files']:
    assert_row(row,restored);assert (restored/row['path']).read_bytes()==(ROOT/row['path']).read_bytes()
assert len([p for p in restored.rglob('*') if p.is_file()])==len(payloads)+1
for row in freeze['files']:assert_row(row)
receipt={'task':TASK,'status':'FINAL_PACKAGE_VERIFY_ONLY_PASS','utc':datetime.now(timezone.utc).isoformat(),'archive':rec(archive,BASE),'manifest':rec(ROOT/'MANIFEST.json'),'zip_entries':len(payloads)+1,'payloads_verified':len(payloads),'fresh_restore_root':str(restored),'exact_entry_set':True,'all_regular_files':True,'all_payload_sha256_size_mode_and_source_byte_equality':True,'manifest_byte_equal':True,'all_candidate_payloads_unchanged':len(freeze['files']),'candidate_freeze':rec(ROOT/'evidence/CANDIDATE_FROZEN.json'),'review':rec(ROOT/'independent/DECISION_REVIEW.json'),'science_main_invocations':0,'old_main_or_suite_invocations':0,'new_program_replay_in_this_action':0,'kernel_derivative_evaluations':0,'remote_restore':False,'verified_paths':[r['path'] for r in manifest['files']]}
write(BASE/'phys30_finalization/FINAL_PACKAGE_RECEIPT.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_paths'},ensure_ascii=False))
