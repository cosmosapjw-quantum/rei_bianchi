# West82 source binding + high-l optical reference

Python3.10+, NumPy/SciPy. 새 namespace `bass_he_west82`는 별도 rate package의 `bass_he_rcx`와 충돌하지 않는다.
원 B1 optical/rate 두 historical wheel은 서로같은 namespace이므로 동시 설치하지 않는다.
새 package는그어느것도 import하지않는다.

```bash
python -m pip install --no-deps dist/bass_he_west82_reference-0.2.0-py3-none-any.whl
python -m bass_he_west82 table --root . --out /tmp/west82_table_new.json
python -m bass_he_west82 solve --input data/MANUFACTURED_HIGH_L.json --out /tmp/optical_new.json
PYTHONPATH=src python -B -m pytest -q -p no:cacheprovider -W error tests
PYTHONPATH=src python -B validate_high_l.py --out /tmp/exact_diagnostics_new.json
```

NumPy/SciPy는환경에있어야하며 검증버전은provenance/RUNTIME.json에있다. wheel에는PDF/표/원자료를포함하지않는다.
`table`은private원PDF의SHA와표SHA를검사한다. 출력표는sigma표가아니다.
`solve`는제조입력만받고, `--physical-rct`는거부한다.기존출력은atomicno-replace보존한다.

```python
from bass_he_west82.source import optical_point
x=optical_point(4.,-.8,-1.6,[.1,.2,0], energy_unit='Hartree', c_atomic=100.)
# 위숫자는제조검사입력이다. 실제moleculardata가아니다.
```

정확한가정/단위/부호/경계/오차구분은math/B2_DERIVATION_KO.md와REPORT_KO.md에있다.
원l32제한을64로확장했지만partial-wave수렴이나실제원자정확도를의미하지않는다.
