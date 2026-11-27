# BASS_HE PR124 | Pitts C0621 1989 실측 절대 포획단면적 기반 시간반전 연구

**핵심 결과:** 고정 IAEA EXFOR에서 이전 PR121/123에 없던 C0621 original source 3,269B를 Git blob 수준으로 확보. 95 MeV deuteron beam에서 실측 unpolarized absolute `dσ/ddΩ` 8행 + vector Ay 8행 + tensor Ayy 8행 = 24행 (독립 실험 한 캠페인). DA의 DATA-ERR는 통계+기타 계통, **별도 4% 절대 정규화**를 제외한다.

불변량 s 매칭은 He 정지계 광자 71.7266474339893 MeV, q/k는 298.4821852096 / 70.3850027716. 정확한 역/정방향 ordered spin factor는 (9/2)(q/k)²=80.9261874756649, full sphere event density 가정 시 그 절반인 40.46309373783246. 이전 PR107의 2/9*(k/q)²은 방향 명칭이 반대로 되어 있으므로 이 부모의 파일을 수정하지 않고 별도 교정 근거를 첨부했다.

실측 55° 2.02±0.14 nb/sr → *조건부* 광분해 ordered 163.4708987 nb/sr 또는 event 81.73544935 nb/sr; 90° 0.21±0.02 → ordered 16.99449937, event 8.49724968 nb/sr. 어떤 경우에도 이 8개의 역반응값을 관측된 Rice의 γ+He4 직접 측정값이라 부르지 않는다.

정규화 4%와 미제공 잔여 각도 공분산을 분리했다. 원전 Ay/Ayy는 dimensionless 및 별도 오차로 보존. 8개 조건부 딸 D 운동에너지 쌍은 관측 각도 좌표에 대한 kinematic evaluation. 전구면 총단면적이나 우주론적 사건률은 새로 생성하지 않는다.

본 프로젝트에 적용 가능한 scientific result는 ① 신규 실측 절대 source 추가 ② reciprocal 방향 오류 검출·교정된 조건부 numerical atlas ③ 계수/공통 정규화/열침적 경계 분리다. 연구범위 DAG `new source=2/2`, 중앙 `28/88`, HE physical `14/18` (no admission). Native independent R6/C9 NOT_RUN, production HOLD.

다음 직접 실험: Rice 1998/2000 원본 PDF의 12개 절대 광분해 DA 수치와 coincidence acceptance/efficiency, 또는 별도 원문 재인증 후 조건부와 실측값 비교. 현재 고정 Rice 두 에너지 구간은 150–250 MeV, 이번 Pitts 일치 에너지는 71.7266 MeV로 **직접 overlap이 없으므로** 동일 s 비교나 Rice 수치로 대체 금지.
