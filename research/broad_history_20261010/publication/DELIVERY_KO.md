# REI-ACCEL01 전달 및 복구 기록

z20→4 전체 구간의 축약 R15/HG97-B 계산, 수렴 및 독립 적분 비교, 과학 그림과 연구 DAG를 게시했다. 판정은 **PROMOTE_SCOPED_REDUCED_HISTORY**다. 전체 native CR/RCT/HH/열진화는 **HOLD**이며, 모두 해결했다는 뜻이 아니다. 원래 원자 정밀 연구 lane은 보존했다.

- REI: [PR104](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/104), draft/unmerged.
- 과학 commit: `7530e0239a4d30e99bfeba68d4b4ddc0b78a2c18`.
- 새 문서/receipt만 후속 commit에 추가한다. 이 후속 commit은 과학 결과나 허용 기준을 바꾸지 않는다.
- BASS, bass_cr, BASS_HE, WU088_HH, rec_bianchi에는 각각 새 `research/rei-accel01-sync-20261010` branch로 담당 작업을 전달했다. 정확한 commit은 DELIVERY_RECEIPT.json에 있다. 기존 owner branch를 merge/force-update하지 않았다.

## 최종 복구 묶음

**C02B를 사용한다. C02는 잘린 ZIP이므로 사용하지 않는다.** 실패 기록은 C02_INVALID.json에 남겼다. 원인은 확인하지 못했다. C00/C01은 유효한 앞선 checkpoint다.

- 파일: `REI_ACCEL01_C02B_FINAL_20261010.zip`
- 크기: 30,729,916 bytes
- SHA-256: `3d114d3bea604035e2873b804e965605ea8ff9dc06caebe82e5dadfa735e2857`
- [Drive 최종 묶음](https://drive.google.com/file/d/1TW1f2vC9ix2qXLn9vsbv0dsMzS-_Dj8z/view)
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/REI_ACCEL01_C02B_FINAL_20261010.zip`
- Drive는 공급자 메타데이터의 크기 일치를 확인했다. Dropbox는 실제 내려받은 전체 파일 SHA-256, ZIP CRC 및 내부 219개 파일 SHA-256을 확인했다. 두 공급자 모두에서 복원 실행을 했다는 의미는 아니다.

과학 commit을 checkout한 rei_bianchi 루트에 묶음을 overlay하면 전체 원시 궤적과 reference, 보고서, 코드, DAG가 복원된다. `RESTORE_MANIFEST.json`으로 파일 해시를 확인한다. 압축 내부 `handoff/` 행정 기록은 묶음 생성 전 snapshot이며, 최종 백업 ID와 상태는 이 detached Git receipt가 우선한다. 압축 파일 자체를 Git에 넣지는 않았다. 논문 PDF 원문도 재배포하지 않았다.

## 바로 이어갈 작업

`RESUME.json`, `DAG.json`, `BLOCKERS.json`, `START_CODEX_KO.md`를 읽고 N1(source/low-T), N2(native chronology)를 병렬 진행한다. BASS N4, CR C1, REC A_REC는 별도로 진행할 수 있다. N3 전체 native history는 N1/N2 뒤에 온다. 완료된 RUN001/002와 기존 PHYS21/22 검산을 반복하지 않는다. 4시간마다 실제 입력·코드·진단·first failure와 다음 최소 실험을 checkpoint로 남긴다. 현재 백그라운드 실행 작업은 없다.
