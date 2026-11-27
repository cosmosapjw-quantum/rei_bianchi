# BASS_HE TANGENT13 — full nonnegative quartic aperture 최소값의 엄밀한 구간

## 결과

258 MeV EXFOR 자료의 고정된 네 민감도 창에서, free endpoints를 가진 full nonnegative even-quartic angular family에 대한 두 same-event aperture의 **전역 최소값을 엄밀히 감쌌다**. 채택 대상은 `ACCEPT_SCOPED_FULL_QUARTIC_MINIMUM_REFERENCE`다. 실제 1회 construction, exact certificate reader와 8개 검증이 성공했다. 최종 nonauthor admission과 게시·전달 상태는 각각 review와 외부 최종 권위 문서로 확정한다.

| Aperture | QUARTIC12 최소값 구간의 기존 표시 | TANGENT13의 바깥쪽 십진 표시 | 새 exact fraction 폭(근삿값) |
|---|---|---|---:|
| HEMISPHERES | [0.6183761009029307, 0.6185538316867235] | **[0.6184085476376238, 0.6184085476376327]** | 8.794662532001996e-15 |
| CAPS | [0.060675724442147666, 0.06112027086968309] | **[0.0607568813452193, 0.0607568813452364]** | 1.6987466706439967e-14 |

새 구간 각각은 기존 정확한 구간에 포함되고 사전 목표 폭 `1e-10`을 만족한다. 이는 해당 family에서 허용되는 aperture fraction들의 전체 범위가 아니라, 그 family의 **최소값 하나를 감싸는 계산 구간**이다. 최대값, 다른 에너지, endpoint-zero 조건은 이번에 다시 계산하지 않았다.

## 출발점과 조사 결과

사용자가 준 EXFOR11 종료 기록을 보존하면서 최신 접근 가능한 자료를 조사하니 QUARTIC12가 이미 COMPLETE_SCOPED였다. 따라서 EXFOR11을 반복하지 않고 QUARTIC12의 full nonnegative even-quartic 최소값에 남은 inner/outer N16 간격을 다음 연구 대상으로 골랐다. Source S10 `4c71acfa2b8721a0d0b8f9cec8814f75f1c55739`와 tree `08e11c808d86cdf2a00ceb9feb3de43fc1bf3089`, 최종 패키지 SHA256 `d4b9fa00d2af2597c5574b7608eb602edb02d74761aa3526d3f8f3c7e4643219`를 읽었고 복원한 repository 파일 65개의 Git blob identity가 일치했다.

관련 7개 repository의 1444 heads/18 terminal pages, 최근 Library 1843 metadata/10 terminal pages, Dropbox dossier 5300 entries/9 terminal pages 및 BASS_BACKUPS 331 entries/1 terminal page를 조사했다. Drive의 이번 조회는 927 document metadata/10 terminal pages와 별도 archive 조회로 구성된다. Drive 전체와 전체 private chat의 완전 접근은 확보하지 못했다. Private context 실제 호출은 SERVICE_ERROR였다. 상세 실제 조회 및 내용 읽기의 범위는 `sources/SURVEY_GITHUB_KO.md`, `sources/BACKUP_SUMMARY_KO.md`, `sources/BACKUP_COVERAGE_AND_DECISIONS.json`에 있다. Metadata enumeration과 본문 읽기를 동일하게 세지 않는다.

다른 repository의 최신 조건부 EOS inverse, CR pair/energy support, WU reactive-array 준비, REC thermal-defect 경로 reference, BASS integration 및 anchor-defect, VigilODE 기록을 대조했으나 이번 접근 범위 안에서 HE의 세 actual physical input을 닫는 payload는 확인하지 못했다. 이 사실이 어디에도 존재하지 않는다는 증명은 아니다. 관련 선행 성과와 상태는 유지하면서, 지금 해결 가능한 정확한 aperture 수학 문제를 수행했다.

## 정의와 데이터

`mu=cos(theta_cm)`, `z=mu^2`로 놓고

\[
q_b(z)=b_0+b_1z+b_2z^2\ge0\quad(0\le z\le1),\qquad
f_b(\mu)=q_b(\mu^2)
\]

인 모든 signed coefficient 벡터 b를 다룬다. Coefficient 단위는 nb/sr이며 분모와 aperture ratio는

\[
d=(2,2/3,2/5),\quad D=d\cdot b>0,\quad
P_g(b)=\frac{k_g\cdot b}{D}
\]

이다. `k_g`는 이전에 엄밀히 감싼 동일 detector union의 moment다. Uniform azimuth와 기존 convention을 그대로 사용했다. 같은 사건의 두 검출기 union에 관한 기하를 재계산하지 않았다.

