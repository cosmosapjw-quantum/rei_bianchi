# BASS_HE → REI F05 원본 광자 이온화 결합에너지 및 1차 광가열

2026-11-01 | source-native physical contribution | Draft/HOLD | One scientific unit; not a new canonical DAG node.

## 1. 원본 입력·근거

- Original REI source TAR SHA256: a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.
- Accepted 46,080-cell tick160 state array SHA256: cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.
- Native original 26-event kernel SHA256: 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.
- Original continuous RHS SHA256: b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36.
- Source PR: REI #355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00; group source receipt SHA256 5f050d6c57cfc06a80af5e02c2c64f2cba25776f618dd2b3890cbfa4dcb57fd9.
- BASS_HE original ionization potentials: HI 13.598434599702, HeI 24.587389011, HeII 54.41776 eV. Native REI source group currents, supports and excess energies are used, not PW19 external incident spectrum.
- Original REI group 0 has no supported resolved absorber, group 1 HeI, group 2 HI+HeI, group 3 H/He but upper photon current only 1e-323/s.

## 2. 원본 46,080셀 물리 계산

Accepted source tick160, proper time, original 26-event F05 source, four-group H/He photoionization. The intervals below are in s^-1 for event rates and erg/s for both energy powers.

| Species | Photoionizations/s | Positive chemical binding reservoir source (erg/s) | Primary excess photoheat (erg/s) |
|---|---|---|---|
| HI | [6.098784367254445e47,6.109750644912204e47] | [1.3287478936007087e37,1.3311371268414556e37] | [3.054698729304746e37,3.0601914098799483e37] |
| HeI | [5.065687377970238e48,5.083051028870021e48] | [1.995543460473579e38,2.0023835825375072e38] | [5.160230479636213e37,5.17915487935958e37] |
| HeII | binary64 subnormal, physically negligible | binary64 subnormal | binary64 subnormal |
| Total | [5.675565814695681e48,5.6940260933612425e48] | [2.128418249833649e38,2.1354972952216537e38] | [8.214929208940958e37,8.23934628923953e37] |

Midpoint fraction: chemical binding 0.7215549133971356 of (binding + primary heat). HeI contributes 0.937618721751496 of binding source and 0.8926211678405518 of resolved original photoevents. Native G1 approximately 4.65e48 events/s; G2 approximately 1.035e48 events/s. G0/G3 negligible to resolved H/He events.

These are positive photo-origin binding and thermal source terms, NOT net chemical dB/dt or net gas heating. Frozen tick160 positive binding rate times a 4.87184874916821289e9-s proposed step would be about +1.038657580736829e48 erg but is NOT the true integrated tick160→161 result, which remains NONAUTHORITATIVE. Original source is frequency-group reduced and cannot establish full photon energy conservation or photon-spectrum closure.

## 3. Direct derivation and verification

Native J_g, external opacity E_g, global source moments S_s, original coefficients a_sg:
D_g=E_g+sum_s(a_sg*S_s),
q_sg=a_sg*S_s/D_g,
R_sg=J_g*q_sg,
Bdot_sg=1.602176634e-12*chi_s*R_sg,
Qdot_sg=1.602176634e-12*native_excess_sg*R_sg.

Fixed forcing source moment derivative:
d(Bdot+Qdot)_g/dlnS_k=1.602176634e-12*J_g*q_kg*[chi_k+native_excess_kg - sum_s q_sg*(chi_s+native_excess_sg)].

Wolfram symbolic residual: {0,0,0}; allocation sum: 1. Original 46,080-cell full source run exited 0; exact native HI, HeI, HeII fields and total heat interval overlaps 4/4. Original REI #355 independent group receipt Decimal high-precision algorithm: 12/12 source channel rate and binding overlap, 4/4 group primary heat and photon-rate overlaps. Three-moment finite difference max scaled error 5.308590411952111e-9 (criterion <1e-5). Same-author checks, distinct external blind referee NOT_RUN. Initial independent audit had a test-key typo, repaired without changing physics or tolerance.

Source-free immutable receipt checks read only frozen derived outputs, never the original REI source. Python 3.12 NumPy2 host displayed legacy compiled numexpr/bottleneck optional-import ABI warnings; source/full numeric run finished exit 0 and produced correct outputs, classified environment warning not physics failure.

## 4. Evidence identity, scope and drift

Output CSV 12rows SHA256 73f1c739ab1ea3d940abca44edacca4a54e94e3a937a25a98b63fd065bd8bfc3.
Full science JSON SHA256 d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8.
Independent receipt SHA256 e2f5f91a3637842facdb587739f2c5a84c2858ac27edf0a7c55f38607a0e28aa.

Parent BASS_HE PR148 source head at original branching 3e4713b83d097d26b7ed985d158d895b0408fd1a. Concurrent upstream PR148 head later advanced to de2ae2685e186b76dad51b7e18a8c8cbb0578c3b adding finite-clock theory only; we did not rebase. Separate BASS_HE PR149 Draft/HOLD. Original source, worktrees, original worker, accepted state, main and production unchanged.

Progress at each bounded phase: REI central 28/88_REPORTED, REI working 33/88_REPORTED, REI physical fast 4/7_REPORTED, BASS_HE physical 14/18_REPORTED, canonical delta 0. This is ONE supplementary original-source energy partition unit, NOT twenty canonical nodes. Next source owner: original local causal spectral-angular photon Jnu with radiation emission and absorption, OTS, cooling, Bianchi proper clock and versioned original F05 tick161 admission before claiming integrated gas or CMB observable. Stop PW19 static opacity atlas or duplicate review loops.

References: Verner et al. (1996) ApJ 465 487 https://www.pa.uky.edu/~verner/photo.html ; Taira et al. PW19 https://doi.org/10.5281/zenodo.15367103 ; source original REI PR355 https://github.com/cosmosapjw-quantum/rei_bianchi/pull/355.
