# BR05: native birth-panel monitor — mathematical contract

## 1. Bounded conclusion

The BR03 fitted rule supplies a constructive, positive, constant-source/constant-opacity reference on every birth-age panel. BR05 can attach that reference to the actual accepted native cohorts without altering photon creation, propagation, gas reaction, CX splitting or timestep acceptance. The resulting monitor describes actual panel resolution, verifies provenance, and measures discrepancies between precisely named measures.

A frozen-kernel distance is an error certificate for that specified reference problem. It is not an absolute error certificate for the evolving H/He/D radiation–gas solution. Actual source amplitudes, Killing trajectories and final photon counts remain independently observable. Their difference from a frozen reference includes physical evolution and need not vanish as birth refinement increases.

The equalities and bounds below concern real arithmetic. Binary64 outputs require independent numerical checks; they are not directed-rounding interval enclosures.

In BR05, accepted means a successful local advance_core transaction in the fixed-macrostep native driver. The S10 adaptive four-corner controller and ap_budget still use the unchanged parent path. This monitor does not newly instrument outer adaptive-trial acceptance or rejection.

## 2. Variables, labels and units

For an accepted macrostep, let t0 be its initial time, dt > 0 its duration, and t1 its represented end time. A fitted rule uses normalized target age x in [0,1], with intended age A_target = dt x. Native emission stores tb = fl(t1 - fl(dt x)); the represented age is A_clock = fl(t1 - tb). Export both ages and their difference. Do not replace the stored birth clock by the target clock.

A label lambda identifies the actual source template entry by template ordinal, spectral index, angular index, emitted-energy bits and the full signed birth-direction bits. Expanded spectral entries need the ordinal/energy identity in addition to owner indices. Rule caching by emitted-energy bits is a computational cache, not a merging of physical labels. A retained cohort ID additionally contains the accepted birth-batch ID and node ordinal; a panel ID consists of the batch ID, label and consecutive node-pair ordinal.

For the axisymmetric Bianchi-I metric with signature (-,+,+,+),

$$
a_X=a_Y=a e^{-b},\qquad a_Z=a e^{2b},\qquad V=a^3,
$$

retain each original birth geometry and direction. At time t, the corresponding ray obeys

$$
K_i=a_i(t_b)E_b n_{b,i},\qquad
E(t)^2=\sum_i K_i^2/a_i(t)^2.
$$

The signed s/H is distinct from the nonnegative shear normalization sqrt(3)|s/H|. The monitor neither changes this convention nor adds Einstein feedback.

In that equation n_b is the unit direction used by the original CharacteristicRay constructor. The stored raw direction bits are also retained as source identity; binary64 normalization may change a component by rounding. A Killing-vector readback must reproduce the original ray normalization instead of assuming that the raw stored direction and the constructor's normalized direction are bit-identical.

The units are: dt, A and panel time width in seconds; x, optical depth tau, CDFsup and normalized reference probabilities dimensionless; reference-comoving photon count density in m^-3; kappa in s^-1; normalized W1 in seconds; count-weighted W1 in m^-3 s. Energy-weighted statements need their explicit eV or joule conversion and the original energy owner.

## 3. Actual opacity selector and panel replay

Read the gas actually supplied to the accepted corrector's emit_births call. At the actual template's emitted energy E_b, use the original four nonnegative opacity channels, in order HI, HeI, HeII and DI:

$$
\kappa_\lambda=\sum_s\kappa_{\lambda,s}(E_b,\mathrm{rate\_gas}),
\qquad \tau_\lambda=\kappa_\lambda\,dt.
$$

This is the selector used by the fitted rule. It is not the path-integrated opacity of a photon whose energy changes with geometry. Export the four channels, their sum, the actual rate-gas state, E_b and source identities. In particular, kappa_reference = 0 does not establish transparency along a blueshifting trajectory that later enters an absorption band.

Replay only the existing panel-boundary recurrence; obtain node locations from the unchanged original rule. For refinement r in {1,2,4,8,16}, starting at l=0,

