# 다음 연구 스레드: REI-LRS V14 native projection 진단 이후

나는 독립 LRS photon–chemistry–thermal 시간적분 연구를 이어간다. Production v3/rux와 별개다. $physmath-research-loop를 사용해 실제 이론 유도와 샌드박스 경량 native 검증을 수행하고, 가능한 수정은 완성해 같은 GitHub branch에 push하라. NCP에는 컴파일·작은 호환 수정·실제 실행만 남긴다. 완료 단계마다 게시·백업·DAG를 기록하며 사용자에게 다운로드·수동 SSH/SCP를 요구하지 않는다.

## 첫 행동: 새로운 결과부터

Drive `REI_RESEARCH_BACKUPS/rei_bianchi/`, Dropbox `/bianchi/research_backups/rei_bianchi/`, repository `cosmosapjw-quantum/rei_bianchi`의 branch `research/rei-lrs-v14-physical-birth-20261018`과 [draft PR #198](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198)을 먼저 읽어라. 최신 HEAD·receipt·stdout·종료코드·원시 CSV·source SHA를 확인하고, 이 인계 뒤 새 결과가 있으면 우선한다.

`v14/RESEARCH_DELIVERY_KO.md`, `SOURCE_DELTA.json`, `stages/FINAL_DELIVERY.json`, `stages/PROJECTION_DIAGNOSTIC_20261019.json`, `projection_diagnostic_20261019/RESEARCH_CONTINUATION_KO.md`, `CODEX_NCP_EXECUTE_KO.md`를 읽어라. 후속 dual-backup receipt가 있으면 실제 object id와 readback SHA로 상태를 확인한다.

## 완료된 실제 결과

원래 V14 컴파일·표적 36 tests·smoke·84 full histories는 2026-10-18 NCP에서 완료됐다. Smoke는 28 histories/336 rows, full은 84 histories/7056 rows이며 모두 exit 0이다. 36 distinct tests를 양쪽에서 실행해 72회 PASS다. 이번 진입 때 HEAD는 `55d267d00e8dd9b04005af5d8551e948251c0777`이었다.

Frozen native source anchor는 `f6046418d15e2f44418dfbc04ca67999f389a7df`, V13 parent는 `7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e`다. `ef94f08df149b57959b868646b397a2bff2b268b`는 run 종료 뒤인 12:45:53 UTC에 생성된 실행 증거 게시 commit이며 runtime checkout attestation이 아니다.

원본 full archive는 2,713,000 bytes, SHA256 `049686b0dbe28f59ca0c8c3d7365e35fb2bef7f99799976f029501948899ad22`다. Drive `1BgKZPcl0bhtNKf_ylvA3-eD57IEwlPA1`, Dropbox `id:BSpOijBcT10AAAAAAD_MvA`의 전체파일 readback으로 확인했다. 기존 57 Python 시험과 76 제조 문제는 과거 결과이며 재실행·재집계하지 않는다.

실제 GL2 T p는 Xend=1e-5/1e-4에서 1.0591/0.94695였다. 원시 P/C/R/D와 signed CMB, EOS의 exact finite difference로 photoheat·종별 absorption이 leading T 차이를 운반함을 확인했다. 기존 source-off는 photon arrays가 비어 모든 photo 사건이 0인 gas-only controls다. X endpoint displacement와 gas/electron ledger residual도 finer source-off 차이에 영향을 준다. 작은 차이를 전부 ulp floor로 부르지 않는다.

## 새로 완료한 유도와 native 진단

고정 기체·기하, M=(N,Uq), AR(M)=M, Lf=−κf에서 현재 map은 Φ_h=A exp(hL)R이고, closed-moment ODE는 M′=F=ALR이다. Full minus two halves는

\[
\Phi_h-\Phi_{h/2}\circ\Phi_{h/2}
=\frac{h^2}{4}AL(I-R'A)LR+O(h^3).
\]

고정 node의 exponential family에서는 number coefficient=N⟨κ_perp²⟩≥0다. CSV는 halves-minus-full convention이라 부호가 반대다. 가정과 전체 유도를 보고서에서 읽어라. 일반 projection lemma의 새로운 novelty나 흡수계의 entropy theorem을 주장하지 않는다.

새 native example은 실제 MD14+Verner/physical c, 고정 gas/geometry, cells=8/16/32/64, broad와 delta60을 시험했다. 48 pair+14 frozen-history=62 고유 행, 13,312 cell 행이다. Sandbox Rust 1.94.1에서 compile 0/run 0, 첫 실행 0.094112117 s였다. Fresh sibling runner를 한 번 재현해 두 CSV 모두 동일한 bytes를 얻었다. 이는 새로운 우주론 이력이나 124개 고유 사례가 아니다.

Cells16의 local N/U defect slopes는 1.9426/1.9552다. Fixed-medium global self-difference slopes는 N/U=1.00924/1.00736, HeI=0.99318, heat=0.97984다. Delta pair의 상대 N/U 차이는 1.65e-16 이하다. 작은 N/U 보존 잔차와 1차 오차가 공존한다.

독립 agent가 이론·native 대응·CSV를 읽어 PASS_SCOPED로 검토했다. 또 다른 agent가 기존 CSV 채널 분해를 했다. 서로 다른 모델 계열이 합의했다고 꾸미지 않는다. Native full coupled T 오차에서 projection 기작의 기여율은 아직 미분리다.

실제 수정은 두 기존 summary의 species global max 0을 4.84017834763862e-14/H로 정정하고 원래 값·근거를 보존한 것이다. 새 analyzer의 NCP 상태 hardcode도 고쳤다. 기존 네 V14 native 파일·source·rates·EOS·default/adaptive/checkpoint는 그대로다.

## 다음 유한한 연구

완료된 compile/smoke/84 이력이나 76 toy/57 제조 CSV를 반복하지 않는다. 다음 수정 대상은 기존 closure R(M)를 유지하면서 F(M)=ALR(M)와 반응·열 사건을 시간 중심 stage에서 일관되게 적분하는 source-free photon–gas update다. Gas midpoint opacity만으로 old-moment spectral reconstruction의 2차항이 맞춰지지 않는다. Birth quadrature를 더 높이거나 closure/rates/광속을 바꾸는 것으로 이번 결함을 제거했다고 하지 않는다. 단순한 음수 Richardson 조합 역시 양수성·realizability 검토를 대신하지 않는다.

먼저 closed-moment time-centering의 opt-in 수식을 고정하고 구현하라. 현재 positive broad-spectrum frozen matrix와 delta 대조에서 원래 결함이 사라지는지 확인하고, 양의 기존 photon을 가진 evolving-gas source-free history, 그 뒤 source-on paired refinement로 진행한다. 이는 알고리즘 연구이지 NCP 호환 수정이 아니다. Full source-on 2차·uniform stiff·Case B·full EoR·signed Bianchi는 실제 새 증거 전까지 HOLD다.

이전 controller의 Desktop Commander probe는 월 사용량 SERVICE_ERROR였고 재시도 금지 응답이었다. 이전 환경 결과를 현 환경에 영구 일반화하지 말되 실패한 서비스를 맹목적으로 반복하지 않는다. 기존 승인 NCP 경로는 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`다. 현재 외부 실행이 불가능하면 실제 실행했다고 하지 말고 `CODEX_NCP_EXECUTE_KO.md`의 완성 runner 인계를 사용한다.
