# REI↔BASS Li6 전하 pool: 원본 소스 기반 정확한 21→17 축약

**2026-10-29, 범위 한정 연구 보고서.** 부모 REI PR265 `9b0b97aadeebf368802f865c10eb8b633f2726e4`의 상태(working 33/88, central last 28/88, physical delta 0)를 그대로 유지하며 신규 IVP는 수행하지 않았다. 이번 목적은 기존 REI/BASS 물리적 동일성을 주장하지 않고, 정확히 어디까지 BASS 원래 화학계 내부에서 17상태로 줄일 수 있는지를 실제 코드로 증명하는 것이다.

## 핵심 결과

원 BASS `atomic_network.py`의 full21은 H1/D/T, He3/He4, Li6/Li7을 모두 포함한다. Li6·Li7 전이계수는 같은 `(Z=3,q)`에서 동일한 광이온화·재결합 행렬이고 직접 Li 핵반응·약붕괴 항은 없다. 실제 파일 SHA256: network `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, model `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614`. 선택 REI 7행은 SHA `7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77`이지만 두 파일군은 다른 pilot의 고정 입력이다.

양의 Li inventory ν6,ν7과 동일한 초기 전하분율 아래 `Y6,q=gamma*Y7,q, gamma=nu6/nu7`는 BASS full21에 대해 불변이다. REI 17개 이름에 대응하는 BASS retained 17상태로 정확한 lift E와 projection P를 구성하면 `F21(Ey)=E f17(y)` 및 `J21(Ey) E=E J17(y)`가 성립한다. 전체 21상태가 실제로 17차원으로 축약되는 **BASS 내부의 조건부 정리**이며, REI native source는 별도이다.

17상태에서 Li6 전자량을 빠뜨리면 `deltaq=gamma q_Li7` 및 `R=Gne,17`에 대해 `deltaF=nb(deltaq^T y)R y`, `deltaJ=nb[(deltaq^T y)R+(R y)deltaq^T]`가 된다. **두 번째 항만 rank-one**이고 첫 항은 원칙적으로 rank-one이 아니다. 원천적 양성성/원자수 제약에서 `0<=delta(ne)/nb<=3 nu6`가 sharp하게 얻어진다. 동일 주어진 상태에서만 `0<=delta(tau_x)<=3 K nb nu6/H`이며 K, H, nb의 실제 물리 시간 이력은 미입력이다.

원본 BASS binary64 inventory에 따라 `nu6≈7.54954398759313812e-15` baryon당, `3nu6≈2.26486319627794144e-14`, 초기 자유전자 총수 대비 Li6 비율 `≈4.99986250353115957e-11`이다. 이 값은 REI의 지리적·관측적 n_e가 아니고, PR265에서 H1/He4의 다른 inventory 때문에 생긴 0.4943–0.5186%의 **pilot mismatch를 해소하지도 않는다**.

## 검증과 오차 분류

- 현재 실행: Python 3.13.5 및 SymPy 1.14.0: `30/30 PASS`, 22개 독립 seed 방향의 21→17 정확한 `Fraction` RHS/Jacobian identity, source SHA 불일치 거부, Li6 광이온화 rate perturbation 반례, exact charge, 상대 시계식 검증.
- C++20(g++14.2.0) raw Li7 세 전하 성분 + owner nu6/nu7 독립 구성 `7/7 PASS`. 저장된 REI 7행에 BASS lithium fraction을 형식적으로 이식한 *counterfactual* 입력. 원래 BASS native empirical rates와 동일 physical output이 아니다.
- Wolfram: 직접 nonlinear 2-charge/2-isotope 예제에서 `F(Ey)-E f=0_(4)`, `J(Ey)E-Ej=0_(4x2)`; Li6의 rate만 다르게 하면 `(-epsilon gamma u,+epsilon gamma u)`가 남는다.
- 원래 첫 C++ 검사가 같은 스칼라 곱을 재현하는 약한 독립성이 있어 raw Li7 charge 및 두 isotope inventory를 입력하는 방식으로 개선. Python의 한 항등식 자가비교 테스트도 실제 Li6/Li7 4×4 광이온화·재결합 행렬 비교로 대체. 원래 오류와 수정은 `results/REPAIR_HISTORY.json`에 보존했다.
- Python 실제 테스트 1.17초 wall, user1.46초, sys0.12초, 최대 RSS130000KiB. 준비/연구/host/transport 비용은 UNKNOWN_NOT_ZERO, 원래 예산을 이전하지 않았다.

## 독립성, 가정과 한계

시험용 photo/recombination rate 숫자는 원본 구조에 대입한 **synthetic exact rational fixtures**다. 이는 원본의 소스 구조, 초깃값, 전하/핵종 표기와 기호적 RHS 형태를 검증하지만 실제 source-owner `atomic_coefficients.json`에서 native `AtomicNetwork.evaluate`를 호출한 과학 rate 검증은 아니다. 원래 chemical/thermal external source를 보유한 REI model.py에는 다른 photonuclear, CR, injection, fast-reservoir, prescribed-bath 항이 존재하며, 실제 공통 초기 상태·코드·source clock·전자 pool·K/H는 결속되지 않았다.

PR265의 full repository `verify` workflow 40836826002는 inherited Rust `cargo fmt --check` 단계 실패이며 이번 새로운 Python/C++ 시험의 실패로 대체하지 않는다. Native distinct-author subagent가 노출되지 않아 R6/C9는 NOT_RUN. `F4=PARTIAL`, `L4_ready=false`, 기존 원 DAG는 33/88·28/88·physical delta 0, `NO_MORE_IVPs=true`.

## 후속 시행조건

이제 BASS 내부의 Li6 전하 closure 조건은 명확해졌다. 다음 `REI_BASS_FULL_EVENT_RATE_COMPAT`는 두 파일군의 **실제 photo+RR+DR source rate, IC, nHref/nb, H와 시간변수**를 동일한 provenance로 결속한 뒤, static event-by-event vector-field/Jacobian commutator로 검증한다. T→He3 weak injection, Li6/7 isotope equality, REI nuclear/CR source, hidden fast pools는 외부 입력 또는 명시적 채널로 남긴다. 독립 다른 작성자 R6/C9 완료와 새로운 IVP 실행 승인은 각각 별도 게이트다. 정확히 이 조건이 충족되기 전에는 새로운 τ history/CMB posterior/L4 production을 주장하거나 실행하지 않는다.

참고 문헌: Ovchinnikov, Pérez Verona, Pogudin & Tribastone, Bioinformatics 37 (2021), DOI 10.1093/bioinformatics/btab010 (exact Jacobian-invariant lumping). Eilertsen et al. (2026), arXiv:2606.28895 (special source/parameter-rate degeneracy). 논문들은 BASS 전용 소스의 대체 증거가 아니라 이론적 프레임이다.
