# Reproduce ANGTHERM02

Use Python3 with existing NumPy, SciPy and Matplotlib. No installation is needed.
Keep the checkpoint intact and reproduce in a separate empty directory containing
code/, inputs/, and THEORY_CONTRACT.md. The exact donor bytes must be at sibling
../rei_angular_thermochemistry_20261023 or packaged
donor/rei_angular_thermochemistry_20261023. The prepared archive references the
immutable prior backup and is not a complete binary reproduction claim.

Commands in an empty reproduction directory:

    python code/bounded.py preflight preflight.py
    python code/bounded.py chemistry run_cases.py 1 2 3 4 5 6 7 8
    python code/bounded.py bootstrap run_cases.py 9 10
    python code/bounded.py analysis analyze.py

Resource accounting is results/cost_receipts.json, at most120CPU/180wall,
per invocation at most60CPU/90wall, 1GiB and one thread. Existing partial/completed
cases are rejected. Preserve a failed case; diagnose before an authorized repair.
The archived execution receipts contain historical charges, so a fresh separate
reproduction starts with a new empty results directory rather than modifying
those receipts.

Driver NPZ contains original accepted-node logT/logv, physical-RHS slopes,
initial Li fractions/optical depths, and high-bin log counts. Hermite primary
and PCHIP secondary are explicit prescribed bath models. Case NPZ retains both
reported and accepted states. Old donor comparisons use exact matching report
times. No original coupled IVP is repeated. Scientific admission belongs to the
controller and independent reviewer; finite GL differences are not certified
asymptotic convergence orders.

