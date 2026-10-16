# Lane C execution (independent scientific review pending)

`code/laneC/run_spectrum.py` consumes the actual saved lane-B raw F and kinetic derivative. A prefix-summed piecewise-linear-in-z F interpolant provides conservative exact cell moments and O(log N) boundary lookups. Rate-derived differential spectra and physical source rates use the independent derivative columns. Direct donor Li7 is excluded. The donor per-H/per-baryon normalization identity is checked numerically with the frozen YH.

Commands:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests/laneC -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/laneC/run_spectrum.py > code/laneC/raw/run_stdout.json 2> code/laneC/raw/run_stderr.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/laneC/plot_saved_results.py
```

Requested executor gpt-6.1-sol, observed UNKNOWN; Python 3.12.14, NumPy 2.3.5, Matplotlib 3.10.8. C numerical time 0.12968888 s; combined final C tests/run/summary process took 0.40414536 s. Plot-only successful time 1.2526006 s, plus initial failed plotting process 0.551907094 s. Plotting reads saved evidence and performs no kinetic run.

All frozen C checks pass. Total present number density 9.383793856e-17 cm^-3, energy density 2.58266097264e-15 eV cm^-3, combined mean 27.52256723 eV. Ground/excited dn/dE modes are 29.74984389/13.26281042 eV; FWHM 2.324459949/1.03627003 eV. Peak interpolation and all conditional-statistic denominators are explicitly recorded in JSON. Independent kinetic-Jacobian M0/M1 discrepancies are approximately 0.00104154/0.00104318, below 0.003; these retain the native-grid endpoint-phase effect and are not forced to vanish. Cropped [12,35] eV and full [0,100] eV below/inside/above closures, moments and analytic toy results are stored.

Three C unit tests passed before export. The initial empty [0,0] energy-bin test emitted a temporary-denominator overflow warning (all assertions passed); before export, its prescribed zero-energy limit was implemented with masked division into explicit infinity. Warning and correction are retained in `code/laneC/raw/pre_execution_warning.txt`. The first plotting-only attempt failed due to NumPy field-name sanitation of unit headers; the reader now preserves headers verbatim. That failure is recorded in `code/laneC/raw/plot_first_failure.txt`; no physical calculation was repeated or changed.

This result applies the paper's literal 0.896/0.104 branches and rounded line energies within the specified FLRW trace-kinetic trajectory. It sums propagated flavors in the freely streaming ultrarelativistic approximation. Source gamma and approximate initial recoil energies are separate diagnostics, with no deposited heat, exact Q closure, present electron-flavor, neutrino mass or late-time claim. Raw 1-F_end is a floating closure residue, separately distinguished from underflowed propagated a+b; it is not claimed as a present neutrino tail. The two-panel PNG/PDF carries these qualifiers and has been visually inspected. Numerical PASS remains subject to independent scientific review.
