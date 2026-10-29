from pathlib import Path
import json,hashlib,csv,collections
R=Path(__file__).resolve().parents[1];D=json.loads((R/'results/RESULT.json').read_text());v=json.loads((R/'results/MP90_VERIFICATION.json').read_text())
a,b=D['scenario_totals'];cross=D['source_method_crossover'][0]
events=list(csv.DictReader((R/'results/INTERVAL_84_EVENT_EXPOSURE.csv').open()))
fams={1:'H1',2:'D',3:'T',4:'He3',5:'He3',6:'He4',7:'He4'}
def famsums(s):
 d=collections.defaultdict(lambda:[0.0,0.0]);
 for row in events:
  if row['scenario']==s:
   f=fams[int(row['event_index'])];d[f][0]+=float(row['loglinear_photoelectrons_per_Href']);d[f][1]+=float(row['loglinear_photoheat_eV_per_Href'])
 return d
fmt=lambda x:f'{x:.9g}'
repo='cosmosapjw-quantum/rei_bianchi';head='2a667c23de02f19d973f41174480ed1809918aa2'
source={'schema':'REI_P19_FROZEN_EXPOSURE_SOURCE_PROVENANCE_V1','date':'2026-10-30','parent':{'repo':repo,'pr':271,'head':head,'archive':'source_archive/PR271_SOURCE_FULL.zip','bytes':429682,'sha256':'c20b7a776e407c35dff99c32595f394ce0c9426c3469358a8b5d7f2750c68165','member_count':30,'crc':'PASS','manifest_sha':'29/29 PASS','fresh_replay':'19/19 PASS, mpmath56/56 PASS'},'tables':['PR271 results/REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv, 98 rows','PR271 results/REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv, 14 rows'],'primary_paper':{'doi':'10.1093/mnras/stz222','table':'Puchwein 2019 D1 non-equilibrium, existing 13 selected knots, not D2'},'other_source_branches':{'REI_PR270':'six-moment hypothetical nonnegative spectrum, cannot be silently used as actual P19 history','VigilODE_PR118':'BASS saved 127 endpoints / 25 tau histories, owner/different epoch, no common IC','BASS_PR258':'41-sample collisionless Bianchi I Einstein-Vlasov independent baseline','BASS_CR_PR125':'100K RR photon spectrum source, unrelated gas/bath','BASS_HE_PR113':'EXFOR gamma-alpha breakup measured rows, unrelated species/bath','REC_PR160':'HD rotational frequencies, not this H/He UVB','WU_PR164':'HD molecular branching, separate clock'},'source_bytes':'exact ZIP SHA + member sha/csv; no external source re-fit','claim_type':'conditional physical units, not physical posterior or self-consistent cosmological history'}
(R/'SOURCE_PROVENANCE.json').write_text(json.dumps(source,indent=2,ensure_ascii=False)+'\n')
contract={'schema':'REI_P19_FROZEN_EXPOSURE_CONTRACT_V1','program':'REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030','parent_head':head,'source_archive_sha256':source['parent']['sha256'],'input':{'saved_epoch_count':7,'scenario_count':2,'events_per_epoch':7,'elapsed_proper_unit':'s','source_unit':'photoionizations Href^-1 s^-1','heating_unit':'eV Href^-1 s^-1'},'output':{'interval_event_count':84,'interval_summaries':12,'two_scenario_totals':2,'cumulative_knots':14},'methods':{'loglinear_positive':'I=dt*(b-a)/(ln(b)-ln(a)) for each event rate and separately for each heat rate','trapezoid':'I=dt*(a+b)/2','combined_absorption':'I_abs=I_heat+threshold*I_event, not logmean(pointwise absorption)','log_mean_order':'sqrt(ab)<=L(a,b)<=0.5*(a+b)','difference_interpretation':'model/interpolant sensitivity only, NOT a guaranteed error bar or physical difference'},'stiffness_rate_native_ode':'NOT_RUN','new_ivps':0,'actual_p19_rei_coupled':False,'Thomson_tau':None,'constraints':{'NO_MORE_IVPS':True,'F4':'PARTIAL','L4_ready':False,'no_merge':True,'no_force_push':True,'original_DAG_working':'33/88','original_DAG_central':'28/88','physical_fast':'4/7'},'tests':{'python':12,'mpmath':168,'wolfram':'integral identity symbolically zero'},'different_author_R6_C9':'NOT_RUN','source_pins':'SOURCE_PROVENANCE.json'}
(R/'CONTRACT.json').write_text(json.dumps(contract,indent=2,ensure_ascii=False)+'\n')
dag={'schema':'REI_P19_FROZEN_EXPOSURE_DAG_DELTA_V1','original':{'working':'33/88','central':'28/88','physical_fast':'4/7','physical_delta':0,'F4':'PARTIAL','L4_ready':False,'NO_MORE_IVPS':True},'new_scoped_data_node':{'id':'REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030','completed':1,'total':1,'admission':'PASS_SCOPED_CONDITIONAL_QUADRATURE','inputs':'Immutable PR271 source rows only; not new IVP','outputs':list(['INTERVAL_84_EVENT_EXPOSURE.csv','INTERVAL_12_SCENARIO_EXPOSURE.csv','TOTAL_2_SCENARIO_EXPOSURE.csv','CUMULATIVE_14_KNOT_EXPOSURE.csv'])},'dag_88_new_completions':0,'next_physics':{'id':'BASS21_NATIVE_SAVED_193_CLOCK_RESPONSE','source':'VigilODE PR118 original BASS trajectory.npz 193 samples, source integrity readback needed','needs':['original binary trajectory bytes, exact SHA','original BASS time/clock and electron density','original source-owned tau K without invented c sigma','strictly saved-history postprocessing, not new IVP','separate REI/BASS physical model mismatch preserved']},'next_rei_source_event':['common 17/21 initial inventory','P19 radiation source owner with constrained LiI spectrum','full RR/DR/CR/nuclear and fast reservoirs','physical nHref/nb and directional tau geometry']}
(R/'DAG_DELTA.json').write_text(json.dumps(dag,indent=2,ensure_ascii=False)+'\n')
(R/'REPAIR_HISTORY.md').write_text('''# Recorded scientific repair (single bounded episode)\n\n- **Observed first execution FAIL:** `LOGLINEAR_ABS_ENERGY_LEDGER` when independently applying a logarithmic mean to endpoint absorbed power, in addition to independently log-interpolating photoheat and photoionization-storage sources. This violates energy additivity between knots because log interpolation is nonlinear: `L(H+I)` generally differs from `L(H)+L(I)`.\n- **Smallest physics-preserving correction:** define the interpolated absorbed-power function as the sum of independently interpolated heat power and `I_j` times photo-event rate; integrate as `Q_abs=Q_heat+Q_ion`, not a separate logmean of the endpoint total. Keep the trapezoid separately, which preserves additivity by linearity.\n- **Subsequent actual result:** 12 Python regression methods PASS; 168 independent mpmath90 comparisons PASS; all 84 event records have positive source integrals and exact component-energy closure within finite precision. No tolerance relaxed.\n- **Visual repair:** removed a bottom caption overlapping the time-axis label; information moved to chart title.\n- **Not an error certificate:** difference of two assumed interpolants is descriptive scheme sensitivity; no smoothness/curvature bound on true history was supplied.\n''')
lines=['# REI × Puchwein 고정시각 7표본의 시간구간별 photon event/energy 노출량','',f'**Unit:** `{contract["program"]}` · Parent REI [PR271](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/271) HEAD `{head}`.','',
'## 근거와 한계','',
'- 원본 PR271 master ZIP 429,682 B를 바이트 SHA/CRC 및 29/29 내부 payload SHA로 확인하고 복원했다. 19/19 Python, mpmath 56/56 선행 재생 결과를 원본과 분리하여 보존했다. 새 17상태 IVP나 화학방정식은 계산하지 않았다.',
'- Puchwein et al. 2019 MNRAS DOI [10.1093/mnras/stz222](https://doi.org/10.1093/mnras/stz222)의 D1 비평형 UVB 중 기존 PR261에서 선택·검증한 13개 knot와, PR262 ON_refined 17상태의 7개 **다른 모델** 저장상태 및 proper-time 표본만 쓴다. BB13 GLS nominal은 기존 조건부 보정이고 관측 후방분포가 아니다.',
'- 기존 고정 상태의 `rate=particles/Href/s`, `Q_heat=eV/Href/s`를 보존한다. 새 출력은 **각 구간에서 가정한 보간 모델의 exposure**이며 원래 300K bath의 진화·P19 bath 진화·전체 recombination·국소 온도 변경·tau·CMB 관측을 재구성하지 않는다.',
'', '## 새 유도: 양의 로그선형률 노출량', '',
'양수 양끝 source `a,b`와 시간 길이 `Δt>0`에 대하여 구간 내부를 `r(s)=a exp[s log(b/a)]`, `s=(t-t_i)/Δt`로 **명시적으로 가정**하면:',
'', '\\[ I_{\\log}=\\Delta t\\frac{b-a}{\\log b-\\log a},\\qquad I_{\\mathrm{trap}}=\\frac{\\Delta t}{2}(a+b).\\]', '',
'연속 극한 `a=b`에서는 둘 다 `Δt a`. 양의 로그평균과 산술평균 관계로 `I_log<=I_trap`; **이 순서는 가정한 두 보간식 사이의 순서이며 실제 미상 연속 곡선의 오차상계가 아니다.** `r`와 `Q_heat`는 서로 별도 로그선형 함수로 보간한다. 각 photo 사건 j에 대해',
'', '\\[N_j=\\int\\lambda_j dt,\\quad E_{\\rm ion,j}=I_jN_j,\\quad E_{\\rm abs,j}=E_{\\rm heat,j}+E_{\\rm ion,j}.\\]', '',
'처음부터 `Q_abs(t)=Q_heat(t)+I_j lambda_j(t)`로 정의하여 임의의 두 보간 함수를 독립적으로 조합한 후 합으로 적분한다. `Q_abs` endpoint만 따로 로그보간하면 에너지장부가 깨지는 결함을 첫 RED 실행에서 발견·교정했다.',
'', '## 실제 산출물과 새 물리 데이터', '',
'- 시간 구간 6개, 사건 7개, UVB 시나리오 2개: **84개 사건-구간 적분**, 12개 구간/시나리오 총계, 2개 전체 시나리오 총계, 14개 누적 proper-time knot. 실제 숫자들은 CSV·RESULT.json에 보존했다.',
f'- 기존 저장 구간: `z_mean={a["from_z"]:.9f}`에서 `z_mean={a["to_z"]:.9f}`로 진행, 기존 `Δt={a["dt_total_s"]:.12e} s` (신규 time evolution 아님).',
'', '| source prescription | loglinear 사건수 [Href⁻¹] | loglinear 광가열 [eV/Href] | 이온화 저장 [eV/Href] | 총흡수 [eV/Href] | 전자 수 보간 비교 차이 |', '| --- | ---: | ---: | ---: | ---: | ---: |',
]
for t in [a,b]:
 lines.append(f'| `{t["scenario"]}` | {fmt(t["loglinear_photoelectrons_per_Href"])} | {fmt(t["loglinear_photoheat_eV_per_Href"])} | {fmt(t["loglinear_ionization_storage_eV_per_Href"])} | {fmt(t["loglinear_absorbed_photon_eV_per_Href"])} | {100*t["electron_interpolant_sensitivity_frac"]:.5f}% |')
