# v9 — 실제 age32 반환과 source exposure 분석

## 결론과 현재 판정

최신 PR199 HEAD를 실제 읽어 v8 배송 이후의 native age32 완료 결과를 확보했다. 입력 HEAD는 `93aca4cc483080b802fa85c9c44e43b9c85db5b7`, 그 실제 부모는 `5ef6766c66b319e48612f316ac1581bd12f6ebfc`다. 새 native 실행은 완료됐고 원 photon/energy 보존 gate를 통과했다. 그러나 같은 computational base·B1·runtime의 기존 age64와 비교한 endpoint 상대차는 **N 0.8248861211419689, U 0.7916059535400799**다. 원 finite-neighbor 목표 0.005는 충족되지 않는다.

따라서 기존 `R_AGE32_BLOCK_MAX_SAME_SOURCE_WITH_PASSIVE_DIAGNOSTICS`는 **실행·분석 완료**로 옮긴다. Native age/time 정확도는 **HOLD**, 실제 nonlinear Grackle response bound는 **NOT_ESTABLISHED**, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다. 완료된 age32를 다시 READY로 남기지 않는다.

근거는 [최종 분석](native_age32_analysis_20261020/results/attempt004/ANALYSIS.json), [유도](native_age32_analysis_20261020/THEORY_KO.md), [독립 R6](native_age32_analysis_20261020/reviews/r6/R6_RECEIPT.json), [독립 C9](native_age32_analysis_20261020/reviews/c9/C9_RECEIPT.json)에 있다. 초기 attempts001–003은 교정 이력을 위해 보존하며 attempt004가 현재 결과다.

## 1. 새 결과 탐색과 입력 동일성

실제 확인 범위는 REI 253 branches·최근 updated PR100, VigilODE 154 branches·PR78·최근 workflow25, Drive 지정 폴더의 반환 직접 자식130, Dropbox 지정 폴더28개(has_more=false)다. 다른 대화 검색은 이번에도 실제 호출했고 `Personal context is unavailable for this conversation` 오류를 받았다. 예전 연결 blocker를 그대로 상속하지 않았다. 모든 과거 대화·브랜치 내용·오래된 백업을 읽었다는 주장은 하지 않는다.

새 age32 archive의 전체 bytes와 SHA256을 Drive에서 확인했고, Dropbox에서는 같은 새 파일의 metadata를 확인했다. Archive 안의 실제 실행 source와 receipt의 45개 raw output hash가 일치한다. 기존 v8 C10과 confirmation도 전체 bytes로 재확인해 원 B1 binary를 복원 가능한 상태로 확보했다. 새로운 다른 lane BRPERF01 백업7개는 metadata까지만 읽었다.

VigilODE PR77의 Bernstein residual·invariant-box·log-norm 코드를 읽었고, REI PR212의 prescribed-bath contraction/rate-defect 계약과 코드를 읽었다. 두 결과 모두 실제 Grackle feedback 경계로 승격하지 않았다. 자세한 범위는 [GitHub·대화 intake](native_age32_analysis_20261020/intake/RELATED_INTAKE_RECEIPT.json)와 [백업 intake](native_age32_analysis_20261020/intake/BACKUP_INTAKE_RECEIPT.json)에 있다.

새 native 입력은 q0, age32/source8/n_mu8/transport16/time1, block-max/binary64, diagnostics ON, transport48, case/total cap1800s다. 원 native physics는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, B1 binary SHA256은 `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`, computational base SHA256은 `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`이다. 새 실행 source SHA256 `ab240948846a3a09e2bb60767af206e3865f6528a8673c90de177582569596f7`를 실제 bytes와 대조했다.

## 2. Native 실행과 원 기준의 비교

| 항목 | 실제 결과 |
|---|---:|
| Native status / exit | COMPLETE / 0 |
| Native wall / controller wall | 248.815719 s / 249.768710 s |
| RHS calls | 11,786 |
| Peak Python RSS | 122,884 KiB |
| Runtime | Python3.12.3 / NumPy2.3.5 / SciPy1.17.0 |
| Source pre/post coverage | 32/32 |
| Retained intervals | 33 |
| Photon gate, 저장된 native 계산 | 1.1374614327500605e-10 < 1e-8 |
| Photon gate, exact stored-term 재합산 | 1.1374619501580464e-10 < 1e-8 |
| Energy gate | 1.1442337713380224e-13 < 1e-8 |

