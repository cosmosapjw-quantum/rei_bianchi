# V7 다음 실행 단위

기준: PR161 `4e292a44e71dfca35d551c754fc1a64151c368c7`; native PR150 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`. V7의 source-on X∈[0,1e-5], N=16/32/64/128 결과와 원시 파일은 `evidence/ncp_20261016T0118Z/`에 있다. Baseline·midpoint 각각 4/4 exit0, 원본 baseline parity byte equality, `cargo test --test axbi_driver` 13/13 PASS. 전체 2차는 HOLD이다.

다음 첫 계산은 source-free **동일 Rust RR/DR midpoint 연산자**를 독립 Radau와 직접 비교하는 작은 시험이다. 현재 `reference/radau_casea_reference.py`는 PR150 literal rate, FLRW density/H(a)의 연속 RR/DR reference이며 129/129 owner table parity를 보인다. 하지만 Rust RR-only 단계를 별도로 실행하지 않았으므로 직접 오차를 아직 보고할 수 없다. 먼저 이 실행 seam과 RR/DR cooling의 별도 ledger를 추가하고 10–24k K 범위에서 time refinement한다. 기본 source-on 결과를 반복하지 않는다.

그다음 native full source-on 1차 주도 항을 식별한다. 기존 owner는 각 전체 step의 source를 먼저 주입하고 photon을 BE 감쇠시키며 비재결합 chemistry도 BE이다. source-age 적분과 photon attenuation의 시간 중심 연산자를 독립 experimental branch에서 바꾼 뒤, 같은 초기 상태·물리 구간·Q64/nmu8 설정으로 직접 재계산한다. 2차 판정은 T, electron, photon N/U에서 연속 두 slope 1.8–2.2와 독립 ledger를 모두 요구한다. 기존 PR150 production과 checkpoint는 변경하지 않는다.

Case-B emitted photon retransport, full EoR history, signed Bianchi I, spectral/angular 수렴과 강성 영역은 계속 HOLD다. PR #150 기존 full Q512/Q1024는 종료된 별도 실행이므로 재시작하지 않는다.
