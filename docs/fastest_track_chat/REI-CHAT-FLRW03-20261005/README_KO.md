# REI-CHAT-FLRW03-20261005

판정: SCOPED_EXPANDING_REFERENCE_AND_CONTRACT_VERIFIED__NATIVE_CONSUMER_OPEN.

기존 fastest-track의 FLRW03 이론·경량 연구를 마쳤다. F00/F03 정지 fixture, production source와 runtime 반환은 수정하지 않았다. 외부 REI-F04 interval 작업, PB02/FT07 deferred를 보존한다. 이 폴더는 요약·연결 계약이며 전체 보고서/연구 코드/상세 결과/실패 로그는 아래 immutable ZIP에 있다.

## 주요 결과

1. 변하는 proper density의 사건수/H는 J=integral R(t)/nH(t)dt, discrete J=sum h_j R_j/nH_j다. 먼저 적분한 뒤 최종 nH로 나누지 않는다. R proportional nH², Hh=.2의 처방 반례에서 잘못된 값/올바른 값은1.4110594001952546이다.
2. 정확한 nuclear density history와 연결하는 BE residual은 R_n=n1-(nH1/nH0)n0-h*S1=nH1*R_q다. exact nuclear dilution과 BE ion dilution을 혼합하면 반응 없이도 fraction이 변한다. Theta*h=.3,x0=.99에서 x1=1.0279693996155717이다. 현행 정지 F03의 버그 판정은 아니다.
3. photon q=aE,F=nE/(a*nH)이면 source=sE/(a*nH), birth label=a(tb)*Eb다. 새 방출을 공통 초기시각으로 redshift하지 않는다. fixed threshold의 dot eta=source-absorption-H*a*chi*F(a*chi)다. subthreshold photon을 유지하면서 chi*Z를 전체 energy에 다시 더하지 않는다.
4. 즉시흡수는 k/H>>1만으로 보장되지 않는다. 문턱까지 tau=(k/H)*ln(Eb/chi)를 검사해야 한다. k/H=100,Eb/chi=1.001에서9.5117%만 흡수되고90.4883%는 문턱까지 살아남는다. source-counting approximation과 기존 numerical local gate는 별개다.
5. 연속 단색 방출의 prescribed E^-3 bath에서 공급0.6/H는 above0.243882577516055863,absorption0.112261079298440556,exit0.243856343185503581/H로 분해된다. 60자리 birth integral과 독립 conserved-energy quadrature의 최대 count 차이는8.60e-17/H다.
6. density/neutral/electron feedback, pulse와 threshold crossing을 결합한 별도 순수H reference를 실행했다. 종료 xHII=.280055888606393,T=3156.37481603218K,above photon=.003469107238970/H,exit=.026474253136042/H다. 두 상태표현의 fraction/lnT 최대차1.01160e-10, DOP853/Radau3.20988e-12다.

## 검증 범위

최종4개 명령 exit0. unit2,symbolic8,exact rational120,invalid6,monoemission4시각/hazard9점, 세 integration run 각각5segment(max dimension15). 초기+최종 합계30개의 작은 segment solve. 과거 suite 재실행0, 이 runtime의 rustc 부재로 native/cargo 실행0이다.

최대 number ledger residual5.686e-13/H, energy+work4.055e-11eV/H. 보존은 time integration accuracy나 physical/interval accuracy의 증거가 아니다. synthetic constant alpha/E^-3 cross section은 실제 Verner provider나 원자율 accuracy를 대신하지 않는다. QV, Peebles 및 Einstein-solved history를 이번에 계산하지 않았다. integrating-factor residual만으로 이산 energy product가 자동 보존되는 것도 아니므로 event/work의 stage quadrature가 필요하다.

## 동시 native 결과 수신

시작 head aa3e98d7a4f90105c4ac9712ba71c955f9b53cea 이후4 commits가 들어왔고 ccbc15019296b9128a90fa45b9c68c7daddc7b77을 읽었다. 새 flrw_three_equations.rs(blob b25f1ea0d85d7d78b8dfa8b63661423f567a6764)의 실제 pointwise hook이 있으므로 이를 부재라고 계속 표시하지 않는다. connected_cell/photon_balance/ensemble/filling diagnostics 및 외부 최종84 tests를 수신했다. 그 실행을 이 대화 시험에 재집계하지 않았다.

해당 photon array는 a³*n per reference comoving cm³, 옛 cMpc^-3와 다르다. 각 stage의 ensemble perH rate는 이미 그 시각의 mean nH로 나눈 값이다. birth/source history, edge-spectrum reconstruction, integrated event/work와 geometry QV는 별도다. 외부 photon-only history를 coupled atom/photon history로 확대하지 않는다.

## 전체 재현 패키지

파일 REI_CHAT_FLRW03_20261005.zip,56930 bytes,43 entries.
SHA256 f06180a470d6d6700b9d19c6143f2b438b00e0984190014b649d918492e43b18.
Drive: https://drive.google.com/file/d/1r1AvMXqlCSSUElo9VZf2tslIYwgbbE9x/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW03_20261005.zip

ZIP의 rei_chat_flrw03_20261005/ 아래 REPORT_KO.md, EXPANDING_SUCCESSOR_CONTRACT.json, research/run_all.py, results/final_verification.json과 payload manifest를 읽는다. 재현은 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python research/run_all.py다. 신규 standalone oracle만 실행한다.

다음 chat node REI-CHAT-FLRW04_EVENT_WEIGHTED_CONSUMER_CONTRACT는 외부 REI-F04와 별도다. 새 actual pointwise API에 source-stage/birth/edge/event callback을 연결한다. 기존 strict local<2e-4/public width<2e-3,[160,161] FAIL=2.1245050576368385e-4,tick160 및 physical HOLD를 유지한다. R1 백업 metadata와 actual restore를 구분한다. 새 branch/merge/force push 없음.
