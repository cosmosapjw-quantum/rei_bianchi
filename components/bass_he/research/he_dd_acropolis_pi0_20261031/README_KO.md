# BASS_HE PR136 | ACROPOLIS v1.3.1 coupled cascade from measured coherent-pi0 daughter photons

## Scientific identity and execution

- Parent Draft PR135 SHA: `36c3c30dde29be5837985c84ec8326935e17ee9a`. The parent and its source science are immutable and unmodified.
- Input user-supplied ACROPOLIS source `acropolis-main.zip` SHA-256 `1d933f8d53c614d379166ada9319b4188ec45c0b74e065ba790034da41f0d9e1`, `VERSION=1.3.1`, GPL3. Source is imported **unmodified**; do not call this an upstream Git commit/tree SHA because the supplied ZIP lacks `.git`.
- Source Rambo et al. (1999), *Nucl. Phys. A* **660**, 69–83, DOI 10.1016/S0375-9474(99)00383-8; supplied PDF SHA-256 `0221c872f2ed44f35e215b86fd068569bd3af113cca0baafce96ecee17894d3a`.
- Source MacCormick et al. (1997), *Phys. Rev. C* **55**, 1033–1038, DOI 10.1103/PhysRevC.55.1033; supplied PDF SHA-256 `2fe2558f443e107a0ae2e04d4707ea25fe327f8f77f7b6be9f62c74452a09bb7`.
- Parent PR134/PR135 source EXFOR CSV is imported read-only; no external source values are silently replaced. The parent PR135 Git diff stores the `pi0_physics.py` inside its verified ZIP rather than as unpacked Git content; therefore this new add-only subtree contains a **byte-exact owned source snapshot** `src/pi0_physics.py` with SHA256 `c19b64cc63593803eccf9bfb77462bf691c26ed1226fc749e39390274f1c129c` (not an external third-party library). No parent file is modified.

## Original physics addition

The previous PR135 followed **prompt pi0 daughter photons only above 150 MeV**, with no secondary e± or photonuclear reaction network. This unit performs a source-angle-conditioned continuous photon injection into the **genuine ACROPOLIS 1.3.1 photon/electron/positron coupled steady cascade** down to its native 1.5 MeV floor and computes six target-typed photodisintegration responses, i.e. a first-generation pion Green response.

For photon energy E and alpha rest mass Mα, with physical mass-energy notation throughout:

`s = (Mα c²)²+2(Mα c²)E`;
`Eπ*=(s+(mπ c²)²-(Mα c²)²)/(2 sqrt(s))`;
`pπ*c=sqrt((Eπ*)²-(mπ c²)²)`;
`β_CM=E/(Mα c²+E)` and `Γ_CM=(Mα c²+E)/sqrt(s)`;
`Eπlab=Γ_CM(Eπ*+β_CM pπ*c μ)`;
`Eγ±=(Eπlab±pπlab*c)/2`.

Let the measured angular support quadrature define normalized `w(μ)` only on observed angles. The daughter photon source per *produced* pion is

`Sγ(Eγ|Einc)=2 B_2γ ∫_observed dμ w(μ) 1[E−(μ)<=Eγ<=E+(μ)]/(E+(μ)-E−(μ))`,

with exact photon count `2B_2γ=1.97646` and exact photon energy moment `B_2γ <Eπlab>`. Rambo Table 1 angle bins are used at source-matched incident energies 206,216,229,241 MeV, **not at interpolated cross-sections outside their source bins**.

ACROPOLIS solves the stationary coupled three-species Boltzmann cascade at fixed Planck temperature Tγ(z) = k_B T_CMB,0 (1+z) (in MeV). Its internal QED cross sections and numerical solver use natural units ħ=c=k_B=1. We preserve dimensional units in external physics contracts. The photonuclear event response for target nuclide A is `P_A,c=∫ dEγ Fγ(Eγ,T) n_A(T) σ_A,c(Eγ)`, with `n_A` target typed: D target uses n_D, He4 uses n_alpha, Be7 uses n_Be7. At 1st-order abundance response, gross D births are `P_alpha,npD+2 P_alpha,dd` and D destruction is a *separate* `P_D,np`. No full coupled BBN abundance evolution is run.

