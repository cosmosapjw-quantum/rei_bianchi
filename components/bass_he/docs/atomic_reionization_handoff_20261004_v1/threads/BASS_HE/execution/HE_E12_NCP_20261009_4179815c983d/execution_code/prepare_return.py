import pathlib,json,csv,hashlib,subprocess,sys
from execute import write
R=pathlib.Path(__file__).parent
val=json.loads((R/'FULL_VALIDATION.json').read_text())
measure={}
for tag in ['TESTS','BUILD']+['PILOT_'+m for m in ('OFF','KF','GM')]+['FULL_'+m for m in ('OFF','KF','GM')]:
 d=R/'logs'/tag;rec=json.loads((d/'EXIT.json').read_text());assert rec['exit']==0
 text=(d/'stderr').read_text();v={'elapsed_s':rec['elapsed_s'],'exit':rec['exit']}
 for name,key in [('User time (seconds)','user_cpu_s'),('System time (seconds)','sys_cpu_s'),('Maximum resident set size (kbytes)','peakRSS_KiB')]:
  v[key]=float(next(x.split(':',1)[1] for x in text.splitlines() if name in x))
 measure[tag]=v
write('RESOURCE_MEASUREMENTS.json',{'measurements':measure,'serial_native_processes':1,'host_limits':'HOST_RESOURCE_LIMITS.json','speedup_claim':False})
stage={}
for mode in ('OFF','KF','GM'):
 rows=list(csv.DictReader((R/'full'/mode/'OWNER_ACCEPTED_STAGES.csv').open()));a=[q for q in rows if int(q['step'])>0]
 stage[mode]={'raw_rows':len(rows),'initial_sentinel_rows':3,'accepted_rows':len(a),'accepted_steps':384,'stage_indices':[0,1,2],'count_total':sum(int(q['count']) for q in a),'temperature_summary_min_K':min(float(q['min']) for q in a),'temperature_summary_max_K':max(float(q['max']) for q in a),'continuity_max_relative':max(float(q['continuity_max_relative']) for q in a),'trace_coverage_finite_schema':'PASS','independent_stage_numerical':'NOT_EVALUATED','metadata_is_not_full_stage_inputs':True}
