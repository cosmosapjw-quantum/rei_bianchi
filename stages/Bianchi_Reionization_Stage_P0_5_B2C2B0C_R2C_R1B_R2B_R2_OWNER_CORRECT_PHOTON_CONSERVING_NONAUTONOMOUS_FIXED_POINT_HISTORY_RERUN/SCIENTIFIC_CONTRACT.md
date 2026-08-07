# Scientific contract

- Signature `(-,+,+,+)`, `epsilon_123=+1`.
- Explicit `c`, `hbar`, and `k_B`; CGS microphysics with explicit proper/comoving conversion.
- Material state per node: `(N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved)`.
- Canonical total `kappa_g,J_g` is authoritative; state determines only the conditional owner/node split.
- Four mutually exclusive owners: effective-HI subgrid, resolved H I, resolved He I, resolved He II.
- Subgrid resolved source vector is exactly `(0,0,0)`.
- Positive chemistry is enforced by parametrization/implicit solve and infeasible-step rejection, never clipping.
- Photon-number and energy accounts remain separate.
- Accepted history is committed once after a successful step; rejected attempts and event rollback preserve exact parent bytes.
