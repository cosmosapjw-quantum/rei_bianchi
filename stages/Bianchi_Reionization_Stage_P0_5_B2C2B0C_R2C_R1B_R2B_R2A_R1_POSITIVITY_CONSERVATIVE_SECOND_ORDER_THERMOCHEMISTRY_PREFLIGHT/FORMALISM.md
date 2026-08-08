# Formalism — second-order positive thermochemistry preflight

## Conventions

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B`
remain explicit.  Internal thermal energy is in erg and time in seconds.

## Material blocks and production--destruction representation

The resolved material vector is

\[
y=(N_{\rm HI},N_{\rm HII},N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII}) .
\]

For a nonnegative pairwise flux tensor \(P_{ij}\), where \(P_{ij}\) transfers
material from species \(j\) to species \(i\),

\[
\dot y_i=\sum_j P_{ij}-\sum_j P_{ji}.
\]

The deterministic stage adapter constructs separate H and He blocks and never
creates H--He nuclei transfer.  Its net reconstruction is hard-gated, but this
representation is not event-unique in the three-state He block.

## MPRK22(1)

With \(\alpha=1\), the Patankar--Euler predictor is

\[
\left[I-\Delta t\,A(P^n,y^n)\right]y^{(2)}=y^n,
\]

and the corrector uses \(\sigma_i=y_i^{(2)}\):

\[
\left[I-\Delta t\,A\!\left(\tfrac12(P^n+P^{(2)}),y^{(2)}\right)\right]
y^{n+1}=y^n.
\]

The matrices have M-matrix form for nonnegative transfer rates.  The implemented
kernel refuses nonpositive or nonfinite states and preserves each block total by
construction.

## Thermal SDIRK2

The accepted thermal candidate is the Alexander two-stage SDIRK method with

\[
\gamma=1-\frac1{\sqrt2},\qquad
A=\begin{pmatrix}\gamma&0\\1-\gamma&\gamma\end{pmatrix},\quad
b=(1-\gamma,\gamma).
\]

It is stiffly accurate and satisfies

\[
\sum_i b_i=1,\qquad \sum_i b_i c_i=\frac12,
\]

with stability function tending to zero on the negative real infinite limit.
Each stage is solved in \(x=\ln T\), so \(T>0\) without clipping.

The nonlinear thermal balance is solved with analytic \(dR/d\ln T\), safeguarded
Newton steps inside the same positive bracket used by the reference bisection,
and deterministic bisection fallback.  The BE predictor and both SDIRK stage
balances use this root backend.

## Local-error gate

For one full step and two half steps, the local estimator is the maximum of

\[
|\Delta x_{\rm HII}|,\quad |\Delta x_{\rm HeII}|,\quad
|\Delta x_{\rm HeIII}|,\quad |\Delta\ln T|.
\]

The hard gate is \(2\times10^{-4}\).  Partitions 512 and 1024 fail; partition
2048 passes in all three predeclared lanes.

## Event-ownership limitation

The same net helium RHS

\[
(-1,0,+1)
\]

can arise either from a direct HeI\(\to\)HeIII transfer or from simultaneous
HeI\(\to\)HeII and HeII\(\to\)HeIII transfers.  Those decompositions have
different reaction and energy ownership.  Hence this stage validates a bounded
net-RHS numerical closure only.  The full-OTS event decomposition must be
source-locked before any production history is promoted.
