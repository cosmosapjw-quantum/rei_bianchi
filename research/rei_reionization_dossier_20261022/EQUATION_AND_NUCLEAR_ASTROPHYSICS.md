# Reading the equations as physical processes

This companion explains the equations used in the updated dossier and its plots. It covers the nine groups below, not every formula in the three original source volumes. The distinction throughout is between changing a nucleus, changing its electrons, and changing the time available for either process. A reionization curve can change strongly while the underlying nuclear inventory hardly changes at all.

## 1. Abundance, charge fractions and the cosmological clock

`Y_A=n_A/n_B` counts nuclei of species A per baryon. The identity `sum_A A*Y_A=1` weights each nucleus by its baryon number: one helium-4 nucleus contains four baryons, whereas one proton contains one. It is a conservation statement, not a claim that the numbers of different nuclei add to one. `Y_Aq=Y_A*f_Aq` then separates how many nuclei exist from what fraction carries charge q. Changing f can move a population between neutral and ionized states without changing Y_A.

Hydrogen-1 supplies most nuclei and electrons. Deuterium is a rare hydrogen isotope and a nuclear fuel for DD reactions. Helium-4 carries a substantial baryon inventory; helium-3 is much rarer and is a target for neutron-induced tritium production. Lithium-6 and lithium-7 have very small imposed inventories but distinct nuclear creation/destruction routes. Tritium and free neutrons are unstable and start at zero in this experiment. Their new trace inventories should not be confused with the much larger pre-existing stable reservoirs.

The supplied initial abundances are finite-time inputs, motivated by primordial composition; this calculation does not rerun Big Bang nucleosynthesis or solve the primordial lithium problem. Equal electronic operators make H1 and D share a conditional charge history here, likewise the two helium and two lithium isotopes. Their absolute abundances remain different. Newly produced T has no solved charge partition and cannot inherit the hydrogen fractions by assumption.

The coordinate `x=ln(a/a_ref)` obeys `dx/dt=H`, while `1+z` is inversely proportional to a. Therefore `dt/dx=1/H`: at a given state, doubling H halves the proper time available per unit x. At fixed baryon number in the common comoving volume, `n_B` is proportional to `(1+z)^3`; doubling 1+z raises that density by a factor of eight. These relations explain why equal redshift intervals are not equal time intervals. Time axes start at z=20 and measure elapsed Myr, not the age since the Big Bang. Auxiliary axes use the labelled reference trajectory, because different cases have different clocks.

## 2. Event counts, stoichiometry and binary collision rates

`R_A=sum_r nu_Ar*R_r` says that every reaction event changes each species by its signed multiplicity. DD producing T+p removes two D nuclei and adds one T and one proton. The corresponding source per baryon is `dY_A/dt=sum_r nu_Ar*R_r/n_B`. Cosmic dilution cancels in this ratio when the baryon current is conserved; it still affects the collision frequency through n_B.

For a binary reaction i+j, the implemented event rate per volume is

`R_ij = n_B^2 * Y_i * Y_j * <sigma v>_ij / (1+delta_ij)`.

Its rate per baryon is `R_ij/n_B`. Doubling density at fixed temperature and fractions quadruples the events per physical volume and doubles the events per baryon. Doubling only one distinct reactant fraction doubles the rate. For DD, doubling the available D fraction quadruples its source. The factor one-half for identical reactants counts each unordered DD pair once; it is not an extra factor applied separately to each product. Stoichiometry then removes two D nuclei per event.

The appropriate reactant fraction depends on the declared model. The first DD audit used the saved ionized-deuterium fraction; the later all-bare conditional network treats the whole retained nuclear reservoir as available. Their difference is a physical availability assumption, not a change in a measured nuclear constant.

`Q_A^a=sum_r integral Delta p_A^a dR_r` uses the same events to count momentum and energy transfer. More events proportionally increase both inventories, but reaction energy is not automatically deposited as gas heat. Recoil nuclei, photons, electrons and escaping neutrinos carry separate shares. The covariant divergence equations encode local particle and energy-momentum balance; their factors of c depend on the declared coordinate convention. They do not permit a second copy of the same reaction energy in a separate heating routine.

