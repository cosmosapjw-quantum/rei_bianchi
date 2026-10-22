# C1: isotope-native source, charge and energy contract

Date: 2026-10-22 KST. Selected stage: **C1 only**, the next genuinely
incomplete `COUPLED_ISOTOPE_NATIVE_CONTRACT` node. This unit fixes a usable
mathematical/API contract and performs finite algebraic checks. It does not
advance a cosmological IVP, replay a completed campaign, implement the full
native solver, or claim completion of C2-C10.

## 1. Baseline and concrete target

Authoritative continuation: `cosmosapjw-quantum/rei_bianchi` PR219,
`5a1e5220b301a1c497f2863d6fd823e605faba80`, especially
`research/rei_reionization_dossier_20261022/NEXT_DAG.json` and its final
delivery ACK. The parent atomic/nuclear calculations retain their existing
scoped admissions. PR220 at `8be7533cc97b3302bf42608699d6e8313ed6af8a`
is an independent compact-coordinate donor with 127 main + 2 full62 oracle
cases. Its 5-200 eV field is different from PR219's 5-60 eV field. REC119's
126 cases are another cohort. None of these counts or source fields is merged.

Target: an additive event operator that can inject nuclear daughter isotope
and charge populations into a thermal/atomic evolution without losing charge,
baryon number, or energy. The operator is defined on absolute abundances;
zero-inventory tritium and neutron states must remain representable. A
subsequent physical solver must supply applicable rates, daughter branches,
energy distributions and transport. Those are input obligations, not implicit
zero rates or invented probabilities.

Geometry remains non-tilted LRS Bianchi I, signature (-,+,+,+), with proper
time t in s, H=(1/3)theta in s^-1, and x=ln(a/a_ref), d/dx=H^-1 d/dt
only where H>0. sigma=diag(-s,-s,2s); pi_A=diag(-p_A,-p_A,2p_A).
The massive pi_m belongs to a separate nonbaryonic collisionless component;
pi_r=pi_gamma+pi_nu. An isotropic thermal baryonic bath has pi_b=0. A nuclear
heating source must not be confused with sigma:pi_m or sigma:pi_r. Fast
anisotropic baryonic products require a separately supplied stress closure.

## 2. State, stoichiometry and free electrons

Use i=(A,q), with q the positive ionic charge, and the 21 slots

```
n; H1 I,II; D I,II; T I,II; He3 I,II,III; He4 I,II,III;
Li6 I,II,III,IV; Li7 I,II,III,IV.
```

Y_i=n_i/n_B, where n_B is conserved baryon-number density, not mass density.
For a closed homogeneous baryon cell, dot n_B=-3H n_B. A_i is nucleon
number and Z_i nuclear charge. Sum_i A_i Y_i=1. The number of nuclei per
baryon, Y_N=sum_i Y_i, need not be conserved by capture/fusion.

For event j and a resolved branch b, integer stoichiometry nu_ijb is
products minus reactants and R_jb has units events baryon^-1 s^-1:

    dot Y_i = F_i^atom(Y,T,J) + sum_jb nu_ijb R_jb.

Each branch has A dot nu=0. If positrons/negative ions are absent and all
free electrons are included, charge neutrality gives

    Y_e,total = sum_i q_i Y_i,
    delta_e,jb = sum_i q_i nu_ijb,
    dot Y_e,total = sum_i q_i dot Y_i.

`delta_e` is the **net free-electron increment**, not merely the number of
new weak-decay electrons. It includes shake-off, capture and atomic
ionization/recombination. With N_bound=sum_i (Z_i-q_i)Y_i,

    delta_e + delta N_bound = sum_i Z_i nu_i.

For a strong/EM event the right side is zero; for beta-minus it is one.
This identity prevents counting the weak electron twice. A supplied
independent electron source must agree with q dot nu.

A binary branch with applicable coefficient k [m^3 s^-1] has
R=n_B k product_i(Y_i^multiplicity)/product_i(multiplicity!). A unary
decay has R=lambda Y_parent [s^-1]. A bare-nucleus rate applied to the
sum of neutral and ionized populations is a named all-bare sensitivity
assumption; it is not an established charge-resolved rate.

### Daughter branch contract

For a given resolved reactant channel, p_b>=0 and sum_b p_b=1.
R_jb=p_b R_j is permitted only when p_b is actually supplied with a physical
or explicitly manufactured interpretation. Conservation applies to every
branch, not only to a probability-averaged output. Branch probabilities may
depend on reactant charge and energy; do not turn a nuclear-only family into
a unique ionic daughter map without that input.

Useful **conditional spectator endpoints** are

| Event | delta_e | Interpretation |
|---|---:|---|
| n -> H1 II + e + antineutrino | +1 | continuum beta endpoint |
| T I -> He3 II + e + antineutrino | +1 | one bound spectator retained |
| T II -> He3 III + e + antineutrino | +1 | bare continuum beta endpoint |
| T I -> He3 III + 2e + antineutrino | +2 | one additional electron shaken off |

