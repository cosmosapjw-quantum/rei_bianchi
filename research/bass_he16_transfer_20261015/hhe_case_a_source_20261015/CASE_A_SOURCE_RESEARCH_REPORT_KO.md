# HHE_AB6: cold AXBI Grackle Case-A non-equilibrium H/He + thermal A/B (2026-10-15 KST)

**Research status:** Original source-rate operator integrated and tested in an isolated Rust experiment. This is a **source-scoped exploratory implementation**, not a full C2-Ray coupled OTS or production EoR global-error certificate. No local Codex or native subagents were used.

## Model/source provenance

- Original cold Bianchi-I owner stayed at git HEAD `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`.
- Original cold AXBI native source epoch SHA256: `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`.
- Experimental separately linked original Rust `librei_microphysics-2db3552c92b16edc.rlib` binary SHA256 `44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f` and compiled full-source identity `fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67`. The whole source epochs differ, but seven selected native source rate/point/EOS method bodies (`igm_rates`, `igm_point_rhs`, `AxbiProvider::{rates,point}`, `IgmGasState::{new,eos,adiabatic_to}`) match byte-for-byte across both records (see `SOURCE_RATE_SURFACE_IDENTITY.json`). Previous verified atomic and transport function surfaces are reused under their separate matching contract. No assertion of whole-binary identity is made.
- Native cold rates are **Grackle 3.4.1**, pinned upstream commit `af7939494ce65007887ada7b98d1813df6843346`, Case-A escape with low-temperature CI floor and documented DR branch. **Do not substitute** warm BASS_HE HE18 FT03/HM12 closure, rates, helium ratios, raw photon stock, or thermal energy.
- Initial experimental gas is T=8.098143045064857 K, fHe=0.2454/[4(1-0.2454)], cold proper nH and nHe in cm^-3, proper time in seconds, thermal gas energy erg/H in native point and eV/H in experimental gas, LRS Bianchi I metric with signature (-+++), source mean redshift 20 -> 19.998.
- This is one initial packet `Nγ0=1e-6 / H` at one original energy node, with no continued emissivity, secondary photon transport, or recombination photon injection. Case-A recombination photons are assigned to the native **escaped radiation** ledger, not silently recycled by coupled OTS.

## Constructive numerical coupling

Let `x=xHII,y=xHeII,z=xHeIII`, `ne/nH=x+fHe(y+2z)`. Photo collisions use the original two reference paths at identical geometrical proper-time midpoints:

- PROJECTED: original `Driver::geometry_map` at each half-step, canonical grid `E_i`, original `AtomicProvider::cross_section` with signature cache; repeated energy-grid reprojection.
- COVARIANT: exact spatial covector `CovariantPhoton` and original `absorb_frozen_gas` reference expm1 absorber, without intermediate grid projection.

For each photon packet, photoevent counts (per H) are `ΔN_j=N_before *[-expm1(-(Σ_j c n_j σ_j(E)) Δt)] * λ_j / Σ λ_j`. They directly change gas fractions `Δx=ΔN_HI`, `Δy=(ΔN_HeI-ΔN_HeII)/fHe`, `Δz=ΔN_HeII/fHe`, while thermal energy gains `Σ_j(E-χ_j)ΔN_j`.

At the same source midpoint, the independently updated gas state is handed to the original `AxbiProvider::point` with **zero additional photo input**, fixed native proper nH,nHe, original `Tcmb=2.7255/a`, and `h=0` because the exactly integrated adiabatic half-step `u->u(a0/a1)^2` is evaluated separately. Its original `igm_point_rhs` supplies the proper-time CI, RR, DR, CE, free-free, photo-independent thermal sink, and CMB exchange. This avoids double counting photoionization and Hubble expansion terms.

The micro source is integrated using checked explicit Heun (SSP RK2) subcycles, each with `Δt≤1e10 s`, and no positivity or source-rate clipping. The original Grackle operational domain T∈[1,10^6] K remains enforced by the native point provider. Alternative `Δt≤5e9 s` is run as an independently compiled micro-step sensitivity reference.

Native event accounting, per H:
\[
\begin{aligned}
Δx&=P_{\rm HI}+C_{\rm HI}-R_{\rm HII},\\
f_{\rm He}Δy&=P_{\rm HeI}+C_{\rm HeI}-R_{\rm HeII}-D_{\rm HeII}-P_{\rm HeII}-C_{\rm HeII}+R_{\rm HeIII},\\
f_{\rm He}Δz&=P_{\rm HeII}+C_{\rm HeII}-R_{\rm HeIII},\\
Δ(n_e/n_H)&=\sum(P_j+C_j-R_j)-D_{\rm HeII}.
\end{aligned}
\]
Here `P,C,R,D` represent proper-time integrated photo, collisional-ionization, radiative-recombination, and dielectronic-recombination event counts divided by nH. Hydrogen and helium nuclear totals remain algebraically constant.

