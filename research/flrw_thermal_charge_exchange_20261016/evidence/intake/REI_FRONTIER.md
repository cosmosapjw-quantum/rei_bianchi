# REI frontier intake — 2026-10-16

Pinned canonical head: `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`. PR166 observed open/draft head: `553ce556d9f8662290c000ec675c7e6007c9d895`.

**Do not select source-age convergence as unowned.** PR166 `contracts/NEXT_DAG.json` explicitly owns positive source-matched MD14/signed reference and diagnosis/correction of increasing 8/16/32 age differences on a common chemistry mesh. DOP853 fails an internal negative-photon trial at call291; the supplier's current scientific admission is HOLD.

**Do not recreate a frozen binary charge-exchange kernel.** Canonical `deuterium_charge_exchange.rs` already contains the exact frozen-rate Riccati extent, positivity/conservation, Savin2002 rates, and signed thermal/binding defect ledger. `deuterium_atomic.rs` already provides the D atomic/CX point RHS and a wrapper calling that exact frozen map.

SOURCE011 is actual completed evidence: 24 accepted suffix steps, 504 native plus288 separately charged observer RHS, three analyzed final chemical stages, and6185 terminal entries bit-identical. Its selected second-half EOS correction is3.320956088753001e-15 K. The larger3.322583431789993e-14 K belongs to the discarded FULL trial. Neither number bounds whole-history error or explains the SOURCE009/010 temperature difference.

## Independent candidate for root selection

Advance **thermally self-consistent isolated D/H charge exchange** at fixed proper volume. This changes the mathematical integration problem from the existing frozen-coefficient map while reusing its physical source and ledger.

For forward-positive extent xi,
```
(H0,H+,D0,D+)=(H0_0+xi,H+_0-xi,D0_0-xi,D+_0+xi)
nthermal=nH+nD+ne = constant
T(xi)=(u0-DeltaChi*xi)/(1.5*kB*nthermal)
xi' = kf(T(xi))*(D0_0-xi)*(H+_0-xi)
    - kr(T(xi))*(D+_0+xi)*(H0_0+xi)
```
The density interval is [-min(D+_0,H0_0), min(D0_0,H+_0)]. Intersect it with the existing Savin temperature domain,2.7–200000 K. On the monotone branch before the first equilibrium, invert the scalar time-of-flight integral t=integral(ds/F(s)). A domain-boundary hit is an explicit event. No extrapolation, clipping, full-network activation or new trajectory is required.

A tiny nonduplicate exact oracle uses kf=kr=k0*T/T0. With beta=DeltaChi/u0, F0=k0*(D0_0 H+_0-D+_0 H0_0), K=k0*(nH+nD), and K>beta F0>0:
```
E=exp[-(K-beta*F0)*t]
xi(t)=F0*(1-E)/(K-beta*F0*E)
```
This distinguishes a coupled thermal map from the old frozen map. Additional tiny checks are zero-defect reduction, charge/electron invariance, u+DeltaChi*xi=u0, reverse flow, equilibrium, absent D and a thermal-domain event. No calculations were executed in this intake. Cross-repository active ownership remains for the companion intake.

The JSON contains exact inspected source blobs and all controls. No native/reference execution, code modification, publication, or new resource allocation occurred.