The last row demonstrates why a universal `beta_electrons=1` is inadequate
for free-electron accounting. These rows specify valid charge endpoints;
their physical branching weights, excitation distribution, bound-state beta
branches, and charge-state-dependent decay corrections remain provider work.
T fractions must never be filled by copying H fractions.

### Single beta owner

The new coupled mode shall use the already pinned nuclear
`EVALUATED_DECAY_INPUTS.json` as its sole conditional decay-constant source.
Its tritium value is 12.312 years using 365.24219878 days/year, whereas an
inherited atomic helper uses 12.32 Julian years. In the coupled mode beta
events must be removed from the atomic generator if the nuclear event module
owns them. Historical atomic helpers and completed results are unchanged.
The source discrepancy is an integration hazard, not evidence that the old
zero-T pilot was numerically wrong. Both historical definitions remain recorded.

## 3. Energy reference and exactly one owner per exchange

The actual PR219 nuclear code uses bare nuclear masses (Li is approximated by
neutral atomic mass minus three electron masses), and for beta-minus subtracts
one electron rest mass. Its `Q_J` is therefore **not neutral-atomic Q**.
Do not silently correct its old Q values or reuse them under a different name.

Let B_Aq>=0 be the total binding energy of the bound electrons in the
chosen ionic ground state, B_AZ=0. Define I_Aq=B_A0-B_Aq and

    m_Aq c^2 = M_A c^2 + (Z_A-q)m_e c^2 - B_Aq,
    m_A0 c^2 = M_A c^2 + Z_A m_e c^2 - B_A0.

For nu=products-reactants, the charge-neutral reference convention is

    Q_bare = -sum_A M_A c^2 nu_A - m_e c^2 sum_A Z_A nu_A,
    Q_0 = -sum_A m_A0 c^2 nu_A = Q_bare + sum_A B_A0 nu_A,
    Delta I = sum_i I_i nu_i,
    Q_available = Q_0 - Delta I = Q_bare + sum_i B_i nu_i.

The electron rest-mass term automatically gives -m_e c^2 for beta-minus and
zero for strong/EM nuclear events. For atomic photo/RR/CI events nu_A=0 and
Q_0=0. These are identities for a self-consistent mass/binding table. The old
Li binding omission must remain an explicit legacy approximation unless a
new consistent table is adopted; mixing corrected and uncorrected references
would manufacture an energy defect.

Using a neutral-atom rest reference, store translational e_th and ionic
e_ion=sum_i I_i Y_i separately, both in J per conserved baryon. For each
event, let W be external supplied energy and let signed increments include
thermal, fast-particle kinetic, excited atomic state, retained photon,
escaped photon and neutrino energy. The local ledger is

    Q_0 + W = Delta I + Delta E_th + Delta E_fast + Delta E_exc
              + Delta E_gamma,ret + E_gamma,esc + E_nu.

Increments can be negative for an inverse or cooling event. The code must
not assign Q both to instantaneous heat and to a fast/gamma/neutrino ledger.
Later fast-particle stopping is a transfer: +D to thermal and -D to fast,
with no second Q source. A generated hard photon belongs to one radiation
field/reservoir; counting it does not prove it escapes or is reabsorbed.

In an all-thermal finite diagnostic, photoabsorption of energy E at threshold
I has Delta I=I and Delta E_th=E-I. RR requires an energy-weighted kinetic
loss/cascade model: a number-rate coefficient alpha(T) alone does not supply
that energy moment. DR has the same number-versus-energy distinction.
Neither a nuclear Q ledger nor an external J_nu prescription constitutes a
closed radiation/thermal solution.

For an explicit external spectrum, h=2 pi hbar, and one-electron direct photo yield,

    Gamma_i = integral [4 pi J_nu/(h nu)] sigma_i(nu) dnu,
    H_i = n_i integral [4 pi J_nu/(h nu)] sigma_i(nu) (h nu-I_i) dnu.

Gamma_i is s^-1 and H_i J m^-3 s^-1. If secondaries or nonthermal electrons
are followed, this excess energy first enters their reservoir and is not
also injected into H_i. A threshold-support zero applies to that named
external field only. PR219's 5-60 eV and PR220's 5-200 eV fields do not
describe newly generated MeV photons.

## 4. Spectator EOS with a changing particle count

For an isotropic, nonrelativistic, classical monatomic common-temperature
thermal pool define C_th=sum_i Y_i,th + Y_e,th. Then

    e_th = (3/2) k_B T C_th,
    p_th = n_B k_B T C_th,
    dot e_th + 3H k_B T C_th = Q_th/n_B,
    dot T = -2HT - T dot C_th/C_th + 2 Q_th/(3 k_B n_B C_th).

Q_th is net translational deposition [J m^-3 s^-1], excluding separately
stored ionization, excitation, rest, and fast energy. If all nuclei and
electrons are thermal, C_th=sum_i(1+q_i)Y_i and
dot C_th=(1+q)^T (dY/dt). Replacing this derivative by dot Y_e alone is
incorrect when a two-nucleus capture produces one nucleus.

