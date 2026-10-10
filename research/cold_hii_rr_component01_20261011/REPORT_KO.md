# COLD_HII_RR_THERMAL_COMPONENT01

HG97 원전 PDF의 고정 SHA와 기존 REC 네 endpoint에서 별도의 공개 Rust HII Case-A 재결합·냉각 성분을 구현했다. `cold_hii_rr::coefficients`와 `cold_hii_rr::stage`가 proper SI를 사용한다. 온도는 3..1e9 K이며 경계 밖 입력은 typed error를 반환한다.

`ne=nHII=nH*xe`로 재결합 반응률과 냉각 power를 계산하고 HI/HII/electron 변화를 같은 반응률에 결속한다. 열·binding·escape 에너지는 별도로 반환한다. Escape photon 수와 spectrum은 정의하지 않았다. He은 spectator다. 입자수 감소를 포함한 Tdot도 같은 stage에서 반환한다.

Build 1회(exit 0), 네 endpoint campaign 1회(exit 0)를 수행했다. Decimal80 oracle의 최대 상대차는 1.1705252239672026e-15, Tdot scale 차는 8.721433894769249e-16, total power scale residual은 0이다. 도메인, zero-reactants, conservation 및 기존 저온 `RAW_TEMPERATURE_DOMAIN` 검사도 통과했다. 최초 stdout/stderr와 실행 receipt를 evidence에 보존했다.

이는 순간적인 HII 성분의 수치 구현 결과 `PASS_SCOPED`다. HG97의 2%는 Ferland et al. 자료에 대한 각 fit의 agreement일 뿐, 독립 원자물리 오차, 전체 열·이온화 closure 오차 또는 history uncertainty가 아니다. 저온 전체 atomic/thermal closure, He 반응, Bianchi IC 채택, CR 진화, coupled history와 global admission은 HOLD다. 기존 AtomicProvider/FT03/PhysicalHistory에는 변경이 없다. 독립 Astra review도 `PASS_SCOPED`이며 추가 build·campaign은 수행하지 않았다.

Bounded harness RULES 파일은 현재 경로에 없어 HARNESS_UNAVAILABLE로 기록했다. Parent가 고정한 one-build/one-campaign 실행 제한을 적용했다. Git commit/push는 수행하지 않았다.
