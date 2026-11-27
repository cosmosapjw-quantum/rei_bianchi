from __future__ import annotations
import json,hashlib
from pathlib import Path
from fractions import Fraction as F
W=Path(__file__).resolve().parents[1]
parent='11b3cfdb987137323d8ebd220e74063b0ed6db22'
source={'repository':'IAEA-NDS/exfor_master','commit':'939a14d7bba1ddce51975cb5e8711ce96b3b0871','path':'exforall/M04/M0475.x4','previous_sha256':'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f','git_blob':'c49433293921dbb012d7f1b0387745732a598efa','identity_status':'pinned GitHub source / parent transcript, no fresh local EXFOR raw bytes'}
D={'central':'28/88','HE':'14/18','PR105':'2/2','PR106':'1/2','reciprocity':'1/2','birth_ledger':'1/2','PR109_angular':'1/2','new_certified_FE':'1/2_SCOPED_CONDITIONAL_ONLY','physical_delta':0}
gates={'kappa':None,'R_event':None,'heat_rate':None,'physical_activation':False,'L4':False,'production':'HOLD'}
vals={}
for L in ['1/700','1/200','1/100']:
    r=json.loads((W/'evidence'/f'EXTREMA_CERT_L_{L.replace("/","_")}.json').read_text())
    r['numerical_brackets']={k:float(F(v)) for k,v in r.items() if k.startswith(('min_b_','max_b_'))}
    vals[L]=r
