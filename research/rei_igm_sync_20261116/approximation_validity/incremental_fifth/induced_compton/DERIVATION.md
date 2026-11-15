# Photon-only induced-Compton synthesis for original AXBI

This unit reuses only the general axisymmetric Compton energy-moment method from BASS PR335 at commit `d3ec945c4674d20ae63d4e7f659df24d798630de`, `research/typeii_spectral_closure_20261116/DESIGN_AND_THEORY.md`. It does not import the TypeII/HYREC state or evolve a new IGM history. The radiation is the actual Planck photon/CMB subset with T_ref=2.7255 K/a. The effective Ω_r fluid used for the separate stress comparison, including any neutrino contribution, is not a Compton photon energy density.

Take isotropic nonrelativistic Maxwell electrons in their bulk rest frame, unpolarized Thomson scattering, and retain leading photon recoil and thermal electron energy terms. With h=2πℏ, define b_l(E)=〈P_l(μ)n(E,μ)〉 and U=8π/(h³c³)∫E³b₀dE. The general induced kernel is S=b₀²−(6/5)b₁²+(1/2)b₂²−(3/10)b₃². Original AXBI directional Planck photons are reflection-even, so b₁=b₃=0. Consequently

\[
\frac{T_C}{T_{\rm ref}}=
\frac{\int_0^\infty x^4[b_0(x)+b_0(x)^2+\tfrac12b_2(x)^2]dx}
{4\int_0^\infty x^3b_0(x)dx},\qquad
n(x,\mu)=\frac1{\exp[x\sqrt{D(\mu,b)}]-1},
\]

where x=E/(k_B T_ref) and D=(1−μ²)e⁻²ᵇ+μ²e⁴ᵇ. This includes stimulation; a simple 〈T⁵〉/〈T⁴〉 prescription is not the same collision moment. The photon energy density is U=a_rad T_ref⁴〈D⁻²〉, a_rad=π²k_B⁴/(15ℏ³c³).

For n₀(x)=1/(eˣ−1), direct expansion gives

\[
b_0=n_0+b^2\left(\frac85xn_0'+\frac25x^2n_0''\right)+O(b^3),
\qquad b_2=\frac25b\,xn_0'+O(b^2).
\]

Let A₀=∫x³n₀dx=6ζ(4), N₀=∫x⁴(n₀+n₀²)dx=24ζ(4), and K=∫x⁶(n₀′)²dx=120[ζ(4)−ζ(6)]. The last identity follows by expanding (n₀′)² in exp(−kx), whose kth coefficient is k(k²−1)/6. Boundary terms vanish in the two integrations by parts. The numerator's quadratic coefficient is 4N₀−(18/25)K, while the denominator's relative quadratic coefficient is 8/5. Therefore

\[
\frac{T_C}{T_{\rm ref}}=1+
\left(\frac{12\pi^2}{35}-\frac65\right)b^2+O(b^3),
\qquad C=2.1838643660877803.
\]

At b=0 the full induced result returns T_C=T_ref. Exact finite-b spectral quadrature was performed only at b=0,±0.003,±0.006 with GL16/GL32 angular nodes and x upper limits 80/120. The even finite-difference coefficients are 2.183865780831 at 0.003 and 2.183870024609 at 0.006; their deviation from C scales approximately as b², as required by a remaining even quartic term. `RESULT.json` retains all finite-b values and refinement gaps. Total spectral computation took 0.119 seconds in the initial execution.

Applying only the leading Cb² term to the actual 1001 saved samples for each of five cases gives maximum ΔT_C≈1.241293820e−3 K for |q|=0.01 and 3.103336437e−4 K for |q|=0.005, at sampled zbar=7.333870578. The equal sign-pair values here follow from the explicitly truncated even approximation, not an exact finite-b symmetry: the exact quadratures retain cubic sign differences. The shift is smaller than the original 0.01 K gas-response floor, but it is a photon equilibrium-target shift, not a gas-temperature response or error bound. Full original coupled thermal response and AX11/AX12 admission remain open.

At the actual leading-approximation sampled peak a=0.11999226418091513 (zbar=7.333870578), b=±0.005002395171905325 and T_ref=22.7139642593 K, two additional GL32/x≤120 quadratures give exact spectral ΔT_C=0.001236231494326 K for +0.01 and 0.001246360616732 K for −0.01. These are exact spectral values at that selected point, not asserted full-history maxima. The maximum TC-ratio difference across the five original GL16/GL32 and 80/120 checks is 4.44e−16.

`INDEPENDENT_COEFFICIENT_CHECK.json` records the parent reviewer’s independent exact coefficient and high-precision K-integral verification. Its scope is this bridge’s coefficient/normalization, not the complete BASS335 implementation.

The target-temperature correction is distinct from the Compton cooling-coefficient correction U/U_ref−1 (up to about5.57e−5 in the original saved family). This coefficient multiplies the difference from the gas temperature. Consequently the millikelvin target shift alone cannot certify a sub-0.01 K gas response; both moment corrections would enter a future coupled thermal calculation.
