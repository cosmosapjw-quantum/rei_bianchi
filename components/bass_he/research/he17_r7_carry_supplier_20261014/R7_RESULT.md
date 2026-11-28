# HE17 R7: carried-error discriminator and live AXBI supplier

2026-10-14 Asia/Seoul. Selected R7 from PR51 `16a990556ea72f87246b3bb0ae5a14fbbb650497`. R8-R10 remain unexecuted. This result partitions the SAME certified first cell, not the next stored source cell or the full16-cell history.

## Same-reference numerical result

The attached fixed Hermite input remains SHA256 `7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be`, source P01 NPZ `3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`, receiver `a5c958c414dea41216b445c05f58df837f05cacb`. Warm FT03/HM12 CaseA, prescribed normal-comoving Bianchi I, CR/RCT/HH OFF, exact dyadic inputs and decimal source constants unchanged. Signature(-+++), x0=ct, proper seconds, c/kB/hbar retained.

Use the existing whole-cell A,B,C and stored residual coefficient intervals. No new source RHS, atomic function, ODE or interval source-jet evaluation. Let h=6250000000s,u=t/h,a=hA,K=h^2BC and m=hB*incoming_photon_error. On a subinterval[alpha,beta],delta=beta-alpha:

    P=delta*a+delta^2*K/2,
    D=(I-P)^-1[eg+delta*m+dg+dN],
    dg=integral_alpha^beta |S^-1 Rg|du,
    dN=hB integral_alpha^beta(beta-u)|RN|du,
    m_next=m+delta*K*D+hB integral_alpha^beta|RN|du,
    eg_next=D.

S=diag(1,1,1,32eV/H). Incoming gas AND photon errors are kept. Since B is fixed on this certified cell, its four-component memory is an exact algebraic compression of the comparison system. A new B on a genuinely subsequent cell cannot consume old m alone; the exported ENDPOINT_MEMORY.json retains all2904 raw photon-error components. All source and reference conditions are inherited with their explicit scope, not certified afresh by a hash.

Residual envelopes are the original16-piece Bernstein quadratic bounds plus M3|u-.5|^3. Exact overlap integrals and exact remainder primitives are used; the pieces are not source samples. Rational matrix inversion and an outward integer ceiling to80decimal places per gas step include the new assembly rounding. The full first-cell initial condition is unchanged and all artificial subcell boundaries use the SAME continuous cubic.

Column radius bound is c*1e6*h*nHmax*sum delta*(Dx+3Dy/38+6Dz/38). Observed sufficient radii(m^-2):

|pieces|radius upper|
|---:|---:|
|1|3125.496134708492|
|2|2343.089035545432|
|4|1952.102468852234|
|8|1756.680194457358|
|16|1658.988405901361|
|32|1610.147234933861|
|64|1585.727990634604|

The64-piece radius is49.26475918percent smaller than the old one. This is a certificate-radius reduction, not measured true error or solver speedup. The center is unchanged. At sigmaT6.6524587051e-29m^2 once:

    tau_firstcell in[7.99991934859042930820e-9,
                     7.99991934859042951919e-9],
    conditional_probability in[7.99991931659107451622e-9,
                               7.99991931659107481254e-9].

Exact rational endpoints and probability Taylor remainders are retained. The old R3 full-history coarse interval and old proper-ne PL bias remain separate. No physical foreground is set to zero and no atomic/calibration/energy-continuum accuracy follows.

An intentionally invalid64-piece reset of all incoming errors yields48.75141498m^-2, marked NOT_A_BOUND. A separate exact g'=2N,N'=0 test carries7e-8 rather than1e-8 across length3. The initial helper omitted memory, failed the focused test, and passed after repair. No upstream R5 bug is asserted.

## Actual live REI development and useful output

Direct Desktop read succeeded at2026-10-14T11:24:37.180129Z. HEAD `d662637da4705b6546fab5d46a83bcec83dba974`, branch codex/rux-science-delivery-20261014; tracked status clean, untracked files not inventoried. Actual STATE, signed-continuation decision, epoch-recovery rereview, ZERO output receipt and compare_histories.py were read. AX07 is scoped complete; AX08 signed family runs; AX11 T1 and AX12 variant preparation are already done. The owner's tuple/list recovery fix is already reviewed and is not duplicated or attributed to HE.

The live STATE reported old observer and two signed groups alive. A separate combined ps/read request was blocked by the OpenAI safety-status gate. No independent ps observation, process action or bypass is claimed. Owner dispatch remains subject to natural old-owner/workers exit, exact terminal classification, shared capacity and existing finite authority. No owner STATE/source mutation or solver start occurred.

