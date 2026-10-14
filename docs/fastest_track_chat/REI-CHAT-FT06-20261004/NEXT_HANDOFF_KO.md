# FT06 -> FT07 physical model error budget

같은 repo cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, draft PR83. 시작/단계경계/게시전후 live HEAD를 조회한다. FT06 도중 Codex5f3bfe2fc8fe275ab6a054ca9082f03c5b91427a를 수신했으며 이 commit을 보존한다. F00/F02의 수신은 CODEX_RETURN_ACK.json이다. browser 직접전달 상태와 Git 수신을 혼동하지 않는다.

읽기: 이 README와 TASK_RETURN -> PAIR_CONTRACT_SUMMARY/PILOT_RESULTS_SUMMARY -> ZIP의 REPORT_KO.md 및 필요한 exact inputs. Full PAIRED_SCIENCE_SPEC.json SHA는 f320c5507f77fde3344febfb734d3738562988ea91461c9ee65350a314c4689b이다. Git projection을 full contract byte identity로 해석하지 않는다. 기존 FT suites 또는 Codex시험 전수 반복 금지. 이론/경량 standalone research만 수행한다.

다음 bounded node: REI-CHAT-FT07_PHYSICAL_MODEL_ERROR_BUDGET.

1. Rate-moment cooling에 필요한 함수오차와 lnT slope오차를 구분한다. |log alpha_true/alpha_model|<=eta0와 그 slope<=eta1이면 relative cooling bound는 exp(eta0)-1+exp(eta0)*eta1/qmin이다. 원문 rate 정확도만으로 eta1을 채우지 않는다. 필요한 source 채널만 targeted 조사한다.
2. 이미 source를 읽은 line/brem/Compton 및 secondary 후보에서 다음 controlled comparison에 넣을 항과 event/thermal/photon 단일 소유권을 선택한다. 실제 model truncation 차이를 paired estimator로 계산하되 새로운 ab-initio나 full history를 요구하며 멈추지 않는다.
3. Shared atomic function, same volume/proper-time input, angular M4와 rotation test, spectral support/event를 유지한다. +/-0.02는 물리오차 bound가 아니다. 몇몇 RR/slope/DR probe 변화는 baseline angular 진단보다 작으므로 nuisance-specific refinement 없이 negligible로 판정하지 않는다.
4. Fixed-time dynamical change와 observed-z endpoint shift를 분리한다. Prescribed geometry를 Einstein-solved cosmology라고 부르지 않는다. Same H/matter/Lambda+nonzero shear는 constraint와 충돌한다.

FT06 핵심 반례: six-axis deltaT=-.02286130K,128방향+.02161902K. Six axes가 독립적인 delta-beam model일 때는 오류가 아니다. Isotropic continuum 효과를 주장하려면 fourth angular moments/rotation/refinement까지 확인한다. Scalar first variation null은 smooth isotropic fixed-volume model에 한정하고 일반 evenness는 주장하지 않는다.

Codex는F01 typed provider를 계속한다. 여기서 해당 구현을 중복하지 않는다. Runtime F00의 actual_solver_binding은 NOT_IMPLEMENTED_F03_F04였다. F02 scalar oracle가 생겼다고 actual HHe residual이나 FT04 remainder를 닫지 않는다. 새 실제 residual/site/box가 들어오면 exact commit/blob를 읽어 그 항만 활성화한다.

Stop condition: 선택된 추가항의 source/회계/domain과 bounded paired sensitivity 및 열린 physical error를 남기고 게시한다. Strict local<2e-4/public width<2e-3, [160,161] FAIL과 tick160 보존. Same branch non-force append, 기존 Drive folder1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ와 Dropbox ATOMIC_REIONIZATION_HANDOFF_20261004_v1에 create-only backup. Metadata ACK, byte restore와 science validation은 별개다.
