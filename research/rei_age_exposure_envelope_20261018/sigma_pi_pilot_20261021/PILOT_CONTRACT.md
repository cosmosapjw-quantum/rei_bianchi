# SIGMA_PI_PILOT_20261021 — Astra execution contract v1
Date: 2026-10-21 (Asia/Seoul). User objective: first same-day non-tilted Bianchi I (Sigma,Pi) preliminary plots, with reusable code and cooperative NCP64/128GB execution; no benchmark campaign.
Publication parent: rei_bianchi PR199 branch research/rei-age-exposure-envelope-20261018, expected HEAD964b2e3c098f6e475999a4eddc7a6aa0f8f053cc. New owned path: research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/. Existing native age/time outputs and all other lanes preserved.
Scientific executor separation: root Astra owns this contract and decisions; lower-tier implements and executes bounded commands; independent Astra reviews contract before science and diff before result admission. Observed runtime model identity is not independently established merely by requested profile.

## R1–R5: model and explicit parameter slice
Reuse exact PR147 3b85dedce84d37b3e165da00685a8a984950aafe / PR145 canonical FV source, no rewrite of its physical RHS. This first pilot is the axisymmetric LRS subset of non-tilted Bianchi I, self-consistent Einstein + collisionless gamma/nu L8 and canonical massive Vlasov cells plus cold dust + Lambda. It is a new family of that model, not the PR199 native thermochemical age/time campaign.
metric(-,+,+,+), ds²=-c²dt²+a²exp(-2b)(dx²+dy²)+a²exp(4b)dz²; s=dot b, sigma=diag(-s,-s,2s). Stress coefficient pi_s=(Pparallel-Pperp)/3 and pi=diag(-pi_s,-pi_s,2pi_s).
Public tensor norm for this pilot is Frobenius: Sigma_F=sqrt(sigma_ab sigma^ab)/H=sqrt(6)|s|/H. Existing model Sigma_half=sqrt(3)|s|/H=Sigma_F/sqrt(2); output BOTH and the sign s.
SI pi in J/m³ and H in s^-1: kappa_t=8piG/c²=c² kappa_E, with kappa_E=8piG/c⁴. Pi_F=kappa_t sqrt(pi_ab pi^ab)/H²=sqrt(6)kappa_t|sum_A pi_s,A|/H². Output signed Pi_F_signed and per-species signed contributions. This c² is mandatory for the user's dimensionless Pi when Einstein kappa_E is used.
Trace, norms and contraction: Trsigma=Trpi=0; sigmasigma=6s²; pipi=6pi_s²; sigmapi=6s pi_s (Wolfram evaluator checked; undefined-H symbolic warning only).
Equations: H²=kappa_t rho/3+Lambda c²/3+s²; dot s+3Hs=kappa_t pi_s; dot rho+3H(rho+pbar)+6s pi_s=0; dot H=-kappa_t(rho+pbar)/2-3s², with Lambda excluded from rho+pbar.
Use the exact source lock's cosmology and clock ONLY. Historical lock fields describing stress-free q_ref prescriptions are not the active model; the reused PR145/147 physical RHS is the active model. ai=1/21,af=1/5,b_i=0,elapsed proper time zero. Massive fraction=.1, m/Tref=30, isotropic massive A=0,24x12cells, positiveGauss3; cold dust fraction reduced correspondingly. gamma/nu energy and number hierarchies separately, ne_source=None and no Thomson donor.
Physical initial gamma and nu have common W=1+k P2(mu), |k|<=.5; E2=N2=k/5. Pi_i source allocation is therefore fixed common radiation anisotropy with initially isotropic massive species, not arbitrary matter stress.
At fixed Sigma_F,i: H_i²=Href²/(1-Sigma_F,i²/6). pi_s,rad,i=rhoCrit0 Omega_r k/(15 ai⁴).
Thus k=5 ai⁴ H_i² Pi_F,signed,i/(sqrt(6)H0² Omega_r). Record analytic calibration and actual initialized Sigma/Pi. Do not relabel k as Pi.
Sigma_F,i grid=[0,0.0003,0.001,0.003,0.01,0.03,0.1].
Pi_F,i magnitude grid=[0,0.00001,0.00003,0.0001,0.0003,0.0006,0.001].
Keep shear orientation +1 at positive Sigma,0 atzero. Use stress sign +1 and-1 for nonzero Pi, deduplicate Pi0. Total91 distinct IVPs. The sign of pi_s relative to s is an additional sheet, stored explicitly; norms alone do not define IC. At Sigma0 relative alignment undefined, retain absolute axisstresssign.
New work has no strong no-go claim. Existing PR199 HOLD and PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED are unchanged.

