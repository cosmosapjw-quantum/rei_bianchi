# THEORY16 R6: recovered conserved-energy observable bound

Date: 2026-10-14, Asia/Seoul. Parent: PR41 at `1a34c42504502bb3b30898f640b00ddb14e2a323`. This is publication of the original R6 result, not a new science replay. The source52 stopping-event norm remains `2 E_parent`; the invalid old `2 DeltaE` bound is not reinstated.

## Actual preserved artifacts

- Original 65-member ZIP: `BASS_HE_THEORY16_R6_ENERGY_QUOTIENT_20261014_v1.zip`, 368684 bytes, SHA256 `f31b71483f80346d44a1d60e06e7487236bc006298a3d67e88fee00415511cc4`.
- [Complete original evidence on Drive](https://drive.google.com/file/d/1sWr4Am8j_sRlqbikgDPA8K4hrW9cnz9G/view). Parent folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`. A native Drive fetch restored the actual ZIP; its SHA256, CRC and all 64 manifest entries were checked.
- Dropbox completed: `id:BSpOijBcT10AAAAAAD46Gg`, `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_THEORY16_R6_ENERGY_QUOTIENT_20261014_v1.zip`, server size 368684. This is provider acknowledgement and size verification, not a separate Dropbox restoration test.
- [Original full Korean report on Drive](https://drive.google.com/file/d/1Vq-fJEQ6wVw8_HEzvDay7cRz_y4K8gni/view), `BASS_HE_THEORY16_R6_REPORT_20261014.md`, 23548 bytes, SHA256 `f3a5bf6722679e9314b6c1a224f37029791fa4a29713e610f98f414954ecd4fb`.
- Same standalone report completed on Dropbox: `id:BSpOijBcT10AAAAAAD46Sw`, original name and 23548-byte size. Report bytes match the report inside the immutable ZIP.

No originals overwritten, permissions changed, or production source edited.

## Reusable result and proof

Let `Z=(E_i N_i, C_H, C_He, U)` use the same cell-energy coordinates (eV), and let `e=Z_full-Z_selected` obey `||e||_1 <= B_D(t)`. The source-bound total free-electron census is `N_e=N_ref+C_H/B_H+C_He/B_He`, not the thermal-only census.

For two trajectories preserving the same initial total energy, `1^T e=0`. With `w=(0,...,0,1/B_H,1/B_He,0)` and `Bmin=min(B_H,B_He)`,

    w^T e = (w - 1/(2 Bmin) 1)^T e,
    |delta N_e| <= B_D(t)/(2 Bmin).

The constant is sharp on the energy-conserving subspace: choose `e_CH=d`, `e_U=-d`, other components zero. This is the standard zero-sum/oscillation duality applied to the particular conserved energy lift; no novelty claim is made for that general norm identity. It does not claim this extremizer is reached by the physical source.

For an independently bounded nonzero total-energy difference `DeltaE=1^T e`, the corresponding valid formula is `|delta N_e| <= (B_D+|DeltaE|)/(2 Bmin)`. A changed geometry/source still needs its own valid state-error bound; adding a bookkeeping coordinate alone does not transfer an old certificate.

The inherited positive donor series is `B_D(t)=sum C_j t^(r_j+1) phi_(r_j+1)(Lt)`. For endpoint upper scores `b_j`,

    integral_0^h B_D dt <= h sum b_j phi_(r_j+2)(Lh)/phi_(r_j+1)(Lh).

All source52 scores, `h=100000 s`, branch and rate model remain unchanged. The stored upper integral is `0.0001818776180517631685428510876028327695884387681524275198 eV s`.

For the common rest-frame fixed-volume Thomson probe, `tau=c sigma_T/V integral N_e dt`. Thus `R_tau_R6=R_tau_R5/2`, about `1.32502933987391672344507453423e-25`.

Outward displayed intervals:

    tau_T_full in [5.947279908386803e-15,5.947279908651810e-15]
    tau_T_full-tau_T_initial in [1.238825929118346e-23,1.265326515917261e-23] > 0

The surrogate center is unchanged; full-minus-surrogate sign is not determined. No measured error reduction or runtime speedup follows from this certified-radius reduction.

## Covariant/clock boundary

Signature (-,+,+,+), u.u=-1, J^a=c(N_e/V)u^a. For dx^a=c k^a ds, D=-u.k>0, `d tau/ds=c sigma_T(N_e/V)D`. The same u,V,k are required for scalar transfer. A nonzero spatial electron flux stays in `-sigma_T k_a j^a`. Different clocks, volume, escaped energy, external power or shear work cannot be silently discarded. Constants c,hbar,k_B retain physical units.

The projected identity of the old and expanded stopping surrogates is a different statement from the bounded difference between the full model and either surrogate. Their root IVP closes only under the actual source's U-independent root rates and active-path cutoff assumptions.

## Evidence status and next selected work

Original R6: 98 exact/source checks, including 46 parent identity checks; two actual cloud Wolfram calls; 11 zero xTensor groups. The original Limit warnings and version-context metadata issue are preserved. Same assistant, separate arithmetic/CAS paths; external independent scientific review not performed. No ODE, full generator or native-science run.

Actual immutable `NEXT_ACTION.json` selects R7. Continue source-bound current/opacity consumption and clock/geometry discrimination, not a repeat of unchanged R6 CAS. Source-owner `NT_GEOMETRY_TEMPORAL_BINDING` and HE native/RUX/all-Bianchi/D2.3 obligations retain their owners. Any R7 result will be recorded separately; this preservation commit does not declare R7 complete.
