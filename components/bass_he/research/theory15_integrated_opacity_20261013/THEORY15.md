# THEORY15: source-bound integrated opacity from existing CR exposure data

Unit: HERE_RUX03_SOURCE_BOUND_INTEGRATED_OPACITY_15. Date: 2026-10-13.
Status: derived and checked; independent scientific review pending.

## Actual source and scope

Reuse the fixed post-G1 CR_TIME_DONOR model, commit15193ccf88207de3a5134a4dc56c72e8ed1c7262, and its original MODEL, exposure interval and all-time donor error. New work evaluates a passive observable with exact rational arithmetic. It does not rerun the source IVP or the full donor cascade.

The reference cell has V=1.0060180360540648648 m^3, nuclear count13, initially thermal electron1 plus two active electrons, total3, HI7 and HeI3. The proper source horizon is h=100000s. Ionization and downward stopping, the energy grid and total-gas EOS remain unchanged. The diagnostic represents a spatially homogeneous medium followed for the source duration; it is not a single crossing of a cube of side V^(1/3).

Thomson opacity uses all free electrons. For exact KN diagnostics add the explicit common-frame isotropic active-bin and same-temperature Maxwell–Jüttner bath closure. Do not change the source EOS. Signature is(-,+,+,+), physical velocities include c, and photon E=hbar*omega. The70eV diagnostic is in the common rest frame. Model and measured-constant uncertainties remain distinct from the following exact-real numerical enclosures.

## 1. Exact exposure representation

The inherited first-event model supplies

    x_a(q)=X_a0[1-exp(-kappa_a q)],
    dq/dt=P/V,
    P(q)=1-x_H-x_He-z_P(q),
    z_P(q)=V integral_0^q lambda_P(n_thermal(v)/V)dv,
    n_thermal=1+sum beta_a x_a.

The total free-electron count is N=3+x_H+x_He, since an ionization edge changes the active count by M-1 and the bath count by2-M, summing to1. Stopping redistributes free electrons without changing N.

Hence the new observable is

    tau_T,sur=c sigma_T(3h/V)+c sigma_T I,
    I=integral_0^{q(h)}(x_H+x_He)/P dq.

The constant census term uses exact h directly. Only the small ionization excess is integrated in q.

## 2. Certified rational integral, not an ODE replay

The saved source exposure bracket is

    q_-=99327.871978146434238310354571715721513707759910680253209715185089,
    q_+=99327.871978180579471736004008665379050197705296302313852614717041 s/m^3.

Use the actual rational source coefficients and all-time lambda_P bounds. On0<=s<=1, the degree4 alternating polynomial of1-exp(-kappa q s) is a lower bound and degree3 is an upper bound; every kappa q_+<1e-8. Sum these to X_L,X_U at q_- and q_+ respectively. Set

    y_L=X_L+V lambda_- q_-s,
    y_U=X_U+V lambda_+ q_+s,
    ycap=y_U(1)<1/500.

With G6(y)=sum_(j=0)^6 y^j and0<=1/(1-y)-G6(y)<=ycap^7/(1-ycap),

    I_-=q_- integral X_L G6(y_L)ds,
    I_+=q_+[integral X_U G6(y_U)ds
              +ycap^7/(1-ycap) integral X_U ds].

All integrals are exact polynomial coefficient sums. Positivity and monotonicity justify replacing the unknown q(h) by its bracket endpoints. The resulting interval is

    I in[0.00062780949239541925788746338145753972,
         0.00062780949239613906965575013595078185] s/m^3.

At the specified central constants c=299792458m/s and sigma_T=6.6524587051e-29m^2,

    tau_T,sur in[5.94727990851930625514596617230557846e-15,
                 5.94727990851930625516032178831133607e-15].

These decimals display exact rational endpoints, whose width is about1.44e-35. The passive thermal-only comparison is1.98242663246402933418e-15; total/thermal is3.00000000561292815. That comparison reflects the two active electrons in the actual initial data and does not assert a defect in the original source code.

## 3. Integrate the inherited donor error one order further

The original full-versus-surrogate positive-energy error obeys

    ||Z-Zhat||_1<=B(t)=C_I J2(L,t)+C_P K(L,lambda_P,t)+C_S K(L,lambda_S,t),
    Jn(a,t)=t^n sum_(r>=0)(at)^r/(r+n)!,
    K(L,lambda,t)=lambda/(L+lambda)[L J2(L,t)+lambda J2(-lambda,t)].

The coefficients are fixed all-time bounds for the selected horizon. Since d_t J3=J2 and J3(a,0)=0,

    Bint=C_I J3(L,h)
       +sum_(a=P,S)C_a lambda_a/(L+lambda_a)
                          [L J3(L,h)+lambda_a J3(-lambda_a,h)].

