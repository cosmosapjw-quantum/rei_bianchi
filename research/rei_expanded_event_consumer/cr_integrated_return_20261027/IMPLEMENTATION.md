# C1–C5 implementation record (pending execution and scientific admission)

## C1 — Exact input interface and ownership

Base ee6746ab172f862dddfdec63b59e5e3707b59eaa; owned unit only. The CR exporter and its actual 24-event JSON are copied byte for byte, with admission/review evidence. Legacy source_commit b11b2e9255f2b10fb5582376412e045bd1e9151c remains unchanged; actual export-containing source is 4e72c89b714431eb4c6ae07def777bbf72a5ae4c and delivery ec463db0c7e5c7fb5070796071c926caa4db6445. The JSON is never resampled, reconstructed, or summed across alternatives. Native atomic source, species model, and coefficient JSON are copied as data-only identity inputs. No native module is executed. Only unchanged CR validate_event and its pure validation helpers may execute.

## C2 — Map and general interface tangent

A=Ncap, K=-fast_kinetic, and G=radiation are read in existing SI units. The supplied G and every reservoir remain in the raw event. Positive explicit consumer b gives a=A/b, k=K/b, gamma=G/b. Native indices 11,12,21,22 receive a,-a,-a,-k; the separate photon port receives a,gamma. All other native entries, including external-energy index23 and logT24, stay exactly zero. The flattened27 diagnostic appends photon count/energy at25/26; it is not an ODE state. The production reader without b retains proper-volume data and a null projection.

The JVP uses dA/b-A*db/b² and corresponding K,G formulas. Directions are independent signed finite interface directions; positivity constrains base moments only. The conservative tangent dG=dK+I*dA is selected only in the declared check. General incompatible directions return the nonzero energy-constraint derivative. This is the root clarification of the existing contract, not a model change. Binding plus fast plus retained energy is (-I*A-K+G)/b; source residual tolerance is2e-13, new algebra tolerance2e-14 with sums of absolute physical operands and no max(1,tiny) floor.

## C3 — Reference, clock, and endpoint algebra

Reference density rows multiply by beta, with tangent beta*dDelta+dbeta*Delta. logT passes through. Consistency uses b=beta*r and db=beta*dr+r*dbeta, with beta1.7 and dbeta=-.09beta. Integrated proper/eta packets are identical and d/dH=0. No H or exposure divisor is inserted. The existing continuous reference/RHS convention remains inherited and untouched.

The separate fixed-volume endpoint utility computes (rminus*xminus+Delta_n)/rplus and its full quotient tangent, including drplus. Only manufactured endpoint controls use it. logT and its tangent pass through. It does not claim an expansion trajectory or any physical time history.

## C4 — Controls, capacity, and algorithm

Each actual alternative is checked separately with Decimal precision50 explicit row quotients, the declared mixed direction, and centered FD h2e-4 and1e-4. The FD denominator is frozen from analytic value and tangent operands at the baseline; no convergence-order claim follows. Independent direct physical/r quotients and Decimal endpoint formulas check reference transformations.

Capacity smax=min(nHeIII/A,Nfast/A,Ufast/K), with zero-denominator bounds serialized null, is only a manufactured candidate certificate. Frozen capacities are1e4m^-3,1m^-3,100eV_J. Controls use s0,.25smax,smax,1.01smax. Endpoint uses .25smax and ds=.17s; no actual state is changed. Invalid b (including bool), missing directional b, frame, qualification/channel/support, duplicate event, alternative accumulation, negative or wrong-sign energy, nonfinite tangent, fabricated rate/exposure/RHS/history/spectrum/heating, zero moment/amplitude, and zero capacity are explicit controls. Exact zero native rows include neutron0 and tritium5/6.

Mutations have row-unit signatures: drop fast count, duplicate retained G into wext, thermalize K, omit db, omit dbeta, divide by H, omit endpoint drplus, and rebase the nonzero endpoint logT. The logT increment is identically zero, so it is not used as a mutation discriminator.

Work is O(24*27) with standard-library floats and Decimal; no integration, source generation, IVP, quadrature, old suite, new83, NCP, or replay is called.

## C5 — Execution package and stopping rule

Run command after root review: `python -B implementation/run_bounded.py` from this unit. EXECUTION_GO.json must contain authorization ROOT_C5_REVIEW_GO, exact PREEXEC_MANIFEST SHA256, authoritative prior_planning_known_CPU_s, and authorized_reserve_CPU_s .90. The runner refuses a preexisting attempt01 or cumulative prior+.90 above14.9. It freezes single-worker environment,512MiB address space, child .75CPU, wrapper .10CPU, wall8s, and .05CPU receipt-tail reserve. It preserves raw stdout, stderr, incremental CHECKS.jsonl and OBSERVATIONS.jsonl, all24 maps in JSON/Markdown, and resource receipt. Any failure is fail-fast with no automatic rerun. Actual measured child+wrapper plus tail is added to the supplied cumulative prior; unknown historical/remote/LLM cost stays UNKNOWN_NOT_ZERO. Main595.225063/600 NO_MORE_IVPs and every foreign owner budget are unchanged.

Preparation and run permission are separate. No scientific run has been performed during authoring; admission is pending root and independent Astra review. No figure or publication is performed by these files.
