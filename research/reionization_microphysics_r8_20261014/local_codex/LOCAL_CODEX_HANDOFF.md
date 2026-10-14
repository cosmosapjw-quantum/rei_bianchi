# Reionization R8: local implementation and heavy calculation handoff

Status: **package prepared; local Codex has not executed these calculations**. Start from the R8 report and `integration/CURRENT_SNAPSHOTS.json`. Preserve existing working trees. Read each relevant repository's current AGENTS and actual code before adapting it. The user authorizes this work and external backup/publication; this package does not authorize an unreviewed main merge or change the scientific acceptance scope.

## 1. Reuse first, then select the expensive calculation

R8's native lightweight outputs and tests are the first input; do not rerun the R7 or cross-thread scientific suites by default. Recover complete source archives only where the adapter needs code absent from the read scientific report. Exact archive identities and observed remote entrypoints are in the integration snapshots/reports. The GitHub research entries sometimes publish a substantive report rather than the full executable source. A report URL is not an executable provider.

The current sources are HE R10/PR45, HH PHYS29/PR62, CR moving cluster/PR56 and published REI OBSERVER15 R7 at PR115 commit 8bf8e3c18d607334614cfea734f9b10961fbd4d4. The earlier Library R7 proof is a separately retained variant, as detailed in integration/DELTA_AND_REUSE.md. Specifically, HH's Coulomb thermal integral is already numerically computed. Its next remaining numerical obligation is finite quadrature/all-roundoff certification; do not regenerate its physical result merely to match an obsolete readiness table. CR's seeded moving result uses a lifted static reference and a new defect bound, so a full moving ODE is a distinct computation. REI's exact-real GL32 baseline now has source-node error; consuming the same cubic avoids a redundant interpolation term.

On the user's 12-core/24-thread, 64-GB workstation, start with two independent single-thread pilots and a total 48-GB scheduling cap. Discover actual CPU/RAM before using these defaults. Do not assume the GPU accelerates Fortran scattering or a dense generalized eigensolver. Cap BLAS/OpenMP separately to avoid nested oversubscription. For each real model, benchmark one small representative block, record wall time and peak memory, then choose workers from measured memory plus headroom. The runner's sampled RSS covers the main process only; MPI aggregate memory needs scheduler/cgroup measurement.

## 2. Execute the prepared runner

```bash
python3 local_codex/run_jobs.py preflight --out local_runs
python3 local_codex/run_jobs.py benchmark --out local_runs --workers 2 --threads 12 --memory-mb 49152
python3 local_codex/run_jobs.py run --out local_runs --workers 2 --threads 12 --memory-mb 49152 --max-seconds 14400
```

Initially preflight returns blocked because actual heavy providers were not supplied. This is the truthful state, not a failed physics calculation. Follow PROVIDER_CONTRACT.md to bind actual executable SHA, source commit and input-file SHA for each job. `run` benchmarks each partition before running it, limits concurrency/threads/declared memory/wall time, writes logs and atomic receipts, and reuses successful matching receipts. The initial `selected_model` partition is a scheduling label, not a scientific input deck. Replace it with real independent symmetry/energy partitions once chosen. A local wrapper may translate this interface into an existing program's native input format, but must not silently invent Hamiltonians, potential curves, external radiation or undocumented defaults.

## 3. Implement remaining providers

### Li bound and continuum: `li_bound` then `li_continuum`

Read BASS_HE and the R7 microscopic-reconstruction chapter. Reuse radial integrals, ECG matrices and symmetry routines actually present, not assumed capabilities. Construct balanced neutral Li and Li+ targets in common isotope/mass conventions. The finite-mass nonrelativistic target Hamiltonian is

H=sum_i[p_i²/(2 mu)-Z e²/(4 pi eps0 r_i)]+sum_i<j[e²/(4 pi eps0 r_ij)+p_i.p_j/M].