$$
d_*=
\begin{cases}
1/r,&\tau\le1,\\
\min(1,\tau^{-1}+l)/r,&\tau>1,
\end{cases}
\quad
u=\min(1,l+d_*),\quad d=u-l.
$$

The last panel is clipped. It follows directly that

$$
d\le 1/r,\qquad
\theta=\tau d\le (1+\tau l)/r,\qquad
h=dt\,d\le dt/r.
$$

For tau <= 1 the second inequality follows from theta <= tau/r <= 1/r. For tau > 1 it follows from the second branch. These are panel-size statements, not global convergence-order results. Record possible rounding excesses separately instead of silently forcing an inequality by clipping output values.

For tau > 1 the recurrence before clipping is geometric in 1+tau*l; its panel count grows logarithmically with tau at fixed r. This is the cost advantage over enforcing a uniform optical width over an interval of optical length tau.

Check that the two original nodes belong to the replayed panel, their weights are positive, and their order and exact emitter reconstruction agree. Store nominal h and represented birth-time endpoints [fl(t1-dt*u), fl(t1-dt*l)] separately. Generic floating-point target distinctness does not by itself justify discarding a cohort at an equal represented clock. This monitor does not claim that a clock collision occurs in the accepted native run; it observes and validates the actual clocks.

## 4. The positive fitted panel

Write m=l+d/2, z=tau*d/2. For tau>0 let

$$
q=\operatorname{acosh}(\sinh z/z),\qquad
x_\mp=m\mp q/\tau,\qquad w_\mp=d/2.
$$

At tau=0 use the continuous GL2 limit. Equivalently, for local y=(x-l)/d, the two nodes are f and 1-f, with

$$
f=\tfrac12(1-q/z),\qquad
f(0)=\tfrac12(1-1/\sqrt3).
$$

Since 1 < sinh(z)/z < cosh(z) for z>0, monotonic acosh gives 0<q<z. Thus 0<f<1/2 and both weights are strictly positive. The first inequality follows from sinh(z)>z; the second follows from z*cosh(z)-sinh(z)>0, whose derivative is z*sinh(z)>0. These are finite-z statements; the limiting nodes approach the panel boundaries as z grows.

Near zero, sinh(z)/z = 1+z^2/6+O(z^4) and cosh(q)=1+q^2/2+O(q^4), so the positive branch gives q/z -> 1/sqrt(3). This proves the stated GL2 limit. At large total tau the exact full-step survival B*Phi(tau) approaches B/tau = j/kappa, resolving the constant-opacity thin survival layer in mass without assigning every photon one common birth age.

For a constant reference source rate j_lambda and B_lambda=j_lambda*dt,

$$
d\mu_{\lambda,p}=B_\lambda e^{-\tau x}\,dx,\quad
M_{\lambda,p}=B_\lambda e^{-\tau l}d\,\Phi(\theta),
\qquad
\Phi(v)=\int_0^1e^{-vy}dy.
$$

The two-node survivor mass is

$$
B_\lambda d\,e^{-\tau m}\cosh(q)
=B_\lambda e^{-\tau l}d\,\Phi(\theta)=M_{\lambda,p}.
$$

It follows that emitted mass, emitted first age moment and frozen survivor mass are exact on each panel in real arithmetic. Positivity and the exact survivor mass do not make all survivor moments exact.

For the emitted local uniform measure, the signed second-moment defect is

$$
\tfrac12[f^2+(1-f)^2]-\tfrac13=f^2-f+\tfrac16.
$$

In global x coordinates, integrating the panel's constant source gives defect

$$
B_\lambda d^3(f^2-f+\tfrac16),
$$

and in physical age it is multiplied by dt^2. The l-dependent terms cancel because mass and first moment agree. At the GL2 limit this defect is zero; at very large theta it approaches B_lambda*d^3/6.

The local normalized emitted W1 is exactly

