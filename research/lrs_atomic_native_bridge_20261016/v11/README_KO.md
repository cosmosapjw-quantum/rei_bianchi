# REI-LRS V11: source-off CI/CE/free-free/CMB 시간배치 분리

독립 구현/증거는 `cosmosapjw-quantum/rei_bianchi` Draft PR #172의 고정 commit
`c91ba18a38b744a1e64ff40423f02a35f2999605` 위에 적층한 별도 연구다.
원래 native Grackle owner `6ea2b1b4b3875c9163cafc45efe720afded43fc4`는 수정하지 않았다.

- `R5_THEORY_KO.md`: 개별 반응 time-clock의 국소 절단오차와 에너지 owner.
- `src/ci_thermal_clock.py`: Grackle Case-A owner literal CI, RR/DR, CE, free-free,
  CMB microphysics의 별도 Python 번역과 8개 time-clock 갱신.
- `tests/test_ci_thermal_clock.py`: frozen owner identity, EOS/ledger/양수성 및
  실제 기본 검산 41개.
- `evidence/C8_MATRIX_144.json`/CSV: 샌드박스에서 실제 완료한
  3조건 × 8대조군 × 6시간분할 = 144개. 이들은 144개의 production native 이력이 아니다.
- `regenerate_case_views.py`: 같은 144 원시 행을 case별 파생 view로 분리한다.
- `merge_study.py`: 파생 view를 병합해 원래 144행을 바이트 단위로 재생한다.
- `V11_SOURCE_MANIFEST.json`: 원본 Grackle 코드 및 입력파일 14개 SHA-256.

## Fresh sandbox 검증

원본 V7 소스 아카이브를 복원하고 3개 Grackle source SHA, V7 reference Git blob,
41개 Python pytest, 144행 원시 evidence의 유일성/에너지 회계 및
split→merge deterministic byte identity를 다시 검증했다.

```bash
bash research/lrs_atomic_native_bridge_20261016/v11/REPLAY_V11.sh
```

실행에는 Python3.11+, NumPy, SciPy, pytest가 필요하다. 별도 GitHub clone에서는
기존 repo의 원본 `rust/rei_microphysics`가 그대로 존재한다.

## 결론 범위

관측된 N=128 온도오차: BE→CE-mid 97.0–97.5% 감소,
전 채널 midpoint는 비강성 경우 약 2차. 실제 native Rust V11 진단과
원래 source-on 다단계 2차 수렴 검증은 **NOT_RUN/HOLD**이다.
구체적인 해석·숫자는 `RESEARCH_V11_KO.md` 및 `evidence/C8_SUMMARY.json` 참조.
