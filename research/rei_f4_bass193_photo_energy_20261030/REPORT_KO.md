# REI F4 물리 데이터 보고서 | 원 BASS 193 저장 시점 광자–전자 에너지 분해

신규 구성은 기존 PR276 matched-bath REI rate discrepancy를 반복하지 않는다. 원본 BASS21 finite radiation photo-source에서 **2,509개의 핵종별 광전이 행, 13,703개 스펙트럼 에너지-bin 행, 193개 epoch 요약과 193×13 energy-partition NPZ**를 생성하였다. 원본 BASS source를 고정된 저장 상태마다 실제로 실행하였으며 IVP/원래 방사전달/가스 열적 진화를 추가하지 않았다.

핵심 수학은 `Qabs=Qion+Qprimary+Qcore`. 원본 광자 bin integrals로 다시 구성한 absorbed·primary·core 수치는 source `AtomicNetwork.evaluate`와 각각 최고 상대 오차 5.38e-16, 5.43e-16, 8.77e-16으로 일치한다. Li 1s `Qcore/(N_1s)`는 58.998 eV로 재현되고 기호 Wolfram 계산에서도 정확하게 성립한다. Source positive rate/threshold, isotope-charge positions, proper density/time conversion을 테스트하였다. 최종 독립 pristine Python 테스트 **40/40 PASS**.

실제 source 저장-grid 사후노출량은 **흡수 121.1542586591429, threshold 92.83563382986274, primary 28.3186248272491, unresolved Li1s core 2.0310979599168846e-9 eV/baryon**. 이는 prescibed BASS pilot의 `z=20→2` 193 저장 시점이고, 실제 열전달·온도증가량·REI optical depth·CMB likelihood는 아니다.

Li I 1s 흡수 원전에서 Auger/형광 branching을 검증할 필요가 있다. 원본 BASS 코드의 전하증가 한 단계는 model-specific assumption이며 정확한 Li double ionization/cascade 에너지 분배가 아니다. REI Rust `IgmPhotoInput`의 heat input은 별도 source-owner에서 열적으로 정해져야 한다. 따라서 이 데이터는 REI full model의 thermal source와 에너지 conservation이 **미결인 구체적인 이유와 입력 형태**를 제공한다.

원 버그: 첫 코드 작성에서 `site_inner` cross-section 배열을 1 epoch 처리 후 `site_inner` 사건률 벡터로 덮어써 2 epoch에 차원 오류가 발생하였다. 변수명을 `site_inner_sigma`로 분리하고 동일 입력/조건에서 재실행 40/40 PASS. 또한 의미없는 자기배열 비교를 원본 감마×저장 population 대비 스펙트럼 direct sum 검사로 교체했다. 실패/수정 이력은 `results/REPAIR_HISTORY.json`에 기록. 허용오차 완화, 실제 BASS source mutation, 신규 IVP 없음.

완료 판정은 새로운 보조 데이터 단위 `1/1_SCOPED`, 기존 보조 데이터 2/2와 합쳐 계보 `3/3_SCOPED`. 원 핵심 DAG는 **Working33/88, Central28/88, F4fast4/7, physical delta0**, `F4=PARTIAL`, `L4_ready=false`, `PRODUCTION=HOLD`. 실제 다른 작성자 R6/C9는 `NOT_RUN`, 기존 CI 실패 보존. 다음 실제 물리 과제는 1s Auger/형광과 secondary electron 에너지 침적의 source owner 확보 또는 실험실 실측 분기·열원천 확보이며, 그 전 BASS 광전 에너지 장부를 REI 열적 source로 직접 이식해서는 안 된다.
