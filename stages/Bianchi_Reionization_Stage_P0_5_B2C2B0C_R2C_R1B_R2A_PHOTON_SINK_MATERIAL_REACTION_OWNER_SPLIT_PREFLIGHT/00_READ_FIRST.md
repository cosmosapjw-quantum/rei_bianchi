# R1B-R2A owner-split preflight — read first

This bounded stage starts from `452e8272739ee08f7feb5eec350cfc6be8cf5b3f` and does **not** inherit the invalid first R1B-R2 full run as evidence.

The target is to split ionizing-photon removal by physical owner before any material or thermal update. `EFFECTIVE_HI_SUBGRID` removes photons but has exactly zero resolved H, He, and resolved-thermal source unless a separately locked subgrid reservoir and exchange law exists.

No clipping, cloud-mass inversion, geometry inversion, owner reassignment, or post-hoc lane selection is permitted.
