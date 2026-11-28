# BASS_HE C0A2: Liu CSV native-node provider

원자 데이터 전용. 입력은 사용자가 제공한 4개 CSV이며, 같은 bytes를 `raw/`에 보존한다. `rei_bianchi`의 기하·유체·수송은 다루지 않는다.

## 실행

Python 3.10 이상. 실행 코드의 외부 Python 의존성은 없다. 시험에는 pytest가 필요하다.

```bash
cd BASS_HE_EOR_C0A2_NATIVE_DATA_20261003_v1
PYTHONPATH=src python -B -m bass_he_liu --root . sample NR_CX:1s:1s 100
PYTHONPATH=src python -B -m bass_he_liu --root . sample EXC:1s:2p 100 --unit m2 --accept-contextual-unit
PYTHONPATH=src python -B -m bass_he_liu --root . sample NR_CX:2s:total 225 --scope payload_domain
PYTHONPATH=src python -B -m bass_he_liu --root . audit --out /tmp/liu_audit_new.json
PYTHONPATH=src python -B build_products.py --root . --out /tmp/liu_products_new_directory
PYTHONPATH=src python -B -m pytest -q -p no:cacheprovider tests
```

출력 경로가 있으면 덮어쓰지 않는다. 마지막 build의 out 디렉터리도 새 경로여야 한다. 외부 설치에는 `dist/*.whl`을 쓸 수 있지만 CSV와 input lock은 이 묶음에 둔다. wheel에 원자료를 공개 재배포하지 않는다.

## API

```python
from bass_he_liu import load_dataset
from pathlib import Path
root = Path('BASS_HE_EOR_C0A2_NATIVE_DATA_20261003_v1')
data = load_dataset(root/'raw', root/'provenance/INPUT_LOCK.json')
p = data.sample('NR_CX:1s:1s', '11.56')
# p['value_token'] == '2.96E-18'; first CSV axis is NOT used for this channel.
q = data.sample('NR_CX:1s:n2', '100')
# Exact sum of two supplied columns, not an independently tabulated quantity.
```

정확한 node 조회이므로 energy는 str/Decimal/int를 받는다. float key, 임의 nearest node, interpolation, extrapolation, E_cm 변환은 허용하지 않는다. `paper_domain`은 논문 선언1~200 안의 실제 nodes만 반환한다. 200 자체가 tabulated node라는 뜻은 아니다. `payload_domain`은225까지 보존된 원값의 명시적인 조회를 허용하지만 물리 타당성을 승격하지 않는다.

## 단위

CSV는 에너지 헤더 `keV/u`만 제공하며 sigma 단위는 쓰지 않는다. 기본 출력 `source_native`는 원 숫자와 미지 단위를 보존한다. `--unit cm2|m2 --accept-contextual-unit`은 논문 figure2~10과 값 규모에 근거한 cm² 해석을 명시적으로 수용하는 경로다. m² 변환계수는1e-4다. Excitation 그래프의 표시 배율1e-16을 scientific-notation CSV 값에 또 곱하지 않는다. 이 해석은 provider가 제공한 unit metadata나 checksum 확인을 대신하지 않는다.

## 주요 산출물

- `data/generated/LIU2024_NATIVE_DATA.json`: 원 행/열 token, 27개 source quantity, 743개 값,6개 명시적 결측.
- `LIU2024_NATIVE_SAMPLES.csv`: 743개 nonempty source값의 long-form과 원 위치/해시.
- `CHANNEL_ENERGY_COVERAGE.json`: 이전37개 figure quantity의27 direct/4 derived/6 missing 구분.
- `DERIVED_SHELL_SUMS.json`: 실제 공통 energy node의4개 shell sum,114개 exact decimal 합.
- `NATIVE_DATA_AUDIT.json`:17개 grid불일치,54개200초과 값, total/partial 동일energy 비교.

이 도구의 완료는 데이터입수·native query의 완료다. 단면적 source uncertainty, 저에너지 핵 운동, radiative CX, ionization, secondary/recoil/heat, 실제 rate, consumer production admission은 자동 완결되지 않는다.
