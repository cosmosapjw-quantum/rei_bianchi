# LRS V5 다음 실행 단위

- Parent PR156 `0c2e7b2ada4fea131a5779066894589d0dda8059`. PR150 원자 point owner는 `4e2f0682fb605c6aa940bd756d9869e67b6ded0b`까지 blob 동일. 기존 V4 816건을 반복하지 않는다.
- 채택: Grackle 3.4.1 Case-A RR/DR와 recombination cooling의 10–24 kK 내부, 저밀도 지정 background 부분계. `RESEARCH_V5_KO.md`의 NCP 결과와 독립 검토 scoped PASS에 한정한다.
- HOLD: 고밀도 재결합 시 온도 의존 계수를 동결하는 map의 1차 오차; full native transport/source time-history; Case B, 재결합 광자 재수송, 전체 CI/CE/freefree/CMB, 실제 EoR.
- 다음 단일 계산: PR150 `CovariantTransport::prepare`/`PreparedAbsorption::evaluate`가 만드는 `IgmPhotoInput`에 V5와 동일한 frozen state, Verner spectrum, Grackle donor를 공급하고 source-on FLRW 한 짧은 구간을 실행한다. proper density, `dt/dX`, species/photons, thermal/binding/escape를 stepwise 비교한다. 작은 재결합 우세 케이스로 time-step 1차 결손을 포함한다.
- 원시 결과는 `REI_LRS_ATOMIC_NATIVE_BRIDGE_20261016_000210Z` NCP staging과 별도 immutable archive에 둔다. NCP의 R9/BASS owner 작업은 유지한다.
