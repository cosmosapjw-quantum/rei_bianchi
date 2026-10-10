# REI-PHYS20 — 방향별 Bianchi-I 흡수·가열 응답

PHYS19가 지정한 다음 물리 연구 루프를 완료했다. 전체 유도는 `PHYS20_REPORT_KO.md`, 최종 machine-readable 결론은 `RESULTS_SUMMARY.json`, 다음 연구는 `NEXT_HANDOFF_KO.md`에 있다.

**독립 최종 판정: PROMOTE — PHYS21 이론 연구의 입력으로 사용하는 범위. Physical admission: HOLD.**

## 이번 연구에서 확인한 것

1. Physical birth source의 `J_b`, current-angle density의 `1/J_t`, fixed-q photon count 합의 역할을 구별했다. Causal opacity를 포함한 방향별 primary absorption/heating 응답을 유도했다.
2. Smooth isotropic continuum의 coupled scalar first variation은 명시한 조건 아래 0이다. C¹과 bounded C²의 결론을 구별했다.
3. Actual midpoint grid는 generic shear의 선형 평균을 보존하지 않는다. 현재 xy shear는 특별한 교환대칭으로 보호된다. 이 xy free-photon quadratic energy coefficient는 8×16 격자에서 연속값보다 0.971221923828125% 높다. 이 값은 실제 온도·광학깊이 오차가 아니다.
4. Threshold에 정확히 놓인 δ-line에는 |shear| cusp가 가능하다. 실제 13.7 eV FT03 source와 별도의 반례다.

Owner focused directional 81/81, threshold 2/2와 별도 reviewer Decimal70 검산 23/23이 통과했다. Fraction/Decimal80의 independent angular checks도 포함한다. `independent/DECISION_REVIEW.json`은 실제 별도 실행자의 판정이며 report SHA를 고정한다.

## 기준과 보존 상태

입력 commit: `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`. Scientific Rust src subtree: `cb69b4736dd046e4675557577eb8e0ead037d1f3`. `SOURCE_BINDING.json`과 `SOURCE_MANIFEST.json`은 실제 읽은 16 source files를 식별한다.

`[160,161] FAIL`, `tick160`, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED 유지. 새 native/gas IVP/이전 proof 실행 0회. 이 커밋은 새 docs 디렉터리만 추가하며 source/default/runtime_returns를 변경하지 않는다.

`PHYSICS_CONTRACT.json`은 intake 당시 bytes를 보존한다. 그 파일의 IN_PROGRESS는 intake 상태이고, 최종 완료 상태는 `RESULTS_SUMMARY.json` 및 `state/RESEARCH_STATE.md`를 따른다.

## 전체 재현 패키지

이 디렉터리는 텍스트 보고서·검산 code/evidence·decision·handoff를 담은 Git 문서 사본이다. 전체 재현 ZIP의 filename, SHA256, bytes와 실제 local restore 검증은 `ARCHIVE_IDENTITY.json`에서 확인한다. ZIP에는 여기에 중복하지 않은 pinned source snapshot, figures, 전체 payload manifest, `reproduce.py`도 포함되어 있다. 실행은 ZIP을 풀어 그 루트에서 한다.

```bash
python3 reproduce.py --verify-only
python3 reproduce.py --output-dir /absolute/path/to/NEW_OUTPUT_DIRECTORY
```

첫 명령은 bytes/source identity만 확인한다. 두 번째는 이번 PHYS20의 세 작은 진단만 실행하며 기존 evidence를 덮어쓰지 않는다. 처음 계산의 precision-initialization 수정과 reviewer의 환경 실패/대체 성공 기록도 보존했다.

## 다음 물리 질문

**PHYS21_SECOND_ORDER_SCALAR_SHEAR_RESPONSE**: smooth regime에서 방향 quadrupole, survival/source covariance, scalar gas feedback을 연결하여 2차 scalar forcing을 유도한다. 이번 frozen-neutral-fraction probe를 evolving gas의 계수로 승격하지 않는다. 구체적인 functional·작은 검산·제한을 산출하고 bounded loop를 닫는다.
