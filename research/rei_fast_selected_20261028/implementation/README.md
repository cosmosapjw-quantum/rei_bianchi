# Saved-history selected-state projection

`project_saved.py` reads the preserved, receipt-pinned ANGTHERM01 default `grid044_M4_nominal.npz` history and pinned isotope registry. It does not solve any ODE. It writes a 201-row CSV with all 21 source populations both per Href and per baryon, using the constant source `n_b/n_Href` reference, and a seven-panel PNG showing the requested **17** states after the owner's Li IV correction. The seven nuclides are n, H1, D, T, He3, He4, Li7. Li6 I–IV remain hidden dynamical closure. n and T are explicitly source-zero, not fabricated log-scale curves. The native clock is `eta=ln(a/a_i)`, with source mean-scale-factor `z=21 exp(-eta)-1`, spanning z=20 to 2. The separately saved tight case can be selected explicitly for a bounded comparison, not substituted silently for the default.

The source ZIP was recovered intact into `../inputs/REI_ANGTHERM01_FINAL_20261023_46519489c540.zip`, SHA256 `46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036`. Narrowly extracted sources are in `../inputs/angtherm_selected/`. At run time, the reader verifies archive, receipt, source registry, NPZ and paired case JSON bytes; the registry is parsed as a literal rather than imported. All 21 states contribute to the baryon reference. Li IV is included as the seventeenth display curve without renormalizing the others.

The saved result is conditional atomic thermochemistry with shared isotope electronic rates and initial charge fractions, a prescribed six-bin initial UV inventory, and a prescribed anisotropic background. It is not a new BBN nuclear-production calculation, stellar-emissivity history, or Einstein feedback. Source case scientific admission is scoped in its `SCIENTIFIC_DECISION.md`. New projection/figure checks remain **NOT_RUN** under the closed planning/presentation allowances.

After the controller explicitly reopens a bounded presentation allowance, one possible single-attempt command is:

```bash
python research/rei_fast_selected_20261028/implementation/run_bounded.py
```

For a separately authorized bounded planning check, use `python research/rei_fast_selected_20261028/implementation/run_bounded.py --tests-only`.

The wrapper selects the saved nominal case once, with child CPU≤3 s, wall≤30 s, address space≤3 GiB. A separate `--tests-only` mode runs the targeted unittest discovery with child CPU≤1 s, wall≤10 s, address space≤3 GiB. Each mode has its own start marker, stdout/stderr and resource receipt; neither mode retries automatically. Wrapper CPU after startup is also measured; import/startup and other unknown cost are not claimed to be zero. Source recovery and this code preparation did not consume the main IVP ledger. No scientific acceptance or rendered figure is claimed before these bounded steps run and are reviewed.
