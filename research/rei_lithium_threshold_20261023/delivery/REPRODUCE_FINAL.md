# Reproduce the final ANGTHERM02 checkpoint

This delivery supplement gives the exact archive layout and fresh-output
location for the FINAL archive. The existing top-level REPRODUCE.md describes
the model and commands; use the concrete layout below with that document.

## Extracted evidence root

Extract REI_ANGTHERM02_FINAL_20261023.zip into an empty directory, for example
ang02_evidence/. Its research unit is then:

    ang02_evidence/research/rei_lithium_threshold_20261023/

That directory contains code/, inputs/, results/, figures/, sources/, delivery/,
the final scientific documents, and donor/rei_angular_thermochemistry_20261023/.
The archive also contains AGENTS.md at its top level. The embedded donor path is
the fallback explicitly implemented in code/trace_model.py. No sibling donor
checkout or separate prior archive is needed for this unit's runtime inputs.

## Preserve recorded results and use a fresh run directory

The archived results/ is completed evidence. Do not run into it: the launcher
correctly refuses to replay completed/partial cases and its receipt contains
the historical charged costs. The implementation uses BASE/results, so a
separate fresh copy of the runtime inputs defines the separate output path.

From the directory containing ang02_evidence/, create ang02_rerun/ with no
results directory, then copy these items from the extracted research unit:

    code/
    inputs/
    donor/
    THEORY_CONTRACT.md

For example, using a shell from that parent directory:

    mkdir ang02_rerun
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/code ang02_rerun/
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/inputs ang02_rerun/
    cp -R ang02_evidence/research/rei_lithium_threshold_20261023/donor ang02_rerun/
    cp ang02_evidence/research/rei_lithium_threshold_20261023/THEORY_CONTRACT.md ang02_rerun/
    cd ang02_rerun

Only an independently authorized reproduction should execute:

    python code/bounded.py preflight preflight.py
    python code/bounded.py chemistry run_cases.py 1 2 3 4 5 6 7 8
    python code/bounded.py bootstrap run_cases.py 9 10
    python code/bounded.py analysis analyze.py

The fresh output paths are ang02_rerun/results/ and ang02_rerun/figures/.
Use Python 3 with NumPy, SciPy and Matplotlib. Observed module and Python versions
are recorded in delivery/RUNTIME_VERSIONS.json. Runtime packages are not bundled.
No dependency installation, original full gas/photon trajectory replay, or
driver regeneration is required. The retained bath_drivers.npz is an exact input
of this conditional experiment. build_drivers is available for diagnosis but is
not part of this reproduction recipe.

The archived cost receipts, driver manifest and final decision distinguish
known measured use, the conservative debit for a lost old failure, and separate
packaging costs. Numerical comparison uses the declared residuals/tolerances;
ZIP timestamps and recompressed NPZ bytes are packaging identities.
