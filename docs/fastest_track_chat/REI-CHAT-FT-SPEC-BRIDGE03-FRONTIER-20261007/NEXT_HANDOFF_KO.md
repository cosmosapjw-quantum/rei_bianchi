# BRIDGE03 FRONTIER -> 실제 출력격자 연결

같은 rei_bianchi, forward/rust-reion-kernels-20260922, PR83. 시작·단계 경계·게시 전후 live ref와 관련 delta만 읽는다. 원 scientific source, S0, CODEX_SYNC, runtime 반환은 유지한다.

첨부 BRIDGE02 SHA b18d67...와 원격 동명 SHA9820ae...는 다른 산출물이다. 이 결과는 첨부의 birth-frontier 연구를 계승했고 원격의 cohort parent-box admission은 별도 owner로 남겼다. 원 BRIDGE02 문서를 덮어쓰거나 과거 미게시 패치를 적용하지 않는다.

이번에는 t/T=.25,.5,.75,1의 출력시각과 각 cutoff/binding의 birth 역상을 미리 분할했다. 원 T0 half-clock 경계1601개를 모두 보존한 공통2237구간에서 여섯 source규칙을 실행하고 같은G2B64 birth로4474구간을 추가했다. Source가 변할 때clock을 바꾸지 않고 time만refine할때birth를 바꾸지 않는다. 출력마다광자를재배분하지않는다.

PlainM128의active참조차3.73609e-6/H에서splitG2B64의1.88587e-7/H로감소했고time이등분뒤9.42948e-8/H다. 온도차는.226857K->.113450K다. G2B32/B64차1.24e-10/H를전체오차로간주하지않는다. 무흡수registeredtime계산은정확산술에서정확하지만unregistered.831T에-3.02075e-5/H가남는다. FreeCDFbound4.51055e-5/H는coupledgascertificate아님.

다음 한 작업 FT_SPEC_BRIDGE04_DECLARED_OUTPUT_GRID_ADMISSION: 실제 F08 public output 시각 목록과 관측량별 spectral predicate를 읽고 source partition을 그 목록에 연결한다. 또는 별도로 증명한 연속 birth-cell 출력 적분을 구현한다. 서로 다른 출력시각마다 다른 물리적 photon realization을 만드는 방법은 금지한다. 사전등록 출력의 수가 많아지는 비용과 coarse birthcell compression은 별도 조건 없이는 승인하지 않는다.

Actual primary_stage_root의 photon parentboxes와 에너지 불확실성은 원격 해당 lane의 결과를 먼저 수신하고 중복 구현하지 않는다. Point comparison으로intervalgate를승계하지않으며fullF08campaign을재실행하지않는다.

재현 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. Source13hash확인후test/compile/7native/nativecheck/theory 다섯명령. 최종7이력17896stage21independentroots5006scalar,turn전체14/35792/42. Unit8개중1개red/green,나머지tests-after. Parent suite/native oldcampaign/newcontinuousIVP/cargo0. Toolchain서명진본성은미검증.

Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존. SPECsigned,BIraw,physicalfit/omittedcooling은open. 같은branch새FRONTIER폴더append-onlynonforce와create-only이중백업. R1metadata,byteidentity,remote복구와과학검증을구분한다.
