# REI G2b endpoint owner denominator — exact reduction before binary intake

Date: 2026-09-07
Parent: PR #78, commit `a40c74cf24e793f0853235f33180e6b983ab6e8a`
Status: `G2B_DENOMINATOR_REDUCTION_PROVED__ENDPOINT_NUMERIC_VALUE_BLOCKED`

## Scope

This is a source-bound mathematical reduction for the already selected task
`REI_G2B_SAVED_ENDPOINT_OWNER_BOUND`. It does not rerun O01--O10, the validated
map producer, the canonical interval, production Rust, or any earlier suite.
It does not relabel the saved endpoint box as a continuous trajectory tube.

The available GitHub connector can read the relevant JSON and text sources but
cannot decode the binary NPZ payload into numerical arrays in this session. The
local container/Python route also failed before process start. Therefore the
actual endpoint scalar is not invented. The point of this note is to reduce the
remaining binary calculation to the smallest exact quantity and remove an
unnecessary nodewise-hazard interpretation.

## Fixed source facts re-read

At the parent commit:

- `VALIDATED_PUBLIC_BOXES.npz` has Git blob
  `8f67740b43c82be04f8efd521990b7b2b185afea`, size 2,623,393 bytes.
- The selected lane is `LOCAL_NEUTRAL_HAZARD_PRIMARY`; public coordinates are
  `(x_HII, x_HeII, x_HeIII, log_T)` with 46,080 nodes.
- Its historical reported public widths are
  `w_HII=2.6643106193491306e-6`,
  `w_HeII=1.2958711863020334e-5`,
  `w_HeIII=2.8461103586743808e-8`.
- The lane report says `certified=true`, `map_enclosed=true`, partition 2048,
  no table event, and maximum validated local error
  `1.1621773858117024e-4`. These are inherited reported results, not rerun here.
- `STAGEWISE_ENDPOINT_CONTAINMENT.json` reports direct endpoint containment with
  zero outside count. This is a containment statement, not a neutral-fraction
  lower bound.
- `initial_material_state_metadata.json` records fixed global H and He totals,
  and initial global fractions
  `x_HII=0.999917`, `x_HeI=2.099999999994901e-5`,
  `x_HeII=0.997137`, `x_HeIII=0.002842`.
- G2b atomic literals are
  `sigma_HI=2.1304056570433978e-19 cm^2` and
  `sigma_HeI=2.456081711325024e-18 cm^2`.
- The source constants are `NH0=1.88e-7 cm^-3`,
  `YHE=0.079`, `MPC_CM=3.085677581491367e24 cm`.
- G2b external subgrid response is structurally zero in the first forcing cell,
  while its saved current is positive.

## Exact denominator reduction

For G2b define fixed elemental totals

    H_H  = sum_i h_i,
    H_He = sum_i he_i,

where `h_i=N_HI,i+N_HII,i` and
`he_i=N_HeI,i+N_HeII,i+N_HeIII,i`. Define normalized node weights

    a_i = h_i/H_H,   b_i = he_i/H_He.

Thus `a_i,b_i >= 0` and, by definition of the same fixed totals,

    sum_i a_i = sum_i b_i = 1.                         (1)

No quadrature weight is added: the source `N_*` values already carry the node
measure.

Let

    q_H  = NH0 * MPC_CM * sigma_HI,G2b,
    q_He = NH0 * YHE * MPC_CM * sigma_HeI,G2b.

The common `(1+z)^2` factor cancels between numerator and denominator for this
fixed-current state partial. With `x_HI=1-x_HII` and
`x_HeI=1-x_HeII-x_HeIII`, the normalized owner denominator is

    D = q_H  * sum_i a_i (1-x_HII,i)
      + q_He * sum_i b_i (1-x_HeII,i-x_HeIII,i).        (2)

Hence D depends on the node state only through two **global weighted neutral
shares**

    X_HI  = sum_i a_i (1-x_HII,i),
    X_HeI = sum_i b_i (1-x_HeII,i-x_HeIII,i),

so

    D = q_H X_HI + q_He X_HeI.                          (3)

This is the main reduction. A nodewise minimum neutral fraction is not required.
A single node may have a very small neutral share without making D small if its
fixed elemental weight is correspondingly small. Conversely a positive minimum
at one or a few nodes proves nothing about the global denominator.

## Exact Cartesian-box lower bound

Let the stored endpoint box give componentwise bounds

    L_HII,i <= x_HII,i <= U_HII,i,
    L_HeII,i <= x_HeII,i <= U_HeII,i,
    L_HeIII,i <= x_HeIII,i <= U_HeIII,i.

Because every coefficient in (2) multiplying an ionized fraction is negative,
D is affine and coordinatewise nonincreasing in all three charged-fraction
arrays. Therefore the exact minimum over the **stored Cartesian box** is attained
at the upper charged-fraction face:

    D_box,lo = q_H  * sum_i a_i (1-U_HII,i)
             + q_He * sum_i b_i (1-U_HeII,i-U_HeIII,i). (4)

