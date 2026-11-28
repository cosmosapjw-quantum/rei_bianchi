# KINEMATIC08: 물리 입력에서 직접 구성하는 유한 수용각 경계

현재 사용자 지시로 시작한 새 이론 R1–R10 / 코딩 C1–C10 단위다. APERTURE07은 종료된 선행 근거이며 재실행하지 않는다. 이번 산출물은 정확 유리수로 선언한 핵의 rest energy A=m_alpha c², M=m_d c²와 광자 에너지 e에서 직접 유도한 검출기 수용각 참조 계산이다. signature=(-,+,+,+), 에너지/운동량 c배의 수치 단위 MeV.

## 선택과 완료 기준
후보1 물리 입력→대수적 각도 판별, 후보2 유한 방위각 기하, 후보3 moving-target encounter kernel을 비교했다. 후보1은 선행 Bernstein 적분과 공유 사건 구조를 재사용하면서 저장 gamma/a 변환 오차라는 실제 미완료 연결을 닫는다. 원 M0475002 정규화·입사 flux/history·named nonthermal/thermalization의 새 입력은 조사에서 아직 확보되지 않았다.

0<A<2M, e>0, H=A²+2Ae−4M²>0인 정지 bare target의 동일질량 두 딸입자를 다룬다. 입력은 int/Fraction/유리수·십진 문자열/명시적 finite stored float이며 bool, nonfinite, 잘못된 단위/범위는 거절한다. H<0 closed channel 및 H=0 threshold atom은 이 연속 방향 API에서 거절한다. 물리 mass/beam uncertainty interval과 liquid-He target motion은 별도 입력 의무다.

정확 p+q sqrt(r) 부호 판별, a<1/a=1/a>1 topology의 exact 분류, irrational fold의 rational bracket과 outer-only 처리, full-azimuth polar windows의 preimage 및 shared event measure를 구현한다. 기존 degree<=8 비음수 Bernstein 밀도와 pair의 even coefficient 조건을 유지한다. 새 scalar default δ=σ/(20 Mmax 2^40)에서 pair mass width≤σ 2^-40을 유도/검증하고 수동δ는 실제 반환 width/width_bound만 사용한다. 질량 uncertainty가 없는 정확 상수 입력에 대한 인증이며 empirical rate나 thermal deposition으로 승격하지 않는다.

과학 채택 전 실제 새 테스트·정확 예·독립 대수 검산·저장 결과 plot 읽기 및 한 독립 검토 pass를 완료한다. 기존 suite, plot, archive 재생성0. 새 예산은 RESOURCE_CONTRACT.json에 한정한다.

## 보호 상태
PHOTON05=24/24 PASS, plot CPU4.40726504>4 FAIL, workflow PARTIAL. HE101=C8 PARTIAL_EXPORT19/20, reserve0, original PASS/FAIL/FAIL. Binding은 population_rest_energy_witness에 한 번만 포함. independent binding RHS, Gamma_thermal, Cv, species_heating, thermal_deposition=null; birth_pool=UNASSIGNED. Global physical completion=null; L4=false; production=NOT_APPROVED.

## DAG와 게시
8 complete +1 pending +3 physical open /12로 시작하며 새 참조 계산을 실제 채택할 때만9/12가 된다. 중앙은 별도 범위28/88, 허용 HE delta0. 매 S01–S10의 해당 R/C 작업물을 신규 source checkpoint와 Drive·Dropbox에 create-only 백업하고 실제 ACK를 외부 영수증에 기록한다. Git PREPUBLICATION 기록은 commit 당시 snapshot이며 최종 외부 POSTPUBLICATION closeout이 후속 ACK의 권위다. 현재 origin은 local 원본이며 GitHub 게시는 확인된 connector로 별도 수행한다.
