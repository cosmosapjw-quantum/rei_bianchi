# VigilODE affine prefixes for a frozen native source-age model

This directory integrates the original VigilODE affine error transport module
with coefficients exported from the frozen REI native implementation. It asks
how changing birth clocks alone changes surviving photons when source packets,
energy nodes, endpoint geometry and endpoint gas are held fixed.

This is a new declared fixed-source, fixed-opacity model. It does not run a new
cosmological history or replace the nonlinear native solver. The existing native
time HOLD and age32 NCP READY states are not changed.
`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## Inputs and source identity

The native source revision is `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`.
`prepare_export.py` calls the existing manifest-checked `prepare_native.prepare`
function. It creates a separate runtime copy, appends one read-only prepared-node
accessor, and derives a separate executable example. The original generated
`positive_native.rs` remains unchanged. The accessor validates through the
existing `evaluate(ab, nh, 0)` and returns prepared node values; it does not
change reconstruction, rates, or the transformed native RHS.

There are exactly 64 original source injection templates, 896 nodes per template,
and 57,344 rows in `inputs/nodes.csv`. Four settings use these same rows and
weights. Settings 8, 16 and 32 assign each contiguous source cohort group its
native proper-time midpoint; setting 64 uses every original midpoint. No packets
are merged, reconstructed, deleted or replaced by evolved endpoint photons.

The exporter compares births, proper birth times, physical source vectors,
encoded source vectors and source inventory exactly against the archived age64
setup. Endpoint geometry uses the archived `setup.x1`; frozen gas fractions and
thermal energy come from the archived endpoint. The latter are
`[0.010065857799832125, 0.010066719415292124, 0.000999219556540277]` and
`1.1243735845579859 eV/H`.

Each CSV row records source cohort, cell and node identity, reference energy,
number weight, all three cross sections and excess energies, physical energy,
all three absorption hazards, original birth log-scale and proper birth time.
Exported binary64 weights, rates, energies and clocks define exact real inputs
to the declared model. In particular the certified kernel sums the imported
species hazards exactly and multiplies by the exact difference of imported
clocks. It does not certify the earlier native floating point coefficient
calculation as an exact atomic-physics evaluation.

## The certified calculation

For each node the study evaluates survival, energy, first and second age moments,
and species absorption events. The species share is the exact imported species
hazard divided by the exact sum of imported hazards. Passive zero-hazard nodes
retain their entire source weight. The photon ledger encloses
`surviving number + sum(species events) - initial number` and must contain zero.

The exponential kernel range-halves exact rational optical depth until it is at
most one half. Odd degree 19 and even degree 18 alternating Taylor partial sums
bound the reduced exponential. Rational-to-binary64 conversion compares the
candidate's exact rational value and steps outward until the comparison proves
the bound. The original VigilODE directed products square the interval back to
the original depth. For depth at least 752 the result is `[0, smallest positive
binary64 subnormal]`; positive upper bounds are retained even when central
outputs round to zero. `THEORY_KO.md` gives the model and proof details.

The affine study compares labelled source cohorts after both paired births have
occurred. Its local defect is the weight times `1-exp(-Lambda*birth_time_gap)`.
The original `AffineErrorMap`, `parallel_error_prefix` and reusable
`AffinePrefixWorkspace` evaluate the recurrence on later-birth events and a final
observation-time tail. The global minimum sensitive hazard gives a valid but
loose first bound. The added grouped method keeps each exact species-rate tuple's
constant total hazard, evaluates the original prefix separately in each group,
and sums final group bounds in a fixed sorted order. Both retain the original
source labels and age-rate correlation.

The sharp per-node final bound and grouped prefix are independently rounded
upper bounds on the same real quantity. Their floating point endpoints need not
order. Their minimum is another valid upper bound. These photon-number bounds
do not certify first or second age-moment differences; passive nodes can change
age moments when their clocks change.

### Completed fixed-data result

| Birth groups | Central surviving N | Central U (eV/H) | Central N difference vs 64 | Grouped affine upper bound on absolute N difference |
|---|---:|---:|---:|---:|
| 8 | 1.296397120090e-07 | 1.761997297127e-06 | -1.291403161341e-09 | 1.2923127689727070e-09 |
| 16 | 1.296607543069e-07 | 1.763374631415e-06 | -1.270360863444e-09 | 1.2882258655815744e-09 |
| 32 | 1.298638373257e-07 | 1.774361899442e-06 | -1.067277844595e-09 | 1.2502515736715599e-09 |
| 64 | 1.309311151703e-07 | 1.821872035172e-06 | 0.000000000000e+00 | 0.0000000000000000e+00 |

The final grouped kernel completed in 51.048 seconds, with 53,408 distinct cached
exponential evaluations. The single native coefficient export, including native
compilation, took 11.802 seconds. The initial global-minimum prefix was roughly
1,356–1,438 times looser than the sharp bound; the grouped prefix is within about
7 parts in 10^15 of the independent Decimal100 direct defect. These are timings
and bound comparisons within this model; they are not solver speed comparisons.
All four photon ledger intervals contain zero, and 10,880–11,040 central
underflowed node populations retain strictly positive interval upper bounds.

### Passive mass and sensitive population

The total N table is dominated by an invariant zero-hazard population. Exactly
4,096 rows contribute passive mass
`2567757288181244159093 / 19807040628566084398385987584`, approximately
`1.2963861367952044e-7/H`. Subtracting this exact dyadic mass from the existing
certified total intervals gives:

| Birth groups | Sensitive N interval (/H) | Signed relative sensitive difference vs 64 |
|---|---:|---:|
| 8 | [1.0983293258238907e-12, 1.0983301709774838e-12] | [−0.9991502303953932, −0.9991502284342793] |
| 16 | [2.2140627217826137e-11, 2.2140628063006203e-11] | [−0.9828699413248649, −0.9828699393743761] |
| 32 | [2.2522364606161115e-10, 2.2522364690676477e-10] | [−0.8257459300091148, −0.8257459281613881] |
| 64 | [1.2925014906580857e-9, 1.2925014915032395e-9] | Exactly [0, 0] |

Thus the invariant passive mass masks substantial sensitivity to coarsened clocks
within the positive-hazard subset: the coarse sensitive populations are about
99.915%, 98.287% and 82.575% lower than setting 64. The signed relative intervals
use exact Fraction subtraction and division with a strictly positive reference
denominator, followed by checked outward binary64 conversion. This reporting
split reuses the original model and calculation; it adds no dynamics.

The separate archived evolving native endpoint has N=`1.2909104481275381e-9/H`.
Its source hash is checked before reporting that value. Neither the fixed-model
total nor its sensitive subset establishes trajectory closeness to the archived
native history. `results/ANALYSIS.json` records this distinction explicitly.

## Original VigilODE code and offline dependencies

`rust/src/vendor/{affine_transport,directed}.rs` are unmodified source files from
VigilODE revision `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406`.
`rust/VENDOR_PROVENANCE.json` pins their SHA256 hashes. The upstream MIT license
is included. A thin local compatibility layer supplies the three `CoreError`
variants required by these modules. This is vendored module integration, not an
installation or admission of the full VigilODE solver.

The directly pinned dependencies are Rayon 1.12.0, num-rational 0.4.2,
num-bigint 0.4.6, num-traits 0.2.19, serde 1.0.228 and serde_json 1.0.145.
The latter enables `float_roundtrip`. `Cargo.lock` pins all 22 packages;
`rust/vendor` and the portable Cargo configuration include their sources and
licenses for an offline handoff. No faer, Krylov solver or nonlinear integrator
is built.

## Reproduce

An existing Rust 1.94.1 prefix is sufficient. Choose a new task runtime directory;
the runner sets its own Cargo cache and target without repurposing HOME.

From this directory, reuse the bundled immutable coefficient export and rebuild
entirely offline:

```bash
python run_study.py \
  --runtime /absolute/path/to/new-runtime \
  --rust-prefix /absolute/path/to/rust-1.94.1-prefix \
  --bundled-inputs --offline
