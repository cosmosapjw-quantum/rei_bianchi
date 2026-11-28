# HE-ANG-CCC-EXCHANGE 결과 — scoped 승인과 현재 파일의 전달 메타데이터

## 확보한 범위

새 CCC equal-sharing source-convention adapter와 실제 TP Table I 산술 입력을
구현하고, 계획한 tests → source analysis → plot의 세 child를 각각 한 번
실행했다. 초기 14개 test method가 모두 PASS였고, C9가 발견한 oracle assertion gap을
고친 뒤 해당 test_05 한 개만 reserve로 다시 실행해 PASS했다. Source table 8행의 원래 수치
문자열과 이미 적용된 factor-four를 보존했다. 과학적 독립 R6는
PASS_AFTER_CORRECTION이다. Coding 독립 C9도 PASS_AFTER_CORRECTION이고
root는 PASS_SCOPED를 채택했다. 현재 전달 메타데이터의 20개 stage row는 COMPLETE_SCOPED다.
자체 delivery identity는 CURRENT_FILE_COMMIT이며, 최종 사용자 보고는 실제
D/E 게시·readback과 B3 이중 ACK 뒤에 한다.
이는 조건부 구현 수용이며 물리 공급자 승격을 대신하지 않는다.

부모 HE-ANG과 HE-ANG-SOURCE-PAYLOAD는 SOURCE_INPUT_PENDING이다.
`physical_provider_admitted=false`, 전체 물리 목표 완료율은 미정이다.
새 full H angular payload, CCC/BRM/Hex solve 또는 IVP를 만들지 않았다.

## 식과 구현

제어 식은 `THEORY_KO.md`의 (1)–(6)이다. 같은 spin의 raw CCC outgoing-argument
pair a,b에 대해 U=|a|²+|b|², C=|a+s b|², D=|a−s b|²를 직접 계산한다.
원전 v3 Eq.(26)의 인쇄 부호와 달리 정확한 항등식은 2U=C+D다.
a=1+i,b=2−i에서는 S0의 (U,C,D)=(7,9,5), S1은 (7,5,9)다.
처음 author draft의 (7,10,4)는 실행 전에 교정했다. 그 오류와 최초 reviewer
informal PASS의 한계는 R6/R7 원문에 보존했고 실행비용을 리셋하지 않았다.
원전 곡선 계산이나 다른 version의 오류로 확대해 주장하지 않는다.

`code/ccc_exchange.py`는 raw pair, 이미 coherent인 density, phase 없는
intensity pair를 구별한다. raw pair는 자체 common phase provenance를
요구하며 phase를 재구성하지 않는다. coherent density는 그대로 보존하고,
spin_average는 적용 여부에 따라 1/4,3/4를 정확히 한 번 적용한다.
서로 다른 source/producer/kinematics/preparation, energy point, unit 또는
measure의 channel 결합은 거부한다. spin 사이의 상대 위상은 incoherent
mixture에 필요하지 않다. exact decimal outgoing energy가 같아야 하며
near-sharing tolerance나 finite-bin 복원은 사용하지 않는다.

Quadratic은 mantissa×2^exponent로 보존한다. ordinary binary64가 범위 밖이면
float는 null이고 OVERFLOW/UNDERFLOW를 명시한다. 성분별 scaled 합·차를
직접 제곱하므로 C=2U−D의 소거 뺄셈으로 C를 만들지 않는다. U=0의 eta는
null이다. 비유한 입력, 음수 density/error radius를 거부한다.

위상이 없을 때는 단일 C 대신 이론적인 정확한 free-phase range를 반환한다.
가까운 A,B의 lower endpoint는 rationalized expression을 사용한다.
Complex-error disks는 지정된 반지름에서 결정론적 enclosure를 계산한다.
Binary64 endpoint는 고정 5e−13 scaled numerical 기준에서 검산했으며
기계적 directed-rounding certificate나 모든 mixed-scale 입력의 상대오차
보장을 주장하지 않는다.

## 실제 검증과 실행

`results/test_report.json`과 immutable child stdout/stderr를 보존했다.
14개 test method가 다음을 검산했다.

