# Physical fast F4: measured H I rate likelihood and a UVB moment adapter

2026-10-28. Requested old skill `skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop`, built-in1.0.0, read with RESEARCH_POLICY,THEORY_LOOP,CODING_LOOP,EVIDENCE_AND_HANDOFF,REI_EXECUTION_POLICY. Current explicit parallel/publication instructions supersede old routing defaults; this author does not publish or execute IVPs. Requested authority Astra; actual runtime model unobserved.

## Selected useful advance

Implement a correlated likelihood using actual Lyα-forest-inferred H I photoionization rates, and a physically sourced H I/He I/He II photoionization/photoheating table adapter. Calibrate its one common logarithmic amplitude over the measured redshift overlap. This directly reduces the physical F4 source-input obligation. It does not rebrand the existing uncalibrated MeV/CR/injection/stopping channels as calibrated. Physical F4 remains PARTIAL until its complete selected channel and prehistory inputs are fixed; originalphysicalfast4/7 and global33/88 do not increase from one calibrated UV subobligation.

Adopt ON_refined as the default future numerical option: rtol2e-8, scaledatol2e-12, the previously frozen scaled variables. This changes the default selector only; the completed old case bytes and its physical source definitions stay unchanged. The user-requested single-axis17-state BBN-style plot uses the existing ON_refined data. A BBN-style layout describes visualization, not a new BBN or observationally calibrated history.

## Exact source inputs and domains

1. `sources/BECKER_BOLTON_2013.json`: primary Becker&Bolton2013 Tables1–2,7points z=[2.4,2.8,3.2,3.6,4.0,4.4,4.75], d=log10[Γ_HI/(1e-12s^-1)], full7×7 statistical covariance already converted to dex² (printed Table2 values divided100). The source is Lyα-forest inference conditional on hydrodynamic/thermal/cosmological assumptions, not direct photon counting. Preserve EOS shifts and separately reported Jeans systematics. This is a concrete historical data set, not asserted to be the latest2026 consensus.
2. `sources/PUCHWEIN_2019_FIDUCIAL.json`: author ancillary `https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt` with its readme;59rows z0..15.1. Six columns used: Γ_HI,Γ_HeI,Γ_HeII in s^-1 and corresponding heating in eV/s per absorbing target. This is the model's fiducial nonequilibrium-rate table, not the distinct equivalent-equilibrium table and not an observed spectrum. Preserve actual sourceversion and bytes/parsed identity. Exclude the final Compton column because this adapter does not establish its normalization.

Require strictly increasing redshift knots, finite nonnegative rates, positive rates on any log-interpolated interval, symmetric positive-definite covariance, correct dimensions and exact input column names. No diagonal-covariance substitution. A genuinely zero rate may be returned at its exact knot; interpolation touching zero uses explicitly labeled linear-rate interpolation, not a tiny positive floor. For the current likelihood overlap all used Γ_HI values must be positive. Reject extrapolation beyond the supplied support.

Raw UVB rates are available on0≤z≤15.1. Observation-conditioned H I interpolation and common-amplitude calibration claims apply only on2.4≤z≤4.75. The requested historical trajectory beginsz20, so this table alone supplies neither its full prehistory nor the missing15.1<z≤20 bath. Domain failure is explicit MISSING_PREHISTORY, never Γ=0 by default. A future larger-domain run needs an actual named prehistory or a separately chosen starting epoch.

### Actual Lumina history inputs added after successful recovery

Use the newly recovered `sources/lumina/` text files and their metadata from the real `/data-access/` page: global SFRD, volume-weighted neutral-H fraction, HeIII median history, and cumulative CMB optical depth. The previous failure at a guessed `/data` path did not establish absent public numerical data; supersede that specific absence claim with the successful actual-file receipt. These are simulation predictions/subbox histories, not observed measurements or an observational covariance. No inaccessible conversation is asserted to have been searched.

Parse each file's actual units and column names from preserved metadata; do not invent them. Sort rows by increasingz for interpolation while preserving raw file order/bytes. SFRD covers approximately2.9915≤z≤27.4335; HI median4.775≤z≤29.4285; HeIII median2.9924≤z≤29.4285; cumulativeτ covers0≤z≤49. Check actual exact endpoints from each parsed file rather than those rounded prose numbers. A domain-report table atz20,10,6,4,3 must explicitly distinguish AVAILABLE and OUT_OF_RANGE for each history. Use piecewise-linear interpolation in z for all four Lumina histories, preserving nonnegative SFRD and bounded fractions without floors. This explicit finite reconstruction is not an interpolation-error measurement. These functions are new empirical-model input adapters, not another cosmological trajectory.

Check that the published fraction medians are finite and within[0,1]. Detect labeled percentile/min/max inversions rather than sorting them into a manufactured band. In the HeIII source, the final row has raw15.87th percentile above median and raw84.13th below it, with min>max. The likely complement-without-label-reversal explanation is not an adopted correction. Median-only interpolation is permitted, and uncertainty-band interpolation returns UNRESOLVED_QUANTILE_LABELS. The raw columns stay unchanged. Source plots/metadata may support a future explicit complement transformation withp→1−p and min↔max; that repair is outside this unit.