```

To obtain coefficients from the original native input instead, omit
`--bundled-inputs`. The runner automatically uses the restored original input
folder or the frozen donor archive if present. It also supports explicit
`--native-input-dir`, `--archive` or `--repo`; the existing preparer checks every
native source file against the 153-file frozen manifest. With no local source it
uses the original preparer's public source retrieval and manifest validation.
No user file reconstruction or manual native editing is required.

A native export has a 120-second subprocess cap. Rust test and diagnostic commands
have 240-second caps and two Cargo build jobs. A completed export can be reused
with `--reuse-export /absolute/export/path`; its receipt and file hashes are
checked before reuse. A second export into the same runtime is refused.

## Results and verification

`results/STUDY.json` contains full intervals, central values, both affine methods,
all global prefix leaves/radii, group work counts and group final bounds.
`CASES.csv`, `BOUNDS.csv` and `ANALYSIS.json` summarize the same data.
`results/global_min_before_grouping/` preserves the original completed diagnostic
and its logs before the evidence-driven grouping improvement. These are the same
four scientific settings, not additional independent cases.

The Rust tests exercise outward rational conversion at normal, subnormal and
midpoint boundaries; exact zero and positive underflow bounds; and the original
affine prefix against an exact rational oracle at every prefix. They also check
workspace/API agreement and Rayon 1/2/4 byte parity. The unmodified upstream
arithmetic test remains included.

`verify.py` independently compares 17 exponential fixtures with Python Decimal at
100 digits, independently recomputes the full labelled sharp defect with Decimal,
checks ledgers and passive invariance, rehashes all 153 original
native files when they are present, and checks unmodified upstream module hashes.
It includes a concrete correlation counterexample: weights `(1,1)`, hazards
`(0,1)`, observation time 1, and births `(0,1)` versus `(1,0)` have equal unlabelled
birth and hazard marginals but surviving numbers `2` and `1+exp(-1)`. The actual
label-preserving defect encloses their difference. All reported results must be
finite.

`IMPLEMENTATION.json` records owned paths, hashes, actual command invocations,
wall times, unique scientific setting counts and remaining limitations.
