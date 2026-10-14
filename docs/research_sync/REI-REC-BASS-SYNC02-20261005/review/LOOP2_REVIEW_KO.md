# Loop2 독립 판정

실제 REC–REI–BASS 팽창 benchmark를 **범위 한정 PROMOTE**로 판정했다. 미해결 blocking finding은 없다. Loop1 고정 판정과 sync identity를 확인한 뒤 새 통합 코드·oracle·실행 결과만 검토했다.

source와 실행체의 27 identity가 기록과 일치한다. 실제 RK4는 모든 stage 및 endpoint에서 REC를 호출하고, midpoint는 별도의 half RK4로 계산한다. HHe state는 density carrier이며 HHe/FT03/RCT RHS를 호출하지 않는다. proper 밀도 희석, cm⁻³↔m⁻³, a_eff=Δt/Δη 및 c 변환의 소유권이 명확하다.

| 가장 미세한 N=1600 결과 | 실제 값 |
|---|---:|
| 최종 xHII | 0.045601104174408616 |
| 독립 DOP853 대비 최대 x 절대차 | 1.9641732684760882e-11 |
| 구간 추가 optical depth | 5.195116786234065 |
| optical depth 상대차 | 3.578215511124118e-7 |
| interval probability L1 차이 | 5.7708002308726896e-8 |
| 세 clock τ 최대 절대차 | 4.440892098500626e-15 |

세 chemistry history와 세 constant-x 해석 fixture, 91 집계 검사, 오류 CLI 4건을 확인했다. τ 오차 감소비 4.00075/4.00018은 유한 grid에서 관측한 midpoint refinement다. reviewer는 history를 반복 실행하지 않았다.

사전등록한 세 잘못된 density/clock 변환 sensitivity control은 최초 실행 전에 포함돼 모두 검출됐다. 이는 production 코드를 변조해 실행한 mutation test가 아니다. 모든 원래 수용기준과 source profile을 유지했다.

이 결과는 pure-H, 한 온도, 지정 matter-only FLRW의 z=1200→1000 benchmark다. 초기 x=0.8과 observer tail=0.2는 지정값이다. full HYREC/전체 BASS, retained n=2 이력, EoR 예측, 일반 Bianchi, F04/F05 continuum certificate 및 finite-T/스펙트럼 승격으로 확대하지 않는다. 현 범위의 추가 과학 실행 gate는 없다. 소유자별 다음 과제와 기존 병렬 lane을 보존한 게시 단계로 진행할 수 있다.
