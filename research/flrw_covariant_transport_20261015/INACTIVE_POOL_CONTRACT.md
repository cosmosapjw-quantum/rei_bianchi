# Explicit FLRW HI cut-cell variant

This contract extends the published covariant N/U/support method at
`a71052cec02c48c08d6823e00331fab1db654a76`. It does not rewrite the retained
inert-photon baseline or its first capped pilot. The selected variant is
`inactive_hi_split=true`; its default remains false. Activation is restricted
to q_ref=0 and forward, non-increasing ray energy scales. General anisotropic
or blueshifting activation is a separate future contract.

The HI photo fit vanishes below13.6 eV. In the declared expanding FLRW
background, a photon below that cutoff cannot become ionizing again. At each
geometry endpoint, restrict the existing positive reconstructed spectrum to
the two sides of q_cut=13.6/R. Keep the above-cut N/Uq/support as active; move
the below-cut count and reference first moment into passive arrays indexed by
the SAME q cell and ray. Both arrays start at zero for a fresh source history.
A source-free delta at the cutoff is active; an actually subthreshold delta is
passive. No physical or tabulated threshold changes.

This restriction is a declared spectral closure operation, not recovery of
an unknown true spectrum. The restriction of a bounded exponential to an
interval belongs to the same family. Use the existing positive moment-matched
quadrature and retain its64eps count/128eps first-moment checks. No clipping,
negative weights, or arbitrary broad-support delta fallback is allowed.

The driver owns six arrays: active N/Uq/support_lo/support_hi and passive
N/Uq. Passive moments retain nonnegative counts and valid q-cell first moments;
their physical support is enclosed by the cell lower edge and the current HI
cut, intersected with the upper edge. In false mode passive arrays must remain
zero. Chemistry, source injection and Gamma operate on active photons only.
The original coupled cold Newton stage remains the only photo-event owner.

Geometry work is calculated using TOTAL active+passive physical energy before
and after redshift. Pool transfer itself changes neither N nor Uq. Passive
photons continue to redshift and contribute to total photon moments/stress;
they are not discarded into an exit ledger. Existing boundary outflow stays
zero in this variant. Gas expansion, source, escape and CMB owners are unchanged.

Time adaptivity uses, per corresponding q cell and ray,
abs(delta active N)+abs(delta passive N), and the analogous sum for Uq times R.
Normalize by the original TOTAL photon N/U with the original floors. This is
at least as discriminating as the old combined-cell norm, up to ordinary
binary64 summation roundoff. Keep the original gas/thermal terms, local1e-5
target, strict<2e-4 ceiling, Newton1e-11, step1e-10/cumulative1e-8 ledgers and
parity1e-12. Removing passive photons from the denominator or error accounting
is not permitted.

Use checkpoint V4 with all six arrays. Outer run exact source/config binding
is authoritative; old V3 runs are not resumed under this changed source.
History remains25 columns and spectrum12 columns. Spectrum N/U are TOTAL
cell moments, with the union of active support and the conservative passive
envelope, explicitly labelled as bounds rather than a recovered density.
Export active/passive N/U totals as four VALUE ledger records. Gamma is active
only; photon stress is from both pools. Record the representation and pool
meaning in metadata.

The pre-implementation control compared the same preserved12000-step state,
after one common partition, at h,h/2,h/4. The preselected launch criterion was
both combined-cell and stronger split-pool errors <= one fifth of the existing
baseline error at h, with original physical invariants maintained. Its observed
~14.97-fold discrepancy reduction supports implementation; it is not a measured
runtime speedup, global convergence certificate or full-history admission.

After focused driver tests and independent changed-surface review, run fresh
short FLRW pilots on the actual NCP. Reuse the original z20→19.8 q128/256/512,
time1e-5/2.5e-6 and angle8/16 screen, numerical criteria and finite per-case
budgets; set only the explicit new variant flag. Start q128 alone, then at most
two cases concurrently after its completion. Keep first failures, cumulative
costs, source/config identities and durable checkpoints. A complete reviewed
screen opens the already-authorized fresh full NCP campaign. A capped pilot
remains incomplete and requires a diagnosed, finite next action.