A NEW read-only scan consumed the completed canonical ZERO history165923083bytes/312238rows, verifying SHA256 `4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f` while streaming. Domain violations0; max stored charge residual2.220446049250313e-16/H; input size/mtime unchanged. Exact source-derived crossing brackets and linear-time Fractions are supplied for xHII.1/.5/.9. These are stored-history diagnostics, not true crossing-time error bounds, QV, paired convergence or new solver results. Private full raw histories are not published or redistributed.

## Actual electron-floor contract finding and minimal patch

Live reducer SHA256 `b49fbed5f31a45e866915846357d1ddfdef8708ff7ba97ed17695ec8a5c3dc60` gives xe floor1e-7 but Ye floor9.3865e-8. For declared ionic-to-electron propagation at YHe=.2454:

    fHe=1227/15092,
    floor_xe=(1+3fHe)*1e-7=1.243904055128545e-7,
    floor_Ye=(1-YHe/4)*1e-7=9.3865e-8,
    floor_Ye=(1-YHe)*floor_xe.

The original two metadata floors do not commute with that normalization. An intentionally stricter independent xe policy is possible, but must be declared separately; this supplied patch restores the current propagated policy. The reducer already withheld scientific admission, so no false physical trajectory or detected shear claim is alleged.

Actual live-function AST extraction failed the normalization assertion. The minimal xe-only in-memory patch passed12checks, preserving all other tested floors and owner bytes. Full-source patched SHA256 would be `35e1499ef9a69180e5df442c198d3b4c28ea1090c9f6829aad1a68eba8c69cc9` at that exact original. The patch is distributed here, NOT applied to REI. It was additionally applied and checked in temporary exact function context. HH68's separate source_pair_guard was actually read atb8c6fef512cdc3b3b109749b9d4e76335a03aa1f; reuse it rather than duplicate or bypass source-pair binding.

HE_REI_ZERO_BASELINE_MILESTONES is COMPLETED_SCOPED_STORED_HISTORY_DIAGNOSTIC. HE_REI_ELECTRON_FLOOR_ALIGNMENT is READY_FOR_OWNER_SCOPED_INTEGRATION. This is a genuine supplier result, not an external AX11/12 execution transition. Optional optics remains nonblocking for abundances.

## Actual verification and preservation

19new tests passed. R7 exact assembly ran1/2/4/8/16/32/64pieces with no old source solve. One actual Wolfram15.0.1 call:10scalar zero groups,3True controls,4actual xTensor1.3.0zeros; official archive/xTensor hashes matched. Final ZIP114members/113manifest payloads passed CRC/all hashes, relocated read-only verification and altered-copy rejection/restoration. Same assistant plus separate arithmetic/CAS; native subagents and external independent scientific review NOT_RUN.

Retain the first equality-check failure: exact Fraction envelope integration is slightly narrower than the original extra iv rounding, so correct inclusion is <=, not equality. No source/tolerance change. Also preserve initial carry failure, live floor assertion, blocked ps request, temporary patch-hunk generation repair and minor wrong-cwd wc diagnostic. The inherited mpmath.iv trust boundary remains experimental-supported arithmetic, not formal library verification.

[Full Korean proof, executable source, original inputs and exact outputs](https://drive.google.com/file/d/1qZ5NSYancycWzbG8zJFsIZFKcCr7kT7R/view):4615010bytes,SHA256 `f6d28d418900323aa0d1392c0a23d3d54ceb234eac3fd6f53163221887fc3ff1`. Dropbox completed same4615010-byte object `id:BSpOijBcT10AAAAAAD6XpA` in the existing dossier directory. No new output remote restoration test.

[Small Codex supplier packet](https://drive.google.com/file/d/1bWxiMcpymHgyhVH_jE7eok2r7DC1X57W/view):8304bytes,SHA256 `c08f5d9dda23fb5be9d5ced3e61b210991fb13a7a373006c05d6e647d2ed8ffc`. Its contents are also in both full backups. No sharing permissions changed.

Run python src/propagate.py in a separate extracted copy to reproduce new assembly; python -m unittest discover -s checks -p 'test_*.py' -v runs the new tests. python verify_release.py is read-only and calls no source producer. Git includes the actual propagation/helper code and supplier patch; complete inputs/tests are in the immutable archive.

Next R8 judges this scoped result using existing evidence. Remaining15source cells, their actual coefficients/reference jumps and raw carried photon errors, native integration and physical calibration remain distinct. No merge, production activation, external-repo mutation or new global gate.
