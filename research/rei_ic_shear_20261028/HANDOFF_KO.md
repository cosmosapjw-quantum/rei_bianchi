# 초기조건·Bianchi I 연구 인계

기준: rei_bianchi PR248 HEAD022f2ed85595364f05834d8eb1573434efce92d0. 새 branch research/rei-ic-shear-20261028, 실행 전 checkpoint a9b9288c9cb80d7774fd53fd1246a217ce9b0c2c. 최종 PR/HEAD·백업은 DELIVERY_RECEIPT.json의 containing commit과 provider 결과를 따른다.

이번 연구: 초기조건의 원전과 가정 구분, 명시적인 17상태 후보, Bianchi I의 일반 STF와 LRS 구분, 양의 radiation/matter 분포와 Hamiltonian 초기화, 자유·강제 해석적 응답. 이론과 코드·10개 검사가 완료됐으며 독립 판정은 PASS_SCOPED_IC_BIANCHI_ANALYTIC이다. 상세는 review/DECISION.json을 확인한다. 전체 working 33/88·central 28/88, physical fast 4/7, 이전 현상론적 pilot 7/7은 그대로다.

기존 OFF_base는 추가 source와 escape를 끈다. 기존 photo/RR/beta/capture를 전부 끄는 것이 아니다. ON_base는 추가 source와 escape를 켠다. ON_refined는 같은 물리에서 rtol=2e-8, scaled atol=2e-12로 기본값 1e-7, 1e-11보다 5배 엄격하다. 이전 세 IVP를 반복하지 않는다.

기존 donor는 z=20, Tgas=300 K, s/H=0.24494897427831772, Omega_sigma=0.06이다. Cold 8 K 초기조건을 기존 지정 bath에 조용히 대입하지 않는다. 새 IC는 theory/INITIAL_PROFILES.json, 초기값·전자·열에너지는 outputs/INITIALIZED_PROFILES.json에 있다. n/T의 source-onset 0은 근사이며, 선행 source가 있으면 causal prehistory를 지정한다. constant_prehistory helper는 finite/relaxed 초기 재고를 구분한다.

초기 shear/stress를 바꿀 때 Hamiltonian 제약을 만족해야 하며 signed sigma:pi와 성분 간 상대 고유축을 보존한다. 먼지의 kinetic pi는 0이고, warm matter에는 velocity pressure가 필요하다. 현재 helper는 비-IVP이며 신규 isotope time-evolution sensitivity는 아직 실행하지 않았다. 42개 response와 12개 signed-work 행을 cosmological trajectory로 부르지 않는다.

새 과학 suite를 1회 실행해 10/10 PASS. Measured child+partial wrapper=0.075538 CPU s. Main은 inherited 604.395912+actual 0.075538+new tail 1=605.47145이며 임시 한도 620을 종료하고 원래 600으로 복귀했다. Planning 20.819461885/policy 10, presentation 62.468055494/policy 30을 보존한다. 미계측 overhead는 UNKNOWN_NOT_ZERO다. 예산을 reset/transfer하지 않는다. 기존 세 IVP exception은 닫혔고 이번에도 IVP 0이다.

다음 최소 작업: 선택 IC와 일치하는 photo/T/ne bath adapter, 지정한 양의 radiation/matter distribution을 Bianchi provider에 연결. 이후 유한 sensitivity case와 승인 범위를 고정한다. 기존 lane·원시 결과·담당자 예약은 보존한다.
