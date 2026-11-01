# Source-correlated local map proof obligation and one bounded adversarial pass

Let \(X\) be the **actual** accepted tick160 H/He thermo/source parent set and \(\Theta\) original four-site uncertain source parameters. The quantity required for rigorous local-error admission is

\[
D_h(X,\Theta)=\{F_h(y,\theta)-F_{h/2}(F_{h/2}(y,\theta),\theta):(y,\theta)\in X\times\Theta\}.
\]

For \(H_h=F_{h/2}\circ F_{h/2}\), the same-parameter Jacobian obeys
\[
J_{D_h}=J_{F_h}-J_{F_{h/2}}(F_{h/2}(y,\theta),\theta)J_{F_{h/2}}(y,\theta),
\]
with a separate chain-rule term for common source \(\theta\), including both half-step source histories. A midpoint Jacobian is only suggestive without an interval enclosure of the difference and of the remainder. In particular, the original `sup_{a∈F_h(X),b∈H_h(X)}|a-b|` is sound but generally needlessly wide: for F=H=identity it equals diam(X), while true same-parent D=0.

## New experiment

For \(\alpha\in\{0.05,0.5,0.95\}\) choose \(\ell(\alpha)=\ell^-+\alpha(\ell^+-\ell^-)\) node by node, with a common original nuclei-conserving point population. Apply original F and original H to this one-dimensional *conditional* path, with source forcing drawn from original sealed model; no source law modification or exogenous averaging. The outputs are strictly **interval images even for a point parent** and their separate cross-box upper/lower distances are not D(X) certificates. The physical computed change of H/He ion fractions and U/H is meaningful only under this declared conditional parent selection.

## Blind-referee findings

1. **Source correlation (BLOCKS central admission):** distinct alpha paths are not proved jointly realizable states of the original full uncertain source/clock. Do not assert actual ensemble derivatives, prior or confidence distribution. Reconstructing H and He complements enforces nuclei but not all hidden source correlations.
2. **Interval endpoint dissociation (BLOCKS central admission):** original `run_step` uses interval arithmetic for source four-site, low-rank owner feedback, root enclosures. Even point parents result in nonzero output intervals. Center defects and independent-output gap are diagnostics; rigorous D_h requires a shared symbolic/automatic-differentiation representation and full remainder.
3. **Energy scope (NONBLOCKING within experiment):** derived `U/H` uses `(3/2) k_B T (1+y_He+x_e)` from midpoint outputs. It is neither full cosmological thermal/chemical/escaping photon global ledger nor point-state validated interval energy; original event source identities are separately zero-containing.
4. **Lane semantics (NONBLOCKING):** original accepted arrays have identical numeric columns, but lane forcing models may differ. Therefore each lane evaluated separately; never count labelled copies as independent observations.
5. **Operational risk (FAIL CLOSED):** missing archive, hash mismatch, original map false certificate, runtime limit, source table event, or failure on any λ yields a partial result plus typed failure, NOT a PASS and NOT a reason to relax threshold.

**One constructive stop:** If all point probes succeed, preserve and use the resulting sensitivity as a *candidate for joint derivative bound*, not a new recursive auditing campaign. If they fail, preserve exact failed phase and move directly to the original source-correlation proof or a source-qualified physical interval, rather than running unrelated atomic physics.
