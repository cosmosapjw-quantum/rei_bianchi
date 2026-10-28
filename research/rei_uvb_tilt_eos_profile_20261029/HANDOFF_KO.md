# REI_UVB_TILT_EOS_PROFILE_20261029 · 다음 기존 연구 스레드 handoff

$physmath-research-loop

PROJECT=cosmosapjw-quantum/rei_bianchi
UNIT=REI_UVB_TILT_EOS_PROFILE_20261029
BRANCH=research/rei-uvb-tilt-eos-profile-20261029
PR=253 (Draft/Open/Unmerged)
PARENT_F=eecd9b2c1c95f9319c1da41951b814855b0feb11
CONTRACT_S0=042f8ef390a5ce5fefac5a01c5d29c5e15ae0523
THEORY_ST=f7bfb0320202e8b4731f97d0b3680fde66043fa8
SCIENCE_S1=912dcaa111962d1ba550c42e1c262e6c85acee0d
FINAL_F=READ_LATEST_BRANCH_CONTAINING_COMMIT
CENTRAL_LAST_OBSERVED=4824eec8526185b6b866a5e7e0dabdc624b5543c
ORIGINAL_CANONICAL_DAG=28/88,delta0
WORKING_REI=33/88_SEPARATE
WORK_OUTPUTS=18/20
HELD=R6,C9_Distinct_Author_NOT_RUN
C8_RESOURCE=CONCERN_PLOT_CPU_OVERRUN
AUTO_NEXT_NODE=false

PINNED SOURCE:
BB13(2013) Table1 gamma_TDR v, Table2 correlated C/100 in input/BB13.json. Original saved Puchwein2019 template and prior amplitude-only result in input/CALIBRATION_RESULT.json; prior single tilt result in input/ONE_TILT_RESULT.json. The full source ZIP carries original bytes, frozen input hashes, theory, run_once, meter, tests, Decimal reference, results/logs, and two figures. No old IVP, 17-state histories, original fit or source rates were rerun.

THEORY:
r(theta)=d-m+theta*v, theta=(gamma_TDR-1.4)/0.2 in [-1,1], x=z-3.6, X=[1,x]. beta(theta)=-0.04591874303144477+0.07822682984779859 theta dex. kappa(theta)=0.06866173948059068-0.009302630273776263 theta dex/redshift. Q2(theta)=11.347835208970784-1.6985030665884824 theta+0.06771443624148252 theta^2. theta_star=1; unconstrained mathematical theta=12.541661430446666 is out of box. At theta1 gamma=1.6: beta=.032308086816353825,kappa=.05935910920681441,Q2=9.717046578623782/5,amplitude-only Q0=15.721474783438495/6, DeltaQ=6.0044282048147135. Kappa box [.05935910920681441,.07796436975436694]; conditional statistical sigma_kappa=.0242243173193387. EOS/x collinearity after amplitude=-.8278414328672586. Not a physical UVB detection or Bianchi velocity tilt.

EVIDENCE:
Actual one science child32 unit methods PASS, 21 Decimal80/source checks PASS, exit0, CPU.118925s/wall.123564799s under8CPU/25wall. Wolfram six algebraic residual families=0; not independent author. Two figures generated once and inspected. Figure CPU7.04user+1.53system=8.57>frozen8CPU (RESOURCE_CONCERN), wall8.15<25wall. Do not erase this overrun or claim fully budget compliant; science child remains within budget. Other network/model/metadata cost UNKNOWN_NOT_ZERO. Prior main budgets CLOSED_NONTRANSFERABLE.

ARCHIVES:
S0 ZIP bytes6330, SHA782e74eff0efdfd280b280da4cdcd68493e9d0d07f45e3f4cefb8f1b296935f7: Git/Dropbox SUCCESS, S0 Drive upload safety check BLOCKED. S0 source payloads were later included in dual-backed ST/S1, but original S0 upload is not retroactively marked successful.
ST ZIP bytes10022, SHA3f0750fefa96500a1939876d7b6f7c5d40f63df87b74f0c69e0e089bd78a1a97: Drive1AsURPBLw8OQ9PZi_ODLI4XW-zCcGaZRJ, Dropbox id:BSpOijBcT10AAAAAAEGpRQ, rev65ee850e921260af03d47; both completed and size matched.
SOURCE ZIP bytes246574, members34, SHA db2cf1726d9e2f233ffcda334616018a847bbd4c8fbad62b21a33cc68e7bb541: Drive1POtDmDstQN6plSSlixGIqef6z_JQSdC6; Dropbox id:BSpOijBcT10AAAAAAEGpRw rev65ee8686980290af03d47; both actual completed and separate size matched. Local CRC and payload SHA PASS; remote whole-byte SHA NOT_RUN. Do not regenerate immutable archive for later ACK.

Git published the exact executed blobs of profile.py/reference_decimal.py/run_once.py/plot_saved.py/test_profile.py; meter.py Git blob action was blocked by service safety checks, but its original bytes remain in SOURCE ZIP. Git projection is not the entire ZIP.

NEXT:
1. Read actual final F Git commit, FINAL_ACK.json, stage ledger and scoped source ZIP. Re-check current HEAD/AGENTS/parallel owner PRs.
2. Conduct **one genuine distinct-author** R6/C9 review on saved inputs, EOS sign/box, statistical covariance, numeric tests and C8 resource finding. Same-author review, Decimal80 or CAS is not independent authority.
3. Do NOT silently add EOS prior/Jeans covariance, refit template, delete points, claim physical F4, merge, change central or launch another node. Future physically justified UVB source history needs its own actual sources and fresh bounded allocation.

Physical F4=PARTIAL, L4=false, physical_radii/global_completion=null. H-Li 26 ground+5 nuclear extras and102 formal requests are NOT active rate coverage; original REI ON_refined17 state remains unchanged.