사용한 실제 자료는 EXFOR M0475002의 **258 MeV 네 DCS점**이다.

| Nominal angle (deg) | 고정 DCS 창 (nb/sr) |
|---:|---:|
| 46 | [0.05, 0.11] |
| 61 | [0.15, 0.31] |
| 73 | [0.09, 0.23] |
| 87 | [0.18, 0.32] |

`±ERR-S`는 deterministic coordinate sensitivity window로만 쓴다. 확률적 동시 신뢰구간으로 해석하지 않는다. 에너지격자가 다른 M0475003 총단면적 6점을 결합하거나 보간하지 않았다. 선행 proof의 `|b_j|<=160`, `D>=49/4800000`과 saved nominal-angle/moment enclosure를 source identity와 함께 재사용했다.

## 하한을 증명하는 짧은 논증

True data row를 감싸는 midpoint row를 `m_i`, 그 오차를 `epsilon_i`라 하자. 확장한 창의 61도 lower bound와 73도 upper bound로

\[
\rho=\frac{L_{61}^{o}}{U_{73}^{o}}\ge0,\qquad
h=m_{61}-\rho m_{73}
\]

를 만들면 모든 true feasible b에 `h·b>=0`이다. 또한 `v(r)=(1,r,r^2)`는 `[0,1]`의 모든 r에서 `v(r)·b=q_b(r)>=0`를 만족한다.

실제로 두 geometry 각각에 대해 정확한 유리수로

\[
k_{g,\mathrm{mid}}-\alpha_gd
=\lambda_gh+\eta_gv(r_{\mathrm{out}}),
\qquad \lambda_g,\eta_g\ge0
\]

를 구성하고 세 성분의 잔차가 정확히 0임을 확인했다. 따라서 모든 true feasible b에

\[
\frac{k_{g,\mathrm{mid}}\cdot b}{D}\ge\alpha_g
\]

이다. 코드의 dual `mu`는 위 식의 `eta_g`를 뜻하며 각도 변수 mu와 구별된다. 이 증명은 후보 optimizer가 전역 탐색을 완료했다는 가정 없이 전체 비음수 cone에 적용된다.

Saved moment가 midpoint와 다를 수 있으므로, 기존 containing outer polytope의 정점 V로

\[
M_j=\max_{v\in V}\frac{|v_j|}{D(v)},\qquad
\Delta_g=\sum_jM_j\frac{k^+_{g,j}-k^-_{g,j}}2
\]

를 정확히 계산했다. 분모가 양수인 convex combination을 분모 가중치로 다시 쓰면 모든 feasible b의 `|b_j|/D<=M_j`가 따라온다. 그러므로 true moment objective의 하한은 `alpha_g-Delta_g`다. Signed coefficients의 부호를 무시한 interval 평가를 사용하지 않는다.

## 상한을 주는 실제 feasible square

두 active row의 square 접촉 조건에서

\[
w_i(r)=r^2-2m_{i,1}r+m_{i,2},\qquad
F(r)=U_{73}w_{61}(r)-L_{61}w_{73}(r)
\]

를 얻었다. Outer/inner 각각 `[4/5,9/10]`에서 endpoint signs와 양의 derivative를 확인하고 80회 정확한 이분법을 적용했다. Inner root bracket의 위끝을 `r_in`으로 골라 허용 scale interval의 중점 a를 쓰면

\[
q(z)=a(z-r_{\mathrm{in}})^2,\quad
b=a(r_{\mathrm{in}}^2,-2r_{\mathrm{in}},1)
\]

이다. 실제 a는 양수이고 네 contracted row 모두를 통과한다. 따라서 이 polynomial은 모든 z에서 비음수이며 true data windows를 만족하는 구성적 witness다. 표시용 근삿값은 `r_in≈0.8627060313243863`, `a≈0.38074526996935787`, `b≈(0.2833741205554522,-0.6569424816015935,0.38074526996935787)`이다. 권위 있는 값은 saved certificate의 exact fractions다.

Witness의 sign-aware moment upper ratio를 `U_g`라 하면

\[
\max(0,\alpha_g-\Delta_g)
\le\min_b P_g(b)\le\min(1,U_g)
\]

가 된다. 실제 witness는 family의 비공허성을 증명한다. 이전 coefficient box와 denominator floor가 주는 compactness/continuity로 최소값 존재도 확보된다. `THEORY.md`가 비자명한 전이와 조건을 모두 전개한다.

## 구현·검증·비용

