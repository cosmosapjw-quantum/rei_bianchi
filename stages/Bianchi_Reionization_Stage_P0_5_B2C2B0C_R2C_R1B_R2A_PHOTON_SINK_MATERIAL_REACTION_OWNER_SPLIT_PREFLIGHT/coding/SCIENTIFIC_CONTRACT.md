# Scientific contract

Resolved material state: `N_HI,N_HII,N_HeI,N_HeII,N_HeIII,U_resolved`. Radiation reaction fluxes are group- and owner-labelled absorbed photon rates. The subgrid sink is an unresolved photon-removal owner, not a resolved species state.

Conventions: metric `(-,+,+,+)`, `epsilon_123=+1`, explicit `c,hbar,k_B`; time in s/Myr; rates in `s^-1 cMpc^-3`; opacity in `cMpc^-1`.

Required identities: `sum_owner kappa_g,o=kappa_g,total`, `sum_owner J_g,o=J_g,total`, and exact zero resolved H/He/thermal sources for `EFFECTIVE_HI_SUBGRID`.

NaN/Inf, negative owner mass, unowned current, duplicate owner, clipped capacity, or silent owner reassignment fail closed.