Separate L,S,parity blocks and antisymmetrize; solve H c=E S c with explicit overlap conditioning. Retain threshold errors between parent and all daughter targets, not just absolute parent energy. Converge basis scale/count and core/valence balance. A historical 829-configuration target is a reproducibility target only if its actual configuration list is recovered; an independently converged target is a different, scientifically usable reconstruction.

For the continuum, first compute requested response moments using block Lanczos/resolvent or exterior-complex-scaled driven equations if those preserve the chosen observable. Inclusive dipole response alone does not supply exclusive double-ionization or electron-energy/angle distributions. Use a source-specific CCC/R-matrix/close-coupling implementation for those. Construct the Coulomb asymptotics and exchange explicitly. A public method description is not evidence that the native CCC code/deck is available. If source access is missing, mark `missing_provider` and proceed with independent bound-state work.

Parallelize by irreducible symmetry and incident-energy panels; reuse each target factorization and dipole RHS. Accumulate number, energy and response-weighted moments together. Locate resonances adaptively, with a tail and interpolation estimate. Checks: normalized bound states, overlap-spectrum conditioning, threshold convergence, Coulomb normalization, flux/unitarity, positivity, length/velocity gauge comparison at converged basis, shared forward/reverse rates. The full correlated model requires these checks; a gauge difference alone is not a rigorous error bound.

### Molecular low-temperature rates: `molecular_lowT`

Generate or recover charge/symmetry-specific Li–H, Li–He, T/H, T/D potential curves, derivative couplings, asymptotic thresholds, radiative dipoles and hyperfine contacts. These are required physics inputs. Isotope changes enter reduced masses and finite-mass/adiabatic corrections; a universal mass-rescaling factor is insufficient near a pole.

For each J/parity/channel block solve the coupled radial system using renormalized Numerov, log-derivative propagation or an R-matrix method with long-range asymptotic matching. Reuse the common electronic curves. Separate threshold pole searches from thermal convolution. Compute S(E), channel-resolved cross sections, then

k(T)=sqrt(8/(pi mu)) (kB T)^(-3/2) int E sigma(E) exp[-E/(kB T)] dE.

Use x=E/(kB T), split thresholds/resonances, and compute all requested temperatures from a common adaptive energy representation. The Wigner threshold law can guide a bounded extrapolation only after the physical long-range class and absence/location of nearby poles are established. Radiative channels need continuum dipoles and photon energy; an elastic/charge-exchange S matrix does not determine them. Verify radial/domain/energy convergence, unitary open-channel flux in the nonabsorbing case, reciprocity with degeneracies, and bound-plus-continuum normalization. Return actual 1, 6.11, 10 K values only for a converged physical model; retain the full temperature grid used in reionization.

### Correlated daughters: `daughter_correlated`

Use the same parent wavefunction and charge/isotope convention as the bound calculation. Define exclusive asymptotic daughter channels by orthogonal projectors or a controlled POVM; raw overlaps in a nonorthogonal Gram basis are not exclusive probabilities. Construct amplitudes with the nuclear recoil/weak operator and electron correlation, then evolve or project to asymptotic channels. Retain missing norm as unresolved continuum until convergence, rather than renormalize it away.

For additive mean observables in a fixed external bath, compute sufficient one-particle marginals and conditional first moments before attempting the full joint grid. This can remove several dimensions. For coincidence observables, eventwise conservation or nonlinear event feedback, retain the common nuclear/electronic/photon event measure. Use daughter-rest photon energy -u_d.k (with the agreed energy-valued four-momentum convention), not the COM photon energy as the target threshold. Verify total probability including continuum, baryon/charge/energy/momentum event ledgers, projectile recoil conventions and the time/domain plateau of channel projectors. The one-electron sudden/cusp result or independent-electron determinant is a comparison model; neither becomes correlated two-/three-electron data by declaration.

### Precision nuclear response: `nuclear_precision`