최초 launcher는 system Python에 NumPy가 없어 native를 시작하기 전에 실패했다. 올바른 기존 venv로 연결한 뒤 실제 native 한 실행이 완료됐다. 이력과 최초 오류는 보존했다. Native 내부의 4개 trial-state domain rejection(event10/11/12/32, retry0)은 후속 retained interval과 구분한다. 성공한 전체 실행을 오류가 없었던 실행으로 기록하지 않는다.

| Endpoint | Native age32 | 기존 native age64 | age64 기준 상대차 |
|---|---:|---:|---:|
| N [photons/H] | 2.260563358299723e-10 | 1.2909104481275381e-9 | 0.8248861211419689 |
| U [eV/H] | 1.250278763896144e-8 | 5.999589648241735e-8 | 0.7916059535400799 |
| Temperature [K] | 7963.15976899287 | 7963.159582677747 | 2.339713549896287e-8 |

18개 공통 pre/post 관측의 N/U 차이도 endpoint와 비슷한 크기다. 보존 gate는 큰 source·absorption 합의 수지를 검사한다. 작은 survivor 자체의 해상도 오차를 보장하는 조건이 아니므로 gate PASS와 finite-neighbor FAIL은 양립한다. 원 rtol/atol, RK, source schedule, photon/energy1e-8와 비교 목표0.005는 바꾸지 않았다.

## 3. 정확한 저장 이력에서 residual의 위치를 분리

출생 전후의 photon invariant를 `I=N+sum(photo)-sum(injected source)`로 정의했다. 각 저장 binary64 항을 정확한 dyadic Fraction으로 변환하고, 출생 jump J와 출생 사이 변화 H를 분리하면

`I_end - I_init = sum(H) + sum(J)`

가 정확하게 성립한다. 초기 photon·photo가0이라는 가정은 실행된 source의 초기화와 그 SHA에 연결했다. 모든32 pre-state와 마지막 endpoint의 interval N·clock·active·accepted-state photo counter, 총33개 연결을 대조했다.

| 저장 이력 항 | Exact Fraction의 decimal 표시 |
|---|---:|
| Endpoint I | 1.6596188359096910e-14 |
| sum(H) | 1.6596175588774037e-14 |
| sum(J) | 1.2770322873736215e-20 |
| sum(abs(J)) | 3.2955571922167330e-20 |
| Telescoping residual | 정확히 0 |

이 데이터에서 endpoint residual은 출생 jump 절댓값 합보다 약 503,593배 크다. 출생 시 gas·nonbirth·ledger 좌표 bits는 보존돼도 재구성된 총 photon 합에는 작은 저장 산술 차이가 남는다. **출생 jump만으로 endpoint residual을 설명할 수 없다.** H에는 integration, reconstruction/RHS 연산, 출력 변환 등의 영향이 함께 있으므로 H를 순수 truncation error나 full roundoff bound로 이름 붙이지 않는다. 기존 age64에는 explicit source events가 없어 그 분해는 INCOMPLETE로 남긴다.

두 실행의 차이도 `DeltaN=DeltaS-sum(DeltaPhoto)+DeltaI`로 정확하게 닫힌다. Delta=32−64이고 아래는 모두 native64 N으로 나눈 값이다.

| 항 | 부호 있는 값 |
|---|---:|
| Delta N | -0.824886121141968939 |
| Delta source | -0.000133681986259923 |
| -sum(Delta photo) | -0.824742659650618901 |
| Delta residual | -0.00000977950509011548 |

이 표는 저장 endpoint 차이의 수지다. Absorption response 자체의 continuum 정확도나 그 원인별 오차 경계를 새로 발행한 것은 아니다.

## 4. 실제 survivor age와 v8 고정 모형의 대응

| Native survivor 통계 | age32 | age64 |
|---|---:|---:|
| N-weighted mean age [s] | 2.6853664785442347e11 | 1.3773461326234178e11 |
| U-weighted mean age [s] | 2.6981198321101004e11 | 1.3967325373324636e11 |
| 마지막 cohort N fraction | 0.9933973814 | 0.9820776026 |
| 마지막 cohort U fraction | 0.9911881982 | 0.9759776575 |

평균·centered variance·quantile은 각 native population 자신의 N/U mass로 정규화했다. 저장 cohort 합과 endpoint 합의 작은 차이도 정확한 값과 사용한 consistency tolerance를 함께 남겼다. 이 native 통계는 outward certificate가 아니다.

