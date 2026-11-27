# BASS_HE to rei_bianchi: original V2 He III → He II Lyα local H/He OTS feedback, tick160–162

Date: 2026-11-15 KST. Project source-controlled REI IGM, metric signature (-,+,+,+), gas proper time seconds, c retained, photon energies eV and erg, positive ionization-potential reservoir.

## Authority, claimed new unit, physical relevance

Immutable BASS_HE parent PR153 HEAD b2de625f0f8976c20ccaa21e62610ae42d8bb750. Original REI source-owner PR369 HEAD 645437697d915da45147071e266bc47937e76f6c; sealed F05 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644; original source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b; historical accepted tick160 array cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; separately versioned research V2 t161 SHA256 c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823 and t162 SHA256 35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b. The source-original 3 shape lanes represent ONE physical IGM realization. No original worker/source/history/main was changed; research tick161 and162 remain NONOFFICIAL / production HOLD.

Prior PR153 already evaluated only **local OTS escaped** He II Lyα line energy [0,2.4492444763567325e47] erg over V2 [160,162], source photon number [0,3.7455863979586685e57]. New physical unit actually measures the COMPLEMENTARY original native H I/He I local OTS reabsorbed He III cascade Lyα and corresponding physical ionization-potential and electron-thermal consequences in the *same* original source stage-sites, not another static opacity atlas or new incident G3 photons.

## Derived exact source algebra; original implementation correspondence

Original He II Lyα Eα = 0.75 χHeII = 40.81332 eV = 6.539014765996487e-11 erg; original H and He I thresholds χHI=13.598434599702, χHeI=24.587389011 eV. With native r3cas, original Hummer–Seaton v, f∈[0.1,1.0], and recipient ratio z=κHI,41/(κHI,41+κHeI,41), the locally generated single-line rate is r3cas(1-v). Partition:
  r_HI = r3cas(1-v)f z;
  r_HeI = r3cas(1-v)f(1-z);
  r_escape = r3cas(1-v)(1-f).
For one correlated physical realization r_HI+r_HeI+r_escape=r3cas(1-v).
  dB_Lya = εeV(χH r_HI+χHeI r_HeI);
  dQ_Lya = εeV((Eα-χH)r_HI+(Eα-χHeI)r_HeI);
  dE_escape = εeV Eα r_escape.
Exact event identity dB_Lya+dQ_Lya+dE_escape=εeV Eα r3cas(1-v). Original source EventBox.resolved_heat and EventBox.escaped_energy are respectively dQ and dE_escape. Native full original RHS already includes the LOCAL OTS H/He photoionizations through its A_H/A_HeI event branches. DO NOT add the local absorption events again to population/electron/thermal derivatives.

The native original Alexander SDIRK2 half-step source quadrature uses γ=1−1/√2 and actual source stage and endpoint EventBox, Ihalf=h[(1−γ)rateγ+γrateend]. One original V2 microtick is sum of two native half-step integrals. Source v/f/z interval dependencies make independent channel upper bounds non-additive. Physical conservation is pointwise; verify interval intersection and source identification rather than force equality of separately optimized upper bounds.

## Original-source physical data actually generated

Original 46,080 material integration nodes ×2 genuine V2 source research intervals = 92,160 cell-time physical records. 6 original 46k-node native full/half1/half2 source maps executed on one primary physical lane, 2×14 original signed nucleus/photon/energy ledgers included zero, 0 table events, and four-array exact equality with the archived nonproduction t161/t162 source endpoints. Original frozen V2 common-parent gate <2e-4 and width <2e-3 unchanged; legacy V1 old logT 2.1245050576368385e-4 FAIL preserved. Original outgoing source parent PR153 CSV/JSON bytes reproduced EXACTLY.

| V2 microtick | locally absorbed by H I photons | locally absorbed by He I photons | original resolved OTS heat [erg] |
| --- | --- | --- | --- |
| 160→161 | [9.158488423207021e55,1.1334682011904528e57] | [7.864469958243624e55,9.505586081428103e56] | [6.037891721203950e45,7.413416374949811e46] |
| 161→162 | [9.149877750584127e55,1.1324418907144973e57] | [7.872710563496636e55,9.515833101967510e56] | [6.036279499298829e45,7.411605246095896e46] |
| cumulative | [1.8308366173791148e56,2.265910091904950e57] | [1.5737180521740258e56,1.9021419183395613e57] | [1.207417122050278e46,1.4825021621045708e47] |

