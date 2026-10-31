# REI F4 | BASS193 × CCC6 첫 비탄성 충돌 (2026-10-31)

본 패키지는 PR #311 (`63052797e382b438ef375e8389f539118a7e2a0c`)의 공개 CCC 6채널 부분 전자충돌 단면적 표본, 원래 BASS193 frozen chemistry 및 PR #309의 전체 21종 자유전자 Coulomb 감속 자료를 동일 snapshot에서 계산한다. 원래 Li II 2E1 singlet 조건부 광자 도달원에 한정된다.

- `code/run.py 2100`: 193 상태 × 7입사에너지, 192 arrival, 3,840 전자 source band에서 selected first event; 통계적 첫-event 확률과 원본 수/에너지 first moment 경계.
- `code/plot_science.py`: 실제 새 물리 출력으로 과학 PNG/SVG 5쌍.
- `tests/test_science.py`: 32개 표적 테스트. `evidence/independent_first_event_audit.py`는 저장된 7epoch에서 적분을 독립적으로 계산한다.
- `VERIFY.sh`: 원본 SHA/전체 manifest/테스트/재생을 독립 추출본에서 실행한다.

실행: `bash VERIFY.sh`. Python 3 + NumPy, SciPy, Pandas, Matplotlib 필요. IVP 없음. 기존 소스·프로덕션/기하 상태 불변. 원저자 완전 CCC 데이터셋과 EXHALE Git 표본의 byte equality는 검증되지 않았으며, EXHALE 저차원 0.5%-peak interpolation 표본을 그대로 사용한다.

전제·범위: 여섯 채널은 완전 원자 충돌 연산자가 아니며, He II 타깃, 추가 여기·탄성 채널, 첫 충돌 이후 cascade와 실제 heating/온도 진화는 계산되지 않았다. `E_e<13.7 eV`에서의 물리적 충돌 수가 0이라는 주장이 아니라 이 모형의 계산 범위가 제외되었다는 뜻이다.

원본 193개 상태와 검증된 선행 소스에 대한 SHA는 `evidence/SOURCE_LOCK.json`. 20개 R/C 기록은 하나의 단일 bounded 연구 단위에 대한 회고적 stage checkpoint이지 독립적인 20회 과학 실험이 아니다. Canonical DAG 33/88 working, 28/88 central, 4/7 Physical Fast, delta0; F4 PARTIAL, production HOLD, NO_MORE_IVPS, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.
