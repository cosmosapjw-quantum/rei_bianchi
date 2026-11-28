# BASS_HE handoff, 2026-10-29

다음 스레드에 아래 블록을 복사해 실행해.

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
NEW_UNIT=HE_NAMED_NONTHERMAL_BIRTH_POOL_NEXT
AUTHORITATIVE_PREDECESSOR=research/he-pair-count15-20261029@ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce
ORIGINAL_15_ROW_SHA256=1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264
SOURCE_NEW_LOCAL=BASS_HE_NONTHERMAL_D_BIRTH_20261029_SOURCE_HANDOFF.zip
CURRENT_GITHUB_BRANCH=research/he-nonthermal-d-birth-20261029
GITHUB_POSTED_COMMIT=9044ef53762f1985eb0be1aaa4127cc11dfc094c
GITHUB_FULL_SOURCE_PUSH=BLOCKED_BY_TOOL_SAFETY; LOCAL_ZIP_IS_SOURCE
CENTRAL_PHYSICAL_DAG=28/88 unchanged
PAIR_COUNT15_LOCAL_DAG=14/18 unchanged
NEW_SCOPED_WORK_PRODUCTS=17/20; C8_PARTIAL, R6/C9_NOT_RUN

1. 원 repo/다른 BASS_HE 분기의 최신 실제 HEAD, draft PR103/102, 중앙 rei_bianchi의 실제 HE 상태를 다시 조회하라. 위 고정 SHA를 현재 HEAD로 추정하지 마라.
2. 새 ZIP의 EVIDENCE_MANIFEST.json, hashes, source/tests, prior saved input identity를 검증하고, 기존 frozen 15-row/source/numerical campaign은 재실행하지 마라.
3. 앞선 제한적 결과: He4(target rest)+gamma(330MeV)->D_fast+D_fast, K0=153.0767609 MeV, rest deficit=23.8464782 MeV, pair kinetic=306.1535218 MeV; 사건당 상관모멘트의 count law는 iid marks independent N 조건에만 유효. 28/28 standalone Python tests PASS; Wolfram 6 exact zeros; 31 synthetic rate balance plot, photon sign mutation FAIL as expected. Full suite & distinct R6/C9 NOT_RUN.
4. 물리 생성률 R_event와 입사 photon flux/history, 330MeV exclusive differential joint cross-section, target-motion frame, named physical D pool, fast-to-thermal stopping, heating & Cv는 모두 미제공. 이때 NULL을 0으로 바꾸거나 old Rice(150–250MeV) 값을 330MeV source로 사용하지 마라. 621 missing process cells NULL; H–Li entries are requests not admitted rates.
5. 추가 이번 유도: finite-mass daughter pressure trace는 하나의 m2만으로 결정되지 않는다. FULL m2=24377/71485에서 범용 trace [588.113334807457,588.113999573142] MeV/event, 폭 0.000664765685910278 MeV/event. 새 conditional_pressure_trace.py 와 test_conditional_pressure_trace.py 8/8 PASS. Jensen/secant 정확 항등식을 Wolfram으로 검산했고 pressure_trace_moment_gap.png 실물 플롯을 읽었다. 이 bounds는 모든 even angular laws에서는 sharp이나 기존 sextic angular family에서 sharp 입증 아님.
6. 먼저 physical provider의 energy/domain/units/normalization/uncertainty/identity를 고정하고 independent verification을 요청하라. 그 다음에만 kinetic gain f_D(p, t), energy-momentum exchange, thermalization의 독립 소유권으로 확장하라.
7. 원 중앙 DAG 28/88과 HE local 14/18을 올리지 말고 source-only 한정 주장과 필요 증거를 별도 node로 명시하라. production=false, L4=false, activation=false.
8. 실제 tool capability/runtime를 이번 실행에서 다시 조사하라. Native subagent 호출 가능하면 독립 model reviewer를 실제 dispatch하라. R6/C9를 same-model 재독으로 독립 검증했다고 주장하지 마라.
9. 각 변경단계의 Git commit/backup provider ACK/bytes/hash/readback 성공 여부를 따로 기록하라. GitHub full source upload failure는 실제 blocker이며 최초 theory checkpoint 게시만 성공했다. source ZIP을 GitHub 게시본과 혼동하지 마라.
10. 코드 권위는 source-only Python 모듈. 현 테스트: `python -m unittest discover -s tests -p 'test_*.py' -v`. 결과와 manifest/plot을 보존하고, 안정된 새 물리 source 입력이 확보되지 않으면 generic architecture refactor 대신 source validity research만 진행하라.
```