No generic interval package, PCHIP range helper, optimization search, nodewise
minimization, or artificial positive floor is required for (4).

If (4) is strictly positive, then the endpoint owner denominator is rigorously
positive conditional on the inherited inclusion meaning of the saved box and
the chosen exact-real interpretation of its binary inputs. If (4)<=0, the
Cartesian representation is insufficient for this proof. That result does NOT
show that the physical endpoint has nonpositive neutral material, because the
independent `x_HeII`/`x_HeIII` box may lose simplex anticorrelation and admit
unphysical combinations.

If one intersects the box with the helium simplex
`x_HeII+x_HeIII<=1`, then the He-neutral term is nonnegative but can reach zero
unless an additional correlated lower margin is present. Therefore a simplex
constraint alone cannot manufacture a strictly positive He contribution.

## Midpoint-width form and a coarse data-independent width budget

Writing stored midpoint arrays C and widths W=U-L, equation (4) is equivalently

    D_box,lo = D_mid
             - (q_H/2)  * sum_i a_i W_HII,i
             - (q_He/2) * sum_i b_i (W_HeII,i+W_HeIII,i).  (5)

Using (1) and the reported maximum coordinate widths gives the safe inequality

    D_box,lo >= D_mid - Delta_width,                      (6)

    Delta_width <= 1/2 * [
        q_H  * 2.6643106193491306e-6
      + q_He * (1.2958711863020334e-5 + 2.8461103586743808e-8)
    ].                                                    (7)

From the source literals one has conservatively `q_H<0.124` and `q_He<0.113`
in the corresponding cMpc^-1 normalization, so

    Delta_width < 1.0e-6 cMpc^-1.                        (8)

Equation (8) is deliberately loose. It is a width-budget theorem, not the
missing endpoint denominator. Therefore a single scalar check

    D_mid > 1.0e-6 cMpc^-1                               (9)

is already sufficient to prove `D_box,lo>0` without separately evaluating every
box corner. For a tight bound, use (4) directly with directed/exact arithmetic.

As a scale control only, the initial global state has positive neutral shares
`X_HI=8.3e-5` and `X_HeI≈2.1e-5`. This is NOT substituted for the endpoint.
It only confirms that the initial denominator is not structurally zero.

## Conditional owner-current derivative

For G2b, with resolved species `s in {HI,HeI}`,

    j_{s,i} = J q_s u_{s,i}/D,

where `u_HI,i=N_HI,i/H_H`, `u_HeI,i=N_HeI,i/H_He`. On any endpoint input set
with `D>=D_min>0`, the previously derived augmented-normalization estimate gives

    ||D_u j_G2b||_1 <= 2 J_max max(q_H,q_He)/D_min.       (10)

The first-cell exact-real PCHIP current hull can still use the conservative
`J_max<=1.4e48` box photons/s declared in the parent handoff. Equation (10) is
not evaluated numerically until (4) is actually consumed from the saved arrays.

## Arithmetic and rounding boundary

The earlier `pchip_bounds.py` generic final-`nextafter` issue is irrelevant to
(4): no polynomial is evaluated here. For a rigorous binary-input calculation,
read the NPZ doubles exactly (or as exact binary rationals) and accumulate (4)
with directed rounding / exact rational arithmetic. Converting the arrays to
ordinary binary64, summing, and applying one final `nextafter` is not enough for
a certification claim.

The fixed global totals should be constructed from the same source arrays or
verified against them. The decimal metadata totals are provenance/control data,
not silently promoted to exact sums.

## Actual execution status in this session

- GitHub text/JSON source and metadata readback: DONE.
- Binary NPZ base64 transport probe: the 2.6 MB public box returns empty content
  through the connector size path; the 415 kB stagewise NPZ returns base64 but
  the connector response is truncated before complete reconstruction.
- Local container: ClientError before process start.
- Local Python: ClientError before process start.
- Wolfram MCP: SSE probe HTTP 404 before kernel evaluation.
- New project/CAS test execution: NOT_RUN.
- Producer / previous suites / GitHub Actions rerun: NOT_RUN.

Therefore the actual numerical `D_box,lo` and conditional L are BLOCKED by
binary-array intake in the present conversation, not by a mathematical ambiguity.

## Scientific classification

Established in this node:

1. G2b denominator is a two-global-share quantity, not a nodewise hazard.
2. The exact minimum on the stored Cartesian endpoint box is the single affine
   upper-face evaluation (4).
3. The public maximum widths contribute less than a coarse `1e-6 cMpc^-1`
   denominator budget around the stored midpoint.
4. If the Cartesian lower is nonpositive, that is representation insufficiency,
   not evidence of physical negativity.

Still unresolved:

- actual `D_box,lo` from the saved binary endpoint arrays;
- endpoint conditional G2b current/JVP bound;
- other source sites / continuous source-input tube;
- binary64 implementation parity, total OTS/atomic derivatives, thermal inverse,
  exact-flow rho, native four-site production and provider admission.

The science claim ceiling therefore remains below first-interval/provider PASS.
