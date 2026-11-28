# Eq. (18) ambiguity policy

The attached CPC paper's Eq. (18) is not used literally for a generic
implementation because the printed expression mixes primed and unprimed
`n2` symbols.

R3 does not infer what the authors' unavailable code does.

Instead:
1. implement the unambiguous Eq. (17) for Z1=1,Z2=2;
2. construct the complementary Z2 ordering at fixed (k,m);
3. require exact Appendix-A DIRECT and INVERSE regression;
4. independently validate selected labels against large-R real-TERM energies.

Status:
`GENERIC_EQ18_PRIME_AMBIGUITY__PRESERVED`
`HEH_SPECIFIC_CORRELATION_MAP__IMPLEMENTATION_VERIFIED`
