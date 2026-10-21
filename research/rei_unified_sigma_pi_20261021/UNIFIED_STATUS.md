# Current continuation: D8 complete, D9 scoped PASS, D10 ready but not run

This section updates the historical status preserved below. D8's four accepted adjacent stored-sample brackets were already complete and were reused without a D8 rerun. D9_COMPONENT_SHEAR_BUDGET is scientifically complete with the controller's **PASS_SCOPED_D9**, supported by its frozen identity derivation, 175 nominal stored histories ×153 epochs, 35 exact references, four meaningful software controls and one independent complementary review whose three findings are closed.

D9 created **0 new IVPs, 0 ODE callbacks and 0 momentum-moment recomputations**. Maximum sampled scaled residual is 1.473444875767401e-6, below the fixed 2e-5 diagnostic. All four accepted D8 brackets retain reconstructed signs and satisfy the local 0.1 residual ratio requirement; maximum observed ratio is 2.022140048467199e-5. These are sampled-data consistency results, not a convergence certificate, continuous-root estimate or trajectory-superposition theorem.

Final D9 source/result publication is **PENDING_FINAL** and final backup is **PENDING_FINAL** at this assembled snapshot. Phase-1 source checkpoint `cf2dfcad80960726283c641ba781e0bb166fc041` and its dual-provider complete readback are actual completed evidence; their receipts are under `D9_COMPONENT_SHEAR_BUDGET/preservation/phase1/`. This final source snapshot does not claim its own future commit or future provider acknowledgement. Read the later D9_DELIVERY_ACK and external post-publication receipts for those outcomes.

The next single node is **D10_ZERO_INITIAL_MATTER_STRESS_GENERATION**, status **READY_FOR_THEORY_AND_SAVED_DATA_INTAKE_NOT_RUN**, depending on D9. Begin with an exact LRS pressure-moment derivation and existing 35 zero-initial-matter histories; initial new-IVP allowance is **0**. D10 has not been executed here. Completed pilot/AGE/PR198/D8/D9 campaigns must not be replayed.

D9's portable NCP input is included, with a python3 wrapper and externally bound compact-input identity; actual D9 NCP execution is **NOT_RUN**. PR215 NCP evidence remains a separate physical lane. PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production admission NOT_ISSUED and V12 restrictions remain unchanged.

Current scientific report, code, input identities and handoffs: `D9_COMPONENT_SHEAR_BUDGET/`. Current code guide and next-thread prompt are also copied to the central handoff paths with this context.

---

# Historical status snapshot retained verbatim

# REI 통합 상태 — 2026-10-21

## 현재 결론

Lane B의 175점 component pilot은 **COMPLETE_WITH_VERIFIED_RAW**다. 35개 기존 nominal을 그대로 재사용하고 누락된 140개 nominal +3개 refinement만 계산했다. 기존 91+3과의 중복을 제거한 237개 history 모두 z=20→2까지 완료했다. 각 history는 121개 저장 prefix와 32개 새 epoch를 합친153 epochs다. 기존 PR198 및 AGE 계산 재실행은 0이다.

B1/B2 numerical gate, 독립 raw 검토, 실제 그림 검토와 최종 bundle 독립 판정은 PASS_SCOPED_PRELIMINARY로 닫혔다. 최종 독립 감사는 independent_audit/FINAL_REVIEW.json이며 미해결 material finding은 0개다. 최종 Git/provider closure는 별도 receipt로 기록한다. Production scientific admission은 NOT_ISSUED다.

## 최종 전달 상태

- Reviewed source/results commit: `3a525e3e16f1ba9393818a800327cc58597fd7b5`, tree `d12858ca1caa2496374e87f3fe3f489425eebda9`.
- 175개 게시 대상 파일, 8,013,267바이트 전체 Git readback PASS. 실제 변경 171개는 지정한 두 연구 경로 안에만 있으며 삭제는 0개다.
- 최종 archive: `REI_UNIFIED_FINAL_20261021_20261021T111808Z.tar.gz`, 36,855,980바이트, payload 2,900개 + manifest.
- SHA256: `7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251`.
- Drive `1PeQ_F7oNut4qjcy7dv5RCuEZBUk6th72`, Dropbox `id:BSpOijBcT10AAAAAAD_gOw`: 각각 upload ACK, HTTP200 전체 GET, 크기/SHA256 및 2,900개 payload hash 검증 PASS.
- D0–D7 완료. 현재 과학 case pending 0. 다음 단일 노드는 D8의 저장 sample에 기초한 네 late sign reversal의 redshift bracket 산출이며, 새 ODE 호출 허용량은 0이다.
- archive는 source/results 게시 후 포장한 고정 객체다. 이 최종 상태 문서와 FINAL_DELIVERY_ACK는 포장 후의 별도 metadata다. 마지막 metadata commit은 이 파일을 포함한 Git commit과 외부 transport ACK에서 확인한다.

## Lane별 source와 provenance

