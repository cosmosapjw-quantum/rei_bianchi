# HE38 coding contract

Workflow1.0.0 / approval0.2. New code is a bounded sandbox component, not a replacement of completed HE32–HE37 executions. Author: ChatGPT research team.

## Inputs and identity

Production masses are CODATA2022 electron/proton masses; m_H=m_p+m_e. Temperature is scalar or1D within2000..200000K. The energy convention is relative-COM E=μg0²/2; I=13.6eV and original-Jacobi uniform G are explicit. A new identity includes this scope and the exact reused provider hash. Artificial ion masses are confined to labelled event-kinematics controls.

The local instantaneous API takes nonnegative n_e,n_H and independent symmetric traceless π_e,π_H in Pa. Absent species require their own stress exactly zero. Tensors are validated without renormalization, clipping or projection. Inputs reject mixed bool, non-real, nonfinite and wrong-shape values. Nonzero numerical underflow/overflow is not converted to physical zero. Outputs are immutable.

## Outputs and ownership

Species order is electron,H0,proton; input STF columns are electron,H0. Moment coefficients carry no density; STF column0 multiplies n_Hπ_e and column1 multiplies n_eπ_H. Number increments are(+1,−1,+1)r. Heat and STF units are Pa/s. Each species S=J+(2Q/3)Id; direct totalQ/J and direct heavy-combinedQ are authoritative at small scales.

Pure-H21 uses H0 slot1 and H+ slot2, other slots zero, Y_H+Y_p=1, n_e=n_B Y_p. The physical fixed-T,n_B abundance Jacobian includes this n_e(Y) dependence. Its ambient extension is used only along the normalized pure-H tangent; the donor frozen-ne Jacobian is separately labelled. Temperature and stress derivatives are not silently included.

The HE36/REI event lift is byte-preserved. Q, summed species heat and reservoir dEth are one owner and must not be added. Explicit all-retained thermal inventory permits the conditional reaction contribution dotT=−(r/n_part)(T+2I/(3k_B)); this does not demonstrate rapid thermalization. Scientific STF consumers use wrapper.J or species.total_J_Pa_s. Nested donor event_tensor_source is audit evidence; its legacy trace-projected J can lose tiny STF by cancellation.

## Execution and acceptance

No old IVP, old diagnostic, old suite or old benchmark script is replayed. The unchanged provider arithmetic may be called by the new finite-mass component; those calls are new dependency evaluations, not a rerun of the old workload. Parent saved129T rows are reused with exact identity as a comparison baseline. New affected controls, an independent full-source quadrature, one129T finite-mass diagnostic, one sharing-compression cost comparison and one actual PNG/SVG figure pair are bounded and have attempt receipts. Numerical error is separated from model uncertainty. No coupled IVP is scheduled.

Original independent-control/diagnostic budgets are30 CPU seconds each and512MiB target; actual attempt resources are recorded, including any charged failure. No fast-math, silent reduced grid, unrecorded repeat, or fabricated certificate is permitted. Binary64 Python/NumPy/SciPy is selected for this small O(N_T) closed expression. Native Fortran/OpenMP/MPI is activated only if a remaining measured bottleneck justifies it for the same workload.
