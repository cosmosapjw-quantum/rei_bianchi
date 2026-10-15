# REI Sigma-pi initial-condition response

Selected constructive theory plus direct coding follow-on to REI PR145 (git SHA 54e29dff...). The original full-source baseline and 312238-row original H/He donor are retained by SHA, not recopied.

Run under REI repository root with original source and the original ZERO HHe composed donor available:
python3 research/rei_sigma_pi_response_20261015/response.py --owner /path/to/original/rei_bianchi --output /tmp/new_response.json
python3 research/rei_sigma_pi_response_20261015/degeneracy.py --owner /path/to/original/rei_bianchi --output /tmp/new_degeneracy.json
python3 -m unittest discover -s research/rei_sigma_pi_response_20261015 -p test_response.py -v
python3 research/rei_sigma_pi_response_20261015/parallel_bench.py --out /tmp/new_parallel.json

Four independent IC q,kappa_gamma,kappa_nu,A_massive. Distinct q and kappa_gamma produce equal late signed shear within 7e-17 but gamma E2 differs by 0.00646. Original gamma/nu/massive collisionless/one-way Thomson source model only; no stellar-energy reservoir or observational covariance. Mathematical and actual runtime derivation in REPORT_KO.md.
