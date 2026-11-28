# RCT03E: 실제 coupled path의 시간·분광 정확도와 관측량 예산

이번 RCT03D는 frozen segment 평가기가 아니라 기존 short-hhe-midpoint Newton/characteristic path를 실제 결합한 로컬 수정본이다. 전체 12개 짧은 coupled chain, 432개 단계가 원 비선형·광자수·에너지 gate를 통과했다. 같은 연결을 새로 작성하지 않는다.

읽기: REPORT_KO.md, PLAN.json, FOLLOWUP.json, RETURN.json, evidence/canonical/RESULTS.json, OWNER_RCT_DELTA.patch. sourcefree N1600 성공과 기존 C1 kernel 검사, 원자·과거 reference 전체 suite는 수신 때문에 반복하지 않는다.

원 remote receiver 39c39eab/owner source reservation은 유지한다. OWNER_RCT_DELTA.patch는 research/transport_20261007/short-hhe-midpoint/src의 material/coupled/radiation 세 파일에 적용한다. receiver에 igm_rct_point module/export가 이미 필요하다. 전체 staged vendor는 패키지에 있고 inputs/RECEIVER_MIDPOINT_COMBINED_FROM_03B.patch는 이전 dependency patch다. 적용한 적 있는 receiver에 다시 중복 적용하지 않는다. 기본 State::new/OFF는 보존하며 with_rct의 empty-radiation 경계는 별도 opt-in이다.

다음 과학단위는 동일 common-domain/source 제조조건에서 보호할 시간·분광 관측량을 명시하고 refinement/reference 범위를 고정하는 것이다. 현재 N24->48의 최대 온도 차는 약1e-4K이므로 root/energy gate 통과만으로 exact-flow 또는 모든37field 정확도를 주장하지 않는다. Gauss2->4가 작은 것만으로 시간오차를 닫지 않는다. midpoint의 unconditional positivity/강성감쇠나 장기source-driven history도 미확립이다.

RCT source는 nonphoto material stage에만 들어가며 A/B/primarysource의중복계산금지, cell-midpoint RCT와 event-bounded radiation stages의 구분, 실패시모든후보장부폐기, source/mean 고정,실제EOS common guard를보존한다. baselineOFF/원자모멘트null/physicalHOLD/HE-F2globalfalse/F09전체미완료는유지한다. 실제광자평균계산을이조건부closure경로의새필수gate로묶지않는다.

재현: bash run_checks.sh /absolute/new/output. Rust1.94.1 prefix, Python3+SymPy가필요하며외부Rust의존성은없다. 주어진출력은새디렉터리여야한다. fullwrapper는실제로exit0을확인했다. 원본 vendor/owner source를고치지않고특정12tests,12이력,별도originalOFF1이력만실행한다. 전체원자/기존benchmark를실행하지않는다.
