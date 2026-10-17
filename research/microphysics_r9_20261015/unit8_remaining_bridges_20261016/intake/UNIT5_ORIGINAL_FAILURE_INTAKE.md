# Unit5 원본 종료와 한정 수정

원본 NCP 실행은 `2026-10-16T04:21:24Z`에 exit 1로 끝났다. 직접 잔차 그리드 평가 이후 `getattr(np, "trapezoid", np.trapz)`의 기본 인자가 먼저 평가되며, NCP NumPy 2.5.4에 `np.trapz`가 없어 발생한 후처리 호환성 오류다. 원본 영수증·traceback은 [Drive 실패 archive](https://drive.google.com/file/d/11GDYLRFxGcqR3EJHev2YGN_ut1hiPNTp/view)와 Dropbox `id:BSpOijBcT10AAAAAAD-akg`에 보존했다. SHA256은 `252501cc58c6b8434c29199e2697e73bc106ba36664e94b315530ff110c1b5b1`이다.

원본 supervisor 실행시간은 5549.584초, peak RSS는 2,774,752 KiB이며 새 H 작용은 정확히 70회다. 저장 checkpoint·128차 내부 gate PASS·refinement HOLD는 유효하다. 아직 완성 잔차 파일은 없다.

독립 검토가 승인한 한정 수정은 `np.trapezoid`를 먼저 찾고 없을 때 `np.trapz`를 참조하는 지연 fallback 두 줄이다. NCP 환경의 0이 아닌 작은 fixture에서 경계값과 사다리꼴 적분 회귀검증을 통과했다. 저장 checkpoint의 동일 직접 진단을 새 H 작용 0회로 원래 04:48:54 UTC 기한 안에서 감독 실행 중이다.
