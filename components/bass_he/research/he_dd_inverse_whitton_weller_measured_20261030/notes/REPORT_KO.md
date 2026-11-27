# BASS_HE PR121 | 실제 실험 자료로 신설된 inverse-DD 원전 atlas

## 신규 과학 성과

IAEA 소스에서 1993 Whitton의 상대방사포획 DA 14행, 편극 두 포인터 15행, 1984 Weller의 partial capture DA 6행 및 TAP 6행으로 구성된 **두 독립 연구 41행 실험기록**을 획득하여 출처와 관측량 형태를 보존한 원자료 atlas를 만들었다. 1993 REL과 1984 PAR은 절대 무편극 전체 포획단면적이 아니므로 총계·event-rate로 합산하지 않았다. 4개 원본 EXFOR 엔트리를 IAEA의 같은 고정 commit에서 Git byte까지 검증하였다.

코드는 상대론적 invariant-s에서 실험실 d kinetic energy 9.7/20/30/50 MeV를 He4 정지계 Eγ=28.803787555/33.986735465/39.018723728/49.082700253 MeV에 정확히 mapping한다. 세 실험 출처가 같은 입사 광자 에너지 범위에 들어간다는 **측정 기반 에너지 지원 교차 지도**를 완성했다. 이는 미인증 상세평형 `σ` 교환이나 detector 보정이 아니라 kinematic mapping이다.

상대 DA 실측만을 사용한 30/50 MeV near90-to-shoulder 비는 각각 0.02606383,0.0375이며, source DATA-ERR ± 직교상자는 각각 [0.01133005,0.04335260], [0.02941176,0.04666667]이다. 대칭 거울점 7쌍은 값이 거의 같지만 소스 편찬 방식으로 상관되었을 수 있으므로 독립검정으로 취급하지 않는다.

1984 `A1256002` 9.7 MeV/51.4° partial capture DA = 1.405E-05 mb/sr = **14.05 nb/sr**, ERR-S = 7.176E-07 mb/sr = **0.7176 nb/sr**. 이는 **partial, digitized curve** 값으로 오인된 unpolarized σ가 아니다.

## 계산 결과와 증거

- `sources/C0122.x4` 5049 bytes, blob ac638ddbea7795b281ab8494d3e75a62606b3f6d.
- `sources/A1256.x4` 2729 bytes, blob b4dba8ecb9ce5eb44501b9afba4c40db329b826b.
- `sources/M0011.x4` 2508 bytes, blob 20804471fb7584e07ab979ecad6a3e96cba0c6a2.
- `sources/M0826.x4` 2396 bytes, blob 95010842754215e98eea8d99eff5f3de0799c666.
- `src/build_inverse_dd_atlas.py`은 소스 SHA256와 Git blob을 강제 검증, 원본 subentry별 41행을 파싱, 56개 scalar component를 유지, photon-equivalence energy를 계산, 7개 대칭 관측쌍과 두 near-90 suppression 및 M0011/M0826 실험 지원지도를 생성.
- `tests/test_source_inverse.py` **19/19 unittest PASS**, `python -m compileall -q src tests` PASS. Wolfram exact rational and high precision kinetic numerical verification PASS (4 Eγ, 4 phase space q²/k², source two ratios and error boxes).
- `results/INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.json` 및 `.csv`, `results/SOURCE_ENERGY_CROSSWALK.json`에 실제 41개 측정행과 파생 기록을 보존. 각 측정행의 모델계수나 편극 변환 불확실성은 새 원자료로 승격하지 않았다.

## 성과 판정과 다음 단계

이 source unit의 두 완료조건 **S1 source byte-locked 41 rows**, **S2 energy + observable type map & executed verification**만 **2/2 scoped** 완료. Central 28/88; HE physical 14/18; PR114 lowE 3/4; PR119 angular 2/3; PR120 shape 2/2; physical delta 0. `R_event=null;heat_rate=null;kappa=null;L4=false;production=HOLD`. R6/C9 distinct-author NOT_RUN. 원래 연구의 물리적 L4, event normalization, D_fast 열침적, 전우주 gamma history는 완료되지 않았다.

가장 유의미한 다음 연구는 `C0122`의 **REL** 자료를 정규화할 원본 절대 cross section과 실험의 편극/상관/거울 점 처리 근거, `A1256`의 partial observable definition 및 이종 source comparison의 실제 통계 covariance를 추적하는 것이다. 그 뒤에만 상세평형의 spin/statistical/identical-2D symmetry 계수를 공증하고 실제 광분해 사건률로 변환한다. 높은 150–400 MeV 국소 photon history/ D_fast stopping은 별도 source-needed이다. 이전 IVP와 4501 node LP, 고비용 numerical optimization 재실행 없음.