## C1–C5: implementation boundary
All implementation under pilot_20261021/package/ locally, mapped to new owned repo path. No clone/worktree, owner checkout modification, root Rust/.github change, or old campaign run.
Vendor exact minimal3 Python modules + exactSourceLock + MIT license, preserving original SHA map. New adapter caches source parse and immutable legendre matrices per worker keyed by full args, and reuses fixed canonical momentum packets. Do not change mathematical RHS, summation order, solver or tolerances. Any broad vectorized RHS rewrite is deferred; existing NumPy packet arithmetic already vectorized.
Persistent independent-case process execution, spawn importable module, BLAS/OMP/MKL/NumExpr1 before NumPy import. Cache setup only; no benchmark or64core speedup claim.
CLI: plan, run (--profile sandbox|ncp --max-workers optional --resume), plot, check. Exact input+source hash creates case identity; completed matching cases reused, mismatched metadata returned explicitly. Write each result atomically with rawstate samples, actual config, numevals, exit and elapsed; preserve failures and incomplete attempts, no silent rerun.
Use JSON manifest/endpoints CSV and percase compressed NumPy/raw JSON as appropriate. At least one standalone PNG and PDF + full finitegrid data; show both stresssigns and actual norm units, source-free LRS pilot label, epochs and N of cases. No interpolation masked as extra samples; plot failed cells as failed/empty.

## Minimal meaningful validation (not benchmarking)
Independent reviewer must admit contract before new trajectories.
Reuse existing kernel tests/convergence receipts for unmodified code, not rerun full suites.
New adapter mechanical tests: norm/calibration on0 andcorner; invalid amplitude; cache returns same bitwise matrix and immutable; deterministic case ids; resume mismatch; bounded resource allocation underbusy CPU/memory; no owner process kills.
Scope checks all91: finite sol; reached exact a_end; expected121 epochs; positive H, canonical populations nonnegative; original gamma/nu number tolerance5e-11; initialSigma/Pi absolute mismatch<=5e-12; physical energypositive; report normalized Hamiltonian construction residual as consistency only. Check gamma/nu reconstructed brightness at64Gauss nodes>=-1e-10 (sample check not global theorem). Keep solver rtol3e-11,atol3e-13,methodDOP853.
New domain guard: only three extra corner reruns with L12,48x24Gauss3 at (Sigma,PiSigned)=(.1,+.001),(.1,-.001),(0,+.001); compare nominal saved endpoints. Gate for preliminary numerical stability: max absolute differences of Sigma_F,Pi_F_signed,b <=2e-6 and H relative<=2e-6. Record actual values; fail gates preserve data/preliminary unadmitted. No extrapolated global error bound. Isotropic gridcase checks |Sigma_F|,|Pi_F_signed|<5e-12 across trajectory; it is part of91, not duplicate.
One preproduction review of contract and one diff/result check by same independent reviewer, at most targeted repairs for concrete defects. No recursive reviewers.

## Resource/compute allowance for this NEW pilot only
Local sandbox: at most4workers and actual affinity/cgroup limit, child cumulative wall<=240s, totalcontroller elapsed<=180s, each case<=30s, fixed91+3 scientificIVPs max (no automaticretries); targeted tests<=30s. Overhead measured separately; no oldbudget reset. If sandbox limit ends, persist completed and NCP can resume remaining. Only new admissible case set; don't redo oldcompletedage/time or PR147fourIC.
NCP opt-in same code: up to63single-threadworkers on64effectiveCPUs; actual affinity/quota wins; reserve16GiB memory on128GBhost, budget0.5GiB/worker with measuredRSS reported; on smallerhosts keep at least max(1GiB,10%)reserve. Per-case60s, cumulativechild1800s,controller1200s. No new paid instance, reconfiguration or package purchase.
Busy server is not a blocker: use available CPU/memory, nice10, boundedlaunch, dynamic slots from CPUidle samples and memoryheadroom; never kill, renice or pause unrelated jobs. If CPUbusy but memory allows, allowone nice worker; for no memoryheadroom wait bounded intervals and preserve pending state, not an owner-session STOP. Respect ownprocess locks only for duplicate case writes; no exclusivehostlock.
This session actual DCdevice listedonline; fresh start_process was rejected by monthly usagecap beforeSSH; no reconnect/retry. NCP actual state is NOT_OBSERVED. Provide copyableCodexprompt using ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p22; usermanualfilehandlingnotneeded.
Publication after review: actual currenthead re-read; build commit with actualparent, update_ref expected_sha and forcefalse; PR199 staysdraft, no merge. Dual backup create-only compactpilotbundle; providerACKs and small readbacks. Source/resultpackage contains manifest+plots+rawcaseoutputs; deliveryreceipt separate to avoid recursive selfhash.

## Interpretation and finish
Deliver actualfinitegridplots if localboundedrunfinishes; otherwise partialplotswithpendingcellsandreadyNCPresume. No claim nativeHHe ionization/temperature/CMBangularobservations or fullygeneralnonLRS background. Next handoff clearly states model slice, normconversion, admissible scope, actualcompletion and pendingactions. Actual freshness coverage: REI253branches/211PRs,VigilODE182branches/78PRs/25runs; Drive141,Dropbox38+40; targetedconversationsearchsuccess. Detailed files only selectedrelevant lanes; no all-chat/all-branch-byte claim.

