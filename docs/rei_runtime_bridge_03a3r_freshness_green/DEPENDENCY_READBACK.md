# BASS / REC dependency readback for REI 03A3-R1 closeout

## BASS state-surface contract

The required BASS analysis distinguishes six semantically different state surfaces:

```text
GRID_F_Q_E               f(t,q,e)
PSTF_F_AELL_Q             F_Aell(t,q)
J_I_AELL                  momentum-integrated J_Aell^(i)
G_ANGULAR_ENERGY          radially integrated G(e)
FLUID_COMPONENT_SUMMARY   rho, p, q_a, pi_ab
POLARIZED_COHERENCY       coherency / spin state
```

The basic exact representation pair for a general frequency-dependent source is

```text
f(q,e) <-> F_Aell(q)
```

whereas `J_Aell^(i)` and `G(e)` require an explicit source-weighted projection or spectral-closure certificate. Radial and angular product workspaces are independently constrained, generically by

```text
N_work >= N_out + N_chi
L_work >= L_out + L_chi
```

REC owns the representation-neutral source authority. BASS owns state evolution and representation machinery. REI runtime success cannot silently replace this contract.

## Live BASS readback

```text
repository  cosmosapjw-quantum/bass
PR          #116
state       OPEN / DRAFT / MERGEABLE
head        bc7ea693bd8ac4f14376aaac51d4007467702803
```

The role-graph count contract remains:

```text
formula-consumer pairs           10
implementation-role rows         11
named source symbols             12
explicit absent implementation    1
```

The single explicit absent implementation is REI generic photon direction flow. Local replay history shows that the Python verifier, Python 9/9, Wolfram validator, and MUnit 11/11 had passed at prior heads; the remaining failures were strict-JSON receipt serialization/publication defects. Fix3 was published after replacing Association value recursion. The current exact head still requires a final local replay with nonempty atomic JSON receipt and exit code 0. No consumer runtime parity, `J/G` closure, provider, or science promotion is established.

## Live REC readback

```text
repository  cosmosapjw-quantum/rec_bianchi
PR          #55
state       OPEN / DRAFT / MERGEABLE
head        5372556d91c07e0714929dfd948ca7fbf4405118
```

The R5D static handoff contract is present and its static workflow passed. The actual trusted RF-00 payload install and backend cone run remain unexecuted. Therefore:

```text
NO_REC_SOURCE_INTEGRATION
NO_GRID_PSTF_NUMERICAL_PARITY
NO_SOURCE_IDENTICAL_PHYSICAL_FACE
NO_PROVIDER_EXPORT
NO_PASS_REC_PHYSICAL_SPLIT
NO_PASS_RF04
```

## Effect on REI

Neither dependency opens the REI provider gate. The current REI node is governance-only and changes no BASS/REC source, representation, runtime, or claim.
