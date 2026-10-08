# Decision log

Decision: `MANUFACTURED_MODEL_DISCRETE_REFINEMENT_PASS_0P0008__CONTINUUM_HOLD`.

The k17 failure was caused by a scalar transport boundary: the checkpoint retained finite canonical N/U and loss while the next characteristic consumed binary64 zero. The repair passes the canonical stock into the positive linear characteristic, carries it through each segment, and binds scalar fields only at compatibility readout boundaries. The saved energy mismatch is retained as loss. No floor, tail deletion, tolerance increase, source/provider substitution or completed-prefix rerun was used.

At the completed 0.0008 horizon, coarse/fine/tail states satisfy the unchanged 37-field, source N/E and representation-budget tests. This supports the discrete manufactured-model refinement claim for that horizon only.

Do not promote this result to z=12 to 10 completion, continuum validation or physical admission. Spectral reconstruction, source integration, time-residual/Jacobian propagation, historical-prefix/kernel/provider authority and joint nonlinear remainder remain incomplete. REC Gate I and matched evolution remain HOLD; BASS outside-window optical depth remains UNKNOWN.
