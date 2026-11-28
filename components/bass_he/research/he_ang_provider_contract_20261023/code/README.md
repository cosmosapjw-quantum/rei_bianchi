# HE-ANG-CONTRACT: bounded exact event and metadata components

Version 0.1.0. workflow1.0.0 / approval0.2. Authoring task: C5 components plus affected controls. New implementation execution, test execution, IVP, provider scan, benchmark and X1/HE38 suite replay are all NOT_RUN/0 at author handoff. Root owns the frozen shared CPU <=10 s / wall <=30 s execution ledger, the independent review and subsequent publication.

## Files and entry points

The package uses Python >=3.10 and the standard library only. It has no installed-package, service, network, X1 or HE38 import dependency.

- heang_contract/exact_events.py: exact input validation, event integration, cross-section conversion, raw moment transformation and serialization.
- heang_contract/metadata.py: structural source/frame/preparation/domain/content precheck.
- heang_contract/cli.py and __main__.py: bounded manufactured JSON fixture interface.
- example/law_payload.json: eight explicit events for the longitudinal-recoil witness.
- example/candidate.json: manufactured source metadata with actual SHA256 bindings.
- controls.py: new affected controls with hand-derived expected results, refusal paths and per-case JSON output.
- SOURCE_VERSION.json and SOURCE_MANIFEST.json: authored source identity and local bytes.

From this directory, root can execute the prepared commands under its frozen external budget:

    python controls.py > affected_controls_raw.json
    python -m heang_contract example/candidate.json > example_result.json

The first command is the single intended control-suite invocation. It returns 0 only if every affected control succeeds; failed cases remain in its JSON and produce exit 1. The CLI returns exit 2 for malformed, inconsistent or deferred inputs. The CLI is also exercised inside the control suite, so a separate CLI invocation is optional and should consume budget only if required by a concrete gate.

No command above has been executed by the author. Do not interpret the presence of controls as a pass receipt.

## Exact input and physics convention

Public numeric inputs accept Python integers, Fraction objects, or decimal integer/rational strings such as "14/3". Bool, binary float, NaN, infinity, decimal floating strings and zero denominators are rejected. Vectors must have exactly three components and matrices exactly 3 by 3. There is no clipping, symmetrization, normalization or hidden float conversion.

Production-facing quantities are explicitly SI-tagged. The example uses manufactured m=1 kg, M=3 kg and I=2 J to obtain small rational fixtures. These are not physical electron/proton masses or a measured H1 threshold.

The fixed convention is Newtonian finite mass, h=M+m, with the internal threshold I kept separately. c_light, hbar and k_B remain explicit in the theory contract. They do not disappear into a natural-unit convention. No relativistic or quantum-amplitude calculation is performed by this component.

### Event and raw-moment API

Event(weight, q1, q2, qp) stores a nonnegative exact weight and three exact COM momenta.

integrate_events(events, m, M, E, I) requires normalized weights summing exactly to one and checks every event:

    q1 + q2 + qp = 0
    (|q1|^2 + |q2|^2)/(2m) + |qp|^2/(2M) = E-I

The output has inclusive electron count2, ion count1, P=sum(q), R=sum(q q^T/m), K=trace(R)/2, J=STF(R), and C12=<q1 q2^T+q2 q1^T>. Incoming energy E is the relative-pair COM energy. The order q1,q2,qp is explicit; no sorting or relabeling changes the source.

The EventMoments container checks common normalization, count, momentum, energy and cross-correlation identities. This is an algebraic consistency check. Only integrate_events supplies direct finite-event support evidence.

cross_section_weighted(result, sigma) multiplies conditional moments by a nonnegative exact sigma, changing the normalization tag. It refuses an already weighted result. zero_cross_section(m,M,E,I) directly returns zero cross-section moments, including below threshold, without creating a conditional probability. The CLI zero-sigma branch requires empty events and cross_section_weighted normalization.

The measure mass Z is 1 for conditional moments and sigma for cross-section-weighted moments:

    Kp = Z*(E-I) - Ke
    tr(C12) = 2*M*Z*(E-I) - 2*(M+m)*Ke
    Rp = (m/M)*Re + C12/M

R has units J in the conditional event normalization and m^2 J after cross-section weighting. P, N and C12 receive the same normalization factor; serialized records retain the tags and units.

### General Galilean and orthogonal transformation

RawMoments(mass,N,P,R,normalization,kind) is an algebraic raw-moment container. kind is gain or signed_source. Negative N is accepted only for signed_source. Exact symmetry is required for R.

RawMoments and transform_raw do not certify PSD, an HE-X1 cone or physical realizability of arbitrary supplied tensors. HE-X1's existing necessary-cone evidence is a separate input and is not reimplemented or imported.

transform_raw(raw, boost=U, rotation=O) applies q'=O(q-mU), in that order:

    N' = N
    P' = O*(P-m*N*U)
    R' = O*(R-U*P^T-P*U^T+m*N*U*U^T)*O^T

O must be exactly orthogonal. The formula supports the full signed reactive number term. A species-central tensor uses the same boost with U equal to its declared reference velocity. The transformation never promotes a raw tensor to a physical source.

