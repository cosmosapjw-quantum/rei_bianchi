# BRIDGE02 -> cohort parent box와 실제 transaction admission

대상은 cosmosapjw-quantum/rei_bianchi, forward/rust-reion-kernels-20260922, draft PR83이다. 시작·단계 경계·게시 전후 live ref와 관련 delta만 읽는다. 원 source/S0/CODEX_SYNC/runtime 반환은 변경하지 않는다.

이번에 닫힌 것은 F08 점값 순서 재현과 시간/birth 오차의 독립 분리다. 원 T0 macro1.25e9 s의 half6.25e8 s에서 geometry→endpoint source→endpoint BE를 구현했고, 처음 두 committed half의 세 분율은 원 기록과 같았다. 전체 paired_trial의 interval root/local/width/restart를 실행한 것은 아니다.

같은 T0 시계에서 grid8 T=47942.77067098594 K, cohort T=47917.90527278305 K다. 계승한 연속 참조47917.6292226325 K와 각각25.14144835345,0.27605015056 K 차이다. 별도 midpoint-birth 교차시험은 M16/32/64와 공통188구간을 r1/2/4로 세분했다. M64/r4에서 time 차이0.7787622641 K, source 차이-0.0009109058 K다. 원 F08의 implicit source를 literal endpoint Dirac birth와 동일시하지 않는다.

다음 한 bounded gate는 실제 primary_stage_root의 photon parent boxes에 증가하는 cohort 길이를 연결하고, 기하/birth count enclosure와 reject/commit을 원 macro transaction 하나에서 검사하는 것이다. 에너지 literal 또는 characteristic 반올림의 해석을 명시한다. 이전 interval 불확실성을 소멸시키거나 기대 absorption/reference endpoint를 정답으로 주입하지 않는다. 기존 source clock과 canonical gate를 유지한다. 후보는 opt-in이며 production default로 바꾸지 않는다. 전체 F08 campaign은 재실행하지 않는다.

현재 시간오차가 지배하므로 방출 cohort 수만 늘리거나 증명 없는 압축을 우선하지 않는다. SPEC05 signed-bound, BI raw 입력, 물리fit/생략과정은 별도 열린 의존성이다. 1.25e9 s의 옛 native certificate를1e12 s에 이전하지 않는다.

전체 코드와실행증거는 ARCHIVE.json의 sealedZIP에 있다. 재현은 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. Source13과inputidentity를 먼저 검사하고, network/Cargo 없이13개native진단과4개새reference를 실행한다. 구성단계들은 이번에 실제 실행했다. Launcher 자체는py_compile을 확인했으며 추가폴더에서전체 end-to-end 재실행하지않았다. 이전suite/proof를또반복하지않는다.

새6tests 중clock3개만red/green이고endpoint3개는tests-after다. 원scientificmodule의버그를수정한것이아니다. Outgoing백업R1과remote전체복구를구분한다. Local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD보존. 같은branchappend-onlynonforce, 기존Drive/Dropboxcreate-onlybackups.
