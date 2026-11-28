# BASS_HE B3: 명시적 원자 데이터 공급기

선택한 문헌근사의 thermal rate·종별 사건계수·광자수를 JSON으로 공급한다.
원자 scope만 다루며 Bianchi 배경·밀도·수송은 받지 않는다.

## 설치와 실행

ZIP에서 풀린 루트에서 실행한다. 공개Git에는 코드·시험·설정이 있고, 검증용 upstream
기록·부모 archive·wheel은 이 묶음에 있다. wheel에는 원 PDF나 표가 포함되지 않는다.

```bash
python -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install --no-index --no-deps dist/bass_he_atomic_export-0.1.0-py3-none-any.whl
python -m bass_he_atomic_export sources
python -m bass_he_atomic_export export contract/EXAMPLE_REQUEST.json --out /tmp/bass_he_new_packet.json
python -m bass_he_atomic_export validate /tmp/bass_he_new_packet.json
```

rate/count 공급기 자체는 Python3.10+ 표준라이브러리만 사용한다.
West광학reference도 필요한 경우 별도 wheel을 설치한다. 이 경우 호환되는 NumPy/SciPy가 필요하다.
이번 검증에서는 호스트에 이미 있던 NumPy/SciPy를 사용했고 인터넷에서 새로 설치하지 않았다.

```bash
python -m pip install --no-index --no-deps dist/bass_he_west82_reference-0.2.0-py3-none-any.whl
```

새 namespace 둘은 공존한다. 역사적 두 `bass_he_rcx`배포물을 한 환경에 동시에 설치하지 않는다.
`pip install` 외에 파일을 직접 복사해 덮어쓰는 우회는 하지 않는다.

## 요청 의미

EXAMPLE_REQUEST.json의11개 필드는 모두필수다. source 선택 및 상충인지가 없으면 거부한다.
quantity=thermal_rate 또는event_count_coefficients만 허용한다. 온도목록1–4096개.
GM25_W82_RCX_CONSTANT_200_10000_K_V1는 200≤T/K≤10000의 공통T·상대drift0 Maxwellian,
W82의4He-H source범위, H1s 및 자발단광자 반응에 한정한다. source 숫자는
1.70E-13cm³/s 또는1.70E-19m³/s다. 물리적 반응률을 새로 측정하거나 fit한 것이 아니다.

packet은 source 선택·부모codeSHA·원본문 locator·null moments·상충을 보존한다.
`validate` 성공은 packet/selectedcode 일관성이지 source uncertainty나 independent review가 아니다.
full spectrum·heating·inverse source·sourceUQ는 null이다. geometry/density필드는 허용하지 않는다.
모든 batch가 유효할 때만create-only로 저장하고 기존 결과는덮어쓰지 않는다.

## 검증

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
 python -W error -m pytest -q -p no:cacheprovider tests
```

전체76개 시험에는byte동일한 upstream core/io와 비교하는 focused parity가 있다.
과거60/49/43 scientific suite를 합쳐 재실행한것이 아니다.
두wheel을같은빈target에설치한 뒤 `verify_coexistence.py`로 실제import경로를검사할수있다.
검증시 readonly 부모자료와 source code를 임의변경하지 않는다.

B3의 기능범위는 완료했지만 raw Westσ/V/A,source충돌·불확실성과 전체원자프로그램은열려있다.
실제 rei_bianchi API와의통합시험은미수행이다. NCP64측정·Fortranbuild·MPI실행도없다.
