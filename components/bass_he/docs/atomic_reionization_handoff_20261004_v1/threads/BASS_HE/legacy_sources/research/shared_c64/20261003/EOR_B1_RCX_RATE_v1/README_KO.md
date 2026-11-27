# BASS_HE B1: 선택형 복사성 전하교환 반응률

Python3.10+, runtime 외부 의존성 없음. 원자 데이터 전용이며 rei_bianchi의 동역학을 실행하지 않는다.
근거: García Muñoz et al., arXiv:2511.21966v1 Appendix B.3의 West1982 재적분 근사.
200–10000 K에서 k=1.70e-13 cm³/s. source uncertainty 미제공, KF96와의 >10배 차이는 미해결.

```bash
export PYTHONPATH="$PWD/src"
python -B -m bass_he_rcx rate 1000 \
 --source-id GM25_W82_RCX_CONSTANT_200_10000_K_V1 \
 --distribution MAXWELL_COMMON_T_ZERO_DRIFT --acknowledge-source-conflict
python -B -m bass_he_rcx counts 1000 \
 --source-id GM25_W82_RCX_CONSTANT_200_10000_K_V1 \
 --distribution MAXWELL_COMMON_T_ZERO_DRIFT --acknowledge-source-conflict --out /tmp/new_rcx_packet.json
python -B -m pytest -q -p no:cacheprovider tests
```

`counts`는밀도를곱하기전의species와single-photon coefficient다. photon energy/heat/recoil은null이다.
범위외/비Maxwell/유한drift/다른isotope/initial state/불명source/상충미인지 요청은거부한다.
기존출력은덮어쓰지않고temporary-write/fsync/hardlink로create-only저장한다.

```python
from bass_he_rcx import SOURCE_ID, rate, count_coefficients
kw=dict(source_id=SOURCE_ID, distribution="MAXWELL_COMMON_T_ZERO_DRIFT",
        acknowledge_source_conflict=True)
r=rate(1000, **kw)
assert r["rate_token"] == "1.70E-19"
assert r["fit_error_bound"] is None
```

wheel은`dist/`에서offline설치할수있다. sourcePDF는wheel에포함되지않으며 privateZIP에만보존한다.
GM25PDF/HTML은web에서읽었지만 원bytes다운로드는실패했다. 짧은numeric sentence의로컬전사와
locator를보존했고원PDF해시를만들지않았다. `data/`의여러온도값은동일fit의평가이며독립실험표가아니다.

완료범위: source식평가와에러처리·단위·count계수·배치·CLI. 물리정확도/원σ재계산/열source/전체B1완료아님.
