# HE29 HPC64 실제 canary 반환 분석

**기존 native reference 4/4 pair를 재사용했고, 신규 packed canary 1/1을 유한 case 범위에서 채택했다. 현재 준비된 미완료 HE29 실행은 0개다.** 이 소비자 분석에서는 NCP 제출, solver/native 실행, 기존 tests 재실행이 모두 0이다.

- 실제 실행 code: `802a32361288bf5aa0e0d1f63c912768f1a1d407`.
- 실제 반환: [PR81](https://github.com/cosmosapjw-quantum/BASS_HE/pull/81), 원본 `d6c1cf97ee216269114b1b0d1bb45984e2140f8b`.
- 결과를 바꾸지 않은 게시 tree 복구: `fcdf56d9a66b2d159d42a9a72131f94040cd5891`, tree `ffef714245a9a69a008395e0f93ae7893173d91a`.
- [수치·성능 해석](RESEARCH_KO.md), [실제 소비자 분석](evidence/CONSUMER_ANALYSIS.json), [게시 복구 영수증](evidence/PR81_TREE_REPAIR.json), [생산자 반환·백업 영수증](evidence/PRODUCER_RETURN_RECEIPT.json).

소비자 reader는 저장된 JSON과 gzip만 읽는다. 새 원시 gzip은 handshake 1개와 point 182,280개를 EOF/CRC까지 읽었고, 모든 record의 source/binary identity, 유한 wire 값, count가 일치했다. 새 bridge library bytes도 SHA가 일치했다. 원래 native owner binary, table 배열, 22 DATA의 실제 bytes는 이번 새 archive에 없으므로 기존 admission 및 생산자의 identity 검사를 재사용한다. 이 경계를 새 bytes 검증으로 바꾸어 적지 않는다.

반환 archive `BASS_HE_HE29_HPC64_CANARY_RETURN_20261021_a00990e5.tar.gz`는 32,120,999 bytes, SHA256 `a00990e5f8a5978a8881c1b56fb96072df5abd91600495494b9397cc9360aec7`이다. 생산자 Dropbox/Drive 전체 raw PASS 영수증을 읽었다. 소비자는 Dropbox 실제 raw readback을 수행했고, 중단 중 workspace pruning 이후 같은 archive를 복원했다. 과거 Drive UNKNOWN과 무재시도 정책은 그대로다.

PR78과 PR81은 모두 Draft/open/unmerged로 유지한다. `4b7621…`의 SSH 인증 HOLD는 과거 시도의 기록으로 보존하며 현재 canary 상태를 덮어쓰지 않는다. 현재 문서 HEAD, 실행 code pin, 결과 게시 pin은 서로 다르다.

연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 HOLD다. 실제 단일 canary 시간은 측정됐지만 동일 작업의 packed 전후 대조가 없어 solver 전체 속도향상 배율은 아직 없다.
