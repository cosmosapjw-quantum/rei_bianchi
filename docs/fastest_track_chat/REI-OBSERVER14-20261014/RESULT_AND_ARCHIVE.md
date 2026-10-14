# RUX-BI-OBSERVER14: fixed-observed-redshift optical depth and visibility

2026-10-14 KST. Derived, symbolically checked and numerically checked on declared inputs; no separate scientific reviewer. This additive document changes no production source, PR body, scientific admission, optional-channel state or prior failure. Immediately before publication PR83 was open/draft/unmerged at fd6f811a65cdf527d315b8fcc12fd00d2cb8b9f2 on forward/rust-reion-kernels-20260922.

## 1. Artifacts and recovery

[Full compact proof and results in native Google Docs](https://docs.google.com/document/d/1vok_GrtuU1iFiT_WM7KSlpNg1hqsseTiyJp0s7toqKo/edit). Document creation, text insertion, move to existing folder 1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ and text readback succeeded. Revision AHj4eMRXCJS-jtAe9_0XeSy0zbPZ-eLjtM8X-KOdcsq_3MP2CIBOicnln-rMjjhH8f4zKdqDtl--xAlhXYatdbFH8zQdW-7-Ou7n_JRh4e4.

[Reproducible archive in Dropbox](https://www.dropbox.com/preview/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_BIANCHI_OBSERVER14_20261014_REPRO.zip)

- 59857 bytes; 13 flat-layout members; no font binaries.
- SHA256 ec290f04afa616ca4e0ec9caf3b7298690845caf7042a2386de28c074aa16b78.
- Dropbox id:BSpOijBcT10AAAAAAD4lKQ, rev65dba9c89327c0af03d47, server modification2026-10-13T15:38:51Z.
- Local SHA256 and ZIP CRC passed; server metadata matched59857bytes. Complete remote restoration was not run.
- Contains REPORT_KO.md with22 numbered equations, R1-R10 state, actual parent CSV, successful cloud Wolfram inputs, selected normalized returned fields, failed Python pilot/source/log and recovery provenance.

The native Google Doc is a separate semantic proof/results backup, NOT a second byte-identical copy of this ZIP. Host container/Python ClientError prevented host attachments/PDF. Raw Drive upload failed its file-reference contract, and a remote rclone transfer was blocked. Neither failure is reported as upload success.

Before this new work, [THRESHOLD13's chat-preserved equations were reconstructed](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/fd6f811a65cdf527d315b8fcc12fd00d2cb8b9f2/docs/fastest_track_chat/REI-THRESHOLD13-RECOVERY-20261014/RECOVERED_THEORY_KO.md), published and saved to Dropbox. Recovered Markdown7877bytes SHA25615c94189637f722313b45686134ec04079a92da54160c7a5da2c24cee1ccaa2e; Dropbox id:BSpOijBcT10AAAAAAD4kjA. [Native Drive reconstruction](https://docs.google.com/document/d/1gqFAmIvCoL75lbufvDU7g-9HCd5NnS5FJ45Euzs27cc/edit) was also written, moved and read back. Original THRESHOLD13 raw CAS/numerical receipts were not recovered: historical numerical claims remain transcript evidence.

## 2. Source reuse actually inspected

- SHEAR12 archive776788bytes, SHA2563b275b00a9542f34a1e4075c7eb1ab8f7248a63e65226d4be40756a5789b2ce9; its synced bytes and CRC were checked. Extracted RESPONSE_HISTORY.csv SHA25669bceac64e356d202c4cc4cb8c3db35d9e37c632df7d37bc6219f7c53a696927.
- BASS_HE PR40 THEORY15 at1b4ed28d82a90a810e159801bb95b4f19f9f22d0, complete THEORY15.md: use the total free-electron number current, including active electrons when that model is selected; keep model and numerical opacity errors separate.
- WU088_HH PHYS25 at a4476944dad44ae3ec6c5d5a39cca87fa432fbed, HANDOFF_KO.md: threshold coefficient versus full rate, tagged/event convention and unresolved high-energy tail remain distinct. HH is not activated here.
- bass_cr PR51 live head15193ccf88207de3a5134a4dc56c72e8ed1c7262, retained same-event/current-error structure.
- bass PR141 live head d520c5e47ebf5cf218351082430ae3ef5e1ab3ec, finite-history electron/visibility and explicit observer tail. Its prelaunch executable-hash hold is not changed.

These are applicability mappings, not transfers of those sources' numerical constants. Historical2026-10-12 DAG pending values are not treated as current status.

## 3. Observer-centered geometry and endpoint proof

Use signature(-,+,+,+), proper time, c explicit, prescribed a_i=a exp(epsilon B_i), trace B=0, same mean a and matched initial matter/source. Fix observer time t_o and observer-tetrad unit direction n. Let D=B(t_o)-B(t), S=dot B. Conserved spatial covariant photon momentum gives

    Z_epsilon(t,n)=1+z=(a_o/a)*sqrt(sum_i n_i^2 exp(2epsilon D_i)),
    n_i(t)=n_i exp(epsilon D_i)/rho,
    h_epsilon=sum_i(H+epsilon S_i)n_i(t)^2,
    d(log Z_epsilon)/dt=-h_epsilon.

The primary identity is FPU15(arXiv1410.8473), sectionIV.1. Require a common monotone inverse bracket h_epsilon>=h_min>0 and the stated C3 regularity. Endpoints stay away from intrinsic threshold events. For X=X0+epsilon X1+epsilon^2 X2 and t_epsilon=bar_t+epsilon t1+epsilon^2 t2, put d=D:nn,cD=D^2:nn,s=S:nn at bar_t. Expanding log Z gives

    t1=d/H,
    t2=(cD-d^2-s*t1-dotH*t1^2/2)/H.

The observer-sky averages are <t1>=0, <t1^2>=2tr(D^2)/(15H^2), and

    <t2>=tr(D^2)/(5H)-2S:D/(15H^2)-dotH*tr(D^2)/(15H^3).

No emission-angle average is substituted for the observer solid-angle average.

## 4. Optical-depth and normalized-geometry response

Let chi=c sigma_T n_e, using the total free-electron current in the non-tilted family. Keep an explicit tail beyond fixed t_b<=t_o. For chi=chi0+epsilon^2chi2 and a common isotropic tail, let R2 be the fixed-time integrated2nd coefficient including intrinsic threshold surfaces where required. Moving the lower limit yields

    tau1=-chi0*t1,
    tau2=R2-chi0*t2-dotchi0*t1^2/2,
    <tau2>=R2-chi0*I2/(5H)+2chi0*S:D/(15H^2)
             +(chi0*dotH/H-dotchi0)*I2/(15H^2), I2=tr(D^2).

If a first-order opacity or anisotropic tail is supplied, its terms must be added; they are not assumed away in a general model. THRESHOLD13's intrinsic event contribution and this observer endpoint contribution are separate.

With Q_ij=(15/2)<(n_i n_j-delta_ij/3)tau1>,

    Q_ij=-(chi0/H)D_ij,  Z*d(tau0)/dz=chi0/H,
    D_ij=-Q_ij/[Z*d(tau0)/dz],  S_ij/H=Z*dD_ij/dz.

This follows from the sphere fourth moment and inverse time derivative. It cancels the electron-density normalization in this matched, no-first-order-matter-anisotropy response class. For a measured/computed finite-epsilon quadrupole it diagnoses epsilon D at leading order. No observational tau tomography is claimed.

## 5. Visibility, folding and error transfer

For P=exp(-tau), P1=-P0*tau1, P2=P0*(tau1^2/2-tau2). Therefore

    <P2>=P0*(chi0^2*I2/(15H^2)-<tau2>).

The variance term survives even when the first sky mean vanishes. On a monotone redshift branch,

    g_z=-dP/dz=chi(t(z))*exp(-tau)/[Z*h(t(z))],
    g_z,1=P0/(Z*H)*[(dotchi0-chi0*dotH/H+chi0^2)*t1-chi0*s/H].

Finite cell mass is P(z_L)-P(z_R); its response is the same endpoint difference. Retain tail and unscattered mass. For nonmonotone redshift push forward the time measure and sum all regular preimages:

    g_z(z)=sum_{t_r:z(t_r)=z} chi(t_r)*P(t_r)/[Z*|h(t_r)|].

A nondegenerate h=0 fold gives an integrable |z-z_star|^(-1/2) density. Use time preimages for cell probabilities.

If the log-redshift root residual is r_z and geometry error eta_z, |delta t|<=(r_z+eta_z)/h_min. Thus

    |delta tau|<=E_tail+integral|chi-chihat|dt
                 +chihat_max*(r_z+eta_z)/h_min+E_quad.

For nonnegative depths, survival error<=1-exp(-E); cell mass error<=sum of its two endpoint survival bounds. Signed electron residual can be integrated using global W(s)=integral_max(s,t_s)^t_b kappa_T(t)dt, without resetting the horizon per step. Numerical, source/model, tail, geometry and event errors remain separate.

## 6. Actual checks and saved-result consumption

Three new cloud Wolfram calls, System`$Version15.0.1. Actual xTensor1.3.0/xCoba0.8.6/xPerm1.2.4 with external xPerm connection and official archive SHA25610ed8c7892d65d656198a9be145bbd749d879a093afadaba6a09aa037375695d. xAct6named groups contained9zero scalar residuals. Separate algebra10groups contained18zero scalar residuals. Final numerical reference returned2exact zero identities and4scientific True checks; a NoNewChemistry metadata field is excluded from check counts.

Exact prescribed exponential test: Ht*=1,S_it*=(.3,-.2,-.1), t_o=0, chi=.02 exp(-3t/t*)/t*, tail=.13, logZ=.7. Positive14-direction degree5 rule; coefficient sky averages also proved analytically.65-digit roots at epsilon=.08,.04,.02,.01 give last coefficient error orders2.00011494,2.00010590,2.00009473 for tau1,tau2,P2. Outputs:

- z=1.01375270747047652; tau0=.177774466083784334;
- tau1 axes=(-.0342979136327841303,.0228652757551894202,.0114326378775947101);
- <tau2>=.00213409240381767922; <P2>=-.00168439242788591512.

Saved SHEAR12 consumption uses a DECLARED cubic-Hermite cumulative-column reconstruction on the single [.245,.25] cell, with its saved edge column and k*xi_e derivatives; observer .5 and source .2475. No new chemistry solve. Source-specific physical sigma_star was not selected; all following optical-column coefficients require sigma_T/sigma_star:

- z=.0101511771512956557;
- scaled tau0=.01021305007436961545;
- fixed-time path2=-4.93301088260634134e-8;
- fixed-z mean tau2=.478431828153502929;
- tau1 axes=(-.154656091976711201,.103104061317807467,.0515520306589037337).

At epsilon=1e-4,5e-5,2.5e-5 all inverse endpoints remained in that same cell. Maximum2nd-coefficient differences5.36920598e-6,1.34229919e-6,3.35574653e-7 passed the unchanged5e-5 criterion. This certifies comparison with the declared finite reconstruction, not the interpolation error of an underlying physical history.

## 7. Failures and executable handoff

The initial Python piecewise-linear-rate pilot FAILED at epsilon=.0005: tau2 coefficient error .0001277447551006894 exceeded5e-5. Its script and stderr remain in the archive; no PASS is assigned. A remote refinement command was blocked and not executed. Successful cloud Hermite evaluation is a separately declared reconstruction, not a retroactive repair of that failed pilot. The successful cloud scripts and selected normalized result transcriptions are preserved. Prepared reference input uses implicit multiplication where submitted code used explicit stars: semantic identity, not byte identity. The other two cloud inputs match modulo transport encoding.

Archive layout is flat. The three .wl scripts contain the successful reference expressions and can be evaluated in a stateless Wolfram kernel; xAct script downloads the official package. The Python pilot is retained for failure reproduction and expects the original workspace layout, not advertised as an all-passing package. No current PDF or sandbox download was created.

Existing SOURCE07-CONSUMER/BASS owner consumes a(t),B_i(t),observer time/direction, complete electron census, fixed-time responses/events, explicit tail, root bracket and error contracts. Return fixed-z tau, survival/cell masses, STF diagnostic and separate error terms. New atomic campaign, physical KN quadrature and cosmological chemistry histories:0. No new mandatory theory gate, independent promotion, production edit or merge.

Primary attribution: FPU15 arXiv1410.8473 sectionII/IV.1 read through Exa; Marcori et al2018 arXiv1805.12121 checked at abstract/metadata scope. Exact geometric identities are inherited; endpoint/observable formulas above are derived for the stated response family. Absolute scholarly priority is not claimed.
