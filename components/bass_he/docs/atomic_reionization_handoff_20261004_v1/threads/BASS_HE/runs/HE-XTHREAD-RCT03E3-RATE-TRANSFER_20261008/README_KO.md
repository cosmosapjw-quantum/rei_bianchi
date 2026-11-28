# HE-XTHREAD-RCT03E3: 세 스레드 수신과 직접 rate 검증

PARTIAL_DIRECT_RATE_REFINEMENT__LINEAR_AND_OPT_IN_CUBIC_READOUT_DECOMPOSED.
CR R8/R9의 두 exact readout 코어를 불변으로 재사용했다. HH는 Library ON06G(total256,t3.2e11s), REI는 종료 전 게시된 BRIDGE07(two-cohort carried family)까지 수신했다. 서로 다른 FT03/LCS/IGM 모형·시계·parameter box를 하나의 물리이력으로 합치지 않았다.

부모 HE E2의 missing Gamma를 채우기 위해 기존 native probe 그대로 OFF/KF/GM N192,P512,O4의3이력576step만 새로 실행했다. 기존 N192 상태·장부23160값은 bit-identical이고 원 native gate는 모두 통과했다. 새 rate 기준 2.5e-23 s^-1+1e-6 relative는 실행 전에 고정했다. 시간축 비는 모두1미만이나 Gauss2/4차가 지배해9개 rate 목표는 모두FAIL이다. 세축 최대비는 HI3.62413,HeI6.71880,HeII9.74925다. 원18필드 성공을 취소하거나 기준을 완화하지 않았다.

CR R8로 integral Gamma/H와 integral a*Gamma/H를 exact stored-node 함수로 분해했다. OFF HI에서 N192->384 노출량 변화5.00398490e-7 중 history1.84035759e-9, readout-grid4.98558132e-7로99.6322%가 출력격자 항이다. 끝점에서 재구성한 AH는 producer의 내부stage 장부와1.51730832e-7/H 차이가 나지만 그 정의가 다르므로 producer FAIL로 바꾸거나 덮어쓰지 않는다.

늦게 수신한 CR R9 cubic을 OFF/GM에 opt-in 적용했다. 실제 네 시각의 정확 cubic 적분24개/분해12개를 계산했고2304개 panel의 Bernstein계수가 비음수였다. OFF의 노출량 grid항 감소비는 HI9.7621,HeI231.5123,HeII1143.6502다. CR Thomson에서의18509배를 HE에 이전하지 않았다. 참 node오차/C4전제가 없어 enclosure요청12개는거절됐다. Rate 분광FAIL은 그대로다.

후속 진단에서 원 Grid::new의source/cutoff anchors는N24에 고정돼 있었다. OFF HeII의anchor시각 Gauss비3.55e-6 대 중간시각9.74의 차이는 cutoff-aware 동일스펙트럼 대조를 다음 우선순위로 삼을 근거다. 아직 원인을 분리한 시험이 아니며 실패시각을 삭제하지 않는다.

새Python13시험 RED/GREEN, common-node product1737개, linear분해30개, 별도100자리 배경1155/적분90대조와 기호5식을 확인했다. 원source535payload와 CR코어2개는불변이다. 새native단위suite/원자/타owner기존science/referenceODE 재실행0, 독립과학심사와연속해구간인증NOT_RUN.

사용자첨부E2 e15e7e...와 remoteE2 c8820730...는 다른archive다. 첨부는9개완료,remote는5개완료와중단prefix로범위가다르며합산하지않았다. 이번source는첨부535payload다.

전체소스·기준자료·새3이력·검산·늦은수신·실패로그는 DELIVERY_RECEIPT의ZIP에있다. Git은요약/계약/pins이며전체실행crate라고주장하지않는다. 다음은HE-XTHREAD-RCT03E4_CUTOFF_AWARE_RATE_READOUT. 원receiver/root/다른repo변경0, baselineRCTOFF, 실제원자모멘트null, physicalHOLD, HE-F2/F09globalOPEN이다.
