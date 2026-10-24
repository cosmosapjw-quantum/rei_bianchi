# Independent bounded kernel review — 2026-10-22

Decision: **PASS_SCOPED** for C3 manufactured local representation and CR1 primary-table transcription/numerical diagnostic. No concrete repair is required. One fresh-context read-only review covered implementations and saved raw outcomes. No source/Git mutation, historical campaign execution, scientific rerun, or extra review layer was performed. Requested reviewer role: Astra tier; actual runtime model identifier is not exposed.

## C3 local representation

Read rei_bianchi/intake/AGENTS.md, C3_FROZEN_CONTRACT.md, c3_probe/local_source.py, run_probe.py, BINDINGS.json slots, RESULT.json, EXECUTION.json, stdout/stderr, COMMANDS.txt and IMPLEMENTATION.md. Saved execution hashes match the reviewed files:

- local_source.py: e6818290a2f50f4e6872eff861f1aec1c461c21539751dbc4763496461549a79
- run_probe.py: e52bca4f756e4b00fdab3ae385beb2b918c0a96576b594b589d9a0e803e1433d
- input/BINDINGS.json: 274ceb3d67f1d2144966d07c0b92397a31aa4adfe2ae8d2496b0629cee9e1aff
- frozen contract: 4445e9532c7766faa8db6f74bfd7681768d2b8ab876aefb049bc6837af77563f

The event factorial, positive-product logarithms, exact-zero branches, scaled source calculation and fixed-scale Jacobian agree with the frozen equations. Reduced polynomial exponents preserve multiplicity-one zero-boundary derivatives while DD at zero has zero first derivative. Sources use signed fsum. Applicability states remain distinct; UNRESOLVED raises explicitly. Integer bookkeeping agrees with the A/Z/q slots. Decimal references use declared decimal strings and direct products independently of the log implementation.

The single scientific invocation exited 0: Python 3.12.14, wall 0.100463153 s, CPU 0.094889168 s, max RSS 19,968 KiB, recorded limits 30 s wall/CPU and 256 MiB. Stderr is empty. Seven fixtures, nine applicability controls and five other controls pass.

| Fixture | Evidence | Maximum scaled source/Jacobian relative error |
|---|---|---:|
| Ordinary DD | Decimal R=1.2e-23; positive zero-initial TII source; identical-reactant factor 1/2 | 3.2911e-15 |
| Tiny DD | Decimal R=5e-209 at DII=1e-104; raw/scaled positivity | 3.1716e-15 |
| Underflow unary | Decimal R=1e-334; raw 0; UNDERFLOW; logR=-769.0634210600113; scaled daughter source 1.0000000000000371e-230 | 3.7118e-14 |
| Zero-stock unary | Exact-zero source; nonzero boundary derivative 1.0000000000000371e-230 | 3.7118e-14 |
| One-zero binary | Zero source; positive derivative near 5e-101; delta_N=-1, delta_e=0, delta_C=-1 | 4.2669e-14 |
| DD zero boundary | Exact-zero source and first derivative | 0 |
| Moderate two-event sum | Independent Decimal source/Jacobian comparison | 1.9985e-15 |

All nonzero scaled comparisons satisfy 2e-12 without an absolute floor. Moderate central differences give maximum relative discrepancy 1.377800e-10 against 2e-7, using positive moderate inputs only. They do not certify boundary or underflow cases. SUPPORT_ZERO, ABSENT and UNRESOLVED controls pass for all three event declarations. Nonconserving DII→H1II is rejected. Both negative controls exhibit the expected failure: raw multiplication before scale division gives zero and R/Y at zero raises ZeroDivisionError.

The 17→21 map is [0,1,2,3,4,5,6,7,8,9,10,11,12,17,18,19,20]. Full A.Y=1; omitted Li6I=1e-8 leaves projected A.Y=0.99999994 and deficit 6e-8, without renormalization. Binary64 deficit error 3.158136e-17 is below the recorded four-ulp bound 8.881785e-16. Decimal event balance retains positive tiny rates rather than passing by total underflow.

Scoped admission covers manufactured representation, zero-onset differentiation and scale handling only. Next executable action: small supplied-branch event assembly with provider-matched coefficients. Off-grid coefficient policy, thermal/fast dependencies, physical branch/energy providers and coupled production remain open. No IVP or physical rate-builder call was made.

## CR1 source reconstruction

First visually inspected bass_cr/primary/SW91_p305.png. Equation (16) assigns b_i to 1s→2s; equation (17) assigns c_i to 1s→2p. All 36 Table 3 numbers match new_unit/code/hydrogen_excitation.py in sign, digits, power of ten and temperature column. Columns are 2e3–6e4, 6e4–6e6 and 6e6–1e8 K. This independent visual comparison resolves column assignment. Printed p304 PDF text additionally identifies ln(T), the Boltzmann factor and 0.75 Ry threshold in equations (10), (12) and (13).

Read hydrogen_excitation.py, verify_diagnostic.py, README and saved RESULTS.json. Horner differentiation gives dlog(q)/dlog(T)=P′+Delta/(kT). Upper regions own internal boundaries; original jumps remain. Out-of-range inputs return NaN/False. The gas loss and photon gain share one signed energy flux under the explicit prompt-decay/optically-thin closure.

Saved evidence: 126 cases against 80-digit direct polynomial evaluation; maximum relative rate roundoff 3.262552e-12 and absolute log-slope discrepancy 4.743920e-13, below 2e-10. Seven domain controls pass; paired-energy residual is zero. Largest original boundary jump is 0.0059620345 relative at 6e6 K for 2s. This is arithmetic verification, not independent atomic-scattering accuracy.

The 201-point saved C22B history contains 71 valid samples and 70 adjacent valid intervals, covering duration fraction 0.0215754927. Partial trapezoid excitation loss is 0.0489597873 eV/Href; invalid gaps are not bridged. This remains a partial saved-history diagnostic, not a full integral, continuous coverage guarantee, global error bound or active trajectory. Saved result records zero ODE runs, RHS calls and active C22B changes.

Scoped admission covers source transcription, coefficient/slope implementation and numerical/ledger diagnostics. Below-2000-K coverage, higher-n/He/Li excitation, D/T isotope transfer, optical-depth feedback and active integration remain open. Next action: publish the additive verified diagnostic or scope its integration separately; unchanged campaigns need not be rerun.

Review operations note: a read-only JSON summary initially encountered max() on the all-zero DD fixture; its corrected summary did not invoke either kernel or alter raw evidence. The first attempt to write this review was rejected before process creation by an exec-server transport disconnect; no scientific result was affected.
