# REI F4: original BASS photon-budget-constrained 8-moment spectral cone

Scoped source-derived research only, **no IVP**. Parent PR270 HEAD `691560db50937dc7e3d33b0547a1ac637cba1e92`; independent PR271 and VigilODE PR118 are read-only context. Full 5–200 eV BASS source bin grid, seven frozen REI ON_refined z labels, P19 2019 six H/He rate-and-heat moments. Additional *hypothetical* constraint: preserve both source BASS total number flux and bin-centre photon-energy flux at each frozen z.

Run `bash VERIFY.sh` from an extracted copy. See `THEORY_KO.md`, `REPORT_KO.md`, `CONTRACT.json`, `RESULTS.json`, `MP75.json`, and `HANDOFF_NEXT_THREAD_KO.md`. Source embedded PR270 master ZIP unchanged. Never overwrite source, compute physical tau, run a new IVP, or promote F4 without a common owner source.
