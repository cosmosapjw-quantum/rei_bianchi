import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
s=json.loads((R/'results/EXACT_SUPPORT.json').read_text());t=s['nuisance_support'];ref=json.loads((R/'results/NUMPY_REFERENCE.json').read_text());inp=json.loads((R/'source/FROZEN_BB13_SUPPORT_INPUT.json').read_text())

def put(n,v):(R/n).write_text(v)

put('THEORY_AND_CONTRACT_KO.md',f'''# REI: EOS–Jeans 보정 상자에 대한 2차원 UVB GLS support (2026-10-29)

## 실제 source와 변경하지 않는 전제

1. [Becker & Bolton (2013), Table 1/2](https://doi.org/10.1093/mnras/stt1610): z=(2.4,2.8,3.2,3.6,4.0,4.4,4.75), nominal log10(Γ_HI/10^-12 s^-1) 7개, 상관 통계 공분산 C (dex², Table2 original 100×C /100), γ_TDR=1.4 기준. γ=1.6의 인쇄 보정 v={inp['eos_response_dex']} dex; Jeans smoothing asymmetric source shifts lower={inp['jeans_smoothing_lower_dex']} and upper={inp['jeans_smoothing_upper_dex']} dex. Full original source Git blob {inp['original_source_observation_git_blob']}.
2. Puchwein2019 저장 template 7개와 PR251 calibration blob {inp['original_saved_calibration_git_blob']}는 기존 그대로. 이전 PR252 단일 redshift slope, PR253 단일 EOS response는 모두 **재사용**. 새 코어는 그 어느 저장소 source나 solver를 변경하지 않는다.
3. EOS의 θ=(γ_TDR−1.4)/0.2 ∈[-1,1], 고정 응답 벡터 v; Jeans 보정 j_i∈[l_i,u_i]를 7개의 **독립적인 결정론적 범위 좌표**로 허용한다. 이는 실재 물리의 독립 확률변수나 68% credible interval을 주장하지 않으며 실제 가능한 공동집합은 더 작을 수 있다. γ와 Jeans가 실제 공동물리에서 연관된 경우에도 이 직사각형을 **상위 집합**으로 사용하는 조건부 해석만 가능하다.
4. 모든 C/자료 값은 정확한 binary64 실수상(Fraction.from_float). Source projection file SHA256 `{s['source_sha256']}`. 원래 논문 PDF raw byte를 받았다고 주장하지 않는다. 고정 Puchwein template, EOS response의 선형 보간, C의 nuisance 비의존성을 유지한다.

## R4–R5: 핵심 정리와 증명

X=[1,z−3.6], W=C⁻¹, M=XᵀWX. 입력된 C는 정확 LDLᵀ에서 7개의 양의 pivot을 가지며 M은 rank2이고 det(M)>0이다. r=d−m으로 두면

**a(θ,j)= (β,κ)ᵀ = a₀ + A(θv+j), A=M⁻¹XᵀW, a₀=A r.**

c_i=(l_i+u_i)/2, h_i=(u_i−l_i)/2. ∣θ∣≤1, ∣q_i∣≤1인 독립 상자에서

a = a₀ + A c + (A v) θ + Σ_i (A_:i h_i) q_i.

즉 8개 생성자를 가진 2차원 **zonotope**의 정확한 선형상이다. 임의 쌍대방향 s∈R²의 support는

**h_Z(s) = s·(a₀+A c) + ∣s·A v∣ + Σ_i h_i∣s·A_:i∣.**

증명: 각 θ, q_i가 독립 구간 [-1,1]에 있으므로 s·a의 최대는 각 항의 계수 부호에 따라 각각 끝점에서 달성된다. 같은 원리로 최소는 −s에 대한 최대로 얻는다. 물리적 likelihood에서 독립이라는 가정은 사용하지 않았다. 2²? 정확히 2^(1+7)=256개 외곽 꼭짓점의 완전 확인은 수치 프로그램의 교차검사일 뿐, 위 해석적 증명에서 요구되지 않는다.

추가로 1열 진폭-only 잔차의 profile χ²와 2열 profile χ²의 차이는 

ΔQ(θ,j) = [x_⊥ᵀW(r+θv+j)]²/(x_⊥ᵀWx_⊥)≥0, x_⊥ = x−1(1ᵀWx)/(1ᵀW1),

C가 양정치이고 x_⊥≠0이므로 항상 비음수다. 256개 상자 꼭짓점에서 정확 유리수로도 확인. 이 항등식은 nuisance box를 확률적 marginalization으로 바꾸지 않는다.

## R7–R8: 실제 수치 정리

- 기존 nominal κ₀={s['reused_amplitude_tilt']['kappa0']} dex/z; β₀={s['reused_amplitude_tilt']['beta0']} dex.
- EOS 방향 dκ/dθ={s['eos_direction_dtheta']['dkappa']} dex/z, 이전 PR253과 동일 (새 독자성 주장 없음).
- Jeans 중심 shift={t['kappa_central_Jeans_center_shift']} dex/z; Jeans half-width={t['kappa_Jeans_halfwidth']}; EOS half-width={t['kappa_EOS_halfwidth']}.
- **κ ∈ [{t['kappa_min']}, {t['kappa_max']}] dex/redshift**, 끝점은 실제 정확 유리수 연산과 명시적 꼭짓점 witness로 달성됨.
- β ∈ [{t['beta_min']}, {t['beta_max']}] dex (β와 κ 각각의 한계는 서로 다른 꼭짓점에서 달성될 수 있으므로 둘을 직교 신뢰상자로 오해하지 말 것).
- κ-min witness: θ=+1, γ=1.6; j={t['kappa_min_witness']['j']}.
- κ-max witness: θ=−1, γ=1.2; j={t['kappa_max_witness']['j']}.
- 256/256 exact corner supports 및 nested χ² identity 점검. 별도 NumPy Cholesky/solve 256-corner 결과와 각 4개 극값 차이 < 3×10^-17. 별도 Wolfram 선형대수 대조도 부호/숫자 일치. 표적 테스트 8/8 PASS.

이 결론은 **인쇄된 EOS 방향과 per-redshift Jeans 구간의 직사각형에서 κ의 0 교차가 없다는 조건부 support 정리**다. 실제 물리적 UVB slope 발견, 관측 원자료의 독립 선별, posterior, 모델 불확실성 전파, Bianchi global velocity tilt, 완결된 F4·L4·native25가 아니다. C에 Jeans를 임의로 quadrature 합성하지 않았다. 

## 다음 과학 및 코드 경계

Source-labelled 범위의 독립 모델 심사 R6/C9는 `NOT_RUN` (이 스레드에서 native child 도구 없음). 기존 PR253·254·255의 결과와 충돌하면 새 산출물은 observation-only 참고자료이며 owner source 결과를 자동 덮어쓰지 않는다. 새 실수치 IVP, heat, photo-rate, Li provider, 종 배열 및 중앙 DAG 갱신 없음. 실험 개시 전 resource: 새로운 bounded command 5+5 CPU seconds target, 8 CPU seconds presentation; 측정값과 미측정 overhead 분리. `UNKNOWN_NOT_ZERO`, closed grants 유지. 원 DAG working33/88, central28/88, delta0.
'''.replace('\x12',''))
put('REPORT_KO.md',f'''# REI 2026-10-29 새 연구 단위 결과와 재현성 복구

## 최신 연구 재사용

PR248 17-state prescribed-bath pilot 7/7 재실행 없음, PR251 고정 Puchwein template / 7-point BB13 full covariance, PR252 single redshift tilt 18/20 재실행 없음, PR253 EOS-only tilt θ∈[-1,1] 18/20 (C8 그림 CPU overrun, R6/C9 대기), PR254 clean checkout repaired, PR255 exact-rational/Wolfram EOS-only 교차검증이 선행 근거다.

이번 연구는 EOS-only의 중복이 아니라 **7개 redshift-specific Jeans smoothing 구간을 추가하여 β, κ의 공동 affine support**를 구했다. primary source Becker & Bolton2013 Table1·2 외의 2026년에 새 추정한 자료가 아니다.

### 조건부 계산 실제 결과

| 값 | Source-bounded 값 |
| --- | --- |
| nominal κ₀ | {s['reused_amplitude_tilt']['kappa0']} dex/redshift |
| EOS+Jeans κ min | {t['kappa_min']} dex/redshift |
| EOS+Jeans κ max | {t['kappa_max']} dex/redshift |
| EOS+Jeans β min | {t['beta_min']} dex |
| EOS+Jeans β max | {t['beta_max']} dex |
| GLS covariance pivot | 7/7 exact positive |
| Exact vertices and nested model | 256 corners PASS |
| Independent NumPy reference | 4 extrema within 3e-17 |
| Wolfram independent engine | 4 extrema and projected derivative matched |
| Targeted unittest saved result | 8/8 PASS |

그림 `results/ZONOTOPE_SUPPORT.png`는 256 outer-box 꼭짓점의 2D convex hull, 기존 EOS-only 선분과 PR252 nominal 한 점을 분리해 표시한다. 실제 직접 이미지 readback PASS. 

### 별도 PR254 재현성 복구

[PR254 sibling clean CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40722462146)는 source Git blob 9/9, 원본 clean checkout `results/` 없음, post-fix 24/24 Python 테스트 PASS, 13 source/reference guards PASS. 0.20 wall, 0.08 user+0.01 system CPU, RSS14464KiB, exit0; GitHub source code와 관측 원본은 변경하지 않음. [원시 CI artifact](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40722462146/artifacts/12830273306)는 5400 bytes SHA256 `93a063aeb75db23cb96f0c6d72d1df1aae3bea7776c3d334d8c6250ba777b4d3`. Drive `1HwD2Kg4H8jWDgREXshkFs_cUigJeiJtn`, Dropbox `id:BSpOijBcT10AAAAAAEGpXA` 완료. 별도의 Rust repository-wide cargo fmt CI 실패는 해당 UVB Python 검증 성공과 혼동하지 않는다.

### 실제 새 실행과 자원

Exact Fraction worker user0.37+sys0.00 CPU-s, wall0.37s; NumPy reference user1.16+sys0.08 CPU-s, wall0.84s; 8-test suite user0.03+sys0.01 CPU-s wall0.04s; zonotope figure user1.44+sys0.12 CPU-s wall1.57s. Commands and raw stderr/stdout/time are preserved. Model, tool transport, remote publication and other unmetered tails `UNKNOWN_NOT_ZERO`; old exhausted reservations are not reset nor transferred. No global cumulative budget PASS claim.

### 수용 범위

`MATHEMATICALLY_DERIVED_AND_NUMERICALLY_CHECKED_CONDITIONAL_SUPPORT`, independent distinct-author R6/C9 `NOT_RUN`. Local work R1–5,R7–10 and C1–8,C10: 18/20; original canonical28/88, owner working33/88 unchanged. Physical F4 remains PARTIAL, L4 false, actual native25/temperatures/physical radii null. H–Li registry 26 ground+5 nuclear excited/102 formal requests are NOT new active species and do not change 17-state solver. No ODE/IVP or actual photonic source transfer.
''')
put('HANDOFF_NEXT_THREAD_KO.md',f'''# 다음 rei_bianchi 연구 스레드 handoff (복사용)

```text
$physmath-research-loop
PROJECT=cosmosapjw-quantum/rei_bianchi
CURRENT_NEW_UNIT=REI_UVB_EOS_JEANS_BOX_20261029
SOURCE_PR251_PIN=c5ab42c8673db614e7fb16695ad071c65becb81b
PR252_PARENT=eecd9b2c1c95f9319c1da41951b814855b0feb11
PR253_EOS_OWNER=21c695be2f672f5487e3fe1beb69b07af07a3c92
PR254_REPRO_OWNER=2a1c163e3bddef9706e133117b35a1fb5750f4aa
PR255_EOS_SUPPLEMENT=63c8659670e159ce4a76db243a65fed25286da82
PR254_CLEAN_CI=https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40722462146
PR254_CLEAN_CI_ARTIFACT=12830273306
PR254_CLEAN_CI_PASS=9/9 blob, 24/24 unittest, 13 guards, 0.09 CPU-s
PR253_PROGRESS=18/20_SCOPED_R6_C9_HELD_C8_RESOURCE_CONCERN
NEW_UNIT_PROGRESS=18/20_SCOPED_R6_C9_HELD
CANONICAL_DAG=28/88
REI_WORKING_DAG=33/88
DAG_DELTA=0
F4=PARTIAL
L4_ready=false
actual_REI_temperature=null
actual_native25=null
physical_radii=null
NO_MORE_IVPs=true
AUTO_NEXT_NODE=false

SCIENTIFIC_DERIVATION:
C=BB13 seven-point full statistical covariance dex2.
r=d-m; X=[1,z-3.6]; A=(X^T C^-1 X)^-1 X^T C^-1.
theta=(gamma_TDR-1.4)/0.2 in [-1,1].
Per-redshift Jeans j_i between source-printed l_i,u_i independently
ALLOWED as an outer box, not a probability prior.
a(theta,j)=(beta,kappa)=A(r+theta v+j).
Support h_Z(s)=s dot (A(r+c)) + |s dot Av| + sum_i h_i |s dot A_i|.
KAPPA_MIN={t['kappa_min']}
KAPPA_MAX={t['kappa_max']}
BETA_MIN={t['beta_min']}
BETA_MAX={t['beta_max']}
Exact rational 256/256 corners/nested chi2 PASS.
Independent NumPy 256 vertex/cholesky, Wolfram numeric, 8 unittest PASS.
No physical discovery, same-source covariance, no EOS/Jeans posterior.

NEXT:
1) Verify latest PRs, especially PR253 EOS owner, PR254 reproducibility and
   PR255 supplemental audit; avoid duplicate EOS-only research or re-running IVPs.
2) Collect a TRUE distinct-author R6/C9 review of this joint source-bound
   support, plus PR253 and PR252 affected code. Current same-author reviews
   and Wolfram/NumPy are not a native different reviewer.
3) Scientific promotion only for scoped conditional support when independent
   admission and resource accounting pass. No source/solver change automatically.
4) Preserve actual Git and Drive/Dropbox ACK IDs and source hashes. Full backup
   does not mean unverified remote whole-byte SHA. No force push or merge.
```
''')
put('README.md','# REI UVB EOS+Jeans conditional support\n\nSource-bound exact-rational 2D zonotope and frozen reference/figure. Read THEORY_AND_CONTRACT_KO.md, REPORT_KO.md, HANDOFF_NEXT_THREAD_KO.md. R6/C9 native independent reviewer NOT_RUN. All code preserved as experimental research, not an active REI provider. Original DAG 33/88 working /28/88 central unchanged.\n')
ST=[]
items={
'R1':('question+source/claim freeze','source/FROZEN_BB13_SUPPORT_INPUT.json'),
'R2':('primary BB13 Table1/2 and reusable PR251-253 inputs','THEORY_AND_CONTRACT_KO.md'),
'R3':('fix log units, EOS theta and independent-box meaning','THEORY_AND_CONTRACT_KO.md'),
'R4':('derive affine GLM/zonotope support candidate','THEORY_AND_CONTRACT_KO.md'),
'R5':('prove support endpoint witness and nonnegative nested Q','THEORY_AND_CONTRACT_KO.md'),
'R7':('exact arithmetic 256 and Wolfram numeric readback','results/EXACT_SUPPORT.json'),
'R8':('conditioned claim ceiling and countercases','REPORT_KO.md'),
'R9':('formal theorem and GLS code contract','THEORY_AND_CONTRACT_KO.md'),
'R10':('handoff and durable result closeout','HANDOFF_NEXT_THREAD_KO.md'),
'C1':('reuse source and fix acceptance','FROZEN_EXECUTION.json'),
'C2':('map C/observed/model to exact source/units','source/FROZEN_BB13_SUPPORT_INPUT.json'),
'C3':('exact LDL Gaussian plus independent numpy oracle','code/jeans_support.py'),
'C4':('frozen commands and resource family','FROZEN_EXECUTION.json'),
'C5':('complete exact code + numpy + saved figure path','code/jeans_support.py'),
'C6':('actually execute frozen exact worker and 8 tests','results/RUN_TIME.txt'),
'C7':('exact 256 nested and signed kappa witnesses','results/EXACT_SUPPORT.json'),
'C8':('independent float64 256 vertices and actual CPU/figure','results/NUMPY_REFERENCE.json'),
'C10':('scoped decision plus user-transfer handoff','HANDOFF_NEXT_THREAD_KO.md')
}
count=0
for ix,code in enumerate(list(items),1):
 count+=1
 obj={'stage':code,'stage_local_progress':f'{count}/20','original_DAG_working':'33/88','central_last_observed':'28/88','DAG_delta':0,'stage_status':'OUTPUT_COMPLETE_SCOPED_NONAUTHORITATIVE','objective':items[code][0],'primary_evidence_path':items[code][1],'R6':'HOLD_DISTINCT_AUTHOR_REVIEW','C9':'HOLD_DISTINCT_AUTHOR_REVIEW','independent_native':'NOT_RUN'}
 (R/'stages'/f'{code}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');ST.append(obj)
ST.append({'stage':'R6','stage_status':'NOT_RUN_DISTINCT_AUTHOR_REVIEW','progress':'18/20','original_DAG':'33/88 working / 28/88 central','claim_gate':'HOLD'})
ST.append({'stage':'C9','stage_status':'NOT_RUN_DISTINCT_AUTHOR_REVIEW','progress':'18/20','original_DAG':'33/88 working / 28/88 central','claim_gate':'HOLD'})
(R/'STAGE_LEDGER.json').write_text(json.dumps({'schema':'REI_UVB_EOS_JEANS_STAGES_V1','local_count':'18/20','theory':'9/10','coding':'9/10','reused_parent_not_changed':True,'DAG_working':'33/88','DAG_central':'28/88','DAG_delta':0,'stages':ST},ensure_ascii=False,indent=2)+'\n')
print('BUILD_REPORTS_COMPLETE',len(items))