## 3. Shear, signed stress and expansion

`H^2=K*epsilon/3+Lambda*c^2/3+s^2` relates mean expansion to material/radiation energy, the cosmological constant and shear. At fixed energy density, increasing the shear magnitude increases H through s squared. Its sign does not appear in that single term, but sign still matters in the coupled stress evolution. The shear equation `dot(s)+3Hs=K*(p_m+p_gamma+p_nu)` balances expansion damping against signed anisotropic stress. Without a source, the dimensional shear decreases in proportion to a to the power minus three. With a source, aligned stresses reinforce one another and opposite stresses can cancel temporarily.

`S=sqrt(6)*s/H` measures signed shear relative to expansion; `Sigma=abs(S)` discards its orientation. Similarly, `P_X=sqrt(6)*K*p_X/H^2` compares a dimensional stress with the expansion scale. Holding p_X fixed while doubling H divides P_X by four. This is why fixed raw angular amplitudes need not imply fixed physical initial Pi when another background parameter changes.

Radiation stress is added before taking its magnitude: `Pi_r=abs(P_gamma+P_nu)`. The total magnitude is `abs(P_m+P_r)`, not the sum of magnitudes. Small total stress can hide large opposed contributions. Photons scatter on the computed electrons whereas the retained neutrinos free-stream, so their initial cancellation need not persist.

The matter stress here belongs to a collisionless nonbaryonic component. It does not directly squeeze the atomic gas, heat nuclear reactants or alter nuclear cross sections. Its effect on the retained atomic and nuclear histories is mediated by geometry and elapsed time under the prescribed gas closure.

## 4. Photoionization, recombination and electron feedback

The electron closure `n_e=w^T f` counts how many free electrons each populated charge state contributes. The weights contain baryon density, isotope abundance and ionic charge. A doubly ionized helium nucleus contributes two electrons; neutral helium contributes none. Thus increasing ionization can increase the supply of electrons available for recombination elsewhere.

The atomic generator is `G=P+n_e R`, and `df/dx=Gf/H`. P contains one-body photoionization hazards for the imposed radiation field. R contains radiative-recombination coefficients; multiplying by electron density converts them to a hazard per ion. If the external radiation field is unchanged, doubling gas density does not double the photoionization rate per atom. It does double the recombination rate per ion at fixed fractions and temperature. Per physical volume, photoionization is then proportional to density, whereas recombination is proportional to density squared.

For an isotropic photon number spectrum, a photoionization hazard has the form `Gamma=c*integral n_gamma(E)*sigma(E) dE`. Doubling its normalization doubles Gamma if the spectral shape is unchanged. The retained recombination coefficients decrease with temperature across the specified gas-temperature interval; hotter electrons are less readily captured in these coefficients. Temperature and UV amplitude are prescribed functions of redshift, so their simultaneous rise is an input, not a heating history predicted by the solver. Geometry changes the proper-time exposure through the factor one over H, while electron feedback can modify the later response.

The Jacobian term `outer(Rf,w)` is the change in recombination caused by the perturbed electron supply. Omitting it would treat electrons as fixed while varying the charge states that produce them. Column sums of G vanish because ionization and recombination transfer nuclei between charge states rather than destroy those nuclei.

The 5-60 eV source crosses the approximate H I, He I and He II thresholds of 13.6, 24.59 and 54.42 eV. It crosses Li I at 5.392 eV but not Li II at 75.64 eV or Li III at 122.5 eV. Therefore helium can reach its doubly ionized state, whereas initially empty Li III/IV remain empty in this restricted model. This is a spectral-support statement with the selected initial conditions and channels. Adding energetic collisions or harder photons would change it. A very small absolute lithium abundance can nevertheless have a visibly changing conditional fraction.

## 5. Charged nuclear reactions and the Gamow window

For the admitted bare charged-particle continuation, `sigma(E)=S0*exp[-sqrt(E_G/E)]/E`. S0 fixes the overall strength; the exponential represents Coulomb tunnelling. Larger nuclear charge product raises E_G and suppresses penetration. A higher relative kinetic energy reduces that barrier penalty, but high energies are rare in a cold Maxwell distribution.

