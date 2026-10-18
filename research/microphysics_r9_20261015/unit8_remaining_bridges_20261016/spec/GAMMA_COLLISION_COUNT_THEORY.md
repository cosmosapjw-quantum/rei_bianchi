# Unit8 C2: repeated cold-electron scattering indexed by collision count

This separate addendum advances the admitted 477.6 keV first-collision kernel through n=1,2,4,8,16 collisions in a frozen background. It computes the photon distribution, cumulative electron kinetic energy, and expected elapsed time at each count. The parent explicitly authorizes a new 5 s target / 10 s hard numerical ceiling, including grid comparisons. The existing lane-C contract and its 30 s allowance remain unchanged. This is not a new cosmological cascade or heat calculation.

## Reused inputs and positive conservative operator

Reuse the exact Unit7 inputs, cosmology, gamma branch, and CODATA constants frozen in `GAMMA_TRANSFER_CONTRACT.json`, plus the admitted Unit8 KN results for the independent first-collision mean. The normalized photon state starts at the exact node E0=477600 eV. The final physical amplitude is the actual gamma source count N0*0.104*DeltaF, without resetting DeltaF.

Use positive log energy nodes from 1000 eV to E0, including both endpoints, plus an E=0 sentinel. Primary grids have 256 and 512 positive nodes. At each positive parent energy Ei, integrate the normalized KN angular probability with 128-point Gauss-Legendre quadrature. Each outgoing photon energy Eout=Ei/[1+Ei*(1-mu)/(mec2)] is placed on its two bracketing energy nodes with positive linear weights summing to one and weighted energy exactly Eout. This defines the column-stochastic matrix Pji. Its support is j<=i. The zero sentinel is an identity state with sigma0=sigmaT; it completes the operator at its lower boundary and must remain unoccupied for this task. No out-of-grid energy clipping is allowed.

For p0 concentrated at E0, set p_(k+1)=P p_k. Let kj=Ej-sum_i Ei*Pij, the per-collision mean electron kinetic energy for a photon in parent state j. Accumulate K_(k+1)=K_k+sum_j kj*p_k,j. Then sum p_k=1 and K_k+sum_j Ej*p_k,j=E0 to roundoff. The bin placement preserves the first energy moment rather than replacing an outgoing energy by a bin center. It introduces controlled distribution interpolation error, assessed by the two grids and 256-point angular refinement of the fine grid.

For an exact continuous photon, 1/E_after=1/E_before+(1-mu)/(mec2). Hence after n collisions E0/[1+2nE0/(mec2)]<=E_n<=E0. This elementary support bound is independent of scattering probabilities. Report it alongside the numerical support and any interpolant probability below it. Grid interpolation may place probability just below the physical bound, so report this as numerical leakage rather than assert an exact support theorem for the projected chain. If Delta=log(E0/1000)/(Npositive-1), the projected process obeys E_n>=exp(-n*Delta)*E_min,continuous(n): each lower-node placement loses at most one factor exp(-Delta), and the recoil minimum f(E)=E/(1+2E/mec2) satisfies f(aE)>=a*f(E) for 0<a<=1. Require no occupied sentinel and no appreciable probability below this explicit projected support bound. At n=16 the continuous minimum is about 15.45 keV and even the coarse projected bound exceeds 10 keV, well above the 1 keV numerical boundary.

## Expected time and a nonasymptotic background check

At fixed source redshift zs, the holding time in photon state j is exponential with mean 1/[ne(zs)*c*sigma0(Ej)]. The exact mean time of the projected process through n collisions is

`<t_n>(zs)=L_n/[ne(zs)*c]`, where `L_n=sum_(k=0)^(n-1) sum_j p_k,j/sigma0(Ej)`.

Evaluate H(zs)*<t_n> at Unit7 z10,z50,z90 and integrate it against the actual raw decay measure. This mean is not a pathwise elapsed-time bound.

A useful stronger bound follows directly from the kernel. Write a=1-mu^2 in [0,1], r=[1+x(1-mu)]^-1, and d sigma/dmu=pi re^2*(r^3+r-a r^2). Its derivative with respect to r is positive because 3r^2+1-2ar >= 3(r-1/3)^2+2/3. Since dr/dx<=0, sigma0 decreases with photon energy. Every cold scattering decreases E, so all holding rates are at least Gamma0=ne*c*sigma0(E0). Therefore t_n is stochastically bounded above by an Erlang(n,Gamma0) variable. For epsilon>0,

