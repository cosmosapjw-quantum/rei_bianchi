# HE34-SCR: 오차 상한 기반 pressure 축약과 중성 H/He 수송

**workflow1.0.0 / approval0.2.** [PR88](https://github.com/cosmosapjw-quantum/BASS_HE/pull/88). HE32의 30/30 완료 결과와 HE33의 기초를 재사용한다. 병렬 Lorentz PR87과 구분되는 연구 단원이다.

**현재 단원 20/20 완료.** 최종 science pin은 `24b134545822cff6c2bf2ee9623d330e7efd1176`이다. 전체 79개 payload의 archive 내부 SHA256와 실제 원격 Git blob이 모두 일치하고, 최종 archive 저장 acknowledgement를 확인했다. [저장·게시 영수증](delivery/S2_ACK.json)과 [원격 readback](delivery/S2_REMOTE_READBACK.json)을 보존한다. 후속 B1–B5는 이 완료 수에 포함하지 않는다.

## 실제 결과

- 저장된 HE32 한 배경의 201 nodes에서 prescribed-chi mechanics를 계산했다. 고정 1e-6 r/log-pressure 기준으로 chi=10,100은 거절하고 1000,10000은 수용했다. chi=1000의 r 오차는 6.84089e-7, 연속계 상한은 6.86890e-7이다. 별도 구적 gate도 통과했다.
- 중성 H1/He4 first-Sonine 점성의 정확한 유리식과 직접 2×2 풀이의 최대 상대차는 6.4653e-16이다. 별도 진단량 chi_match=p_neutral/(eta H)는 1.6671e4에서 1.5527e-3으로 변한다.
- 제한된 host/baseline 측정에서 기계 계산은 73.505 ms, segmented Radau는 785.762 ms였다. 중성 vector 유리식은 0.244831 ms, batched matrix는 0.315845 ms였다. Raw timing의 편차를 보존하며 보편적이거나 최적화된 가속비를 주장하지 않는다.
- 독립 physics → math/code → output → 실제 PNG 심사는 `pass_within_stated_scope`, 미해결 blocker는 0이다. 새 그림 두 PNG+SVG 쌍을 저장했다. 과학 재실행 없이 현재 19개 파일의 receipt/hash를 확인했다.

## 문서와 재개

[RESULTS_KO.md](RESULTS_KO.md)는 유도·수치·성능·한계·실행 횟수의 완전한 보고서다. [CONTRACT.json](CONTRACT.json)은 실행 전에 고정한 계약이며 현재 진척은 [DAG.json](DAG.json)과 [RUN_RECORD.json](RUN_RECORD.json)이 담당한다. [식–코드 대응](theory/EQUATION_CODE_MAP.md), [물리 범위와 의존성](theory/SCOPE_AND_DEPENDENCIES_KO.md), [NEXT_DAG.json](NEXT_DAG.json)을 함께 읽는다.

```bash
python research/he34_sandbox_certified_relaxation_20261022/verify_saved.py
```

기본 재개는 해시/receipt 검사다. 완료된 IVP, benchmark, render를 반복하지 않는다. [CODEX_HANDOFF.md](CODEX_HANDOFF.md)와 [NEXT_THREAD_HANDOFF.md](NEXT_THREAD_HANDOFF.md)에 두 종류 인계를 제공한다. 최종 science pin/archive/provider ID는 delivery/S2_ACK.json, 앞의 checkpoint는 delivery/S0_ACK.json과 S1_ACK.json에 기록한다.

## 현재 물리 범위

기계계는 상수 chi, Q=j=0이다. S의 정의된 선형 보간에 대해 연속계 축약 상한을 증명했다. Outward-rounded machine proof를 제공하는 것은 아니다. 중성 진단은 공통 T=20000 K와 HE32의 A*m_u 관례를 쓴다. p/eta는 저주파 점성 일치율이며 transient eigenvalue, PR87의 순간 Grad율, chemical number-rate와 구별한다.

HE32는 8핵종 21상태의 prescribed-UV photo+caseA RR pilot이다. 기존 matter stress는 nonbaryonic이고 gas pi_b=0이다. Fully reactive19채널, 모든 불안정종·음이온·분자, 열·광원 진화, 실제 바리온 stress feedback의 완료로 범위를 확대하지 않는다. B1 수송 보정 + B2 열·반응 adapter → B3 closure → B4 새 coupled gas → B5 metric feedback은 별도 미완료 DAG다.

기존 HE32 IVP/render/benchmark 재실행은 0/0/0이고, 새 coupled cosmological IVP는 0이다. 저장 배경의 새 mechanical reference는 11 histories/2200 short interval solves다. 별도 synthetic/reviewer 검산은 각 receipt에 분리했다.

최종 science payload의 독립 검토·게시·백업·두 인계를 완료했다. 단계별 근거와 checkpoint, 다음 DAG는 DAG/delivery 기록을 따른다.
