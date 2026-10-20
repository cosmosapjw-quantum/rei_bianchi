# 2026-10-20 v8: 관측량별 출생시각 경계와 평균 survivor age

## 새 결과

고정 source·opacity 모형에서 energy, HI/HeI/HeII 누적 photoevent, 첫째·둘째 age moment, 평균 survivor age의 출생시각 오차를 실제 outward interval로 평가했다. 이전에는 일부 경계가 이론에만 있었고 광자 수의 경계만 실행 결과로 존재했다. 이번에는 기존 57,344개 label과 clocks 8/16/32/64를 그대로 사용해 이 연결을 완성했다.

**Sensitive population의 age32 대 age64 평균 age 차이 절댓값은 약 `1.308129760096276e11 s`, 새 중심화 인증 상한은 `1.3585264601994653e11 s`다.** 기존 전역 상한 `4.2845291882191944e16 s`보다 약 315,381배 좁으며, 실제 차이의 약 1.03853배다. 이는 같은 고정 모형 안에서 오차 경계의 느슨함을 줄인 결과다. NCP native age32 실행 상태는 별도 READY로 유지한다.

연구 경로: `observable_certificates_20261020/`. 이론은 `THEORY_KO.md`, 입력과 실행은 `results/EXECUTION.json`, 전체 수치는 `results/STUDY.json` 및 `results/DECIMAL_REFERENCE.json`, 재현 명령은 `README.md`에 있다. 기준 Git HEAD는 `cf00684741eb612e35f987713c28937513d44d57`이며 게시한 새 source와 최종 배송 identity는 CURRENT receipt와 실제 PR199에 기록한다.

## 1. 연구 전에 새 결과부터 읽었다

현재 REI 브랜치 251개, 최근 갱신 PR 100개, VigilODE 브랜치 153개·PR 76개·최근 workflow 25개를 실제로 읽었다. Dropbox age 폴더 24개 및 Drive age 폴더 119개와 최신 v7 confirmation 전체를 확인했다. Confirmation의 실제 SHA256은 `4423349eec92b70265b3720c2ee857853926388cfa0a77fe201269901fd3981c`로 기존 최종 기록과 일치했다. 같은 immutable v7 ZIP의 이전 전체 payload 검증은 재사용했다.

새로 확인한 별도 lane의 결과는 다음과 같다.

| 대상 | 실제 새 근거 | 이번 연구와의 관계 |
|---|---|---|
| REI RUN19 Unit A | `f2996d02908e5a2e678fab0dc0efb3424fa86a99`; exact-T 공유/cache, 8 tests, 264 states×28 components parity, RHS/IPC 측정 | 새 IVP 0회, age32 reference와 별도 |
| LRS PR198 | `33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1`; FD preparation 재사용·bounded batch 실제 결과 | 해당 저장 summary의 root admission pending을 유지 |
| BASS_HE PR78 | `1765522318438e966e61d8a72f12084550da399d`; CSR·packed JVP 측정 | native pairs 0/4, 보호한 별도 lane |
| VigilODE PR76 | `6972f28aa4bcbe4c68dbba92e44ff58884545bca`; 성공 run39360536475, 312 cells/30 pairs | 39 CSV rows·30 paired medians 재계산 일치; 원 full states 검산은 재실행하지 않음 |
| VigilODE hybrid branch | `2b828f81512a11cc35229bc77453f305df33d268`; native_tests exit101/E0308 | 새 native benchmark 완료 근거 없음 |

VigilODE PR76은 이전 upstream 점검 이후, v7 최종 배송 이전에 완료되어 이번에 새로 확보한 결과다. 새 LRS/HE29 archive 네 개의 205 manifest payload를 실제 읽고 확인했다. 완전한 관련 인벤토리와 coverage는 `intake/cloud/INTAKE_V8.json`, `intake/upstream/INTAKE.json`에 있다. Dropbox 기존 38,285개 재귀 인벤토리는 변경 없는 부분에 재사용했고 Drive 오래된 dossier는 1,000개 조회 상한 뒤가 부분적이다. 다른 대화 검색은 실제 `ERROR`를 반환했다. 전체 대화나 모든 과거 백업을 읽었다고 주장하지 않는다.