## Structural provider precheck

precheck_provider(metadata, payloads=None) returns one of:

- REJECTED_INCONSISTENT: malformed or contradictory declarations, actual byte-digest mismatch, unmatched identities, invalid declared scalar/domain values, or inherited candidate X1 FAIL.
- DEFERRED_DEPENDENCY: missing required evidence, missing actual bytes, unknown error calibration, missing frame/root/Jacobian information, or candidate X1 INDETERMINATE.
- PARTIAL_SCOPED: a coherent available structural subset with declared partial coverage or absent joint-correlation information.
- STRUCTURALLY_READY_REQUIRES_SOURCE_REVIEW: all selected structural declarations and content bindings are present and coherent.

Every outcome sets empirical_admission=false and runtime_activation=false. Metadata cannot authorize physical admission. A calibration status string, an evidence reference, or a boolean is never an independent source review.

The byte map binds relative payload names to actual bytes. Digests, source_id, event_law_id, preparation_id and angle_source_id must agree across sigma, electron, moment and correlation components. This protects against accidental stale or mismatched provenance; it is not an authentication, authorization or security proof.

The precheck checks the existence and form of source references. It does not establish that a cited paper contains the claimed mass, threshold, exchange law, measured range, preparation or uncertainty. It validates declared positive m/M/I, ordered nonnegative COM-energy bounds, the current h=M+m convention and H1_ground scope. Conditional domains cannot extend below their declared threshold. It does not establish the empirical correctness of those scalars or the adequacy of the nonrelativistic approximation.

The general rate dependency is sigma(E,a;preparation). Only an explicit unpolarized_isotropic preparation declaration permits the structural scalar sigma(E) reduction. Either declaration still needs independent source review. Frame metadata retains the relative incident axis, relative flux, target motion and, where needed, the lab/COM map. Fivefold joint-shell coordinates require both root-convention and Jacobian references; energy/solid-angle densities require a Jacobian reference.

Actual candidate payloads may contain different source formats. The structural precheck checks their bound bytes, not their scattering content. The manufactured fixture CLI additionally checks the identities, normalization, SI units, m/M/I, COM energy interval and COM/discrete-event semantics against the actual event payload before integrating it. An available lab-to-COM reference does not permit this fixed COM fixture schema to be relabeled as laboratory data.

## HE-X1 algorithm evidence versus this candidate

The old HE-X1 32-fixture PASS_SCOPED verifies the old algorithm/theorem within its saved scope. It is not a decision about a newly supplied source candidate.

The x1 record therefore separates:

- algorithm_science_pin and algorithm_evidence_reference: the frozen reused HE-X1 evidence.
- candidate_moments_sha256: the currently supplied moment-input payload identity, which must match bindings.moments.sha256.
- candidate_evidence_kind, candidate_certificate_provenance and candidate_evidence_reference: the evidence concerning this candidate.
- candidate_execution_status: NOT_RUN_ANALYTIC_SUPPORT or a separately recorded candidate execution.
- decision: unchanged PASS / FAIL / INDETERMINATE, plus represented_input_only and source_uncertainty.

The manufactured example's PASS is an explicitly written analytic application: positive event weights and exact finite-mass support yield its necessary outgoing cone, with S_e=diag(1/2,1/2,1), K_e=2, K_p=2/3 and D_e=1/2. Its candidate execution is NOT_RUN_ANALYTIC_SUPPORT. Existing X1 tests were not rerun, and their execution is not relabeled as a new candidate certificate. A precheck can verify this record's structural binding; independent review checks the actual analytic certificate.

## Affected controls and analytic expectations

The A and B witness laws each contain eight events with weight1/8. Their electron moments are Re=diag(1,1,2), Ke=2, De=1/2 and Pe=0. Their proton tensors differ:

    A: Rp=diag(0,0,4/3), Jp=diag(-4/9,-4/9,8/9)
    B: Rp=diag(2/3,2/3,0), Jp=diag(2/9,2/9,-4/9)

The controls check these explicit expectations, equality of the complete finite electron marginals, the Z-weighted energy and nonzero C12-trace identities, nontrivial boost followed by rotation, and a one-particle loss whose transformed R vanishes only when the signed N term is retained. They cover sigma=0 without conditional-law creation, malformed exact input, momentum/energy support refusal, normalization mistakes, corrupted/stale source bindings, partial-domain and missing-correlation statuses, source uncertainty, X1 candidate binding, and CLI return codes.

The continuous-azimuth proof and exact four-direction second-moment quadrature remain in ANGULAR_PROVIDER_DERIVATION.md and WITNESS_SPEC.json. Discrete controls do not replace that proof or constitute empirical angular calibration.

## Parent integration and handoff

Root can integrate this package at its C5 checkpoint, review the source bytes, freeze the expected execution identity, and run the new affected controls once under the cumulative budget. Any failure must be preserved and repaired only in the affected code. Independent review and source admission remain separate.

No all-project completion, physical H1 provider admission, gas closure, new evolution or runtime activation is claimed by this package. HE32 and old HE38 runs remain reused.
