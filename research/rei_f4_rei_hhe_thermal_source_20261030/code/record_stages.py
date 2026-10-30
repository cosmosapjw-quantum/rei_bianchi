#!/usr/bin/env python3
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/RESULT.json').read_text())
stages=[
('R1','연구 목표·계약','Bind source-qualified REI igm_rates/thermal point RHS to 193 immutable BASS original states; no IVP, no native REI17 claim','SOURCE_LOCK.json'),
('R2','원전·기존 성과 재사용','Read PR293/276/287/281, Rust igm_rates.rs, igm_thermal.rs, bianchi_i.rs; source identities pinned','THEORY_AND_RESULT_KO.md'),
('R3','전제·주장 정합성','Distinguish REI-HHe-only electron bath, full 21 free-electron bath, nHref/nb, and external CMB monopole','THEORY_AND_RESULT_KO.md'),
('R4','대안 구성','Build 5-state HHe source with gamma sourced from BASS, optional full 21-species charge cross-J, conditional Bianchi K proxy','code/build_physics.py'),
('R5','구성적 유도·증명','Derive F/J charge chain rule, source replacement, thermal/binding/escaped ledger and energy conservation identities','THEORY_AND_RESULT_KO.md'),
('R6','적대적 심사','Same-author hostile review identified and corrected b/K convention; identified BASS vs REI ionization threshold energy owner defect','ADVERSARIAL_AUDIT_KO.md'),
('R7','경량 판별·실제 계산','193 real original states; 579 events; 965 F, 4825 J, 20265 full-bath cross-J cells; 6 scientific plots','results/RESULT.json'),
('R8','과학적 수용 판정','Accept source-qualified point RHS as scoped auxiliary; do not promote physically complete F4 or heat/CMB predictions','THEORY_AND_RESULT_KO.md'),
('R9','이론-계산 연결','Computational source replacement in event-count, energy-owner and thermal-capacity units with explicit clock','code/build_physics.py'),
('R10','결과 보존·인계','Archive original source + tested code, output and plots; preserve next blocked native REI17 work','HANDOFF_NEXT_THREAD_KO.md'),
('C1','계산 목표·기준','Preserve PR293 master bytes SHA and BASS original 193 trajectory','SOURCE_LOCK.json'),
('C2','코드·데이터 매핑','Map Rust IgmRates/PointRhs chemistry rates to BASS photo gamma and per-absorber primary heat, using PR276 source owner','code/build_physics.py'),
('C3','물리적 이산화 설계','Point RHS on existing saved proper-time snapshots, no solver; signed energy conservation and 5x21 derivative','THEORY_AND_RESULT_KO.md'),
('C4','작업·백업 단위','Isolated Git branch + source-inclusive ZIP; periodic scoped checkpoints without changing production','SOURCE_LOCK.json'),
('C5','계산 구현','Run 193 real states from original source: source-translated thermal FJ, Compton, energy and K proxy; output CSV/NPZ/PNG','code/build_physics.py'),
('C6','회귀·소프트웨어 검증','35 targeted Python tests; frozen PR276 F/J parity and archive corruption negative test','tests/test_source_thermal.py'),
('C7','물리 검증','Event stoichiometry, charge conservation, energy ledger, threshold source defect, axisym sign test','ADVERSARIAL_AUDIT_KO.md'),
('C8','수치·재현 검증','Exact deterministic replay, source SHA, cross-J finite differencing; no irrelevant speed optimization','VERIFY.sh'),
('C9','독립 코드 심사','Single same-author hostile check on source substitution and K sign; genuine distinct-author C9 NOT_RUN','ADVERSARIAL_AUDIT_KO.md'),
('C10','배포·계속 판정','Bounded auxiliary source data, full ZIP, Git draft, Library+Drive backup; F4 still PARTIAL','HANDOFF_NEXT_THREAD_KO.md')]
for st,name,summary,path in stages:
 v={
  'schema':'REI_PHYSFAST_STAGE_V2','stage':st,'stage_name':name,'assessment':'SCOPE_STAGE_CHECKPOINT',
  'same_science_execution':True,'evidence':summary,'artifact':path,
  'original_source_PR293_head':'fd9385f131f93dae2868bbb50b6a542f09dd870b',
  'science_counts':'193 BASS saved states | 579 event rows | 965 F5 | 4825 J5 | 20265 J5x21 | 6 plots',
  'DAG':'working33/88|central28/88|fast4/7|canonical_delta0|auxiliary1/1',
  'R6_C9_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN',
  'scientific_gate':'F4=PARTIAL;L4_ready=false;PRODUCTION=HOLD',
  'new_IVP':0,'no_merge':True,'no_force_push':True,'auto_next_node':False,
  'non_independent_execution_note':'20 stage records belong to ONE bounded source calculation, not twenty independent runs'
 }
 out=ROOT/'stages'/(st+'.json');out.parent.mkdir(exist_ok=True)
 out.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print('STAGES=20/20 recorded; independent-author 0/2')