lines+=['', '같은 source를 사다리꼴로 처리하면 fiducial 16.2224221 events/Href 및 76.8745795 eV/Href photoheat, BB13 nominal 14.7545033 events/Href 및 70.1527283 eV/Href photoheat다.',
'','### 사건별 적분량 (양의 loglinear 보간)', '', '| species | P19 fiducial 사건수 [Href⁻¹] | P19 fiducial 광가열 [eV/Href] |', '| --- | ---: | ---: |']
for k,vals in famsums(a['scenario']).items():lines.append(f'| {k} | {fmt(vals[0])} | {fmt(vals[1])} |')
lines+=['',f'저장 knot에서 H1와 He4 photon-electron *source share*의 선후가 바뀌는 구간은 `z_mean={cross["bracketed_z"][0]:.6f}`와 `{cross["bracketed_z"][1]:.6f}` 사이다. 각 group rate의 두 양끝 로그보간과 `z_mean`의 time-linear label 보간을 같이 사용한 **설명용 proxy**는 `z_label≈{cross["at_mean_z_label_linear_time_proxy"]:.6f}`이다. REI/P19 physical crossing redshift는 아니다.',
'', '## 교차 검증, 연구 DAG 및 부족한 입력','',
f'- 새 독립 mpmath 90자리 **{v["cases"]}/168** positive logmean values 비교 PASS; 최댓값 상대차 `{float(v["max_relative_error"]):.3g}`. Python unit **12/12 PASS**; Wolfram 닫힌 적분식 잔차 0. 원본 PR271 Python 19/19 및 mpmath56/56은 다시 실행했으나 신규 단위 과학 완료에 더하지 않는다.',
'- **원 working 33/88, central 28/88, physical-fast 4/7, delta 0**. 새로운 scoped static exposure 데이터 단위 1/1은 원 DAG88의 물리 노드 완료가 아니다. F4 PARTIAL, L4 false, NO_MORE_IVPs true.',
'- 실제 저장된 193-sample BASS native trajectory와 명확한 K/nHref/nb/clock/초기동위원소 정합, REI full chemical/Jacobian 및 source-owned photon spectrum은 여전히 필요한 입력이다. 이번 계산은 해당 gate를 통과하지 않는다.',
'', '## 재현', '', '```bash', 'python -m unittest discover -s tests -v', 'python code/exposure.py', 'python code/reference_mp.py', 'python code/plot_exposure.py', '```', '',
'산출물: `results/INTERVAL_84_EVENT_EXPOSURE.csv`, `INTERVAL_12_SCENARIO_EXPOSURE.csv`, `TOTAL_2_SCENARIO_EXPOSURE.csv`, `CUMULATIVE_14_KNOT_EXPOSURE.csv`, 두 PNG, `RESULT.json`, `MP90_VERIFICATION.json`. 원본 source ZIP은 `source_archive/PR271_SOURCE_FULL.zip`로 정확히 잠금.',
'']
(R/'REPORT_KO.md').write_text('\n'.join(lines))
(R/'THEORY_KO.md').write_text('''# 시간구간 물리 소스 적분 이론\n\n가정: frozen REI `ON_refined` 7개 `(t_i,z_i,y_i)`는 원본 source의 proper seconds와 mean-z label. `lambda_j(t_i)` 및 `Q_heat,j(t_i)`는 Puchwein 2019 D1 13-knot six-moment를 별도의 원 REI 시뮬레이션과 조합한 **조건부 hybrid source**다.\n\n두 양의 endpoint `a,b` 사이에 `r(t_i+s Δt) = exp((1-s) log a+s log b)`로 보간.\n\n`Integral r dt = Δt*(b-a)/(log b-log a)` (단 a=b는 Δt a). 이는 정확하게 로그평균 `L(a,b)`이며 `sqrt(ab) ≤ L(a,b) ≤ (a+b)/2`. 사다리꼴 `I_tr=Δt(a+b)/2`는 두 번째 선언된 interpolation diagnostic이다. 이 사이의 차이는 물리 연속해/적분 오차 상계가 아니다.\n\n각 H1/D/T/He3/He4의 7개의 원 REI ionization 사건 j마다 양수 source `lambda_j=Y_src Γ_c`, `h_j=Y_src H_c`, ionization threshold I_j (eV).\n\n`N_j=integral lambda_j dt` (events/Href), `Heat_j=integral h_j dt` (eV/Href), `Ion_j=I_j*N_j` (eV/Href), `Abs_j=Heat_j+Ion_j` (eV/Href). `Abs_j`를 별도 로그보간하지 않는다. 그러면 사건별 전자 생성 횟수 1, 핵자수 보존은 원본 S 행의 linear invariants에서 계속 성립.\n\n경계: 실제 P19-fiducial 전개된 chemistry `(y(t),T(t),H(t))`가 아니다. 서로 다른 UVB 노출과 원 REI frozen 이력의 hybrid. Source injection/recombination/collisions 및 광자 전달, 실제 proper τ/Thomson K/directional redshift 미포함.\n\n행렬 산출: 6 intervals × 7 events × 2 cases =84, 12 interval totals, 14 cumulative, 2 totals. 조건부 source H1↔He4 dominance proxy도 two endpoint linear time label의 model output에 불과.\n\n실행 기록: 첫 `LOGLINEAR_ABS_ENERGY_LEDGER` 실패를 근거로 energy construction 교정. 12 Python PASS, 168 mpmath90 PASS, Wolfram symbolic logmean identity residual zero.\n''')
(R/'HANDOFF_NEXT_THREAD_KO.md').write_text(f'''# REI 원본 저장시간 photon-source 노출 데이터 후속 연구 인계 (2026-10-30)\n\n`$physmath-research-loop $scispace $exa $wolfram`\n\n```
PROJECT=cosmosapjw-quantum/rei_bianchi
PARENT_PR=271
PARENT_HEAD={head}
UNIT=REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030
NEXT_NODE=BASS21_NATIVE_SAVED_193_CLOCK_RESPONSE
NO_AUTO_NEXT_NODE=true
WORKING_DAG=33/88
CENTRAL_DAG=28/88
PHYSICAL_FAST=4/7
PHYSICAL_DELTA=0
F4=PARTIAL
L4_ready=false
NO_MORE_IVPs=true
NO_MERGE=true
NO_FORCE_PUSH=true
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
```
\n이 패키지는 PR271 고정 원본 ZIP SHA {source['parent']['sha256']}를 보존한다. `REPORT_KO.md`, `THEORY_KO.md`, `CONTRACT.json`, `SOURCE_PROVENANCE.json`, `DAG_DELTA.json`, `results/*`, `tests/test_exposure.py`, `code/exposure.py`, `code/reference_mp.py`, `code/plot_exposure.py` 및 `delivery/FINAL_ACK.json`(GitHub final closeout only)을 먼저 읽어라. 새 source-only 데이터 84 interval-event, 12 interval, 14 cumulative, 2 total, 168 mpmath checks. **HYBRID INTERPOLANT**이다.\n\n다음 실제 물리 데이터 우선 작업: VigilODE PR118에서 원래 BASS 193 point/time trajectory `research/rei_hheli_compact_pilot_20261022/results/pilot_v2/cases/s00_m00_r00/trajectory.npz` (Git blob 57a5375c5183f83d3eb3dd094cac31a212c39de3, size254301, expected SHA256 37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086)을 소스 원문 바이트로 확보하라. Native source K, n_b,H, clock, chemical 21-state, tau operator와 저장 193 points를 동일 source에서 묶어 **기존 저장 이력의** electron-column/Thomson RHS 대조만 수행하라. 재차 IVP solve 금지. 마땅한 소스 바이트/clock/K가 없으면 HOLD with exact gap. 이 BASS 지표를 REI hybrid 7상태나 P19 스펙트럼과 혼합하여 단일 물리 posterior/tau로 승격하지 마라.\n\n각 수행 단계에서 실제 GitHub commit/backup ACK를 적고 canonical 33/88 및 28/88을 유지하라. 독립 작성자 R6/C9는 실제 부재이므로 PASS로 선언하지 않는다. Drive/Dropbox success는 실제 ACK 및 리드백이 있는 경우만. Historical resource budget은 reset/transfer 금지, host overhead UNKNOWN_NOT_ZERO.\n''')
(R/'REPAIR_HISTORY.md').write_text((R/'REPAIR_HISTORY.md').read_text())
print('REPORT',len(lines),'lines',R/'REPORT_KO.md')
