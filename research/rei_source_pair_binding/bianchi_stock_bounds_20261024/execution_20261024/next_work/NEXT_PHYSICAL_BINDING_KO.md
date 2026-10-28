# 다음 실제 cohort: 물리 입력 결속 메모

**현재 work 실행·게시를 차단하지 않는 후속 인계다. 새 물리 선택·science/test/CAS·review gate 추가는 0이다.**

HI의 채택 범위는 **z=2.479의 elemental ground-state HI summary consumer**다. Bath-rest target·zero recoil·선언된 isotropic source·진폭 a=1·no-deposition을 유지한다. A는 target당 s⁻¹, B/P/K는 eV·target⁻¹·s⁻¹이다. Stock/work는 주어진 양의 모멘트와 외부 geometry의 조건부 경계를 제공하며, 이 한 점을 시간 이력이나 초기 재고로 확장하지 않는다.

## 다음 단일 행동: 실제 입력의 값·단위·출처를 아래 표에 선언

| 선언 필드 | 이미 있는 것 / 실제 미결 입력 |
|---|---|
| `t0,t1,z(t); source(t)` | 고정 source card 한 점만 있음. 주입을 적분할 경우 A/B/P/K의 실제 시간 이력·적분 가능 범위와 출처가 미결; 상수 연장·보간을 가정하지 않음. |
| `n_HI(t),n_ref(t),X_HI(t)` | per-target→per-Href 규칙은 있음. 물리 부피당 target 밀도와 단위(cm⁻³ 또는 m⁻³), Href 기준 재고·밀도 연결은 미결. |
| `nu0` 또는 `N0,U0,L0` | 실제 초기 재고·epoch·단위·출처가 미결. 초기값 0을 자동 선택하지 않음. 구간만 계산하면 모멘트가 충분하나 실제 tensor에는 분포/각정보가 더 필요. |
| `frame,clock,a_i(t),H_i(t)` | HI bath frame과 proper-second convention은 있음. Cohort의 comoving 물리틀과 일치 여부, 시간 구간의 scale factor/ratio와 work rate가 미결; boost·배경을 생성하지 않음. |
| `mu_t(k,Omega),L(t)` | 현재 k=E−χ, χ=13.6 eV, 광자 support 13.6–50000 eV. 독립 반올림 summary의 공통측도·원자별/각분포 결속은 미검증. 사용할 모멘트·측도·각모델의 출처를 선언; isotropic 제한에서는 자유각분포 sharpness를 이전하지 않음. |
| `transport,collision,photon_supply` | 현재 no-deposition에서 physical secondary heat는 null. 실제 구간에 collisionless 자유수송을 적용할지, stopping/열화·secondary 채널을 선택할지 미결. 반복 주입에는 외부 유지 광자장인지 유한 재고·보충인지도 선언해야 함. |

## 조건부 연결식과 소유권

양의 per-target 일차전자 측도 \(\mu_t\)가 공급되고 \(\int d\mu_t=A(t),\ \int k\,d\mu_t=K(t)\)이면

\[
I_t=a\,n_{\rm HI}\mu_t,\qquad Q_N=a n_{\rm HI}A,\qquad Q_U=a n_{\rm HI}K.
\]

\(Q_N\)은 number/(physical-volume·proper-second), \(Q_U\)는 eV/(physical-volume·proper-second)다. Href route는 \(n_{\rm ref}(aX_{\rm HI})=a n_{\rm HI}\)를 **한 번만** 적용한다. SI를 쓰면 부피와 eV→J 변환도 각각 한 번이다. 에너지 소유자 순서는 기존 그대로 \(a n_{\rm HI}(0,B,-P,0,0,K)\); 입자 source는 \(Q_N(-1,+1,+1,0,-1)\)을 HI/HII/e_nt/e_th/광자에 준다. **K는 primary_nonthermal의 kinetic energy이며 thermal heat가 아니다.** 정지질량을 새 에너지원으로 더하거나 e_nt를 thermal heat capacity에 즉시 넣지 않는다. 선택 모델의 thermal source 0과 physical secondary_heat=null을 구별한다.

기존 자유수송 관계를 쓸 수 있는 조건에서 \(T_{t,s}p=\mathrm{diag}[a_i(s)/a_i(t)]p\), \(D(t,s)=\prod_i a_i(s)/a_i(t)\)이며,

\[
\nu_t=D(t,t_0)(T_{t,t_0})_*\nu_0
+\int_{t_0}^{t}D(t,s)(T_{t,s})_*I_s\,ds,
\qquad
\dot N+\theta N=Q_N,\quad\dot U+\theta U+\mathrm{tr}(H\mathsf P)=Q_U.
\]

\(\mathsf P\)는 stress tensor다. Source-free cohort는 **그 구간에 주입이 없다고 선언한 경우에만** 적분항과 Q가 0이다. 양의 주입은 관련 수·에너지 모멘트가 시간 적분 가능할 때 cohort별 경계를 합성한다. A/K 두 summary만으로 실제 \(\mu_t\), 주입 지속시간, thermalization 또는 온도를 정하지 않는다.

## 그대로 유지할 기준과 후속 상태

Source pin·범위·정규화, 표현된 \(r_B=B-\chi A\), \(r_E=B+K-P\)와 null을 보존한다. B/P/K 재구성이나 잔차의 임의 owner 배분은 하지 않는다. L1 source-consistency 허용기준은 **NOT_EVALUATED_NO_FROZEN_CRITERION**이며 기존 2e−12 gate는 원래 범위에서 유지한다. 다음 실제 cohort의 executor·명령·case·CPU/wall·호출 수는 **NOT_FROZEN**이고 기존 미사용 예산을 이전하지 않는다. 완료 시험은 replay 0; ANGTHERM02 `8d10231b…` 예약은 READ_ONLY다. **전체 L1/L4/모델 완료율=null, L4_ready=false.**

근거 재사용: [HI 채택](sandbox:/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/work/research/rei_source_pair_binding/hi_primary_20261024/ADMISSION.json), [HI 계약](sandbox:/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/work/research/rei_source_pair_binding/hi_primary_20261024/authority/IMPLEMENTATION_CONTRACT.json), [HI 이론 §§2–4](sandbox:/workspace/scratch/03a65a604d4c/rei_l1_execute_20261024/work/research/rei_source_pair_binding/hi_primary_20261024/authority/THEORY_L1_KO.md), [stock 이론 §§1·2·7](sandbox:/workspace/scratch/03a65a604d4c/rei_stock_execute_20261024/work/research/rei_source_pair_binding/bianchi_stock_bounds_20261024/authority/THEORY_KO.md), [work 이론 §§1·5·7](sandbox:/workspace/scratch/03a65a604d4c/rei_stock_execute_20261024/next_work/THEORY_KO.md).
