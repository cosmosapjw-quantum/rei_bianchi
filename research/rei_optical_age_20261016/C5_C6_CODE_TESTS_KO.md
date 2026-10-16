# C5–C6: exact positive optical-age oracle and 21 sandbox regressions

Continue R5 (Git commit `6c0894b1a41332d5d4f35ac94dc4607e878bc40e`) without changing original PR171/production. The complete **actually sandbox-executed** `src/optical_age.py`, `tests/test_optical_age.py`, two runnable study scripts and Korean theory/handoff are in the independently RESTORED source capsule:

- [Source-only v2, Google Drive](https://drive.google.com/file/d/1l8_dqZ3gXTdH0CeQwTubz2sLsXjzI-w3/view); **23,280 bytes**, SHA256 `53cd6f16aa01c09799fb9e242eb4021bb537dabc7225fd54dacabe9971888004`.
- Identical second ChatGPT Library backup; independently downloaded and **21/21 tests + full numerical/figure replay exit 0** from each source-only copy. GitHub contains this *publication index* and scientific acceptance; the complete tested source bytes are in the linked restorable source ZIP, **not copied as native executable source into the original Rust tree**.
- [C5/C6 standalone backup](https://drive.google.com/file/d/1P-THX1w5PPwM6ED_k8XDSmGz1wANA7_N/view); **16,231 bytes**, SHA256 `94df15998508f907c0dac78ff8182dba7aaa37557f73d64f93ca88e9b52d3904`, full source+failure logs+CRC/hash manifest. Library second full-byte readback PASS.

### Implemented physics/numerics

- Positive `N'=j(u)-κ(u)N` manufactured reference, with **time-varying** HI κ and HeI κ active until exact fit crossing.
- Exact affine integrated `K(u)`, cancellation-resistant inverse mapping, Gauss–Legendre for `0≤z≤K(u_cut)` and shifted positive Gauss–Laguerre for higher depth.
- Source-conserving φ1 slab comparison and uncorrected uniform midpoint birth comparison.
- Signed exact LRS Killing photon geometry, separate HeI fit `24.59 eV` and binding `24.587389011 eV`; all rates and j are prescribed toy arrays, not actual native Verner fits.
- Independent `scipy.integrate.quad` and Radau reference integrates photon number, HI/HeI absorption, thermal/photoheat, binding, geometric work, emitted N/U and positive age moment. HeII structural zero at energy less than its 54.42 eV threshold.
- **21/21 Python unittest PASS, exit 0**. Initial 19 PASS/2 FAIL were *test-only* faulty domain fixture and cancellation-prone finite-difference derivative control, repaired with source physics unchanged and independent complex-step derivative; initial failure preserved, no tolerance relaxation.
- **native Rust/NCP execution in this stage NOT_RUN; original Grackle coupled accuracy NOT_ADMITTED.** Host-native subagent not available, NOT_RUN.

To replay without any user manual source preparation, authorized Codex downloads the complete C10 or source-only v2 archive through connected Drive, checks SHA256, extracts in isolated directory and executes `bash verify.sh`. No original PR150 checkpoint or long history restart.

**DAG C5=IMPLEMENTED, C6=21/21 PASS, C7/C8=next numeric cross-solution comparison.**
