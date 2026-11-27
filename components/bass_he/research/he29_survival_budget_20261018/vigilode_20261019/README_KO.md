# HE29: VigilODE 재사용과 제한된 Rust 기준해 연결

2026-10-19. 이 확장은 기존 HE29의 네 Radau+DOP853 기준해를 먼저 완료한 뒤, 같은 m8/GL4/q0/r4/table512 모델에 VigilODE RODAS5P를 한 번 더 적용할 수 있도록 준비한 코드다. 실제 Rust bridge 빌드와 작은 FFI 검사까지 완료했다. HE29 물리 기준해의 관측된 새 반환은 여전히 **0/4 NOT_RUN**이며, 선택적 canary도 NOT_RUN이다. 원격 NCP 도구는 월간 사용량 한도로 막혔다. 제출·실행을 주장하지 않는다.

## 이번에 새로 한 일

| 단계 | 실제 결과 | 성립 범위 |
|---|---|---|
| 결과 intake | 연관 GitHub와 Drive/Dropbox 및 보존 보고서 조회 | 조회한 표면에서 새 HE29 반환 없음; 숨은 원격 실행 부재 증명 아님 |
| R2 이론 | 가스·광자·수동 ledger 블록의 Schur 소거, Wolfram 잔차 8개 정확히 0 | 조립된 유한 행렬의 대수 항등식 |
| 새 경량 수치 | 23개 합성 선형계, 6개 부적합 경계, 잘못된 부호 검출 | 수치 구현의 작은 회귀 검사 |
| 새 Python 검토 | callback 71개, FFI/identity/canary 25개: 고유 96개 PASS | fake C callable과 실제 ctypes 경계; HE29 물리 실행 아님 |
| 새 Rust 빌드 | Rust 1.94.1, locked/offline, release bridge만 빌드 PASS | 고정 a21d와 4개 bridge source identity |
| 실제 Rust FFI | 비자율 정확해, callback 실패, 부분 반환 3/3 PASS | 작은 2상태 ODE; 기존 과학 suite 재실행 0 |
| HE29 기준해 | Radau+DOP853 네 쌍 0/4 관측 | NCP 실행 필요 |
| VigilODE canary | NOT_RUN, 선행 기준해 4/4 필요 | r4/table512 한 건만 허용 |

빌드된 library SHA256은 `8d2f1271726781d2b000f0cd5eaadb0adac8029eb9357f786bfd647cea390460`이다. 이 환경의 binary 식별자이며 NCP 재빌드가 동일 binary bytes를 낼 것이라고 가정하지 않는다. NCP는 자신의 source/compiler/library identity를 새로 기록한다.

실제 smoke의 scaled endpoint 최대 절대 차이는 `4.065636716177323e-13`이었다. 이는 해당 합성 정확해와의 비교다. HE29의 `1e-11` absolute fraction gate, 온도 `1e-9 K`, photon/energy/species ledger 허용치는 변경하지 않았다.

## 무엇을 재사용했는가

