#!/usr/bin/env python3
"""Close an actually approved PHYS29 candidate and verify one local archive restore.

Metadata/file operations only. No scientific program or historical module is run.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib, json, stat, zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
TASK='REI-PHYS29-20261011'
TOP='REI_PHYS29_SMALL_WIDTH_SECOND_ORDER_DECOMPOSITION_20261011'
def read(p): return json.loads(p.read_bytes())
def sha(b): return hashlib.sha256(b).hexdigest()
def record(p,base=ROOT):
    b=p.read_bytes(); return {'path':p.relative_to(base).as_posix(),'bytes':len(b),'sha256':sha(b)}
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def utc(): return datetime.now(timezone.utc).isoformat()

review_path=ROOT/'independent/DECISION_REVIEW.json'
review=read(review_path)
decision=review.get('decision',review.get('verdict'))
assert decision=='PROMOTE_SCOPED',decision
freeze=read(ROOT/'evidence/CANDIDATE_FROZEN.json')
assert len(freeze['files'])==freeze['file_count']
for row in freeze['files']: assert record(ROOT/row['path'])==row,row['path']
summary=read(ROOT/'report/PHYS29_RESULTS_SUMMARY.json')
assert summary['first_summary']['all_pass']
assert summary['first_summary']['passed']==summary['first_summary']['total_checks']
assert summary['replay']['byte_equal'] and summary['replay']['parsed_json_equal']
assert summary['total_execution']['new_main']==2
assert summary['total_execution']['joint_k_kprime_ksecond_evaluations']==16
assert summary['total_execution']['new_physical_roots']==0
closed=utc()
closeout={
 'task':TASK,'status':'RESEARCH_CLOSED_PROMOTE_SCOPED','closed_utc':closed,
 'decision':decision,'physical_admission':'HOLD','authority':record(review_path),
 'decision_note':record(ROOT/'independent/DECISION_REVIEW_KO.md'),
 'candidate_freeze':record(ROOT/'evidence/CANDIDATE_FROZEN.json'),
 'all_frozen_candidate_payloads_preserved':len(freeze['files']),
 'first_summary':summary['first_summary'],'replay':summary['replay'],
 'total_execution':summary['total_execution'],'first_failures':summary['first_failures'],
 'protected':summary['protected'],'next':summary['next'],
 'publication':'Actual archive/Git receipt and later delivery ACK remain separate followups; not preclaimed here.',
 'remote_full_zip_restore_claim':False}
write(ROOT/'state/CLOSEOUT.json',closeout)
(ROOT/'state/RESEARCH_STATE.md').write_text(f'''# PHYS29 연구 상태

**RESEARCH_CLOSED_PROMOTE_SCOPED**. 생성·설계에 참여하지 않은 distinct NONBLIND 최종 판정은 `independent/DECISION_REVIEW.json`에 있다.

고정 실제 광자 분산에서의 한쪽 C2 문턱 전개, 이차계수의 항별 분해, 저장된 수치근의 계수 평가와 PHYS27 한 폭 진단을 완료했다. 정확근 존재·커널 부호 조건의 상속 지위와 저장근 오차의 미인증 상태를 유지한다. 이차 나머지의 정량 상계나 유효 폭 구간은 인증하지 않았다.

첫 main1회와 새 경로 replay1회만 실행했다. 전체 main2회, joint(k,k′,k″)16회, k16개·k′16개·k″16개 출력이다. 새 물리 root와 old PHYS19–28 main/suite/root, quadrature, finite difference, 폭 sweep, 부호 certificate campaign, native, gas IVP 모두0이다. 재현의 독립 물리 credit0.

Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; production source/default/runtime 변경0.

원 후보 {len(freeze['files'])}개 payload를 보존했다. 다음 PHYS30은 PROPOSED / NOT_RUN이다. 연구 종료 UTC {closed}. 실제 ZIP·Git 게시와 전달 결과는 분리된 PHYS29_PUBLICATION_RECEIPT.json 및 후속 ACK를 따른다.
''')
payloads=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc']
manifest={'task':TASK,'algorithm':'SHA-256','file_count':len(payloads),
 'files':[dict(record(p),mode=format(stat.S_IMODE(p.stat().st_mode),'04o')) for p in payloads],
 'decision_authority':'independent/DECISION_REVIEW.json','manifest_self_excluded':True,'detached_publication_receipt_excluded':True}
write(ROOT/'MANIFEST.json',manifest)
archive=BASE/(TOP+'.zip'); assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(payloads+[ROOT/'MANIFEST.json']):
        info=zipfile.ZipInfo(TOP+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(stat.S_IFREG|stat.S_IMODE(p.stat().st_mode))<<16
        z.writestr(info,p.read_bytes())
fresh=BASE/'phys29_final_archive_verify_only_20261011'; assert not fresh.exists(); fresh.mkdir()
with zipfile.ZipFile(archive) as z:
    names=z.namelist(); expected={TOP+'/'+p.relative_to(ROOT).as_posix() for p in payloads+[ROOT/'MANIFEST.json']}
    assert len(names)==len(set(names))==len(payloads)+1 and set(names)==expected
    for info in z.infolist():
        name=info.filename; path=PurePosixPath(name); mode=info.external_attr>>16
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in name and path.parts[0]==TOP
        assert stat.S_ISREG(mode)
        dest=fresh/str(path); dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f: f.write(z.read(info))
        dest.chmod(stat.S_IMODE(mode))
restored=fresh/TOP
assert (restored/'MANIFEST.json').read_bytes()==(ROOT/'MANIFEST.json').read_bytes()
verified=[]
for row in manifest['files']:
    path=restored/row['path']; b=path.read_bytes()
    assert len(b)==row['bytes'] and sha(b)==row['sha256'] and b==(ROOT/row['path']).read_bytes()
    assert path.is_file() and not path.is_symlink() and format(stat.S_IMODE(path.stat().st_mode),'04o')==row['mode']
    verified.append(row['path'])
assert len([p for p in restored.rglob('*') if p.is_file()])==len(payloads)+1
for row in freeze['files']: assert record(ROOT/row['path'])==row
receipt={'task':TASK,'status':'FINAL_PACKAGE_VERIFY_ONLY_PASS','utc':utc(),
 'archive':record(archive,BASE),'manifest':record(ROOT/'MANIFEST.json'),
 'zip_entries':len(payloads)+1,'payloads_verified':len(verified),'fresh_restore_root':str(restored),
 'exact_entry_set':True,'all_regular_files':True,'all_payload_sha256_size_mode_and_source_byte_equality':True,
 'manifest_byte_equal':True,'all_candidate_payloads_unchanged':len(freeze['files']),
 'candidate_freeze':record(ROOT/'evidence/CANDIDATE_FROZEN.json'),'decision':decision,'review':record(review_path),
 'science_main_invocations':0,'old_main_or_suite_invocations':0,'new_program_replay_in_this_action':0,
 'kernel_derivative_evaluations':0,'remote_restore':False,'verified_paths':verified}
out=BASE/'phys29_finalization'; out.mkdir(exist_ok=True); write(out/'FINAL_PACKAGE_RECEIPT.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_paths'},ensure_ascii=False))
