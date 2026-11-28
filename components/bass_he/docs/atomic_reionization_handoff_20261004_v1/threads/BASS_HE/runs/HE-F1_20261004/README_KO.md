# HE-F1: 두 출처의 선택형 원자 공급기

2026-10-04, `bass-he-atomic-export==0.1.1`. 현재 B3를 제자리 확장했다. 새 API를 병렬로 만들지 않았다.

## 실행

```bash
python -m venv /tmp/bass-he-f1-env
/tmp/bass-he-f1-env/bin/python -m pip install --no-index /absolute/path/dist/bass_he_atomic_export-0.1.1-py3-none-any.whl
/tmp/bass-he-f1-env/bin/python -m bass_he_atomic_export sources
/tmp/bass-he-f1-env/bin/python -m bass_he_atomic_export export /absolute/path/data/KF96_REQUEST.json --out /tmp/kf96-packet-new.json
/tmp/bass-he-f1-env/bin/python -m bass_he_atomic_export validate /tmp/kf96-packet-new.json
```

0.1.1은 현재 branch의 0.1.0 B3를 기준으로 한다. 다른 historical B3 wheel이나 optical package를 자동 설치/대체하지 않는다.
Runtime은 Python 표준 라이브러리뿐이다. 시험에는 pytest가 필요하다. 원 자료 PDF는 배포물에 포함하지 않는다.

## 호환성

GM25 `_rate.py`와 `_io.py`의 bytes 및 GM25 source/records/request는 보존한다. 새 packet의 exporter label만
`bass-he-atomic-export==0.1.1`이다. `validate_packet`은 정확한 0.1.0 GM25 패킷도 수락한다.
명시적 migration은 `export_packet(old_packet['request'])`다. KF96를 0.1.0으로 표시하면 거부한다.
정확한 네 baseline packet의 canonical SHA256는 테스트 fixture에, 원 패킷은 private 실행 근거에 있다.

## 출처와 범위

GM25: `GM25_W82_RCX_CONSTANT_200_10000_K_V1`, 200..10000 K, 1.70e-13 cm3/s.
KF96: `KF96_HEIII_HI_RCT_NOMINAL_V1`, 엄격 API window 1000..1e7 K, 1.00e-14 cm3/s.
KF96 원표 하한의 `~`와 nominal prescription 의미를 보존했다. isotope/ground-state photon mapping은
명시적으로 선택한 W82 scenario이며, KF96 자체가 isotope·spectrum을 분해했다는 주장이 아니다.
두 source는 같은 reaction_id의 대안이다. 공통 비교 구간은 1000..10000 K. 자동 선택·clamp·extrapolation·합산은 금지한다.

문헌: Kingdon & Ferland (1996), DOI 10.1086/192335, Eq.7/Table1 He2+/p206 prescription.
García Muñoz et al., arXiv:2511.21966v1 Appendix B.3; mechanism West et al., DOI 10.1103/PhysRevA.26.3164.
일반 rate식 1e-9*a*T4^b*(1+c*exp(d*T4))에서 a=1.00e-5,b=c=d=0이므로 KF96값은 1e-14 cm3/s이다.
SI 변환은 정확히 1e-6. 17배는 두 표기값의 산술비이며 물리 오차막대가 아니다.

`nu=(-1,1,0,1,-1,0)`, direct electron=0, photon birth=1. count coefficient에는 아직 밀도를 곱하지 않았다.
열·recoil·광자 energy/spectrum·inverse rate·source uncertainty는 null이다. 소비기가 별도 closure를 결정해야 한다.
Bianchi geometry/fluid/transport, microscopic/effective opacity는 원자 API가 다루지 않는다.

## 변경영역 검증

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -W error -m pytest -q -p no:cacheprovider tests/test_kf96_source.py tests/test_contract_red.py::test_registry_requires_explicit_source tests/test_contract_red.py::test_roundtrip_keeps_source_meaning tests/test_contract_red.py::test_count_invariants_exact_and_unit_scaling
```
54개 새 정의 + 기존 3개 영향범위 = 57개. 처음 새54 중46개는 미구현 실패,8개는 이미 성립하던 거부규칙.
기존 registry의 source수=2 주장은 새 source를 반영해3으로 갱신했다. 기존 source값·허용오차는 바꾸지 않았다.
부모76개 전체 suite, B5C2 59개 및 광학/전자구조 campaign은 재실행하지 않았다.