Additional cumulative interval sources:
  total native HeII Lyα emitted photons [3.409839541159505e57,4.1617626643985686e57];
  local positive H/He ionization-potential gain [1.0188262035347494e46,1.2429932019384512e47] erg;
  local photoelectron heat [1.2074171220502775e46,1.4825021621045702e47] erg;
  locally escaped photon energy [0,2.449244476356763e47] erg;
  native parent PR153 escaping source upper is 2.4492444763567325e47 erg.
The difference in the last 14 floating digits is outward source rounding, not a new physical effect. Correlation between emitted/absorbed/escaped branches is retained as an interval caveat: summed independent upper bounds exceed emitted upper and may NOT represent a simultaneous realization.

The original native local OTS heat upper per research microtick is 0.198% of the respective original net chemical binding ΔB midpoint magnitude, a small CHANNEL MAGNITUDE comparison; it is not a temperature prediction or extra feedback to add. Original V2 ΔU outer intervals include zero; no unconditional net heating/cooling sign. The local OTS heat lower is strictly positive for these source intervals, but no new source photon direction/spatial emission spectrum is created.

## Validation, environment and hostile referee

The earlier archived REI pinned NumPy2.3.5/Pandas2.2.3/SciPy1.17.0 venv was absent from this new Nov15 host layout. An initial source reproduction under host NumPy2.4.2 FAILED exact research tick161 four-array identity, correctly stopped; it was classified as a runtime/byte-reproduction blocker, not a physical nonexistence or permission issue. A new isolated environment was installed at local private research scratch with NumPy2.3.5/Pandas2.2.3/SciPy1.17.0 and Python3.12.13; original REI source files and global Python unchanged. Under this environment original 6 maps PASS with original research endstate exact four-array identity and all local source stage enclosures. Original-source optimized Python cold replay output four CSV/JSON files BYTE_IDENTICAL to original normal process output (including immutable PR153 source CSV+JSON). Event observer wraps source EventBox only in memory, restores the original event function, no patched owner code.

Independent stdlib second algorithm read all 92,160 physical source rows, recomputed gamma-weighted 4 event-site channel integrals, H/He source identity and binding/photoheat interval overlaps. PASS max scaled integral reconstruction difference 2.6228963820573605e-14 and max independent energy decomposition difference 1.5605496342822071e-15. All 92,160 source-cell original native heat and escape intervals intersect independently reconstructed local channels. Same-author hostile check; no different-author blind referee and no native subagent available. Normal and Python -O source-free tests each 3/3 PASS; intentional corrupted JSON negative case rejected. Source-free public GitHub CI only verifies derived evidence and DOES NOT replay private original research states.

Source CSV SHA256 6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae (92,160 physical rows, 51 columns).
Source JSON SHA256 de1451d19d9f678394e9f22415c740105e2ffa3ed7b482dde2b583442c65a8f7.
Independent audit SHA256 8c096f17aa89cd6003837424262a170182b88ac29d9f8339fac79c420d3d7395.
Old PR153 source CSV/JSON SHA256 56b597b57cb08ac1ab25dfe4f9b2b091ca5e36fc3465a89fc3d6f98769fe5521 and bd2ee6b067f75ebd5032627abe476cfab1c628153d809cffd8016b19f682cb1b, respectively, unchanged in cold replay.

## Claim ceiling / DAG

One substantive original OTS H/He local feedback source unit, not 20 full stages. REI canonical reported 28/88, working 33/88 nonadditive, physical-fast 4/7, BASS_HE physical 14/18, canonical delta0. Original official tick160/131072; research V2 t161/t162 remain officially unaccepted; source photons not transported along actual Bianchi null geodesics. No new RUX04 pass, no CMB observable, no production, no merge or force push, no original gate/source/worker mutation. Next REI owner task is source-matched nonlocal radiation and official V2 continuum/error admission, not additional BASS_HE OTS source-only atlases.

Primary paper: Friedrich et al. (2012) coupled full He/HI OTS, MNRAS 421 2232–2250, https://academic.oup.com/mnras/article/421/3/2232/1077406. Source model precedents do not replace original source authority.