M=F('3727.3794118');m=F('1875.61294500');E=F(330);s=M*M+2*M*E
D2=E*E*(s-4*m*m)/(4*s)
result={'schema':'BASS_HE_DD_LIPSCHITZ_DUAL_FE_SCOPED_RESULT_V1','date':'2026-10-29',
'parent':{'repo':'cosmosapjw-quantum/BASS_HE','pr':109,'head':parent},'source':source,
'math':{'b':'(integral sin(theta)cos²(theta)f)/(integral sin(theta)f)','metric':'(-,+,+,+)','M_alpha_c2_MeV':'3727.3794118','m_deuteron_c2_MeV':'1875.61294500','delta2_MeV2':str(D2),'h_degree':'1/50','nodes':4501,'experimental_L_measured':False,'interval_type':'conditional continuum extrema brackets, not statistical intervals','numerical_certification':'exact Fraction dual and algebraic continuum/Taylor/Machin error'},
'cases':{L:{k:r[k] for k in ('L','h','grid_nodes','min_b_outer_low','min_b_inner_high','max_b_inner_low','max_b_outer_high','final_dual_residual','total_continuum_error','certified')} for L,r in vals.items()},
'validation':{'current_python':'17/17 PASS','Cxx_compiler':'g++ 14.2 installed','SciPy_LP':'HiGHS numerical candidate only, bound verified using exact dual residual','Wolfram':'3/3 exact zero identities','previous_science_suite':'NOT_RUN','previous_IVPs':'NOT_RUN','native_distinct_author_R6_C9':'NOT_RUN'},
'DAG':D,'gate':gates}
(W/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
contract={'schema':'BASS_HE_DD_DUAL_FE_CERTIFICATE_CONTRACT_V1','base_sha':parent,'source':source,'environment':{'python':'3.13.5','compiled_native_independent_reviewer':'NOT_RUN'},'input':{'gamma_E_MeV':'330','angle_degree':'[0,90]','source_rows':[{'angle_deg':theta,'da_lower':str(lo),'da_upper':str(hi)} for theta,lo,hi in ((46,F('0.11'),F('0.17')),(61,F('0.11'),F('0.21')),(73,F('0.02'),F('0.12')),(87,F('0.14'),F('0.24')))],'L':'[1/700,infinity) nb/(sr degree)','target_L':['1/700','1/200','1/100'],'grid_h_deg':'1/50','event_normalization':None,'beam_polarization':None},'equations':{'g_t':'(1/4-t)sin(pi theta/180)+(1/4)sin(3pi theta/180)','Dmin':'integral f_minus*(theta/90)dtheta','interpolation_error':'45 L h in degree-integral units','quadrature_error':'90 B (3*(22/(7*180))^2) h²/8','trigonometric_error':'90 B epsilon+90 L h² epsilon/12; epsilon=1e-8','dual_upper':'b dot lambda+B sum(nu)+B sum max(0,c-A^Tlambda-nu)','extremal_bounds':'outer_min<=min b<=verified_min_witness_upper; verified_max_witness_lower<=max b<=outer_max'},'algorithm':{'source':'src/lipschitz_lp_certificate.py','targeted_tests':'tests/test_lipschitz_lp_certificate.py','data':'RESULTS.json','figures':['figures/certified_extrema.png','figures/continuum_budget.png'],'rounding':'directed Decimal polynomial enclosure and rational Taylor/Machin budgets, exact rational LP dual postcheck','LP':'SciPy HiGHS, not trusted as certifier','dual_residual':'exact Fraction computed from numeric proposal','feasible_witness':'rational McShane envelope plus f_minus/f_plus clipping'},'admission':{'theorem':'DERIVED_NUMERICALLY_CHECKED_SCOPED','physical_rate':'BLOCKED_SOURCE_MISSING','native_R6_C9':'NOT_RUN','old_science_suite':'NOT_RUN'},'DAG':D,'gates':gates}
(W/'IMPLEMENTATION_CONTRACT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
survey={'asof':'2026-10-29 ~18:39 KST','scope':'GitHub newest PR metadata and selected report content; Google Drive and Dropbox prior stage logs readback; local previous source ZIP manifest 16/16 PASS; personal conversation context. No all-local-private-source absence proof.',
'current_BASS_HE':{'pr':109,'sha':parent,'draft':True},
'foreign':[
{'repo':'BASS','pr':251,'sha':'cd7e7efdb384580ae44c0cdca873eba018a404e2','import':'no: CE1-J/CE1-K/CE1-L residual/pressure, not nuclear rate'},
{'repo':'bass_cr','pr':123,'sha':'9f520c5e4042cb15bbd55da14ef946d6d9960d97','import':'no: conditional He atomic K3 exact flow, not 4He photodisintegration'},
{'repo':'rei_bianchi','pr':265,'sha':'9b0b97aadeebf368802f865c10eb8b633f2726e4','import':'no: source-isotope mismatch/photo lump, not MeV photon field'},
{'repo':'rec_bianchi','pr':156,'sha':'8806a4f757d916b6cf040625be931a66e2f0f6fe','import':'no: HD rotational line energy ledger'},
{'repo':'WU088_HH','pr':161,'sha':'4a9cc6f701aacbb8d09bbf4a169d5edd4c4fed47','import':'no: H+HD spectroscopic Q is not physical D_fast stopping'},
{'repo':'vigilode','pr':110,'sha':'c15c34d52f09689bd37400443c1f7e328fc51729','import':'method only: GMRES trigger not source'},
{'repo':'vigilode','pr':111,'sha':'23571352200b3919a008327c294dc3bc0f371156','import':'method only: original residual, no physical client'}],
'literature':[{'title':'Arends et al 1976 4He(gamma,d)d','DOI':'10.1016/0370-2693(76)90671-7','full_detector_data':'UNRESOLVED'}, {'title':'Silverman et al 1984 dd->4He gamma','DOI':'10.1103/PhysRevC.29.35','same_s_330':'UNRESOLVED'}, {'title':'Neuenhofen & Kerrigan 2018 direct transcription','link':'https://arxiv.org/abs/1810.04059','role':'method background, not physical result'}, {'title':'Review of rigorous LP optima bounds 2017','DOI':'10.1007/s10898-016-0489-2','role':'method background'}],
'next_physical':'original experiment calibration + event rate + gamma history and target frame + named fast-D stopping, prior hold remains.'}
(W/'SURVEY.json').write_text(json.dumps(survey,ensure_ascii=False,indent=2)+'\n')
rows=[]
for L,r in vals.items():
 lo=float(F(r['min_b_outer_low']));mi=float(F(r['min_b_inner_high']));ma=float(F(r['max_b_inner_low']));hi=float(F(r['max_b_outer_high']))
 rows.append((L,lo,mi,ma,hi,float(D2*F(r['min_b_outer_low'])),float(D2*F(r['max_b_outer_high']))))
table='\n'.join('| {} | [{:.10f},{:.10f}] | [{:.10f},{:.10f}] | [{:.5f},{:.5f}] |'.format(*r) for r in rows)
report='''# BASS_HE HE-DD dual finite-element continuum bracket: 연구 및 코딩 보고서

2026-10-29 · 기준 BASS_HE PR#109 `{parent}` · 별도 add-only 연구 노드.

## 결론

기존 PR109의 PR105 EXFOR source-conditional nonnegative L-Lipschitz family를 그대로 보존하되, sign-split outer의 비최적성을 보완하였다. Finite-grid LP와 **exact rational post-dual** + Lipschitz continuum interpolation + midpoint-derivative quadrature + Machin/Taylor trigonometric error를 결합하여 b=⟨cos²θ⟩의 두 극값을 각각 외측·내측으로 가두었다. 단순 HiGHS 최적값은 증명으로 사용하지 않았고, 원본 source ERR-S도 joint CI로 승격하지 않았다.

| L [nb/(sr degree)] | min b bracket | max b bracket | Var(K_D) outer [MeV²] |
|---|---|---|---|
{table}

격자 h=0.02°, 4501 knots. 숫자는 표시 반올림, 실제 Fraction 원장/쌍대 잔차와 계산식은 `evidence/EXTREMA_CERT_L_*.json`, `src/lipschitz_lp_certificate.py`, `THEORY_KO.md`에 있음. Source-frozen Δ²(330)={delta} MeV². 특히 L=1/700에서 새 형식의 b 전체 외측 [0.2800766324,0.3797024351]은 이전 PR109 numerical outer [0.279238681235,0.386397436244]보다 양끝이 강하다. 다른 L에서는 새 위쪽 경계가 강하지만 아래쪽 경계가 모두 강하다고 과장하지 않는다.

## 수학적·수치적 자격

- T1: nodal Lipschitz finite-element subset와 원래 연속 f 사이의 O(Lh) 직접 부등식.
- T2: sin(z)cos²(z)=¼(sin z+sin 3z), degree-trigonometric second-derivative envelope, rational Taylor/Machin/Decimal enclosure.
- T3: numerical LP dual candidate를 exact Fraction으로 재구성하여 A^T dual 오차를 양의 부분으로 보정하는 우변 증명.
- T4: raw LP primal을 rational McShane L-hull과 EXFOR f±에 clamp하여 실제 feasible witness를 구성; certified quadrature interval로 extrema 내측 증명.
- 실제 테스트: Python3.13.5 17/17 PASS; SciPy HiGHS only proposal; Wolfram exact identities {{0,0,0}}; 차원·정규화·소스조건 검사. 이전 완료된 IVP/science suite 재실행 없음. Native distinct-author R6/C9는 현 기능에 없음(NOT_RUN). Numerics produced inside this current turn; exact Fraction certificate objects are preserved.

## 실험·물리적 한계

Arends1976과 Silverman1984의 원문 detector efficiency/acceptance, coincidence와 event/particle DA 정의, beam polarization, same-s measured inverse numerical DA는 수용되지 않았다. Source 330 MeV photon history/target proper frame, 실제 σ_event, nonthermal D_fast stopping/redistribution/deposition, C_V도 없다. 1/700, 1/200, 1/100은 실험적 각도-L 측정이 아니라 임의 선언한 함수족이다. Constant κ는 normalized b에서 소거되나 angular-dependent detector acceptance는 소거되지 않는다. 이 결과는 **수학적 조건부 바운드**이지 측정된 variance, 물질 가열 또는 event rate가 아니다.

`kappa=null`, `R_event=null`, `heat_rate=null`, `physical_activation=false`, `L4=false`, `production=HOLD`.

## DAG 및 작업 게이트

Central 28/88, HE14/18, PR105 2/2, PR106 1/2, reciprocity 1/2, birth ledger 1/2, PR109 angular 1/2 모두 변동 없음. 신규 mathematical dual-FE 국소 1/2 (scoped certificate only), 물리 증분 0. 연구 R1–R5,R7–R10은 완료 9/10이며 R6 독립 비저자 심사 미완료; 코딩 C1–C8,C10 완료 9/10, C9 독립 비저자 심사 미완료. 각 단계의 실제 Git SHA와 Drive/Dropbox ACK는 `STAGE_LEDGER.json`, 최종 원격 결과는 `DELIVERY_RECEIPT.md`가 SSOT이다.

## 후속 물리 단계

새 규칙을 생산 rate로 붙이지 말고 먼저 Arends/Silverman 원전의 detector/polarization source semantics를 확보한다. 같은 불변량의 measured inverse DA와 330-MeV exclusive event σ를 결속한 다음 고에너지 photon phase-space/He target frame, D_fast stopping/deposition/C_V를 source-qualify한다. 별개 이론 확장은 exact continuum optimal-control solution 또는 더 좁은 interval adaptive FE; 이번 노드의 물리 gate를 열었다는 주장은 하지 않는다.
'''.format(parent=parent,table=table,delta=float(D2))
(W/'REPORT_KO.md').write_text(report)
handoff=f'''# 다음 대화용 BASS_HE handoff

$physmath-research-loop $scispace $exa $wolfram

```text
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=109
PARENT_HEAD={parent}
NEW_BRANCH=research/he-dd-lipschitz-dual-fem-20261029
NEW_HEAD=READ_ACTUAL_REMOTE_PR_AND_SHA
ROOT=research/he_dd_lipschitz_dual_fem_20261029
READ=ROOT/THEORY_KO.md;ROOT/REPORT_KO.md;ROOT/IMPLEMENTATION_CONTRACT.json;ROOT/RESULTS.json;ROOT/STAGE_LEDGER.json;ROOT/DELIVERY_RECEIPT.md;ROOT/HANDOFF_NEXT_THREAD_KO.md
CENTRAL_DAG=28/88
HE_DAG=14/18
PR105_DAG=2/2
PR106_DAG=1/2
RECIPROCITY_DAG=1/2
BIRTH_LEDGER_DAG=1/2
PR109_ANGULAR_DAG=1/2
NEW_DUAL_FEM_DAG=1/2_SCOPED_CONDITIONAL
PHYSICAL_DELTA=0
NATIVE_INDEPENDENT_R6_C9=NOT_RUN
kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

수학적 핵심: PR109 330MeV DA source box, L>=1/700 nb/(sr deg), exchange symmetry 및 azimuth average라는 선언된 함수족에서만 정규화 b=⟨cos²θ⟩의 극값을 인증한다. 격자 h=0.02deg, exact Fraction LP dual postcheck + analytic continuum interpolation bound + Machin/Taylor interval trig + rational feasible McShane witness. 대표 L=1/700: min b in [0.2800766324,0.2803338733], max b in [0.3794460960,0.3797024351]. No physical rate/heat claim. 원본 source 3349-byte EXFOR은 출처 Git blob, 이번 파일은 이전 frozen transcript로 사용; source full text와 beam polarization은 아직 blocker다.

다음: (1) 원본 Arends1976/Silverman1984 full detector efficiency/coincidence/event counting/angular polarization/DA normalization source-lock, (2) 동일 s inverse DA와 330MeV total exclusive event source, (3) actual photon history + He target frame, (4) named D_fast stopping/redistribution/deposition/Cv, (5) 필요시 별도 nonauthor R6/C9. 기존 IVP/old science suite/closed campaigns 재실행 금지, no merge/force push. 매 단계 Git SHA와 Google Drive/Dropbox 실제 ACK 기입, raw restored binary hash와 log ACK 구별.
'''
(W/'HANDOFF_NEXT_THREAD_KO.md').write_text(handoff)
print('GENERATED',[(p.name,p.stat().st_size) for p in (W/'REPORT_KO.md',W/'THEORY_KO.md',W/'IMPLEMENTATION_CONTRACT.json',W/'RESULTS.json',W/'SURVEY.json',W/'HANDOFF_NEXT_THREAD_KO.md')])
