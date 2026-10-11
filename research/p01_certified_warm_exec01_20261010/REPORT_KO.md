# P01-CERTIFIED-WARM-EXEC01 실제 production 첫 interval

동결된 warm H/He 입력을 production `SourceBoundConditional` 경로에서 정확히 한
번 실행했고 runner 검사는 `PASS_SCOPED`, exit 0이다. 독립 Astra 검토도
`PASS_SCOPED`다. 검토자는 clean-build source/binary/receipt 및 저장 결과를
독립 재계산했으며 native launch·solver interval·source edit은 추가하지 않았다.
CR/RCT/HH는 OFF이며 global scientific admission은 HOLD다.

실행 시 checkout은 `research/cr-first-build-gate-20261010`, commit
`8722f3ab587399700d96d300b617f0f37f1d831a`, tree
`7d4777b9231c5913d551c0a85cb311bfbcac838d`였다. 최초 읽기에서 tracked/untracked
상태는 clean이었다. 이 새 evidence directory 추가 후 실제 launch를 수행했다.
원본 dirty checkout은 읽거나 수정하지 않았다.

실제 사용 executable은 기존 clean build commit
`f9135eca0d41dd00465fcd524c07872a9c3c8fb8`, tree
`35389ad8e9a6baf7dcde91a93e5e7d53495911fd`에 연결된 것이다. receipt SHA는
`eba5b76a2d1056586aba3d06370ffd81585c1d470c4a1ea5b6835d6de51a52fa`,
binary SHA는 `e098111ee8e403c5985fea20cfca7b0408e5d82ea77c2eded50cff72d1392d0f`다.
launch 전에 receipt의 34개 consumed source와 binary를 검사하여
`PRELAUNCH_BUILD_PASS`를 얻었다. metadata checkout identity와 built identity는
각각 `PRELAUNCH.json`에 기록한다. 재빌드와 production source 변경은 0이다.

frozen reference NPZ SHA는
`3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`,
reference JSON SHA는
`f1ef5e09495df872e705656ff8d1252376c230e860ccbb882e3527b17e41a24b`이다.
Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0으로 실행했다. 환경 차이는 기록하며
수치 출력에는 동결된 오차 기준을 적용했다.

실행 명령은 `EXECUTION.json`의 command 배열에 보존한다. 실제 production
interval stdout, stderr, JSON 및 NPZ는 각각 `stdout.log`, `stderr.log`,
`output/production_interval.json`, `output/production_dataset.npz`이다.
외부 command wall은 3.170178345986642 s, user CPU는 5.418656 s, system CPU는
0.276741 s다. 이는 production subprocess와 자식 실행의 측정값이며 준비·검토
overhead를 포함하지 않는다. interval 내부 wall은 2.6889258220326155 s다.
600 s wall limit 및 10000 native RHS limit 안에서 RHS 257회, BIND 1회,
SIGMA 17회, 저장 epoch 17개를 실행했다. 최초 failure와 repair는 없다.

state 최대 scaled 차이 `1.0471941498209426e-15`, observable 최대 차이
`7.52579095108088e-16`로 2e-6 기준을 만족했다. global energy ledger
`1.5753781884128723e-15`, global photon ledger `5.704207918928809e-15`,
local energy ledger `1.7556755934167118e-16`, local photon ledger
`7.000969126733937e-15`로 1e-9 기준을 만족했다. 모든 saved state는 finite이며
photon positivity와 ionic normalization을 만족했다. 온도 범위는
49999.7770770447..50000 K로 30000..110000 K guard 안에 있다.

동일 stage의 geometry/state/source/opacity 계약, `N_rel=a_rel^3 n`, `E=qR`,
`R^-3` source mapping과 thermal/binding 분리는 기존 source를 그대로 사용한다.
closure는 `HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE`이며 recombination은 escape
ENERGY ledger에만 기록한다. 방출 recombination photon count는 UNDEFINED다.
기존 실패 자료·11-history·F04/F08 tolerance는 수정하거나 재실행하지 않았다.

이 결과는 동결된 2904-node discretization의 같은 warm interval에 대한
production consumer 검증이다. 독립 atomic/continuum/global validation,
cold REC IC, CR-first 전체 침적/history와 observational admission은 HOLD다.
controller가 P01 bounded use를 닫고 다음 READY node를 선택한다. 현재 standalone worktree에 AGENTS.md, tier-policy 문서 및
bounded-work RULES가 없어 `HARNESS_UNAVAILABLE`을 기록하고 parent가 동결한
실행 계약을 적용했다. 누락된 하네스를 기억으로 복원하지 않았다.
