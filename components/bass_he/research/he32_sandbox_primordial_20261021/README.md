# HE32: sandbox-complete primordial H–Li LRS Bianchi I pilot

This portable research unit computes non-tilted LRS Bianchi I evolution from
mean redshift 20 to 2, with separate signed matter, photon and neutrino stresses,
and a coupled primordial atomic photoionization/recombination network. It has
no NCP, compiler, online rate service or original worktree dependency.

The selected model contains **8 primordial nuclei and 21 atomic charge states**:
n; H-1, D, T in charges 0–1; He-3, He-4 in charges 0–2; Li-6, Li-7 in charges
0–3. Electrons are reconstructed from ionic charge. The exact isotope-sharing
subspace uses 9 charge fractions, and restores all 21 populations in every NPZ.
This is a prescribed-UV, isothermal, positive-atomic-ion pilot. It does not
implement every unstable isotope, negative ion, molecule, or all nuclear
reaction channels as a fully reactive production network.

## Read the completed campaign first

The Git branch carries executable code, pinned inputs, six SVG figures, summaries,
review evidence and raw-data hash manifests. The complete numerical deliverable
is the verified archive **BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz**:
394 NPZ files with 394 case receipts, all PNG/SVG figures, and all 30 stage archives.
The Git branch deliberately has no `results/cases/*` pairs and no PNG copies.
An inventory or a detached Git blob upload is not a branch publication of data.
See `delivery/DATA_DELIVERY.json` and `delivery/FINAL_BACKUP_ACK.json`.

Archive SHA-256:

```text
27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a
```

The executed reference environment is Python 3.12.14 with NumPy 2.3.5,
SciPy 1.17.0 and Matplotlib 3.10.8. Use the publication metadata revision
`9179848428510efcc88c2b5da72efc9a71ef2182` (P4) or a later documentation-only
revision when reading delivery ACKs. The P3 code/evidence revision is their
subject and predates those ACK files. From that final publication checkout:

```bash
python3 -m pip install -r research/he32_sandbox_primordial_20261021/requirements.txt
bash research/he32_sandbox_primordial_20261021/run.sh plan
```

For the existing campaign, download the full archive and set `HE32_ARCHIVE` to
its absolute path. Verify its SHA-256 against the value above. Extract only its
results into a fresh directory so that the archive's older publication notes
cannot replace the final Git code and ACKs:

```bash
HE32_ARCHIVE=/absolute/path/BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz
sha256sum "$HE32_ARCHIVE"
HE32_RESTORE=$(mktemp -d /tmp/he32_saved_XXXXXX)
tar -xzf "$HE32_ARCHIVE" -C "$HE32_RESTORE" --wildcards 'research/he32_sandbox_primordial_20261021/results/*'
HE32_RESULTS="$HE32_RESTORE/research/he32_sandbox_primordial_20261021/results"
bash research/he32_sandbox_primordial_20261021/run.sh plot --out "$HE32_RESULTS"
```

With the delivered figure manifest and unchanged plot source, `plot` reports
`REUSED_COMPLETE_RENDER`: no IVP and no new rendering. The catalog's NPZ paths
are relative to its directory. Existing PNG/SVG files can also be opened directly.
For a deliberately requested independent saved-data readback, the helper accepts
`--results "$HE32_RESULTS" --out <new-evidence-directory>`; the completed readback
is already included and does not need repeating.

`results/SUMMARY.json`, `results/CATALOG.json`, `results/ANGULAR_GUARDS.json`
and `results/figures/FIGURE_MANIFEST.json` identify the scientific inputs and
actual saved trajectories. `results/cases/*.npz` in the archive is the numerical
deliverable. Open NPZ files with `allow_pickle=False`.

## Intentionally compute a new pending campaign

The code is independently runnable without the delivered raw results. On a host
with no completed or failed registry record for the identities in question:

```bash
bash research/he32_sandbox_primordial_20261021/run.sh run --max-workers 6 --reserve-cpus 1 --reserve-gib 1
```

The `run` action integrates pending identities, reuses valid completed results,
checks two angular guards, builds a 392-case catalog and renders six PNG/SVG
figure pairs. An empty compatible output requires **394 IVPs**, including the
two L24 guards; the three L16 preflight points are reused in the main sweep.
The existing campaign is complete, so archive restoration is the default.
A fresh output path must not be used to bypass a completed/failed global registry
or a partial attempt. Incomplete and failed attempts remain visible and are not
silently retried. All native numerical libraries use one thread per worker.

## Observables and scientific scope

For D=diag(-1,-1,2), sigma=sD and pi_X=p_XD, the convention is the spatial
orthonormal Frobenius norm:

* Sigma_F = sqrt(6) abs(s)/H; signed_Sigma = sqrt(6) s/H.
* P_X = (8 pi G/c^2) sqrt(6) p_X/H^2 for SI energy-density stresses.
* Pi_m=abs(P_m), Pi_r=abs(P_gamma+P_nu), Pi_total=abs(P_m+P_gamma+P_nu).

