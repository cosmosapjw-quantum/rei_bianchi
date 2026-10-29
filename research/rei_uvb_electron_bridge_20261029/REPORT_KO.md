# REI UVB electron source→BASS reduced30 관측행: 후속 이론·코딩 연구 보고

**2026-10-29 KST** · `REI_UVB_ELECTRON_BRIDGE_20261029` · independent add-only draft branch `research/rei-uvb-electron-bridge-20261029` (REI PR263 HEAD `f52ecdb11b3f7e43fdf1fbc19d9feff38fe56927`부터 분기). **단계 18/20 scoped, R6/C9 실제 다른 작성자 NOT_RUN**, 원 DAG REI working **33/88**, canonical central **28/88**, physical delta **0**, F4 `PARTIAL`, L4 `false`, `NO_MORE_IVPs=true`.

## 1. 최신 소스·브랜치·대화·백업 조사 범위

새벽 2026-10-29 현재 GitHub connector로 개별 PR HEAD와 일부 source blob을 직접 읽었다. 관련 스레드의 과거 결정은 현행 명시 제약을 재확인하는 데 사용했으나 모든 사적 대화·로컬 작업트리에 대한 byte-level 전수검사라고 주장하지 않는다. 기존 업로드된 `REI_PR263_SERIAL_AUDIT_PROJECTION_20261029.zip` (SHA256 `9491bb98ea9693bef9c29af1b88889082d2faf20f4f7fea9cd519f23bf2fe689`) 및 `rei_pr263_continuation_20261029` 보고서·코드를 readback했다. 새 소스는 기존 코드를 덮어쓰지 않는다.

| repo | 최신 직접 확인한 관련 PR HEAD | 이번 REI bridge 이식 판정 |
|---|---|---|
| rei_bianchi | PR263 `f52ecdb11b3f7e43fdf1fbc19d9feff38fe56927`, PR262 `6fbc3a79ceaa916c88d26656d84f7a916eeaa6cf` | 실제 17상태·7사건·국소 τ-jet source pin |
| bass | PR234 `c74317ce5df34c442514eccf8a1e87494657393d`, 최신 CE1-G PR244 `94385b1094442cf7c425e31b6d34dd7b0d1b3811` | reduced30 전자 가중치 관례만. CE1-G의 조건부 MPFR 경계는 UVB 물리 provider가 아니므로 미이식 |
| BASS_HE | PR107 `85e2faeebd777ab3e9b287a0dc1dfd38d9af723c` | DD inverse kinematics, UVB 전자 source 아님 |
| bass_cr | PR121 `6c3c91f9fd6261b6d79383ef7c5c8de7b6004fb6` | He K3 기하학적 budget, 화학 J_y 아님 |
| rec_bianchi | PR156 `8806a4f757d916b6cf040625be931a66e2f0f6fe` | HD 광자/준위 frequency ledger, REI 7 photo 사건 아님 |
| WU088_HH | PR158 `1a5c6f47350da2b74e0b7e3071c4db3502810500` | 105 K HD consumer still unbound, UVB 공급자 아님 |
| vigilode | PR108 `611e697ac4c4beb10b87573e985a95a9bc70ce09`, PR106 `c6cba2b62629e819dd163325c7c9fb9bb5e3080c` | weighted lognorm/GMRES 방법론 재사용 가능, 현재 full J_y/clock/norm 미결속이라 수치승격 금지 |

`SOURCE_MAP.json`에 실제 읽은 Git blob과 각 사용 범위를 적었다. Puchwein 2019의 full non-equilibrium UVB Table D1을 Table D2 equivalent-equilibrium 값으로 바꾸지 않는다. CLUE exact lumping literature와 2026 Eilertsen 등의 generic/critical parameter 조건을 검토했으나, REI↔BASS의 정확한 동역학적 lumping이 따라온다고 추정하지 않는다.

**백업 현황:** 원 PR263 Drive `1ebVyeMIXQLTLD0Kr4Fg9WMnRoFR6UIP4`의 `349471` bytes metadata readback 재확인, 원 Dropbox Paper `id:BSpOijBcT10AAAAAAEHAbg` 존재 확인. 원 Dropbox ZIP `/REI_UVB_TAU_JET_20261029_FULL.zip`은 정확 경로 조회 `NOT_FOUND` (원격 업로드 실패/성공 어느 쪽도 단정하지 않음). 신규 단위는 GitHub 단계별 20개 commit ACK 및 6개 code/source/figure-independent Git blob local match; 코드/보고서 선택본은 Library `/REI_UVB_ELECTRON_BRIDGE_20261029`에 성공 ACK. **신규 전체 ZIP의 Drive/Dropbox ACK는 아직 별도로 취급**한다. 모든 원 DAG 예산은 비이월, 모델/IO overhead는 `UNKNOWN_NOT_ZERO`.

