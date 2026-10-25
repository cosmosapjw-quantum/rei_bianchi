# HI native instantaneous Bianchi I strain response

Unit `HI_NATIVE_STRAIN_RESPONSE_20261025`, builtin PhysMath workflow 1.0.0.
Status: implementation prepared; scientific child **NOT_RUN** and admission pending.

`strain_response.py` adds the fixed-atom fourth radial moment R and its mass
derivative R_M. It forms C=5W-R, C_M=5S-R_M, kappa=2C/15 and Gamma=C/(3W),
then the initially-isotropic instantaneous tensor response
`L_C(B)=-C*((tr B)I+2B)/15` and full amplitude/mass/strain JVP. Exact symmetry
and finite scalar guards reject malformed matrices and bool inputs.

Inputs are the same 4,368 stored HI/z=2.479 atoms, exact nominal electron mass
`510998.95069 eV`, and exact prior raw/helper copies. Native W/S intervals and
their Decimal100 values are selected by exact nominal mass string from the saved
massive-stress output; A,K,L are reused verbatim. Only R/R_M are newly integrated.
The old `massive_terms` function is never called. Individual native terms are
exact rational; their totals use the unchanged outward dyadic integer accumulator
at P128/P160. The eight new control groups cover literal hand values, tensor
decomposition/linearity, rational rotation, full JVP, input/zero guards, exact
14-ray moments and unreduced derivative, Decimal100 finite transport/remainder,
and new tensor signed cancellation/underflow/subnormal classification.

The 14-ray fixture has exact second/fourth angular moments. Finite transport at
nonzero strain is a discrete 14-ray reference; it is not identified with the full
continuous sphere integral. Native coefficients use the separately declared
initial isotropic closure. Units and the finite-strain remainder are fixed by
`authority/THEORY_STRAIN_RESPONSE_KO.md` and the root implementation contract.
Source coefficients are per target per birth-proper-second. The transported
tensor is a source-weighted coeval cohort; arbitrary birth history requires its
separate history integral. Synthetic amplitudes and matrix directions are controls. Actual HI history,
density, birth amplitude, geometry clock, IC, and thermal heat remain open.

## One authorized execution

Run from this leaf, only after explicit root GO binding the prepared manifest:

```bash
python3 run_focused_once.py --go authority/ROOT_GO.json
```

The launcher uses one child, CPU6s/wall8s, one thread, 512MiB address-space cap,
no network calls in the scientific code, an exclusive attempt record, and no
automatic retry. It writes raw stdout/stderr/resource receipt and on observed
success a result summary. No project import/test/build occurs before the child.
Independent Astra R6/C9 and root claim admission follow actual results.

Known partial CPU before this unit is 11.160661s. Historical 10.110448s against
10s remains failed with 0.110448s overrun; no reset or relaxation. Whole L0 is
UNKNOWN_NOT_ZERO; original cumulative cap NOT_FROZEN. CAS remote CPU and
model/IO/packaging costs are separately unmeasured. Old scientific replays0;
L4_ready=false and whole-model completion=null.

Prior science S42f5984a78f123ce26950cec0e0b8505da3e7ce4 and documents
Decbb3124b49e75d8a7e948705b3894307d628349 remain read-only. Publication is root-only,
new leaf only, after current HEAD/AGENTS/protected-state and expected-SHA checks.
Inherited scoped prerequisites are L0 at566f242b843fe4428cedbb8f2ea319ad706ac605
and native-HI science8d68dff35ca2bdc456049081132a7d2449b29143; this unit neither
reruns those calculations nor closes whole L1/L4.