- 인쇄 부호 반례, 두 spin, 30개 별도 Fraction complex-algebra grid case.
- swap와 common phase invariance, destructive/zero amplitudes, zero eta.
- 1e308/1e−308 scale 및 큰 성분 소거 뒤 작은 coherent remainder의 표현 상태.
- free-phase endpoint, nextafter로 만든 거의 같은 A,B의 Decimal100 참조.
- complex-disc 경계 witness와 zero-centered 큰 error disk.
- raw/coherent/preweighted 경로의 동일한 spin average와 가중 정확히 한 번.
- phase 없는 intensity의 interval-only 결과, source/point/unit/measure mismatch,
  unequal-sharing/nonfinite/negative 입력 거부.
- 실제 Table I의 이미 4CCC인 값을 새 factor 없이 보존.

독립 oracle은 kernel에서 가져오지 않은 Fraction 복소수 대수와 Decimal100
near-equal square-root reference다. 모든 assertion은 통과했다. 테스트가
측정하지 않은 최대 오차를 숫자로 꾸미지 않는다.

실제 analysis는 printed data 8행과 제조한 phase point 65개를 별도 저장했다.
65점의 max |2U−C−D|는 8.881784197001252e−16이었다. 이는 해당 제조 controls의
관측값이며 물리적 calibration 오차가 아니다.

| 실제 child | CPU seconds | Wall seconds | 판정 |
|---|---:|---:|---|
| 01_tests | 0.054267 | 0.068218467990 | PASS |
| 02_source_analysis | 0.033651 | 0.036370955000 | PASS |
| 03_plot | 1.266430 | 1.270911768996 | PASS |
| 04 C9-01 targeted test_05 reserve | 0.055673 | 0.068160983996 | PASS |
| 측정 합계 | 1.410021 | 1.443662175981 | PASS |

새 전용 cap CPU8/wall30의 측정된 네 child+runner 구간 합계는 위와 같다.
계획한 세 child 뒤 C9-01의 진단된 validation assertion repair 한 번만
reserve로 실행했다. Kernel은 변경하지 않았고 전체 14method/analysis/plot을
재실행하지 않았다. 원래 test05의 expected_C≈4e−616 비교가 기본 absolute
scale floor1e−300 때문에 magnitude fidelity를 엄격하게 검산하지 못했다.
이를 scale=expected_C로 바꾸어 frozen5e−13 normalized 기준으로 검산했다.
원래14PASS와 이 assertion gap/교정 근거를 함께 보존했다.
각 child는 CPU2, wall5/5/10/10(마지막은 reserve), memory512MiB,
threads1 제한을 사용했다.
과학 child 실패·측정 cap overshoot·새 IVP·old suite replay는 0이다.
Reserve 최초 runner 호출은 기존 empty RUN.lock 때문에 START/child 전에
FileExistsError로 중단됐다. root가 세 child의 실제 FINISH/PASS와 single-owner
상태를 근거로 해당 task lock만 stale로 판정하여 제거를 승인했다. 이 실패는
과학 child가 아니며 부모 CPU비용은 UNKNOWN_NOT_ZERO다. 그 도구 응답의
reported wall0.000036474s는 process-level timer가 아니므로 별도로 보존했다.
Host 준비·문서 I/O의 미측정 비용도0으로 바꾸지 않는다. 따라서
end_to_end_cpu_cap_established=false이며 완전한 전체 CPU합계는
known-plus-unknown이다. Ledger의 측정 합계는 리셋하지 않는다. plot의 Matplotlib
config 경로가 writable하지 않아 임시 cache를 사용했다는 warning은 실제
stderr에 보존했다. 종료0이며 추가 render/환경수정 replay는 하지 않았다.

R7 Wolfram은 root의 실제 evaluator 1회이며 별도 context 호출 1회도
`evidence/EXTERNAL_TOOL_ACCOUNTING.json`에 기록했다. corrected identity residual은 두 spin
모두0이다. toolwall8.981s, 보고된 body CPU0.066279s/wall0.066602s와 전체
remote CPU UNKNOWN_NOT_ZERO를 구별한다. 비음수 전제가 빠진 optional phase
endpoint 출력과 warning은 NOT_ADOPTED이며 재호출하지 않았다.
이전 ledger의 비용·실패·unknown은 hash-bound reference로 보존하고 새
allocation에 이전 잔여량을 옮기거나 전체 비용을0으로 바꾸지 않았다.

