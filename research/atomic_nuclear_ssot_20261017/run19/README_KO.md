# RUN19 — T 계수 재사용, 경량 cubic table, Li/Be 및 19개 목표 반응

**선택한 optimization/coding 단위 A·B·C의 실제 구현·유도·검증·게시·백업을 완료했다.** 기준 physics/source는 RUN18 `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e`이며, 게시 branch는 `research/rei-run19-rate-acceleration-20261020`, draft PR은 [211](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/211)이다. 최종 과학/source commit은 `e540256ecf77df1c88fccb57b81d5d60110f367c`다. 최신 게시·백업 상태는 [최종 receipt](delivery/UNIT_B_FINAL_DELIVERY.json)와 [최종 DAG delivery](DAG_PROGRESS_FINAL_DELIVERY.json)를 따른다. 개별 보고서의 PENDING 문구는 보존한 게시 전 시점을 가리킨다.

## 최종 백업 확인

[Google Drive 전체 패키지](https://drive.google.com/file/d/1pRPhitdAFfEU8HrSC02uXXVXwRI1U8wk/view)와 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN19_FINAL_T_RATE_ACCELERATION_LI_BE_20261020.zip` (`id:BSpOijBcT10AAAAAAD_SVw`)에 보존했다. 두 서비스에서 각각 실제 전체 GET으로 내려받은 25,344,988 bytes의 SHA-256이 모두 `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62`와 일치했다. ZIP은 1,175항목이며 경로·형식·mode·CRC·모든 manifest SHA를 대조했다. 이 다운로드 검사는 원격에서 과학 계산을 재실행했다는 뜻이 아니다.

## 완료한 구현

| 단위 | 실제 완료 범위 | 상세 증거 |
|---|---|---|
| A | H/He/D prepared T bundle 공유, exact EOS-T cache, caller-owned ordered batch, text IPC batch | [Unit A](execution/unit_a/UNIT_A_REPORT_KO.md) |
| B | 32,769-node guarded value-cubic logT table, source-bound cache 저장/로딩, native opt-in, SIMD 및 1/2/4 workers 측정 | [통합 보고서](UNIT_B_FINAL_KO.md), [native 기록](execution/unit_b/UNIT_B_REPORT_KO.md) |
| C | 기존 PR150 Li6/Li7 number-rate source의 compatibility forwardport, VF1996 Be RR 3채널, 전체 19개 반응 목표 보존 | [Li/Be](metals/README_KO.md), [19반응 계약](metals/network/TARGET_NETWORK_19.json) |

`native/`는 원래 RUN13 native 91개 파일에서 만든 명시적 개발 fork다. 원래 RUN13 owner 91개 bytes와 main/production은 바꾸지 않았다. 기존 Direct 기본값 및 STEP owner를 유지하며 새 경로는 `--rates cubic --table-cache FILE`로 선택한다. Density, electron/heat assembly와 radiation/photo/geometry 상태는 T table에 저장하지 않는다. 계수의 T 의존성과 반응 flux의 상태 의존성을 구분한다. Savin charge-exchange 등 아직 direct인 경로의 table 이식 의무도 남아 있다.

## 실제 수치 결과

- 원래 assembly 대비 A Direct의 264 상태 × 28출력은 bit-equal였다. B 연결 후 보존한 9,216 입력에서 Direct/loglinear 각각 258,048개 f64 출력도 A와 bit-equal였다.
- Cubic 기본 table의 196,636개 실제 coefficient query에서 최대 상대차는 `1.532909445522450e-8`이었다. Payload는 기존 loglinear `9,109,624`에서 `4,358,273 bytes`로 줄었다.
- 같은 executable, N=32,768, one-worker 계수 query 중앙값은 ordered logT에서 Direct/loglinear/cubic `446.19/140.07/61.22 ns`, random logT에서 `492.68/576.36/127.84 ns`였다. 같은 입력·worker 수에서 비교했으며 전체 IVP 속도가 아니다.
- 실제 gas 9,216점에서 cubic H net 상대차 최대 `3.827730095e-9`, chemical net `1.399808165e-8`, scaled signed energy ledger residual `3.591488474e-16`였다. Cancellation 때문에 positive flux·절대오차·ledger를 따로 보존했다.
- Ideal exact-source cubic 보간의 전역 channel bound는 `8.512614813784016e-8`이다. 별도 stored-node arithmetic 3,072개 유리수/interval 검사에서 최대 상대 roundoff는 `2.9515449298378586e-16`, 최대 directed upper는 `8.824802554719956e-16`였다. 실제 source evaluation·log-grid/query 오차·coupled IVP를 모두 포함한 f64 bound는 미완료다.
- Li와 Be의 실제 coefficient 6,177행, number contribution 1,282행을 보존했다. Li/Be table 상대차 최대는 각각 `1.0729097573713986e-6`, `7.877227004016163e-8`였다. BeI RR와 핵붕괴·광핵·포획·전체 thermal/photo coupling은 이 단위의 구현 범위 밖이다.

각 최대값이 같은 입력에서 발생한다고 가정하지 않는다. 과거 RUN13 m2 standard/tight 이력과 RUN16–18 완료 계산은 다시 실행하지 않았다. 이번 native IVP 수는 0이다. 기존 m1/m2의 sub-H-fit-edge 약51.99% 차이와 spectral continuum 미확립 상태는 그대로다.

## 실제 검증과 보존한 실패

실제 focused 검사는 A 6 integration+2 server, generic cubic 5, B 4 integration+관련 server 2, Li/Be 10, 이론 Python 3이다. B의 server 2개는 A의 동일 test identity이며 unique 수에 두 번 더하지 않는다. 기존 Rust160 및 역사적 Python 전체 suite는 새 PASS로 표시하지 않는다.

초기 cubic MAGIC 길이 compile 오류, Be golden 비교의 최초 1개 실패, 초기 외부 SIMD witness의 vector 0개 기록은 보존했다. 수정 후 필요한 범위만 실행했다. Rounding JSON의 domain `[1,0]`은 출력용 변수 shadowing 오류이며 실제 입력 `[1,1000000]`과 계산 결과를 구분한 [addendum](execution/unit_b_final/ROUNDING_DOMAIN_METADATA_ADDENDUM.json)을 따른다. 원래 결과를 덮어쓰지 않았다.

## 재사용·복원·게시

`sha2=0.10.9`와 정확한 Cargo.lock을 실제 적용했고 10개 registry package의 614파일을 license와 함께 vendor backup에 보존했다. 새 source copy, 빈 Cargo home/target, 보존 vendor의 `--offline --locked` build는 6.04476초에 성공했고 META-only가 기존 cache identity를 확인했다. 새 binary bytes는 기존 실행 binary와 달라 source/cache 호환성으로만 기록한다. 전체 역사 Git-only 복원이나 byte-identical binary 재현을 주장하지 않는다.

[재현 명세](REPRODUCE_UNIT_B_FINAL.json)는 실제 repo-relative source closure, 원래 RUN13 91파일, RUN18 VigilODE directed.rs와 LICENSE, vendor, 정확한 명령과 toolchain 요구를 명시한다. 작은 source·텍스트 결과·manifest는 Git, 큰 raw CSV/gzip/cache·이미지·실제 ELF와 vendor 원문은 전체 archive에 보존한다. Archive manifest는 archive-only 항목까지 해시로 연결한다.

Unit A source `f2996d02908e5a2e678fab0dc0efb3424fa86a99` 및 Unit C source `ffcb3709c3d19d577b1e6eb69dd0ce4d4d94d85a`는 이미 별도 게시·두 백업을 완료했다. [A receipt](delivery/UNIT_A_DELIVERY.json)와 [C receipt](delivery/UNIT_C_DELIVERY.json)는 업로드 성공과 다운로드 byte readback 미실행을 구분한다. B 최종 receipt가 aggregate archive의 실제 검증 단계를 기록한다.

## DAG 및 다음 작업

원래 45-node/26-node DAG를 줄이거나 재정의하지 않았다. [B overlay](DAG_PROGRESS_UNIT_B.json)는 선택한 최적화 단위와 원래 과학 의무를 구분한다. 사용자 이미지의 오른쪽 19개 반응 ID도 모두 보존했으며 7↔13, 8↔12, 11↔19의 forward/reverse 중첩만 명시했다.

다음 원래 노드는 **동일 first-birth panel의 original-owner continuous interval RHS와 admissible gas/depth feedback tube**다. Source-node/log-grid/query interval, 실제 interval Jacobian, whole-time residual, logarithmic norm, prefix 초기 불확실성, event maps 및 gas/photo spectral forcing이 필요하다. M4, continuous spectral/angular/birth-time, whole donor/full EoR/Einstein, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8은 그대로 남는다. 즉시 재개용 최소 지침은 [RESUME](RESUME_KO.md)에 있다.

Inventory 초기 R9의 “Li/Be 6개” 요약은 원래 contract의 H I/He I/He II/Li I/Li II/Li III 범위를 잘못 읽은 것이다. 원문과 [R9 정정](inventory/R9_SCOPE_CORRECTION.json)을 함께 보존했다.
