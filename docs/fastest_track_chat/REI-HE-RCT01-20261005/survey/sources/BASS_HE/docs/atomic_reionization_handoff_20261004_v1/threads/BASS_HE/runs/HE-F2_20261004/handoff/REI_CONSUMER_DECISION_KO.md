# rei_bianchi로 전달할 HE-F2 재개 조건

BASS_HE fastest HE-F1 공급기0.1.1은 완료다. 동일반응의 명시적GM25/KF96 대안을 제공한다.
BASS_HE HE-F2의새원자전달물은 READY지만 실제 소비기 binding은 미수락이다.

고정해읽은 소비기: forward/rust-reion-kernels-20260922,
64bc3aa0871bb324817afd3d36db018dd34181cf. MODEL_POLICY의 id는
REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1. 그모형의 charge_exchange제외와
Tguard30000..110000K,RR/DRescapeclosure를존중하여RHS를수정하지않았다.
GM25/KF96공통1000..10000K와교집합이없다. KF96단독지원은paired비교나물리수락이아니다.

소비기스레드에서 할 다음단일작업은 원자원전재조사나큰runtime이아니라 RCT의범위/closure선택이다.
현재FT03 baseline은그대로진행한다. RCT가현재목표에불필요하면 optionalREI-F09보류를명시하고
BASS_HE에그결정identity를반환한다. RCT감도가필요하면 결과보기전에별도모형ID와온도범위를고정하고
각source의범위가모든평가점에서충족되는지확인한다. 두출처비교는공통범위에서만한다.

반환할최소machine-readable 항목:
- scope/model id, exactrepo/commit/path/hash, RCT enabled 여부와 source_id 또는 비교family
- 온도domain,Maxwell/commonT/zero-drift,초기상태/동위원소scenario,단위
- RCT closure id 및 approximation: fulltransport,coupledOTS,escape또는명시적limitedclosure중실제선택
- binding/thermal/photon/escape/recoil소유권,density곱한번과proper/comoving/time변환의소유자
- 실제providerinstance/runtimeadapter identity. schema파일만반환하지않는다.

참고결속: Y=nHe/nH; r_H=k*nH*Y*(1-xHII)*xHeIII;
(dxHII,dxHeII,dxHeIII)=r_H*(1,1/Y,-1/Y). directelectron0,photonbirth1.
Q=chiHeII-chiHI는chemicaldefect이고 E_gamma=Q,promptheat0은별도근사선택이다.
공급기null을0으로고치지말고consumer-owned추가closure로표시한다. opacity미시/유효중복금지.

소비기결정이도착할때까지HE는동일contract검사·wrapper추가·B5C3재개를반복하지않는다.
새계약이실제로생기거나현재핵심입력이바뀌면affected path만회수해HE-F2를완결한다.
BASS_HE에서우주론campaign을실행하지않는다. NCP성능최적화·largehistory handoff는현재불필요하다.
