# STATE04 저장 결과 그림의 직접 판독

판독자 `/root`, 관측 시각 2026-10-27 09:59 UTC. `view_image`로 실제 PNG를 열어 두 패널의 축, 단위, 범례와 끝점을 확인했다. 새로운 rate, fit, source 또는 테스트를 실행하지 않았다.

- PNG: `STATE04_SOURCE_COMPARISON.png`, 95,227 bytes, SHA256 `67c7fa23a21a9e65bd2328d74e355ef32b8e57c9e299d82f53a018e5a0c5cde3`.
- SVG: `STATE04_SOURCE_COMPARISON.svg`, 84,310 bytes, SHA256 `daad0fdc4ae5866d7549f65de3d84ebf6197d2334a3cd3d73154bc71e2a0e217`.
- 정확한 plotted data: `plot/PLOT_DATA.json`, SHA256 `1ce5de1eb8275ee38d7b1313ed31096ce8bd733a4136115d33471ab4ea566aa3`.

## HD 패널

가로축은 K, 세로축은 m³/s이며 양쪽 모두 로그 축이다. 파란 원은 선택한 HD 2→1 edge의 원문 하향 계수이고 주황 사각형은 명시적 열적 reciprocity로 유도한 상향 계수다. 낮은 온도의 상향 억제와 높은 온도에서의 weight ratio에 따른 상향 증가가 구별되어 보인다. 이 모양은 저온 Boltzmann 억제를 빠뜨리거나 state weight를 제거한 경우와 맞지 않는다. 인쇄 계수의 cm³→m³ 변환은 새 단위 검사에서 독립 Decimal80 참조로 확인했으며 이 그림의 단위와 일치한다.

3005 K의 초록 x는 실제 원문 하향 점을 보존한 표시다. 해당 온도에는 실행 가능한 상향 점을 만들지 않았으며 논문의 3000 K 범위와 결속하기 전의 HOLD를 범례에 명시했다. Native 온도는 1005 K이고 1000 K로 바꾸지 않는다. 점 사이의 선은 시각적 연결일 뿐 보간 공급자, fit 또는 에너지별 DCS를 뜻하지 않는다. 24개의 수용 온도는 한 edge의 지원 범위이며 원표의 모든 171개 전이를 구현했다는 주장이 아니다.

## LiH 패널

가로축은 K, 세로축은 원표 단위 10⁻²⁰ cm³/s이며 양쪽 모두 로그 축이다. HD 패널의 SI m³/s 축과 혼동하지 않는다. 파란색은 Bennett 2003의 역사적 표, 주황색은 Bennett 2008 정오표의 교정 표다. 낮은 온도에서 비슷한 두 표가 중간·높은 온도에서 크게 갈라진다. 교정본을 선택할 때 같은 소유권 사건에 두 표를 합산하면 안 된다는 실제 영향을 드러낸다. 1000 K의 17.7→3.19, 3000 K의 51.2→1.80은 저장된 인쇄 행과 일치한다.

두 곡선은 각각 27개 native 행의 표시다. 인쇄 fit을 평가하지 않았고 원전의 fit residual을 물리 불확도나 covariance로 해석하지 않았다. 이 교정은 state branch, 광자 에너지·각분포 또는 thermal deposition을 채우지 않는다.

## 판정과 한계

`PASS_SAVED_SOURCE_PLOT_READ`. 범례가 source/derived/historical/corrected/HOLD를 분리하고 축·단위가 읽히며 잘림이나 겹침이 없다. 단위와 끝점 혼동을 막는 데 충분하여 추가 렌더를 하지 않는다. 실제 render는 1 process, exit 0, CPU 3.35712228 s, wall 3.3577162440051325 s이며 4 CPU s / 15 wall s / 512 MiB / 1 thread 배정 안이다. 과학 함수 호출은 0이다. 기본 Matplotlib 설정 경로의 쓰기 불가로 임시 캐시를 사용했다는 stderr 경고는 원문 그대로 남긴다.

그림은 total material kinetic compensation을 종별 가열이나 열화로 분해하지 않는다. Population energy witness, 열용량, 총 입자수 및 비열적 에너지의 소유권은 MODEL_CONTRACT의 분리를 따른다. 기존 HE101·INTAKE01·DRIFT02·EVENT03·WU 검증을 재실행하지 않았다.
