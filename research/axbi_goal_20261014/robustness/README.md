# Source and IC sensitivity reduction

`compare_variants.py` delegates the same completed-history ZBAR convention and source identities as the convergence reducer:

    python3 research/axbi_goal_20261014/robustness/compare_variants.py --kind SOURCE --manifest INPUT.json --output research/axbi_goal_20261014/robustness/NEW_RESULT

Use `--kind IC` for the IC case. Manifest shape is in `../convergence/README.md`; supply an `assumption_reference` to the frozen scenario/variant choice. SOURCE permits escape_fraction to change; IC permits initial_temperature_k to change. Other physical/numerical inputs, including q_ref, must match; resource/output bookkeeping may differ. The frozen minimum is FESC_025_ZERO and TGAS20K_ZERO versus baseline ZERO. These are named baseline-model sensitivities, not posterior uncertainty or evidence of robustness of signed-shear response. Missing/incomplete inputs are typed unknown, not zero effects. No variants were run or actually reduced here.
