# OBSERVER15 R9: certified cubic to actual BASS component return

2026-10-14 KST. Selected R9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT, resumed after interruption. Parent R8 head39dce6702dcadbb516fc8e25e7ba5a6991f64c22 was read unchanged before this additive publication.

Decision: **PASS_SCOPED_SAME_TARGET_CELL_INTEGRAL_COMPONENT_RETURN**. This is an actual isolated compiled BASS source-component consumption, not the full BASS crate, chemistry/REI production, physical RUX05/RUX10 admission, polarized transport, or R10 completion.

## Complete executable source and evidence

- REI_OBSERVER15_R9_20261014_SOURCE.zip,725524bytes,77members/76manifest payloads.
- SHA256:7183aba312b0b521a28c3c5160193eec0b99f7dfd2c6869d4e15a9a7ea45c1c0.
- [Full Korean proof, tested adapter, immutable source inputs, actual native/CAS outputs and handoff](https://drive.google.com/file/d/1UOGPzchSkX4_FRXIgUenENrv-4mim6py/view?usp=drivesdk).
- Drive ID1UOGPzchSkX4_FRXIgUenENrv-4mim6py, existing parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Actual upload and name/ID/size/parent readback matched. Local CRC, all76payload hashes, nested font absence and relocated verifier passed. New full-R9 remote restore/Dropbox upload not performed.

The archive includes the complete unchanged R8 ZIP with both R7 variants. Git contains this substantive result and restore entrypoint; all executable payload files are in the archive, not all expanded into the repository. Download by ID/hash, not a filename-only match.

## 1. Same target and exact projection

Keep selected R7-A archive10b74244bc9dd56f7043861ae5a492c5b7ec8d3d232e487f092d729c7657e26a and CUBIC_OBSERVER_RESULT.json402a92a38e8884c1cf1dcd44bf47644481eeb83be8131f6c52ac7414eb5aac40. Target remains SHEAR12_EXACT_DECIMAL_EPS0_NORMALIZED_MATH_GL32, source-free primary photoabsorption and normal-comoving gas. Original CSV/source, exact-decimal parameters, mathematical GL32 measure and R7 continuous-time certificate remain unchanged. No historical runtime q/w byte restoration or spectral-continuum/physical-rate certificate is asserted.

For q(t)>=0 on the same normal proper clock and cell edges:

    D_i=integral_cell q dt, qbar_i=D_i/(t_(i+1)-t_i),
    tau_i=tail+sum_(j>=i)D_j,
    S_i=exp(-tau_i),
    P_i=S_(i+1)-S_i=exp(-tau_(i+1))*(1-exp(-D_i)).

These follow from d exp(-tau)/dt=q exp(-tau). Replacing q by its cell average preserves edge tau/S and cell/bin masses exactly. Coarsening telescopes, with unscattered mass retained. It does NOT preserve within-cell visibility profiles, peaks, or arbitrary new cut boundaries. q=2t versus qbar=1 on[0,1] has the same total depth1 but different midpoint-to-observer depths3/4 and1/2.

The certified cubic supplies C_i=integral_cell .4exp(-.12u)xi_e du, u=t/t_star. The adapter maps

    qbar_i=r*C_i/(t_star*Delta u_i), Delta t_i=t_star*Delta u_i,
    r=sigma_T/sigma_star.

r and C_i are dimensionless; qbar is normal s^-1. Apply sigma once before the nonlinear probability. The generic integrate_visibility API does NOT multiply sigma or Doppler again. t_star200s versus1400s is a synthetic unit embedding/clock discriminator, not physical cosmological calibration.

Signature(-+++), x0=ct, dx=c*k*ds. General current/age conventions retain A=q.k, D=-u.k, q=c grad(theta), and column C_SI=integral[cDN/(VA)-k.j/A]dtheta. The present zero-tilt/spatial-current fixture uses its matching normal clock. No double dilution or foreign proper-volume assumption is introduced.

## 2. Actual native seam, not the sampled-PL API

Read the full existing BASS visibility.rs and historical source contract at commit41fa2d5f6874a6d9eb1a151ff83b2d56f1d2fd25. Recovered exact modules:

- frame.rs4068bytes SHA25682aa87fecfbac746ebca7ff3e9da0d243f30e9bdd9fc905c7b7abdb52a726674.
- visibility.rs10763bytes SHA25604afff8fecbbfc961a7c405e8821b6121c71b7a63fe37a9a58d8f6c5acb560c8.

Actual API is integrate_visibility(time_edges_seconds, interval_rates_s_inverse, observer_optical_depth). A new26-line receiver wrapper calls this unchanged production module. integrate_rest_frame_sampled_visibility is a distinct PL-edge-rate API and was NOT substituted for the cubic integral interface.

One rustc1.94.1 build and one native process batch completed. PRELAUNCH.json was written before execution, with source/input/binary identities. Original dirty BASS/REI checkouts were not edited. This new receipt does not repair the historical warm P01 prelaunch-HOLD retroactively.

- Binary SHA256a98fb713de67cb52c5e253f029bedde522a22cdaafa352112d4f6fda3265af3e, identical before/after.
- Input SHA2564c5e8008cf06de0eb3dd78fab6dde8091b66758bb50a31a04622a2553a343764.
- PRELAUNCH SHA2562ff6ea1946ac9c3efff26ec3072e4876fb41827af17dc0e8f4ce288aa9c4152d.
- Raw stdout SHA256de49477e77e3bb7c4c534ba9769cc3c2d4c2a5416266303e5f21c4fa1c20f3c6.
- Build/native exit0; no compiler/native stderr. Prelaunch UTC05:50:13.291092; postlaunch05:50:13.296753 on2026-10-14.

Original native source/input/output/receipts were separately uploaded and actually restored: Drive1B7JSBNcA0cRFcv2F5lZwYaxc4I8M6FF7,14971bytes SHA256062e85cd7b1ca45afc5c164245838f27ffd312c938b20bf14422d2623ac0b749. Its15payload hashes and ZIP CRC match. This restore claim is for that native evidence archive, not the new full R9 ZIP.

## 3. Actual results and error accounting

Fixed observer u=.5, near.25, far.20; missing fixture tail0. An unrelated physical continuation stays null. The strict adapter rejects other sources, active chemistry, epsilon!=0, conformal clocks, different boundaries and unspecified tails.

Native returned bin probabilities:

| Case | P |
|---|---:|
| fine60cells,r1,t_star200s,tail0 |0.0020224807481703175|
| coarse2cells,same integral and edges |0.0020224807481703175|
| fine60cells,t_star1400s,rates/7 |0.0020224807481703175|
| fine60cells,synthetic tail.25 |0.0015751095904218838|
| coarse,r1e-24 |2.04512357396277e-27|
| r0 |0|

The reported fine-bin value sums the retained native cell probabilities exactly, then rounds once to binary64; that last round is included in the check. Negative rate/repeated time/negative tail returned InvalidRate/InvalidGrid/InvalidObserverDepth, respectively, within the successful9-case batch.

Inherited true finite-source interval for r1,tail0 remains

    P_source in[.0020224807481693721,.0020224807481712630].

The point-to-true-source radius for the actual native r1 result is <=9.454286881658e-16. Fine-case actual native probability versus the exact-real result of its transmitted binary64 inputs differs by <=2.840063324692e-22. Its separate input-quantization sufficient bound is4.255852430797e-20. Coarse/clock7 native-arithmetic bounds are2.695192456946e-20/2.287911134201e-20. These are fixed-output a posteriori comparisons, not universal libm constants or measured physical uncertainties.

Separate source-versus-cubic error, midpoint/input conversion, and actual receiver arithmetic. The exact exp(-x) reference uses alternating rational Taylor bounds and rational squaring on0<=x<=16; larger numerical requests are refused although the symbolic formula remains general. No assumed f64 exp/exp_m1 ulp guarantee. Independent mpmath220-digit values are diagnostic crosschecks, not the interval proof. Output sidecars retain exact target intervals even when native point outputs are reported.

## 4. Current cross-repo binding

Read actual REI117 BASS_RECEIVER_CONTRACT and TRANSPORT_REUSE_AND_BINDING at bccbe300955e59efd72326c0b74c9e3124c3cd81. CC-RECV/RUX10 requires one admitted RUX05 physical proper-ne segment, presently absent. The current synthetic return is not that segment and does not complete its physical source/observer obligations.

Read full HE49 R4_RESULT at40659a752b9348fb7919cf5afcf42f310e05d064. Reuse the exact representation split true-old=(true-new)+(new-old), not warm P01 numerical coefficients. Its forced/temperature-coupled source differs from source-free SHEAR12; fine whole-cell warm residual work remains with HE17. Latest CR59/HH65 metadata was reviewed without importing changed kinetic/continuum models. Existing SOURCE07 wider event/thermal/source obligations, BASS observer-cap, REC, global DAG and CR/RCT/HH OFF are preserved.

## 5. Verification, failures and next

280new named validation conditions pass; counts include individual edge exponential comparisons and are not280independent theorems. A deliberate new adapter candidate missing t_star failed its focused assertion and passed the identical test after correction; not an upstream bug or whole-workflow TDD claim.

Actual cloud Wolfram15.0.1:11scalar zeros. Actual xTensor1.3.0/xCoba0.8.6:6CTensor/current/covariant-derivative zeros, xPerm connected, xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Scripts precede submissions; observed cloud JSON is normalized transcription, not raw network transport.

Preserve the manual base64 transport failure before execution, stale-cwd shell diagnostics, empty fresh Drive search and the110-digit checker rounding failure on an exceptionally thin exp interval. Exact Taylor/source bounds were unchanged; 180/220-digit diagnostic resolved the checker's precision. No physical tolerance relaxation or old source rerun.

Same author separate arithmetic/CAS; external independent scientific review and native subagents NOT_RUN. Native component1batch, full BASS crate0, source ODE0, R7 residual replay0, old suite0, HPC0. New replay_component.py is syntax-checked packaging guidance; the actual original run was through the remote terminal, not that later driver.

Read REPORT_KO.md, CONSUMER_RETURN.json, CONTRACT.json and HANDOFF_KO.md in the archive. Read-only validation: python code/validate_return.py; no native or source launch. Explicit native replay, only when requested, uses code/replay_component.py NEW_DIRECTORY and needs a new output comparison.

**Next selected stage: R10_SOURCE07_CUBIC_RETURN_CLOSEOUT.** Preserve this actual same-target return and prepare the owner handoff from existing evidence. R10 remains unexecuted. No production switches, global gate changes, main merge, force push, external-repo mutation or old-source overwrite.