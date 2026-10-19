# REI-LRS V14 후속: native 모멘트 시간 중심화와 공통 기체 midpoint

2026-10-19. 독립 LRS photon–chemistry–thermal 연구. PR #198의 기존 branch에서 진행했으며 production v3/rux DAG와 별개다.

## 1. 이번에 실제로 달라진 결론

기존 두 모멘트 재복원·지수 감쇠의 시간 결함을 직접 적분하는 opt-in SSPRK(2,2) transport와 공통 gas-midpoint 결합을 구현했다. 실제 Rust1.94.1에서 14개 고유 표적시험, 52행 고정 매질 진단, 16개 고유 결합 이력을 실행했다. 16이력은 clock 수정 전후 같은 행렬을 한 번씩 실행했으며 32개의 새 사례로 세지 않는다. 최종 결합 행렬은 2,488 accepted step rows를 갖는다.

고정 기체·기하의 broad spectrum에서 local full-versus-two-half 차이는 약 3차, fixed-total-time 차이는 약 2차다. 양의 초기 photon을 둔 evolving gas의 주요 변수에서도 약 2차를 관측했다. 실제 GL2 source-on의 이번 짧은 구간에서는 photon N, photoheat, w, T의 최미세 자기차분 지수가 각각 2.04256, 2.02858, 2.03401, 2.02319다. HeIII 최종값의 차이는 약 2.4e-17로 수치 분해능에 걸려 이 채널의 차수는 보류한다.

이는 조건과 관측량이 명시된 결과다. source-on 전체의 일반 2차 정리, uniform stiff accuracy, CaseB, fullEoR, signed Bianchi 또는 native 일반 4차를 채택하지 않는다.

## 2. 새 실행 결과를 먼저 읽었다

재개 시 실제 GitHub HEAD는 ddfa6f5210ed6e17b54c0757fc23ed40d16f18c6였다. Drive V14 parent 및 하위 5개 folder, Dropbox rei_bianchi parent와 recursive 결과를 읽고 최신 archive metadata를 기존 전체파일 readback과 대조했다. 보존된 전체 archive의 SHA와 내부 source receipt, stdout/stderr, 종료코드 및 CSV를 실제 확인했다. 조사한 경로에서 이 HEAD 이후의 새 실행은 관측되지 않았다. 미게시 외부 실행의 부재까지 단정하지 않는다.

이전 NCP의 원래 V14 컴파일·36개 고유 표적시험·smoke 28이력·full84이력은 이미 실제 완료였다. 이를 다시 실행하지 않았다. original native source anchor f6046418d15e2f44418dfbc04ca67999f389a7df와 V13 parent 7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e를 재사용했다. ef94f08… 및 이후 게시 commit을 실행 당시 checkout SHA로 소급하지 않는다. 기존 제조76 문제, Python57, 이전 projection62행은 이번 새 검증 수에 넣지 않는다.

최신 projection archive는 5,748,523 bytes, SHA256 63eefca04fb7bb3c4884e40ecfd3b7058a3be3d43c7aee110b8e0f928014ef04다. 실제 intake 범위·시각·파일 식별자는 intake_drive/와 intake_dropbox/에 있다.

## 3. 왜 지수 감쇠 대신 닫힌 모멘트를 적분했는가

