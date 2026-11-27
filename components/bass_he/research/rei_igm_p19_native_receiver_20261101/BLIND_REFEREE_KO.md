# 한 차례 자기 적대적 심사 | BASS_HE→REI original-source crosswalk

**BLOCK_NOW: 비교 대상으로서의 P19 D1는 EoR neutral-weighted effective UVB다.** PR332 source는 자체 photon current/opacity로 46k node를 공급한다. H I Γ 72.3배 불일치를 source 결함이나 우주론적 관측과의 72.3배 불일치로 말하면 물리적 오류다. 이번 산출물은 동등하지 않은 source가 동일 frozen target에서 계산한 사건예산 대조로, 원본 REI RUX04 adoption은 보류한다.

**BLOCK_NOW: native HeII 고에너지 group G3는 5e−324 photons/s이다.** P19 D1 유효 HeII photon demand를 source current에 그대로 대입하거나 IMF/AGN escape fraction으로 역추론할 수 없다. 실제 high-energy spectrum/opacity owner, Group G3 flux 및 HeII reionization chronology가 필요하다.

**FIXED: original owner heating 표 수기 전사 오류.** 첫 복사본이 원본 Git blob과 맞지 않아 (1,566 B), 원본 Git 출처와 재조사하여 1,577 B, Git blob SHA-1 `2dbcd3db376fcfad27a19a992814fdd33aea547b`를 일치시켰다. 오타를 새 소유 원본 파일로 제시하지 않는다.

**FIXED: nearly-unit helium fraction subtraction precision.** 처음 HeII node population을 `N_HeI/(1-x_HeII-x_HeIII)*x_HeII`로 복원하면 전역 합의 약 9e-10 차이가 관측되었다. 기존 original provider의 정확한 원소비 `YHe=.079`를 재사용해 `0.079*N_H*x_HeII`로 변경, HeI source를 사용한 독립 abundance 검사 유지. Decimal 재검산 전수 PASS. 이는 수치 representation 오류이며, cosmological perturbation/physics gate relax가 아니다.

**FIXED: log-linear knot endpoint 1e-15 상대 부동소수점 재표현.** 첫 정확 바이트 단언은 실패했고, endpoint 보간을 오류 허용이 물리적으로 정당한 상대 오차로 변경했다. 원본 발표 rate는 수정하지 않았다.

**CONCERN: full correlated parent not reconstructed.** 원본 PR320 accepted interval 중성 분율을 midrepresentative로 사용하고 PR332 original photon-owner와 원본 원소비를 접합했다. 본 결과는 source-conditioned receiver input probe이지 새 46k node H/He chemical IVP 또는 original source history owner에 대한 완전 엄밀성 주장 아님.

**CONCERN: 짧은 z5.81–6.14 interval의 급격한 source cliff.** log/linear interpolation 차이는 H I Γ 5.42배. 이것을 강한 관측 결론 또는 모델 수용 불확실성으로 둔갑시키지 말고 시나리오별로 분리. 원본 곡선의 미출판 보간법을 알고 있다고 주장하지 않는다.

**FINDING: REI PR #344는 이 BASS_HE 스레드가 아닌 원본 REI 저장소에 잘못 게시되었다.** Draft/HOLD는 그대로 보존하고 merge 하지 않으며 이 작업의 소유 repo는 BASS_HE이다. REI 내 예전 source/thermal-root 결과는 참고/수요자 코드 근거이지 BASS_HE DAG나 canonical increment가 아니다.

**Claim ceiling:** BASS_HE RUX02/03 scoped-source diagnostic, 46,080 new frozen target model rows, 0 observational rows, 0 new IVPs, REI central 28/88+0, HE physical 14/18+0, RUX04 NOT_ADMITTED. 외부 다른 저자 blind referee 및 연결 PC/Chrome 실행 NOT_RUN. 중복 검사 반복하지 않고 실제 photon/spectrum owner binding으로 넘어간다.