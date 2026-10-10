# External source contract: bounded global reionization history

Date: 2026-10-10. Role: source-contract contributor, not independent final reviewer.

Decision: the Robertson et al. (2015) emissivity plus Hui–Gnedin case-B coefficient is a literature-supported, physically interpretable **global filling-factor model**. It can support a controlled calculation from z=20 to z=4. It does not establish a complete microscopic CR physical provider, close the existing CR full-history HOLD, or supply a new observational fit. Source byte identity and model adequacy are separate claims.

## Primary source identities

| ID | Versioned PDF and bibliographic identity | Bytes | SHA-256 |
|---|---|---:|---|
| R15 | [Robertson et al., arXiv:1502.02024v2](https://arxiv.org/pdf/1502.02024v2), ApJL 802 L19, DOI 10.1088/2041-8205/802/2/L19 | 1060881 | `40c785185e8924ce241253a415004c7a69fcb47dbe7c79087ccb2d6bdc736581` |
| HG97 | [Hui & Gnedin, arXiv:astro-ph/9612232v1](https://arxiv.org/pdf/astro-ph/9612232v1), MNRAS 292, 27, DOI 10.1093/mnras/292.1.27 | 1383278 | `6ea0b803b554c91d598705f96416e1a8b67549fb02cb567944eaacdba5d148b0` |
| M17 | [Madau, arXiv:1710.07636v1](https://arxiv.org/pdf/1710.07636v1), ApJ 851, 50, DOI 10.3847/1538-4357/aa9715 | 426819 | `084aebac3285d0c732d678f03b27458a9593bc992cdb3ca7d5582ffc8638bfb0` |

All three versioned URLs were retrieved as PDF bytes on the recorded date; complete retrieval metadata are in the companion JSON. The documents are reference material, not deliverable contents: do not include downloaded PDFs or full extracted text in any uploaded project bundle. This contract retains equations, factual parameters, locators, and original analysis only. SciSpace was used for discovery; the numerical contract comes from primary PDFs, not generated search summaries.

## Published inputs

R15 pp. 2–3, equations (1), (2), (4), (5):

\[
\rho_{\rm SFR}(z)=\frac{a(1+z)^b}{1+[(1+z)/c]^d},\quad
\dot n_{\gamma,{\rm com}}=f_{\rm esc}\xi_{\rm ion}\rho_{\rm SFR},
\]

\[
\dot Q=\frac{\dot n_{\gamma,{\rm com}}}{n_{H,0}}-\frac Q{t_{\rm rec}},\quad
t_{\rm rec}^{-1}=C_{\rm HII}\alpha_B(T)(1+Y/4X)n_{H,0}(1+z)^3.
\]

The comoving numerator and denominator must use the same volume unit.

| Parameter | R15 value | Unit / meaning |
|---|---:|---|
| a | 0.01376 | solar masses yr^-1 comoving Mpc^-3 |
| b, c, d | 3.26, 2.59, 5.68 | dimensionless |
| f_esc | 0.2 | escape fraction |
| log10(xi_ion) | 53.14 | xi in photons s^-1 / (solar masses yr^-1) |
| C_HII | 3 | adopted clumping factor |
| T | 20000 | K |
| h, Omega_m, Omega_b h^2, Y | 0.6774, 0.309, 0.02230, 0.2453 | flat cosmology; mass fraction Y |

R15 extends the fitted SFR beyond observed z~10; use at z=20 is an extrapolation. Its optical-depth prescription adds doubly ionized helium at z<=4. The source model itself warns about the near-overlap neutral fraction. These dated inputs are a reproducible baseline, not a current-data fit.

HG97 Appendix A, manuscript pp. 27–29, unnumbered HII case-B recombination entry:

\[
\lambda_{\rm HI}=2(157807\,{\rm K})/T,
\qquad
\alpha_B(T)=2.753\times10^{-14}
\frac{\lambda_{\rm HI}^{1.500}}
{[1+(\lambda_{\rm HI}/2.740)^{0.407}]^{2.242}}
\;{\rm cm^3\,s^{-1}}.
\]

The stated fit accuracy is 0.7% for 1–10^9 K, against Ferland et al. data. This is the **rate coefficient** (RI), not the adjacent recombination-cooling coefficient (RC). Fit validity over that temperature range does not validate this global reionization closure over the same range.

## Derived implementation contract

These are explicit lane assumptions and mathematical consequences, not extra claims about what either original paper implemented.

1. Set X=1-Y and y=Y/(4X). Define the present comoving hydrogen **number** density as n_H0=X Omega_b rho_crit/m_H, with rho_crit=3 H0^2/(8 pi G). Specify the chosen hydrogen mass constant and unit conversion. The density expression in R15's surrounding prose omits a mass divisor; copying it literally as a number density is dimensionally wrong.
2. Convert the comoving emissivity from Mpc^-3 to cm^-3 before division by n_H0 in cm^-3, or convert both densities to Mpc^-3. No extra (1+z)^3 belongs in their ratio. Use physical n_H(z)=n_H0(1+z)^3 for recombinations.
3. Q denotes ionized **volume**, with fully ionized H and singly ionized He inside those volumes and approximately neutral gas outside. Interior electrons are n_e,inside=(1+y)n_H; volume-average electrons are <n_e>=(1+y)Q n_H. Recombination is proportional to Q, not Q^2. Substituting the volume-average electron density into the interior recombination coefficient would mix closures.
4. Adopt fixed T=20000 K and C=3 for the fiducial lane. Changes are sensitivity scenarios and must be labeled. This is not a thermal evolution calculation, a HeI/HeII/HeIII network, residual-electron recombination history, or spatial radiative transfer.
5. The interval z=20 down to z=4 with Q(z=20)=0 is an explicit initial-value problem. No paper-backed claim of exactly zero earlier ionization follows. For the single-He closure, treat the endpoint as z=4 approached from above (4+), without a HeIII switch. A total Thomson optical depth requires an additional specified history below z=4 and above z=20; the interval contribution alone must be named accordingly.
6. With time in seconds, set S=dot(n_gamma,com)/n_H0 and R=t_rec^-1. Convert redshift using dt/dz=-1/[(1+z)H(z)]. Record whether H(z) includes radiation; changing a background cosmology is a scenario choice, not a fresh fit of the R15 source parameters.
7. Enforce 0<=Q<=1 with a separately recorded nonnegative rate U: Qdot=S-RQ-U. For Q<1, U=0. At Q=1, U=max(S-R,0), allowing Q to decrease if S<R. For nonnegative S and R, the lower boundary is invariant without negative-value clipping.
8. Track I=int(S dt), D=int(RQ dt), E=int(U dt), all photons per hydrogen nucleus, so Q-Q_initial=I-D-E. The integral E is a bookkeeping remainder beyond the capped filling factor, not an evolved radiation energy density, escape fraction measurement, or specified absorption process. A finite-step cap must preserve this identity with the same within-step recombination integral; silent clipping is insufficient.

## Scope and case-B caution

M17 section 1 and section 3 explain why the standard source-minus-recombination equation can overshoot Q=1: it assigns all escaped ionizing photons to diffuse gas. Its improved treatment includes Lyman-limit absorbers. M17 section 4.2 also uses case A when recombination photons redshift below threshold before reabsorption. Therefore case B is a declared R15-style closure, not a universally correct property of the IGM. A cap plus E ledger fixes bookkeeping and bounds, but it does not implement M17's post-overlap physics. In particular, do not infer a Lyman-alpha forest neutral fraction or photoionization rate from Q=1.

## Reject common incorrect substitutions

| Incorrect substitution or claim | Required handling |
|---|---|
| (a,b,c,d)=(0.015,2.7,2.9,5.6) called the R15 fit | Different fit; use the verified R15 tuple above. |
| log10(xi_ion)~25 used with SFR density | That normalization is per UV luminosity, not the R15 per-SFR quantity. |
| lambda=157807/T | Missing factor 2; lambda=315614/T. |
| 2.753e-13 prefactor, or HG97 case-A coefficients | Wrong fit; preserve case-B prefactor 2.753e-14 and all exponents. |
| xe averaged over volume inserted in RQ | Produces a spurious second Q. |
| n_H0=X Omega_b rho_crit without mass conversion | Mass density is not number density. |
| Case B plus separately reionizing every ground-state recombination photon | Double counts the effect represented by case-B closure. |
| Capping Q establishes realistic post-overlap radiative transfer | Unsupported. |
| Historical fit, selected cosmology, or byte hash proves current observational agreement | Unsupported. |

Recommended source lane: **R15 + HG97-B**, with these assumptions frozen. HM12 is a separate possible lane and has not been authenticated by this contract. Do not extend a bounded HM12 table to z=20 without explicit data support or a labeled extrapolation model. The original CR physical-provider full-history status remains **HOLD**.
