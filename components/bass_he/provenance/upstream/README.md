> **2026-11-01 research routing update:** [Adversarial REI IGM process audit](docs/strategy_igm_20261101/AUDIT_KO.md) · [Science-first DAG overlay](docs/strategy_igm_20261101/DAG_OVERLAY.json) · [Prospective development policy](docs/strategy_igm_20261101/DEVELOPMENT_POLICY_KO.md). Historical DR/ARSENY research and source-scoped HE-DD results below remain preserved; neither is the current canonical REI EoR scientific milestone.

# BASS_HE — audited He–H collision research kernels

**독립 논문 기반 재구현이며 저자 ARSENY 코드가 아니다.** 물리 production release가 아닌 audit-led research release `0.2.0`이다.

기존 DR7의 에너지 일치 조건이 일반 eigenroot를 branch point로 잘못 인증할 수 있다는 반례를 발견했다. 새 `bass_he` API는 spectral rank/fold와 monodromy 검사를 분리한다. 회전 ODE는 정확한 gauge 변환과 parity-block batched Magnus4로 가속했다. `arseny_reimpl`은 기존 구현/비교용으로만 보존하며 그 legacy branch certificate를 다시 사용하지 않는다.

핵심 문서:
- [수학·물리·코딩 감사 및 연구 보고서](docs/RESEARCH_REPORT_KO.md)
- [단계별 연구 계획](docs/RESEARCH_PLAN.md)
- [증거 기반 연구 실행 계약](docs/RESEARCH_HARNESS.md)
- [발견사항 및 claim gate](evidence/FINDINGS.json)
- [실행 결과 요약](evidence/RESULT_SUMMARY.json)
- [공통 Case A 사건과 implicit primary의 이론 연결 — HERE_RUX03_PRIMARY_THEORY_03](research/rux03_primary_theory_20261012/dossier/README_KO.md)

## 설치

Linux/POSIX 또는 WSL2, Python>=3.11, NumPy 2.3.5. 원문 PDF, 저자코드 archive, API key, Codex, Wolfram은 실행 의존성이 아니다. 네트워크는 최초 의존성 설치와 Git publication에만 필요하다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

현재 workspace에서 패키징된 새 tests와 작은 pilot는 이미 실행했다. 사용자가 같은 smoke를 다시 수행해야 다음 개발이 열리는 구조가 아니다.

## 새 bounded pilot

```bash
.venv/bin/python scripts/run_research.py \
  --stage pilot --workers 2 --out runs/pilot \
  --cache-dir runs/shared_cache
```

두 rho에서 다섯 numerically certified branch, geometry reuse, E=0.5/5 keV/u, exponent=1/2를 계산한다. 이후 같은 입력의 재개는 `--resume`을 추가한다. 완료 cache는 payload hash와 source/environment identity가 맞을 때만 재사용한다. 파일을 수정한 뒤 이전 run을 덮어쓰지 말고 새 `--out`을 사용한다.

```bash
.venv/bin/python scripts/run_research.py \
  --stage pilot --workers 2 --out runs/pilot \
  --cache-dir runs/shared_cache --resume
```

## 작은 Eq. (54) 연구 계산

```bash
.venv/bin/python scripts/run_research.py \
  --stage quadrature --order 2 --panels 32 --workers 2 \
  --out runs/quad_q2 --cache-dir runs/shared_cache
```

이 명령은 physical capture/ionization 합이 아니라 indexed-state off-diagonal area를 출력한다. 기존 order1/2 비교의 vector 오차가 최대25.9%여서 **수렴 판정은 OPEN**이다. 해상도를 크게 늘리는 것으로 모형의 coherence/trajectory/upper-shell/exponent ambiguities가 해결되지는 않는다.


## AUDIT2 adaptive Eq. (54)

`audit2/adaptive-eq54` adds support-split, component-wise adaptive Eq. (54) research integration in `u=rho^2`, explicit exponent-factor lanes, and an exact-held-out-validated local-cubic `Delta(u)` surrogate. The current numerical result reaches a 0.2% component-wise target with independent GK3/7 and GK7/15 agreement, but **does not promote the result to a physical production cross section**. At 0.5 keV/u the ±10% rotational matching-radius sensitivity reaches about 6–7% in the factor-2 lane, and the Eq. (52)/Eq. (55) exponent normalization remains unresolved.

Use `scripts/run_research.py --stage adaptive`; `--geometry-mode exact` is the direct lane and `--geometry-mode surrogate` requires exact runtime held-out validation before integration.

## 파일과 실패 보존

`RUN_BINDING.json`은 source/Python/NumPy/수치 설정을 고정한다. `EP_CERTIFICATES.json`, `GEOMETRY_RESULTS.json`, `INITIAL_COLUMN_OUTPUTS.json`, `SUMMARY.json`은 각 단계에서 atomic write된다. 실패는 traceback과 함께 남고 임의 0으로 대체하지 않는다. 동시에 같은 run을 열면 lock으로 거부한다. `.RUN.lock`이나 cache의 `.lock` 파일을 지워 우회하지 않는다. 중단 후 재개 단위는 완료된 branch/geometry이며 Newton 내부 stack의 byte-level 복원은 아니다.

## 범위 제한

- `F=0, det(F_z)=0`+monodromy는 numerical certificate이며 엄밀 interval existence proof나 전역 enumeration이 아니다.
- straight-line/static-Coulomb/small-R model과 inherited approximate rotational matching radius가 유지된다.
- Eq. (52)와 (55)의 exponent는 두 policy lane이며 resolution을 주장하지 않는다.
- stochastic probability transport는 coherent amplitude propagation이 아니다.
- diagonal survival area는 elastic cross section이 아니다.
- upper Nmax surrogate를 bound capture와 physical ionization에 중복 합산하지 않는다.
- 첨부 원문 PDF는 공개 저장소에 재배포하지 않는다.
- 배포 라이선스는 프로젝트 소유자가 별도로 정하며, 저자 program의 라이선스를 자동 상속한다고 표시하지 않는다.

원본 데이터 identity와 실행 증거는 `evidence/`, 보존된 기존 값과 convention 문서는 `legacy/`에 있다. GitHub publication의 실제 상태는 별도 publication receipt를 확인한다. 로컬 commit을 remote push 완료로 부르지 않는다.
