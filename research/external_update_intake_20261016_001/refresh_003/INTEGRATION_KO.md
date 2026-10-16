# 외부 업데이트 반영 — 2026-10-16 02 UTC

로컬 Dropbox 최신 파일을 먼저 조사한 뒤, GitHub의 BASS·REC·REI PR을 확인했다. 기존 checkout과 dirty 파일, 원래 계산의 epoch·deadline은 보존했다. 원시 비공개 자료는 공개 git에 추가하지 않았다.

## 실제 반영

- **FULL005 Thomson 비교:** 새로 게시된 구현·실제 결과·독립 검토를 같은 branch에서 동기화했다. 저장 PL 이력의 공통 z20→4 구간에서 명목 `B=8.749468843353422e-8`, `q=8.749468460587409e-8`이다. 양성 조건과 명목 binary64 계산에 한정한다. outward enclosure, 점별 visibility 진폭, z<4 tail, solver 수렴은 보증하지 않는다. 이미 완료된 계산은 반복하지 않았다.
- **비선형 오차 예산:** 별도 owner의 C6–C9 구현·synthetic 검사·독립 검토를 동기화했다. C9는 제공된 R/J packet에 대한 선형화 진단만 scoped PASS다. 실제 accepted-state residual/Jacobian packet은 아직 없으므로 현재 solver의 상태 오차를 판정한 결과로 사용하지 않는다. 다음 측정에서 검토된 모듈을 재사용하고, 완료된 oracle·검사는 반복하지 않는다.
- **HE25 백업:** 분할 gzip/tar의 146개 member 목록과 작은 메타데이터를 repo 밖에 복원했다. 선택한 4개 문서의 SHA는 내부 manifest와 일치한다. 짧은 고정 이산화 모델의 시간 수렴과 독립 Radau/DOP853 비교를 참고한다. source·초기 조성·정규화가 현재 MD14 계산과 다르며 spectral 수렴은 HOLD다. 별도 review receipt가 archive 목록에 없으므로 보고서의 검토 진술을 현재 REI의 독립 admission으로 승격하지 않았다.
- **R9 T4 종료 백업:** tar SHA를 sidecar와 대조했다. wall limit에 따른 부분 종료, supervisor exit -9, numerical pass false, checkpoint length 64 및 32→64 refinement 실패를 유지했다. 완성된 isotope provider로 채택하지 않았다.
- **REI #162–165:** source-age·birth cancellation·따뜻한 RR/DR 참고 결과를 exact commit으로 기록했다. 기존 실패의 원인 가설을 좁히는 자료이며, 현재 cold MD14 모델의 원인 판정이나 solver 변경 근거로 단독 사용하지 않는다.
- **REC #99:** `HOLD_MISSING_VALIDATED_HISTORY`, null boundary와 서로 다른 helium normalization을 확인했다. 현재 초기조건을 대체하지 않았다.

## 현재 실행과의 연결

SOURCE010은 기존 SOURCE009 ELF·source·물리를 유지하고 local target만 절반으로 줄인 두 구간이 실제 정상 종료했다. 새 native 결과는 각 26개 검사에 통과했다. LOCAL baseline과 NCP 결과의 비교는 환경 차이를 포함한 민감도 진단이다. 다음 후보는 끝점 직전 SIGNED_MINUS checkpoint에서 남은 24 accepted 단계만 관찰하여 실제 accepted-state R/J를 얻는 측정이다. 이는 별도 frozen contract와 실제 비교 결과 후에 실행한다.

정확한 source와 결손은 `SNAPSHOT.json`, `ARCHIVE_INTAKE.json`, `HE25_INTAKE.json`, `NEW_PR_INTAKE.json`에 기록했다. 전체 signed Bianchi 이력, isotope-native 반응망, 시간·각도·에너지 수렴 및 64-core scaling은 여전히 미완료다.
