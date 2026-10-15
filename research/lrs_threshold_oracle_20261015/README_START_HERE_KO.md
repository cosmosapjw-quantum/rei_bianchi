# rei_bianchi 독립 V4 연구 패키지: NCP 실행 인계

**연구 기준:** PR #153 source HEAD `e98d30efb5e725a79743d3a8ff61ee7e5169b498`에 기반한 독립 신규 PR용 payload. 원본 v3/rux/PR #150/PR #154 및 NCP 기존 프로세스 불변.

이 ZIP에는 원전 Verner-1996 H/He 단면적 원본 ASCII, PR #152/153 독립 기준 코드, 새 재결합·thermal 소스와 테스트, 15개 Radau convergence cases, 3개 shear의 이온/온도 이력 CSV 및 PNG, 그리고 NCP 실행기·한국어 연구보고서·Codex handoff가 모두 포함돼 있다. **실제 Cosmological EoR 결과가 아니다.**

주요 경로: `research/lrs_threshold_oracle_20261015/`.

우선 파일을 위 폴더로 연 다음:

```bash
sha256sum -c V4_INPUT_SHA256SUMS.txt
python3 -m pytest -q tests/test_lrs_threshold_oracle.py tests/test_verner_angular.py tests/test_dynamic_chemistry.py tests/test_recomb_thermal.py
python3 run_recomb_thermal_v4.py
# bounded NCP smoke only (the full 816-case campaign is not part of ChatGPT's execution)
NCP_SMOKE_ONLY=1 NCP_WORKERS=4 bash NCP_RUN_V4.sh
# NCP에서만, 기존 생산작업과 분리한 상태로:
NCP_WORKERS=12 bash NCP_RUN_V4.sh
```

NCP SSH 명령과 안전한 전송·중단·백업 지침은 `CODEX_NCP_HANDOFF_20261016.md`에 있다.

증거 상태: ChatGPT 컨테이너에서 98/98 pytest PASS, 독립 SciPy Radau 비교 및 FLRW 대칭성 확인, 12-case 단일/4-worker CSV byte identity 확인, Wolfram Language 에너지/온도 비율 항등식 잔차 0. **NCP에서 신규 816-case 실행은 NOT_RUN**이고, Ubuntu 원격 사용은 Desktop Commander 월간 사용량 한도 때문에 BLOCKED.
