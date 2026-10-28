# REI-CHEM-LEDGER-01: composition and energy-reference theorem

The new interface permits isotope-labelled molecular composition and distinct electron pools while retaining exact event number, charge and energy accounting. The contribution is a usable extension of the inspected atomic-rung interface; the following conservation algebra is established linear algebra, not a claim of a new fundamental conservation law.

## R1–R4: setting and representation

Let S be a finite supplied species catalog and I a finite supplied set of nucleus identities `(Z,A,isomer)`. A material species s has nucleus multiplicities a_is>=0 and integer charge q_s. Its bound electron count is z_s-q_s, with z_s=sum_i Z_i a_is. Free thermal and fast electrons have empty composition, charge-1, and distinct identities. Molecular species need several nonzero a_is; anions need q_s<0. The old single-isotope charge ladder cannot represent these two extensions.

For reactant/product integer matrices L,R, use N=R-L. Keep L and R themselves for event identity. Replacing (L,R) by (L+d,R+d) leaves N unchanged but adds spectator reactants; dividing by a common integer changes event normalization. Neither transformation is an allowed automatic event deduplication.

Chemical events preserve each nucleus identity; nuclear events preserve baryon count but may change isotope identities and require separate source/energy qualification. The q<=z schema bound ensures nonnegative bound electron count but establishes no bound-state existence. The producer remains responsible for the physical catalog.

## R5: constructive derivation

For x=N_particles/N_ref and r events/(N_ref second), dot(x)=N r. Chemical conservation follows columnwise from A N=0 and q^T N=0. These are stronger than tracking only elements or baryon count. For example H1+He4 -> D+He3 preserves element counts (one H and one He), baryon count5, nuclear charge3 and total ionic charge0, but changes all four isotope counts. It must fail a chemical-channel check. The same transformation may occur only as a separately typed nuclear event with its own provider.

Let e_s denote stored internal energy per particle in eV. For physical reservoirs a, let D_ar be the independent energy increment per event. Total per-reference energy source is

    dot(E_total) = (e^T N + 1^T D) r.

A zero row e^T N+1^T D is sufficient for any normalized rate vector; conversely, if cancellation holds for all independent nonnegative unit-rate vectors, each column must vanish. Thus a column-level ledger is exactly the required local criterion, without imposing a cosmological solution or kinetic closure.

For a conserved-row matrix C with C N=0, define e'=e+C^T lambda. Then

    e'^T N + 1^T D = e^T N + lambda^T C N + 1^T D
                       = e^T N + 1^T D.

This proves energy-reference independence on the conservation subspace. In chemical scope choose C=(A;q^T). The q row includes free electrons, so even a charge-dependent reference change cancels exactly. If the PI electron is omitted, q^T N=1 and a reference shift lambda_q changes the computed reaction energy by lambda_q. This is an explicit diagnostic of inconsistent electron/mass bookkeeping, not a tolerance failure.

A physical rest-mass convention can be transformed to the internal-energy convention only when the removed rest-energy vector lies in the span of the actually conserved rows. For chemical events, constituent nuclear rest energies and all electron rest energies are conserved. Total electron count is z_s-q_s on material species plus1 on each explicit electron species; its row equals Z^T A-q^T, hence is conserved. Nuclear isotope conversion does not conserve arbitrary isotope rest-energy rows; dropping those rows would erase physical nuclear Q. This interface therefore leaves nuclear Q unqualified and never applies a chemical isotope-reference transformation to a nuclear energy ledger.

For any perturbation v of normalized rates, delta(dot(x))=N v and delta(dot(E_total))=(e^T N+1^T D)v. Signed v is legitimate. For a state-dependent physical rate r(x), the local Jacobian is N dr/dx; differentiating C dot(x)=0 yields C J=0 wherever the rate is differentiable. This unit tests the fixed-rate/JVP algebra; it does not fabricate a state-dependent rate model.

A reverse representation interchanges L,R and negates every signed energy increment. Hence N_reverse=-N and Q_reverse=-Q. Its rate remains an independent physical input. Canonical unordered sides can identify an algebraic reversible pair, but cannot imply detailed balance, microscopic reversibility, an inverse cross section, or equivalent photon support.

## R6: independent checks by direct event reasoning

Attachment H1+e_th -> H1− has charges0-1=-1 and one H1 on both sides. With synthetic e(H1)=-10,e(H1−)=-12, material energy falls2eV and an emitted photon reservoir receives2eV. A free-electron rest-energy reference shift cancels because the extra bound electron is the consumed free electron.

Association 2H1 -> H1H1 preserves two nuclei and consumes no net free electron. Synthetic internal energy -20 -> -25 releases5eV. Reversal absorbs5eV; treating a positive cumulative emission tally as an additional radiation state would double count the release.

For D+H1+ -> D++H1, synthetic material energy -11 -> -10 requires1eV from the thermal reservoir. Both charges equal+1 and D/H1 inventories remain separately fixed. Replacing isotope-specific thresholds by an element-average value would hide this difference; the interface preserves labels even when a provider explicitly adopts equal-rate approximations.

For fast-to-thermal electron transfer, the two species columns are(-1,+1). Their shared charge cancels, while kinetic increments(-3,+3)eV transfer energy exactly. A population column alone cannot determine the deposited energy; it must be supplied with the event.

The same-net spectator example demonstrates why a signature based only on N is insufficient. Two independently active providers on an identical physical event ownership slot can double its contribution although all conserved sums remain zero. Conservation and unique event ownership are separate necessary interface checks.

## R7: finite discriminating execution contract

The frozen contract supplies literal exact fixtures and negative cases. All arithmetic acceptance is exact rational/integer. No empirical coefficient or ODE is needed. Implementation and its actual child execution remain the lower-tier executor's responsibility; the present authority has performed derivation and static source intake only. The exact H1+He4 isotope counterexample is an additional recommended guard if included before the single child is frozen; otherwise it remains an analytic R6 witness and causes no extra run.

## R8–R10: status, contribution and next use

Theory verdict DERIVED_SCOPED. Core conservation, reference invariance, reverse orientation and event-identity distinctions follow under stated finite catalog assumptions. No strong no-go is proposed; NG1–NG7 admission does not apply. Implementation and scientific admission are pending independently reviewed raw outcomes. No stage count is a global model completion fraction.

PASS enables delivery of species/channel-qualified microphysics: WU088_HH owns isotope/atomic/molecular rate and binding/branch inputs, BASS_HE owns angular/finite-mass collision moments, bass_cr owns distribution/stopping and photon/electron moment chains, REC owns line/continuum recombination and history, BASS owns spacetime/kinetic donor mapping, VigilODE owns numerical integration evidence, REI owns finite event assembly. These are interface assignments for future contracts, preserving existing owner's domains and active tasks.

After a compiler PASS, choose one source-qualified molecular or expanded-ion input only after the target catalog, native state resolution, channel support, event normalization, energy/charge partitions and uncertainty are supplied. An unqualified cell stays unqualified; a supported zero remains zero. The current derivation supplies no physical molecular-rate coverage.
