# BASS_HE C1 연구 패키지

전자구조 solver 설계·최소 구현과 R=2 한 지점 검증이다. STOP=`ELECTRONIC_DISCRETIZATION_NOT_CONVERGED`. 독립 reference의 energy/coupling 기준이 미달했으므로 broad C2는 아직 실행하지 않았다. 다음은 C1b independent reference convergence다.

먼저 `BASS_HE_POST_R10R_THEORY_CLOSURE_REPORT_KO.md`, `C1_ELECTRONIC_DERIVATION_KO.md`, `RESULT.json`, `review/C1_INDEPENDENT_REVIEW.json`, `NEXT_HANDOFF_KO.md`를 읽는다. 코드는 `code/`, 실제 실행 증거와 실패 기록은 `evidence/`에 있다. 초기 실행 driver는 evidence에 보존했고 현재 driver는 I/O 보호만 고쳤다. `run_pilot.py`는 기존 outputs가 있으면 변경 없이 거부한다. 재현 시 새 출력 경로를 설정해야 하며 이 요청 자체가 재실행 승인은 아니다.

Private dependency에는 불변 A2 ZIP과 새 primary PDF 3개가 들어 있다. 원문 PDFs/ZIP은 public Git subset에 넣지 않는다. `PUBLIC_MANIFEST.json`은 public file identity, `MANIFEST.json`과 `MANIFEST.sha256`는 self-excluding 전체 payload identity다. 외부 archive identity/receipt는 archive의 SHA, publication commit, backup ACK·metadata를 기록한다. 실제 remote raw restore는 수행하지 않았다.

scientific_PROMOTE=HOLD; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.
