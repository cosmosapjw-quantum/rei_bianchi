#!/usr/bin/env python3
"""Integrate frozen PHYS27 evidence; arithmetic/readback only, no science."""
from pathlib import Path
from decimal import Decimal as D, getcontext
import hashlib
import json

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT/path).read_text())
def ident(path):
    p=ROOT/path
    return {'path':path,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(path, value):
    p=ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

r=read('contributions/numerics/FINITE_WIDTH_FIRST.json')
t=r['threshold_comparison']
replay=read('portability/REPLAY_RECEIPT.json')
assert r['summary']['all_pass'] and replay['status']=='PASS' and replay['comparison']['byte_equal']
reduction=D(t['coexistence_width_PHYS26_eV2'])-D(t['coexistence_width_delta_eV2'])
percent=100*reduction/D(t['coexistence_width_PHYS26_eV2'])
case=next(x for x in r['physical_variance_cases'] if x['label']=='mixed_W19_74')
theory=read('contributions/theory/THEORY_CLAIMS.json')
summary={
    'task':'REI-PHYS27-20261011','name':'FINITE_WIDTH_RESPONSE_ENVELOPE',
    'scientific_results_status':'COMPLETED_CANDIDATE; final decision authority is independent/DECISION_REVIEW.json',
    'successor_of':'REI-PHYS26-20261011','model':'GPT-6 Astra','harness_version':'4.0.0',
    'input_commit':'75fd81e9e63c442d6da5f95bd3a80bdec16a4c37',
    'source_tree':'cb69b4736dd046e4675557577eb8e0ead037d1f3',
    'physical_admission':'HOLD',
    'family':{'mean_eV':'18','photon_support_eV':['13.61','24.58'],
        'half_width_eV':'0.05','full_width_eV':'0.10','center_support_eV':['13.66','24.53'],
        'normalization':'photon number','W_photon':'V_center+delta^2/3',
        'Wmin_exact_eV2':'1/1200','Wmax_exact_eV2':'850231/30000',
        'Vmax_exact_eV2':'28.3402'},
    'derived':theory['exact_formulas'],
    'root_existence_evidence':'Exact monotonicity plus explicitly numerical endpoint signs; no interval-certified endpoint sign campaign',
    'numerical_endpoint_signs':r['numerical_endpoint_signs'],
    'threshold_numerical_approximations':t,
    'coexistence_reduction_eV2':str(reduction),'coexistence_reduction_percent':str(percent),
    'root_diagnostics':{k:{a:b for a,b in v.items() if a!='history'} for k,v in r['new_physical_roots'].items()},
    'nine_variance_cases':[{'label':x['label'],'W_photon_eV2':x['W_photon_eV2'],
        'V_center_eV2':x['V_center_eV2'],'interval_s-4':x['interval_s-4'],
        'PHYS26_same_W_interval_s-4':x['PHYS26_delta_allowed_same_W_interval_s-4']} for x in r['physical_variance_cases']],
    'representative_W19_74':case,
    'mixtures_W19_74':r['mixtures_at_W19_74'],
    'first_execution':read('contributions/numerics/EXECUTION.json'),
    'first_summary':r['summary'],
    'portability':{'status':replay['status'],'main_invocations':1,'independent_physics_credit':0,
        'stage_payloads':replay['stage_verification']['payload_count'],
        'comparison':replay['comparison'],'replay_counts':replay['replay_counts_as_instrumented_by_frozen_program'],
        'receipt':ident('portability/REPLAY_RECEIPT.json')},
    'display':read('figures/DISPLAY_RECEIPT.json'),
    'execution_ledger':{'new_first_science_main':1,'new_program_portability_main':1,
        'total_actual_PHYS27_main_invocations':2,'first_physical_root_searches':2,
        'replay_physical_root_searches':2,'total_PHYS27_physical_root_search_executions':4,
        'first_kernel_evaluations':3923,'replay_kernel_evaluations':3923,
        'display_kernel_values':5508,'old_PHYS19_26_main_or_suite':0,
        'old_physical_root_searches':0,'new_derivative_sign_campaigns':0,'native':0,'gas_IVP':0},
    'scoped_artifacts':[ident(x) for x in ['PHYSICS_CONTRACT.json','SOURCE_MANIFEST.json',
        'contributions/theory/FINITE_WIDTH_DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json',
        'contributions/numerics/finite_width_envelope.py','contributions/numerics/PROTOCOL.json',
        'contributions/numerics/PREEXECUTION_FROZEN.json','contributions/numerics/FINITE_WIDTH_FIRST.json']],
    'protected':read('PHYSICS_CONTRACT.json')['protected'],
    'not_promoted':read('PHYSICS_CONTRACT.json')['claim_ceiling'],
    'next':'PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY; proposal only, not executed',
    'decision_authority':'independent/DECISION_REVIEW.json and DECISION_REVIEW_KO.md',
    'publication_authority':'Detached PHYS27_PUBLICATION_RECEIPT.json after final gate; no preclaimed Git or upload success',
}
write('report/PHYS27_RESULTS_SUMMARY.json',summary)
claims={
 'task':'REI-PHYS27-20261011','final_gate_authority':'independent/DECISION_REVIEW.json',
 'common_condition':'Frozen source-real kernel and serialized numerical J; Physical HOLD',
 'nodes':[
  {'id':'C27.1','claim':'Finite-band family, exact moments and feasible photon variance',
   'grade':'derived','depends_on':['PHYSICS_CONTRACT'], 'evidence':['TH27.1','TH27.2','TH27.3']},
  {'id':'C27.2','claim':'Averaged derivative signs, all-W sharp bounds, unique extremes and endpoint degeneracies',
   'grade':'derived','depends_on':['C27.1','INHERITED_PHYS24_25_26'], 'evidence':['TH27.4','TH27.5','TH27.6','TH27.7','TH27.8']},
  {'id':'C27.3','claim':'Strict containment within original response interval at the same physical W',
   'grade':'derived','depends_on':['C27.1','C27.2','INHERITED_PHYS26_UNIQUE_ATOMIC_EXTREMES'],'evidence':['TH27.9']},
  {'id':'C27.4','claim':'Numerical endpoint signs and two finite Decimal root approximations',
   'grade':'numerically checked','depends_on':['FROZEN_NUMERICAL_PROTOCOL','FROZEN_J_AND_SOURCE'],
   'evidence':['contributions/numerics/FINITE_WIDTH_FIRST.json'],
   'limits':'No directed interval or physical uncertainty enclosure'},
  {'id':'C27.5','claim':'Two unique exact-root definitions, five sign regions and inward threshold directions',
   'grade':'derived conditional on numerically supported endpoint signs',
   'depends_on':['C27.2','C27.3','C27.4'],'evidence':['TH27.10','TH27.11','TH27.12','TH27.13']},
  {'id':'C27.6','claim':'Actual same-moment two-band positive/negative examples and zero-response convex construction',
   'grade':'derived and numerically checked with separate roles',
   'depends_on':['C27.2','C27.4'],'evidence':['TH27.7','FINITE_WIDTH_FIRST.physical_variance_cases[mixed_W19_74]','FINITE_WIDTH_FIRST.mixtures_at_W19_74']},
  {'id':'C27.7','claim':'Weak delta->0 optimizer convergence, response convergence and conditional root convergence',
   'grade':'derived','depends_on':['C27.2','INHERITED_PHYS26'],'evidence':['TH27.14','TH27.15']},
  {'id':'C27.8','claim':'First fixed program passes and its fresh-path replay reproduces bytes',
   'grade':'implementation-verified','depends_on':['C27.4'],
   'evidence':['contributions/numerics/EXECUTION.json','portability/REPLAY_RECEIPT.json'],
   'limits':'Replay gives no independent physics credit'},
 ],
 'not_claimed':['All continuous spectra','Positive-width nesting for arbitrary widths','First-order width coefficients',
    'J/atomic/gas uncertainty','Finite-time or finite-epsilon remainder','Native equivalence','Physical source admission','Novelty priority'],
 'generator_roles':['/root','/root/phys27_theory','/root/phys27_numerics'],
 'portability_operator':'/root/phys27_portability','context':'NONBLIND; no generator may issue final decision',
}
write('claims/CLAIM_DAG.json',claims)

report=r"""# PHYS27 — 유한 폭 스펙트럼의 정확한 응답 구간

**REI-PHYS27-20261011 · FINITE_WIDTH_RESPONSE_ENVELOPE · 2026-10-11**  
GPT-6 Astra · physmath research harness v4.0.0  
이론·첫 수치 실행·별도 경로 재현 완료. 최종 승격 권위는 [독립 판정](../independent/DECISION_REVIEW_KO.md)과 [판정 JSON](../independent/DECISION_REVIEW.json)에 있다. **Physical HOLD**를 유지한다.

## 1. 이번 루프가 답한 질문

PHYS26은 평균 18 eV와 에너지 분산을 고정한 모든 광자 수 확률측도에서 초기 HeIII 응답의 정확한 상한·하한을 구했다. 그 극값은 이상적인 델타 선 두 개가 달성했다. 이번에는 각 선을 **전체 폭 0.10 eV인 균일 대역**으로 바꾼 명시적 분포족에서 같은 질문을 풀었다. 광자 수, 평균 에너지, 실제 광자 분산을 그대로 비교하며 대역 중심 분산과 혼동하지 않는다.

반폭 δ=0.05 eV에서 두 물리 분산 문턱은 다음과 같다. 아래 숫자는 고정된 source-real 상수와 직렬화 수치 J에 대한 수치 근사다.

| 문턱의 의미 | PHYS26: 델타 선 허용 | PHYS27: 균일 대역족 | 이동량, eV² |
|---|---:|---:|---:|
| 비음수 응답을 내는 스펙트럼이 처음 존재 | 16.3399446546 | **16.6294590240** | **+0.289514369390** |
| 모든 허용 스펙트럼의 응답이 비음수 | 23.4202189924 | **23.3008661823** | **−0.119352810041** |

양·음 응답이 공존하는 분산 구간의 폭은 약 **7.08027433776 → 6.67140715833 eV²**로 줄었다. 감소량은 약 **0.408867179431 eV²**, 비율은 **@REDUCTION_PERCENT@%**다. 표의 모든 분산은 실제 광자 에너지 분산 W다. 중심 분산은 각각 W−1/1200 eV²다.

이동의 방향은 새 소수값의 비교에만 기대지 않는다. **같은 실제 분산에서 유한 폭 족의 모든 응답 구간이 PHYS26 구간의 엄격한 안쪽에 들어간다**는 전역 정리를 증명했다. 수치 계산은 두 문턱의 값·이동량과 구현을 확인한다. [전역 이론](../contributions/theory/FINITE_WIDTH_DERIVATION_KO.md), [수치 원자료](../contributions/numerics/FINITE_WIDTH_FIRST.json), [기계 판독 요약](PHYS27_RESULTS_SUMMARY.json).

![유한 대역 응답 구간과 같은 모멘트를 갖는 반대 부호 스펙트럼](../figures/PHYS27_FINITE_WIDTH_ENVELOPE.png)

그림의 회색은 PHYS26 전체 측도족, 파란 영역은 이번 균일 대역족의 달성 응답이다. 아래 두 밀도는 같은 W=19.74 eV²에서 각각 상한·하한을 달성한다. 대역 폭은 실제 축척으로 그렸다. 곡선 표시용 161점은 별도 binary64 계산이며 이론 증명이나 추가 수치 검증으로 세지 않는다.

## 2. 고정한 물리량과 해석 범위

원 지원구간은 [a,b]=[13.61,24.58] eV, 평균은 m=18 eV다. 각 대역을 잘라내거나 다시 정규화하지 않도록 중심 c를 [a+δ,b−δ]=[13.66,24.53] eV에 제한한다. 중심 분포 Q에는 원자점도 허용하지만, 실제 광자 측도는 다음 밀도를 가진다.

\[
p_\delta(E)=\frac1{2\delta}\int\mathbf1_{[c-\delta,c+\delta]}(E)\,dQ(c).
\]

이는 비음수이며 적분값이 1인 **광자 수** 확률밀도다. 0≤pδ≤1/(2δ)이고 지원은 [a,b] 안에 있다. 점프가 있는 밀도도 허용하므로 모든 매끄러운 스펙트럼을 전제하거나 대표하지 않는다. 같은 폭의 uniform convolution으로 표현되는 가족을 정확하게 지정한 것이다.

응답 A는 초기 전개의 **ε²t⁴ HeIII 계수**, 단위 s⁻⁴다. ε² 계수는 2차 ε 미분의 절반이고 시간 다항식 계수에 추가 factorial을 넣지 않는다. 시간은 gas-comoving proper seconds, metric은 (−,+,+,+), 열 변수 w는 eV/H다. 광자 초기 각분포는 상속된 등방 조건을 유지한다.

\[
A[p]=\int_a^b k(E)p(E)\,dE,
\quad k(E)=\frac{qN_0\kappa}{180}(D^2+3D)
\{\sigma(E)[J_x+J_w(E-\chi)]\},\quad D=E\partial_E.
\]

여기서 q=2 shear², κ=c_light nH(1−xHII)다. N0는 source binary64 0.05 photon/H의 정확 실수 해석이고 qN0/45는 k에 이미 포함되어 있다. HI 단면적과 source constants는 현재 저장소의 실제 pinned source에 묶었다. 결합에너지 χ=source f64(13.598434599702)는 opacity cutoff 13.60 eV와 구별한다. 지원구간은 HI와 HeI 문턱을 넘지 않는다.

J는 PHYS22의 직렬화 수치에서 실제 두 행렬 원소를 읽어 고정했다. J 원자료 SHA256은 `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79`다. 소스 리터럴을 정확 실수로 해석하는 수학적 계약이며 native floating-point 연산의 동일성을 주장하지 않는다. 원 J의 근사 오차, 원자 데이터와 기체 상태의 불확실성을 둘러싼 결과도 아니다. [계약](../PHYSICS_CONTRACT.json), [소스 연결](../SOURCE_MANIFEST.json), [수치 정규화 추적](../contributions/numerics/NUMERICS_NOTE_KO.md).

## 3. 중심 분산과 광자 분산을 구별해야 한다

균일 대역 내부 변위를 S∼Uniform[−δ,δ]라고 쓰면 E=C+S이고, 조건부 평균 변위는 0, 분산은 δ²/3이다. 따라서 직접 적분으로

\[
\int E p_\delta(E)dE=\int c\,dQ(c)=m,
\qquad
\boxed{W=V+\frac{\delta^2}{3}},
\]

\[
V=\int(c-m)^2dQ(c),\qquad
W=\int(E-m)^2p_\delta(E)dE.
\]

이 관계는 작은 폭 근사가 아니다. ℓ=m−(a+δ)=4.34, h=(b−δ)−m=6.53으로 두면

\[
\int(c-a-\delta)(b-\delta-c)dQ(c)=\ell h-V\ge0.
\]

전체 중심 분산 범위는 0≤V≤ℓh=28.3402 eV²이고 아래의 명시적 두 중심 측도가 모든 값을 달성한다. 실제 광자 분산의 필요충분 범위는

\[
\boxed{\frac1{1200}\le W\le\frac{850231}{30000}}
\quad({\rm eV}^2),
\]

즉 약 0.000833333333333≤W≤28.3410333333 eV²다. W=0은 이번 족에서 허용되지 않는다. 모든 후보는 총 광자 수 N0와 총 에너지 N0m를 보존한다. 유한 폭을 넣은 후 중심 분산 V를 그대로 W라고 부르면 서로 다른 모멘트를 비교하게 된다.

## 4. 모든 분산의 정확한 경계와 이를 달성하는 밀도

평균화 커널을

\[
f(c)=\bar k_\delta(c)=\frac1{2\delta}\int_{-\delta}^{\delta}k(c+s)ds
\]

로 정의한다. 상속된 닫힌 조건 k∈C³, k″>0, k‴<0를 동일 지원구간의 양의 평균에 통과시키면 f″>0, f‴<0가 성립한다. 또 Fubini에 의해 Aδ(Q)=∫f dQ다. 미분 연산자 D를 임의로 중심 변수의 c∂c로 바꿔 평균 단면적에 다시 적용하지 않는다.

α=a+δ, β=b−δ, V=W−δ²/3, v=m+V/ℓ, u=m−V/h로 쓰면 극값을 달성하는 중심 측도는

\[
Q^+_W=\frac{V}{\ell^2+V}\delta_\alpha+
\frac{\ell^2}{\ell^2+V}\delta_v,
\qquad
Q^-_W=\frac{h^2}{h^2+V}\delta_u+
\frac{V}{h^2+V}\delta_\beta.
\]

각 중심 원자를 동일 폭의 균일 대역으로 펼치면 실제 밀도 p⁺, p⁻가 된다. 따라서

\[
\boxed{A_{\delta,+}(W)=
\frac{Vf(\alpha)+\ell^2 f(m+V/\ell)}{\ell^2+V}},
\]

\[
\boxed{A_{\delta,-}(W)=
\frac{h^2 f(m-V/h)+Vf(\beta)}{h^2+V}}.
\]

각 허용 W에서 전체 달성 응답은 정확히 **[Aδ,−(W),Aδ,+(W)]**다. 상한·하한을 달성하는 중심 측도와 실제 밀도는 각각 유일하며 밀도 동등성은 거의 모든 곳에서 이해한다. 내부 응답은 두 극값 밀도의 볼록 혼합으로 모두 달성할 수 있다. 내부 응답의 표현까지 유일하다고 주장하지는 않는다.

전역 부등식은 두 접촉점을 갖는 이차 함수로 증명했다. 구체적으로

\[
R_s(c)=\int_0^1(1-t)f''(s+t(c-s))dt,
\quad \partial_c R_s(c)=\int_0^1t(1-t)f'''(s+t(c-s))dt<0
\]

이므로 v에서 접하고 α를 지나는 이차식은 f 전체를 위에서 지배하고, u에서 접하고 β를 지나는 이차식은 아래에서 지배한다. 질량·평균·분산을 고정하면 그 이차식의 기대값이 고정된다. 비음수 잔차의 영 집합이 바로 해당 두 중심점이므로 등호 조건과 유일성도 함께 따른다. 유한 격자의 최적화 결과를 전 구간으로 외삽한 주장이 아니다.

두 분산 끝점은 별도로 처리했다. V=0에서는 Q=δm이 강제되어 p(E)=1/(2δ)·1[m−δ,m+δ] 하나가 남는다. V=ℓh에서는 Q=h/(ℓ+h) δα+ℓ/(ℓ+h) δβ가 강제되어 양쪽 경계 대역 두 개만 남는다. 양 끝에서는 Aδ,−=Aδ,+이고, 내부에서만 Aδ,−<Aδ,+다.

두 경계는 실제 W에 대해 엄격히 증가한다. 미분하면 각각 Rv(α)>0, Ru(β)>0가 나온다. 여기에는 f″>0가 쓰이며 극값 접촉 방향을 정하는 f‴<0의 역할과 구별한다. 전체 증명은 [이론 §2–6](../contributions/theory/FINITE_WIDTH_DERIVATION_KO.md)에 있다.

## 5. 유한 폭이 문턱을 안쪽으로 이동시키는 이유

같은 실제 W에서 유한 대역 밀도는 PHYS26의 전체 허용 측도족에 속한다. 그러나 유한 대역 광자 측도는 절대연속이고, PHYS26 경계를 달성하는 유일 측도는 원자 두 개다. 따라서 어느 유한 대역 밀도도 그 원자 극값과 같을 수 없다.

새 족에서도 상한·하한은 실제로 달성되므로, 개별 밀도의 엄격 부등식이 두 극값에도 적용된다.

\[
\boxed{A_{0,-}(W)<A_{\delta,-}(W)
\le A_{\delta,+}(W)<A_{0,+}(W)}.
\]

이 부등식은 이번 허용 W 전부에서 성립하며 유한 폭 분산의 두 끝에서도 바깥 부등식은 엄격하다. 여기서 최대·최소의 **달성**을 사용했다는 점이 필요하다. 모든 개별 응답이 열린 구간에 든다는 사실만으로 일반적인 infimum·supremum의 엄격성을 자동 추론하지 않는다.

두 영점이 존재하려면 f(m)<0<Bδ(m)라는 끝값 부호가 추가로 필요하다. 곡률 부호만으로 이 사실을 결론내리지 않는다. 이번 이론은 PHYS26의 실제 원 결과에서 A0,+(8)<0, A0,−(26)>0라는 수치 지원을 명시적으로 상속하고, 단조성·엄격 포함과 Wmin<8<26<Wmax를 연결했다. 새 계산도 끝점 응답을 각각

\[
-1.18983092355\times10^{-64},\qquad
+4.67989940743\times10^{-65}\quad({\rm s}^{-4})
\]

로 확인했다. 따라서 정확근의 존재·분류는 **명시적으로 수치 지원을 받는 끝값 부호에 조건부**다. 이 끝값을 directed interval 인증으로 승격하지 않았다.

상단 영점 W*,δ에서는 A0,+(W*,δ)>0이고 하단 영점 W0,δ에서는 A0,−(W0,δ)<0다. 원 경계의 엄격 증가와 새 구간의 내부 간격을 합하면

\[
\boxed{V_{*,0}<W_{*,\delta}<W_{0,\delta}<W_{0,0}}
\]

를 얻는다. PHYS26의 V*,0는 δ=0에서의 실제 분산이다. 새 근을 기준으로 비교하므로 옛 근들이 새 허용 분산 안에 들어온다는 별도 가정도 필요 없다. 이 주장은 한 양의 폭과 δ=0의 비교이며, 서로 다른 임의의 양의 폭 두 개 사이의 족 포함이나 단조성을 증명한 것은 아니다.

## 6. 전체 부호 지도

아래 표의 문턱은 수치로 반올림한 숫자가 아니라 정확한 경계 함수의 유일한 영점으로 정의한다. 모두 허용 범위 W∈[1/1200,850231/30000] 안에서의 양화다.

| 실제 분산 W | 모든 허용 균일 대역 혼합에 대한 결론 |
|---|---|
| Wmin≤W<W*,δ | 모두 음수 |
| W=W*,δ | 모두 비양수; 영 응답은 상한 밀도 p⁺ 하나 |
| W*,δ<W<W0,δ | 음수·영·양수 모두 가능 |
| W=W0,δ | 모두 비음수; 영 응답은 하한 밀도 p⁻ 하나 |
| W0,δ<W≤Wmax | 모두 양수 |

따라서 비음수 응답이 **존재**하는 최소 분산은 W*,δ이고, **모든** 응답이 비음수인 최소 분산은 W0,δ다. 엄격 양수의 존재에는 W>W*,δ가, 모든 엄격 양수에는 W>W0,δ가 필요하다. 이 두 엄격 양수 분산 집합의 아래끝은 infimum이고 최소 원소는 없다. 영 응답이 가능한 분산 범위는 닫힌 구간 [W*,δ,W0,δ]다.

## 7. 같은 W=19.74에서 실제 대역을 구성했다

중심 분산은 V=19.74−1/1200 eV²다. 아래 대역은 각자 폭 0.10 eV이고 비율은 광자 수 확률이다. 밀도 높이는 해당 비율을 0.10 eV로 나눈 값이다.

| 달성 응답 | 첫 균일 대역, eV | 광자 비율 | 둘째 균일 대역, eV | 광자 비율 |
|---|---|---:|---|---:|
| 하한 | [14.9271567126,15.0271567126] | 0.683566117809 | [24.48,24.58] | 0.316433882191 |
| 상한 | [13.61,13.71] | 0.511711887650 | [22.4981950845,22.5981950845] | 0.488288112350 |

두 경우 모두 총 광자 수 N0, 평균 18 eV, 실제 분산 19.74 eV²다. 응답은

\[
A_{\delta,-}\simeq-2.69700289966\times10^{-65},\qquad
A_{\delta,+}\simeq+1.44841271009\times10^{-65}\quad({\rm s}^{-4})
\]

다. 평균·분산이 같아도 세부적인 에너지 배치가 초기 계수의 부호를 바꿀 수 있으며, 이 현상이 명시적인 유한 폭 분포에서도 남는다는 뜻이다.

상한 밀도에 θ=−Aδ,−/(Aδ,+−Aδ,−), 하한 밀도에 1−θ를 주면 영 응답을 구성한다. 수치값은 θ≈0.650598915418이며 실제 네 대역 혼합의 질량·평균·분산·총 에너지도 직접 적분했다. 대역 합으로 계산한 유한 Decimal 응답은 `0E-144`, 응답의 affine 합은 `2E-145`였다. 유한 산술의 0을 정확한 영 응답 증명으로 삼지 않는다. 정확한 경계값으로 정의한 혼합식이 정확한 영 응답을 보장한다.

## 8. 실제로 수행한 수치 검증과 재현

실행 전에 물리 계약·입력 identity·정밀도·노드 규칙·독립 비교·허용오차·표본 규칙·근 탐색 횟수를 동결했다. Python 3.12.14의 표준 라이브러리 Decimal 80자리를 사용했고 의존성을 설치하지 않았다. 첫 실행은 2026-10-11 04:29:55.585896–04:29:57.956443 UTC, 약 2.371초, exit 0이었다. 사전 지정 **405/405 검사 PASS**, 실패 0이다.

주 평균화는 Gauss–Legendre 16점이다. 다른 차수인 24점과 별도 scalar 원식에 의한 composite Simpson 32/64/128 panel 및 Richardson R8을 사전 선택한 7개 중심에서 비교했다. Gauss 노드는 Decimal polynomial recurrence와 Newton으로 계산했고 binary64 cosine은 시작값으로만 사용했다. 양의 근 20개와 Newton 반복 118회는 응답 근 두 개와 별도로 계수했다. GL16의 0–31차, GL24의 0–47차 전체 다항식 모멘트와 양의 가중치·지원·중복 없음도 확인했다.

| 검증 | 관측된 최대 정규화 차이 | 사전 허용오차 |
|---|---:|---:|
| GL16 대 GL24 | 4.50×10⁻⁷⁸ | 10⁻⁵⁵ |
| GL16 대 별도 scalar Simpson–Richardson R8 | 1.05046×10⁻²⁸ | 10⁻²² |

정규화 scale은 kbar에서 10⁻⁶⁴ s⁻⁴, kbar′에서 10⁻⁶⁴/18 s⁻⁴ eV⁻¹다. 원 Simpson 32→64→128의 오차는 모든 선택 중심과 두 함수에서 감소했다. 서로 다른 대수·적분 경로의 일치지만 원 HI fit, J와 일부 Decimal 연산을 공유한다. 독립 물리 데이터와의 대조는 아니다.

두 응답 근은 각각 80회 이분법으로 구했고 최종 실제 분산 bracket 폭은 약 2.34425×10⁻²³ eV²다. midpoint 응답 잔차는 상단 +1.41664×10⁻⁹⁰, 하단 +8.24347×10⁻⁸⁹ s⁻⁴로 남겼다. 이 bracket은 유한 quadrature 계산이 유지한 수치 bracket이며 정확 적분 근의 엄밀 enclosure가 아니다. 새 문턱은 최대 12 유효숫자로 제시하며 원 JSON의 긴 소수는 재현용이다.

Gauss exactness와 Simpson 방법은 [NIST DLMF §3.5](https://dlmf.nist.gov/3.5), [Hu의 Newton–Cotes 강의노트](https://math.ucla.edu/~njhu/notes/na/numint/newtoncotes/)에서 실제 읽은 해당 절과 연결했다. 이 문헌은 방법의 수학적 배경을 제공한다. 우리 커널의 고차 미분 remainder 상계를 새로 계산하지 않았으므로 위 일치를 문헌의 일반 오차식만으로 interval 인증으로 바꾸지 않는다. 실제 열람 범위는 [문헌 기록](../evidence/LITERATURE_SCOPE.json)에 있다.

| 실행 계수 | 첫 과학 실행 | 별도 경로 재현 |
|---|---:|---:|
| 새 PHYS27 main | 1 | 1 |
| 응답 근 탐색 | 2×80 반복 | 2×80 반복 |
| 주 Jet 커널 | 3020 | 3020 |
| 별도 scalar 커널 | 903 | 903 |
| 합계 커널 | 3923 | 3923 |
| 지정 W 표본 / 비교 중심 | 9 / 7 | 같은 9 / 7 |
| 과거 PHYS19–26 main·suite·근 탐색 | 0 | 0 |
| 새 도함수 부호 campaign / native / gas IVP | 0 / 0 / 0 | 0 / 0 / 0 |

첫 과학 main의 예산은 kernel 20000 이하였다. 별도 실행자는 새 프로그램의 입력 15개와 manifest를 새 경로에 복구하고 hash·size를 확인한 뒤 PHYS27을 정확히 한 번 재실행했다. **305521바이트 결과가 첫 JSON과 byte 및 parsed JSON 모두 일치**했다. 재현은 구현 재현성의 근거이며 독립 물리 evidence credit은 0이다. 실제 main 총 횟수는 2이고 그중 하나가 재현이다. [재현 영수증](../portability/REPLAY_RECEIPT.json), [재현 사용법](../portability/NOTE_KO.md).

표시용 곡선은 161개 W와 총 5508개 scalar kernel 값을 별도로 계산했다. 레이아웃 수정 시 이 캐시를 재사용하여 추가 커널 평가는 0이었다. 근 탐색과 도함수 인증도 추가하지 않았다. 그림은 실제로 열어 확인했다. [표시 기록](../figures/DISPLAY_RECEIPT.json).

## 9. 독립성, 실패 기록과 근거의 계층

이론 생성자, 수치 설계·실행자, 별도 재현 실행자, 최종 판정자를 분리했다. 모두 full-history 노출 여부를 기록하고 **NONBLIND**로 다룬다. 수치 설계자는 실행 전에 owner의 포함관계·문턱 이동 방향 제안을 읽었다. 이론 생성자는 새 PHYS27 수치 결과를 읽지 않고 정리를 마쳤다. 최종 판정자는 후보의 생성자나 검증 설계자가 아니며, 승격 범위와 남은 한계를 [판정문](../independent/DECISION_REVIEW_KO.md)에 남긴다. 각 역할의 실제 읽기 범위는 해당 PROVENANCE.json에 있다.

| 근거 등급 | 이번에 그 등급으로 주장하는 내용 |
|---|---|
| derived | 정확 모멘트, 전역 경계, 등호·퇴화, 같은 실제 W의 엄격 포함, 조건부 부호 지도·이동 방향, 약한 δ→0 극한 |
| numerically checked | 끝값 부호, 두 문턱의 소수와 이동량, 일곱 중심 적분 비교, 아홉 W와 구체적 대역 모멘트·응답 |
| implementation-verified | 사전 동결 identity, 실제 첫 실행, 새 경로의 byte 동일 재현, 최종 묶음의 identity 검증 |
| 미승격 | 물리 source admission, J·원자·기체 불확실성, finite-time/finite-ε remainder, native 동등성, 모든 연속 스펙트럼, 세계 최초성 |

첫 과학 실패·수치 실패·과학 코드 실행 후 수정·허용오차 변경은 모두 0이다. 출력 표시 절단, 잘못된 하네스 phase 경로, 선택 패키지 inventory의 mpmath 부재, 수치 결과를 읽는 후처리 스니펫의 괄호 오류, owner 보고서 생성기의 문자열 구분기호 오류는 별도 도구 사건으로 보존했다. 원 과학 입력·프로그램·첫 결과는 수정하지 않았다. 이전 PHYS26 ZIP은 실제 원본을 복구하고 payload 68개를 검증했으며 옛 과학을 실행하지 않았다. [회복 기록](../evidence/RECOVERY_INVENTORY.json), [owner 읽기 범위](../evidence/OWNER_CONSUMPTION.json), [주장 의존표](../claims/CLAIM_DAG.json).

저장소 intake의 실제 head는 `75fd81e9e63c442d6da5f95bd3a80bdec16a4c37`, 과학 source subtree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`였다. pinned source 7개의 blob·크기·mode가 그 최신 tree와 모두 일치했다. 최종 게시 head, 새 경로와 원래 경로 보존, 선택적 원격 readback 및 전달 상태는 hash cycle을 피한 별도 PHYS27_PUBLICATION_RECEIPT.json에 기록한다. 원격 전체 ZIP 복구를 새로 수행했다고 주장하지 않는다.

## 10. 물리적 의미와 다음 한 질문

이번 결과는 평균·분산만으로 정해지지 않는 초기 HeIII 계수의 부호가, 이상적인 선의 위치 조절뿐 아니라 명시적 유한 폭 대역의 배치에서도 달라질 수 있음을 보여 준다. 유한 폭 제약은 응답의 가능한 폭을 줄인다. 그 결과 비음수 응답을 처음 만들기는 더 큰 분산이 필요하고, 모든 응답을 비음수로 강제하는 데는 더 작은 분산이면 충분하다. 두 양화가 서로 다른 문턱을 갖는다는 구조가 남는다.

이 부호는 초기 ε²t⁴ 계수의 부호다. 유한 시간의 전체 HeIII 편차, 이온 분율 자체의 부호, 관측 가능한 우주 재이온화 history의 승인을 의미하지 않는다. **Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED**를 유지한다. 생산 source/default/runtime 변경은 0이다.

δ→0에서는 경계 응답과 극값 측도가 PHYS26로 수렴한다는 해석적 검사를 마쳤다. 원자 극한이므로 측도는 약하게 수렴하며 밀도 함수의 점별·L1 수렴을 주장하지 않는다. 그러나 문턱 이동의 첫 비영차 계수는 이번에 구하지 않았다.

다음 단일 질문은 **PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY**다. 실제 W를 기준으로 δ→0⁺의 두 문턱 이동계수를 도출하고, support 축소와 대역 평균화 중 어떤 항이 처음 작용하는지 분리하여 이번 δ=0.05 결과와 비교한다. 기존 근을 새로 탐색하거나 여러 폭을 훑지 않는 이론·제한된 도함수 평가 작업으로 제안했다. 구체적 계약은 [PHYS28 인수문](../next/PHYS28_NEXT_HANDOFF_KO.md)에 있고 **아직 실행하지 않았다**.
"""
report=report.replace('@REDUCTION_PERCENT@',format(percent,'.8f'))
(ROOT/'report/PHYS27_REPORT_KO.md').write_text(report)

handoff=r"""# PHYS28 다음 물리 연구 루프 — 작은 대역폭에서의 문턱 민감도

상태: **PROPOSED / NOT_RUN**. 이 문서는 PHYS27의 후속 한 질문이며 PHYS28 실행 증거가 아니다.

## 1. 다음에 답할 한 질문

**같은 실제 광자 분산 W를 기준으로 δ→0⁺에서 두 영점 W*,δ와 W0,δ의 일차 이동계수를 구하고, 대역 중심 지원구간의 축소와 균일 대역 평균화의 효과를 분리할 수 있는가? 그 국소식은 PHYS27의 δ=0.05 이동량을 어느 정도 설명하는가?**

명칭: PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY. 이 질문 이외의 신규 native solver, gas IVP, 폭·평균·J parameter campaign으로 확대하지 않는다. 두 이동계수가 0일 가능성도 사전 배제하지 않고 실제 유도에서 판정한다.

## 2. 실제 완료한 PHYS27에서 시작

PHYS27은 평균18, 광자 지원[13.61,24.58], 반폭δ0.05인 균일 대역혼합에서 전역 sharp interval, 유일 극값과 끝점, 같은 실제 W에서의 엄격 포함을 유도했다. 수치 지원 끝값 부호에 조건부로 두 영점과 전체 부호 지도를 정리했다.

- Wmin=δ²/3=1/1200; Wmax=(4.39−δ)(6.58−δ)+δ²/3=850231/30000 eV².
- W*,δ≈16.6294590240, W0,δ≈23.3008661823 eV².
- PHYS26 대비 +0.289514369390, −0.119352810041 eV².
- 첫 Decimal80 실행405/405 PASS, root2개×80회, kernel3923회. 새 경로 재현1회 결과 byte 동일. 재현의 독립 물리 credit0.
- 현재 새 code·J·first result identity는 아래와 같다. 전체 원리와 실제 승인 범위는 PHYS27 보고서·판정 파일에서 소비한다.

| 입력 | SHA256 |
|---|---|
| PHYS27 PHYSICS_CONTRACT.json | 46fe6fb98a78ca549f27ed78968850c14bdc12cdd3250892f28e239574005443 |
| PHYS27 새 numerical code | b2eeed5377f46ca1327672991ef9b9f9ebda93696e2c107df3f258a2d98cdd58 |
| PHYS27 FINITE_WIDTH_FIRST.json | 3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314 |
| PHYS22 J 원자료 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |

최종 원본 ZIP·승격·게시 commit identity는 **분리된 PHYS27_PUBLICATION_RECEIPT.json**에서 읽는다. 동봉한 `independent/DECISION_REVIEW.json`의 실제 decision 및 조건을 소비한다. 본 인수문 작성 시 그 최종 판정을 선제 주장하지 않는다. intake source subtree는 cb69b4736dd046e4675557577eb8e0ead037d1f3이며 새 세션에서는 최신 actual head/source와 대조한다.

## 3. 해석적 작업의 계약

δ는 0≤δ<min(L,H), L=4.39, H=6.58에서의 국소 변수다. 광자 분산 W와 중심 분산 V=W−δ²/3를 엄격히 구별한다. fδ(c)=균일평균 k(c+s), α=a+δ, β=b−δ, ℓ=L−δ, h=H−δ를 모두 함께 미분한다.

PHYS27의 경계식과 exact-root 정의를 출발점으로 삼는다. PHYS26의 두 단순근과 양의 ∂W A0,±를 소비하여 implicit-function 조건과 단위부터 확인한다. fδ의 δ=0 우미분, 움직이는 지원 endpoint·이동 중심·확률의 항을 명시적으로 추적한다. 정확식의 미분과 수치 저장근에서 평가한 근사값을 구별한다. PHYS27에서 증명한 평균화 O(δ²)와 약한 극한은 재유도 캠페인 없이 소비해도 된다.

목표 산출물은 W*,δ=V*,0+c*δ+o(δ), W0,δ=W0,0+c0δ+o(δ)의 정당한 국소식과 c의 단위·부호·해석이다. 더 강한 remainder를 주장하려면 필요한 정칙성과 실제 상계를 따로 제시한다. δ=.05의 선형 예측 잔차를 기존 원값과 비교하는 것은 허용하지만 한 폭의 잔차를 수렴률 인증이나 유효 폭 전체의 단조성으로 승격하지 않는다. 다른 두 양의 폭의 분포족이 서로 포함된다고 가정하지 않는다.

## 4. 제한된 새 계산을 쓸 경우

실행 전에 새 계약·직렬화 입력·정밀도·대수 경로·허용오차를 동결한다. PHYS26/27의 저장된 원 근과 source-real constants 및 J를 그대로 사용한다.

- 새 과학 main 최대1회, **새 물리 근 탐색0회**.
- 이전 PHYS19–27 main/suite/root 재실행0회. 실제 읽은 순수 수식을 명시적으로 적응하는 것은 가능하며 old module main을 호출하지 않는다.
- 새 커널/도함수 평가 최대24개, 새 width root sweep0회. 필요 수치비교는 같은 고정 노드에서 다른 대수 표현으로 제한한다.
- PHYS24/25 k″·k‴ 부호 certificate campaign0회, native0회, gas IVP0회, dense LP0회.
- PHYS27 δ=.05 비교값은 원 JSON에서 읽고 재계산하지 않는다.
- 새 프로그램을 만들었다면 portable bundle의 별도 경로 replay1회만 허용하며 독립 물리 credit0으로 계수한다.
- 첫 실패를 보존한다. 사후 허용오차 완화나 root/width 추가로 원하는 부호를 만드는 실행을 하지 않는다. 새로운 필요가 드러나면 주장 범위를 줄이고 이유를 기록한다.

전역 곡률·모멘트 정리, 옛 스펙트럼 감사를 반복하지 않는다. 동결 입력의 값과 의미가 맞는지 선택적으로 확인하고 이번 미분 문제를 해결한다.

## 5. 종료 기준과 증거

정확 국소 미분식·가정·동일 물리 W의 처리, 첫 수치 결과가 있다면 원 stdout/stderr/exit와 모든 실제 횟수, 비례 상수와 실제 δ=.05 관측의 연결, 의미 있는 한계, distinct NONBLIND 최종 판정, 재현가능 묶음과 다음 한 질문을 남긴다. 생성자·수치 검증 설계자는 최종 승격을 판정하지 않는다. 하네스는 실제 채택 모델의 router로 읽고 템플릿 상태를 실행 근거로 쓰지 않는다.

## 6. 기존 권한과 보호 상태

사용자의 다음 물리 연구 루프 요청 및 기존 세션의 같은 branch additive docs 게시 권한을 유지한다. `cosmosapjw-quantum/rei_bianchi`, branch `forward/rust-reion-kernels-20260922`, PR83 draft를 사용하고 새 PHYS28 문서 prefix에만 추가한다. 최신 head를 읽고 expected-head nonforce CAS, 기존 경로·source subtree 보존과 선택 readback을 수행한다. merge, production source/default/runtime 변경, 타인에게 메시지 전송 권한은 포함하지 않는다. 게시 영수증은 hash cycle을 피하여 분리한다. 원격 ZIP 전체 복구를 다시 실행할 필요는 없다.

이 채팅은 fastest-track 이론·가벼운 수치 lane이다. BASS_HE/bass_cr/WU088_HH의 별도 atomic lane을 활성화하지 않는다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED**를 유지한다. 초기 ε²t⁴ 계수의 구조 연구와 실제 emitter·우주론 history admission을 분리한다.
"""
(ROOT/'next/PHYS28_NEXT_HANDOFF_KO.md').write_text(handoff)
print(json.dumps({'written':['report/PHYS27_REPORT_KO.md','report/PHYS27_RESULTS_SUMMARY.json',
                            'claims/CLAIM_DAG.json','next/PHYS28_NEXT_HANDOFF_KO.md'],
                  'coexistence_reduction_percent':str(percent),'new_science':0}))
