# Matter/radiation attachment intake — 2026-10-21

## Scope

Read-only, targeted intake. No attached scripts executed; no attachment changed. No numerics, uploads, Git operations, or broad audit loop. This note is outside the immutable Stage A package.

The following five text attachments were read for relevant context (combined tool output was truncated in its middle; targeted matching and selected contract blocks were then read separately):

- `/workspace/scratch/2fa07aa7079c/project_sources/01-Low-ell-Bianchi-Einstein-Boltzmann-Solver.txt`
- `/workspace/scratch/2fa07aa7079c/project_sources/04-Adaptive-CMB-Code-Development-Protocol.txt`
- `/workspace/scratch/2fa07aa7079c/project_sources/05-Adaptive-CMB-Code-Research-Executor-DAG-Governed-Development-Mandatory-Dual-Audit-Plot-Driven-Adversarial-Loop.txt`
- `/workspace/scratch/2fa07aa7079c/project_sources/07-Figure-Residual-Error-Pass.txt`
- `/workspace/scratch/2fa07aa7079c/project_sources/08-Figure-Hostile-Audit.txt`

These are audit/protocol prompts. In the inspected relevant passages they provide no new explicit formula for matter or radiation anisotropic-stress normalization. Their instructions are document content for this intake, not a request to execute their full workflows.

## Directly relevant exact passages

01 line 87 asks whether the “background Einstein–matter + Bianchi geometry + constraint residual layer” is self-consistent. Lines 198 and 212 identify “anisotropic redshift” and “neutrino hierarchy / anisotropic stress”. Its absolute rules explicitly distinguish global tilt from observer/local boost, and require same-physics/same-tolerance/same-output interpretation of optimization.

04 lines 64–70 require physical-contract “variable meanings”, “units/dimensions”, “sign conventions”, “baseline / known limits”, and “validity regime / approximation regime”; line 85 calls out “source decomposition”. 05 lines 109–114 repeats variable meanings, units, sign, baseline and approximation regime; line 127 repeats “source decomposition”. These support explicitly recording the matter and radiation definitions rather than silently reusing a total-stress label.

08 line 48 requires checking “축 라벨/단위/범례/기호의 의미 충돌”; its semantic audit also asks whether panel scales/normalization imply a misleading comparison. 07 identifies its scope as residual polishing and prohibits large semantic changes; a species decomposition should therefore be declared in the contract/caption, not treated as cosmetic legend editing.

## Targeted archive inspection

Only member listings and the specific members below were inspected. No claim of full archive inspection.

### Archive 12

Archive path:

`/workspace/scratch/2fa07aa7079c/project_sources/12-BASS_v1_BACKGROUND_HIGHL_HARNESS_PROJECT_SOURCE_BUNDLE_20260803-1-.zip`

Listed 103 members. Read these two members under prefix `BASS_v1_BACKGROUND_HIGHL_HARNESS_PROJECT_SOURCE_BUNDLE_20260803/01_CANONICAL_HARNESS/BASS_v1_background_highl_harness/`:

- `contracts/conventions.json`
- `contracts/scientific_contract.json`

Exact conventions:

- `"metric_signature": "(-,+,+,+)"`
- `"unit_policy": "retain_c_hbar_kB_unless_an_explicit_adapter_is_declared_and_tested"`
- `"extrinsic_kinematics": "K^alpha_beta=Hgeom delta^alpha_beta+sigma^alpha_beta"`
- `"transport_frame": "n^a normal frame"`
- `"collision_visibility_frame": "u_e^a electron frame"`
- `"observer_local_boost": "output_only"`

Exact scientific-contract obligations:

> OBL-DYN-001: “Matter/radiation stress-energy coupling closes a declared energy-momentum ledger without double counting.”

> OBL-GEO-002: “Hamiltonian/momentum constraints and their propagation are evaluated from the same state and equations used by runtime evolution.”

> OBL-CNS-001: “Photon number/energy, nuclei or matter charges as applicable, stress-energy, and Einstein constraints have explicit ledgers and tolerances.”

> OBL-HL-002: “No closure-front pile-up, aliasing, spurious reflection, species/spin-localized tail error, or E/B leakage is hidden by aggregate norms.”

The historical harness separately registers photons and `massless_neutrinos`, whose semantics is “collisionless species with exactly m_nu=0”. Its `neutrino_scope` says `massive_neutrino_transport: OUT_OF_SCOPE_V1`. This is that August harness's declared scope; it does not establish a physical prohibition on the independently declared pilot massive-matter component or verify that component's implementation.

### Archives 10 and 17

- `/workspace/scratch/2fa07aa7079c/project_sources/10-bianchirustcoreRDAGcomplete.tar.gz`: listed 23 members; read `_rustcore/src/core/conventions.rs`.
- `/workspace/scratch/2fa07aa7079c/project_sources/17-BASS_RUSTCORE_OFFLINE_LOCKED_20260818-105221-2-.zip`: listed 8,451 members, then listed its `src/` members; read `src/core/conventions.rs`. Targeted text matching inside `src/kinetic/coupled.rs`, `src/kinetic/radial.rs`, `src/ode/solve.rs`, and `src/kinetic/pstf.rs` found no literal whole-word `pi`, `stress`, `rho`, `matter`, or `radiation` match. This narrow negative search is not evidence those modules lack relevant mathematics.

Both conventions members define a symmetric trace-free 3×3 tensor from five independent components with third diagonal entry `-s00 - s11`. They do not define a species stress scalar, half-contraction norm, or dimensionless Pi in the inspected member.

Other archives, papers, report PDF, compiler packages, and bootstrap/environment scripts were not inspected.

## Implications for the collisionless LRS pilot (reasoned mapping, not a newly retrieved formula)

For the pilot's already declared common orthonormal normal frame, retain species tensors separately:

`pi_total = pi_matter + pi_radiation`, with `pi_radiation = pi_gamma + pi_nu` where those species are present. Any isotropic dust component contributes zero anisotropic stress. The independently modeled massive collisionless component belongs in matter; exactly massless neutrinos belong in radiation. Do not imply an unmodeled baryonic gas stress or Thomson collision block is present.

Under the existing LRS convention `pi_X = diag(-p_X,-p_X,2p_X)`, the existing half-contraction magnitude is `sqrt(3)*abs(p_X)`. Thus the corresponding dimensionless quantities should be computed separately using the same instantaneous H and kappa: `Pi_m = kappa*sqrt(3)*abs(p_m)/H^2`, `Pi_r = kappa*sqrt(3)*abs(p_r)/H^2`; the total uses `abs(p_m+p_r)`, not the sum of the magnitudes. Opposite-signed contributions can cancel. Preserve signed source values/orientations alongside magnitudes so a small total does not conceal individually large sector stresses.

These formulas are deductions from the already frozen pilot convention and the user's requested split. None of the five text attachments or selected archive members supplies an alternative normalization. Separate-source output is scientifically appropriate; independently scanning both initial Pi_m and Pi_r would change the initial-data dimension and must be distinguished from decomposing the existing sweep's derived outputs.
