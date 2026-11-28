# BASS_HE next-thread handoff: HE_DD_ANGULAR_MOMENT_20261029

\`\`\`text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=108
PARENT_HEAD=e1587adb8fc515384014dd0838b93e5961308bfd
BRANCH=research/he-dd-angular-moment-envelope-20261029
HEAD=READ_CURRENT_REMOTE_PR_AND_BRANCH_HEAD
ROOT=research/he_dd_angular_moment_20261029
READ=ROOT/THEORY_KO.md;ROOT/REPORT_KO.md;ROOT/IMPLEMENTATION_CONTRACT.json;ROOT/RESULTS.json;ROOT/STAGE_LEDGER.json;ROOT/DELIVERY_RECEIPT.md;ROOT/SURVEY.json

SOURCE=IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4
SOURCE_GIT_BLOB=c49433293921dbb012d7f1b0387745732a598efa
SOURCE_SHA256_PRIOR=b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f

CENTRAL_DAG=28/88
HE_DAG=14/18
PR105_DAG=2/2
PR106_DAG=1/2
RECIPROCITY_DAG=1/2
BIRTH_LEDGER_DAG=1/2
ANGULAR_MOMENT_DAG=1/2_SCOPED_CONDITIONAL
CURRENT_THEORY_STAGES=9/10
CURRENT_CODING_STAGES=9/10
R6_C9_DISTINCT_AUTHOR=NOT_RUN
CHECKPOINT_ACKS=20/20_GIT_AND_DRIVE_AND_DROPBOX
PHYSICAL_DELTA=0
KAPPA=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD

THEORY:
  For 330 MeV gamma+He4->dd in target rest frame,
  PR105 EXFOR DA=[0.14,0.16,0.07,0.19] nb/sr
  at theta=[46,61,73,87] degrees, ERR-S statistical.
  Assume nonnegative exchange-symmetric f(theta) and
  externally declared L>=1/700 nb/(sr degree).
  b=int_0^(pi/2) f(theta)cos²theta sin(theta)dtheta
    /int_0^(pi/2) f(theta)sin(theta)dtheta.
  Signed-kernel pointwise upper/lower f± envelopes yield VALID
  OUTER bounds, not sharp: b(L=1/700) ~ [0.279238681235,0.386397436244].
  L=1/200 ~ [0.186315404014,0.472747698143].
  L=1/100 ~ [0.133108297140,0.573194162276].
  b(f±) provide feasible inner witnesses.
  Var(K_D)=Delta² b, Delta²(330)=3798.60144551708985 MeV².
  Global kappa cancels in ratio; angular detector acceptance DOES NOT.
  Numerical endpoints NOT outward-certified, boxes NOT joint CI.

STOPPING:
  If h(K) from named actual material/time-window stopping provider
  is twice differentiable and |h''|<=H [MeV^-1], then
  |E[h(K+)+h(K-)]-2h(K0)|<=H Delta² b_upper.
  Manufactured h(K)=K²/Kstar is a COUNTEREXAMPLE/UNIT TEST,
  not a physical heat source. Need real photon history, target
  frame, rho_He, stopping/redistribution/secondaries/Cv.

TESTS:
  New only: Python3.13.5 unittest 21/21 PASS;
  C++20 32768-point independent Simpson 3x2 roots max
  difference 8.27512419698806e-10;
  SciPy 8 analytic quadrature comparisons <2e-12;
  Wolfram 4 exact zero identities.
  Source/test/theory Git blobs verified against local.
  R6/C9 distinct-author native subagent NOT_RUN.
  Old IVP / full suite / completed campaigns NOT_RUN.
  Numerical outward-rounded rigorous certificates NOT_RUN.

NEXT:
  1. Source-lock original Arends 1976 & Silverman 1984
     detector efficiency, angular acceptance, coincidence event/particle
     counting and beam polarization, plus matched-s inverse DA.
  2. Obtain actual E_gamma~330MeV total exclusive event sigma and
     phase-space n_gamma(E,n,t), He target distribution with frame/clock.
  3. Obtain named nonthermal D_fast stopping/redistribution + heat/Cv
     with controlled derivatives or actual transport.
  4. Only if physically sourced evaluate conditional deposition bound.
  5. For rigorous plotted numeric interval claims, use outward-rounded
     interval trig/root isolation. Never substitute precision for proof.

Do NOT re-run complete IVPs/science suite without changed dependencies.
Preserve original EXFOR bytes; no force-push/merge/production.
Log every stage's actual Git SHA and Drive/Dropbox ACK and DAG numbers;
never borrow prior unit's ACK as a current binary ZIP backup.
\`\`\`
