# OBSERVER15 R8: selected finite-source cubic reference and recovered R7 variants

2026-10-14 KST. Selected R8 only, resumed after interruption. Decision: **ACCEPT_SCOPED_FINITE_GL32_CUBIC_REFERENCE**. No R9/R10, source ODE, inherited residual campaign, native receiver or HPC run. Existing production, CR/RCT/HH OFF, global DAG and BASS prelaunch history remain unchanged.

## Complete preserved payload

Full Korean report, decision, machine-readable consumer selection, source map, new validation/CAS records, and BOTH complete immutable R7 archives:

- `REI_OBSERVER15_R8_20261014_SOURCE.zip`, **581699 bytes**,44members/43manifest payloads.
- SHA256 **f6f27bb37ccc1cdd85de2f3df95242f3fd7e18496ff091e95dadb3022da13099**.
- [Full archive on Drive](https://drive.google.com/file/d/1bSgTnnGc91TNxwdB21D_0hr4cY2mv96D/view?usp=drivesdk).
- Drive ID1bSgTnnGc91TNxwdB21D_0hr4cY2mv96D, existing parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Actual create-only upload and ID/name/size/parent readback matched.
- Local CRC, all43payload hashes, nested archive CRC/font absence and a relocated read-only verifier passed. New R8 remote full restore and Dropbox upload were not performed.

This Git document is the substantive decision and restore entrypoint; full programs, inputs and evidence remain in the immutable archive. Download by exact ID/hash, not filename alone. Read REPORT_KO.md, DECISION.json, CONSUMER_SELECTION.json, then HANDOFF_KO.md.

## 1. Recover and distinguish two actual R7 archives

The direct conversation predecessor R7-A is276880bytes, SHA256`10b74244bc9dd56f7043861ae5a492c5b7ec8d3d232e487f092d729c7657e26a`, Drive`1aF9HQVkfR6zpGCRuer0xN3AT3T07-eUp`. Its interrupted-operation Drive upload was already complete and was not repeated.

The live PR115 head additionally contained R7-B at commit`8bf8e3c18d607334614cfea734f9b10961fbd4d4`:236530bytes, SHA256`3524a7e6b5211c268222bd6ef1af108e35d23ff23330fb116c741afdcff70eaa`, Drive`1_y0StgG8NmfFnfKf0YD-r2sxfCv3Wm1v`. The R7_B entrypoint is preserved unchanged. These are distinct payloads with the same filename.

Both complete Drive archives were actually restored, hashed and CRC/manifest checked:67A payloads,48B payloads. Raw fetch used the same generic container mount name; B was copied to a hash-specific name and A restored from its own ID. No cloud original was overwritten. Both complete originals are in R8 inputs/R7_10b74244bc9d.zip and inputs/R7_3524a7e6b521.zip.

Four original source files are byte-identical across A/B:

- SHEAR12_source.py SHA25650d2bbd8d6dd4c3a60c34644297041adb5a55ba0ab03bf8f96978a8e819456ba.
- SHEAR12_CONTRACT.json SHA256e5e36ce5dab3b43198353bf596b56c22a0a54069570113f9f9db0443f34e8a91.
- SHEAR12_RESPONSE_HISTORY.csv SHA25669bceac64e356d202c4cc4cb8c3db35d9e37c632df7d37bc6219f7c53a696927.
- SHEAR12_REPORT_KO.md SHA256cbf01e9005320dd2a29bce69758cc3009f61d1622eaa5a08bd465ee4681bcf20.

Actual definitions agree on exact-decimal epsilon0, normalized mathematical GL32 initial measure, expansion, cross sections and observer boundaries. This is semantic TARGET identity, not identity of the two error-norm implementations or historical binary64 spectral arrays. A uses weighted gas norm |dh|+2|dz|+|dv|; B uses gas l1 with a separate electron-functional factor. Historical internal quadrature bytes remain un-restored; continuous-energy error is not certified.

## 2. Selected return and preserved alternatives

Choose the inherited **R7-A certified cubic** as the default mathematical reference for this same finite source, because its continuous residual certificate is attached to the actual consumed reconstruction. Keep PL as a compatibility path, and retain R7-B as a distinct certified alternative. Do not claim an actual PL-native result is cubic, and do not add PL interpolation error again to the cubic certificate.

Signature(-+++), u=t/t_star, H*t_star=1/25, Y=2/25, initial(h,z,v)=(9/10,19/250,1/250), initial photons7/10/H, q in[65,110]eV. Same source-free pure photoabsorption GL32 baseline; c and physical sigma units retained.

Observeru=.5, near.25, far.20. Exact baseline redshift labels exp(.01)-1 and exp(.012)-1. Input reaches the actual fixture observer, so missing fixture tail0. An unrelated physical continuation remains unspecified.

    n=Cnear=integral_.25^.5 .4 exp(-.12u) xi_e du,
    b=Cbin=integral_.20^.25 .4 exp(-.12u) xi_e du,
    P(r)=exp(-r n)*(1-exp(-r b)), r=sigma_T/sigma_star>=0.

C is dimensionless relative to sigma_star; C/sigma_star is the SI electron column. Apply a passive sigma once before the nonlinear probability.

Inherited R7-A outward short displays:

    b in[.0020451235739618286,.0020451235739637115],
    n in[.0101109764426899827,.0101109764427051460],
    P(r1,tail0) in[.0020224807481693721,.0020224807481712630].

Actual exact-Fraction comparisons show these columns and probability lie inside R7-B and the retained PL enclosures. B/A probability width ratio is4.117422496707386869..., while PL/A is the previously reported1.870067e6. These are enclosure-width ratios, not measured solution-error or speedup factors. This R8 does not rerun those source certificates or manufacture independent scientific review.

## 3. New stage-local bound for all passive r

For n in[nlo,nhi], b in[blo,bhi], nlo>0,blo>=0:

    L(r)=exp(-r*nhi)*(1-exp(-r*blo)),
    U(r)=exp(-r*nlo)*(1-exp(-r*bhi)).

Let dn=nhi-nlo, db=bhi-blo. The derivatives obey

    |P_n|=r exp(-rn)(1-exp(-rb)) <= r^2*bhi*exp(-r*nlo),
    P_b <= r exp(-r*(nlo+blo)).

The maxima of r^2exp(-nr) and r exp(-cr) occur at2/n and1/c, giving4/(e^2n^2) and1/(ec). Integrating across the column box yields the uniform absolute-width bound

    U(r)-L(r) <= 4*bhi*dn/(e^2*nlo^2)+db/(e*(nlo+blo)).

Evaluate conservatively with the exact positive rational e_lower=sum_(k=0)^16 1/k!<e and outward Decimal conversion:

    sup_(r>=0)(U-L) <= 2.21189644208073687935538684180e-13.

A known common nonnegative foreground multiplies this bound by exp(-tail). This excludes unknown foreground uncertainty and is an absolute, not relative, error statement. Required native tolerance remains null, not newly chosen. r=0 gives P=0; the r1 inherited width is much smaller.

For ACTIVE source changes n=n(r),b=b(r), there are additional exact chain terms -r*n'(r)*P+r*b'(r)*exp(-r(n+b)). The passive certificate cannot silently absorb changed reaction rates or source histories.

## 4. Current cross-repo consumer selection

Read NEW HE46 full R1_RESULT at d9a60904225f90d0e139c9b220dbd583413ccb51. Actual warm P01_EVENT_BRIDGE02_17_NODE_0_1e11s uses FT03/HM12 CaseA, fHe3/38, ongoing photon forcing and temperature feedback, not the source-free SHEAR12 model. Its stored-PL arithmetic is not a true-IVP bound. Keep HE17 R2 as the owner of same-warm-source dense/signed-residual intake; no SHEAR12 numerical constants/radii are transplanted.

For a Bianchi-I chart x0=ct and vol=a1a2a3, Jproper=(c ne,0,0,0) and Jcomoving=(c Ncom/vol,0,0,0) agree only with Ncom=vol*ne. Dividing already-proper ne by vol again produces a spurious dilution. Actual xAct checked these current views, their covariant divergences, normalized-clock factor t_star, and separate spatial-current correction. This is a new discriminator, not an asserted upstream native bug.

The current6-repo query also returned CR57 smooth-front/right-limit closure, HH63 newly completed finite Coulomb rate certificate and REI116 microphysicsR8. These were read at metadata level only; no new numerical input imported. CR57 closure is conditional, HH rate change is active chemistry, and REI116 is a different R8 unit. Earlier actual CR56/HE45 source reads, BASS observer-cap and REC provenance remain recorded. No external repo mutation.

## 5. Actual checks, limitation and next stage

New39named selection/source/arithmetic checks passed. Nine r samples at mpmath100 are supplementary, not proof of the all-r bound. Original R7 producers were not imported or run.

Cloud Wolfram15.0.1 returned13scalar zero groups and an e_lower numerical sanity True. The first scalar call failed JSON serialization of an unevaluated GreaterEqual and emitted p/r-limit warnings; no individual zeros were admitted from that failed export. Replacing that leaf by derivative/origin identities and using the Taylor coefficient resolved the representation problem; failed input/output retained.

Actual cloud xAct/xTensor1.3.0/xCoba0.8.6 returned6new CTensor/covariant-derivative zeros. xPerm connected. xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Inputs were saved before calls; observed outputs are normalized records, not raw connector transport bytes.

Same author plus distinct arithmetic/CAS paths; external independent scientific review/native subagents NOT_RUN. No source ODE, R7 residual replay, production/native/HPC, main merge or force push. CR/RCT/HH OFF and all original global owners retained.

**Next selected stage R9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT.** Bind the chosen finite-source oracle to the actual consumer representation/clock/observer contract. Keep PL/cubic outputs distinct. No new source or full model calibration is needed merely to use the present finite reference; different physical source inputs require their own error evidence. Read the exact machine-readable selection and handoff in the archived payload. R9/R10 remain unexecuted.