## 2. 새 이론 결과

상세 정의·증명은 `THEORY_KO.md`를 참조. 우선 REI charge row `q17`, BASS reduced30의 6 charged coordinate 전자가중치 `eB`, 그들 사이 형식적 6×17 `M(x)`과 `rho=nHref/nb>0`를 정의했다. `M`은 REI H1+D / He3+He4 / Li7 charged states를 BASS isotope inventory weights로 나누어 만든 **관측량용 선형시험 사상**이다.

핵심 항등식:

`eB^T M y = rho (q17^T y − y_Tplus)`;
`eB^T M y + t = rho q17^T y`, `t=rho*y_Tplus`.

이는 물리적 one-to-one state projection의 증명이 아니다. T0와 T+ 사이에서 전체 T 보존을 유지하며 전자를 바꾸는 두 REI 상태는 같은 6개 projected coordinate를 주므로, 이 고정 `M`에서 T-sensitive complement가 최소 1차원임을 증명한다. PR262 실제 photo event matrix `S`에 대해 `eB M S-rho q17 S=(0,0,-rho,0,0,0,0)`이 정확히 남아, 이 7건의 사건에서는 T0→T+ 단 하나가 **전자 source 잔차**다. Li6·fast pool·nuclear/CR·recombination 등은 사상 바깥에 그대로 남는다.

더 일반적으로 `tau_x=c(x)y`, `c_a=0`, `y_x=F/H` 및 local restart `D_a y(x0)=0`, 공통 source scaling `B_kappa=(z−3.6) B_beta`에서 정확히 `det D_a(tau_xx,tau_xxx)=(z_x)(cB_beta^x)^2`다. `c_x`, full unknown `J_y`, `D_xB_beta`는 determinant에서 상쇄된다. 이것은 PR263에서 scalar `W q`로 쓴 정리를 시간 의존 charge covector까지 확장하지만, **모수 의존 geometry/clock/covector**에서는 일반적으로 거짓이다.

`epsilon=lambda_T/sum_j lambda_j`라면 공통 scaling 안에서 `D_projected/D_REI=(1−epsilon)^2`. 비음수 He photo events 아래 각 frozen 시점에서 `epsilon<=y_T0/(y_H10+y_D0+y_T0)`. 7행에서 최대 `epsilon_upper=1.20052873728269005e-16`, 대응한 최대 source-only normalized determinant 상대결손 `2.40105747456537996e-16`이다. `nHref_x*y_T+`, 다른 chemistry, 누적 적분과 optical-depth/observer frame 오차는 이 부등식으로 한정되지 않는다. Double precision 직접 1−epsilon을 계산해 0으로 잘라서는 안 되므로 Fraction/Decimal85로 계산한다.

## 3. 코드·실험·검증

새 별도 `code/bridge.py`는 17원 전하, 7 photo stoichiometry, 정확한 분수 사상, 하나의 T 보조좌표, 이벤트 source 잔차, synthetic simplex gate, epsilon 경계와 85자리 Decimal jet 출력, 실제 physical tau 호출 fail-closed를 구현한다. `tests/test_bridge.py`는 초기 str 유리수→float 변환으로 2개 ERROR가 발생한 것을 **테스트 입력 표현만** 바꿔 재실행한 기록을 남긴다. 최종 24/24 PASS, 약 0.010s; 정상/음수/기하학 분기·결손반례·소스 SHA 변조 거절·출력 범위 테스트를 포함한다. `g++ -std=c++20 -O2 -Wall -Wextra -Werror` standalone reference는 7/7 PASS, 상대 차이 최대 `1.17536e−19`. 이는 장시간 solver 벤치마크가 아니다. Source-only 7개 high-precision 결과 `results/RESULT.json` 및 C++ TSV와 그림 두 장을 생성했고 실제 그림을 읽었다. 끊긴 연속 궤적처럼 선을 연결하거나 공동 posterior처럼 그리지 않았다.