과학 코드·테스트는 BASS_HE `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native microphysics owner는 rei_bianchi `f7830e2f55e7a1938bc3c98f61b60651f8dae474`를 유지한다. HE28 pilot/6개 study, HE29 finite-donor 90사례/720구간 및 50개 source-only tests는 기존 근거를 재사용했고 반복하지 않았다.

VigilODE는 `a21d573980f66fe02891bd216153443b5352f921`의 실제 `integrate_sequential_matrix_free_adaptive_observed`, RODAS5P, GMRES, 기존 faer 0.24.4 의존성을 사용한다. main branch가 최신 연구 버전이라는 가정은 하지 않았다. 새 bridge의 Cargo.lock은 원본 registry version/source/checksum을 유지하면서 실제 Cargo가 생성한 94개 package(root 포함)이다.

num-dual, diffsol, ode_solvers, gauss-quad, russell_ode도 공식 자료와 소스로 조사했다. 현재의 opaque f64 native owner에 자동미분을 적용할 수 있다고 가정하거나, 준비된 Radau/DOP853·GL table을 새 package로 교체하지 않았다. 실제 적용한 Rust 경로는 기존 VigilODE integrator와 그 faer/Krylov 기반 선형해법이다.

최신 VigilODE PR71의 별도 run 39255702592는 source `bab3902b3501d7fede9add7fd646074b9368adb8`에서 build/small native test를 반환했지만 accuracy/timing은 JSON의 NumPy int32 직렬화 실패로 BLOCKED였다. 완료된 새 비교나 HE29 결과로 사용하지 않는다. 그 branch의 source/lock을 a21d bridge에 섞지 않았다. 자세한 근거는 `evidence/LATEST_PR71_RETURN.json`과 `evidence/INTEGRATION_AUDIT_KO.md`다.

## 연결 구조와 이론의 범위

Rust는 적분기만 제공한다. 기존 Python `RefinedSourceModel.rhs/jac`와 동일 native owner를 callback으로 연결하며 원래 scale, cutoff, photon/source table을 유지한다. 각 cutoff 구간을 u∈[0,1]로 정규화하고 partial time derivative는 표현 가능한 실제 시간과 구간 내부의 점에서 계산한다. exact-state Jacobian cache와 CSR JVP를 쓴다. 임의의 상태 clipping이나 cutoff를 넘는 RHS 조회를 하지 않는다.

관측은 구간 양끝뿐이며 dense interpolation을 사용하지 않는다. 원래 모델과 정확히 같은 table SHA, source/input/binary와 Python/NumPy/SciPy identity, 네 기준해의 완료·admission을 통과해야 canary를 호출한다. 반환된 raw endpoint를 먼저 보존하고 기존 `check_result/admit_pair`로 저장된 Radau와 DOP853 양쪽을 비교한다.

새 Schur 유도는 `RESEARCH_KO.md`를 따른다. 수동 ledger가 역으로 물리에 영향을 주지 않고 광자 자기 블록이 -K일 때 큰 선형계를 가스 4×4 Schur 계로 줄일 수 있다. 이번 production bridge는 아직 그 전용 preconditioner를 구현하지 않는다. 현재 적용은 기존 GMRES와 원래 Jacobian의 JVP이며, Schur 항등식·합성 검사를 NCP 성능 향상이나 전역 정확도 증명으로 부르지 않는다.

## 실행 진입점

원래 네 기준해는 상위 `CODEX_HANDOFF_PROMPT_KO.md`의 고정 1569 checkout와 검증 재사용 overlay를 적용한 `ncp/START_REFERENCES.sh`로 시작한다. 과거 `PUBLISH.sh`는 실행하지 않는다. 입력 archive의 22개 DATA만 SHA 검증 후 자동 복원한다.

이 확장의 구체적인 NCP 명령은 `NCP_HANDOFF_KO.md`에 있다. 새 `ncp/build_bridge.py`는 fresh output에 고정 VigilODE와 bridge를 빌드하고 `BUILD_IDENTITY.json`을 만든다. `src/run_vigilode.py preflight`는 물리 적분을 하지 않는다. `canary`는 원래 process-group helper로 wall limit을 집행하고 첫 실패와 부분 관측을 보존한다. 기존 case나 전체 격자를 자동 확장하지 않는다.

## 게시·백업과 주장 경계

새 구현 코드는 `57642252991b5c453db66eb5a078e6a62cc6f4ea`로 게시됐고 **54/54 실제 GitHub readback이 일치**했다. 완전 보존 묶음은 `BASS_HE_HE29_VIGILODE_COMPLETE_20261019_7bf7398b.tar.gz`, 2,958,755 bytes, SHA256 `7bf7398b77b2bf04a6917bef4241fc216764c7658ebf25c85e5df7377fb6147a`다. Drive `1RypR402ikbM_nF42R6NUzExWQfa0Xp6G` 및 Dropbox `id:BSpOijBcT10AAAAAAD_Q4A`에서 실제 raw bytes와 payload 229개 해시가 모두 일치했다. 이 후속 문서·receipt 변경은 위 코드 archive와 분리한다.


R2 체크포인트는 `c0dc26736bea18bcaa8d0a6241daed2b5a1ea7f9`에 7개 파일로 게시됐고 7/7 byte readback이 일치했다. `BASS_HE_HE29_VIGILODE_R2_20261019_78356130.tar.gz`의 SHA256은 `783561303c7d3a47c38b5b4f76ddd93c43d394faf94ee53d6e2de0fc45a88a0c`; Drive와 Dropbox의 실제 raw readback이 모두 일치했다. 새 구현의 실제 게시 commit/백업 receipt는 이 디렉터리의 `DELIVERY.json`을 기준으로 한다. source commit과 후속 receipt commit을 구별한다.

빌드와 smoke 원본 receipt는 변경하지 않았다. 전체 intake 166개 = a21d source 161개 + 별도 fa07 benchmark evidence 5개이며, 그 관계는 `evidence/SOURCE_IDENTITY_ADDENDUM.json`에 기록했다. compile 전에는 필수 coefficient fixture와 integrators/build.rs가 포함되어 있었다. 최초 누락 build failure와 복원 사실도 보존했다.

연속 스펙트럼, 전체 EoR, 전역 gas-temperature 오차상한, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 HOLD다. solver 내부 estimator는 원래 물리 ledger나 엄밀한 연속 오차상한을 대체하지 않는다.