The original injected gamma's first-pion factor is inherited from PR135: `P_pi0_first = (c n_alpha σ_coherent_pi0)/[Γ_QED+c n_alpha σ_abs_total]`. MacCormick Sec III, Eq. (1) explicitly includes neutral-only π0 events inside total absorption; the pi0 cross section must NOT be double counted. Rambo Table 2 provides total coherent π0 cross section including acceptance/interpolation and 7% common systematic; Table 1 supplies measured angular distribution with acceptance gaps and insufficient full-angle covariance.

### Results with 120 energy bins per decade (ACROPOLIS default)

12 actual source-conditional coupled cases: input gamma E=206,216,229,241 MeV at z=10^4,10^5,10^6. Stored 3-species continuum 3048 energy rows plus 12 distinct grid checks. At E=216 MeV and z=10^5:

- `D_birth_per_produced_pi0=7.819991487670358e-4`
- `D_birth_below_150=7.722809654510288e-4`; **98.7572642%** of gross D births occur from secondary photons <150 MeV
- `D_birth_above_150=9.718183316006932e-6`
- `D_birth_per_original_gamma_first_pi0_then_cascade=7.413938952865802e-7`
- `D_birth_coupled/gamma_only=1.001394928993945` at this z, rises toward ~1.61 at z=10^6 in the frozen model, but high-z (NE96 vs NE120) differs by ~1% and remains numerical CONCERN.
- Maximum single produced-pion alpha-photodisintegration response on this 12-case grid is <0.0093, supporting perturbative *photonuclear* opacity at this approximation order.

The pion prompt 2γ branching is 0.98823. The remaining branch is not silently assigned to heat. The alpha nuclear recoil and other pion daughter channels are not deposition. The Hubble expansion while cascade equilibrates is neglected (quasi-static fast interaction). All fields are source-conditional to the original parent FLRW default BBN abundances, no native BASS gamma source, no cosmic R_event or heat_rate. All 17 ACROPOLIS nuclear channels remain defined by its original cross-section fits; only 6 target-typed gross responses are explicitly tabulated here, *not* 17-channel abundance integration.

## Tests and numerical limitation

`unittest` source/integration 11/11 normal and 11/11 Python -O PASS (run logs in `evidence/`). Parent PR135 23/23 normal PASS. Wolfram independent pion threshold 137.4207069015 MeV, two-body endpoint and energy moment checks PASS. Source-projection gamma number exact to floating precision; max relative injection energy projection error <=1.870e-5 at 120 per decade. z=10^4 and 10^5 D gross births at 216 MeV NE96->NE120 relative shifts 4.27e-5 and 1.27e-4; z=10^6 relative shift ~9.89e-3, **do not claim subpercent convergence at z=10^6**. Distinct-author R06/C09 native reviewer tools are unavailable; same-context explicit blind referee performed in `notes/BLIND_REFEREE_KO.md`.

## Reproduce

In a Git checkout containing parent PR135 subtree, provide an unmodified path to ACROPOLIS 1.3.1:

```
export ACROPOLIS_SOURCE_DIR=/path/to/acropolis-main
export PYTHONPATH="$ACROPOLIS_SOURCE_DIR:${PYTHONPATH:-}"
bash research/he_dd_acropolis_pi0_20261031/REPRODUCE.sh
```

The private complete ZIP also contains the exact supplied original ACROPOLIS ZIP, original PDFs, and parent source snapshot; `REPRODUCE.sh` can restore the ZIP when present. No code from ACROPOLIS is modified or committed in our public GitHub subtree, and private raw original PDFs are excluded from that Git commit.

## DAG and claim admission

`Central 28/88`, `HE physical 14/18`, `canonical_delta=0`. Local model micro=1/1 scoped. `kappa=null`, `R_event=null`, `heat_rate=null`, `L4=false`, `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `AUTO_NEXT_NODE=false`. The new physics product is the bounded **fixed-FLRW coherent pi0-daughter coupled-EM gross photodisintegration Green response**; not an active cosmological field theory, not observed D/H or deposition.

Next: iterate pion regeneration as nuclear source feedback with source-owned light-nucleus channel exclusivity, incorporate D-fast stopping/deposition and a genuine BASS native high-energy gamma source if one exists, and validate high-z cascade against pinned ACROPOLIS/BBN observables. Keep real independent-author audit outstanding.
