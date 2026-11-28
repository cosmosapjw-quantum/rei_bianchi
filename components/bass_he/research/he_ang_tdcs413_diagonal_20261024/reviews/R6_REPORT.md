# R6 independent theory and source review — HE-ANG-TDCS413-DIAGONAL

Date: 2026-10-24. Reviewer: separate `independent_review` Astra role requested by the user; actual runtime model identity is not observable from this review. **Verdict: PASS for the frozen, finite nominal model comparison.** No current blocking finding. The root may freeze this theory and proceed to its separately authorized R7 and implementation gates. This receipt is not numerical execution approval or physical-provider admission.

## Reviewed snapshot and method

- `THEORY_KO.md`: SHA256 `da1669bad79e1ed6c6711a42aa13ec861908a9f1951a067473d249bcfed928da`.
- `FROZEN_CONTRACT.json`: SHA256 `38e10f6d0adb65dbd9b44a2f13773923df073974e83221ec7315af62eb596f5b`.
- Source candidate JSON: SHA256 `26a57a253ae6971ccd228738a1b7e7764ee5c8db1967fbe48df9770ff5a875df`; CSV: `d0839282f665a77d1a645d0d8811e31f1eba72705fd44cbbb0243600c8a13386` in `heang_next2_source_20261024/`.

I independently differentiated and rearranged the formulas by hand, checked signs, dimensions, domain restrictions, and the rational toy, read the source report and candidate intake, and visually compared the selected cells with the primary table images `private/table1_diagonal_crop.png` and `private/table1_5000.png`. The source is FIAS-R-39, June 1978, Table 1, report page 30 / PDF page 33, not a date inferred from the local filename `weigold1979.pdf`. The PDF hash in the frozen contract is `aaa750d5d5f0652ba7e6090878f938174fc26268265c256022c4d9437c3a96a8`.

The physmath R6 source/derivation/sign/domain policy is applied. Existing PWBE spin/transition conventions and prior completed reviews are reused; no old suite was replayed. No solver, scientific Python, test, renderer, remote evaluator, or binary64 numerical experiment was run by this reviewer. Hashing and document reads do not establish any numerical acceptance metric.

## Source and normalization assessment

The independently read selected triples `(angle, value, parenthesized error)` are `(32,10,3), (34,11,3), (36,17,3), (38,28,4), (40,50,4), (42,76,5), (43,82,6), (44,100,6), (50,30,3), (52,15,2), (54,4,1), (56,2,1), (60,0,1)`. In particular, the 38-degree value is 28(4), and 60-degree 0(1) remains an observed zero. The three previously excluded settings 45, 46, and 48 degrees remain excluded; no value is inferred from the model or from neighboring rows.

The table supplies a relative coincidence TDCS series at printed incident energy 413.6 eV and equal outgoing energies 200 eV, with equal polar angles and opposite azimuths. The adopted beam-axis geometry is consistent with the selected diagonal series. The relative normalization and the reference-series normalization-error entry do not supply an absolute cross section. The reported point errors may be used as positive deterministic weights, but unknown covariance and detector response prevent interpreting the minimax multiplier as a confidence level, p-value, or guaranteed physical error bound. These limitations are explicit in the theory and contract.

The nominal mapping `U=27.2 eV` gives `epsilon=125/17`, `epsilon0=517/34=2 epsilon+1/2`, hence `k^2=250/17` and `r^2=517/17`. This is internally exact at the declared nominal input. It is not a claim that the measured Hartree conversion is exactly 27.2 eV, and it does not resolve experimental rounding. Keeping that distinction is essential to the scope of any ensuing model discrepancy.

## Independent derivation checks

### Symmetric geometry, spin, dimensions, and point counting

For equal magnitudes and opposite transverse components, `q = (r-2 k cos(theta)) zhat`. Setting `z=r-2 k cos(theta)` yields `q^2=z^2` and `Delta^2=r^2+k^2-2rk cos(theta)=k^2+r z`. Under detector interchange both the momentum-transfer denominator and the bound-state form factor are unchanged, so `d=x=(t-h)/(k^2+r z)`.

The previously derived unpolarized spin trace is `|D|^2+|X|^2-Re(D X*)`. With equal real reduced amplitudes, this reduces to `d^2`; equivalently, the weighted singlet is `(1/4)|2d|^2` and the triplet is zero. There is no extra factor of two or one half for this detector-labeled point density. The source's printed Eq. 21 interference coefficient remains distinct from this adopted model trace; this benchmark neither silently adopts that coefficient nor claims a correction to the author's intent.

The reused transition normalization gives `K=(32/pi^2)(k^2/r)d^2`. This is an atomic-unit TDCS number with dimensional factor `a0^2/Eh` per two solid angles. The energy-shell substitution between the two outgoing energy labels has unit absolute Jacobian. `f=K/K(44 degrees)` is dimensionless and a common scale is absorbed by the fitted amplitude; therefore absolute normalization is not inferred by the fit.

