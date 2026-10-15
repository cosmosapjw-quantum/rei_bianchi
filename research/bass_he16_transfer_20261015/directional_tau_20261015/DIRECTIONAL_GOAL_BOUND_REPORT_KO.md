# AXBI directional Thomson quadrupole: constructive goal-error budget (2026-10-15)

## Claim and scope

This result is a **conditional bound for the stored surrogate and frozen normal-frame clock**, not a certified ODE/global physical error bound. Data authority is the five 200001-row original AXBI signed prefixes, signed-source identity SHA256 \`d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185\`, plus the original numerical parent/geometry caches, each checked by exact SHA before use. All earlier warm BASS_HE HE18 16-cell numbers are kept separate from the cold model.

We retain \((-+++)\) and the original AXBI metric,
\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2.
\]
The normal-comoving observer is at the **shared prefix endpoint** \(\bar z_o\simeq10.2693\), not at present day. We fix a direction cosine \(\mu_o\) measured in the local orthonormal frame of that observer, and the relative photon-energy redshift \(z_{\rm rel}\).

## Derivation

Let \(u=\ln a\), \(d=b(u)-b(u_o)\), and
\[
g(u,\mu_o)=u_o-u+\frac12\ln[(1-\mu_o^2)e^{2d}+\mu_o^2e^{-4d}].
\]
For \(\mathscr F(d,\mu_o)\), the last logarithmic term, its derivative satisfies \(-2\leq \partial_d\mathscr F\leq1\). A uniform source geometry error \(\sup_u|\delta b(u)|\leq\epsilon_b\), including the observer, implies \(|\delta d|\leq2\epsilon_b\) and \(|\delta g|\leq4\epsilon_b\).

If the **nominal** piecewise-linear source geometry has \(M_q=\sup_u |db_q/du|<1/2\), its redshift inverse is strictly monotone, \(|\partial_u g_q|\geq m_q=1-2M_q>0\). Provided the perturbed redshift equation retains a root inside the same interval, its emission event satisfies
\[
|\delta u_e|\leq4\epsilon_b/m_q.
\]
The displaced root may be any of the perturbed roots: no unwarranted uniqueness property of the unknown perturbed geometry is assumed.

With fixed \(t_q(u)\), \(n_{e,q}(u)\), \(n_{H,q}(u)\), and constants, let \(T_q(u)=\sigma_Tc\int_{t_q(u)}^{t_o}n_{e,q}(t)\,dt\) and \(L_q=\sup_u|dT_q/du|\). Then
\[
|\delta \tau_{\rm dir,q}|\leq (4L_q/m_q)\epsilon_b+X_q\epsilon_x,\quad
X_q=(1+3f_{\rm He})\,\sigma_Tc\int_{t_i}^{t_o}n_{H,q}(t)\,dt ,
\]
where the species errors obey **three independent absolute pointwise bounds** \(|\delta x_{\rm HII}|,|\delta x_{\rm HeII}|,|\delta x_{\rm HeIII}|\leq\epsilon_x\). This is the worst-case *additive* error, not a probabilistic confidence interval. \(n_e\) and \(n_H\) are proper cm\(^{-3}\); \(c\) and \(\sigma_T\) are SI and introduce a factor \(10^6\).

The Legendre coefficient \(\tau_2=\frac52\int_{-1}^1P_2(\mu)\tau_{\rm dir}(\mu)\,d\mu\) obeys \(\frac52\int_{-1}^1|P_2|d\mu=\frac{10}{3\sqrt 3}\), checked in Wolfram. Thus for the signed odd response \(O_{\tau_2}(q)=[\tau_2(+q)-\tau_2(-q)]/2\),
\[
\boxed{|\delta O_{\tau_2}(q)|\leq
\underbrace{\frac{10}{3\sqrt3}\frac{4L_{+}/m_{+}+4L_{-}/m_{-}}2}_{C_b(q)}\epsilon_b+
\underbrace{\frac{10}{3\sqrt3}\frac{X_{+}+X_{-}}2}_{C_x(q)}\epsilon_x .}
\]
Both \(L_q\) and \(M_q\) are evaluated by a **piecewise-surrogate exact extremum**: in each source cell \(t(u)\), \(n_e(u)\), \(b(u)\) are affine, so \(dT/du=-\sigma_T c n_e(u)\,dt/du\) attains its absolute supremum at endpoints for nonnegative \(n_e\). The measured coefficients are not rounded outward, so their printed decimal values are diagnostics, not independently rigorous floating-point certificates.

## Actual cold-source numerical result

At the common-prefix normal observer, the goal functional was computed for relative directional redshifts \(z_{\rm rel}=0.20,0.50,0.75\). The known historical odd directional optical-depth quadrupole for \(q=0.005\) at \(z_{\rm rel}=0.75\) is \(O_{\tau_2}=-2.5931564384664036\times10^{-6}\).

| Property for q=0.005, z_rel=0.75 | Stored-source result |
|---|---:|
| C_b (unitless bound per absolute b error) | 0.0975613971785774 |
| C_x (unitless bound per absolute fraction error) | 0.2870530863320277 |
| Max geometry \(\epsilon_b\) alone for 10% goal budget | \(2.65797386410925\times10^{-6}\) |
| Max uniform ion fraction \(\epsilon_x\) alone for 10% goal budget | \(9.03371732247100\times10^{-7}\) |
| Min root-existence logarithmic margin at target | 0.05472761631943994 |

If geometry and species errors coexist, the combined inequality \(C_b\epsilon_b+C_x\epsilon_x\leq0.1|O_{\tau_2}|\) must be enforced. Each individually permitted ceiling cannot be spent simultaneously. Allocating a 5% goal budget to each separately would require \(\epsilon_b\leq1.32899\times10^{-6}\) and \(\epsilon_x\leq4.51686\times10^{-7}\).

## Falsification tests and performance

The independent manufactured-solution tests cover the exact power-law geometry, both angular directions, source perturbations, chunk/ref vector agreement, positivity/domain failures, and the exact Legendre \(L^1\) constant. Injecting \(\epsilon_b=10^{-6}\) in the real +0.005 and -0.005 geometric histories at \(z_{\rm rel}=0.75\) changed the signed odd quadrupole by \(8.9153201\times10^{-10}\), below the formula's conditional \(9.7561397\times10^{-8}\) bound. Injecting absolute ion fraction \(\epsilon_x=10^{-6}\) in the +0.005 source changed the response by \(5.7679108\times10^{-10}\), below \(2.8705309\times10^{-7}\).

Five real histories with 200001 rows each: 16384-node chunked long-double extrema and full-array vectorized reference agreed numerically (observed relative discrepancy 0 for all five cases). Five-run interleaved wall-time medians, Ubuntu x86_64 Python/NumPy with OPENBLAS_NUM_THREADS=1: chunked **0.08494 s**, whole-array vectorized **0.17557 s**. This is a speedup of approximately **2.07×** and reduces additional temporary arrays to \(O(\mathrm{chunk})\), not a native AXBI solver speedup. CPU/caches may shift this ranking on other workloads.

## Stop condition / next genuine science

Only **DERIVED / NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED** for the frozen surrogate. Real native solver \(b(t)\), \(t(a)\), \(n_e(t)\), source closure, EoR thermal coupling, angular quadrature, and full CMB \(z\simeq0\) path have no admitted whole-history error enclosure. A publication-grade claim requires an independent native solution/convergence family with goal-oriented bounds proving the above \(\epsilon_b,\epsilon_x\) tolerances (and analogous clock/source/transport tolerances); neither the scalar 'last_error' nor the saved-row decimation differences is such a proof.

Primary background: Fleury, Pitrou and Uzan, Phys. Rev. D 91, 043511 (2015), DOI 10.1103/PhysRevD.91.043511, exact Bianchi I null light propagation. Friedrich et al., MNRAS 421, 2232 (2012), coupled H/He ionization and heating.

## Five-history exact hydrogen dilution readback

All five original 200001-row prefix history files were independently read and SHA-matched against parent receipts. Each has the expected nH0=0.0017579215852062606 proper cm^-3 and max |nH(a)*a^3/(nH0*a0^3)-1| = 3.3306690738754696e-16. The standalone verifier hashes files in 1-MiB blocks and streams CSV rows, avoiding O(history-file-bytes) scratch. See DIRECTIONAL_HYDROGEN_DILUTION.json.
