# BASS_HE R10L handoff: external physical benchmark and dynamic support audit

Fresh-read PR15/PR17/root AGENTS.md.
Expected PR15 HEAD b8b2fe47a367459f6faf6796eb2f251feacbbd7c.
Expected R10K basis 4e7627b30f835dab81c487e7e8571dba51553dde.
Read R10K AUTHOR_REPRODUCTION_LANE_SPEC.json, DECISION.json, REPORT.md and this R10L DECISION/LITERATURE_NOTES. If identities differ, stop R10L_IDENTITY_MISMATCH.

Preserve lane A exactly as R10K locked. Do not refit or relabel it as physical validation.

Freeze external benchmark sources BEFORE calculating new model C:
1) Stolterfoht et al. PRA81 052704 (2010), DOI 10.1103/PhysRevA.81.052704. Use full PhysRevA.81.052704.pdf. Digitize Fig.8 at 0.5 and 5 keV/u for n=1,2,3. Record source identity, high-resolution private crop, axis calibration, at least two independent digitizations or equivalent calibration perturbations, central value and uncertainty. Do not publicly redistribute the full PDF.
2) Liu et al. PRA67 052705 (2003), DOI 10.1103/PhysRevA.67.052705. Retrieve n=2 at Ecm=0.4 and 4.0 keV. Prefer tabulated/source values; otherwise preserve digitization uncertainty.
3) Minami et al. JPB41 135201 (2008), DOI 10.1088/0953-4075/41/13/135201. Use tabulated state-selective values at 5 keV/u if accessible. Do not extrapolate to 0.5.

Freeze BENCHMARK_MANIFEST.json before new model C execution.

Precommit models:
A = R10K author reproduction control.
B = Nmax3, five branches, factor2, dynamic R10G Delta(rho), printed EXTENDED support, straight-line CPC rotation/cutoff, current m0 consumed-column semantics, existing numerical tolerances. Reuse exact existing B result if identity matches.
C = identical to B except support=rho<=Re(Rc). Dynamic Delta only. No frozen Delta, no author Coulomb rotation. No alpha interpolation.
Write MODEL_CONTRACT.json before benchmark comparison.

Execute C by reusing exact dynamic Delta/cache. REAL is a subset of EXTENDED. Do not solve outside the old domain. Use R10G endpoint/quadrature strategy with REAL boundaries explicit. If new rho coordinates are needed, hash query contract first and compute only those. Record reuse/new Delta counts. Never change tolerance from benchmark outcomes.

For every source/energy/shell report benchmark value+uncertainty and A/B/C, raw ratio and log(model/benchmark). Freeze raw table before any aggregate. If aggregate weights are later used, declare them first.

Allowed verdicts:
EXTENDED_SUPPORT_EXTERNALLY_SUPPORTED_IN_SCOPE
REAL_SUPPORT_EXTERNALLY_SUPPORTED_IN_SCOPE
PHYSICAL_SUPPORT_UNRESOLVED
SUPPORT_NOT_DOMINANT_EXTERNAL_DISCREPANCY

No verdict is a universal hidden-crossing theorem.

Non-scope: no support-radius fitting/alpha interpolation, no exponent/trajectory/cutoff changes during B/C comparison, no author FORTRAN, C_S_AT/MODKG, Nmax expansion, continuum, CODE-I02 rerun, 56-action/worker sweep, L2/Krawczyk, production change, merge or force-push.

Publish append-only on PR17. Return source identities, benchmark manifest, digitization evidence, model contract, reuse/new Delta counts, comparison table, physical-support verdict, limitations, backup receipts and next bounded prompt.

Keep CODE_I02_CLOSED=true, full_certificate_fail_closed=true, scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN.