### Derivative and unique peak

Direct quotient differentiation gives

`d'=[-4z(k^2+r z)-r(1+z^2)+rh(1+z^2)^3]/[(k^2+r z)^2(1+z^2)^3]`,

which simplifies exactly to the stated numerator `N=rh(1+z^2)^3-r(1+5z^2)-4k^2 z`. Its derivative is `N'=-4k^2-10rz+6rh z(1+z^2)^2`, with the signs in the theory correct.

The three-piece proof is sufficient on `[-1,k)`. On `[-1,-1/2]`, writing `x=-z` gives the strict lower bound `56x-6-30x^2`, positive at both endpoints and throughout by concavity. On `[-1/2,0]`, `N'<-26`, while `N(-1/2)>14.5` and `N(0)=r(h-1)<0`, proving exactly one root. On `[0,k)`, the unsimplified quotient numerator is strictly negative because `t'<=0`, the denominator is positive, and `t-h>0`.

The domain bridge is substantive and checked: the rational bounds on `r` and `k`, together with the alternating Taylor upper bound for cosine, imply `z(32)>-0.99783>-1`. The lower cosine bound gives `z(32)<-0.92612<-1/2`. At 60 degrees, `z=r-k>0` since `r>k`, and `r-k<k` since `r^2<4k^2`. Thus the entire angle window lies inside the proved positive-denominator domain and contains the unique root. Moreover `dz/dtheta=2k sin(theta)>0` on this window, so the signs of the derivatives in angle and in `z` agree. With `d>0`, the same signs apply to `K`.

Consequently the unique maximum on the full declared window is at `theta_star=acos((r-z_star)/(2k))`. Since `z_star<0`, its angle is smaller than `acos(r/(2k))`, the zero-recoil-momentum angle. This is a consequence of this nominal model, not an inference about the experimental peak or a theorem for all energies/geometries.

### Weighted minimax, including the zero observation

Solving each absolute-value inequality gives the stated lower and upper scale endpoints. Since `y_i>=0`, `s_i>0`, and `kappa>=0`, every upper endpoint is nonnegative. Thus requiring every lower endpoint to be no greater than every upper endpoint is necessary and sufficient, including the constraint `a>=0`. Multiplication by the strictly positive `f_i f_j` gives exactly

`kappa >= (y_i f_j-y_j f_i)/(s_i f_j+s_j f_i)`.

Taking the maximum over ordered pairs and zero therefore gives the full optimum, not merely a pairwise lower bound. For an active positive pair, equality of its opposing endpoints produces `a=(y_i s_j+y_j s_i)/(f_i s_j+f_j s_i)`, with residuals `-kappa s_i` and `+kappa s_j`. The nonnegative source assumption and at least one positive observation also exclude a zero optimal scale here. When `kappa=0`, all `y_i/f_i` coincide at a positive scale under the stated assumptions. The formula applies to the retained `y=0` row without division by that observation.

Independent hand substitution in the toy gives `a=2/3`, residuals `(-1/3,-8/3,8/3)`, optimum `kappa=8/3`, and active rows 2 and 3. Multiplying all model values by a positive constant leaves kappa unchanged and divides the fitted scale by that constant. Multiplying all observations and their errors by the same positive constant also leaves kappa unchanged and multiplies the fitted scale by it. These make useful independent implementation oracles.

## Numerical plan and limits of this receipt

The proposed independent vector-amplitude route, reused point kernel on the thirteen new geometries, exact rational toy, interval-feasibility solution, and 80-digit reference address distinct failure modes. Comparing normalized shapes as well as the unnormalized kernel is necessary because fitting a common scale can conceal an overall prefactor error. All-row residual and active-pair checks are appropriate. The unique-root bracket avoids an unrestricted numerical search.

The fixed-input binary64 tolerances are plausible acceptance targets, but this read-only R6 receipt does not certify that an implementation meets them. C9 must inspect actual input/code provenance, raw outcomes, independent reference construction, and the saved-output figure. A numerical implementation can pass while the deterministic model discrepancy is large. Conversely, a small discrepancy would not establish a full joint physical provider, an experimental confidence statement, or agreement outside the thirteen admitted points and the explicitly declared model window.

## Findings and disposition

No current blocking defect was found in the reviewed snapshot. There is no requested theory repair and no additional audit or execution gate beyond the frozen workflow. Preserve the pre-model exclusions, observed zero, nominal-unit qualification, distinct source Eq. 21 convention, physical `SOURCE_INPUT_PENDING` gate, and all previous measured/unknown costs. This review adds no scientific child and reallocates no budget.

**Source-citation pass scope:** the selected primary Table 1 cells and geometry/relative-normalization reading, the declared nominal mapping, and reuse of the previously reviewed PWBE derivation. This does not certify an unread publication history, all possible errata, experimental covariance, detector response, absolute scale, or the broader physical model.