If fast nuclei/electrons are retained, C_th excludes them and charge closure
uses total free electrons: Y_e,total=Y_e,th+Y_e,fast. Bulk thermal rates use
the thermal reactants and Y_e,th. A cold-electron Thomson operator cannot
automatically use a relativistic fast-electron population. A terminal
instant-thermalization test is allowed as a labelled fixture, not as a
demonstrated cosmological stopping regime. General nonthermal pressure,
escape and thermalization require extra equations.

Limits: fixed composition and Q_th=0 imply T proportional to a^-2. With
H=0 and zero translational energy input, doubling the thermal particle count
halves T at fixed e_th. Threshold photoionization of a neutral H gas is a
manufactured exact example. These tests do not require a cosmological IVP.

## 5. When the electronic quotient survives

Write Y_Aq=Y_A f_Aq for Y_A>0. Let the shared electronic generator be G_Z
and let S_Aq be nuclear/other injection. S_A=sum_q S_Aq. Direct differentiation
gives

    dot f_Aq = (G_Z f_A)_q + (S_Aq-f_Aq S_A)/Y_A.

Electronic equality alone is insufficient once the second term differs
between isotopes. Shared fractions require matching normalized injection
terms (and matching generators/initial fractions). The special case
S_Aq=f_q S_A preserves shared fractions. At Y_A=0 the fraction equation is
undefined; evolve absolute Y_Aq and define fractions only once populated.

PR220's fixed linear lift additionally imposes n=T=0 and fixed isotope
inventories. Any positive T/neutron source lies outside that image. This
is a scoped algebraic counterexample to reusing that fixed 33-coordinate
map, not a general claim that no smaller valid coordinate system exists.
The reflection-even geometric reduction may still be reused if the new
sources preserve its parity, but the isotope quotient must be replaced or
reproved for the selected source model.

## 6. Executable interface and finite acceptance

The future native operator consumes: (i) ordered 21-slot abundances and
thermal/fast partitions; (ii) explicit resolved reaction branches; (iii)
source rates in events baryon^-1 s^-1; (iv) one pinned mass/binding reference;
(v) signed energy partitions in J/event; (vi) source/field identity and
applicability status. It returns dY, total and thermal electron source,
thermal particle source, and separately owned energy/reservoir derivatives.
Missing branch/partition/provider input is `UNRESOLVED`, not zero or PASS.

This C1 unit runs only a small reference diagnostic, not a physical rate
provider or IVP driver. Its production and verification pass must cover:

1. All 18 inherited nuclear families and 34 directed entries retain exact
   integer baryon balance, bare charge balance including beta electrons,
   source aliases and the eight external-photon support-zero labels.
2. The four beta endpoint fixtures above satisfy free+bound electron balance;
   no physical probability is assigned to their mixture.
3. Photo/RR thresholds and a synthetic fast-to-thermal transfer conserve
   their energy ledgers; an intentionally double-booked Q fails.
4. The mass-reference algebra holds for manufactured binding values and the
   stated Q_bare convention. This is not a mass-data accuracy validation.
5. A two-to-one capture changes C_th even with delta_e=0. The variable-C_th
   temperature identity and the threshold-photo T/2 limit hold.
6. A positive T source is rejected by the old fixed lift; the source-aligned
   common-fraction special case remains possible. No division by absent T.
7. Missing physical daughter probabilities and missing energy partitions
   are rejected; the two legacy tritium definitions are measured separately.

Integer conservation is exact. Floating energy/algebra residuals use
abs(residual)/max(sum(abs(terms)), 1e-300) <= 64*binary64_epsilon. No
scientific pilot tolerance is altered. Runtime cap: one process, no ODEs,
less than 60 CPU seconds and 256 MiB diagnostic working data. Use one
bounded implementation/verification pass and one independent scientific
review; only a concrete defect authorizes targeted repair.

## 7. Completion and next action

C1 completes when the above contract and its algebraic evidence are coherent
and reviewed. C2 then maps actual isotope-charge providers and energy moments
to the operator, retaining source-specific applicability and legacy isolation.
No branch probability, neutral-plasma nuclear rate, fast-product stopping
law, RR/DR energy moment or closed photon field is declared available by this
contract. The old bounded results remain admitted; coupled production remains
HOLD_DEPENDENCIES until those inputs and changed-dependency tests exist.

Primary external context: NIST ASD ionization-energy interface
https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html; Williams and Koonin,
Phys. Rev. C 27, 1815 (1983), https://doi.org/10.1103/PhysRevC.27.1815;
Frolov, https://arxiv.org/abs/1512.04721v2; Smith et al., Grackle,
https://arxiv.org/abs/1610.09591. The beta sources establish that excited and
continuum final states need a model; no numerical branching is imported.
Grackle supplies reusable chemistry/thermal concepts, not the complete
isotope-native H/He/Li nuclear daughter closure specified here.
