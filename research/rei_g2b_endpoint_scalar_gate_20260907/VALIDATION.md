# Bounded validation of the actual saved scalar

Acceptance follows PR #79's six controls, without adding a full solver or suite.
The scalar was evaluated once at commit
`8f6dca8dbb3cbfd8369e9ef2e25dfb305f834da3`. Actual results, not predicted outcomes:

| ID | Control | Result |
|---|---|---|
| G01 | Both actual normalized elemental weight sums equal one exactly | PASS |
| G02 | Upper face agrees with independent scalar expansion and enumeration of all 64 vertices of a small rational box | PASS |
| G03 | Nonuniform extensive weights used once; splitting a node preserves the result; double-weight mutant differs | PASS |
| G04 | Parsed source G2b mask is subgrid=0, HI=1, HeI=1, HeII=0 | PASS |
| G05 | Actual exact face/midpoint/width identities; exact penalty < actual-max-width coarse penalty < 1e-6 | PASS |
| G06 | Positive, zero and negative synthetic scalars classify correctly without floors | PASS |

Process: exit 0, no timeout, raw stderr empty; logs and exact fractions preserved.
No candidate defect, repair, skip, assertion relaxation or old-suite replay occurred.

## PHYS-MATH review, then PHYS-MATH-CODE review

Same assistant performed these sequential reviews. They are not independent
certification or proof-completion/production admission.

| Phase | Item | Finding |
|---|---|---|
| PHYS-MATH | Fixed totals and units | h/he and H/He use the stored extensive counts; D has cMpc^-1 units with common redshift factor removed. No extra node measure. |
| PHYS-MATH | Affine monotonicity | q_H,q_He and elemental weights are positive. Every charged-coordinate coefficient is nonpositive, so the upper face is the Cartesian minimum. |
| PHYS-MATH | State domain | Actual upper-face HI and HeI neutral diagnostics are strictly positive at every node. The result is endpoint-only and retains inherited inclusion semantics. |
| PHYS-MATH | JVP norm | For p=(q*u)/D>=0 with sum p=1, induced l1 norm of I-p*1^T is at most 2; multiplication by diag(q) yields 2*Jmax*max(q)/D_lo. Input is global-element-normalized neutral share, not charged-fraction or raw-count norm. |
| PHYS-MATH | Forcing | Reuses parent exact-real first-cell hull and conservative Jmax=1.4e48. Checks actual adjacent literals are below Jmax, opacity positive, external raw e=0. No PCHIP evaluation or floating-point range certificate inferred. |
| PHYS-MATH | Width and classification | Exact identities hold; weighted penalty is approximately 5.9724e-9, much below the 8.9897e-7 coarse bound. Positive D_lo is an observed result, not an imposed assertion. |
| PHYS-MATH-CODE | Binary intake | np.load allow_pickle=False; fixed keys, float64 shapes, finite values and L<=U checked before arithmetic; both NPZ Git blobs match fixed input identities. |
| PHYS-MATH-CODE | Exact arithmetic | as_integer_ratio lifts each stored entry before arithmetic. No rounded h_i, midpoint, width, NumPy sum or final nextafter enters the load-bearing result. |
| PHYS-MATH-CODE | Constants | Constants obtained from AST source literals / exact species-group CSV rows, parsed to explicit binary64 operands, then exact rational products. This chosen model is recorded and is not a production-parser parity claim. |
| PHYS-MATH-CODE | Metadata | Ordinary source-style H reduction differs from metadata; both are retained as diagnostics. Neither controls the exact normalization. No byte mismatch or scientific failure is inferred from that numerical diagnostic. |
| PHYS-MATH-CODE | Independent small calculation | G02 directly expands the scalar at synthetic vertices without calling the production face helper; G03 includes a double-weight negative control. This reference separation does not imply independent authorship. |
| PHYS-MATH-CODE | Report bounds | Decimal FLOOR/CEILING at precision 20 is checked back against exact Fraction endpoints; exact conditional L is strictly below quoted 1.914e52. |
| PHYS-MATH-CODE | Plot | PNG read with image viewer; labels, units, 12.244069 / 5.838149 / 18.082217 scaled contributions and footer are visible and consistent. Display only. |

Claim ceiling: no producer revalidation, continuous source-input tube, machine
owner parity, full atomic/OTS derivative, thermal inverse, exact-flow defect rho,
native production or admission. A new defect affecting these was neither tested
nor claimed. Existing evidence remains unchanged.