| Lane | 실제 source / 실행 identity | 결과·검토 상태 | 게시·보존 |
|---|---|---|---|
| A: PR198 | HEAD8bd35af5f11c7ea5945b656be1c013d1c1933498, reviewed b140170ce0c58159368b6b81be49ac35ca764851 | 625+606 unique trajectories,z20→4,half-contraction,8states. 기존 PASS_SCOPED_PRELIMINARY 유지 | 기존 final archive/ACK를 Drive·Dropbox에서 모두 전체 회수·검증. 변경·재실행 없음 |
| B: 원래91점 | PR147 kernel3b85dedce84d37b3e165da00685a8a984950aafe. 역사적 실행 wrapper는 UNPUBLISHED_WITH_SHA256 | 91nominal+3refined=94개를 이전 scratch에서 복구.40/56states,121epochs,Frobenius. 기존 C9 PASS 재사용 | 기존 staging은 실제 Git 게시가 아니었음. 이번D0/D1/D3 dual checkpoint에 전체 보존 |
| B:175점 | 같은 vendor; independent matter/radiation 초기 quadrupole; 새 실행 runner49d4464e…374d97 | 35exact reference+140new nominal+3new guards. 신규143개 완료,3refinement PASS | raw/receipt/source D3 양쪽 전체GET 일치. 소유 Git path에 additive publication |
| B:z2연장 | 첫100tail은 runner49d4464e…374d97; 이후137tail은 운영수리 runnera7bf1a82…51b64 | 237unique tail.100개는 raw 저장 후 receipt 직렬화 실패를 데이터만 검증해 복구;137개만 새 적분.6refinement PASS. ODE retry0 | 실패 receipt/attempt/raw와 수리 전·후 source를 모두 보존 |
| C:PR199 AGE | intakeHEAD964b2e3c098f6e475999a4eddc7a6aa0f8f053cc; historical AGE task tree0a45ca2d8fec1381d4cc1c0852f2ca3b0721c44c | NATIVE_AGE_TIME_CONVERGENCE=HOLD; NONLINEAR_GRACKLE_RESPONSE_BOUND=NOT_ESTABLISHED | native AGE files와 완료 time8/16/32 histories 변경 없음. 이후 branch HEAD 변화는 통합/B pilot의 additive publication과 분리 |
| D:PR213 warm729 | HEADd32cd99fa19c65aa1ca63dbc8aab8741834270e8 | a=.1999→.2,z≈4.0025→4의 다른 native slice. z20→2 자료가 아님 | QUALITATIVE_COMPARISON_ONLY |

PR199은 통합 문서 checkpoint8b71c13e23202edfce1ee67fb2da552fefb9a583까지 expected-head FF 게시·전체내용 readback을 확인했다. 최종 source/result publication SHA/tree와 현재 PR HEAD는 PUBLICATION_RECEIPT 및 FINAL_DELIVERY_ACK를 따른다. 실행 당시 파일 SHA와 이후 Git commit은 서로 다른 provenance 필드다. Draft 유지,no merge,no force push.

## 수치 실행과 운영 오류의 분리

- B1:143신규 +35reference, 실패0. 세 refinement의 최대 보고 차이7.893523413572169e-13; gate2e-6.
- B2:237tail/237joined raw, 모두 complete. 여섯 refinement의 최대 보고 차이3.5701298281608576e-13; gate2e-6.
- 최초 B2의100workers는 저장 완료 뒤 NumPy boolean의 RESULT JSON 직렬화 오류로 FAILED_WORKER_EXIT를 기록했다. 원래 실패 기록을 보존하고 raw의33tail/153joined epochs, exactprefix/join, 모든 physical gates를 재검토했다. 원래 nfev/message/RSS 및 실제 solver-success flag는 미기록으로 남긴다. endpoint coverage를 별도 복구 근거로 사용했다.
- 불필요한 재적분 없이137pending만 이어갔다. aggregate120초를 늘리지 않았으며, 남은 작업에는 contracted30초 이하인10초 deadline과2workers를 사용했다.
- B1 cumulative charged child22.980342250994초/240초에는 historical8.778983763986616초가 포함된다. B2 cumulative charged child100.95804054901964초/120초에는 직렬화 실패 비용90.08237553801882초가 포함된다.
- 이는 보수적인 dispatch-to-observation 실행 기록이며 CPU benchmark 또는 speedup 측정이 아니다.

## 실제 그림과 새 해석

z2_extension/figures/에13개 PNG/PDF figure versions와 실제 CSV를 생성했다.175점의 component endpoints,7개 fixed-Sigma detail, opposite-stress histories,91점 radiation baseline,refinement/64-node brightness controls,선택한Sigma_F,i=.003의 signed shear/total-stress plane을 포함한다.

초기(Σ_F,P_m,P_r)=(0,+.0003,-.0003)에서 S_F(z4)=-3.681005243450802e-5,S_F(z2)=-3.145959056164794e-5다. 반대 부호 조건은 각각+3.6809470587529176e-5,+3.1458662949047326e-5이며 정확한±대칭으로 주장하지 않는다. 저장 grid의 최대|S_F|는z≈4.37195627,후속samplez≈4.30809546까지 원 source S_F′가 부호를 바꾼다. 연속극값 root를 새로 적분한 것은 아니다.

