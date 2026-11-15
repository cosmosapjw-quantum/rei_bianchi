# Independent He II Lyα dimensional guard review

Verdict: **PASS_SCOPED_GUARD_REPAIR**. The patch repairs a real units error in a validation guard and adds meaningful negative controls. It does not alter the native source equations, add another local ionization/heating term, or newly certify the complete native solve.

A distinct agent, started with `fork_turns=none`, reviewed the working-tree diff against `09b07147b280448bc05a1d0a7c0508401cf58a0b`, read the source capture and quadrature paths, reran all nine tests, and independently checked the immutable 92,160-row source receipt with long-double arithmetic. No author files were edited. Current-turn runtime: `PYTHON_PASS`.

The source capture defines escaped photon rate as `r_cascade (1−v)(1−f)`, in photons/s per integration node. The gamma-weighted time integral gives photon count, whereas the original `EventBox.escaped_energy` rate is erg/s and its integral is erg. Therefore the valid relation is

`E_escaped[erg] = N_escaped[photons] × 40.813320[eV/photon] × 1.602176634e−12[erg/eV]`.

The conversion factor is 6.539014765996488×10⁻¹¹ erg/photon. The removed check directly intersected a photon-count interval and an energy interval. It was dimensionally invalid, and every one of the 92,160 saved rows has a shared zero lower bound, so intersection alone could accept even a very wrong energy scale. The replacement checks both corresponding nonnegative endpoint representations after conversion, with relative tolerance 6×10⁻¹² and zero absolute tolerance. The same numerical tolerance appears in existing aggregate source-representation checks; applying it per row is a new, stronger representation check, not a change to the physical local-error or width gates.

The independent recomputation found a maximum relative conversion discrepancy of 1.05919×10⁻¹⁵. The saved source SHA256 is `6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae`, matching the test’s immutable receipt. All endpoints are nonnegative. The author tests independently rerun passed 9/9, including the entire original receipt audit and new count-as-energy / factor-two wrong-energy negative controls. The latter controls specifically defeat the old shared-zero interval-intersection loophole.

No double count is introduced: the patch changes one guard and imports a checking helper; it does not modify `OriginalEventObserver.__call__` source expressions, the native population RHS, source energy, quadrature weights, or any update. The already present H I / He I local absorption and photoelectron heating remain an observation of original on-the-spot source physics. The theory correctly distinguishes the exact realization identity `chemical + photoheat + escaped = emitted line energy` from independent interval bounds, whose upper endpoints need not sum as equalities. The remaining heat interval-intersection check is dimensionally consistent; this review does not turn it into a stronger bound certificate.

Limits: the new `allclose` guard is a representation-consistency test, not a proof of outward interval containment or an astrophysical accuracy bound. The existing `nonnegative_outer` helper clips interval portions below zero, relying on the caller’s physical nonnegative-source contract. The full native interval solver was not rerun in this review or by the new receipt regression. Historical source endpoints, native local-error gates, and official/research tick status are consequently not new execution claims. The 46,080 source nodes are material integration nodes; this work adds no spatial propagation or escaped-photon absorption into another domain.

Machine-readable findings are in `HE_DIMENSIONAL_REVIEW.json`.
