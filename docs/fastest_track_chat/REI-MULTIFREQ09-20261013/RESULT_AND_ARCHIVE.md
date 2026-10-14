# RUX-BI-MULTIFREQ09: accumulated-opacity multicolor absorption

Date: 2026-10-13. Parent: RUX-BI-FLUENCE08. Consumer remains SOURCE07-CONSUMER. This is additive theory/reference publication; no production code, default, physical admission, existing review status, or PR body is changed.

## Complete artifact

[Reproducibility archive, Google Drive](https://drive.google.com/file/d/1P7TM74HvxlN64e4NGMzoDNRWiZJuQX_b/view?usp=drivesdk)

- Filename: `REI_BIANCHI_MULTIFREQ09_20261013_REPRO.zip`
- Bytes: **929569**
- SHA-256: `0326f374cb8d43118ca5aefb0c7b877355db800a0eebf20c65cf9c069444ec1a`
- 35 files: Korean 10-page PDF, LaTeX/Markdown, reference code/tests, retained 256-node synthetic trajectory, figures/CSV, original xAct input, failure evidence, parent manuscripts, manifest and handoff.
- PDF: `REI_BIANCHI_MULTIFREQ09_20261013_KO.pdf`; SHA-256 `cb574a07f8ce5903f8e6a4a6589387f504219f957a96fc465b3e2bc9794eff5b`.
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_BIANCHI_MULTIFREQ09_20261013_REPRO.zip`, object `id:BSpOijBcT10AAAAAAD4YUQ`, completed at 2026-10-13T10:58:10Z, 929569 bytes.
- Drive parent `1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ`; upload acknowledged, metadata size and parent matched.
- Both providers acknowledged this archive. Local CRC and per-member SHA/size verified. No remote full-byte restoration test was run: **RESTORE_VERIFIED=false**. No font files are distributed.

SOURCE07 and FLUENCE08 were backed up first in this same run. Their exact sizes, hashes and cloud IDs are in the sibling recovery index at commit `ec0425f56952d74234254517cc27e53cf1c89ed5`.

## Exact six-state construction

Scope: source-free photoabsorption substep with fixed normal-frame energies, bounded nonnegative ground-state cross sections, fixed proper hydrogen density, and finite positive initial photon measure with finite energy. Recombination, CI, Compton, continuous sources and metric evolution retain their own operators.

Let `p=(H0,H1,Z0,Z1,Z2)`, `H0+H1=1`, `Z0+Z1+Z2=Y`, `r=(h,z,v)=(H0,Z0,Z1)`, and `xi=1+2Y-h-2z-v`. Put `s_a(E)=sigma_a(E)/sigma_star` and `k=c*n_H*sigma_star`.

Define the three accumulated absorber exposures and the photon reconstruction:

$$u_a(t)=k\int_0^t r_a(s)\,ds,\qquad d\mu_t=e^{-\mathbf s(E)\cdot\mathbf u(t)}d\mu_0.$$

The fixed initial-spectrum responses are

$$\Psi(\mathbf u)=\int e^{-\mathbf s\cdot\mathbf u}d\mu_0,\quad
\alpha_a=-\partial_a\Psi,\quad
\Psi_E(\mathbf u)=\int E e^{-\mathbf s\cdot\mathbf u}d\mu_0,\quad
\beta_a=-\partial_a\Psi_E.$$

The exact reduced ODE is

$$\dot{\mathbf u}=k(h,z,v),\qquad
\dot h=-kh\alpha_H,\quad \dot z=-kz\alpha_0,\quad
\dot v=k(z\alpha_0-v\alpha_1).$$

The population simplex is invariant. Since `u <= k*t*(1,Y,Y)` and `alpha_a <= sbar_a*N0`, this smooth finite ODE has a unique solution on every finite forward-time interval. Substitution of the reconstructed measure into the original multicolor photon equation proves exact equivalence.

The dynamic dimension is six, independent of spectral node count. The initial spectrum/Laplace response remains retained; evaluating an M-node response is generally O(M), so no measured runtime speedup is claimed.

Photon-charge conservation gives `Psi+xi=N0+xi0` and the optional fifth-state elimination

$$v=h_0+2z_0+v_0-N_0+\Psi(\mathbf u)-h-2z.$$

The six-state formulation is the reference default because reconstructing tiny `v` by differences can lose relative accuracy. In pure hydrogen the reduction is scalar:

$$h(u)=h_0-N_0+\Psi(u),\qquad \dot u=k[h_0-N_0+\Psi(u)].$$

## Spectrum, chronology and common energy

`Psi` is completely monotone and its Hessian is positive semidefinite. For the normalized surviving photon measure,

$$\dot{\overline E}=-k\,\mathrm{Cov}(E,\mathbf r\cdot\mathbf s).$$

Decreasing opacity gives hardening; threshold-edge jumps can give the opposite covariance. Both signs were checked on explicit two-node synthetic measures.

The He generators

$$M(a,b)=\begin{pmatrix}-a&0&0\\a&-b&0\\0&b&0\end{pmatrix}$$

satisfy

$$[M(a,b),M(c,d)]=(ad-bc)\begin{pmatrix}0&0&0\\1&0&0\\-1&0&0\end{pmatrix}.$$

Thus the atomic chronology is retained by the population ODE rather than replaced by one integrated matrix. Photon scalar attenuations can still be integrated exactly.

With `B=chi_H*H1+chi_0*Z1+(chi_0+chi_1)*Z2`,

$$\dot U_{\rm th}=k\sum_a r_a(\beta_a-\chi_a\alpha_a)\ge0,\qquad
U_{\rm th}=U_0+\Psi_E(0)-\Psi_E(\mathbf u)-[B(\mathbf p)-B(\mathbf p_0)].$$

This conserves thermal+binding+photon energy. Parent Maxwell-Juttner electron and heavy-particle EOS gives positive heat capacity and a unique temperature recovery, including the new-electron particle-number term.

## Computable error contract

Let `du=||u-uhat||_inf` and `dp=||p-phat||_1`. For two positive spectral response measures, let `delta1` bound the three alpha-response differences on the exposure box and let `Lalpha` bound their exposure Lipschitz constant. Markov-generator L1 contractivity yields

$$D^+\binom{d_u}{d_p}\le
\begin{pmatrix}0&k\\2k(1+Y)L_\alpha&0\end{pmatrix}\binom{d_u}{d_p}
+\binom{\|\rho_u\|_\infty}{2k(1+Y)\delta_1+\|\rho_p\|_1}.$$

The positive fundamental matrix propagates response/time residuals into populations and exposure. Photon and energy errors follow from the Psi/Psi_E errors. This compares consumed spectral responses, not a falsely small total-variation distance between a continuous spectrum and quadrature delta nodes.

For arbitrary continuous source `dJ_s`, the exact representation gains a history term:

$$d\mu_t=e^{-\mathbf s\cdot\mathbf u(t)}d\mu_0+
\int_0^t e^{-\mathbf s\cdot[\mathbf u(t)-\mathbf u(s)]}dJ_s\,ds.$$

No fixed six-state closure for arbitrary source history is claimed. The report gives the cohort/source-splitting connection to the existing consumer.

## Actual validation

- 12 finite reference cases, 3/8/32/128 nodes, 33 times each; 49 assertion records passed with predefined tolerances.
- Max six-state vs original `(M+5)`-state difference: `5.415667914121514e-13`.
- Max five-state vs six-state difference: `2.0305944425924594e-12`.
- Max photon-charge error: `4.553024623987767e-13`.
- Max scaled total-energy error: `1.8681428237274556e-16`.
- Minimum reconstructed numerical population: `-1.3877787807814457e-17`; the reference DOP853 implementation is not a production positivity-preserving stepper.
- Scalar-H comparison max error `7.666756118851481e-12`; tested trajectory-error/bound max ratio `0.1433567743`.
- All cross sections in the reference runs are explicitly synthetic, not new evaluations of a physical atomic fit. Physical KN quadrature, atomic precision campaigns and full cosmological histories: zero.

Actual Wolfram/xAct ran on the authorized online workstation after the cloud Wolfram connector failed. Runtime **15.0.0**, xTensor1.3.0, xCoba0.8.6, xPerm1.2.4. Two-color radiation divergence, gas chemical+thermal divergence, shared absorption four-force and photon+electron current yielded **4 families / 13 zero scalar residuals**, exit0.

A separate Wolfram algebra subprocess failed (exit2): an illustrative heat definition missed three rate multipliers. The failure is retained. Local SymPy confirmed the corrected ledger; the corrected Wolfram script is explicitly NOT_RUN. A later remote diagnostic command was host-blocked and not bypassed. Do not count the algebra subprocess as passing because the subsequent xAct subprocess succeeded.

No new independent reviewer was available. Status: **derived exact absorption reduction, reference-tested**, not physical/production promotion or an independent scientific acceptance. Preserve prior SOURCE07 review holds.

## Next consumer action

Keep SOURCE07-CONSUMER as the next implementation target. Bind existing `(E_j,N_j,s_aj,p0,n_H)` to this reference within the fixed absorption stage. Return reconstructed photon weights, event rates, binding/thermal increments and the actual residual budget. Keep source/Compton/geometric ownership and energy-domain guards explicit. Do not rerun completed F08 or atomic precision suites merely to use this analytic reference.

Primary context: Pawlik & Schaye (2011), arXiv:1008.1071; Friedrich et al. (2012), arXiv:1201.0602; Mackey (2012), arXiv:1201.5651; Buth (2017), arXiv:1612.07105. The report distinguishes known multifrequency/fluence structure from the direct reduction and does not claim absolute priority.