An SFRDρdot_star in its stated comoving units maps to an ionizing emissivity only after supplying a photon-production yieldξ_ν and escape fractionf_esc (and mass/time/volume conversions): ε_photon,com(ν,z)=f_esc(ν,z) ξ_ν(z) ρdot_star(z). A proper emissivity adds the(1+z)^3 volume factor when the cosmological scale normalization is explicit. Transport/opacity and boundary history then map emissivity to the local F_E orJν that entersΓ. None of ξ_ν,f_esc,hard nuclear spectra or CR yields is inferred from SFRD alone. The newly available high-z history is a real advance toward source prehistory, while a matched localz20 photo/T/ne bath still needs those missing mappings. Likewise volume-weighted neutral fraction cannot be imposed as each local gas parcel's ionic fraction, and cumulativeτ from the source's fiducial cosmology cannot silently become a directional Bianchi observable.

## Observable and energy mapping

Let Jν be energy-specific intensity per area,time,frequency,steradian and E=hν. For isotropic targets at rest,

    Γ_X = 4π∫_(νX)^∞ Jν σ_X(ν)/(hν) dν,
    ε_X = 4π∫_(νX)^∞ Jν σ_X(ν)(hν−I_X)/(hν) dν.

Γ is s^-1 per target, ε energy/s per target. In number-flux energy variables F_E=4πJ_(E/h)/(hE), Γ=∫F_EσdE and ε=∫F_Eσ(E−I)dE, with one consistent energy unit throughout. The supplied table already contains these integrated moments; do not apply an extra4π or c. Using y_X=n_X/nHref, events/Href/s=y_XΓ_X, photoheat/Href/s=y_Xε_X, and ionization internal-energy gain/Href/s=I_X y_XΓ_X. Absorbed photon energy carried by this channel is their sum. Per-volume rates multiply by the matched proper nHref. These event/heat identities support a future generator without inventing a photon spectral distribution.

The six moments do not determine a complete spectrum. They do not provide Li-ionizing rates, MeV nuclear-photon flux, CR inclusive yields, inverse-weak lepton baths or charge-dependent stopping. The partial adapter must return these fields as MISSING_INPUT, not zeros and not the previous toy constants. D/T electronic copying from H, if a later consumer uses it, must retain its explicit isotope-equality approximation; it is not an independently calibrated D/T cross section. The rate adapter also supplies no gasT,ne,H,shear or initial populations. It is a typed radiation input, not a complete thermochemical bath.

## Correlated amplitude calibration, directly executable

At each observed z_j interpolate log10Γ_HI,template linearly in z using the actual table. Let m_j=log10[Γ_template(z_j)/(1e-12s^-1)], r=d−m and C the observed covariance. The constant common amplitude A=10^β predicts m+β1. Its Gaussian statistical objective is

    χ²(β)=(r−β1)ᵀ C^-1(r−β1).

Solve linear systems by Cholesky rather than forming C^-1 explicitly. Set W=C^-1 symbolically. Differentiation gives

    βhat=(1ᵀWr)/(1ᵀW1),
    Var(βhat)=1/(1ᵀW1),
    χ²min=rᵀWr−(1ᵀWr)²/(1ᵀW1).

Report βhat,Ahat,σβ,χ² before/after,7input residuals and6nominal degrees of freedom for this statistical one-amplitude fit. Ahat times all six source moments is a fixed-template rescaling assumption: H I data constrain its amplitude; helium/heating rescaling inherits the template shape. Do not report those six quantities as six independently observed calibrations. The factor is valid as a model over the fit overlap; outside the overlap a table value times the factor is labeled EXTRAPOLATED_CALIBRATION_ASSUMPTION and excluded from the default calibrated adapter.

For the supplied EOS nuisance, define θ=(γ_EOS−1.4)/0.2∈[−1,1] and the verified positive endpoint shift v in dex, so data become d+θv. Use residual r+θv−β1. Eliminate β with

    β(θ)=[1ᵀW(r+θv)]/(1ᵀW1),
    P=W−W1(1ᵀW1)^-1 1ᵀW,
    θhat=clip[−vᵀPr/(vᵀPv),−1,1].

If vᵀPv is numerically zero under a scale-aware1e-12 relative test, the nuisance is degenerate with the amplitude: report the degeneracy and both θ endpoints rather than divide by it. This boxed profile has no Gaussian prior onθ and is not a marginal posterior. Report its χ² and β alongside the statistical fit; do not attach the statistical σβ as a full marginalized uncertainty. Jeans/history systematic endpoints remain in the source file and in the report as NOT_PROFILED; do not quadrature-add them without a covariance model. A large χ² is evidence of template-shape/model mismatch under this likelihood, not a physical impossibility proof.