The implemented Maxwell average integrates both penalties:

`<sigma v> = sqrt[8/(pi*mu)]*(k_B*T)^(-3/2) * integral sigma(E)*E*exp[-E/(k_B*T)] dE`.

The reacting particles are drawn from a tail, not simply from the mean thermal energy. With constant S and a well-separated Gamow peak, a saddle-point interpretation gives `E0=[E_G*(k_B*T)^2/4]^(1/3)` and an approximate temperature dependence `T^(-2/3)*exp[-3*(E_G/(4*k_B*T))^(1/3)]`. These last expressions explain the numerical integral; they are not a new rate fit substituted into the implementation. Raising T shifts the preferred reaction energy upward in proportion to T to the power two-thirds and greatly reduces the exponential suppression. In this low-temperature regime that exponential change dominates the decreasing algebraic prefactor. There is no single temperature-independent power law for the rate.

At fixed T, doubling S0 doubles the calculated coefficient and source. At fixed density, changing abundance or ion availability changes the source independently of this coefficient. The 100-10000 K gas remains far colder than a conventional thermonuclear-burning environment, so even positive DD tunnelling gives extraordinarily tiny yields. The positive logarithmically stored source refutes an exact mathematical zero in this conditional model; it does not imply astrophysically important synthesis. Constant S down to these energies is a declared extrapolation without direct empirical validation throughout the range.

## 6. Neutron capture, inverse reactions and photon support

Neutrons lack the electric Coulomb barrier of charged projectiles. In the retained low-energy `sigma proportional to 1/v` approximation, multiplying by v gives a nearly constant capture coefficient K0. Slower neutrons have a larger cross section, but they also sweep through targets more slowly; those two effects cancel in sigma*v. A Maxwell average of a strictly constant K remains constant. Consequently temperature has a much weaker role in these adopted neutral coefficients than in the charged Gamow factors, while density and target abundance still control collision rates.

For example, the selected proton-capture anchor is 0.3326 barn times 2200 m/s, giving 7.3172e-26 cubic metres per second. He3(n,p)T has a much larger thermal coefficient, but its tritium source is still limited by the exceedingly small neutron inventory. A large coefficient alone does not guarantee a large yield. Applying thermal anchors to fast DD neutrons requires the explicitly assumed instantaneous thermalization; their actual stopping and transport were not solved.

Detailed balance for a reversible two-body reaction relates reverse and forward coefficients through masses, spin multiplicities, identical-particle factors and `exp[-Q/(k_B*T)]`. For an endothermic inverse with positive forward Q, colder temperatures exponentially reduce the reverse rate. A very negative finite log rate is not an exact zero. The spin factor two-thirds for microscopic n+p/D+photon reciprocity and four-thirds for the leading thermal equilibrium relation describe different incoming ensembles and should not be interchanged.

A photon inverse instead depends on the actual photon distribution above threshold. The imposed 60 eV upper cutoff lies far below the nuclear thresholds, so its external nuclear photodisintegration source is exactly zero under the declared target approximation. A Planck spectrum has no such hard upper cutoff and would give a positive, exponentially small high-energy tail. The original Planck inverse formula is theory for that different radiation ensemble; the present code does not set the photon bath temperature equal to the gas temperature or reprocess its escaping capture photons.

## 7. Radioactive survival, cumulative births and rapid balance

The loss law `dY/dt=-lambda*Y` has `lambda=ln(2)/t_half` and survival proportional to `exp(-lambda*t)`. After one half-life half survives; after two, one quarter. This dependence is independent of density for the retained free beta-decay approximation. Tritium's pinned half-life is 12.312 years, vastly shorter than a Myr-scale reionization history. The retained neutron mean lifetime is also short, about 878 seconds.

With production, `dY_T/dt=s_T-lambda_T*Y_T` illustrates the distinction between births and surviving stock. Cumulative births add every newly formed nucleus; they never subtract an earlier birth when that nucleus decays. Surviving stock does subtract decay and other destruction. If the source varies slowly compared with the loss time and decay dominates, `Y_T approximately s_T/lambda_T`. Doubling a slowly varying source doubles this stock. Doubling the half-life approximately doubles it by allowing nuclei to survive longer. This local balance is an interpretation, not an identity at the initial switch-on or during rapid source changes.

