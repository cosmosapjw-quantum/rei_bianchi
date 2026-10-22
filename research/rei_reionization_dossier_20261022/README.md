# 재이온화 dossier와 핵종·이온 진화 도표

원본 7장짜리 재이온화 dossier, 시리즈 발췌본, 첨부된 핵반응 dossier를 함께 읽고 실제 계산 그림을 추가했다. 원본 PDF와 비공개 입력은 공개 묶음에 포함하지 않는다.

주 문서는 REIONIZATION_DOSSIER_20261022.md와 같은 이름의 PDF다. GALLERY.html은 초기 Sigma, Pi_r, Pi_m를 각각 독립적으로 바꾼 비교와 응력 상쇄·전단 방향 반전의 28개 그림을 제공한다. strong_pi_m/GALLERY.html은 추가로 요청한 큰 물질 응력 실험의 7개 그림을 제공한다. 최종 INDEX.html과 PDF는 두 집합 및 이전 13개 원자·5개 핵반응 그림을 함께 안내한다.

핵종은 n, H1, D, T, He3, He4, Li6, Li7이며 총21개 전하 출력 항목을 추적한다. 새 T의 중성/이온 분할은 아직 풀리지 않았다. 그림은 이를 미해결로 명시하고 조건부 핵반응에서 계산한 T 총량만 보여 준다. 기존 T=0은 생성항이 없는 구현 구조의 결과였으며, 새 조건부 반응망에서 생성량은 양수다.

기본 비교에서는 초기 물리적 Sigma/Pi를 진단값으로 확인하고, 나머지 두 초기축과 같은 z에서의 기체 온도·바리온 밀도·UV 처방을 고정한다. 시간은 각 케이스의 z=20 이후 고유 경과시간이다. 진화 중 응력과 팽창률까지 고정하지 않는다.

기존 차가운 물질 모형에서는 Pi_m,0의 양의 허용 한계가 약0.001367이다. 더 큰 Pi_m 실험은 별도의 준상대론적 비바리온 물질 모형 내부에서 초기 에너지 밀도, 평균 압력, 입자수, H, 다른 초기축을 고정하고 Pi_m,0=0,0.01,0.05,0.1을 비교한다. 두 물질 모형 사이의 차이를 Pi_m 하나의 효과로 혼동하지 않는다.

## 재사용과 실행

기존83개 IVP와82개 핵반응 후처리 결과는 재사용한다. 기본 도표에는 빠져 있던 Am=0.8 케이스 하나만 추가했다. 큰 Pi_m 실험은 별도 계약에 따른4개 명목 케이스와1개 엄격한 대조 케이스를 허용한다. 실제 실행 횟수와 비용은 receipt를 따른다. 기존 검산, NCP 실행, 만료 예산은 재시작하지 않는다.

코드와 의존성은 최종 복원 ZIP에 포함한다. 결과가 이미 있으면 producer의 출력 보호를 제거하지 말고 재사용한다. 그림 재생성은 저장된 결과를 읽는 작업이다. 실행 명령은 각 render 코드 및 CODEX_HANDOFF_PROMPT.md를 따른다.

## 주요 기록

| 파일 | 역할 |
|---|---|
| ATTACHED_DOSSIER_RECONCILIATION.json | 첨부 세 PDF의 식별과 실제 이론 범위 |
| PHYSICS_PLOT_CONTRACT.json | 기본28개 그림의 조건 |
| STRONG_PI_M_CONTRACT.json | 큰 Pi_m의 허용 분포와 실행 한도 |
| CASE_TABLE.csv | 기본19개 선택 케이스의 실제 초기축 |
| GROUP_METRICS.json | 기본 비교의 측정 차이 |
| NEW_CASE_RUN_RECEIPT.json | 중간 Am 케이스의 계산 기록 |
| review/ | 독립 판단 |
| LOOP_PROGRESS.json, NEXT_DAG.json | 완료·대기·의존성 |
| delivery/ | 실제 게시 commit, ZIP, 이중 백업 검증 |

PASS_SCOPED는 명시된 범위의 수락이다. 그림 생성, 백업 성공, 조건부 반응망 통과를 FLRW production이나 최종 Bianchi I 과학 승인으로 승격하지 않는다.

최신 사용자 승인에 따라 최종 소스·개별 그림·공개 NPZ의 Git 게시와 이중 백업을 완료했다. Payload commit은 `c004c22ef938fdfbc7a135fcd4a31c2df0f25f12`이며 실제 branch head readback이 일치했다. 현재 상태는 [FINAL_DELIVERY_ACK.json](delivery/FINAL_DELIVERY_ACK.json)을 따른다.

- [최종 81쪽 PDF](https://drive.google.com/file/d/1hxw8OgXcRxkvBvcsio1PQwoFvBgZFJx-/view?usp=drivesdk): 17,997,787 bytes, 원본 SHA256 `a3a642c3971a545eac4f119b1b38cc4e4fe610edac5537a46d8ef7442c4a914e`; Drive 전체 다운로드 일치.
- [소스 포함 복원 ZIP](https://drive.google.com/file/d/1pq7KtPNKxVoZ_NyqKXG_SVAxDoOweIMI/view?usp=drivesdk): 76,130,340 bytes, 567 members, SHA256 `a6e50ee0aa86c55f46728e55df72bbb84a156317ca951f54ddf5af1ed413f758`. Dropbox와 Drive 전체 다운로드의 SHA256 및 ZIP CRC가 일치했다.

최종 PDF는 Git connector의 16 MiB request 제한 때문에 Git에는 넣지 않았다. 재압축·재빌드 없이 원본을 위 Drive 링크와 검증된 ZIP에 보존했다. 개별 PNG/PDF 그림과 코드·문서는 Git에서 제공한다. 복원 ZIP 내부의 DEFERRED 표기와 DELIVERY_LOCAL_RECEIPT는 포장 당시의 역사적 snapshot이며, 현재 ACK가 delivery 상태만 대체한다. ZIP과 과거 receipt는 변경하지 않았다.

C10은 COMPLETE, 다음 `COUPLED_ISOTOPE_NATIVE_CONTRACT`는 READY다. production은 HOLD_DEPENDENCIES를 유지한다. 이번 전달 재개에서 과학 계산·기존 테스트 재실행은 0회다.
