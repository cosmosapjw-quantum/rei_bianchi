# SOURCE012 입력 수집 결과

부분 수집 및 publication 검토는 scoped PASS로 닫혔지만, 완전한 입력 번들은 계속 `HOLD`다. 수집은 승인된 원본 커밋 `553ce556d9f8662290c000ec675c7e6007c9d895`와 native base pin `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`에서만 수행했다. native pin은 기본 crate를 가리킨다. 캠페인 ELF에는 별도 supplier overlay/accessor가 포함되며, 두 층을 동일한 소스라고 주장하지 않는다. 권위 있는 매핑 파일은 복사본의 `SOURCE_IDENTITY.json`과 `WORKER_RETURN_CONTRACT.json`이다.

첫 수집은 1.06초 뒤 exit 3으로 끝났다. collector의 `put()` 호출에서 `category` 인자가 빠져 있었다. 첫 오류와 부분 원자료는 보존했다. Astra가 승인한 한 번의 제한적 수정 후 fresh `attempt_002`를 1.53초 실행했으며, exit 2와 `HOLD`를 반환했다. 두 static dependency를 `git show`로 읽는 과정에서 Git object pack을 매핑하지 못해 exit 128이 발생했다. 따라서 재시도하지 않았다.

두 번째 시도에서는 supplier 파일 33개와 native base 파일 141개, static dependency 후보 62개 중 60개 및 지정 ELF를 수집했다. private 자료는 두 시도 합계 409개, 7,396,570바이트다(첫 시도 174개, 두 번째 시도 235개). 지정 ELF는 복사 중 계산한 SHA가 승인된 값과 일치했다. 첫 시도와 두 번째 시도의 메타데이터·명령·자원 관측은 각각의 wrapper receipt에 기록했다. 공개 manifest는 `attempt_002/COLLECTION_MANIFEST.json`이다.

누락된 정적 의존성은 `configs/rei_fastest_v1/science_scenario_v1.json` 및 `docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json`이다. 따라서 입력 번들은 완전하지 않으며, 후속 검토 전까지 `HOLD`를 유지한다. 이 수집 결과는 과학적 판정이 아니다.

데이터 축의 의미는 고정 계약 그대로다. `repaired_ncp` axis1 level 1/2/4는 age/birth 패널 8/16/32이고, `source_native` level 1/2/4는 birth 수를 8로 고정한 time subdivisions이며 age-pair refinement가 아니다. 초기 조건은 `[0.01, 0.01, 0.001, 1.1295017576662223 eV/H]`, `delta_lna=0.002`, `q=-0.1`이며 BASS009/010 초기 조건 또는 기하가 아니다.

범위는 baseline H/He와 명시된 e-only 표시에 한정된다. D/full17 네트워크 활성화, coupled 또는 isotope 과학적 승인, solver/reference의 성공 주장은 없다. per-call Gamma, heat, prepared nodes, trial absorber context, intermediate old state 및 성공적인 양수 independent reference는 `null/HOLD`로 남는다. 적분 이벤트로 이 값을 대체하지 않는다. 요청 프로파일은 역사적 Luna/low이며 실제 런타임은 독립 관측되지 않았다.