확인한 범위에서는 새 native age32 완료 결과가 없었다. 완료된 age64·spectral128·v7 최적화 benchmark를 반복할 이유가 추가되지 않았다.

## 2. 관측량별로 필요한 식을 구현했다

같은 label의 두 age 중 작은 값을 `a`, 차이를 `delta`라 하고 `u=exp(-Lambda a)`, `v=exp(-Lambda delta)`라 두면 older-minus-younger 차이는

\[
\Delta n=-wu(1-v),\quad
\Delta(an)=wu[\delta v-a(1-v)],
\]

\[
\Delta(a^2n)=wu[\delta(2a+\delta)v-a^2(1-v)].
\]

실제 A/B 순서에 따라 부호를 적용한다. Energy 차이는 `E Delta n`, 종별 photoevent 차이는 `-(lambda_s/Lambda) Delta n`이다. 각 label의 절댓값을 합하면 해당 전체 관측량 차이의 상한을 얻는다. Signed 총차이도 함께 계산해 상쇄의 크기를 보존한다.

평균 age `mu=M1/N`에는 임의의 center `c`에 대한 항등식

\[
\mu_A-\mu_B=
\frac{\Delta M_1-c\Delta N+(c-\mu_B)\Delta N}{N_A}
\]

을 사용했다. `mu_B`의 outward interval에서 midpoint와 radius를 얻고, `sum |Delta(an)_i-c Delta n_i|` 및 `|Delta N|`의 상한, 양의 `N_A` 하한을 조합한다. A/B를 바꾼 경계와 기존 전역 fallback도 함께 계산해 가장 작은 유효 상한을 선택한다. Sensitive 평균에는 sensitive mass만 분모로 쓴다.

흡수율 0인 passive label은 `Delta N=0`이지만 `Delta M1`, `Delta M2`가 남는다. 이 경계 사례와 분모가 0인 경우를 명시적으로 다룬다. Number와 동일한 node energy를 쓰는 energy ledger도 outward interval에서 0을 포함한다.

## 3. 실제 평균 age 경계

아래 차이는 항상 coarse clock 값에서 clock64 값을 뺀 것이다. 상한은 절댓값의 상한이며 단위는 s다. 전체 유효 자릿수와 interval endpoint는 원 JSON/CSV에 보존했다.

| Population | 비교 | 독립 검산한 signed 평균 차이 (s) | 선택한 인증 상한 (s) | 기존 전역 상한 (s) |
|---|---:|---:|---:|---:|
| 전체 | 8−64 | +6.66644e10 | 6.32926e11 | 2.97789e14 |
| 전체 | 16−64 | +9.78471e10 | 3.71207e11 | 1.48954e14 |
| 전체 | 32−64 | +8.88229e10 | 2.37111e11 | 7.44388e13 |
| Sensitive | 8−64 | +9.22023e11 | 9.22060e11 | 3.50868e19 |
| Sensitive | 16−64 | +3.93992e11 | 3.94641e11 | 8.70761e17 |
| Sensitive | 32−64 | +1.30813e11 | 1.35853e11 | 4.28453e16 |
| Passive | 8−64 | −4.32203e10 | 5.28616e11 | 5.28616e11 |
| Passive | 16−64 | −1.02905e10 | 2.64310e11 | 2.64310e11 |
| Passive | 32−64 | −2.05811e9 | 1.32155e11 | 1.32155e11 |

Sensitive 부분의 centered bound는 실제 절댓값의 약 1.000039배, 1.001646배, 1.038526배다. 전체 평균의 실제 차이는 이 세 clock에서 단조롭지 않다. 전체 평균은 passive와 sensitive 평균의 survivor-mass 가중 평균이며 clock 변경으로 그 가중치도 바뀌기 때문이다. 이를 단일 continuum 수렴률로 맞추지 않았다.

