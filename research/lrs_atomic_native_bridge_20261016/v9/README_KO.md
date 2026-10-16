# REI LRS V9: Photon-birth and opacity clock factorial control

Parent: [rei_bianchi PR #168](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/168), exact commit `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b`. This project is an independent smooth 0D photon/H I source–absorption diagnostic and **does not modify PR #150, PR #168, original user Ubuntu or NCP**. Native agent: NOT_RUN.

Physics: time X=ln(a/a0), photon count N, neutral H I target M, ionized I and new photon births B, all per **total H nuclei**. Mass action N'=S(X)-lambda(X) N M, M'=-lambda N M, I'=+lambda N M. Frozen photon energy 80 eV, event binding 13.6 eV and heat 66.4 eV. No spectral/redshift dynamics or real H/He stellar sources. Tested algorithms include midpoint exponential/pair reaction, independently lagged source/opacity, all births at start, and BE chemistry.

## Execute

    bash REPLAY_V9.sh

Requires Python 3.11+ with numpy, scipy and pytest. The driver runs 61 tests then records `evidence/convergence.json`, `evidence/convergence.csv`, `evidence/study_stdout.txt` (five problems x six methods x six resolutions = 180 rows). Measured Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pytest 9.0.2.

## Scientific result

Dynamic HI feedback representative case N256 absolute photon error vs independent Radau: midpoint 4.087e-7, source_left 1.961e-4, opacity_left 1.359e-4, both_left 6.072e-5, all births at start 4.308e-4, BE 5.437e-4. Corresponding last orders: 2.000, 0.997, 1.005, .989, .998, .998. A genuine proportional-source/opacity *exact subcase* was discovered after the first incorrect test assumption, then specifically tested without numerical tolerance relaxation.

GitHub stage checkpoints: `stages/R5_THEORY_KO.md`, `DAG_R5/C5/C6/C8/FINAL.json` and `stages/C8_RESULT_KO.md`. Cloud Drive raw file upload failed with `container_session_expired` even after one diagnostic attempt; stage R5/C5/C6/C8 were separately backed up as Drive **native Docs readable text mirrors** and source blob IDs read back, not as raw file archives. Dropbox connector direct raw upload was unavailable. Generated sandbox ZIP is a fresh-restorable complete raw archive for user/Codex; use Codex to upload to both providers with raw readback if desired.

Scientific admission: R5 local Taylor defects DERIVED_WOLFRAM_CHECKED, C5/C6 code source Git-blob byte checked, C8 conditional smooth manufactured PASS, original native PR150 source-on error decomposition HOLD, real H/He Case A source events and moving spectral cuts NOT_ATTEMPTED. No astrophysical reionization claims.