표준 라이브러리 Python `Fraction`으로 root isolation, 3×3 elimination, dual, square, moment correction을 구현했다. Producer와 분리한 saved-certificate reader는 후보를 다시 찾지 않고 정확한 algebra와 부등식을 확인한다. 합성 exact example, 부호·특이계·잘못된 certificate rejection, 실제 input/vertices/witness/width를 다룬 8개 unittest가 모두 통과했다. 상세는 `VALIDATION_KO.md`, `SCIENTIFIC_CHECKS_KO.md`, `APPRAISAL_AND_REPRODUCIBILITY_KO.md`에 있다.

최초 S05 launch는 host/local PID namespace를 혼동한 runner monitor 때문에 과학 control 실행 전에 실패했다. 오류를 숨기지 않고 수정 전 로그·두 diagnostic 이력·별도 R01 publication을 남겼다. 수정된 source pin `3beb35dc7dea7a60642497dc373c98e75ca07536`에서 한 번의 targeted retry가 8 PASS로 끝났다. 성공 campaign CPU0.172766 s/wall0.164806602 s, 최초+targeted science launch 누적 CPU0.217837 s다. 새 science repair reserve는 0이다.

Wolfram evaluator 1회는 17 literal zero +12 True를 반환했다. 앞선 context SERVICE_ERROR와 L/U service warnings는 보존했고 `PASS_SCOPED_WITH_MESSAGES`로 판정했다. 원격 CPU/wall은 측정되지 않아 null이다. Saved-only plot 1회는 CPU1.438273 s/wall1.388089466 s, science calls0으로 완료했으나 x tick overlap이 있어 정확한 표를 정량 제시의 기준으로 삼는다.

## 과학적 의미와 남은 의무

이 결과는 선행의 유한 inner/outer cone 사이에 남은 최소값 간격을, 전체 비음수 짝4차 family에 유효한 lower certificate와 actual feasible square로 닫은 것이다. 새로운 일반 최적화 정리나 strong no-go를 주장하지 않는다. 실제 angular/polarization law를 알아냈거나 절대 event rate·medium heating을 계산한 것도 아니다. 절대 normalization이 공통 인자이면 비율에서 상쇄되는 범위만 활용했다.

Local reference admission은 기존 12 complete +1 inherited partial +3 physical open에 scoped complete 1개를 더해 **13/17**을 만든다. 중앙 과학 DAG는 **28/88, HE delta0**이다. 아래 세 입력은 계속 open이다.

1. EXFOR event/inclusive normalization과 liquid-He electron/target-motion/response projection.
2. Actual full angular/polarization law와 photon encounter flux/history.
3. Named nonthermal birth/deposition/thermalization과 global species binding.

Sole binding owner는 `population_rest_energy_witness`다. `independent_binding_RHS`, `Gamma_thermal`, `Cv`, `species_heating`, `thermal_deposition`은 null, `birth_pool=UNASSIGNED`, `global_physical_completion=null`, `L4=false`, `production=NOT_APPROVED`, `activation=false`다. 이전 완료·partial·실패 이력을 유지하고 완료된 science/test/CAS/plot/ACKed backup을 재실행하지 않는다. 이 단일 이론·코딩 루프의 게시·최종 전달 이후에는 새 명시적 후속 작업을 기다린다.

## 출처와 권위 파일

- 실제 데이터: IAEA EXFOR master M0475, `https://nds.iaea.org/nrdc/exfor-master/entry/m/m0475.txt`; 보존한 `official_source/M0475.x4` SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`.
- Arends et al., Physics Letters B62,411–412(1976), DOI10.1016/0370-2693(76)90671-7. 이번 조회에서 논문 full text는 확보하지 않았고 EXFOR 원문을 실제 데이터 근거로 사용했다.
- Nie/Demmel, Shape Optimization of Transfer Functions, 저자 공개본 §2 Theorem2.2의 interval positivity 연결: `https://mathweb.ucsd.edu/~njw/PUBLICPAPERS/TrnShapOptCoef.pdf`.
- Charnes/Cooper(1962), fractional programming 원전 공개 scan: `https://iiif.library.cmu.edu/file/Cooper_box00010_fld00009_bdl0001_doc0001/Cooper_box00010_fld00009_bdl0001_doc0001.pdf`.
- 문헌의 실제 접근 범위와 이 결과와의 대응은 `sources/TANGENT13_PRIMARY_SUPPORT_KO.md`, `sources/PRIMARY_REVIEW_KO.md`에 기록했다. 이번 증명은 위의 elementary weak duality와 exact polynomial construction으로 직접 작성했다.
- 상세 proof: `THEORY.md`; 원시 exact 결과: `evidence/validation/repair1/SAVED_PLOT_DATA.json`; 독립 admission: `review/`; 단계별 실제 게시·백업 및 마지막 source/central/transport identity: 최종 외부 권위 문서.
