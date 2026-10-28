# Frozen contract: REI_UVB_SHAPE_INNOVATION_20261028
Status READY_FOR_LOWER_TIER_IMPLEMENTATION; authority sources28, requested Astra; runtime identity unobserved. No science execution by this author.

## Frozen inputs / paths
Source repo cosmosapjw-quantum/rei_bianchi, immutable c5ab42c8673db614e7fb16695ad071c65becb81b, research/rei_physical_fast_20261028.
- sources/BECKER_BOLTON_2013.json Git blob61c1ecdcb1be05d47bb59165fb4cac8bb14deb52; SHA256893f97497b9aae41f545b17278082602a06b352c86bdeb1db2d9afb5c1c83de4.
- outputs/CALIBRATION_RESULT.json Git blobabd45812fb38691bcc76b5bddd33c55e2e5e4be3; SHA2568ba2652bcf7358319bbdfc83b499a566890fcf6b449fe12ee759a29a6fcfcc7f.
Local exact copies are authority/rei/inputs/. Saved d,m,z must equal observation coordinates/values; m is reused, not recomputed from rate tables.
No source imports. One new subtree only: research/orchestration_expansion_20261028/rei_uvb_shape_innovation/. Root may stage this subtree onto its existing integration checkout, preserving owner lanes. No clone/worktree/merge.

## Claim and derivation
Use statistical covariance C in dex², already divided100. d,m in log10(Gamma_HI/(1e-12 s^-1)) dex; r=d-m; z=[2.4,2.8,3.2,3.6,4,4.4,4.75]. EOS fixedtheta0; no new nuisance profile or missing uncertainty filled.

Let D be6x7 adjacent differences D[j,j]=-1,D[j,j+1]=1. Delta=D r, S=D C D^T. S is SPD because C is SPD and D fullrowrank. Delta gives observed minus template log10 adjacent rate ratios, in dex. Save Dd,Dm,Delta, S, diag standard deviations, 10^Delta multiplicative ratio discrepancy. These six marginal z-scores are correlated and must not be summed as independent chi-square.
Normalization invariance: D1=0, so common shifts of d or m leave Delta unchanged.
Q=Delta^T S^-1 Delta equals the existing amplitude-profiled chi². Proof: D has nullspace span1; minimizing (r-beta1)^T C^-1(r-beta1) is the covariance-induced quotient norm on this nullspace, equivalently the fullrank contrast quadratic. Use Cholesky solves; do not form inverse for production.

New leave-one-out diagnostic for each i:
J=all indices excepti; B=C[J,J]; c=C[J,i]; rJ=r[J]; u=ones6.
t=B^-1u, h=B^-1rJ, g=B^-1c; den=u^Tt.
beta_minus=(u^Th)/den; sigma_beta_minus²=1/den.
a=1-c^Tt; s0=Cii-c^Tg>0.
e=r_i-c^Th-a*beta_minus.
s=s0+a²/den>0; Z=e/sqrt(s).
Conditional predicted residual r_i_pred=c^Th+a*beta_minus.
deleted_chi²=(rJ-beta_minus*u)^T B^-1(rJ-beta_minus*u).
Exact block factorization identities:
Q-deleted_chi²=e²/s,
beta_full-beta_minus=a*e/(den*s0+a²).
Derivation: full objective is deleted_chi²+den*(beta-beta_minus)²+[e-a*(beta-beta_minus)]²/s0; completing its square gives both identities.
Save all7 e,s,Z,beta_minus, beta_full-beta_minus, deleted_chi² and e²/s, with z labels.
These seven Z are mutually dependent diagnostic innovations; their sum of squares is NOT Q. It is not independent held-out validation because the fixed template was selected on the full data. No point may be removed or C changed based on this diagnostic.

Optional exact fixed-null chi-square6 survival diagnostic is mandatory simple scalar:
p=exp(-Q/2)*(1+Q/2+(Q/2)^2/2).
Assumes Gaussian statistical C, fixed template and fixedEOS; no parameter selection correction, no Jeans/systematic covariance. Predeclared descriptive flag p<0.01 => CONDITIONAL_STATISTICAL_SHAPE_TENSION; otherwise NO_1PCT_SHAPE_FLAG. Either result yields scoped diagnostic completion, never physical F4 PASS/FAIL. Do not assign chi-square6 p to the EOS-box minimum.

## Numerical acceptance and independent reference
One new bounded suite (single process, standard library) computes production binary64 Cholesky and a separately implemented Decimal precision60 Gauss elimination reference on exact represented binary64 values via Decimal.from_float. No NumPy/SciPy/old source import, no original9tests rerun.
tol=1e-10 relative +1e-12 absolute for normalized quantities Q,Z²,deltaChi²,beta in dex and contrast values; variance relative1e-10+1e-15dex². Explicit residual quadratics are primary, subtraction used as cross-check. All relevant SPD pivots strictlypositive; domain7points/noNaN; STOP if not.
Required checks: actual Q matches saved19.381736839571925 under tolerance; sixcontrastQ matches full GLS and Decimal; all7 block identities and fullbeta shifts; nonnegative deletion reductions up to tolerance without clamping raw values; shift invariance r+0.125*1 and m+0.25*1; diagonal syntheticC reduces to independently derived weighted mean predictive variance; correlated actual/synthetic distinguishes c=0 approximation; common joint permutation of C,r yields same Q and matching labeled leave-one-out outputs; rank-deficient/nonsymmetricC rejection, incorrectdimensions rejection. Use one synthetic correlated3point fixture C=[[2,1,0],[1,2,1],[0,1,2]] (arbitrarydex²), r=[0,1,-1] to test nonzero cross-correlation terms. No random draws or bootstrap.

## Commands / outputs / limits
Coder implements shape_innovation.py and suite.py plus bounded runner in newsubtree, and docs reporting observed facts. Root releases exact command after static readiness:
python <newsubtree>/run_bounded.py --cpu-limit 10 --wall-limit 30 -- <python> <newsubtree>/suite.py --inputs <authority/rei/inputs> --output <newsubtree>/outputs/attempt001
Use actual sys.executable for nested python; no shell interpreter expansion. Runner singlethread1worker memory<=512MiB, childCPUhard10s, wall30s. Predicted total scienceCPU<1s; fresh maximum10CPU plus root-recorded nonzero wrapper/tail reserve. Ledger is the new orchestration unit, not remainder transfer from owner main606.634374/presentation63.924256494/planning20.819461885. If root charges same cumulative REI ledger, reserve<=10+1 gives617.634374<fresh620cap; restore600 retainingdebit. No IVP/rate/CAS/plot/network in science process. One initial run; no automaticretry. A substantivefailure returns to authority; at most one specificallyauthorized targetedrepair, no campaignrestart.
Outputs: RESULT.json, ADJACENT_CONTRASTS.csv, LEAVE_ONE_OUT.csv, covariance JSON, TEST_RESULT.json, raw stdout/stderr and measured receipt. No new plot required.
PASS -> fresh nonauthor Astra reads theory/code/rawoutcomes -> scoped acceptance -> root publication/dualbackup and handoff. Missing independentreview preserves safe prepared artifacts but scientificadmission pending. Stop after this unit; no new forward solve.