`P[H_s*t_n > epsilon] <= Q(n, epsilon*Gamma0/H_s)`,

where Q is the regularized upper incomplete gamma function, equal to the Poisson probability of fewer than n events. Also <t_n><=n/Gamma0. Compute the fixed-background 99% and 99.9% upper time bounds using gammaincinv(n,p)/Gamma0, recording that they are upper bounds rather than the chain's exact quantiles.

One may compare against expansion without simulating a cascade. In the frozen donor FLRW model H(t)<=H_s after emission, hence u=ln(a/a_s)<=H_s*t. For T=epsilon/H_s, ne(t)>=ne_s*exp(-3epsilon) on [0,T]; redshift and cold collisions still imply E(t)<=E0 and sigma0(E(t))>=sigma0(E0). Counting-process domination then gives

`P[n collisions have not occurred by epsilon/H_s] <= Q(n, epsilon*exp(-3epsilon)*Gamma0/H_s)`.

This bound is valid only within the inherited fully ionized z>=10000 bath. For source zs with ln[(1+zs)/10001]<epsilon, retain a conservative probability bound of one rather than extrapolate the bath. Source-weight the bounds with raw dF and report that endpoint-margin mass separately. Evaluate epsilon=0.01 and 0.05. On the corresponding event, density changes by at most 1-exp(-3epsilon), photon redshift by at most 1-exp(-epsilon), and H decreases by at most 1-exp(-2epsilon) in this positive radiation/matter/Lambda model. These quantify background variation; they are not an a priori error bound on the complete interpolated photon spectrum.

## Outputs, source weighting, and validation

The energy distribution at a fixed collision count is independent of ne. Apply the source amplitude only after solving that normalized Markov problem. For source-weighted waiting times and probability bounds, use each existing native history cell's actual DeltaF and its log(1+z) midpoint, with endpoint-margin handling above. Repeat with pairs of source cells merged for a direct quadrature check. No source probability is discarded or renormalized to full decay.

Export fine-grid photon probabilities and cumulative electron kinetic yields for n=0,1,2,4,8,16. Export the fine-grid sparse redistribution matrix (parent index, daughter index, probability), source-weighted and source-quantile timing/bound tables, and JSON with all residuals. Photon mean, standard deviation, and 5%,50%,95% quantiles are useful at each n; interpolate the discrete CDF consistently and report the method. Count-indexed energies are not common-epoch spectra or deposited heat.

Checks: P>=0, column sums within 2e-12, per-parent photon plus electron energy closure within 2e-12 of max(Ei,1eV), state count and cumulative energy closure within 1e-11, no positive-energy growth, sentinel probability <=1e-14, and probability below the projected support bound <=1e-14 (allow 1e-12 relative energy comparison roundoff). First-collision mean agrees with admitted C within 1e-9 relative. Coarse/fine means and waiting coefficients agree within 3e-3, cumulative K/E0 within 1e-3 absolute, and quantiles within 3e-2 relative. Fine-grid angular128/256 mean and waiting checks use 3e-3 relative and quantiles 3e-2. Raw/coarsened source averages use 1e-4 relative (absolute 1e-8 for tiny probability bounds). Verify <t_n><=n/Gamma0 and 0<=each probability bound<=1. Numerical acceptance certifies the stated projected cold-electron calculation, not thermal corrections or exact continuum transport.

Pre-execution contract correction: an initial draft required negligible probability below 0.99 of the continuous minimum. Barycentric interpolation can legitimately cross that arbitrary margin at a backscatter edge. The replacement is the derived discrete support bound above, with the original continuous-support leakage still reported and observable grid convergence unchanged. This corrects a discretization/acceptance mismatch before execution.

Stop once the fixed requested counts and checks complete. A substantive failure returns for one targeted diagnosis within the 10 s cumulative ceiling; do not silently enlarge this addendum into a time-dependent cascade. PASS advances to independent review and supplies the next electron-cooling input. The concrete remaining physics is electron Coulomb/inverse-Compton redistribution and eventually a finite-temperature photon operator near thermal energies.