Keep the existing np capture result with its actual EFT order and thermal anchor. A precision update requires a Hamiltonian/current scheme, shared low-energy constants and their covariance, detector response and normalization nuisances. Build direct and inverse reactions from the same amplitude and spin/phase-space factors. Do not sample tabulated temperatures independently. For A=3,4 exclusive channels or Li7 near-threshold reactions, obtain the continuum amplitude or fit a specified R-matrix/EFT model to actual data. Parallelize channel/energy solves; compute thermal kernels and uncertainty derivatives cheaply from retained amplitudes. Report theory truncation separately from quadrature and fit error.

### Charge/cascade reduction: `atomic_charge_cascade`

Use block elimination only when the fast block is transient/invertible and its relaxation is short compared with rate/source/expansion variation. For a column generator partitioned slow/fast, Qeff=Qss-Qsf Qff^(-1) Qfs follows a quasisteady approximation; preserve the initial layer or bound it. Solve sparse linear systems rather than form an inverse. Check positivity, exact particle/charge ledgers and whether eliminating radiative states double counts explicit transport. Test the reduced model against a modest full level model on the actual radiation histories. Cold/high-n dissolution and RR/DR branching need physical rates; a hydrogenic 1s kernel cannot supply all multi-electron levels.

### Full BBN to 17-state interface: `bbn17`

The output registry recovered from R7 is [n,H0,H+,D0,D+,T0,T+,He3_0,He3_+,He3_2+,He4_0,He4_+,He4_2+,Li7_0,Li7_+,Li7_2+,Li7_3+], abundance per baryon in the common-rest specialization. Internal Be donors, excited levels, negative ions, molecules, photons and nonthermal particles must be retained where needed; output dimension 17 does not close the internal dynamics.

Carry one finite BBN checkpoint with a,t,Tgamma,Tnu, composition, radiation and covariance into the late solver. Advance the same clock t(a)=tB+int da/(aH). Use one ionic mass ledger: M_q c²=M_0 c²-q m_e c²+sum_{j<q} I_j. Include composition-dependent rest energy once in the background and reaction release once in energy exchange. Baryon conservation uses A^T nu=0, not unweighted Markov column sums. Charge-state transitions of one tagged nucleus may use a conservative generator; nuclear multiplicity-changing events do not generally do so.

Reuse the conditional Be survival result only within its rate/cosmology/no-new-Be assumptions. Extend hyperfine/continuum electron capture and charge-dependent tritium decay where required. Do not renormalize the retained 17-vector to erase excluded nuclei. Use ancestry bounds for excluded channels if they meet the selected observable budget. Propagate a shared parameter sample through nuclear rates, BBN, atomic evolution and reionization; use tangent equations for a smooth low-dimensional response and sample branch/pole/non-Gaussian uncertainties explicitly.

### Full transport and source histories: `full_transport`

First complete a separate baseline H/He calculation using the selected external histories from R8 source research; it need not wait for all trace-species tasks. For the full network, bind stellar/quasar emissivity, escape fraction, spectral normalization, angular measure and initial radiation from named models. Homogeneous isotropic source histories are a controlled baseline, not measured anisotropic Bianchi data. Use conservative spectral transport, distinguish Q_V from Q_M, preserve photon storage and redshift boundary flux, and apply event/source ownership once. Only after binding actual clocks/currents/observer boundaries should the HE/REI adapters consume the source.

## 4. Return exactly what was run

Return model/deck and executable identities; compiler/library versions; per-partition timing, memory, exit status and logs; raw observables and convergence series; retained uncertainty components; source/rate validity domain; failed cases and cause; and the next dependency. Save a checkpoint after each independent block. Distinguish implementation-verified, numerically checked, physically calibrated and unresolved. A prepared job, a passed runner test and a completed physical calculation are three different statuses. Do not claim the original unpublished author arrays have been recovered merely because an independent theoretical reconstruction converged.

The four historical identity gaps G02.11/G06.04/G08.11/G08.12 require original data if exact historical identity is the goal. The independent physics can proceed without that identity, with its own provenance. No amount of heavy execution reconstructs an author's exact unpublished coefficients uniquely from a paper alone.
