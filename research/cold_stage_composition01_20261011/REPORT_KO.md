# COLD_STAGE_COMPOSITION01

네 source-pinned REC endpoint에서 HII Case-A RR, prescribed-CMB Compton, FLRW 팽창 및 EOS의 순간 미분 조합 구현 검사 결과는 `PASS_SCOPED`다. 독립 Astra review와 controller의 백업·게시 상태는 별도 gate다.

새 production `cold_stage_composition::stage`가 기존 `axisym_coupled_derivative`를 실제 호출한다. callback은 현재 isotope state와 thermal energy에서 nH, nHe, xe, thermal particle density, T를 재계산하고 기존 RR와 Compton을 동일 stage 입력으로 호출한다. 실제 binary64 입력은 native 출력 및 validation에 저장했다. engine이 dilution, thermal work 및 입자 수 보정을 소유한다.

열과 binding, recombination escape, prescribed CMB bath를 별도 ledger로 유지했다. photon derivative의 정확한 0은 transport photon state가 없는 이 경로의 값이다. 재결합 방출 광자수의 물리적 값은 여기서 정하지 않는다.

초기 build 1회와 campaign 1회가 모두 exit 0이다. campaign의 derivative attempt는 16회이며 history 실행과 solver step은 0회다. 실패·수정·재실행은 없다. 첫 stdout/stderr와 명령, exit, binary SHA, stdin, wall receipt를 evidence에 보존했다. 원래 bounded harness 실제 경로는 없어 `HARNESS_UNAVAILABLE`을 기록했다.

Decimal80 oracle 최대 scaled 오차는 `1.1345786410396341e-15`, source/팽창 보정 energy 및 charge/baryon 최대 scaled 잔차는 `3.4474616774518186e-17`이다. frozen 계약의 각각 `3e-12`, `1e-13` 한계를 만족한다. source-free, H=0, RR-only/Compton-only engine 비교, ne=0, bath equality/sign, xe doubling 및 unsupported HeII/photon/shear/저온 거절 controls도 같은 campaign에서 통과했다.

baseline/refined derivative 차이는 `VALIDATION.json`에 보고했다. 이 차이는 새 시간 수렴 증명이나 combined model uncertainty로 해석하지 않는다. He reaction closure, Bianchi background/IC 채택, CR evolution, coupled history, radiation backreaction, global admission은 HOLD다.

검토 승인 후 controller가 recovery backup·publication을 수행하고 `COLD_CONDITIONAL_IVP_CONTRACT01`로 전이한다.
