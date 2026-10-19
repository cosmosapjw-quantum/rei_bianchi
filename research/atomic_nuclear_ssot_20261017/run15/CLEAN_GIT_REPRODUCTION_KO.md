# 고정 Git science commit의 실제 재현 결과

대상은 `6405bcba8ec654bf3ab98182be344cd8c3915b97`이며, 별도 `/tmp/rei_run15_clean_git` checkout에서 실행했다. 원래 복원 branch는 `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`를 그대로 유지했다. 검증 범위는 run13/run15와 현재 bounded diagnostic이다.

최종 지위는 **VERIFIED_SCOPED_WITH_BINARY_BYTE_MISMATCH**다. 전체 검증을 무조건 PASS로 요약하지 않는다.

| 대상 | 실제 결과 |
|---|---|
| 새로운 checkout HEAD/tree | 고정 D와 일치 |
| D에 게시한 RUN15 159개 파일 | Git blob·SHA-256·1,497,833 bytes 일치 |
| RUN13 원본 payload | 333개, 내부 manifest332개 및 source/input113개 일치 |
| Fixed-gas 다섯 설정 | 게시한326개 숫자 필드가 binary64 비트까지 일치 |
| 새 native 세 제어 계산 | 128개 숫자 필드, 16개 node, node/weight32개 숫자와 stdout1,851bytes 일치 |
| 원래 gas fresh build | 571,904bytes, SHA `3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b` 일치 |
| 새 quadrature fresh build | 실행 가능·세 제어 수치 일치. Binary 바이트는 불일치 |
| 실행 전후 source | scoped tracked501개와 HEAD/tree/index 불변 |
| 원래·새 coupled IVP | 재현 시험에서 모두0회 |
| 전체 test suite | 재현 시험에서0회 |

## 남겨 둔 native byte gate 실패

최초 postloss executable은569,800bytes, SHA `ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66`이다. Clean Git에서 새 target에 빌드한 executable은569,792bytes, SHA `a6879cb547a2c7ac86cd15b13c369af006a34a5f2e2a745882700d013862a529`이다.

첫 strict byte gate는 실패했다. 해당 receipt를 보존한 뒤 이미 생성된 세 제어 결과를 읽어 비교하고 원래 gas 빌드를 별도로 완료했다. Fixed-gas나 native 제어를 다시 실행하지 않았다. Path/package metadata 차이와 ELF section 차이를 관찰했으나, 바이트 불일치의 인과적 설명·명령어 수준 동등성·경로에 무관한 byte-identical build recipe는 확립하지 못했다. 세 제어의 일치로 모든 입력에 대한 binary 동등성을 증명하지 않는다.

상세 원문은 `verification/reproduction_D/SCOPED_CLEAN_REPRODUCTION_RECEIPT.json`과 `verification/completion_D/SCOPED_CLEAN_COMPLETION_RECEIPT.json`을 따른다. 후속 add-only 진단 정정이나 compact evidence index가 있으면 그 범위와 원래 실패를 함께 읽는다.

이 검증은 완료된 RUN13 계산을 다시 적분한 결과가 아니다. 복원한 원본 bytes와 새 bounded 구현을 실제로 사용해 확인한 범위를 기록한다. 소실 전 RUN15 네 native raw history의 복원이나 전체 spectral continuum bound는 여전히 미완료다.
