# Unit4 exact background cache

원래 배경 계산식을 그대로 둔 32-entry exact-key cache를 production 경로에 연결했다. 새 표적 검사 5개가 첫 시도에 통과했고, 실제 NCP에서 같은 fixture와 8 worker로 off/on을 비교해 전체 물리 상태·ledger·판정·counter·proper time bit가 일치했다.

32 accepted-step 계산 시간은 off 0.602227407 s, on 0.354634095 s로 이 fixture에서 1.69817배였다. 전체 arm 기준 uncached 계산은 1743→135, hit1609, miss135, eviction103, resident32였다. Constructor/setup/warmup/timed/final check가 모두 counter에 포함된다. Historical distinct requested keys는 NOT_MEASURED다.

원자료의 width0/1은 off/on이고 실제 worker 수는 둘 다8이다. speedup_vs_width1은 off/on 시간비이며 parallel_efficiency는 cache 효율 근거로 쓰지 않는다. 이 한 번의 fixture 측정으로 full-history 속도나64core 지속활용을 주장하지 않는다.

BACKGROUND_CACHE_RESULT.json, BACKGROUND_CACHE_REVIEW_MEASURED.json, BACKGROUND_CACHE_LOOP_RECORD.json을 먼저 읽는다. 전체 trace는 runnableZIP에 포함하고 Git에는 compact evidence만 넣는다. Unit3의 실제 five-case screen은 같은 유한 함수라는 검토 근거로 fresh Unit4 full 실행에 재사용할 수 있으나, 모든 screen PASS와 기존 실행 조건이 먼저 충족돼야 한다. Old checkpoint를 exact-source resume로 바꾸지 않는다. Full z20→4 history는 아직 실행 완료로 주장하지 않는다.
