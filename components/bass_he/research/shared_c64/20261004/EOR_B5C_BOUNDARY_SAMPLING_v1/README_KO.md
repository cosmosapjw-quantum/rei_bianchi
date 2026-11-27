# BASS_HE B5C1 optical input reference

원자 데이터 전용이며 rei_bianchi 물리를 수정하지 않는다. 범위는 R/a₀=8..10이다.
전자에너지는 Eh, 좌표dipole은a₀, V기울기는Eh/a₀, F=A t_a/α³는무차원이다.
원PDF/부모원데이터는private archive, 공개코드는별도publication mapping으로분리한다.

## 실행

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/src:$PWD/vendor/b5a/src:$PWD/vendor/b5b/src:$PWD/vendor/b5b2/src"
python -B -m bass_he_optical_sampling --root . export --out /tmp/b5c-new-table.json
python -B -m bass_he_optical_sampling --root . evaluate 9.125 --allow-midpoint-only
python -B -m pytest -q -p no:cacheprovider tests
```

API는 source hash가 고정된 reference를 읽는다. midpoint-only임을 명시적으로 수용하지 않으면 거부한다.
표본의 값은 직접계산, 중간값은explicit interpolant다. h=.25의 midpoint기준 통과를 uniformerror certificate로 부르지 않는다.
외삽·production요청·기존output덮어쓰기는거부한다. JSON은completebytes를임시파일에fsync후hardlink로원자적create한다.

## 설치

```bash
python -m pip install --no-index --find-links dist bass-he-optical-sampling-reference==0.1.0
```

NumPy/SciPy는별도기존환경의exact version을확인한다. 배포wheel은원데이터를포함하지않으므로검증된ZIProot가필요하다.
`tools/run_registered.py`는원preregistration의smallphysics를재실행하므로단순조회에필요하지않다.
실행폴더data/continuation이이미있으면덮어쓰지않는다. 원자료해시를바꿔같은계약으로재실행하지않는다.

## 제한

고정1thread,binary64,명시적MINPACK/LAPACK만사용. Fortran/MPI최적화는이루프미수행이다.
R10에서leadingpolarization근사와직접V가13.2%다르므로tail대체불허다.
σ,k,heat,recoil,spectrum을만들지않는다. 독립표현비교는독립연구자심사와다르다.
