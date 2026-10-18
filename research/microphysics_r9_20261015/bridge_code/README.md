# R9 bounded bridge

First run: `python3 bridge_driver.py --r8 ../vendor_r8 --photo ../photo.dat --out ../bridge_tests/desktop_run`.
Later standalone runs use staged input bytes in `inputs/`: `python3 bridge_driver.py --out RESULTS`.
Verify: `python3 ../bridge_tests/check_bridge.py RESULTS`.

Only Python standard library, C11 compiler, and libm are required. The driver implements frozen CONTRACT_BRIDGE: 17-state inventory with a conserved excluded-nucleus reservoir, statistical shell E1 line spectra with metastable2s energy retained, BB50K source and independent normalized LiI spectral photo-response, and historical np thermal-anchor sensitivity. Source photon birth emissivity is distinct from the prescribed incident flux. No fitted posterior, intermediate cosmic history, synthetic2s photon spectrum, or global eight-job closure is claimed.

This copy was reconstructed after the original scratch exec-server outage. The original run had149/151 checks passing; only covered LiI photo1024vs2048 adjacent convergence failed (Gamma6.29064911272792e-10, heating8.114382499257999e-10). The root authorized a4096-panel photo refinement with unchanged physics. The current raw refinement ladder preserves those failed lower resolutions. Source moments remain2048 panels;16384 is an additional reference check.

All output residuals are measured floating-point arithmetic. A printed zero residual can reflect cancellation; it is not proof of exact physical closure. Zero charge populations follow explicitly selected zero probabilities. Missing physical histories and spectra remain null.
