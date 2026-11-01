# PR320 original physical H/He tick160: nodewise recombination source / derivative research

2026-11-01. **One physically sourced derivative unit, not one completed 88-node canonical DAG unit.**

**Source authority.** Original `rei_bianchi` Draft PR320 HEAD `e5836fc4b8804d1bcdcdcbb97ab33f822703fa46`. Authentic existing Aug-29 first-interval partial run: 3 endpoints / 160 of 131072 ticks; 46,080 distinct physical nodes in each of 3 same-numeric lanes. GitHub Actions run 41259585168, artifact ID 13064333012; complete ZIP SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7`; original raw state array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`. The old original owner contains 26 events and remains unmodified.

**Scientific law.** Independently evaluate *published*, not original-owner-byte-equivalent, Hui & Gnedin 1997 H II Case-A/B coefficients `lambda=315614/T_K`,
`alpha_A=1.269e-13*lambda**1.503/(1+(lambda/.522)**.470)**1.923` and
`alpha_B=2.753e-14*lambda**1.500/(1+(lambda/2.740)**.407)**2.242` cm³/s.
At each of **46,080** original physical state nodes compute `r=alpha(T)*xe*xHII`, first partial derivatives w.r.t. `T,xe,xHII`, second `T` derivative and interval bounds. No density weights, no nH history; `r` is a **per-node conditional coefficient proxy**, NOT a volume-weighted cosmological recombination rate or the original 26-event RHS.

**Original node-state vs mean-state closure:**
- Case A `<r>/(alpha(<T>)*<xe>*<xHII>) = 1.9375156502404693`, conservative interval `[1.937497076938752,1.937534224311686]`.
- Case B `2.256565410424417`, interval `[2.2565413222348507,2.2565894996894986]`.
- `<T>=20237.646048421273 K`; source T spans `2096.67–66261.76 K`. The factor is dominated by `<alpha>/alpha(<T>)` equal to 1.93841599 and 2.25769361. It is not a direct clumping factor, nor evidence that Case A or B is the original provider closure.
- **46,092** derived model records: 46,080 per-node A/B+derivative entries, 10 temperature deciles, 2 summary Case records. No new observations; no new IVP.

**Executed local science:** full 19,992,525-byte source-inclusive ZIP SHA256 `3553d2c5d4afad70085ced5eab0425f2cba52a3cef270d934e0890e07b0f3504` contains `analyze_tick160.py`, `standalone_stdlib.py`, `independent_check.py`, 24 tests, complete 46,080 node CSV, figures, theory, blind referee, 20-stage ledger and handoff. Clean extraction and `bash REPRODUCE.sh` 24/24 PASS; independent 75-digit Decimal 30 source/Case checks max rel 8.93e-16. The **Git exact-blob** compact `code/standalone_stdlib.py` equals the tested local source. GitHub publication is intentionally *thin*: no false claim that 20MB original ZIP is mirrored in git.

**Original scientific blocker remains:** [160,161] next tick failed original cross-image logT error `2.1245050576368385e-4 > 2e-4`. The published `alpha` and derivatives can constrain one of 26-event `D_h=F_h-F_{h/2}\circ F_{h/2}` terms in a future actual same-parent joint state/source remainder. Nothing here certifies the original nonlinear map, the original tick or the first full interval.

**DAG:** central **28/88** (reported), working **33/88** (reported), physical fast **4/7** (reported), canonical +0, first interval BLOCKED, production HOLD, no merge, force push, new IVP, tolerance relaxation or automatic next node.

Primary source: <https://doi.org/10.1093/mnras/292.1.27>. Source artifact: <https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41259585168>.