Passive 부분에서는 centered 후보와 전역 fallback의 선택값이 같다. 출생시각의 signed 상쇄가 커서 label 절댓값 합 자체가 아직 느슨하다. 이 데이터의 모든 population에서 같은 정도의 경계 축소를 얻었다는 주장은 없다.

`results/NORMALIZED_MEAN_BOUNDS.png`는 실제 차이·선택 상한·전역 fallback을 세 population으로 나눠 보여 준다. 서로 수십만 배 이상 다른 값을 구별할 수 있도록 y축을 로그로 표시한다. 그림의 값은 저장된 수치에서 생성하며 추가 solver 실행을 사용하지 않는다.

## 4. age32 대 age64의 관측량별 결과

| 관측량 | Signed 차이 | Label 절댓값 합의 outward 상한 | 단위 |
|---|---:|---:|---|
| Survivor number N | −1.067277844595227e−9 | 1.2502515736716042e−9 | photons/H |
| Survivor energy U | −4.751013573005527e−8 | 5.736190034205418e−8 | eV/H |
| HI photoevents | +5.605586897830901e−10 | 6.481437802611539e−10 | events/H |
| HeI photoevents | +5.061364665264414e−10 | 6.011389173651114e−10 | events/H |
| HeII photoevents | +5.826882856955125e−13 | 9.688760453338186e−13 | events/H |
| 전체 M1 | −384.306095621994 | 17293.33950764273 | photon·s/H |
| 전체 M2 | −6.774813421015088e15 | 3.863205269455289e17 | photon·s²/H |

Passive의 N/U/photoevents 변화는 정확히 0이다. 따라서 위 다섯 관측량의 signed 차이는 sensitive와 전체에서 같지만, 평균 age는 population별 분모가 달라 다르다. 이 구분을 출력 스키마에서 유지했다.

## 5. 코드·검증·비용

새 코드는 별도 Rust binary source와 실행·검산·요약 도구다. 기존 v7 Rust source, 원 VigilODE 두 모듈, 22개 locked dependency, node CSV와 model JSON을 유지한다. 빌드는 scratch에서 원 crate를 복사하고 새 binary만 추가하는 offline/locked 경로다.

새 Rust fixture 10개, 전체 실제 입력에 대한 Decimal100 직접식 612개 scalar 비교, 수정 전후 scientific output의 모든 float bits 비교를 완료했다. Decimal 검산은 Rust의 stable 식 대신 각각의 endpoint exponential과 moment를 직접 계산한다. 검산 cache의 가장 큰 tau는 약 5452.864였고 모든 exponential을 양의 Decimal 값으로 유지했다. 이 유한 수치 검산은 이론의 일반 증명을 대체하지 않으며 구현 연결을 확인한다.

첫 실행에서 rate와 모든 age의 Cartesian product를 preload하는 불필요한 계산을 발견했다. 실제 node가 요청하는 조합만 계산하도록 한 번 수정했다. 고유 exponential 수가 346,945에서 34,625로 줄었고 관측 실행 wall은 42.269 s에서 13.422 s가 됐다. 두 실행의 과학 출력은 모든 float bits가 같아 기존 Decimal100 검산을 재사용했다. 이것은 한 쌍의 비용 관측이며 반복 benchmark의 성능 추정치로 제시하지 않는다. 처음 결과와 receipt는 `results/before_actual_request_cache/`에 남겼다.

현재까지 분석 실행 wall은 68.546 s/240 s다. 빌드와 fixture 비용은 별도 receipt로 보존한다. Peak RSS는 wrapper child의 누적 high-water 값이므로 개별 kernel의 독립 peak memory로 해석하지 않는다. 이전 v7 성능 캠페인·역사 전체 suite·native trajectory는 다시 실행하지 않았다.

R6 이론 검토는 PASS이며 문헌의 dimensionless 식에 weight를 곱하는 설명 한 곳을 교정했다. C9의 최종 구현 검토는 PASS이며 열린 지적은 0개다. C9-01은 `verify.py`·`summarize.py`의 명시적 `--results` 연결로, C9-02는 비어 있지 않은 실패 attempt output의 거절·원본 보존으로 닫았다. 실제 CLI negative control과 저장 수치·Fraction readback으로 확인했으며 새 study·Decimal·native 실행을 반복하지 않았다. 판정과 근거는 `reviews/c9/C9_RECEIPT.json`에 있다.