Sigma_F,i=.003의25점은z4에서모두signedS_F>0이나z2에서4점이음수다. 각점은 실제 계산이며 연속zero contour를 제시하지 않는다. 같은저장자료로완료한 단일후속노드는 cancellation_turnover_on_saved_histories(0newIVP)다. 자세한 수치와 한계는 NEW_SCIENTIFIC_RESULTS_KO.md 및 NEW_SCIENTIFIC_EVIDENCE.json을 따른다.

## Norm 및 재사용 관계

A는half-contraction, B는fullFrobenius다. S_F=sqrt2 S_half,P_X,F=sqrt2 P_X,half이며 Pi_tot=abs(P_m+P_r)다. SI energy-density stress에서K=8πG/c²를 proper-time H와 사용한다. K=8πG/c⁴라는 다른 Einstein coefficient를 쓸 때는(H/c)²로 정규화해야 한다.

A/B의canonical_fv.py,lrs_boltzmann.py,species_hierarchy.py,cosmology lock은byte-identical이지만 wrapper/state/grid/initialaxes는 다르다. 실제 물리축까지 대응하는 공통control만 COMPARABLE_AFTER_EXPLICIT_TRANSFORM이며, 그 외에는QUALITATIVE_COMPARISON_ONLY다. A/B사이 raw의IDENTICAL_REUSABLE_CASE를 부여하지 않는다. B35및Aneutral25 aliases는각 lane내에서hash-bound IDENTICAL_REUSABLE_CASE이며 IVP수에0을기여한다.

Photon/nu각각의energy/number출력은있지만 초기brightness와collisionlessoperator는공유한다. 독립gamma/nuinitialquadrupole,collisions,fullnative reionization을구현했다고주장하지않는다. 이non-tilted모형은각species의reflection-even분포를사용하며 일반적인totalflux상쇄와 개별speciesnon-tilt를동일시하지않는다.

## 보존과 게시 checkpoint

| 단계 | Archive SHA256 | 확인 상태 |
|---|---|---|
| PR198기존final | 2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d | 37,945,383B;5747payload+manifest; 양쪽archive/ACK fullGET검증 |
| D0/D1복구 | 25e1196e3050ae535273f1b88baf99183656bcd0930be49ff9a359e960594abf | 10,829,091B;604payload+manifest; Drive1qHeeBL1y1uIbd7vY0pwo8t4asdNI8kbh, Dropboxid:BSpOijBcT10AAAAAAD_gLA; 양쪽fullGET검증 |
| D3실행 | 7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498 | 31,904,176B;2360payload+manifest; Drive1_noyMOexSIBbHdWIqkoGsvt3nBxwGZGi, Dropboxid:BSpOijBcT10AAAAAAD_gNA; 양쪽fullGET검증 |
| D4–D7 최종 | 7b39d8c8ffa0b61762211295a25d14412de37f6e1a6d163ebf0b93a8337f2251 | 36,855,980B; 2,900 payload+manifest; 양쪽 upload ACK 및 전체 GET/bytes/SHA/manifest 검증 PASS |

CASE_PROVENANCE_LEDGER.json/csv에는1705numerical segments와60referencealiases,총1765rows가있다. B의237prefix와237tail은같은237histories의다른구간이며 신규모형474개가아니다. Git에는losslessgzip사본과index,전체uncompressed파일은최종archive와직접deliverable에보존한다.

## 조사 범위와 남은 한계

REI254branches/212PRentries,BASS261branches,VigilODE184branches의목록pagination과관련4개REI전체recursive tree를조사했다. 관련source/receipt는선별하여확인했다. 모든branch의모든byte,모든ChatGPT/Codex대화,접근불가NCP파일을전수열람했다고주장하지않는다. Exa/SciSpace문헌발견과Wolfram실제기호계산을수행했고원논문으로메타데이터를확인했다.

현재turn에서PYTHON_PASS,CPP_PASS. 실제로컬effectivequota8CPU/8GiB를관측했고협조적4worker또는2worker로계산했다. NCPownercheckout/affinity/RAM/disk/process상태는NOT_OBSERVED. 로컬key부재및현재DesktopCommanderget_config의monthlyquota SERVICE_ERROR/do-not-retry를기록했고재접속하지않았다. 다른작업이존재한다는이유로계산을중단하지않았고 unrelatedprocessactions=0이다.

NCPwrapper는최대63one-threadworkers와실제affinity/cgroup/idle/RAM/disk로하향하는준비상태다. 현재과학casepending=0이므로NCP가사용가능해져도같은계산을재실행하지않는다. NCP64/128의현재실측이나가속배수는없다.

Source/results commit의 verify run39590742697은 unchanged Rust 경로의 cargo fmt --check에서 failure, Rust tests는 skipped다. 실제 변경에 rust/ 파일은 0개다. 기존 전체 CI failure는 scoped Python pilot PASS와 구분하며 CI_POSTPUBLICATION.json에 실제 결과를 보존했다. V12cap180/debit200.39897231891518/remaining100NOT_AUTHORIZED보존. 관측likelihood,통계fit,generalnon-LRS,fullnative reionization및productionadmission은이pilot의승인범위가아니다.