Also implement an observation-only ΓHI adapter: interpolate d linearly between its redshift knots, Γ(z)=1e-12*10^[w(z)ᵀd]. Return dex variance wᵀCw and covariance w(z)ᵀCw(z') for two queried redshifts, and the EOS shift wᵀv. Interpolation is a finite reconstruction; error between measurement knots is not measured by C alone. This adapter has no heating/helium fields.

## Why the new likelihood cannot calibrate nuclear production by itself

For a nonnegative finite photon spectrum with amplitudes f_b, atomic moment constraints are d=Kf. Fewer independent measured moments than spectral amplitudes leave null directions; photonuclear rates k_nucᵀf are fixed only if the nuclear functional is determined by those constraints on the admitted spectral domain. This is a linear algebra observation, not a new universal no-go. With two above-threshold mono-bins E1,E2 and one Γ measurement, parameterize event weights w1=(1−u)Γ,w2=uΓ,0≤u≤1 and fluxes f_i=w_i/σ_i. All choices have the same Γ, whereas ε/Γ=(1−u)(E1−I)+u(E2−I). Even heating is unconstrained by Γ alone. MeV photons and CR protons require their own source data/transport, so an atomic UV amplitude cannot legitimately fix the n/T source history. The next physical F4 delivery must specify those additional channel inputs or an explicitly narrowed scientifically justified process selection, rather than quietly retaining toy rates.

## Model applicability: Bianchi and the current pilot

Γ,ε and populations are local normal-tetrad scalars; inferred observational redshifts and sightline selection are not automatically the current mean-scale-factorz. The adopted observational covariance came from its source's inference framework. Use this calibration as a conditional empirical UV input and cross-model diagnostic until the observational mapping to the substantial-shear donor (Ωσ0=.06) is supplied. The default likelihood does not constrain that shear. Angular spectra/stress and signedσ:π remain separate tensor inputs. Charge and baryon event balances from the previous operator are retained by future consumers; replacing Γ never permits changing isotope totals or electron normalization by hand.

Existing ON_refined histories may be displayed and compared, but rescaling stored populations by Ahat is forbidden: coupled chemistry is nonlinear and a new physical source requires an authorized forward solution. No old IVP is rerun in this unit. Optional old-pilot Γ comparison must use its actual saved clock and affine-in-proper-time hazard interpolation; it is not required for completing the primary UVB-table calibration. Reconstructing the old clock anew is unnecessary when saved source_history_qss.csv contains it.

## Coding acceptance and finite resources

New files only in this unit. Required implementation: table loading/domain checks, log-positive interpolation with explicit zero convention, Cholesky likelihood/profile, partial adapter outputs with units/statuses, actual Lumina median/SFRD/τ history adapters and their domain report, ON_refined default selector, and saved-data plot. Required checks: exact-knot interpolation; correct factor100 covariance conversion already present at input; SPD/symmetry; independent direct quadratic residual atβhat; amplitude scaling and β shift equivariance; correlated versus diagonal fixture distinguished; θ boundary/degeneracy behavior; covariance interpolation; zero and out-of-range handling; event/heat identity; no unsupported physical fields silently filled; actual HeIII quantile-label inversion detected with median retained and band rejected.

Numerical formula tolerance relative1e-11, absolute1e-13 in normalized likelihood quantities, with independently computed explicit residual rather than cancellation-prone χ² subtraction as the primary reported value. Preserve both formulas for comparison. Statistical fit and EOS profile must be reproducible from the actual7points; a synthetic check alone does not complete this unit. At most one bounded non-IVP suite under newly recorded main temporary620; root fixes child/wall/reserve before launch. Retain main605.47145, policy600, and NO_MORE_IVPs. No solver path is invoked.

Presentation authorization: original `rei_external_sources_20261028/BUDGET_AUTHORIZATION.json` records explicit user approval of cumulative65, with closeout restoring the policy ceiling but no user revocation/expiry. The subsequent pilot authorization calls it a continuing approved cumulative ceiling. The present user explicitly requests another saved-data rendering of this result. The minimal justified interpretation is a fresh2CPU-second+0.5tail reservation against the same approved65 with inherited62.468055494, yielding64.968055494 maximum; old attempts/reservations remain closed. This reuses persisting authorization, not unused old attempts or a transferred ledger. Record the present request, old approval and fresh job; restore original30 afterward. If the actual measured/required work exceeds65, stop that job rather than pretend the general<50% policy authorizes a new larger presentation ceiling.

## Actual symbolic evidence

Wolfram evaluator called with symmetric2×2W to check the derivative atβhat and profiledχ² identity, returning{0,0,g,0}; the remaining entries check a normalization identity and the two-bin heating expression. A separate call evaluated the derivative of(r+xv)ᵀP(r+xv) atx=−vᵀPr/(vᵀPv), returning0. These are exact identities for the general finite-dimensional formulas by the displayed algebra, not an empirical fit result or independent review. Actual inputs/results are preserved in PHYSICAL_NEXT_CONTRACT.json. Source-agent primary table recovery is separate evidence; direct OUP opening by this author failed, so this author does not claim an independent successful paper-page readback.