Use degree40 positive series plus a geometric tail for a>0, and degree41/40 alternating lower/upper series for a<0; all |a h|<1. J3(0,h)=h^3/6 and lambda=0 is a continuous branch.

Charge gives |delta N|<=||delta Z||_1/Bmin with actual Bmin=13.60570000000000057...eV. Therefore

    R_N=c sigma_T Bint/(V Bmin)
       =1.21014029518830141299529...e-22,
    Bint=0.08305379653640318942568...eV*s.

This is2.97265331672544 times smaller than h*B(h) converted to the same observable. The slow-parent stopped-donor component occupies99.68641958% of the sufficient integrated budget. This is a bound decomposition, not a measured decomposition of the unknown full error.

Since this selected model only ionizes or redistributes electrons, N>=3. Intersecting the transferred enclosure with the exact initial-census lower bound yields

    tau_T,full in[5.94727989599854402997511e-15,
                  5.94728002953333577399046e-15].

The tiny surplus1.2520762225e-23 is smaller than R_N. Thus the full total-depth interval is established, while isolating that smaller reaction increment requires reducing the donor bound.

## 4. Exact KN diagnostic without a new spectrum trajectory

Let m=m_e c^2=510998.95069eV and eta=70/m. The exact cold-electron KN factor S0 is enclosed by a positive rational angular integral. With y=2eta s,A=1+(1-2s)^2, use degree7/6 alternating lower/upper polynomials for r=(1+y)^-1 in

    S0=(3/4)integral_0^1[A r^2+y^2 r^3]ds.

This yields

    S0 in[0.99972612438017813356016738716942134914,
          0.99972612438017813356016742288594019804].

THEORY14 gives |F_eta(gamma)-S0|<=(10/3)eta(gamma-1) for an isotropic active electron and |s_MJ-S0|<=10eta theta for the bath. The parent total-gas EOS supplies theta=2U/[3m(Nnuc+n)]. As n<=Nnuc=13 and the positive closed energy ledger gives U+sum E_jN_j<=K0=31.12435104103435615...eV,

    |chi_KN-S0 chi_T|<=c sigma_T/V *10eta K0/(3m).

The integrated shape radius is5.51358655786418748e-23. It uses neither an inverse-low-energy-cutoff factor nor a numerical thermal-tail truncation. Apply it to the full Thomson interval, keeping chi_KN<=chi_T:

    tau_KN,full in[5.94565102589490772470911e-15,
                   5.94565126966485870215154e-15].

Its midpoint is5.94565114777988321343e-15 and halfwidth1.21884975488721216e-22. The midpoint represents the certified interval, not a sampled full-cascade trajectory. The explicit cold-reference central integral is separately5.94565109354810639701e-15.

## Actual evidence and remaining tasks

Local installed Wolfram15.0.0 evaluated the new source-bound observable in an exact-rational batch:22 checks True, reported kernel time0.348429s, exit0. Actual xTensor1.3.0 returned9 groups and11zero tensor residuals. The convolution/limit batch returned12checks True. A separate Python Fraction polynomial/convolution implementation passed14checks and matched six key exact outputs.

First xAct rest-frame substitution was applied before contraction introduced the Doppler scalar; corrected ordering preserved the same equation. First analytic script had an extra closing bracket and produced no result despite shell exit0; it was rejected. Final validation checks output existence, expected names/counts, literal True results and exit status. All failed files/logs remain in the archive. The xTensor FindFile hash identifies the installed package entrypoint, not a claimed byte match to a different internal file.

No source ODE, full donor cascade, new native HE stage or independent external scientific reviewer was run. Source simulation evidence is inherited with its original assumptions; this new integrated observable was actually evaluated. Preserve the existing HE native endpoint/residual, HH, RUX/all-Bianchi/D2.3 and review obligations.

Next owner application: use this J3/census consumer on a refined CR donor certificate, prioritizing the dominant slow stopped-donor contribution if that matches the requested observable accuracy. No new abstract gate is required for the existing BASS_HE endpoint/residual implementation.

Primary comparisons: Le-Cambier2017, Physics of Plasmas24,122105, arXiv1711.05946; Poutanen-Vurm2010, ApJS189,286, arXiv1006.2397; Sarkar-Chluba-Lee2019, arXiv1905.00868. SciSpace and Exa were called and original text/bibliography compared. Numerical constants use the declared CODATA2022 central model, with measurement uncertainty separate.

The full Korean proof, actual runtime scripts/JSON/stdout, exact inputs, failures and manifests are in the45-member117244-byte evidence ZIP. Archive SHA256:3fa3799b4db34332c2ff62cac739e1aded07c1b870297516171370daae25192c. Cloud delivery IDs are recorded separately after acknowledgements.