Signed components are summed before taking a norm. Matter stress belongs to
the existing collisionless nonbaryonic massive component (f_m=0.1). The
primordial atomic gas uses the explicit isotropic-stress closure pi_b=0;
non-tilt alone does not imply that closure. The gas supplies electron density
to photon Thomson scattering and optical depth. Neutrinos remain collisionless.

The gas has fixed temperature 20000 K, an external photon-number spectrum
proportional to E^-2.5 on 5.392–60 eV, and
Gamma_HI=1e-12 expit((6-z)/0.3) s^-1. Photoionization and total radiative
recombination (case A) use source-pinned Verner/VF fits. CI, DR, charge exchange,
thermal balance and source emissivity evolution are outside this closure.
The effect of those omissions is not bounded by the nuclear freezeout bound.
The high Li stages remain zero for the adopted spectrum and initial state;
their operators and output channels are retained.

In redshift-dependent histories, z denotes mean redshift, 1+z=1/a. Directional observed redshift in
an anisotropic geometry differs. Elapsed-Gyr panels measure proper elapsed
time since z=20 and do not claim an independently calibrated age at z=0.

Read `HE32_THEORY_KO.md` for derivations, rate provenance, isotope assumptions,
and the conditional nuclear reduction bound; read `RESULTS_KO.md` for the
executed outcome and its limits.

## Grid and computational design

```
Sigma_F0 = [0, 1e-4, 1e-3, .01, .03, .1, .3, .6]
P_m0     = [-.0006, -.0003, -.0001, 0, .0001, .0003, .0012]
P_r0     = [-.0024, -.001, -.0003, 0, .0003, .001, .0048]
```

The 8×7×7 grid samples both stress orientations, zero controls and visible
strong-shear regimes. Every initial angular distribution satisfies its
nonnegative-support constraint; a physically impossible Pi is not introduced
solely to enlarge a plot. Discrete parameter maps are not interpolated.

Reflection-even transport reduces the L16 state to 39 variables. Together
with 9 chemical fractions, optical depth and three integrated source budgets,
the coupled system has 52 variables, versus 97 in the corresponding unreduced
representation. This is a state-count reduction, not a measured speedup.
FV quadrature, source normalization and the BDF tolerances remain fixed.

The solver uses rtol=3e-11, atol=3e-13, max d(ln a)=0.025, and 201 saved
nodes. The mixed Jacobian has exact linear/chemical blocks and exact H-chain
terms for chemistry. The smooth geometry/FV dependence uses four central
finite-difference columns. No clipping, renormalization or fast-math is used.

## NCP and concurrent work

On the NCP 64-core/128-GiB host, the same command can request up to 64 workers:

```bash
bash research/he32_sandbox_primordial_20261021/run.sh run --max-workers 64 --reserve-cpus 2 --reserve-gib 16 --seconds 3600
```

Actual admission is limited by current affinity, cgroup quota, measured CPU
headroom, RAM headroom and shared CPU/case leases in
`/tmp/cosmosapjw_hpc64_cpu_leases`. The default leaves two CPUs available; an
operator may choose zero reserve when those resources are available. Other
jobs are never stopped. The 1-GiB/worker allowance is an admission budget,
not a benchmark of RSS. Existing complete identities do not need NCP replay.

## Artifact-loss recovery

The original complete campaign was lost from scratch during an interrupted
cloud-upload wait. Its 394 successful global receipts survived and were
preserved. `evidence/recovery/` records the incident, all original receipt
hashes, and the explicit artifact-recovery execution. Scientific source/input
identity is unchanged. No failed original identity was retried.

The optional `--recover-missing-artifacts MANIFEST` is narrowly guarded:
the original registry receipt must have its recorded SHA-256, COMPLETE status,
exit code zero and result_valid=true; both original JSON and NPZ must be
absent. New recovery receipts get a separate suffix while the same shared
CPU and identity locks are retained. Original failed receipts are ineligible.
Failed or partial recovery attempts remain preserved within the same recovery
namespace and output path; using a new recovery ID/output to bypass that state
is prohibited by the execution contract.
Do not pass the old incident manifest for a new scientific campaign.

## Evidence, publication and handoff

`DAG.json` lists optimization O.C1–10, physics P.R1–10 and final coding F.C1–10.
The Git `checkpoints/` directory contains stage manifests and receipts; the full
archive also contains the 30 create-only stage tar archives.
The stage source/evidence snapshots bind numerical data through their raw
manifest; the final full archive contains the actual NPZ payloads as well.

`delivery/` contains publication/readback and provider receipts. Interrupted
Google Drive uploads have UNKNOWN outcomes and are not counted as verified
backups. Git publication and verified Dropbox archives are reported separately.

Use `CODEX_HANDOFF.md` or `NEXT_THREAD_HANDOFF.md` to continue from the completed
pilot without restarting literature work or repeating unchanged IVPs.
