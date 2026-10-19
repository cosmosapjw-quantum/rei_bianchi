# BASS-REACTIVE-03: independent native output audit

판정: **PASS_SCOPED**. 독립 Python 감사기는 완료된 12개 native 이력의 496개 행과 예상된 CX work-limit 사례 1개를 검토했다. 최종 CSV·receipt·stderr만 읽었으며 `.running.*` 파일은 최종 산출물에 포함하지 않았다. 이 감사는 원 연구 source나 native 데이터에 쓰지 않았다.

## 원본 식별과 실행 판정

- 13개 사례 모두 raw CSV SHA-256, receipt 행수, 계획한 완료 행수, 최종 행, stderr, 실행 명령 계약이 일치했다. 읽기 전후 bytes도 동일했다.
- 12개 성공 사례는 exit code 0이며 모든 행에 정확한 54열 schema가 있었다.
- `ap_cx_worklimit`은 exit code 2, 빈 CSV와 0개 accepted 행, `Cx(WorkLimit)` stderr를 보존했다. 판정은 `RESOURCE_LIMIT_CX` 및 `NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION`이다. 이 사례에는 수치 이력이 없으며 수렴 실패나 물리적 해 부재로 재분류하지 않는다.
- 모든 receipt의 binary SHA-256이 같았다: `57d2056db8d0ebafa40274bd4e254422ac24dcad4aedd4a635863b34604c8003`. 이는 receipt 간 identity 확인이며 바이너리를 재실행한 검증은 아니다.

## 독립 원장 재구성

CSV의 primitive 에너지 열로 다음 합을 재구성했다. driver의 `maxN` 및 `maxE` 열은 진단값으로 기록했으나 합격 판단의 oracle로 사용하지 않았다.

```text
N residual = surviving photons + absorbed photons - source photons
species residual = HI events + HeI events + HeII events + DI events - absorbed photons
E total = photon + gas thermal + gas binding + escaped + signed CMB reservoir
E expected = initial total energy + source energy + signed geometry work
```

초기 광자수가 0인 native initial 상태를 사용한다. Number/species 잔차는 source photon count로, 에너지 잔차는 현재·예상·초기 총에너지 크기의 최대값으로 정규화한다. 상대 허용 한계는 `3e-10`이었다.

| 전 496개 행의 최대 상대 잔차 | 독립 계산 |
|---|---:|
| Photon number | 9.700747050909076e-15 |
| Total energy | 1.041528045063209e-15 |
| Species event sum | 5.183970680370968e-16 |

Geometry work와 CMB reservoir는 원래 부호를 가진 에너지 항으로 합산했다. 열·화학 변화량도 부호를 유지했다. 작은 total-energy 잔차는 각 항의 절대 정확도나 시간·분광 수렴의 증거로 해석하지 않는다.

## 사례별 최종 광자수

최종 시각은 모든 완료 이력에서 `8e12 s`다. 아래 수는 독립 감사기가 최종 raw CSV에서 읽은 reference-comoving photon density다.

| 사례 | Accepted rows | 최종 photon density (m^-3) | 최대 독립 N 상대 잔차 | 최대 독립 E 상대 잔차 |
|---|---:|---:|---:|---:|
| `off_gl2_n32` | 32 | 2.559394778750123e-09 | 3.143e-15 | 5.786e-16 |
| `off_gl4_n32` | 32 | 8.403585747093016e-09 | 1.241e-15 | 4.629e-16 |
| `ap_n16_r2` | 16 | 1.003869784688376e-08 | 4.201e-15 | 5.786e-16 |
| `ap_n32_r2` | 32 | 1.003824263879714e-08 | 9.092e-15 | 3.472e-16 |
| `ap_n64_r2` | 64 | 1.003801592303224e-08 | 6.416e-15 | 9.258e-16 |
| `ap_n128_r2` | 128 | 1.003790750740001e-08 | 9.701e-15 | 1.042e-15 |
| `ap_n32_r1` | 32 | 1.003824410851938e-08 | 2.453e-15 | 3.472e-16 |
| `ap_n32_r4` | 32 | 1.003824245807652e-08 | 6.859e-15 | 3.472e-16 |
| `ap_n32_r8` | 32 | 1.003824244100916e-08 | 7.648e-15 | 4.629e-16 |
| `ap_n32_r2_spectrum` | 32 | 1.004115550692643e-08 | 7.256e-15 | 5.786e-16 |
| `ap_n32_r2_opacity8` | 32 | 1.003824263879403e-08 | 2.733e-15 | 3.472e-16 |
| `ap_n32_r2_plus` | 32 | 1.003824263879715e-08 | 3.328e-15 | 3.472e-16 |

## 비음수와 age moment 검토

검사한 모든 수치 열은 유한했다. 광자수, 광원 photon count, 4종 누적 photoabsorption 사건수, DII population 및 양의 에너지 저장 항은 비음수였다. 누적 사건수와 시간은 허용 범위에서 단조 증가했으며 시간·단계·옵션 계약도 일치했다. Mean photon age는 실제 역사 구간 안에 있고, exported second age moment는 positive distribution의 variance 및 support 부등식을 만족했다.

전체 13-species population vector는 CSV에 수출되지 않으므로 이 출력 감사는 전체 population positivity를 직접 확인한 것이 아니다. 그것은 별도의 native Rust invariant 검사와 코드 검토 범위에 속한다. Age moment의 허용 support는 분포 근사오차가 작다는 증명이 아니다.

## 검증 범위와 재현

이 판정은 artifact identity, 수출된 quantity의 비음수성, primitive 총에너지/광자 원장, age moment의 필수 부등식에 한정된다. 시간·분광·출생연령 수렴이나 full-EoR 물리조건의 타당성은 별도 연구 판단이다. 원래 sample artifact mismatch와 잔여 `.running.*` 파일의 원인은 이 감사 범위에서 결정하지 않았다. 부모 연구자가 별도의 실패·orphan inventory를 보존한다.

감사기 자체는 실제 native 파일을 읽기 전에 합성 13-case 자료로 검증했다. 정상 집합 및 CX 0행을 수용하고, 행수 불일치와 receipt가 일치하는 에너지 조작을 거부했다. 이 self-test 자료는 science 결과가 아니다.

```bash
python3 audit_native_outputs.py /path/to/evidence/native --output /path/outside/native/NEW_AUDIT.json
```

Output은 create-only이며 native 입력 폴더 밖으로 제한된다. 전체 case별 SHA, 행수, 원장 최대값 및 마지막 재구성 값은 `INDEPENDENT_NATIVE_AUDIT.json`에 있다.