write('STAGE_TRACE.json',stage)
write('TELEMETRY_AND_GAMMA_COMPARISONS.json',{'native_measurement':'new E12 actual State fields; e11.verify_telemetry exact binary64 on explicitly derived accepted-k>0 stage view','full':val,'internal5_bit_checks':5775,'clock_bit_checks':1155,'bit_mismatches':0,'old_E10_CSV_byte_parity':9,'inherited_E11_analysis':'E11/BASS_HE_E11_OBSERVER_ALIAS_20261009_v1/canonical/analysis/RESULTS.json','E11_analysis_reruns':0,'live_endpoint_gamma_definitions':'distinct, endpoint max allowance ratio3.543295 FAIL retained','paired_source_signals':'inherited E11 finite stored-data diagnostics, not new E12 calculation'})
claims=json.loads((R/'CLAIM_GATES.json').read_text())
ret={'task':'E12_NCP_NATIVE_INTERNAL_5_AND_STAGE_TRACE_VALIDATION','status':'BOUNDED_NEW_TELEMETRY_FULL3X384_INTERNAL5_BIT_PARITY_PASS__STAGE_INDEPENDENT_NOT_EVALUATED','source_commit':'a61b6a0294e88f135df226f092e6fee2adf8e28c','pilot':{'accepted_steps':6,'internal5_bit_checks':45,'clock_bit_checks':9,'old_csv_byte_parity':9},'full':{'campaigns':1,'accepted_steps':1152,'states':1155,'internal5_bit_checks':5775,'clock_bit_checks':1155,'accepted_stage_rows':3456,'initial_sentinel_rows':9,'old_csv_byte_parity':9,'native_exit_all':0},'raw_supplied_verifier':'FAILED_k0_default_trace_compatibility','derived_accepted_stage_consumer':'PASS; raw unchanged','native_tests_passed':5,'separate_test_steps':8,'claims':claims,'full_eligibility':'FULL_ELIGIBILITY.json','procedural_finding':'actual cgroup ancestor inspection corrected after first full launch; initial lookup failure preserved','checkpoint':'no codec; k0 starts; per-step fsynced CSV durable evidence only','failure_records':'FAILURE_RECORDS.json','recovery_inventory':'RECOVERY_INVENTORY.json','next':'NEXT_DAG.json','independent_review':'review/INDEPENDENT_REVIEW.json','delivery':'PENDING_IMMUTABLE_SEAL_AND_DETACHED_R1_RECEIPTS'}
write('RETURN.json',ret)
report='''# E12 NCP 실제 내부장부·accepted-stage telemetry 결과

E10 원 shadow source에 E11 exact telemetry example 하나만 추가했다. 새 내부5필드와 accepted trace 측정의 의존성 변경에 한정하여 pilot 후 full OFF/KF96/GM25 각각384 accepted step을 k0부터 한 번 실행했다. 원 E10/E6/E7/E8 science와 E11 저장값 분석을 별도 재현하지 않았다. 기존 E11 Gamma/paired photoelectron/energy scalar observability 결과는 source-locked 상속 결과이며 E12 새 계산이라고 보고하지 않는다.

## source·컴파일·pilot

Git source a61b6a0294e88f135df226f092e6fee2adf8e28c. E10 runtime SHA d2cec9451719d534b78bdd6ebd7570e03697e9fdd69696c24a966c1a25c91598 (2528362bytes/280payload), E11 SHA4179815c983dff7d47c9f22e9b853436fe1acfcaf2d04fd69c88769a412d52e2 (1405462bytes/69payload), E7 SHA020a58ebc4c57a89d973fde66fd1cd82cd5bc3e3f3bccf9f8dce8856cb8bfe2a (64payload)를 CRC/manifest/hash 검증했다. 새 shadow의 base 파일 전체와 세 coupled/material/radiation blob identity가 exact이며 이미 적용된 patch를 재적용하지 않았다. 원 41열 output/source/tolerance/clock/order는 바꾸지 않았다. SOURCE_IDENTITY.json은 compiler/config/example/binary SHA와 flags를 결속한다.

NCP Rust1.94.1 prefix 재사용, -D warnings, offline locked 기존 affected Rust tests5개와 새 release build exit0. PGP authenticity는 NOT_VERIFIED. 첫2step native OFF/KF/GM 모두 exit0. 내부5필드45값+clock9값 E7 bit parity, 기존9CSV byte parity 통과. 예제는 실제 State.radiation.be[0..2]와 State.material.nonphoto_binding/nonphoto_thermal을 erg/H로 출력했다. E7 값을 native 측정으로 복사하거나 scalar photon budget에서 역추정하지 않았다.

원 E11 emitter가 k0 default trace3행(count0/mininf/max0/any0/all65535)을 출력하여 전달된 verifier는 STAGE_OUTSIDE_ACCEPTED_RANGE로 실패했다. diagnostics.rs Summary::default와 State::new를 확인한 후 raw/native source는 그대로 보존하고, k0 sentinel만 제외한 명시적 derived accepted-k>0 입력 view에서 원 e11.verify_telemetry를 실행했다. raw verifier PASS가 아니다. any/all은 u16 bitmask이다. 파일경로 탐색 실패와 이 consumer 호환 실패는 원 stdout/stderr/exit 및 FAILURE_RECORDS에 남겼다. native retry0.

## 한정된 full telemetry 결과

사용자 E12 item6 조건, pinned handoff section3, 기존 mode/384 승인 범위와 unchanged source/config/gates, 실제 pilot 자원 측정을 FULL_ELIGIBILITY에 기록했다. NEW output namespace, explicit --authorized-full, serial1process, OFF→KF→GM 각1회, 총1152 accepted steps/1155states. source/compiler/binary는 mode 경계 전후 hash 확인했다. E9 Debug는 NONRESUMABLE이며 사용하지 않았다.

| mode | accepted | wall s | user CPU s | RSS KiB | max norm | max Nratio | max Eratio |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
for m in ('OFF','KF','GM'):
 v=measure['FULL_'+m];g=val[m]['original_gates'];report+=f"| {m} |384|{v['elapsed_s']:.6f}|{v['user_cpu_s']}|{v['peakRSS_KiB']:.0f}|{g['norm']:.17g}|{g['Nratio']:.17g}|{g['Eratio']:.17g}|\n"
report+='''
원 OWNER_NATIVE_41.csv/OWNER_SELECTED_RCT.csv/STEPS.csv의 full9파일은 sealed E10와 byte-identical이다. 새 BH/BY/BZ/bindMicro/thermalMicro5775값 및 clock1155값은 E7와 exact binary64 일치, mismatch0. 각 accepted step당 세 stage summary, 총3456행이 존재하고 count>0/finite/ordered minmax/u16 mask 형식을 검증했다. raw 초기 sentinel9행은 그대로 보존했다. stage count는 solver summary count이며 별도 accepted timestep 수가 아니다.