## 실제 source Table I

Stelbovics arXiv:physics/9905020v1 Table I p.4의 TP S-wave singlet energy DCS다.
E는 total three-body energy이고 unit은 pi*a0²/Ry다. incident lab energy,
실제 full H TDCS 또는 finite-mass dynamics로 바꾸어 읽지 않는다.

| E/Ry | N | Npos | Published 4CCC | Printed BRM | Published/BRM |
|---:|---:|---:|---:|---:|---:|
| 2 | 20 | 8 | 0.0172 | 0.0140 | 1.2285714286 |
| 2 | 30 | 13 | 0.0145 | 0.0140 | 1.0357142857 |
| 2 | 40 | 18 | 0.0137 | 0.0140 | 0.9785714286 |
| 2 | 50 | 24 | 0.0135 | 0.0140 | 0.9642857143 |
| 3 | 42 | 19 | 0.0072 | 0.0068 | 1.0588235294 |
| 3 | 44 | 20 | 0.0081 | 0.0068 | 1.1911764706 |
| 3 | 46 | 22 | 0.0069 | 0.0068 | 1.0147058824 |
| 3 | 48 | 23 | 0.0069 | 0.0068 | 1.0147058824 |

비율은 Decimal60으로 printed decimals를 나눈 산술이다. 새 solver나
오차 추정·엄밀한 수렴률·단조 수렴을 의미하지 않는다. N,Npos와 원문 decimal
문자열은 CSV와 JSON에 그대로 있다. 표의 factor-four를 다시 곱하지 않았다.

## 그림 확인과 남은 단계

`figures/ccc_exchange_source_controls.png`와 SVG를 한 번 생성했고 실제 PNG를
열어 보았다. 두 패널과 축/범례/출처 구분이 읽힌다. 왼쪽은 제조된 a=1,
b=exp(i phase)의 singlet/triplet control과 이론 phase range다. 오른쪽은
실제 printed 4CCC/BRM 비율이며 3Ry sequence의 비단조성을 그대로 표시한다.
Source TP 자료를 full H angular payload로 오해하지 않도록 caption에 적었다.

B1은 실행 전 preparation 15/20를 실제 Dropbox와 Drive 양쪽에 저장하고
40,303 bytes의 metadata size를 readback했다. Receipt는
`delivery/B1_BACKUP_ACK.json`이다. 실제 Science S는
`63706d605ddfc5d313ca310b09b5fd54a4efdbf4`이고 draft PR95로 게시했다.
Central C는 `d5aa6c94a77b5687052d3d6902d140e2df9ef798`이며 최신 CR-N5
영수증을 포함한 `f3ff95c4ddbdc4279223929a777072ec4eace577` 위에 추가했다.
다른 39개 node, 원래 HE-ANG 계약·의존성과 기존 관측을 보존했다.

B2는 S의 65개 파일과 C의 정확한 3개 파일, 게시 receipts와 복원 자료를
보존한다. Archive는 278,842 bytes, 72 members, SHA256
`21303684dbb2a0bed96d368802c70093cd343ccd644c53710036f16712c881f0`다.
Drive `1QuA8qmz8tOuLcQTAIozQEI0Jy-3pjBkV`와 Dropbox
`id:BSpOijBcT10AAAAAAD_9JQ` 양쪽의 완료 ACK와 독립 metadata size readback이
일치했다. 별도 remote SHA256는 반환되지 않아 독립 원격 hash 비교를
주장하지 않는다. `delivery/FINAL_BACKUP_ACK.json`은 이 실제 S+C backup의
범위를 기록하며, 미래 D/E 또는 B3가 이미 보존됐다고 주장하지 않는다.

현재 파일의 D 전달 메타데이터에서 20개 stage row를 COMPLETE_SCOPED로
기록했다. Actual D/E 게시와 B3 dual ACK는 후속 실제 receipts로 남긴다.
과학 code, source, numerical results, figure, 독립 review와 raw 실행은 S와
동일하며 추가 science를 실행하지 않았다. no_merge/no_activation을 유지한다.
C9-NB-01, C23E, CR-N5의 Drive ACK unknown을 포함한 다른 owner 상태와 기존
HE-X1/HE38/contract/Hex/DDCS20 근거·budget·실패·unknown은 보존한다.
