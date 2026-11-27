# C0A3 atomic interpolation / finite-support rate

Python3.10+. 원자 데이터 전용이며 rei_bianchi 코드를 변경하지 않는다. 실행에는 표준 라이브러리와
동봉 C0A2 native package만 필요하다. mpmath/pytest는 검증용이다. 기본 물리 보간법이나 source 정확도를 승인하지 않는다.

## 로컬 소스 실행

```bash
cd BASS_HE_EOR_C0A3_INTERPOLATION_RATE_20261003_v1
PYTHONPATH=src python -B -m bass_he_liu_interp --root . interpolate NR_CX:1s:1s 56.25 --method linear_E
PYTHONPATH=src python -B -m bass_he_liu_interp --root . interpolate NR_CX:1s:1s 56.25 --method loglog
PYTHONPATH=src python -B -m bass_he_liu_interp --root . functional NR_CX:2s:total 10 100 --theta-native 20
PYTHONPATH=src python -B -m pytest -q -p no:cacheprovider tests
```

기본은 원 단위 숫자이고 m²는 --unit m2 --accept-contextual-unit로 명시한다. theta-native는
source-axis scale이지 gas temperature가 아니다. 출력 --out은 create-only다. 기존 파일은 덮어쓰지 않는다.
partial-rate 명령은 --theta-J, --binding와 --accept-contextual-unit를 요구한다. Binding JSON은
energy_scale_J_per_native, reduced_mass_kg, authority의 정확히 세 필드여야 한다. 실제 source metadata가
미확정이므로 이 API로 사용자 가정을 계산할 수 있어도 physical_certificate는false다.

## API

```python
from pathlib import Path
from bass_he_liu import load_dataset
from bass_he_liu_interp import Interpolator
root = Path('.')
d = load_dataset(root/'raw', root/'provenance/INPUT_LOCK.json')
i = Interpolator(d, method='linear_E', scope='paper_domain')
a = i.evaluate('NR_CX:1s:1s', '56.25')  # brackets47.61/64; not a native sample
b = i.evaluate('NR_CX:1s:1s', '100')   # native token1.15E-17 preserved
f = i.maxwell_functional('NR_CX:2s:total', '10', '100', theta_native=20.)
assert f['full_functional'] is None and f['tail_bound'] is None
```

## 패키지 설치

```bash
python -m pip install --no-index --find-links dist bass-he-liu-interpolated==0.3.0
```

wheel에는 raw CSV/PDF가 없다. 설치 뒤에도 --root에 이 private bundle을 전달한다. 공개 Git source만으로
raw-source tests가 돌아가는 것이 아니다. dist에는 부모0.2.0 wheel과 새0.3.0 wheel이 함께 있다.

## 주요 경계

- native와interpolated를 타입으로 구별하고 own-grid, source SHA/row/col을 보존한다.
- paper_domain의 양쪽 node는1~200 안에 있어야 하므로 actual support upper196.200과225를 몰래 채우지 않는다.
- 로그보간의 합은 성분보간 후 합산한다. total/partial/shell중복과 결측 bridge/외삽은 거부한다.
- 선형모형의 순서속성은 union knot에서 exact rational로 검사한다. 이것은 physical UQ가 아니다.
- finite-support Maxwell은linear_E만. Full/tail은unknown, 정규화하지 않는다. 현재 상대 drift/비열적 rate는 미구현이다.
- binary64 산술의 positive underflow/subnormal/nonfinite는NUMERICAL_RANGE_ERROR이며0으로 숨기지 않는다.
- 실제 source uncertainty, isotope/per-u, heat/secondary/recoil은 미제공. NCP가 이 자료 공백을 자동 해결하지 않는다.
