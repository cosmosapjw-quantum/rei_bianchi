# HE27 donor validation factorization (source only)

For a fixed old Killing-direction cosine `nu`, define `P` as the photon energy
at HE25 birth and `E=P G(x,nu)` at a later emission proper time.  The HE26
Jacobian is `J=exp(-3x)/G²`.  During the newborn source integral, `nu` is held
fixed and `dP=dE/G`.  Thus every true cut child in one physical threshold band
has the same summed moment as the physical birth integral multiplied by
`J/G=exp(-3x)/G³`.  The angular weight is applied exactly once.

The fixed physical vector is

`M_band = integral_[Elo,Ehi] shape(E) * (1,E,sigma_HI,sigma_HeI,sigma_HeII,
sigma_HI*(E-I_HI),sigma_HeI*(E-I_HeI),sigma_HeII*(E-I_HeII)) dE`,

with `Elo,Ehi` from `13.6,24.59,54.42,100 eV` and original physical binding
energies `I_i`.  Summing `angular_weight * J/G * M_band` over original GL
directions gives the same HE26 donor target for the eight admitted moments.
No old photons, source vector, cutoff partition, chemical RHS, native owner,
gas work or transport term is changed by this identity.

The implementation checks GL64 and GL128 physical integrals independently at
construction, then checks every direction and threshold band against the
actual inherited v3 source vector on the original one-sided mask.  The
unchanged relative admission gate is `3e-13`; a failure raises a typed error.
Bitwise source-vector controls, quadrature agreement, timing and source hashes
are recorded in `SOURCE_FAST_VALIDATION.json` alongside this proof.