Native survivor는 최근 출생에 집중돼 있다. V8 sensitive32−64의 N/U 차이는 새 native32−64와 수치적으로 가깝지만, 이를 자동적인 모형 전달 경계로 사용할 수는 없다. V8는64 template weights를 고정해 clock만 묶고, native32는32 midpoint에서 source를 다시 계산한다. V8의 endpoint opacity·energy는 고정되어 있고 native gas·geometry는 진화한다. Native quadrature는 RHS에서 two-moment spectrum을 재구성하므로 endpoint node 번호가 영속 photon label도 아니다.

특히 v8 passive4096 node의 endpoint energy는 HI fit threshold13.60eV 아래지만, q=0 redshift 관계로 birth로 옮긴 spectral coordinate는 모두13.60eV 위에 있다. Endpoint passive를 경로 전체에서 반응하지 않은 native population으로 해석하지 않는다. Provider fit thresholds와 gas binding energies의 서로 다른 기존 역할도 유지했다. [독립 대응 계산](native_age32_analysis_20261020/reviews/r6/MAPPING.json)이 이 차이를 명시한다.

## 5. Source exposure에 대한 새 정확한 scalar 결과

상수 q>=0, lambda>=0, 초기 n(0)=0에서 `dn/dt=q-lambda*n`을 생각한다. 길이 h인 각 panel의 source qh를 midpoint에 주입하면, x=lambda*h에 대한 연속 source 대비 비율은

`R(x)=x/[2 sinh(x/2)]`

이고 같은 endpoint에서 h와 h/2의 비율은

`n_h/n_(h/2)=sech(x/4)`

다. 유한 geometric sum에서 직접 유도했고, `tanh(y)<y`로 R의 엄밀한 단조 감소를 확인했다. 두 오차의 선두 항은 각각 x^2/24와 x^2/32다.

Epsilon=.005에서 finite-neighbor 조건의 경계는 약0.400836030749612다. Continuum 조건의 root는 Decimal100 판정 및 독립 Decimal150 재검산으로 binary64 구간 **[0.3470181810994558, 0.34701818109945587]** 안에 있다. 이 구간은 정확한 binary64 epsilon 입력에 대한 수치 검산 결과이며 native certificate가 아니다. Neighbor 경계에서 coarse continuum 오차는 약0.00666332, fine continuum 오차는 약0.00167168이다.

같은 가정에서 양성 source step

`n1=n0*exp(-x)+q*h*phi1(-x)`, `phi1(-x)=(1-exp(-x))/x`