별도 Wolfram CAS 첫 호출에서 잘못된 `Do` 인덱스 지정으로 예상치 못한 Li 잔차가 보였으나, iterator를 명시적 행 배정으로 고친 뒤 결과는 `{det residual=0, eM−rho q: T+ only=−rho, 7event residual: T event only=−rho}`. **이것은 Wolfram 독립 알고리즘 교차검산이지 별도 작성자 R6/C9 심사가 아니다.** native delegation tool은 이번 ChatGPT 세션에서 노출되지 않았으며 subagent dispatch `NOT_RUN`.

`STAGE_LEDGER.json`에는 이론 R1–R10 + 코딩 C1–C10을 총 20개 stage Git commit과 연결했다. R6, C9를 실제 작성자 심사 보류로 두어 18/20 scoped, physical 0 노드를 보존한다. 서로 다른 시점의 이전 누락·실패·CI (`cargo fmt --check` 원래 상속 실패 및 skipped cargo test)도 포괄적인 CI PASS로 둔갑시키지 않는다. 이번 브랜치 자체의 GitHub Actions CI는 별도로 조회·통과하기 전까지 `NOT_VERIFIED`.

## 4. 왜 source-qualified dynamical projection이 아직 없는가

완전 소스 정합을 주장하려면 다음 결합을 실제 BASS/REI/observer 코드에서 검사해야 한다.

`M_x y + M F_REI(x,y;a)/H_REI(x) == f_B(x, M y; a)`.

현재 `M_x`에는 실제 `rho_x`, 물리 isotope simplex와 Li6/T pool이 빠졌고, `F_REI`와 `f_B`는 source-locked 동일 chemical/recombination/fast energy owner가 아니다. 동일한 전자수 하나로 `n_e`를 표현하는 것은 상대방의 전체 동역학을 닫지 않는다. full chemical `J_y`, electron feedback, K/nHref/nb/H, tangent IC, directional observed redshift, Thomson frame, whole-path error/R radii는 모두 미결속이다. 관측 fitting, new IVP, native25, physical-L4, production claim을 봉인한다.

## 5. DAG 판정과 추천 다음 단일 노드

- 기존 중앙 **28/88**, REI working **33/88**, 추가 physical **0**; F4 PARTIAL, L4 false, 전역 자원/예산 승인 없음.
- 이번 단위 이론·코딩 한정 **18/20**, 독립 다른 작성자 R6/C9 미수행. 새 국소 charge observable/relative jet theorem을 **scoped scientific result로만 유지**한다.
- 다음 DAG-admissible 작업: `BASS_REI_PHYSICAL_CHARGE_BIND`: BASS 원본 binary64 scale 및 isotope simplex와 REI saved origin, 수치 `rho`와 물리 clock, Li6/T 처리, 이력에서의 `M_x`, 동일 사건의 actual source ownership을 결속한다. 초기 작업은 static/source-only와 zero-IVP 검증으로 한정한다.
- 이 자료가 갖춰져 실제 full `J_y`/IC와 승인된 실행이 주어질 때만 후속 dynamic tangent·physical tau·directional CMB 경로를 검토한다.

## 자료 재현과 백업 구별

GitHub Draft 기반 재현은 `research/rei_uvb_electron_bridge_20261029`에서:

```
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s research/rei_uvb_electron_bridge_20261029/tests -v
g++ -std=c++20 -O2 -Wall -Wextra -Werror research/rei_uvb_electron_bridge_20261029/code/bound_reference.cpp -o /tmp/rei_bridge_bound
/tmp/rei_bridge_bound research/rei_uvb_electron_bridge_20261029/results/CPP_INPUT.tsv
```

상대 경로는 저장소 root 기준. `bridge.py`도 `python -B research/rei_uvb_electron_bridge_20261029/code/bridge.py`로 실행 가능. Source-transcript SHA `785708eaba030d4291cf1b9a06976b1a7f16bcb4e3fd102af95f6169c80af262`. 6개 source/theory/code/test/result Git blobs는 현재 로컬 Git hash-object와 **EXACT**. 새 ZIP local backup과 Library upload는 별도 object identity와 size/CRC로 판정한다. Google Drive/Dropbox 새로운 전체 ZIP은 실제 성공 ACK+size+hash 없이 `COMPLETE`로 적지 않는다.

### 외부 원전 (이번 소스 적용은 구별)

Puchwein et al. 2019, MNRAS 485:47–68, DOI 10.1093/mnras/stz222. Ovchinnikov et al. 2021, *Bioinformatics* 37:1732, DOI 10.1093/bioinformatics/btab010. Eilertsen et al. 2026 arXiv:2606.28895. 모두 방법/UVB 문헌으로서 REI/BASS의 실제 physical projection 검증을 대체하지 않는다.