이전 고정 매질 진단에서 복원 R, 모멘트 A, 노드 감쇠 생성자 L의 한 스텝은 Phi_h=A exp(hL)R였다. 같은 매끄러운 support branch에서

    Phi_h-Phi_(h/2) o Phi_(h/2)
      = h^2/4 A L (I-R'A) L R + O(h^3).

개별 노드의 지수 감쇠가 정확해도 매 스텝 닫힌 모멘트로 다시 복원하는 과정은 이 O(h^2) 국소 결함을 남긴다. 기존 실측 local≈2/global≈1의 구체적 기작이다. 이번 변경은 원래 spectral closure의 에너지해상도 오차를 제거하는 작업이 아니다.

기존 native 노드의 f_l, q_l, E_l=r_l q_l, 단면적 sigma_j와 실제 광속 c를 그대로 써서 kappa_j=c n_j sigma_j(E_l), kappa=sum_j kappa_j로 둔다. 실제 forward Euler의 잔존 가중치는 (1-h kappa)f_l, 사건은 h kappa_j f_l이다. 같은 노드에서 N/U_ref/P/binding/heat를 계산한다.

    M*=FE_h(M0;gbar), M**=FE_h(M*;gbar), M1=(M0+M**)/2.

두 번째 stage는 M*를 다시 prepare한다. 사건·binding·photoheat도 두 stage의 같은 1/2 평균이다. 따라서 smooth closed-moment RHS F에 대해 M1=M0+hF+h^2 F'F/2+O(h^3)다. 기존 지수 map을 이 convex formula에 넣는 방법은 사용하지 않았다.

두 stage 모두 실제 노드에서 h max(kappa)<=1이어야 한다. 위반은 명시적인 AXBI_SSP_CFL이며 clipping과 자동 subcycling은 없다. 이 조건에서 노드 measure가 양수이고 {N>=0,lo N<=U_ref<=hi N}가 convex이므로 최종 photon moments도 실현가능하다. gas midpoint Newton의 양수성은 별도의 물리적 domain/해 수렴 조건에 의존한다.

Delta photon의 새 증폭식은 1-tau+tau^2/2이며 정확한 지수 semigroup는 아니다. 이 차이를 기존 delta ulp 기준으로 잘못 실패 처리하지 않고 polynomial과 Exp(-tau)의 알려진 오차를 구분해 검사했다.

SSP convex-FE 원리는 Gottlieb, Shu & Tadmor, SIAM Review43(2001),89–112, DOI10.1137/S003614450036757X의 Lemma2.1 및 Prop4.1/Eq4.1을 실제 원문으로 확인했다. Exa·SciSpace 검색 근거와 관련 원문은 theory/에 보존했다. 논문이 이 프로젝트의 native 결과를 보증한 것으로 표현하지 않는다.

## 4. 기체와 광자의 혼합항을 포함하는 유도

g=(x_HII,y_HeII,z_HeIII,w_eV/H), C는 photo를 제외한 native CI/RR/DR/CE/FF/signed-CMB, Q는 광자 사건·열의 gas RHS다. 각 4변수 Newton trial g1에서 gbar=(g0+g1)/2를 만들고

    M*=M0+hF(M0,gbar)
    M1=M0+h/2 [F(M0,gbar)+F(M*,gbar)]
    g1-g0=hC(gbar)+h/2 [Q(M0,gbar)+Q(M*,gbar)]

를 푼다. 평균 AbsorptionResult를 기존 add_absorption_rhs에 한 번만 전달한다. 온도는 native EOS로 w와 fractions에서 계산한다.

H0=C0+Q0로 놓으면 두 2차항은

    M: (F_M F0+F_g H0)/2,
    g: [(C_g+Q_g)H0+Q_M F0]/2

이다. 결합 ODE의 Taylor 전개와 일치하며 F_g H와 Q_M F 혼합항이 빠지지 않는다. Wolfram15.0.1의 실제 형식 함수 전개에서 두 h^2 잔차 {0,0}을 얻었다. 의도적으로 미정 함수 P,Q를 사용한 warning까지 원 출력으로 남겼다. 이것은 대수적 consistency 검산이며 native 시간 수렴을 대신하지 않는다.

## 5. 실행 중 발견한 실제 시계 결함과 수정

첫 결합 행렬은 원래 (a_end/a_begin).ln()/H_mid를 따랐다. 독립 raw 검토는 매우 짧은 구간에서 ratio가 1에 가까워지며 생긴 binary64 반올림이 누적됨을 확인했다. source GL2 N512의 시간 합은 같은 실제 binary64 endpoint와 native H를 고정밀로 평가한 값보다 112.286124136 s 컸다. 처음 CSV 십진 문자열을 직접 Decimal로 읽은 112.28144 s 추정과 구분했다.

최악 실제 sample은 N512, step386, segment2다. 기존 dt34874947.257907264 s의 오차는 약0.937896485 s였다. 새 opt-in child만

    dln_a=log1p((a_end-a_begin)/a_begin)

로 바꾸고, chemical solve에 실제 사용한 dt를 해당 segment ledger에도 그대로 전달했다. 가까운 양의 endpoint의 뺄셈과 작은 상대 간격에 대한 log1p가 ratio의 반올림 손실을 피한다. 기존 parent/birth 파일 본문은 수정하지 않았다.

한 개의 실제-sample 회귀시험을 추가했다. 이 sample의 stable dt 오차는 약2.65e-9 s, N512 누적 clock 오차는 -4.882812e-7 s로 줄었다. 5,952 birth microsegment의 기록 dt가 실제 안정식과 bit-identical임을 독립 확인했다. fixed geometry의 504 numerical rows는 wall time 외 모든 수치가 전후 같다.

같은16이력의 한 번 재실행에서 source-on 최미세 w/T 지수는 2.6586/4.1889에서 2.0340/2.0232로 바뀌었다. 이를 단순 Newton 누적 잔차 때문이라고 설명하지 않는다. 수정 전 source·결과·진단은 execution_coupled_pre_clock 및 native_files_pre_clock에 보존했다.

## 6. 실제 실행 행렬과 수렴

| 행렬 | 설정 | 실제 고유 결과 |
|---|---|---|
| A local | 고정 a=1/21, gas(.075,.12,.03), cells8/16/32/64, MD14 broad와delta60, theta=.1… .00625 | 40 full/two-half pairs |
| A global | cells16, theta_total=1, m8…256, 두 spectrum | 12 고유 fixed-total histories; A 합계52행/11,136cell행 |
| B fixed | 같은 a, T0=15000K, MD14 초기주입 dt_seed=1e16s, 후속source없음, total t=1/k20, m8…256 | 6 coupled histories |
| B seeded GL2 disabled | 같은 양의 seed, Xend=1e-5, N32…512, 실제geometry와source-disabledGL2분할 | 5 histories |
| B physical GL2 | 처음빈photon, 원MD14를실제GL2birth에주입, Xend=1e-5,N32…512 | 5 histories |

초기 packet의 dt_seed는 고정 z20에서 초기 광자 분포를 만드는 제어 입력이며 그만큼 과거 우주론을 진화시켰다는 뜻이 아니다. 실제 N_seed=.0429803611476/H, U_seed=.871495392921eV/H다. Seed source ledger를 기록한 뒤 초기 energy 기준을 설정했다.

B는 cells16, threads1, backgroundpanels128, native 물리상수와률, AllMid/common opacity midpoint를 쓴다. 새 진단의 Newton tolerance는1e-15로 명시했다. 이전 NCP84이력의1e-13 설정을 소급 변경하거나 두 실행을 같은 tolerances로 비교했다고 표현하지 않는다.

| 관측량 | A broad 고정기체 | B fixed evolving gas | B seeded disabled GL2 | B source GL2 |
|---|---:|---:|---:|---:|
| photon N, finest global exponent | 2.01876 | 2.01867 | 2.01336 | 2.04256 |
| physical photon U | 2.01775 | 2.01769 | 2.01221 | 2.03920 |
| x_HII | — | 2.01880 | 1.99648 | 2.04341 |
| w | — | 2.01339 | 1.99057 | 2.03401 |
| T | — | 1.99929 | 1.97520 | 2.02319 |
| photoheat | 2.01345 | 2.01338 | 1.99992 | 2.02858 |

지수는 연속 세 refinement 수준의 signed 자기차분을 보존한 뒤 log2(|D_N/D_2N|)로 계산했다. 정확해 오차로 바꿔 부르지 않는다. A broad cells16 local N 지수는2.99749, delta exact-exp 오차의 최미세 지수는2.00038이다. Source GL2 HeIII의 최미세 차이는 -2.4286e-17이며 지수0.65208을 2차로 채택하지 않는다.

실제 sourceGL2 최미세 차이는 w -6.54898e-12eV/H, T -1.94723e-8K, photonN +1.85931e-12/H, photoheat -6.65958e-12eV/H다. 차이가 작은 채널의 해석 한계를 함께 남겼다.

![실제 원시 자기차분](figures/ssprk2_refinement.png)

그림의 점은 실제 CSV이며 slope2/3 선은 안내선이다. fits 또는 추가 실험이 아니다. 재생 가능한 그림 코드와 raw hash 연결은 figures/에 있다.

## 7. 회계는 잔차 열을 믿지 않고 재구성했다

Y=.2454/[4(1-.2454)], e=x+Y(y+2z), 모든 사건은 total-H다. P/C/R/D 사건으로 H/He/electron/binding 변화를 각각 계산하고 photo heat, CI binding sink, CE, RR/DR thermal cooling, FF, signed CMB, escape 및 gas/photon work를 분리했다.

    Delta(w+B)+E_escape+W_gas-E_CMB=Q_photo+P_binding.

새 CSV는 initial/final active/passive photon physical N/U와 boundary N/U도 기록한다. 따라서 source ledger의 seed를 이중 계수하지 않는 delta convention에서

    Delta N_photon+P_total+Delta N_boundary-Delta N_source=0,
    Delta U_photon+P_binding+Q_photo+Delta W_photon
      +Delta U_boundary-Delta U_source=0

도 별도로 재구성했다. 예전 누락 CSV에 이 완전 회계가 있었다고 소급 주장하지 않는다. 이번 짧은 실제 run의 boundary 항은 기록됐지만, 이를 비영 경계흐름 stress test의 성공으로 확대하지 않는다.

독립 검토는 새 audit_* 또는 owner energy_residual 열을 판정 입력으로 쓰지 않았다. 2,488 step rows, 6,456 microsegments(고정504+birth5952), 3,968 birth records, 2,048 final cell rows를 원시 성분에서 대조했다. 최종 독립 최대 잔차는 theory/COUPLED_INDEPENDENT_AUDIT.json에 보존한다. 실제 최대 photon수 잔차는1.3712e-16/H, photon에너지는2.0110e-15eV/H, EOS에서 w를 다시 만든 전체에너지는2.9327e-14eV/H다. Thermal 재구성 잔차는3.0055e-14eV/H, binding은2.4590e-14eV/H, electron 사건은1.9389e-15/H다. 이는 이 행렬의 관측값이며 새 허용오차를 만들어 적용한 것이 아니다. 실제 boundary/passive N/U는 모두0이고, native CMB는 모두 음수였다. 양의 CMB heating을 실행했다고 주장하지 않는다.

최대 실제 accepted-stage tau는 .4652814347, 최대 accepted Newton norm은9.97713e-16이다. 실제 matrix에 CFL실패는 없었다. 명시적인 CFL실패·rollback·budget charge는 표적시험에서 검사했다. RHS의 rejected Newton trial까지 포함한 최대 tau를 이 수치가 뜻하지는 않는다.

## 8. 구현·검증·보존을 분리한 완료 상태

새 코드는 native_files/src/axbi_ssprk_transport.rs와axbi_ssprk_driver.rs, 부모파일 끝의 두 module hook, 두 표적시험과 두 diagnostic example이다. 원 transport40422byte와 driver98113byte prefix, 기존 physical_birth, MD14 source, Verner/Grackle/EOS 및 default/adaptive/checkpoint 본문을 보존했다. SOURCE_DELTA_SSPRK2.json은 실제 출력 source hashes와 복원 계약을 갖는다.

Sandbox Rust1.94.1에서 offline/locked/release/jobs2로 빌드했다. 최종14표적시험 exit0, 수정 후 fixed6 exit0(3.53s), birth10 exit0(37.59s)다. 시간은 이 sandbox 관측치이며 NCP 성능 예측이 아니다. 원시 명령/stdout/stderr/exit/timing과 source hash가 execution_coupled/에 있다.

restore_ssprk2_native.py와run_ssprk2_native.py는 정상 Git 파일이다. Fresh 전체 복원·source hash·Pythoncompile·CLI help·prepare-only·명시적 compiler실패의 실패receipt를 실제 확인했다. 이 wrapper 검증은 scientific matrix를 다시 실행한 척하지 않는다. 미래 runner는 실제 rustc/cargo버전을 기록하고 sandbox1.94.1로의 downgrade를 강요하지 않는다. 기존 NCP 관측버전은1.99.0이었다.

| 단계 | 과학·실행 상태 | 게시·보존 상태 |
|---|---|---|
| intake/이론 | 새결과검색완료, 유도·Wolfram·문헌확인 | StageA snapshot에보존 |
| A transport | 7tests/52행, 독립PASS_SCOPED | Git8bec37e, Dropbox전체readbackPASS |
| B gas/source/clock | 16고유이력, oneclockrepair+samecasesreplay, 총14고유tests | 최종payload와수정전후raw에보존 |
| C10 | fresh복원/실행기준비, 주장범위명시 | 최종Git/양쪽백업결과는stages의최종deliveryreceipt에서확인 |
| 새NCP | NOT_RUN | 지정키부재/원격연결기월간한도실제기록, 실행handoff완료 |

StageA Drive upload는 한 번 발행됐으나 ACK없이988.3s대기 후controller가중단했고 UNKNOWN_AFTER_INTERRUPT로 기록했다. 성공fileID나readback을 꾸미지 않았다. 최종 package는 StageA 내용도 포함한다. 최종 원격 archive의 생성·전체 readback 및 최종 HEAD는 업로드 후 작성하는 별도 deliveryreceipt에 기록한다. Archive 내부에 자기 자신의 사후 remote receipt가 들어 있다고 주장하지 않는다.

구현은 별도 coding agent에 요청모델gpt-6.1-sol로 위임했다. 실제 native collaboration의 agentID와반환물은 확인했으며 관측하지 않은 별도의 runtime모델 인증을 주장하지 않는다. root와분리된 두 Astra계열subagent가 한 검토pass를 transport와coupled로 나눠 읽었다. 다른 모델계열끼리 검토했다고 표현하지 않는다.

## 9. 다음 실행의 경계

NCP에 남기는 작업은 게시된 소스 복원, 실제 compiler로 빌드,14표적시험,52행 transport진단과16결합이력의 플랫폼 재현이다. 자동실행기는 준비됐다. 이 session에서는 지정NCP키가없고DesktopCommander가월간한도로호출을중단하므로새NCP실행은0이다. 원래84이력과새16이력을혼동하지않는다.

더긴구간·강성·비영경계흐름·signedBianchi는 다음에 그범위를 명시하고 실제 실행할 대상이다. 현재 결과를 이유로 기본 경로를 교체하거나 arbitrary-step SSP/CaseB/fullEoR로 승격하지 않는다. 완전한 복사형Codex인계는 CODEX_NCP_EXECUTE_KO.md에 있다.
