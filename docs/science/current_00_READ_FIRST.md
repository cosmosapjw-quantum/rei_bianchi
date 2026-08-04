# Stage P0.5-B2C2B0C-R1 — Node-resolved joint chemistry/sink history

## Verdict

\[
\boxed{\text{B2C2B0C-R1}=\texttt{DURABLE\_FAIL\_CLOSED}}
\]

The fixed 46,080-parcel hierarchy was promoted to a node-resolved trial solver, but the independently quasi-static macro cloud closure does not possess a convergent physical history. The coarse run closes photon and H/He nuclei ledgers, yet violates the physical volume, limiter and timestep-refinement gates.

## Decisive failure

During the first interval, post-photoionization macro sink gas approaches \(x_{\rm HII}\to1\). At fixed effective opacity, the neutral cloud area is

\[A\propto1-e^{-\sigma n_H(1-x)R},\]

so the required cloud abundance and mass obey

\[M_{\rm cloud,tot}\propto(1-x_{\rm HII})^{-1}.\]

The exact symbolic limit is divergent. Numerically, one macro would require \(1.118e+08\) times the cosmic H inventory, and the summed target would require \(2.467e+08\).

## Temporal refinement

For the first R1 interval:

- one step: sink H fraction \(0.113327\);
- two steps: sink H fraction \(0.510341\);
- four/eight steps: macro capacity fail-closed.

The two-step result is a factor \(4.503\) above the one-step result. This is not a convergent discretization.

## Coarse diagnostic history

The five-interval coarse history exists only as a diagnostic. Its sink H fraction oscillates between \(0.0481\) and \(0.6818\). The maximum reaction limiter is \(5.351e-02\), and the recorded volume-filling diagnostic reaches \(2.769e+06\).

Photon partition and nuclei identities remain at roundoff, proving that the failure is not lost photons or nuclei. It is the incompatibility of an instantaneous fixed-opacity macro cloud geometry with independently evolved macro ionization.

## Decision

`P0.5-B2C2B-UNRESOLVED-SINK-CLOSURE-LOCK` remains unauthorized. The next stage must first distribute the already validated global reduced-DAE sink moments over macros using constrained mass/opacity moments rather than solving an independent quasi-static cloud abundance in every macro.
