# RUN17 durable science handoff

최신 delivery commit·ZIP·백업은 같은 디렉터리의 `RESUME_DELIVERY_KO.md`와 `DELIVERY.json`을 먼저 읽는다. 이 파일은 동결한 science snapshot이다. 사용자 제공 RUN13 checkpoint SHA 대신 실제 RUN16 HEAD `45ee7192b9d405214ec2650185aeaaa635e0fa13`에서 이어 왔다.

## 다시 계산하지 않을 완료 결과

- RUN13 M2 standard/tight: 전체 6,241 segments, 40,357 variables COMPLETE archived. checkpoint3071에서 재시작하지 않는다.
- RUN15 recovery 및 RUN16 gas-path sensitivity / prefix A·B·C는 원본과 delivery에 보존되어 있다. 이번 RUN17에서는 이 계산들을 재실행하지 않았다.
- RUN17 첫 birth panel native A/B: COMPLETE. 265 states, 252 reflection-pair cohorts = 504 physical rows, all48 cells. 실제 2개 coupled IVP, 578 RHS; residual 분석 800 RHS. 총 1,378회. 전체 campaign 0회.
- 새로운 집중 테스트: 5 dense/sign +4 comparison +3 Bernstein =12 PASS. Dense5는 실제 출력에서 전사한 receipt를 구분한다. 제조한 2변수 linear-decay test IVP는 native solve가 아니다.
- 정확 저장계수 Bernstein 검사: 24 gas pieces와 5,796 R-depth polynomials PASS. 각 piece의 이상적 실수 다항식 admissibility가 확립되었다.
- 독립 검토 1회 완료. 별도 검토자 계산·테스트 재실행 0회.

## 최신 실제 결과

코드 `z=(X−0.7)/(0.7004−0.7)`이며 cosmological redshift가 아니다. 구간 `[0.004989333151072248,0.02371416180174271]`은 first-birth outgoing → second-birth incoming이다. 초기 gas는 저장 RUN16 prefix-C, 그 실제 IVP error enclosure는 아직 없다.

`R`: native Control B의 dense reconstruction. `P`: original tight gas의 다섯 invariant coordinates에 새 PCHIP를 적용하고 `Y0+L(q−q0)`로 올린 경로. P는 RUN16의 14성분 독립 PCHIP와 동일한 객체가 아니다.

| 두 번째 birth 직전 결과 | 값 |
|---|---:|
| R HI/initialH | 0.899996948987685 |
| R T | 9999.735053555296 K |
| `(HI_P−HI_R)/HI_R` | −3.800718802625755e−6 |
| `T_P−T_R` | +0.12465231681380828 K |
| R 첫 birth survivor | 4.3727855891600966e−7 /initialH |
| 첫 birth survivor `(P−R)/R` | +3.095494720825061e−6 |

HII 좌표 차이 3.420635326378818e−6는 초기차 1.4141500097458737e−6와 P의 적분 defect 2.007717655822495e−6가 주요 항이다. Native forcing 적분차 −1.231282605522407e−9와 photo forcing 적분차 −1.0565857009456857e−12도 직접 계산했다. R defect도 유지했다. 5좌표 최대 closure 2.307910671383792e−17은 부호·회계 일관성이다.

## 즉시 사용할 파일

- `native/control_B_execution01/FIRST_BIRTH_CONTROL.json`와 인접 `ACCEPTED_AND_DENSE_STATE.npz`: lossless23piece dense reference. JSON의 state identity와 manifest에 원본 크기·SHA가 있다.
- `residual/analysis_execution01/FIRST_BIRTH_RESIDUAL.json`, NPZ 및 native RHS trace: 부호 있는 forcing/defect 적분, 17samples, GL contrasts, 3pointJacobian.
- `residual/domain_execution01/RECONSTRUCTION_DOMAIN_CERTIFICATE.json`: exact rational admissibility.
- `theory/FIRST_BIRTH_RESIDUAL_TRANSFER.md`, `theory/INDEPENDENT_IMPLEMENTATION_REVIEW.md`: 유도와 한 차례의 검토.
- `SOURCE_IDENTITY.json`, `SCIENCE_MANIFEST.json`, `REPRODUCE_KO.md`: 원본·실행코드 binding, 각 byte hash와 정확명령.

`comparison_propagator.py`의 실행본은 `residual/history/comparison_propagator_executed.py`에 보존된다. 게시본은 docstring만 보완했으며 executable AST는 동일하다. 과거 결과에 기록된 source SHA를 게시본 SHA로 해석하지 않는다.

## 다음 실제 미완료 원래 DAG 노드

**P4-S4C-SPECTRAL-EDGE-SUPPORT / SUBTHRESHOLD-SURVIVOR-RESOLUTION** 안에서, 첫 birth 이후 **연속 gas/depth residual estimate와 admissible feedback tube**가 다음 대상이다. 정확 다항식 인증을 center 정보로 재사용하고, native rate derivative·residual variation·Jacobian block bounds를 실제 tube에서 제한한다. 양의 가중 residual integral을 제한하는 경로도 가능하다. prefix exact-IVP 초기 불확실성과 polynomial piece representation jumps를 포함한 뒤 다음 birth·threshold로 전파한다.

현재 3점 Jacobian 및 GL10의230점 defect는 상한이 아니다. 저장된 polynomial의 piece별 admissibility는 exact IVP error 또는 인접 piece의 정확 연속성을 증명하지 않는다. P optical quadrature remainder와 floating exponential enclosure도 별도 필요하다. 전체 continuous source로 확장할 때는 gas/photo forcing의 spectral quadrature defect를 추가해야 한다.

Full native uniform M4, continuum spectral error bound, small final sub-H component convergence는 미해결이다. 기존 M1/M2 작은 sub-H survivor 차이 약51.99%를 이번 first-birth observable로 대체하지 않는다. Angular·birth-time continuum·whole donor domain·full EoR·Einstein·FLRW-CONV·BI-SIGNED·ISO-COUPLE full·Li/Be·nuclearT1–T8와 원래45/26DAG를 유지한다.
