# Descriptive endpoint analysis

These calculations use the existing 625 endpoint rows. They perform no ODE solves. The fit is empirical and supplies no certified interpolation bound.

The through-origin least-squares fit to signed final shear magnitude `sqrt(3)*s/H` is

`S_end = 0.114380200092 * signed_Sigma0 + 0.24184661411 * signed_Pi0`.

The maximum absolute residual is 3.70652503568e-07 and the RMS residual is 1.23096522998e-07. Relative to the global maximum |S_end|=0.000699738066981, these are 0.000529701785651 and 0.000175918002474. The fitted opposite-sign cancellation ratio Sigma0/Pi0 is B/A=2.11440978347.

Centered near-origin slopes on the smallest nonzero axis values are A=0.114379995242 and B=0.241846078559. One-sided slopes and all four corners plus largest axis controls are preserved in analysis.json.

The smallest nonzero-input grid endpoint Sigma is 2.17726489159e-06, at signed Sigma0=0.000333333333333, signed Pi0=-0.000166666666667 (s01_+1_p02_-1). This is a discrete-grid minimum, not a continuous cancellation solution.

The maximum simultaneous-sign-reversal magnitude difference is 7.38403743945e-07, or 0.00105525735813 of the global maximum endpoint magnitude. The corresponding pair is recorded in analysis.json; the data do not establish exact simultaneous-sign symmetry.