The implemented T/neutron calculation includes coupled creation and capture hazards, so its general fast balance is a small coupled system, not always the isolated formula above. Direct positive-stock propagation remains authoritative. Subtracting two nearly equal, much larger cumulative event totals can destroy all digits of the surviving stock. This numerical cancellation has no physical relation to a negative abundance.

The roughly 3.96e-96 cumulative T births per baryon and 1.39e-104 late surviving T inventory therefore answer different questions. Their large ratio is consistent with short-lived nuclei being produced and lost throughout a long epoch. Neither number changes the inherited stable-isotope composition appreciably in this conditional experiment.

## 8. Thermal energy, optical depth and observational limits

For a nonrelativistic thermal mixture, `U=(3/2)*k_B*N_particles*T` means that energy is proportional to both particle number and temperature. At fixed particle number, doubling T doubles thermal energy. At fixed available thermal energy, adding particles lowers the temperature that the energy can support. Ionization also consumes binding energy, and new electrons change heat capacity. These relationships motivate one consistent energy ledger rather than separate, duplicated heating estimates.

The present temperature is prescribed. The required-heating and photon-energy plots diagnose what exchange would be needed to maintain that history; they do not demonstrate that the specified radiation self-consistently supplies all of it. Nuclear Q values are available energy per event, not automatically deposited thermal energy. Fast recoil, nonthermal electrons and escaping photons/neutrinos require their own deposition rules.

The homogeneous Thomson diagnostic obeys `d tau/dt=c*sigma_T*n_e`, or `d tau/dx=c*sigma_T*n_e/H`. More free electrons or more time increases scattering depth. At fixed electron history versus x, doubling H halves the depth accumulated over that interval. If the electrons change too, their response must be included. This diagnostic alone is not a fitted observed optical depth or a synthetic sky.

The original polarization condition `Q_Stokes^2+U_Stokes^2+V_Stokes^2<=I^2` states that the polarized part cannot exceed the total intensity for a positive coherency matrix. These Stokes symbols are distinct from reaction energy Q and thermal energy U. No polarized light-cone calculation is performed in this atlas, so a radiation-stress curve must not be read as a polarization measurement.

## 9. Positive angular distributions and the near-quadratic stress response

`W(mu)=1+A_m*P2(mu)` is nonnegative only for -1<=A_m<=2. Increasing A_m shifts relative weight toward the symmetry axis without changing its isotropic angular average. At the initial isotropic metric, `pi_s=A_m*pbar/5`, while density and mean pressure are fixed. The original cold family consequently cannot reach arbitrarily large Pi by enlarging A_m: it reaches its positivity ceiling first.

The stronger family changes the nonbaryonic dispersion and fraction, then holds that new family's density and mean pressure fixed while varying its quadrupole. Its zero-stress member is the correct reference. Near that isotropic reference, stress induces shear and directional distortion at first order in A_m. The scalar anisotropic-work term `6*s*pi_s`, the shear contribution s squared, and the radiation monopole source `E0'=-2*(s/H)*E2` are second order because each multiplies two first-order quantities. The massive monopole also has no first-order directional average. Thus H and the retained atomic fractions first change at quadratic order under these particular matched conditions.

The measured maximum fraction shifts at Pi=.01,.05,.1 are close to `5.46e-4*Pi^2`. Doubling a sufficiently small Pi would therefore suggest about four times the leading response within this local interpretation, not a guaranteed law across arbitrary matter models. The observed finite-range values support that interpretation; they do not prove exact sign symmetry or exclude higher-order terms. All three tested nonzero stresses exceed the frozen observed-discrepancy comparison rule, whereas the old cold-family response did not. This modifies the expansion history, not nuclear constants or the prescribed gas temperature.

In the new plots, abundance tick marks represent powers of ten. Signed differences and stresses use symmetric logarithmic axes so that zero and negative values remain visible. The stated linear region is a display choice, not an error bar or a physical detection boundary. Read the numerical controls and model limits alongside the enlarged visual differences.
