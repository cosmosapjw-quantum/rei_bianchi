# HE36 partial Maxwellian moment implementation

Receiving workflow1.0.0 / approval0.2. Code is ready to copy into the separate
HE36 unit after root/independent review. No remote repository was mutated by
this agent. The prior atomic donor survey is complete separately at
`/tmp/he35_survey/atomic_donors/`.

## Delivered interface

`maxwellian_moments.py` exports `PreparedMaxwellianMoments`. Supply energy
endpoints in eV, cross-section endpoints in m², the declared threshold, a
source identity, reduced mass, energy mapping and numerical temperature domain.
The default numerical domain is2000–200000K and the default quadrature isGL16
on each table bin. There is no table interpolation in temperature.

For the CCC87H1 actual source, parse the first two numeric columns only;
cross sections are a0², with noπ or multiplicity factor. Use
`sigma_m2=sigma_a0sq*(5.29177210544e-11)**2`,
`reduced_mass_kg=9.1093837139e-31`, and
`energy_mapping="heavy_fixed_target_incident_electron"`.
Other masses require the explicit manufactured-relative-energy label. This
prevents silently reinterpreting the incident-electron table as qualified
finite-mass relative-energy data.

```python
from maxwellian_moments import PreparedMaxwellianMoments, ME_KG
kernel = PreparedMaxwellianMoments(
    energy_eV, sigma_m2, threshold_eV=13.6058,
    source_id="CCC87:7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae",
    reduced_mass_kg=ME_KG,
    energy_mapping="heavy_fixed_target_incident_electron",
)
result = kernel.evaluate([2000., 20000., 200000.])
alpha = result.alpha_m3_s
beta = result.beta_J_m3_s
gamma = result.gamma_J2_m3_s
delta = result.delta_J3_m3_s
derivatives = result.dlogT_moments_SI  # d(alpha,beta,gamma)/d ln(T)
coverage = kernel.coverage()
```

Output arrays always have a leading temperature-row dimension, including
scalar calls. The four SI moments have units m³/s, J m³/s, J² m³/s and
J³ m³/s respectively. Natural logarithms of those numerical SI values are
stored separately. Underflow/subnormal flags distinguish tiny positive
finite-domain moments from an identically zero supplied table. Conditional
mean incident energy is computed from scaled integrals even when alpha
underflows. Its value and logarithmic slopes are undefined (`None`) for an
all-zero supplied table. Zero-table outputs remain finite-source partial.

## Computational form and reduction

For theta_eV=k_B T/eV_J and a temperature-independent cross section,

    M_j = sqrt(8 eV_J/(pi mu)) theta_eV^(-3/2)
          integral E^(j+1) sigma(E) exp(-E/theta_eV) dE * eV_J^j.

Here E is the numerical energy in eV and j=0..3. Every bin uses a positive
interpolation `(1-t)*sigma_left+t*sigma_right` at GL nodes. Nodes, positive
weights, cross sections and energy powers are prepared once. A single
node-exponential array per temperature batch feeds all four moments. An
anchor at the first positive quadrature node removes the common exponential
before summation; output logarithms restore it. No physical high-energy tail
or lower-source gap is filled. This is numerical quadrature of the declared
finite piecewise-linear model, not an exact quadrature or source-error bound.

The fixed-domain Maxwellian derivative recurrence is

    dM_j/dlnT = M_(j+1)/(k_B T) - 3 M_j/2, j=0,1,2.

The fourth moment is a diagnostic supporting the derivative of gamma, and
does not introduce an additional physical channel. Signed derivative values
are reconstructed from log-absolute values to preserve an otherwise
representable derivative when its undifferentiated moment underflows.

## Actual verification and preserved correction

The frozen `CHECK_CONTRACT.json` preceded execution. One initial bounded
verification passed8/8groups in0.190382575s (command wall1.974469082s):
independent80decimal SI-energy constant-cross-section integrals;
high-precision derivatives of that independent antiderivative;
CCCGL16/GL32 and independent SI-energy QUADPACK comparisons;
mass/cross-section scaling; identical-function bin splitting;
21domain/invalid/full-rate-request guards; underflow/zero-table semantics;
and immutable source identities. No IVP, old suite, benchmark or render ran.

- CCCGL16/GL32 maximum relative difference:2.842170943040401e-14.
- Independent CCCGL16/quad maximum relative differences at2000,20000,200000K:
  3.008704396734174e-14,2.886579864025407e-14,2.7644553313166398e-14.
- Frozen gate for these finite numerical comparisons:2e-9.
- CCC comparison uses9temperatures,4moments; QUADPACK uses3temperatures,
  4moments and86source intervals,29148total integrand evaluations.
- These numbers assess implementation of the declared finite model;
  physical interpolation and omitted-source-tail errors remain unquantified.

Self-review then found one concrete generic-extreme-input defect: multiplying
the scaled numerator by eV_J before division lost1.1364% of the conditional
mean for a manufactured sigma=1e-300m²,1..1.001eV band. The failed fixture,
old source and exact diff are preserved. The fix divides scaled moments
before unit conversion. The one affected fixture was rerun and matched its
independent80decimal reference to the resulting binary64 value (relative0).
No unchanged CCC or8-group suite was replayed. The quadrature, all four
moment/log outputs, derivative recurrence, domains and flags are byte-for-byte
unchanged statements; only conditional-mean evaluation changed.

`FINAL_VERIFICATION.json` maps the initial8passed groups and affected
mean-fix evidence to the final source. There are9unique groups,10group
attempts (9PASS,1preservedFAIL), in3process invocations. Final sourceSHA256:
`644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`.

## Finite CCC values for source-level interpretation

| T[K] | alpha[m³/s], independentquad | beta/alpha[eV], GL16 |
|---:|---:|---:|
| 2000 | 7.2107508159823645e-50 | 14.0102409892 |
| 20000 | 2.74414440739798e-18 | 17.2687065221 |
| 200000 | 1.05663332669931e-14 | 45.3629918341 |

These are partial incident-electron reaction-rate/energy moments. Incident
energy is not automatically common-gas CI cooling. For ground-state
nonradiative CI the chemical defect, rather than all incident kinetic energy,
is the net shared-pool loss when outgoing electrons remain in that pool.
No outgoing differential branching, finite recoil, nuclear stopping, reactive
STF source, or full coupled gas evolution is supplied by this module.

## Dependency/readback sources

- CCC source copied for reading from the exact C22D source hash above;
  the original bytes remain with the nuclear survey agent.
- C22D `ci_finite.py` supplied the explicit source normalization and
  constants. This implementation uses a new independent GL path and does
  not dispatch the donor runner or repeat its existing coefficient suite.
- OfficialNumPy leggauss documentation:
  https://numpy.org/doc/2.1/reference/generated/numpy.polynomial.legendre.leggauss.html
- OfficialSciPy quad documentation:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.quad.html
- Actual runtime versions are inattempt_001.json; the documentation's
  displayed latest version is not treated as the installed version.

## Final acceptance boundary

`require_full_physical_rate=True` is rejected. Off-domain T, nonfinite or
negative cross sections, unordered/duplicate energies, unsupported mass-to-
energy mapping, and unrepresentable intermediate arithmetic fail explicitly.
The2000–200000K numerical diagnostic interval does not expand C22D's separate
active-chemistry contract. Use no new physical rate or higher-T chemistry
admission from this finite numerical witness alone.
