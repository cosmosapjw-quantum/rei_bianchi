# R2/C2 — 근거 재사용과 식-코드 대응
## 이 입력이 답하는 질문
EXFOR M0475002의 같은12개 nominal-angle DCS와 ERR-S 창에 맞는 전체 비음수 짝대칭4차 다항식이 존재하는지, 그리고 그 가족이 동일사건 유한검출기 수용확률을 어디까지 제한하는지를 묻는다.
event/inclusive 정규화, 실제 편극분포, photon history, liquid-He projection 또는 deposition을 공급하지 않는다.
M0475003의6개 total은 다른 에너지 격자다. 그대로 저장하되 보간·결합하지 않는다.
sources/M0475.x4와 EXFOR_M0475_PROVENANCE_AND_DATA.json을 기존의 검증된bytes/hash로 재사용한다.

## 식과 구현
| 수학 대상 | 구현 위치와 의무 |
|---|---|
| q(z)=b0+b1z+b2z²; signed b | src/quartic_aperture.py; rational only |
| nominal angle enclosure, midpoint, eps | angle_row; inherited trig identity, signed row error |
| global minimum on[0,1] | quadratic_minimum; endpoints + interior stationary point |
| old sufficient cone coordinates | folded_bernstein; same exact degree4 polynomial |
| q(1)=0 parameter reduction | lift/transform; b2=-b0-b1 |
| inner Bernstein / outer nodal constraints | positivity_rows/system; fixed N1/4/16 |
| exact active-set vertices | enumerate_shared; all bases, shared inverses across RHS |
| inherited same-event strips | exfor_aperture.geometries; nine new geometry calls only |
| monomial strip integrals | integrate_monomials/moments; signed_numerator |
| certified outer range and witness brackets | vertex_intervals/objective/witness |
| one fixed12-case campaign | campaign; exact certificates + prior saved-only comparison |
| meaningful new controls + saved reader | tests/test_quartic_aperture.py; independent reader is not a second optimizer |
| bounded runner and identity | scripts/measure_execution.py,run_bounded.py,validate_once.py |
| saved-only figure | scripts/plot_saved.py; no scientific import/recalculation |

## Evidence inventory and reuse boundary
- Fresh GitHub source survey: seven repos,1,438refs,16selected verified source bodies.
- Backup survey: Dropbox terminal census; Drive observed capped/indexed views; Library terminal recent metadata and9selected fulltexts.
- Root targeted conversation summaries are derived context. Actual external ACK/ref records govern delivery.
- Exa and SciSpace were each actually queried for positivity/Bernstein alternatives. Ten SciSpace candidates are metadata-level discoveries; only three selected primary works were read in abstract/full-PDF relevant sections through the public web.
- Wolfram context returned documentation; its semantic searches supplied no numerical verification. One new bounded evaluator is scheduled for S07.
- Existing EXFOR11 saved result SHA256=5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243 is comparison-only.
- Neither official source retrieval nor prior campaign is repeated.

