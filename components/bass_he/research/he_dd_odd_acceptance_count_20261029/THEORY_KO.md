# HE-DD odd acceptance and conditional marked-pair moments
Base BASS_HE PR111 0e643121b62a65dd821ea563051c59722a828a8f; reuse PR110 exact source blob 8eec0e162e5ded507a3af1259e60361ed474c376. Read-only donor PAIR-COUNT15 ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce. Central28/88 HE14/18 physical delta0.

Let p(mu)=p(-mu), mu∈[-1,1], q(mu)>0 and sup q/inf q<=r (r>=1). m_q=E_p[q mu]/E_p[q]; b_q=E_p[q mu²]/E_p[q]. For x=|mu|, define a(x)=(q(x)+q(-x))/2>0, d(x)=(q(x)-q(-x))/2. Then |d|<=eta a, eta=(r-1)/(r+1). Pairing ±x under even p, |m_q|<=eta E_a[x]<=eta sqrt(E_a[x²])=eta sqrt(b_q). Equality for a two-point ±x distribution with q+/q-=r (not claimed sharp within the continuous L-Lipschitz source class). Unordered identical-D event response invariant under daughter swapping must be even: in that case m_q=0. A nonzero odd m_q can concern *arm-labelled or tagged selection only*, not intrinsic physical event asymmetry.

Inherited PR111 ratio theorem transports a<=b<=u from source-certified PR110 to b_q in [a/(a+r(1-a)),r*u/(1-u+r*u)]=[B-,B+]. Then m_q²<=eta² B+, centered single selected-daughter mark Var(K+)=Delta²(b_q-m_q²) in [Delta²(1-eta²)B-,Delta² B+]; squared absolute mean shift <=Delta² eta² B+. K±=K0±Delta mu in the alpha-target rest frame, K0=153.0767609 MeV, Delta²=12834742575893748070725/3378807374235230161 MeV². These are conservative exact rational *conditional* envelopes, not measured detector errors.

For N nonnegative integer tagged event records, lambda=E N, nu=Var N, with marks Y_i=(K0+Delta mu_i,K0-Delta mu_i) iid and independent of N, S=sum_i Y_i. Let v=Delta²(b_q-m_q²), ybar=(K0+Delta m_q,K0-Delta m_q). Then E S=lambda*ybar and Cov(S)=lambda*v[[1,-1],[-1,1]]+nu*ybar*ybar^T. Exact common/contrast:
S+ + S-=2K0 N, Var=4K0² nu;
E[S+-S-]=2lambda Delta m_q;
Var(S+-S-)=4Delta²[lambda*b_q+(nu-lambda)*m_q²];
Cov(S++S-,S+-S-)=4nu*K0*Delta*m_q.
Offdiag = -lambda*v+nu*(K0²-Delta² m_q²).
For fixed N, nu=0 gives negative offdiag. For *hypothetical* Poisson N, nu=lambda yields lambda*(K0²-Delta² b_q), positive at frozen 330MeV since K0²>Delta², with no physical Poisson claim.

Count moment admissibility: if lambda=k+p with integer k=floor(lambda), 0<=p<1, (N-k)(N-k-1)>=0 for integer N implies nu>=p(1-p). Reject lambda=.5,nu=0 as impossible. This is a necessary consistency check, not a full inferred stochastic law.

External sources: original IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4 blob c49433293921dbb012d7f1b0387745732a598efa documents two-arm TOF coincidence and four angular DA data at 330MeV, but not acceptance/normalization/polarization numerical calibration or measured total SIG at 330MeV. Arends 1976 doi:10.1016/0370-2693(76)90671-7 and Silverman 1984 doi:10.1103/PhysRevC.29.35 full original methods are not source-locked; Silverman 376MeV deuteron beam is not at 330MeV photon equivalent s. No sextic donor numeric variance imported.

Illustrative NOT-MEASURED q envelope delta=5% gives r=21/19, eta=.05. For L=1/700: |m_q|<=0.03176248, mean offset<=1.95761046MeV, selected mark variance in [986.482704593,1532.895489268]MeV². See machine-readable RESULTS.json for all three L.

Verified this run: Python 20/20 methods normal and python -O, Boost C++20 independent rational 1089 cases, Wolfram 7 exact zero/True, two plots visually read. Independent R6/C9 distinct author NOT_RUN. No previous IVP/full suite/4501 LP rerun; no physical event SIG, gamma photon history, D_fast thermalization, heat or Cv. kappa=null,R_event=null,heat_rate=null,physical_activation=false,L4=false,production=HOLD.