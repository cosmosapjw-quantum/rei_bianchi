# HE-FAST-IGM-RCT02: 공통영역 기준 이력

BOUNDED_COMMON_DOMAIN_NATIVE_RHS_HISTORY_CHECKED__RECEIVER_INTEGRATION_OPEN.
첨부 FAST_IGM_RCT01의 native point bridge와 vendor80payload를 변경하지 않았다. SciPy DOP853/Radau를 그 native RHS의 연구용 시간적분 client로 사용했다. 새로운 generic solver 또는 receiver photon-coupled stepper를 만들지 않았다. 실제 receiver의 optional RCT 통합은 아직 미수행이다.

모형: prescribed H=3e-18/s, nH0=1e-4cm^-3, fHe=.083, nH=nH0 exp(-3Ht), Tcmb=20 exp(-Ht)K; 초기(.1,.05,.9),T=2000K. photon population과 외부source는0. OFF, KF96/GM25 각각 explicit Ebar30/35/Q의7경우를0..1e15s에서세적분설정으로계산했다. Q=40.819325400298eV이며source/mean은각run에서고정된다. 실제EOS-T의공통guard[1000,10000]K를모든stage/output에적용한다.

DOP853 fine의최종T: OFF1939.6198710803K; KF30/35/Q1943.4763264509/1941.6985420082/1939.6295126272K; GM30/35/Q2004.7221521422/1974.7021444938/1939.7829608931K. GM30의J=.00104482892408205events/H, KF30의J=6.18895124463549e-5다. 누적비16.8821644는같은상태rate비17과다르며온도/종분율되먹임때문이다. Ebar=Q의직접열항은0이지만GM-Q는OFF보다최종T가.1630898128K높다. 이수치들은제조초기조건의조건부모형이며관측값/실제원자스펙트럼이아니다.

주실험을읽은후GM30한경우만3e15s로연장하고두방법으로대조했다. t=1.61132358163420e15s,T=2005.458190270465K에서온도가극대이며,3e15s에서는2002.109594360597K로내린다. 전환시점두방법상대차1.26126e-11. wdot=-4.82087360357e-30erg/H/s, particles/H derivative=-1.16074705659e-17/s로둘다감소한다. Tdot/T=wdot/w-sdot/s에서두감소율이같아진것이며열평형이아니다.

총23 ODE solve,960accepted time steps,science native evaluations14758,101output epochs/solve. Native8tests,Python9tests통과. 전체stage/output/Jacobianprobe의actualT범위1939.61987106275..2005.45819027047K. 최대species누적결함4.9960e-16,energy결함1.91824e-15. 고정한상태/온도/RCT허용기준에서주실험최대비.0006087500,후속최대비.0012667608로모두1미만이다. 두방법은같은nativeRHS를사용하며독립atomic검증/intervalcertificate가아니다. Stage/출력검사는연속모든시각의엄밀invariance증명이아니다.

최신receiver a9aea514e086fec6d50cdf14496ff46054cc895e,branch forward/rem-hhe-igm-20261006,PR84 draft를읽었다. 기존spectral/BE/midpoint부분판정과장기실패는보존한다. 실행dependency는기존dbb54009... snapshot이고,igm_state/rates/thermal/he_rct는currentblob와일치한다. current전체library를빌드했다고하지않는다. sourcefreefixture를먼저existingigm_step에RCTcandidate/thermalresidual/endpoint/장부를동시에연결해비교하고,그뒤photon/source단계를검증한다. 본high-orderreference는receiver구현채택이아니다.

원자모멘트null,baselineOFF,physicalHOLD,HE-F2globalfalse,HE-F3/F09source-drivenintegrationopen을유지한다. 전체코드/부모입력/23이력/실패·성공로그는DELIVERY_RECEIPT의ZIP에있다. Git요약만으로전체실행source가있다고가정하지않는다. sourceidentity와숫자결과는같은폴더JSON을따른다. 기존point/원자/FT03/mixed/restart/receiver과학suite는재실행하지않았다.
