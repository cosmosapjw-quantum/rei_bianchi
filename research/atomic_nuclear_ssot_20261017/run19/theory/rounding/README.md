# RUN19 C7 — stored-node cubic arithmetic enclosure

## Actual result

A new standalone Rust program reused the unchanged RUN18 VigilODE directed.rs
and the exact centered_weights/weighted_channels function fragment of the frozen
RUN19 generic implementation. It evaluated 32 admitted source-table stencils at
six specified binary64 theta values: 0, 1/4, the stored binary64 value of 0.371,
1/2, 3/4 and 1. All 16 stored channels were included, including zero padding.

The resulting 3,072 cases contain 2,754 positive polynomials and 318 exact zeros.
An independent Python Fraction calculation verified every ideal polynomial
against the interval, every error bound against the exact rational difference,
and the rounded kernel output against an independently evaluated nearest-
arithmetic expression with the same operation order.

| Quantity | Actual value |
|---|---:|
| Largest exact-rational relative error, displayed as binary64 | 2.9515449298378586e-16 |
| Largest directed relative error upper bound | 8.824802554719956e-16 |
| Rust kernel and CSV writing time | 0.004069594 s |
| Whole Rust process time | 0.005666434 s |
| Python exact-rational verification | 0.140331155 s |
| Fixture export + process + exact verification | 0.158380453 s |
| Compilation, separately measured | 0.435188692 s |
| Native RHS / source-function / IVP evaluations | 0 / 0 / 0 |

The exact rational fraction for the worst relative error is retained in the
result JSON. It was found in channel12 at stored cell6338 and theta=0.371.
These maxima apply to this finite saved fixture. They are not a supremum over
all cells or all real theta.

## Computational definition and proof

Let v0,...,v3 be the four saved binary64 coefficient values, interpreted as exact
real numbers. Let theta be a specified saved binary64 value in [0,1], also
interpreted as an exact real. Define the degree-three Lagrange polynomial

P(theta) = -theta(theta-1)(theta-2)v0/6
         + (theta+1)(theta-1)(theta-2)v1/2
         - (theta+1)theta(theta-2)v2/2
         + (theta+1)theta(theta-1)v3/6.

Starting from degenerate intervals for these inputs, every subtraction,
multiplication, division by2 or6, and addition uses the preserved directed
kernel. Composing its outward elementary-operation enclosures gives a finite
binary64 interval [L,U] containing P.

The separately evaluated frozen nearest-arithmetic kernel gives p_hat. The
interval difference point(p_hat) - [L,U] contains p_hat-P. Its outward magnitude
B therefore satisfies |p_hat-P| <= B. Whenever L>0, directed division gives the
reported relative bound B/L. If P and p_hat are exactly zero, only the absolute
zero statement is made.

This proof concerns one polynomial with stored inputs. The Python verifier does
not approximate P numerically: binary64 inputs are converted to exact Fractions,
the Lagrange formula is evaluated with rational arithmetic, and all three
inequalities are compared as rational numbers.

## Original source reuse and input identity

- Generic crate source SHA-256:
  7c45be5d93778d33d6c300b063b08efc4649c0106f26ac22720220328be4988f.
- Exact extracted kernel fragment: 460bytes, SHA-256:
  7fd3c482b72cabea575e61df3378d3a38e742bb380184dc534de3c112f4994f8.
- VigilODE directed.rs: 17,215bytes, unchanged SHA-256:
  2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814.
  Its MIT license is retained in execution01/source/VIGILODE_LICENSE.
- Original native default cache SHA-256:
  dcfa521f60165632e6fa1c0d10473b194c8aab73844ee0a44ed2454e18f7a23b.
- Cache source/algorithm ID:
  53f101a30c0d6fdae246eb6ca545660e8bab5aaf22e34787c6ba15fd1ec8fcc4.

The runner verifies these original bytes before selecting input rows. The cache
has 32,742 admitted central cells, of which32 evenly distributed admitted cells
are selected. No table, source coefficient or old trajectory is recomputed.
No generic/native/cache-bound source is edited.

The only support layer around the imported arithmetic is a two-variant
CoreError/CoreResult shim. No new package dependency is required. The original
kernel's unused transcendental and test code remains in its retained source but
is not invoked by this experiment.

## Scope of the new arithmetic term

This calculation isolates the last algebraic part of a coefficient evaluation.
It does not include:

- Decimal physical-model constants versus stored binary64 constants.
- Source-fit accuracy, or the binary64 evaluation of a source formula.
- Rounded ln/exp used to construct the table nodes.
- Rounded ln(T), cell selection or theta construction from a query.
- A derivative/Jacobian, gas/opacity feedback, or a trajectory error.

The native wrapper's exact CI-floor and structural-zero postprocessing is
separate from this raw-kernel comparison. Zero cases remain exact here.

Combining this term with the earlier fourth-derivative interpolation bound
requires independent source-node and query-coordinate uncertainty bounds.
The earlier weight norm at most5/4 supplies the map for nodal uncertainties.
The present finite arithmetic result supplies no missing source-function
interval automatically.

## Reproduce in a fresh output directory

Run from this directory, with explicit restored RUN18/RUN19 and Rust1.94.1 paths:

~~~bash
python3 run_rounding_enclosure.py \
  --run19-root /path/to/research/atomic_nuclear_ssot_20261017/run19 \
  --run18-root /path/to/research/atomic_nuclear_ssot_20261017/run18 \
  --rustc /path/to/rust-prefix/bin/rustc \
  --output /path/to/new-output
~~~

The binary has a2second runtime limit. Compilation is separate and needs only the
existing Rust standard library. The exact command, exit codes, source fragments,
raw CSV inputs/results and executable identity are preserved. The first PATH
probe found no rustc; the already-installed prefix recorded by Unit B worked.
There was no installer, external dependency fetch, test rerun or native IVP.

The selected C9 review remains a separate artifact in
../reviews/CUBIC_NATIVE_REVIEW.json. Both this C7 unit and that single review are
complete; no further review or refinement loop is requested.