$$
W_{1,\mathrm{emit},p}=f^2+(\tfrac12-f)^2
=2f^2-f+\tfrac14.
$$

This follows by integrating the uniform CDF minus the two-atom CDF over its four sign intervals. It lies between 1/8 and 1/4. The formula is a useful independent check, not an optimal-quantizer claim about the fitted rule.

## 5. Three measures that must remain distinguishable

Use the actual midpoint template normalization B_lambda = template_count_per_second*dt. The template is generated by the original source expansion and retains all labels.

1. **Frozen kernel reference and fitted rule.** The continuous measure is B_lambda*exp(-tau*x) dx and the atomic measure is B_lambda*sum_i w_i*exp(-tau*x_i) delta_(dt*x_i). Only this pair inherits the fitted constant-source mass identity.
2. **Native source weights under frozen propagation.** Native birth counts are the original represented n_born,i = B_lambda*w_i*g_i, where g_i is the actual birth-geometry source amplitude divided by the midpoint amplitude, with the original multiplication order retained. The comparison measure sum_i n_born,i*exp(-kappa*A_clock,i) delta_(A_clock,i) includes source variation and represented clocks. It has no reason to have the same mass as the constant-source reference.
3. **Actual native retained measure.** Sum_i n_after_photo,i delta_(A_clock,i), or its verified accepted-state counterpart, is the solver's actual discrete result for the birth batch. Its attenuation comes from the unchanged ray/threshold/absorption implementation. The measured difference from the frozen comparator contains varying geometry, spectral thresholds, source weighting and actual attenuation.

Where helpful, also export actual emitted and retained panel masses, the pure-reference emitted and survivor masses, and the two positive native counts individually. A normalized shape is undefined for a zero-mass measure. Do not divide through a zero count or reinterpret a log-scaled conditional reference as physical photons.

The implementation's template certificate reconstructs emitted weights as actual_n/constant_born and uses the represented normalized clock. Its mass can differ by floating rounding from a direct sum of the original actual_n or actual_n*exp(-kappa*A_clock) records. The monitor exports those direct populations separately. A claim of complete source-ratio underflow detection would additionally require tracking loss in the quotient actual_n/constant_born; that specific flag is not part of this bounded implementation. No such quotient loss is asserted to occur in the observed native cases.

If native counts at photo exit and accepted exit agree and all birth labels/geometry are unchanged, that is evidence about this driver's sequence. It is not a permission to omit future verification when adding a compaction or transport stage.

## 6. Local distances and exact composition under matched panel masses

The normalized reference on local y in [0,1] has CDF

$$
G_\theta(y)=\frac{1-e^{-\theta y}}{1-e^{-\theta}},
\qquad G_0(y)=y.
$$

Apply the existing read-only BR04 certificate to the actual local nodes y_i=(x_i-l)/d and emitted weights w_i/d. Record its mass defect independently. If D_p and K_p are its normalized W1 and CDFsup, then the physical panel W1 is h_p D_p, while CDFsup is unchanged.

For a single label with disjoint ordered panels and exactly matching panel masses on both sides, the cumulative mass difference is zero at every panel boundary. The one-dimensional CDF-area identity therefore gives

$$
W_{1,\mathrm{mass}}=\sum_p M_p h_p D_p,\qquad
K_{\mathrm{normalized}}=\max_p(M_p/M)K_p,
\quad M=\sum_p M_p.
$$

The first quantity divided by M is normalized W1 in seconds. This equality uses the true original panel supports, not hypothetical equal panels or compressed births.

A simple constructive coupling supported within each panel gives

$$
W_{1,\mathrm{mass}}\le\sum_p M_p h_p\le M\,dt/r.
$$

Proof: couple the conditional measures inside panel p by any probability coupling; their pointwise distance is at most h_p. Multiply by M_p and sum. The exact local CDF calculation usually supplies a much sharper value.

For unequal normalized panel masses p_i and q_i, with common global age-support diameter D, a valid general bound is