## 6. 외부 문헌·코드 재사용

- Catalano, Lijoi, Prünster (2020), EJS14, DOI `10.1214/20-EJS1746`, Theorem9와 proof Eq(30): exponential survival 차이의 인수분해와 Jensen bound. SciSpace 검색 후 Exa로 저자 원문을 읽었다.
- Habeck, Rudolf, Sprungk (2020), `arXiv:2004.07310`: 정규화 후 measure 안정성의 관련 원전. 평균 age의 식은 이번 고정 모형에서 직접 유도했다.
- 기존 VigilODE directed arithmetic과 v7 exact-rational exponential, Rayon indexed preload 구조를 실제로 재사용했다. 새 crate나 전체 ODE solver 교체는 이 단위에 필요하지 않았다.
- Wolfram evaluator는 핵심 항등식 다섯 개의 잔차 0과 passive 식을 확인했다. 도구의 undefined-symbol warning과 성공한 symbolic 결과를 함께 기록했다.

## 7. 배송과 다음 실행

현재 요청은 샌드박스 연구·코드·가벼운 검증·PR199 게시·이중 백업·인계다. 각 저장 단계의 실제 commit/provider/readback 상태는 `DELIVERY_RECEIPT_CURRENT.json`에, R1–R10/C1–C10과 다음 실행은 `contracts/NEXT_DAG_CURRENT.json`에 기록한다. 변경 전 CURRENT5는 이번 unit의 `baseline_current/`에 보존했다.

다음 native READY는 기존 **q0 age32, source8/n_mu8/transport16/time1, block-max/binary64, passive diagnostics ON, transport48, case/total cap1800s** 한 사례다. 현재 NCP device listing은 성공했지만 이번 연구에서 NCP SSH·native 실행은 하지 않았다. 동일 B1 binary·원 runtime과 원 rtol/atol·RK/source schedule·photon/energy1e-8 조건을 유지하며 사용자 수동 파일 처리 없는 인계는 `HANDOFF_CODEX_CURRENT_KO.md`에 있다.

Native age/time 정확도는 HOLD, 실제 nonlinear Grackle response bound는 NOT_ESTABLISHED다. 현재 고정 모형의 경계 결과와 별개의 의존성이다. Owner checkout, PR150/R9, LRS, BASS HHeD를 유지하고 PR199는 draft 상태에서 expected-head fast-forward 게시만 한다.

**PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.**

## v8 실제 배송 완료

v8 source는 `02767dc5e6c4b47883f590834aee38530852568d`에 게시했으며 2,152개 Git blob/mode, task tree `8fce099de816bdebb1dbd7bb22f87817ff50e9f5`, root/research의 다른 subtree 보존을 확인했다. C8/C10의 Drive·Dropbox 네 upload 및 서로 다른 네 전체 readback이 완료됐다. Whole bytes/SHA256/CRC/모든 manifest payload/source blob·mode/C10 전체 task tree/native153/B1/deduplicated source/vendor22·865 검증은 모두 PASS다. 실제 provider IDs·크기·SHA와 원 receipt는 `DELIVERY_RECEIPT_CURRENT.json`, `evidence/delivery_v8_20261020/`에 있다. Immutable ZIP에는 source 준비 시점의 pending CURRENT가 남고 이 완료 기록이 이를 대체한다. 이 배송 metadata의 identity는 자신을 담은 Git commit이며 exact HEAD와 UTF-8 restore delta는 별도 post-commit v8 confirmation에 기록한다. Confirmation 자체의 두 provider upload/readback은 별도 후속 단계다.

Source push/PR workflow는 변경하지 않은 root native cargo fmt에서 실패했고 workspace tests는 skipped다. Full PR CI green은 아니며 새 scoped C9 PASS와 구분한다. 세부 근거는 `evidence/delivery_v8_20261020/SOURCE_CI_READBACK.json`에 있다.
