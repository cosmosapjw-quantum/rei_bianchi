# Source007 opt-in BASS provider port

Implements a narrow source006 driver seam for the exact selected 121-row COLD_FLRW and SIGNED_MINUS tables. Proper density remains nH0/a^3 and nHe0/a^3. Signed s/H is distinct from user Sigma and from the disabled analytic q_ref knob. Donor Hermite and GL8 clock formulas are unchanged. Strict table scale-domain checks and exact time endpoint lookup implement the frozen no-extrapolation/origin contract.

ResidualContext, Jacobian implementation and covariant transport source bytes remain unchanged. One Astra-approved accounting integration fix preserves started attempt/RHS debits on fixed-step failure. Geometry, clock, domain, signed work, one instantaneous energy owner, source-bound checkpoint/restart and source006 Jacobian compatibility are tested in one targeted target: 9 passed. The fixed-step component example builds successfully but has not been executed. Two of two build/test invocations were used; raw outputs and timings are retained.

Independent review found that the example serializes unmeasured adaptive fields as zero despite the NOT_RUN status. Component execution is held pending Astra authorization for a bounded serialization correction. No automatic third build or run is authorized. Current compiled source and binary identities refer to the observed pre-correction build.

No old matrix, old broad test suite, full NCP pilot or solver campaign was replayed. Full convergence remains HOLD and scientific admission is NOT_ISSUED.