$$
W_1(P,Q)\le
\sum_i\min(p_i,q_i)\,W_1(P_i,Q_i)
+D\,\mathrm{TV}(p,q),
\quad
\mathrm{TV}(p,q)=\tfrac12\sum_i|p_i-q_i|.
$$

Match min(p_i,q_i) locally and transport the leftover TV mass within the full support. Zero components need no invented conditional shape: the corresponding minimum mass is zero. A parallel CDF bound replaces D by 1 and local W1 by local CDFsup, followed by truncation at 1 if desired. This is an upper bound, not equality.

For different source labels, their age supports overlap and CDF differences may cancel. The sum of label costs is exact for transport constrained to preserve those labels; it is only an upper bound for unlabelled age transport. Spectral/directional observables require preservation of their labels. An age-only mixture can hide label errors even when its scalar W1 is zero.

## 7. Native width indicator and its conditional use

For actual positive retained panel counts N_p define

$$
R_{\mathrm{native,width}}
=\frac{\sum_p N_p h_p}{\sum_pN_p}.
$$

This is an observable mean birth-panel width of the photons that the native computation retains. It is finite and nonnegative when represented total mass is positive. It is undefined for zero total represented mass.

For any hypothetical positive measure supported on these same panels and having these same panel masses, the within-panel coupling proof bounds its W1 to the actual discrete retained measure by this indicator. This conditional statement is constructive, but the monitor has not established that the unknown exact nonlinear continuum solution has those panel masses. Therefore R_native,width cannot be called a full gas/radiation error bound.

Refining r shrinks the deterministic maximum width at fixed dt. Native mass-weighted widths need not be monotone because the native weights and opacity selector can change. Likewise a decreasing frozen-kernel W1 does not by itself bound the r difference of an evolving gas observable.

## 8. Birth clock, geometry and future observables

With fixed normalized weights p_i, coupling each target atom to its own represented-clock atom proves

$$
W_1\!\left(\sum_ip_i\delta_{dt x_i},
\sum_ip_i\delta_{A_{\mathrm{clock},i}}\right)
\le\sum_ip_i|A_{\mathrm{clock},i}-dt x_i|.
$$

If weights are recomputed with exp(-kappa*A_clock) rather than exp(-tau*x), there is a second weight-change contribution. Measure its probability TV and use the diameter bound; do not apply the fixed-weight formula to two differently weighted measures. A small atom shift does not imply small CDFsup: two unit atoms at distinct clocks have CDFsup one however close the clocks are.

For a fixed label and an L-Lipschitz observable f(A), a coupling gives

$$
|\langle f\rangle_P-\langle f\rangle_Q|\le L\,W_1(P,Q).
$$

For finite masses M and N and bounded f,

$$
\left|\int f\,d\mu-\int f\,d\nu\right|
\le \min(M,N)LW_1(P,Q)+|M-N|\|f\|_\infty.
$$

These become physical energy/ray statements only after a usable L and the correct same-label map have been established. For example, at fixed observation time and fixed birth E_b,n_b, if each a_i is positive and C1 with |H_i|<=H_max throughout the birth interval, then

$$
\left|\partial_{t_b}E(t;t_b)\right|
=\left|\frac{\sum_iH_i(t_b)K_i^2/a_i(t)^2}{E(t;t_b)}\right|
\le H_{\max}E(t;t_b)\le H_{\max}E_{\max}.
$$

Thus that particular fixed-geometry energy observable has a finite age-Lipschitz constant when the stated bounds hold. This derivation does not cover threshold-discontinuous opacity without explicit splitting or an additional bound. It also does not make two different self-consistent gas histories share a propagation map.

A known common later attenuation independent of cohort birth age multiplies both masses and leaves conditional W1 invariant under the common age translation. Cohort-dependent attenuation or a changed gas solution invalidates this simple composition unless its stability and reweighting terms are bounded. BR05 records native finite measures; it does not add such a nonlinear stability theorem.

## 9. Status and ownership contract

