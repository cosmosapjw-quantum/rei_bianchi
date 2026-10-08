# BRIDGE09: 동일 birth family의 매개변수 포함 macro 비교

판정: SCOPED_PARAMETER_MACRO_COMPARISON_ACCEPTED__CONTINUOUS_ERROR_UNIFORM_LEDGER_RESTART_OPEN.

0..1.25e9 proper seconds의 첫 macro에서 같은 6개 birth 시각과 count/energy/gas family를 사용했다. 부모 BRIDGE08의 fine 9구간과 공통 첫 source의 증거는 해시로 계승했고 재실행하지 않았다. Fine에서 전역 midpoint 6.25e8 s만 제거한 full 8구간 중 나머지 7구간에 세 family를 적용하여 새 root 21개를 계산했다. 원 scientific source 13개와 S0/FT03, production 기본값은 불변이다.

세 family의 이산 full/fine 차이 상계는 각각 1.6970306694e-7, 3.1767814080e-7, 3.2167959108e-7 이하이다. Fine 공개 구간폭은 각각 7.0166095157e-13, 1.4797734061e-7, 1.5197893133e-7 이하이다. Local < 2e-4, public width < 2e-3와 point ledger <= 1e-12를 유지했다. Point ledger 상계는 3.264e-16 이하이다. 새로운 norm은 원 고정 node 대신 cohort별 N/U와 합을 사용하므로 원 paired_trial의 전 계약을 승계하지 않는다.

각 고정 매개변수에서 K subset intY, norm(I-C Ry)<1로 root를 포함하고, 두 endpoint 직사각형의 차이로 matched-parameter 차이를 보수적으로 포함했다. 독립 box subtraction은 상관관계를 잃으므로 상계 실패가 실제 오차 초과를 증명하지는 않는다. 매개변수 폭은 물리오차나 시간오차의 추정값이 아니다.

핵심 반례: 같은 사건격자의 순수 팽창 냉각에서 fine 참오차는 full/fine 차이의 5.05609992326배였다. 대부분의 사건 cell은 세분되지 않기 때문이다. Global midpoint가 이미 필수 사건이면 두 partition이 같아 proxy=0인데 참오차가 남을 수도 있다. Adapter는 동일 partition을 VACUOUS_COMPARISON_MESH로 거절한다. 일반 Richardson 계수나 연속 LTE 인증으로 이번 proxy를 승격하지 않았다.

새 빈 폴더의 6개 명령은 모두 exit0. 12unit 중1 assertion RED/GREEN,11 tests-after;21 uniform roots,33 native point records,centre 포함54 source calls,독립70자리root9,128 exact cases/256 identities를 확인했다. Pilot까지의 source 호출은108이며 구분해 기록했다. 새 IVP/Cargo/부모 fine proof/기존 campaign/다른 owner science는0이다. 명목 점 장부와 uniform parameter-family escape/work 인증을 구분했고, 후자는 아직 미완료다. 새 adapter의 clone/commit rollback 시험은 canonical checkpoint restart가 아니다.

HE RCT03E3의9 direct-rate Gauss차수축 실패, HH ON06G와HH-XTHREAD01, CR R9를 수신했지만 해당 결과를 이번 승인에 합치지 않았다. Historical [160,161] FAIL,tick160,auxiliary escape FAIL,physical HOLD를 유지한다.

다음 BRIDGE10_EVENTWISE_REFINEMENT_PROXY는 같은 birth와 원 입력 family에서 full8의 각 필수 사건 cell을 반분한16구간이다. 기존 full8 proof는 계승하고 새 fine16만 계산한다. 첫 cell도 바뀌므로 원 t0 family에서 시작해야 한다.

## 전체 재현 자료

REI_XTHREAD_BRIDGE09_20261008.zip: 2708333 bytes,102 entries,101 payloads.
SHA256 be4d73943fa6bff09e3d7d060ed21db17b3d2058cbe263789e155bdda29da7f7.
Drive: https://drive.google.com/file/d/1oDHEep0nqJANARXLVbLuMGXmsxx2myvp/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_XTHREAD_BRIDGE09_20261008.zip

ZIP의 rei_bridge09_20261008/REPORT_KO.md와 results/final_verified/FINAL_VERIFICATION.json을 읽는다. 재현은 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. Network/Cargo/IVP/fine-proof 재실행은 없다. 이 폴더의 acceptance.py는 실제 시험한 파일과 Git blob/bytes가 동일하다. 전체 Rust source, binary, stdout, 독립 검사기와 실패 로그는 ZIP에 있다.
