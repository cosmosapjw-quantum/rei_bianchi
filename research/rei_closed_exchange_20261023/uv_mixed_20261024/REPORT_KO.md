# REI-L0 SRC-01 한정 수리와 admission

## 판정

**REI-L0의 선택된 source-exchange / signed STF 대수 참조 조립을 ADMITTED_SCOPED로 판정한다.** 이 판정은 물리 공급자 보정, 수송, 우주론 IVP, Einstein 해, 전체 재이온화 모델의 완료를 뜻하지 않는다. 전체 모델 완료율은 null이다.

고정 authority는 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`의 `research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md`이다. 현재 사용자 승인으로 실제 finding SRC-01에 한정해 두 호출을 수리하고, CPU 1초 / wall 5초 아래 새 fixture 한 묶음을 단일 child에서 수리 전후 비교했다.

## 실제 변경과 결과

- frozen before SHA256: `f551026241d2838852f1eea5a8f3df3c966006e68f70044a97ae8ce594677067`
- repaired source SHA256: `c8dc1d8e8ad1ee72693bae20b86367b0e1aa1e52e9ff307575d21ca0b9279f77`
- `energy_source`의 UV 행: `_add(j,-p)` → `_poly_sum((j,-p))`
- `source_jvp`의 UV 행: `_add(dj,-dp)` → `_poly_sum((dj,-dp))`

두 호출 외에 소스 변경은 없다. 물리식, eV/Href 및 proper-second 단위, 에너지 owner, 공개 함수 API는 유지했다. Fraction와 float가 함께 들어오는 UV 차에서 피연산자를 따로 float로 반올림하지 않고, 표현된 입력의 정확한 합을 만든 뒤 한 번만 float로 반올림한다.

`epsilon=Fraction(1,2**54), chi=1, m=(1,1+epsilon,0,0,1.0)`을 사용했다. JVP는 zero base, direction=m, dchi=0이다. finite 기대 벡터는 `(epsilon,1,-epsilon,0,-1)`, external 기대 벡터는 `(epsilon,1,-epsilon,0,0)`이다.

| 관측 | 수리 전 | 수리 후 |
|---|---|---|
| energy_source / finite | UV만 0으로 소실 | 5성분 모두 정확한 기대값과 일치 |
| source_jvp / finite | UV만 0으로 소실 | 5성분 모두 일치 |
| energy_source / external | UV만 0으로 소실 | 5성분 모두 일치 |
| source_jvp / external | UV만 0으로 소실 | 5성분 모두 일치 |

새 primary fixture는 **1묶음**이며 before 4검사와 after 4검사다. 이를 새 8개 독립 사례로 세지 않는다. 수리 후 UV의 binary64 hex는 `-0x1.0000000000000p-54`이다. stdout 원문과 각 성분의 Fraction/float 표현을 `raw/stdout.jsonl`에 보존했다.

## 근거 재사용과 독립 심사

이전 C 패키지의 red3→green3와 primary66(49 dyadic +16 Decimal180 +1 입력 손실)을 재실행하지 않았다. 이전 소스는 같은 exact-products/sum 및 threshold 수리를 포함한다. 이번 두 UV 호출의 영향은 독립 native 심사자가 before/after, diff, driver, 실행기와 실제 raw를 읽어 확인했다. 구현자는 /root/uv_coding, 심사자는 /root/source_review로 분리했다. 심사자는 구현하지 않았으며, 별도 agent 문맥에서 심사했다. 다른 모델 계열에 의한 검증이라고 주장하지 않는다.

과거 22묶음은 저장된 실행 근거와 정적 영향 지도를 재사용한다. 9묶음은 수정되지 않은 helper만, 13묶음은 변경된 의존 경로를 포함한다. 22묶음 전체가 이번 최종 소스에서 새로 실행되었다는 주장은 하지 않는다.

이전 저장 수치의 올바른 범위는 다음과 같다.

- 부모 subthreshold 오허용: 35/49.
- 부모 net thermal 부호 반전: 해당하는 nonzero 행 32/46.
- 46 nonzero와 3 final-underflow-to-zero를 구별한다.
- Decimal component relative 최대: 1.0577179415105186e-16.
- gross balance 최대: 2.7755575615628914e-17. 이 값은 기록된 **49 dyadic source 벡터** 범위이며 전체 66/JVP의 최대치로 확장하지 않는다.
- 고정 scaled binary64 gate 2e-12를 변경하지 않았다.
- CAS/Decimal/같은 controller의 과거 audit는 fresh independent review가 아니다. 이번 별도 native reviewer의 실제 read-only 판정만 새 independent review로 기록한다.

## 자원

| 항목 | 실제 값 / 상태 |
|---|---|
| 새 child 수 | 1 |
| 새 CPU user + system | 0.046246999999999996 s |
| 새 wall | 0.04686999799741898 s |
| 새 제한 | CPU 1 s / wall 5 s |
| 종료 | returncode 0, timeout false, launch_error null |
| 이전 알려진 같은 탐색 증분 | CPU 10.110448 s |
| 이번까지 알려진 측정 증분 | CPU 10.156695 s |
| 원래 10초 한도의 당시 초과 | 0.110448 s, FAIL 보존 |
| 전체 역사 L0 비용 | UNKNOWN_NOT_ZERO |
| 원 cumulative cap | NOT_FROZEN |
| parent / IO / 모델 심사 / 원격 CAS | 별도 미측정, 0으로 기록하지 않음 |

이번 승인은 장래의 한정 수리 비용을 승인한 것이다. 과거 한도 초과를 소급하여 PASS로 바꾸거나 원래 cap을 11초로 고쳐 쓰지 않았다. 새 한도의 남은 부분을 L1 실행에 전용하지 않는다. 기존 22/66/83, ANGTHERM01·02, NCP 재실행, 새 IVP, 그림 생성은 모두 0이다.

실행자 요청은 gpt-6.1-sol/high였고, 실제 backend 모델 식별자는 도구에서 독립 관측되지 않아 unknown으로 남겼다.

## 해석 한계와 다음 전이

표현된 입력의 작은 차는 복원할 수 있지만 공급자에서 이미 float로 소실된 excess는 복원할 수 없다. Primary excess와 실제 stopping/thermal heat는 다른 양이다. 소스 대수의 보존은 공급자의 실제 물리 정확도를 인증하지 않는다.

L0의 PASS → 다음 행동은 선택된 L1 공급자 intake와 이론/정적 구현 준비다. C23B의 elemental-HI, z=2.479, finite PW19 source를 후보로 삼아 primary 전자 에너지를 명시적 비열 저장고로 남긴다. 새로운 L1 수치 실행 예산과 source/measure 검증은 별도로 동결해야 한다. L1의 정식 admission, L4, L5는 아직 열리지 않았다.

## 백업과 게시

실행 전 Stage A archive SHA256은 `8fc69d96fd0afcce8957f76b6109e984076456c56f27d98bb6138d690caa8a98`이다. Drive `1GqrhXZsjsLoHyhyd9-FMdQeq-1r-w9p9`, Dropbox `id:BSpOijBcT10AAAAAAD_9Iw`에서 저장 ACK와 크기를 확인했다. 원격 byte SHA 재계산을 했다는 주장은 하지 않는다.

Stage B는 실제 raw·독립 심사·이 admission을 담는다. 게시 상태는 외부 publication receipt를 따른다. 게시 전 실제 최신 AGENTS·central HEAD·병렬 경로를 확인하고, owned path에만 additive commit을 만들며 expected-SHA/non-force를 적용한다.

ANGTHERM02 `research/rei-coupled-isotope-contract-20261022@8d10231b1f0f788164d5eadbe1bcee0b802cceca`는 읽기 전용이다. C23E의 조건부 D43K, HE94의 부분 창, PHYS85의 준비/미검증 상태와 다른 owner의 비용을 보존한다.

