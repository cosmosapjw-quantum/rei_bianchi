# BASS_HE C0A4 atomic internal-state moments

원자 자료 전용. `rei_bianchi`의 기하·수송·유체는 변경하지 않는다.
기본 자료는 네 source CSV와 archived ScienceDB metadata다. module이 공급하는 값은
explicit ideal Coulomb state-energy weight × 기존 sigma이며 heating/stopping이 아니다.

## 실행

Python3.10+. runtime 외부 의존성은 부모 두 package뿐이며 동일 source를vendor/에 보존했다.
새 source Python code는float 연산에서binary64, 원 token/계수에서는Decimal/Fraction을 명시적으로 사용한다.

```bash
export PYTHONPATH="$PWD/src:$PWD/vendor/c0a3/src"
python -B -m bass_he_atomic_moments --root . provider
python -B -m bass_he_atomic_moments --root . sample NR_CX:1s:1s 100 \
  --energy-model COULOMB_Z1_Z2_INFINITE_NUCLEAR_MASS_V1
python -B -m bass_he_atomic_moments --root . sample NR_CX:1s:1s 56.25 \
  --energy-model COULOMB_Z1_Z2_INFINITE_NUCLEAR_MASS_V1 --method linear_E
python -B -m bass_he_atomic_moments --root . functional EXC:1s:2p 25 196 \
  --theta-native 30 --energy-model COULOMB_Z1_Z2_INFINITE_NUCLEAR_MASS_V1
python -B -m bass_he_atomic_moments --root . export \
  --energy-model COULOMB_Z1_Z2_INFINITE_NUCLEAR_MASS_V1 --out /tmp/c0a4-new-products
python -B -m pytest -q -p no:cacheprovider tests
```

out parent directory는 있어야 하며 기존 결과는 덮어쓰지 않는다. `--full` 또는 `heat` 요청은
SourceUnavailable, exit2다. `--unit m2 --accept-contextual-unit`은 부모의 contextual cm² 해석을
명시적으로 수용한다. 단위 문자열이 원 CSV에 있었다고 주장하지 않는다.

## 설치

```bash
python -m pip install --no-index --find-links dist bass-he-atomic-moments==0.4.0
```

wheel에는 원 CSV나metadata를 포함하지 않는다. 검증된 ZIP의root와 함께 사용한다.
순수 코드 배포와 licensed source snapshot을 구분한다. 자세한 의미·경계·단위·검증은 math/와 REPORT_KO.md.