- FINITE_POSITIVE: the represented physical mass is positive and all required values are finite. Shapes may be computed.
- ZERO_SOURCE: genuinely zero source input in a generic reference problem. Physical masses and raw moments are zero; shapes are undefined.
- ABSOLUTE_MASS_UNDERFLOW: the mathematical reference mass is positive but the binary64 absolute value becomes zero. Keep a finite log mass and conditional shape when numerically available; do not report zero source.
- NORMALIZED_WEIGHT_UNDERFLOW: count atoms whose positive relative weights become zero numerically, and state the treatment or tail bound. This differs from absolute underflow.
- ZERO_RETAINED_NATIVE: the actual represented retained count is zero. The source may have been positive. A native conditional shape is undefined even if the reference has a shape.
- INPUT_OR_PROVENANCE_ERROR: negative/nonfinite data or mismatch in labels, gas selector, replay, birth clock or retained geometry. The monitor records its failure separately; it does not undo an accepted physics result.
- ORIGINAL_SOLVER_FAILURE: report the solver's own result. Cx(WorkLimit) remains a work-budget failure, distinct from negative populations, invalid source input, lack of forward representability, or established convergence failure.

Observe only the successful local corrector transaction in the fixed-step driver. Predictor calculations do not contribute monitor birth mass or physical ledgers. The new hooks do not instrument rejected outer adaptive trials: any future adaptive caller must buffer these local observations until its own outer acceptance, then export them. This is an integration condition for such a caller, not a BR05 verification claim. A failed monitor may leave diagnostic evidence, but the record must say that it lacks a complete monitor result.

The original physical owners retain source energy, absorption energy, thermal/chemical changes, geometry work and CX half-flows. Diagnostic comparisons create no absorption events and transfer no energy. Native photon-number and total-energy ledger closure is audited separately from quadrature accuracy. No monitor path may renormalize, merge, delete, or move real cohorts.

## 10. Required independent evidence and claim boundaries

The executable monitor should establish exact replay/provenance for actual source labels and actual rate-gas selectors, positive finite node records, original On/Off physical parity in the declared controls, and equality of newborn fields through photo/accepted readbacks where the owner leaves them unchanged. It should export the panel widths and actual retained count-weighted widths, with numerical reference distances independently checked on actual outputs.

A crossed native r-pair is evidence about the measured discretization changes at those particular time/birth grids. Two crossed cells do not establish a universal convergence order. One new Nt16,r8 history can complete a predeclared rectangle with already verified histories, but historical execution evidence must retain its original identity and be distinguished from the new run.

BR05 may therefore conclude that an accepted native history has a verified read-only birth monitor and that the specified r pair has been measured. It may not admit LONGSPAN_SOLUTION or full second order from this monitor alone.

## 11. Primary-source scope

The mathematical derivations above are explicit here. Their foundation is the standard one-dimensional Wasserstein/CDF identity described by De Angelis and Gray, and the same-cell positive coupling construction in Hamm and Khurana. The latter was read at the explicitly pinned arXiv v2 because search metadata and the default retrieval exposed different revisions. No result about nonlinear radiation–chemistry is attributed to those measure-approximation papers.

Mackey's comparison studies timestep and multifrequency errors in specified photoionization algorithms; it supports keeping photon conservation and accuracy distinct. It does not certify this H/He/D Bianchi solver. Fleury, Pitrou and Uzan supplies the Bianchi-I light-propagation context; the actual code's birth/Killing provenance must still be tested independently.

Verner et al. supplies the HI/HeI/HeII fit-parameter source. Its H fitting edge 13.60 eV is distinct from the project binding energy 13.598434599702 eV. The DI gate 13.602134599702 eV and H-equality D opacity are the preserved project contract, not a parameter fit supplied by the Verner table.

See PRIMARY_SOURCE_RECEIPTS.json for exact queries, URLs, version/access scope, and successful/failed accesses. Whole external papers are not bundled in this evidence.

