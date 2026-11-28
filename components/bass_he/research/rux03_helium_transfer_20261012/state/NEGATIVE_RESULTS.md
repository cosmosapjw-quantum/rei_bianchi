# NEGATIVE_RESULTS

1. First Wolfram expression failed to parse because of an extra bracket. Full first input/output and corrected successful invocation are in evidence/WOLFRAM_CHECKS.json. No successful physics result was inferred from the failed response.
2. Initial candidate inspection found base_dataset and extended_dataset differ in energy band, node count, and HeIII initial fraction. Selected extended before executing the new screening. No narrow-band result was generated and relabelled.
3. GM25 at 50000 K is outside its declared 200..10000 K domain. The actual provider rejected that probe; no extrapolation, clamping or source substitution was made.
4. A first Dropbox source-download attempt failed on proxy/connect timeout. No archive bytes were accepted. Existing same-identity Drive archive was then used. This affected recovery only.
5. No native compiler was available for a new Rust build in the bounded analysis environment. New screening is explicitly a SHA-pinned Python transcription plus Decimal80 arithmetic check. Native parity remains NOT_RUN.
6. Reviewer requested three substantive precision edits before final closure: species-specific thick limit p_s; RR/DR notation separation; joint emission-time/energy/direction domain for global energy-measure bounds. All were incorporated before final hash-bound review.
7. RCT scalar rate does not supply photon spectrum, mean energy, heat/recoil moment or source uncertainty. Q reference is an internal energy difference, not a mean photon energy prescription.
8. Frozen response does not establish evolving Bianchi transport or a continuum bound. Near-threshold redshift can alter actual photon support.
9. P03A packaging mismatch was resolved as the documented docstring delta; P01 fresh-build identity and P02A cold-history admission remain distinct. Historical scientific ceilings are preserved.

10. Final independent review corrected one report route sentence: selected PR96 native main.rs::rhs/ft03_rhs with custom node PI is distinguished from the coexisting coupled_primary alternative. Source-owner JSONs were already correct; no scientific values changed.
