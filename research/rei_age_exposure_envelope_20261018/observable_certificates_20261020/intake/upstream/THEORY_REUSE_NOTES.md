# V8 upstream intake and independent theory notes

## Actual fresh upstream result
At 2026-10-20 06:07:05 UTC the current VigilODE repository had 153 branches and 76 pull requests. Existing reused affine pin and PR71/73/74/75 heads are unchanged. The new completed PR76 midcheck was published after the previous 02:41 intake, before the v7 final delivery. Its six retrieved manifest members match SHA256. Independent lightweight parsing confirms 39 result rows, 312 valid timing blocks, 30 pairs, 26 matched pairs and all 30 paired medians. The upstream full-state audit is read, not independently rerun.

The post-delivery hybrid branch at frozen SHA 2b828f81512a11cc35229bc77453f305df33d268 has a native compile failure in run39377432935: E0308 at src/native.rs201, MutexGuard<Work> dereference mismatch, exit101. No new native benchmark is admitted from it. Its generated-model Bernstein residual construction is useful future context; importing that separate generated model is unnecessary for the present fixed-hazard observable unit.

## Primary literature actually read
Catalano, Lijoi and Prünster, Electronic Journal of Statistics14(2),3366–3395(2020), DOI10.1214/20-EJS1746, author full text https://martacatalano.github.io/files/2020_EJS.pdf. Theorem9 and its proof §6.7, Eq(30), establish exponential coupling bounds for nonnegative cumulative hazards. The paper's random-measure assumptions are distinct from REI's finite labelled deterministic input. The common scalar identity and Jensen step are rederived below.

Habeck, Rudolf and Sprungk, Stability of doubly-intractable distributions, https://arxiv.org/pdf/2004.07310, gives related stability of normalized positive densities. It supplies context for the need to control normalization denominators. No theorem from that Bayesian setting is asserted to directly certify REI.

## Exact fixed-model definitions
Let w_i,E_i,lambda_i,s be unchanged finite nonnegative exact dyadic inputs. Let Lambda_i=sum_s lambda_i,s in exact arithmetic. For clocks a_Ai,a_Bi>=0 define
n_Xi=w_i exp(-Lambda_i a_Xi), N_X=sum_i n_Xi, M_kX=sum_i a_Xi^k n_Xi.
The finite label set and species coefficients remain paired. All quantities can be restricted to the same fixed subset S: all, sensitive (Lambda>0), or passive (Lambda=0). A normalized mean mu_X=M_1X/N_X requires a proved positive denominator N_X.

## Labelled observables
Set a=min(a_A,a_B), delta=abs(a_A-a_B), u=exp(-Lambda a), v=exp(-Lambda delta), sigma=sign(a_A-a_B).
Then delta_n=n_A-n_B=-sigma*w*u*(1-v).
For k>=1:
delta_mk=sigma*w*u*[(a+delta)^k*v-a^k].
For a chosen exact represented center c,
delta_qc=delta_m1-c*delta_n=sigma*w*u*[delta*v-(a-c)*(1-v)].
These identities also apply at delta=0 and Lambda=0. At Lambda=0, delta_n=0 and delta_qc=sigma*w*delta: passive age changes must survive.

Let d_i=abs(delta_n_i). Energy envelope B_U=sum E_i d_i. For Lambda_i>0, species event delta_Ais=-(lambda_i,s/Lambda_i)delta_n_i and B_s=sum(lambda_i,s/Lambda_i)d_i. Passive event contributions are zero. Consequently sum_s B_s=sum_i d_i in exact arithmetic. Outward endpoints need only enclose this identity; no artificial bitwise equality is required.

Moment envelopes can use sum abs(delta_mk), and centered envelope B(c)=sum abs(delta_qc). Signed interval accumulation, if separately justified, can be intersected with these envelopes. Absolute labelled sums and absolute signed totals are different observables.

## Centered normalized mean
By direct algebra:
mu_A-mu_B = [delta_M1-c*delta_N + (c-mu_B)delta_N]/N_A.
If I_B encloses mu_B, choose any finite exactly represented c and set r_B=max(|I_B.lo-c|,|I_B.hi-c|). With verified upper bounds B(c),D>=|delta_N|, and N_A.lower>0:
abs(mu_A-mu_B) <= [B(c)+r_B*D]/N_A.lower.
The symmetric denominator choice follows by interchanging A/B. Both bounds and a direct outward difference of mean intervals are independently valid, so their minimum is valid. Do not replace N_A by total all-node mass when reporting the sensitive-subset mean.

If D=sum_i|delta_n_i|, triangle inequality gives B(mu_B)<=B(c)+|mu_B-c|D. Thus exact reference mean is already optimal for this particular L1-based bound. A midpoint of the proved reference mean interval plus its radius is an economical numerical choice. When a tighter signed-total |delta_N| bound is used, optimization of c can improve the combined bound, but is not necessary for the validity of this unit.

## Saturating finite-label Laplace bound
For M=sum_i w_i>0 and H=sum_i w_i Lambda_i delta_i:
D=sum_i w_i exp(-min(tau_Ai,tau_Bi)) [1-exp(-abs(delta_tau_i))]
 <=sum_i w_i[1-exp(-Lambda_i delta_i)]
 <=M[1-exp(-H/M)]<=H.
The middle step is Jensen for the concave function1-exp(-x); it is the finite labelled analogue of the primary paper's scalar argument. It does not permit substituting an unlabelled age-marginal Wasserstein distance for H.
A nonuniform survival-weighted form with z_i=w_i exp(-min tau_i), Z=sum z_i, H_z=sum z_i abs(delta_tau_i) yields
D<=Z[1-exp(-H_z/Z)]
when Z>0. F(Z,H)=Z[1-exp(-H/Z)] is increasing in both nonnegative arguments, useful when forming outward numerical upper bounds.

## Numerical contract
All clock subtraction, Lambda sums, ratios lambda_s/Lambda and center age differences must refer to the model's exact dyadic interpretation. Reusing the existing exact rational interval constructors avoids accepting ordinary floating subtraction as exact. Directional intervals must contain subnormal terms and passive moments. The zero-age-gap branch should return exact zero to avoid artificial inflation. Denominator failure is a typed unavailable normalized-observable result, not a numerical zero or a passed gate.

The current unit is observable analysis on an already frozen fixed model. It adds no native trajectory, no actual nonlinear Grackle response certificate and no new physical configuration. No universal no-go or literature-priority claim is needed.