GM maxnorm .9947619985382534는1에 가까워 여유가 크다고 주장하지 않는다. 원 number/energy/nonlinear/EOS/positivity/branch source gates 유지. Native acceptance와 stage summary는 새 actual evidence지만 독립 stage residual/interval 수치 인증은 NOT_EVALUATED: full stage inputs와 알고리즘적으로 다른 source-bound evaluator가 없어 다음 노드를 BLOCKED로 반환한다. Trace 존재만으로 독립 인증 PASS를 부여하지 않았다.

Native live density Gamma와 E7 Endpoint Gamma는 서로 다른 관측 정의. 기존 max allowance ratio3.543295/FAIL을 유지하며 E11 paired-source 변화와 endpoint 마지막시각 equality를 전체 동일성/true-error로 승격하지 않는다. 원 heat/chemical/escape RCT owner 연구 closure35eV를 보존하며 이미 MaterialOwners에 들어간 escape를 두 번 더하지 않았다.

## 호스트·실패·한계

64CPU/1NUMA/affinity0..63, RAM 약125GiB free, serial native memory는 위 측정값. 다른 HH/CR 세션이 있으므로 source/프로세스를 변경하지 않았다. 초기 HOST 복합 명령에서 root cgroup.cpu.max/memory.max 조회는 실패했고 마지막 gh 성공이 이를 가렸다. 독립 검토 후 실제 self+ancestor3단계를 조회하여 모두 cpu.max=max100000, memory.max/high=max임을 확인했다. 이 보완이 첫 full launch 후였다는 HPC preflight 절차 미달을 실패 기록에 명시했다. 실제 자원호환 확인과 원 실행 순서 미달은 구분하며 재실행하지 않았다. HPC rewrite/parallel speedup/hidden fallback 없음.

CR R14 first-cell conditional Thomson tau, REI BRIDGE16 test-only checkpoint, HH ON06G highT는 frozen cached provenance/compatibility guide로만 읽었다. CR의 공통 branch 조회404는 기록했다. 다른 모형을 HE385 true-error 또는 E9 resume 근거로 쓰지 않았다.

baseline RCT OFF, actual atomic photon/heat/recoil moments null, physical/production HOLD, HE-F2/F09 global OPEN, continuous true-error certificate 없음. Receiver HEAD39c39eab1cc2f1a215723680accc123e67ef13b6를 read-only 조회; 무단 merge/push/reset0, SHADOW_CANDIDATE_ONLY. 원 worktree dirty files 유지.

## 전달·복구

raw CSV/stdout/stderr/native EXIT, source/config/compiler pins, tests/gates/실패, inventory/mtime/SHA, verifier view 및 boundary scripts와 source inputs를 immutable private ZIP으로 보존한다. 각 step CSV fsync는 durable evidence이며 resume codec가 아니다. 공개 Git은 authorized branch에 작은 report/계약/검증/additive execution scripts만 non-force 게시하고 readback한다. 양쪽 cloud R1 ACK·name·size·parent와 remote restore는 서로 다른 판정이다. 봉인 시 delivery pending snapshot과 사후 detached receipts를 구분한다. 다음 DAG의 독립 stage/owner adoption/atomic moments는 BLOCKED로 유지한다.
'''
write('REPORT_KO.json',{'generated_from':'FULL_VALIDATION.json, actual native logs','native_reruns':0})
(R/'REPORT_KO.md').write_text(report)
inventory=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and not any(n in p.parts for n in ('target','cargo_home','__pycache__')) and p.name!='RECOVERY_INVENTORY.json':
  st=p.stat();inventory.append({'name':str(p.relative_to(R)),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
write('RECOVERY_INVENTORY.json',{'files':inventory,'process_inventory':'logs/HOST/stdout','checkpoint_codec':'ABSENT','accepted_evidence':'native sync after each row; no resumable restart','original_dirty_files':'unchanged user-owned paths','scope':'snapshot before review/delivery seal; later receipts detached'})
st=json.loads((R/'STATE.json').read_text());st['criteria']['full']='claimed';write('STATE.json',st)
print('RETURN_REPORT_INVENTORY_PREPARED')