Native micro-energy identity (Wolfram checked):
\[
u_{\rm micro}+B_{\rm micro}+E_{\rm escape}-E_{\rm CMB}=0.
\]
The total source+transport budget includes initial photon energy, final photon energy, adiabatic thermal loss, cosmological photon work, energy-group boundary loss, atomic binding change and native recombination/radiative escaped energy. This is a **calculation-accounting identity**, not an ODE true-error bound.

## Real source outcomes, not full EoR history

54 paired physical conditions, 108 Rust output rows, with `q=-0.005,0,+0.005`, initial `η=0 or 1e-5`, energy indices 5 (HI below HeII), 32 (exact grid HeII opacity threshold 54.42 eV), 33 (above HeII threshold), outer time divisions 1,16,128.

For `q=0, η=0, E0=54.42eV`:
- At one outer step, the midpoint has zero HeII from the initial state and both A/B produce no photo-HeII event. Recombination subsequently creates HeII.
- At 16 steps, projected photo-HeII events are 0.6119734 per injected photon versus **zero** in exact-covariant transport; final `ΔxHeIII(projected-covariant)=-4.8363854675e-5`.
- At 128 steps, projected photo-HeII events are **0.6277021193561264** per injected photon versus zero covariant; final `ΔxHeIII=-4.848315322214525e-5`, `ΔTgas=-0.009629655039089968 K`. The exact-covariant final T≈8.247662459 K. Similar differences occur across q±0.005 and initial η=1e-5.
- Direct photo-HeII *gain* per H is `+6.2770211936e-7`, but the projected lane's native HeIII *recombination excess* per H is `+4.5694480114e-6`, while CI_HeII difference is `~8.14e-18`. The integrated source identity `Δ(fHe xHeIII)=ΔP_HeII+ΔCI_HeII-ΔRR_HeIII` has residual `4.86e-17/H`. Thus the recombination feedback can invert the sign of the final HeIII response relative to the immediate false photo event. The sign of this effect is source- and model-dependent.

The 128-step q=0 eta=0 gas difference is stable when the *internal source subcycle* maximum is halved (1e10→5e9 s): `ΔxHeIII=-4.848315322214525e-5` vs `-4.848344270624860e-5`, a relative change of `5.97e-6`. Outer source-grid projection and energy-grid resolution have **not** yet been independently refined to a true limit.

All 108 source rows were checked against a separate compiled original Rust source-rate provider. In tested data the maximum full global photo+micro+expansion+boundary energy ledger residual is `1.7763568394002505e-14 eV/H`; atomic binding residual `1.4654943925052066e-14 eV/H`; electron-event residual `1.124100812432971e-15 per H`; thermal energy residual `6.938893903907228e-18 eV/H`. Each raw source-epoch and originally compiled metadata remains distinct.

## Performance and next admission

Actual isolated original-code A/B run, same numerical physics output, user Ubuntu 2026-10-15:
- serial `11.43 s`, bounded two-worker parallel `10.49 s` (≈1.09× speedup).
- independently compiled halved micro-step limit `10.21 s` (single measurement, *not* a like-for-like speed comparison because accuracy changes).
- immutable native Driver/geometry/Verner opacity grid cached via OnceLock, low-memory O(case photon stocks) temporary storage; original production Rust code not edited.
- Rust native rate/thermal source semantics verified by direct calls; Python identity and quantitative checks saved in machine-readable form.
- No native model subagent was available: `NOT_RUN`. No local Codex session used.

**Claim policy:** SOURCE_SCOPED_NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED for Case-A source + one-packet transport on high-z short interval. The density, photon injection, complete temperature feedback, coupled OTS, original source BE global error and long zbar20→4 observable have not been independently converged. The next constructive check is 2D convergence in photon energy resolution × source/transport step with ongoing photon source and a source-compatible recombination-photon routing choice, rather than treating this toy threshold signal as full EoR prediction.

**Primary literature:** Friedrich, Mellema, Iliev & Shapiro (2012), MNRAS 421, 2232, Appendix G, https://academic.oup.com/mnras/article/421/3/2232/1077406 ; native Grackle 3.4.1 source `af793949...` in `igm_rates.rs`. Friedrich et al. report notably stricter temperature than ionization-fraction timestep convergence, directly relevant to this coupled non-equilibrium test.
