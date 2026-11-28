# HE-ANG-FINITEMASS-CBA 인수인계 — 실제 S, C8 OPEN

## 1. 현재 판정과 전달 위치

실제 과학 S는 `9fc8185437f145a6ba4569e1b38aa2e12d15acd9`, tree는 `ebecbe9617730e366d258a38c64ca14f846d5102`다. [Draft PR101](https://github.com/cosmosapjw-quantum/BASS_HE/pull/101)은 unmerged이며 activation=false다. S의 선택된84파일은 Git blob·크기·mode·type readback에서 mismatch0으로 확인됐다. 실제 근거는 `delivery/S_PUBLICATION_RECEIPT.json`이다.

**불변 과학 S는17/20이고, 현재 D 전달 스냅샷은 실제 S/C/B2 receipt를 근거로19/20 준비 완료다. C8은 PARTIAL_EXPORT로 OPEN이다.** R10/C10은 이 실제 전달 근거로 COMPLETE_AT_D_DELIVERY_SNAPSHOT이며 D commit 게시 자체와 그 own SHA는 아래 external actual receipt에서 확정한다. D own SHA, 후속 E/B3 및 final PR tail을 미리 채우지 않는다. 20/20 또는 전체 HE-ANG 물리 목표 완료를 주장하지 않는다.

Root 판정은 `ADMIT_SCOPED_THEORY_NUMERICS_AND_EXISTING_PNG_PUBLISH_WITH_C8_OPEN`이다. 독립 C9는 `PASS_SCOPED_NUMERICAL_WITH_FAILED_PROCESSES_AND_PARTIAL_EXPORT`다. 이론·고정 유한 fixture·실제 PNG를 scoped 채택했으며 두 실제 프로세스 FAIL과 미완료 export를 보존했다. 권위 있는 근거는 `reviews/ROOT_ADMISSION.json`, `reviews/C9_REPORT.json`, `RESULTS_KO.md`, `CLAIM_GATE.json`이다.

## 2. 이번에 확보한 모형

PR99의 finite-M Jacobi shell과 PR100의 matched Coulomb overlap을 같은 Hamiltonian·정규화·측도에 연결했다. M>0, mu=M/(M+1), nu=(M+1)/(M+2), a=mu, b=1/(M+1), lambda=mu, B=mu/2다. Incoming target은 lab 정지이고 beam은+z다. 최종 projectile은 R의 plane wave, (B,N) pair는 attractive Coulomb continuum이며 V를 한 번 적용한 labelled direct C1 Born channel이다. Direct spin factor는1이고 exchange amplitude는 포함하지 않는다.

유한질량 전이에는 `exp(i*a*Delta.r)-exp(-i*b*Delta.r)`의 두 위상이 모두 필요하다. 구현은 unchanged parent의 stable overlap 두 개, `L_mu(a*Delta,k)-L_mu(-b*Delta,k)`와 Nc를 사용한다. 두 번째 항을 상수1 또는0으로 대체하지 않는다. 무한질량 limit에서만 parent100의 orthogonality와 fixed-centre 결과로 연결된다.

정규화된 F_M에 대해 `W=4/|P|*|F_M|^2/Delta^4`, Jacobi density는 `mu*nu*q*k*W`다. Lab detector density는 parent shell의 모든 양의 단순 root에 모형 W를 각각 적용한다. Caustic unresolved, continuum endpoint, lab A-zero endpoint를 유한 density0으로 바꾸지 않는다. 단위와 유도는 `THEORY_KO.md`의 식(1)–(14)를 따른다. Er은 상대 pair 에너지이며 lab EB가 아니다.

저장된 근거는17계약시험,12generic,3사례×2항 원 K 적분,12tiny,4kinematics/normalization, Gauss24/48/96의 두-root weighted fold,73-angle illustration,8-mass trend다. Generic 최대 scaled error는4.463835015138282e-16, 원적분 최대는1.3537164052030534e-50, tiny 최대 true relative error는1.7957084932658487e-15다. Fine fold chart/refinement는 각각1.974610792893064e-15/6.160785673826359e-14다. 이는 고정 유한 fixture 관측이며 uniform/outward bound, 실험 보정 또는 calibrated physical uncertainty가 아니다.

## 3. 실제 실행, 실패, 남은 export

| 실제 시도 | 상태 / exit | CPU s | wall s |
|---|---|---:|---:|
| 01_01_tests | PASS / 0 | 0.301362 | 0.31895837299816776 |
| 02_02_analysis | FAIL / -9 | 6.1359639999999995 | 6.184616320999339 |
| 03_REPAIR01_COMBINED | FAIL / -9 | 5.4455029999999995 | 5.482404227004736 |

새 과학 합계는 **11.882829CPU / 11.985978921002243wall**, 원래 상한은12CPU/35wall이다. Parent100의4.987974CPU/5.122489414992742wall을 포함한 lineage는 **16.870803CPU / 17.108468335994985wall**, 상한은20/60이다. 두 child의 개별 CPU overshoot는 삭제하지 않는다. 정확한 kill source는 NOT_OBSERVABLE이며 cumulative cap overshoot는 false다. 새 repair reserve는1사용/0잔여, parent reserve는 미사용 상태 그대로이며 이전하지 않았다.

실패 partial의12generic+첫2quadrature/4항과17시험은 재실행하지 않았다. Original failed partial은42613bytes/SHA256 `e493132d5a1bb56112d5fb87890828949b3a0cbacbcffab634c5df67ff1da830`이고 보존된 prefix의 값·직렬화 bytes equality는 true다. 최종 `results/ANALYSIS.json`은136204bytes/SHA256 `e62cb595be64728b30f08ccfe5c2a0eb68d941fbb325d8e81aa93251e0e586df`다.

실제 PNG는190699bytes/SHA256 `d0d75f7e5422ced1b873f3e1c36e6704724357a2511a0d742e3a8b4f15f0c781`이며 root와 독립 reviewer가 실제 이미지를 검토했다. **`FINITE_M_CBA.svg`, producer의 `FIGURE_METADATA.json`, 원 repair의 `REPAIR01_SUMMARY.json`은 없다.** C9-EXPORT-01/C8은 OPEN이다. 실패한 원 프로세스의 summary를 사후 PASS 문서로 만들어 넣지 않는다. 향후 별도 승인으로 export 의무를 다룬다면 additive actual receipt를 남겨야 한다. 현재 추가 실행·plot/export 재시도·새 연구 단위는 승인되지 않았다.

## 4. 원전·재사용·기존 결과의 경계

Kadyrov et al., Ann.Phys.324(2009)1516–1546, DOI10.1016/j.aop.2009.02.003의§3.1 pp1527–28/Eqs72–84를 실제 읽었으며 PDF는448174bytes/SHA256 `c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165`다. Attaourti–Taj–Manaut의 physics/0411013v2 PDF는326595bytes/SHA256 `b14f054de037722bb21ab8911b0b3917f0978b18dab9c916427d02115ccceda1`다. Source의 exact scattering theory가 이번 C1 closure를 물리적으로 승인한다는 뜻은 아니다. Parent100의 Eq16/18 inverse-radius 차이, Eq28의 다른 J, appendix 부호 및 reference16=Massey–Mohr1933 기록을 유지한다. 원 PDF·fulltext·source page PNG는 공개 전달에 넣지 않는다.

| 재사용 계보 | 실제 source identity | 유지할 범위 |
|---|---|---|
| PR99 finite-M shell S / D | `8d481ed47f57774f48bcfb412671ff927601316e` / `bec636ffa3014035292c1078a758c7aa1827174d` | Canonical mapping, shell, 모든 양의 root 및 caustic guard |
| PR100 direct CBA S / D | `a891cd4b9a3548e66db669b9eb472fea88a3b78b` / `8e0fb28fea520364d8794bac32840621dd150f95` | Matched overlap·Nc,4.987974/5.122489414992742 비용과 모든 실패/unknown |
| PR100 central C / E | `7caca70d94d03732bff5e7adf2f9aa5cf59310ec` / `14976bda37b17e8dd8060f4c89adf6ddf9fbcc6a` | 당시 snapshot과 실제 external tail을 구별 |
| 현재 finite-M CBA S | `9fc8185437f145a6ba4569e1b38aa2e12d15acd9` | 현재17/20, scoped numerical/PNG 채택, C8 OPEN |

HE-X1의32fixture·necessary PSD/moment-cone gate, HE-ANG-CONTRACT, HE38의 기존 finite-mass/model-numerics 근거 및 Hex intake를 재사용한다. 완료된 old suite, HE38129T, 새 IVP, Hex/CCC solve를 이번 전달 문서 작성 때문에 다시 실행하지 않는다. X1의 경험적 angular correction 또는 HE38 raw numerical gate를 물리 uncertainty로 승격하지 않는다.

**DDCS20 고정 결과를 그대로 유지한다.** Childers et al. PRA69,022709(2004) TableIV의 E0=20eV에서40개 전사값을 보존하고 E=3–6eV/theta15–120degree의32개 primary값만 사용한 결과다. `N_W=1.918935932462322e-21 m²`, `mean(mu)=0.5215950231699314`, `mean(P2)=0.1799846901344856`, `mean(E)=4.581073268756349 eV`, `mean(sqrt(E)mu)=1.111325457435915`다. 축대칭 linear-mu 보간과 선택한 deterministic sensitivity box의 조건부 결과이며 box는 confidence interval이 아니다. 각 scalar의 별도 box witness를 공동 극값으로 합치지 않는다. Source error·미지 covariance·보간·미관측 support 의무는 그대로다. 근거 pin은 PR94 S `d8bae9f7e24ad3494e399f7ab46c4167a5623d48`이다. 미래 부분 mu_window의 theta metadata 의무 C9-NB-01은 OPEN이고 이 fixed full-window 결과는 변경하지 않는다.

전체 HE-ANG은 **SOURCE_INPUT_PENDING**이다. 첫 물리 입력 의무는 **HE-ANG-SOURCE-PAYLOAD**, 즉 source-consistent joint outgoing-electron law 또는 amplitude/event payload와 count/spin/exchange/full support/frame/recoil/validity/uncertainty 계약이다. 이번 labelled direct 모형의 확보가 그 물리 입력을 대체하지 않는다. physical_provider_admitted/event_sigma/physical_recoil_distribution/HE-X1 empirical correction은 false, global completion은null이다. C23E와 다른 owner의 모든 OPEN·예산·실패·unknown을 보존한다.

Post-S/pre-C 실제 중앙 변경은 `evidence/survey/POST_S_CENTRAL_CHANGE.json`에 있다. 준비 중이던 중앙 base `ecbb3124b49e75d8a7e948705b3894307d628349` 뒤에 실제 `8e946b46aa44581f09141184f193223277f2ec88`가 관측됐고, 그 새 base 위의 C `46a102b22b54cc03a91ad92bbd58d68dd82b7964`가 실제 게시·readback되었다. WU PHYS90의 최신 관측은 FINAL `9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc`, S2 `60d062104438b3f99553a74d210e9c2b48ed2dd3`의 scoped conditional covariance-cell/consumer-envelope다.11628pairs의 threshold는 `0.5006839145935373 < t_pair <= 0.5006839145944469`이며 full153PSD는 UNRESOLVED, parent는 PARTIAL_INPUT_DEPENDENCIES, actual consumer ACK는null, physical CI는false다. 이전 survey의 S0/10-of-20 관측은 역사적 기록으로 유지하고 최신 owner 상태를 그 옛 상태로 덮어쓰지 않는다. 이 HE 전달은 새 중앙 base에 own3paths만 반영하며 WU handoff/return과 모든 다른 owner·계약·의무를 보존한다. 해당 owner의 전체 branch body나 새 backup restore를 이 worker가 수행했다고 주장하지 않는다.

## 5. 실제 백업과 아직 없는 전달 identity

Post-C 최신 중앙 관측은 `53b2c135a1203a8784b6cc4acdec1d4fe174f166`이며 actual C46a102b2… 뒤에 CR PR105의 H1 ground spontaneous RR finite-chain scoped child가 추가됐다. 근거는 `evidence/survey/POST_C_CENTRAL_CHANGE.json`이다. 읽은 actual return의 science S는 `bdfd34499153575305871bd68a139e2878f5f49f`, named consumer는 `N5_C23D_H1_RR_MILNE_V1`이다. Immutable PR104의8finite electron-energy chains, native13.6eV Verner PI/Milne, stationary zero-recoil heavy target 및 prescribed10000K common baths에 조건부인 결과다. Full N4/N5는 PARTIAL/OPEN, N6/N7은 predecessor-gated, final canonical backup은 ROOT_PENDING이다. 이 owner 상태와 현재 WU90/REI/다른 owner 변경을 fresh E에서 보존한다. HE의 physical joint payload 의무를 닫지 않으며, actual C의 identity는46a102b2… 그대로다. D를 위해 E 완료를 기다리거나 새 과학 계산을 실행하지 않는다.

| 항목 | 현재 실제 identity / 상태 |
|---|---|
| B1 RECOVERY2 | 746657bytes,67members,SHA256 `a15dd819bc164572af0f2c591b7cd3ccfc070e2447be1a0d24db9de6e72c6ef9`; Drive `1jcHpeQW_B0bpLYOV7-nEiujjPoV2d4qI`; Dropbox `id:BSpOijBcT10AAAAAAD_9vw`; 실제 dual upload+별도 metadata ACK |
| B1R REPAIR01 | 776704bytes,80members,SHA256 `79dbf442a088a62797d841e33f34bbdb6118e99eb79497b3964821cc88e679c6`; Drive `1WH-20Vmg9rSaieB3Y3yImFUxNbu0YJqq`; Dropbox `id:BSpOijBcT10AAAAAAD_9wQ`; 실제 dual upload+별도 metadata ACK |
| Current S | 위 실제 S 및 PR101;84/84 selected-file readback |
| Current C | 실제 `46a102b22b54cc03a91ad92bbd58d68dd82b7964`, tree `7a1ccdc0d8a472f021bc2a46903d28f0df70e69a`; base8e946b46… 위 own3files readback mismatch0; 다른39node/계약/authority/integration·WU90/REI/CR 보존 |
| Current B2 | 실제 dual upload+별도 metadata ACK;2732504bytes/109members/107selected payloads,SHA256 `0662cb03fd141886e5c77c1661d2fb5314173f46498c27a878bf6571188d4baf`; Drive `15RPRyRzRorUuYA4t5MvUMm2np_Nt7rjR`; Dropbox `id:BSpOijBcT10AAAAAAD_90g`, rev `65ea1ac97ff150af03d47` |
| Current D | **READY_FOR_DELIVERY_COMMIT**,19/20 delivery snapshot, C8 OPEN; actual own SHA는 게시 뒤 external receipt/PR tail에서 기록 |
| Current E / B3 / final PR tail | **PENDING_ACTUAL_RECEIPTS**; exact D/E archive와 actual external ACK로 닫을 전달 슬롯 |

B1/B1R/B2 확인 범위는 local archive/member identity와 provider upload 완료·별도 id/size metadata ACK다. 이 세 새 checkpoint를 remote full-download로 독립 재검증했다고 주장하지 않는다. B2는 immutable S84+C3와 실제 receipts, B1/B1R 각1회 및 pinned external14파일을 포함하며 post-S mutable 문서를 S로 오표기하지 않았다. B2 selectionCPU0.038864743/wall0.038868167001055554, packCPU0.24344514/wall0.24346663401229307, Drive upload4.799/Dropbox upload2.893/poll0.508/metadata0.383·0.418toolwall초를 별도 보존한다. 원전/도구/IO·preparation 비용은 science ledger와 분리한다. SciSpace1call/7.571toolwall, Exa2search(first6.034s, secondUNKNOWN_NOT_ZERO)+1fetch/2URLs, primary search1call, 실제 PDF GET2회/HTTP200, Wolfram context1회/19.628s와 evaluator1회/8.281s(bodyCPU0.06538699999999986/bodywall0.065335s)를 유지한다. 총 원격CPU와 미측정 모델·IO·실패한 upload 시간은 UNKNOWN_NOT_ZERO다. Filesystem loss와 실패한 첫 upload, 이전 lost B1 pack 비용을 지우지 않는다. 자세한 원장은 `evidence/source/SOURCE_CALL_LEDGER.json`, `evidence/recovery/RUNTIME_LOSS2.json`, inherited references 및 실제 delivery ACK에 있다.

## 6. 다음 thread에 복사할 재개문

```text
HE-ANG-FINITEMASS-CBA를 재개한다. Actual S=9fc8185437f145a6ba4569e1b38aa2e12d15acd9,
draft PR101, immutable S17/20; current D-ready delivery19/20, C8 PARTIAL_EXPORT, two process FAILs retained.
현재 HANDOFF/LOOP_PROGRESS/actual delivery receipts부터 읽고 최신 HEAD/AGENTS/병렬 owner/백업을 확인한다.
Actual C=46a102b22b54cc03a91ad92bbd58d68dd82b7964; actual B2 dual ACK 완료, D own SHA와 E/B3/final-tail은 external receipt 대기다.
B1 Drive1jcHpeQW_B0bpLYOV7-nEiujjPoV2d4qI / Dropboxid:BSpOijBcT10AAAAAAD_9vw,
B1R Drive1WH-20Vmg9rSaieB3Y3yImFUxNbu0YJqq / Dropboxid:BSpOijBcT10AAAAAAD_9wQ,
B2 Drive15RPRyRzRorUuYA4t5MvUMm2np_Nt7rjR / Dropboxid:BSpOijBcT10AAAAAAD_90g를 실제 복구 기준으로 사용한다.
새 science11.882829CPU/11.985978921002243wall under12/35,
lineage16.870803CPU/17.108468335994985wall under20/60, repair reserve0이다.
원7code+두 repaircode, 원/repairmanifest, failed partial, 최종 analysis와 실제 PNG를 보존한다.
SVG/producer figure metadata/original repair summary는 없고 원 FAIL을 PASS로 바꾸지 않는다.
추가 계산·export재시도·old suite replay·새 node/예산초기화·merge/activation은 승인되지 않았다.
물리 첫 입력은 HE-ANG-SOURCE-PAYLOAD다. DDCS20 고정값과 HE-X1/contract/HE38/Hex 근거를 재사용한다.
C9-NB-01/C23E/다른 owner OPEN과 모든 이전 비용·실패·unknown·비양도 reserve를 유지한다.
Post-S 중앙8e946b46aa44581f09141184f193223277f2ec88의 PHYS90 FINAL 관측도 보존하고 옛 S0 상태로 되돌리지 않는다.
Post-C 중앙53b2c135a1203a8784b6cc4acdec1d4fe174f166의 CR PR105 scoped RR child와 full N4/N5 OPEN, N6/N7 gates, final canonical backup ROOT_PENDING도 fresh E에서 보존한다.
```