와 absorbed amount를 함께 구현해 `n1+A=n0+qh`를 확인했다. 작은 x에서는 expm1/급수, 큰 exposure의 weighted product에서는 scaled logarithmic branch로 중간 underflow를 피했다. Phi1 표현의 표준 근거는 Hochbruck–Ostermann(2010), DOI10.1017/S0962492910000048, 식(1.5)–(1.6)이며 [저자 원문](https://na.math.kit.edu/download/papers/acta-final.pdf)을 SciSpace·Exa로 찾아 실제 읽었다. Wolfram은 ratio·source ledger 항등식과 급수를 검산했다.

일반적인 prescribed lambda(t)에 대해서도 panel 내 누적 exposure 차이의 상한 D가 주어지면, 연속 source contribution은 midpoint contribution의 exp(-D)와 exp(D)배 사이에 있다는 양의 kernel-ratio 경계를 유도했다. 가정은 lambda∈L1([0,T]), q∈L1(panel), 유한 panel과 유한 D다. Native 적용에는 실제 경로 exposure와 source/reconstruction 대응을 더 확보해야 한다. Aggregate native 차이에 하나의 effective lambda를 맞춰 continuum 오차를 추정하지 않았다.

## 6. 구현·검증·독립 검토

새 단위는 `native_age32_analysis_20261020/`다. 기존 코드에서는 `src/photon_ledger_diagnosis.py`가 explicit `source_jumps.json`을 우선 읽도록 연결하고 해당 integration test를 추가했다. Root native Rust·physics·.github·다른 연구 lane은 수정 범위에 들어가지 않는다.

새 분석 테스트12개, 기존 photon integration suite12개(기존11+새1)가 PASS다. Unique 새 test methods는13개다. 최종 postprocess는 attempt004이며 이전 nonempty attempts를 보존했다. 구현 측9개 subprocess의 실제 wall 합은 **10.235522128990851/120s**, 독립 C9 검산 process는 **0.562281198s**다. Native trajectory/RHS, v8 STUDY/Decimal campaign, v7 benchmark의 새 실행은0이다.

R6는 finite integrability 가정 명시1건을 닫고 PASS_SCOPED다. C9는 마지막 endpoint 대조 누락, 중간 exp underflow, 거짓 float root bracket의3건을 실제로 재현하고 최소 수정 후 독립 재검산해 PASS_SCOPED(open0)다. 큰 scaled survivor 예제의 상대오차는 약2.38e-14로, universal correctly-rounded primitive라는 주장은 하지 않는다.

현재 chat runtime에서 Python3.12.14·NumPy2.3.5·SciPy1.17.0와 C++ 실행을 실제 확인했다. Rust는 PATH에서 발견되지 않았고 새 Rust build는 필요하지 않았다. 원 native 실행 runtime은 위3.12.3 기준으로 별도 보존했다.

Intake HEAD93aca의 전체 PR/push CI도 실제 조회했다. PR run39415863199와 push39415854273은 root native cargo fmt에서 실패했고 workspace tests는 skipped였다. 이는 scoped 분석·R6·C9 PASS와 별도다. V9 배송 commit의 실제 CI는 delivery receipt/readback에 기록한다.

## 7. 다음 연구 노드와 배송

이번 age32 실행·저장 자료 분석은 완료다. 즉시 추가할 native 실행은 발행하지 않는다. 다음 연구 노드는 `R_NATIVE_PATH_EXPOSURE_AND_RECONSTRUCTION_BRIDGE`이며, (i) time-varying native opacity를 덮는 exposure, (ii)32/64 source weight 대응, (iii)threshold crossing과 재구성의 관측량 전달을 명시해야 한다. 이것이 확보돼야 새 source representation 또는 연속 source 처리를 native에 적용할 수 있다. Native time8/16/32의 별도 representation HOLD는 유지한다.

CURRENT5와 DAG는 이 상태를 반영한다. 게시·C8/C10 양쪽 백업·최종 confirmation의 실제 완료 상태는 [DELIVERY_RECEIPT_CURRENT.json](DELIVERY_RECEIPT_CURRENT.json)을 따른다. C10은 source snapshot이며 별도 confirmation의 정확한 UTF-8 delta를 적용하면 최종 배송 tree가 된다. 복원·download·unpack은 다음 assistant가 자동 수행하며 사용자에게 파일 이동·해제를 맡기지 않는다. PR199는 draft/open, no merge/no force-push, expected-head fast-forward만 사용한다.

### V9 source와 백업 확정

Source `729a12c5fdee8d05e77f26b396f0464c945351e1`, 실제 부모 `93aca4cc483080b802fa85c9c44e43b9c85db5b7`, source task tree `0cd25257f9e0fe4cfe1ce4ea6f34f2f65929fab7`, source 파일2,242개다. C8/C10의 Drive·Dropbox 네 전체 readback에서 whole bytes/SHA256/ZIP CRC/모든 payload/source blob·mode·task tree가 PASS다. 두 C10의 native153/B1/deduplicated source161/vendor22·865 및 새 native32 원 tar도 PASS다. 실제 IDs·SHA·검증 근거는 [배송 receipt](DELIVERY_RECEIPT_CURRENT.json)에 있다.

중단 후 작업 환경이 초기화돼 게시된 Git source와 동일한 Dropbox ZIP에서 자동 복원했다. ZIP을 다시 만들거나 과학 계산을 재실행하지 않았으며, 복원한 bytes와 네 provider payload를 검증했다.

C8/C10은 이 source snapshot이다. 최종 metadata commit의 정확한 HEAD·tree·파일 수는 게시 뒤 별도 `REI_AGE_ENVELOPE_DELIVERY_CONFIRMATION_20261020_v9.json`에 기록하고, 그 정확한 UTF-8 delta를 적용해 복원한다. Confirmation 자신의 SHA와 provider IDs는 최종 사용자 인계 본문 등 외부 receipt를 따른다. 자기 자신의 hash를 내부에 넣지 않는다.

Source729a의 실제 CI는 PR39464799828/push39464790281에서 root native cargo fmt FAILURE, workspace tests SKIPPED다. 최종 metadata commit CI는 post-commit confirmation의 실제 readback을 따른다. Scoped 과학 검증 PASS와 구분한다.
