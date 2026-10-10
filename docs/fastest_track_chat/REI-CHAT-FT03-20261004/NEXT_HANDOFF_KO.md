# FT03 -> FT05 Bianchi-I transport

대상은 cosmosapjw-quantum/rei_bianchi, 기존 branch forward/rust-reion-kernels-20260922, PR83이다. 현재 remote HEAD를 확인하고 본 FT03 요약/반환을 계승한다. 새 branch/merge, full Grackle/Rust build, 큰 production history는 하지 않는다.

읽기 순서: 본 README_KO.md와 TASK_RETURN.json → ZIP의 REPORT_KO.md → MODEL_POLICY.json → RESEARCH_DAG.json → 다음 연구의 필요한 exact input만. FT01/FT02 전체 재감사를 하지 않는다. FT03은 독립 Case-A escape 연구모형의 closure와 finite-domain comparison 및 경량 reference를 닫았지 physical accuracy/admission을 닫지 않았다.

다음 ready: REI-CHAT-FT05_BIANCHI_I_TRANSPORT.
1. static thermal/binding/primary/escape reservoirs의 proper/comoving 변환과 팽창에 따른 work/redshift 항을 정식화한다. photon energy와 particle number에 같은 dilution factor를 쓰지 않는다.
2. diagonal Bianchi-I의 fixed covariant spatial momentum으로 에너지·방향·solid-angle mapping을 구성한다. 이미 채택된 geodesic 전체를 재증명하기보다 새 reservoir/opacity 인터페이스와 연결한다.
3. 작은 angular/spectral reference로 collisionless number, energy/redshift 및 FLRW isotropic limit를 확인한다. cold gas-rest-frame scalar absorption과 polarization transport의 경계를 명시하되 기존 BASS hierarchy를 복제하지 않는다.
4. FT03 coefficient/moment 및 instantaneous Case-A escape의 수송 도입 경계를 정한다. 실제 우주의 optically thin/secondary 부재를 자동 승인하지 않고 정지 T bound를 팽창 모형으로 이전하지 않는다.

FT04 actual-map remainder는 실제 Rust residual/source-site/parameter-box parent가 있을 때만 identity를 연결해 활성화한다. 해당 항이 없다고 독립 FT05 이론을 막거나 전수감사로 되돌아가지 않는다.

주의: rate fit error는 differentiated cooling error bound가 아니다. HeIII literal8*A*T와 hydrogenic8*Lambda_H(T/4)는 다르다. raw source는 보존했고 새 모델은 rate-moment cooling을 선언했다. DR 두공명은 각기 다른 kinetic energy를 가진다. capture count는 emitted-photon multiplicity가 아니다. ceHeI/ciHeIS 및 line/brem/Compton 등은 controlled experiment에서 제외했으며 production negligible로 승인하지 않았다. 온도 bound는 numerical flow/root/remainder 인증이 아니다.

strict local<2e-4, public width<2e-3, [160,161]FAIL=2.1245050576368385e-4와 tick160 보존. 새 결과도 같은 branch에 non-force append하고 기존 Drive/Dropbox 폴더에 create-only 백업한다. ACK/metadata, remote byte restore, 과학적 정확도를 구분한다.
