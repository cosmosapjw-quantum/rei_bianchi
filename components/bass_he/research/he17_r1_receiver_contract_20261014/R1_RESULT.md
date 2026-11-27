# HE17 R1: actual warm native receiver and electron-column contract

2026-10-14, Asia/Seoul. Selected R1 of HE17_SOURCE_MATCHED_RECEIVER_BINDING, following the new user request and THEORY16 R10 handoff at b1f2ef158e0066a4b2d24cc8abf47a1c169742a6. THEORY16 is not reopened. R2-R10 and native integration are not completed here. The installed physmath1.3.0 selection and updated policies were read.

## Concrete source/receiver choice

Select **P01_EVENT_BRIDGE02_17_NODE_0_1e11s**, the actual rei_bianchi SourceBoundConditional/AXI warm FT03/Hui-Gnedin plus HM12 source path at a5c958c414dea41216b445c05f58df837f05cacb, tree2e96362102caa69c814d477bae5d1c0177b502f9. PR114 still has this head. Original native evidence is HE PR30 commit6b337be443d0fbe8f07d99e7b3ff1cc210294bcb.

The original2024590-byte event-bridge archive was actually restored from Drive1giyA_gippzeljvlRAk8oDuO7f3K3itUE; SHA25633745d9234a0ee2fe771c0c37329b889c551b05dc008eab41f360232938539bb and CRC match. Read its provider contract, saved17-node production history, initial/final raw STAGE/RHS/EVENTS and final formatted native code. The two Rust file hashes match the final native receipt, not merely the original pre-format candidate. The frontend was read as pinned connector text; its receipt SHA is retained without a second raw-frontend-byte claim.

The source is prescribed LRS Bianchi I dust+Lambda with gas/radiation test fields; normal proper seconds0..1e11; T0=50000K; Tguard30000..110000K; YHe=.24; initial s/H=.001,b0=0. b is metric anisotropy, NOT velocity tilt. Gas is normal-comoving. Initial HM12 UVB and ongoing HM12 emissivity are distinct. Closure is HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE with CR/RCT/HH OFF. Actual original state has gas4,photon2904,ledger5. Original scientific_admission HOLD and exactly-once/native validation retain their original evidence status.

This is not the cold CR53/55/56 source. R9's load_cr53 is preserved and NEVER called with these warm inputs. Reuse is the general current/column algebra and exact exponential arithmetic, not a foreign numeric certificate.

## Direct fraction-density-current equations

Signature(-,+,+,+), x0=ct, U=c*u,u.u=-1; retain c,hbar,kB. Let x=xHII per H nucleus, y=xHeII,z=xHeIII per He nucleus, and f=nHe/nH=Y/[4(1-Y)]=3/38. Then

    chi_e=x+f*(y+2z), ne=nH*chi_e.

For net proper event rates rH,r1,r2, including recombination with original signs,

    xdot=rH/nH, ydot=(r1-r2)/nHe, zdot=r2/nHe,
    chi_e_dot=(rH+r1+r2)/nH,
    ne_dot+3H*ne=Se=rH+r1+r2.

The native RHS uses proper species dilution, then adds3H*n_species when reconstructing fraction derivatives. Do not add dilution again. Stored gas ne is proper cm^-3 and becomes SI by10^6. Photon stock alone has N_gamma,ref=a_rel^3*n_gamma. Native `volume=a_rel.powi(3)` is a DIMENSIONLESS volume ratio, not an absolute CR cell volume.

With J_e^a=c*ne_SI*u^a, the actual covariant product derivative yields nabla_a J_e^a=Se_SI. For dx=c*k*ds, q=c grad(theta), A=q.k and D=-u.k, column derivative is -k.J/A. This comoving proper-time source has A=D=1 for k0=1, so

    C=integral c*ne_SI dt [m^-2], tau=sigma_T*C.

The temperature coordinate w is eV per H nucleus:

    T=2 epsilon_eV*w/[3 kB*(1+f+chi_e)].

Proper number sources convert by10^6 and proper powers erg/cm3/s by0.1. Work, escape and external power retain native owners. No equal-total-energy difference or CR half-norm numerical radius is imposed on this forced warm source.

## Exact current native seam

Frontend stage(t,state) constructs one geometry, photon characteristic and source at the same time/state. Native detailed_rhs reads thermal events, combines node photo events through CaseAEventBundle::into_ledger, feeds proper species/electron/thermal/escape sources to axisym_coupled_derivative, then reconstructs fraction and per-H thermal derivatives.

The preserved axisym_conditional.rs snapshot has detailed_rhs335ff, a_rel^3341ff, provider356ff, owned event bundle407ff, net edges412, SI sources438ff, coupled derivative459ff, fraction reconstruction467ff, work480ff. A future passive column state must consume that same proper ne once; for normalized solver zeta=t/h it must use dC/dzeta=h*c*ne_SI. This R1 does not add that new native state or enable active scattering.

## New actual saved-history diagnostic

Interpret each recorded float as its exact stored binary64 value. Define ONLY a piecewise-linear reconstruction of saved proper ne, not a continuous-IVP certificate:

    C_PL=c*1e6*sum_i dt_i*(ne_i+ne_i+1)/2.

The17saved nodes have dt=6.25e9s. Exact column:

    17330529084258382468228998565673828125/9007199254740992 m^-2,
    C_PL approximately1.92407524182795857872518825e21 m^-2.

Using explicitly declared passive sigma_T=6.6524587051e-29m2,

    tau_PL=1.2799831091765790683602602238852194e-7,
    P_PL in[1.27998302725874457460799737349e-7,
            1.27998302725874457460799737350e-7].

The last interval encloses the exact saved-node INTERPOLANT arithmetic. It is not the true source solution at30-digit accuracy. The second passive convention6.6524587e-29 is recorded separately, not declared to be an active native photo cross section. Apply sigma once before the nonlinear exponential.

For this explicitly chosen numerical fixture the observer is the last saved time1e11s and extra fixture tail0. The physical continuation beyond that endpoint stays null. No foreign SHEAR12 tail is copied.

chi_e rises from1.0812759846232406 to1.0812759847801665, while proper ne falls from64.1804549337503 to64.18002849673917m^-3. Positive fraction evolution and decreasing proper density are consistent:3H ne dominates the net source. At the two actual saved probes, fraction-RHS versus EVENTS electron source residuals divided by gross positive event sums are1.8981184e-16 and5.1591585e-16, below the inherited3e-11 gross-event comparison criterion. Cancellation-sensitive tiny net-relative errors are not used.

Controlled reconstruction comparisons: frozen initial ne overestimates column by3.32221247ppm; omitting He electrons underestimates by7.51894163percent; dividing already-proper ne by a_rel^3 again underestimates by3.32224627ppm. These are diagnostics, not physical uncertainty budgets. The composition-only tau difference on the same saved nH nodes is6.21301508903e-18.

## Precise remaining input, not a new global gate

True-IVP column/probability intervals remain null. Required evidence is SAME warm-source node/dense signed-residual error and between-node error. The solver's rtol/atol, empirical reference agreement and conservation ledgers are not automatically a rigorous optical forward bound.

If eps_i bounds SI density node error and M_i bounds sup|ne_SI''| on each smooth source cell, the direct accounting is

    |C-C_PL| <= c sum h_i*(eps_i+eps_i+1)/2
               +c sum M_i*h_i^3/12+E_arithmetic.

C_PL assembly uses exact Fractions. No new numeric M_i or nodal radius is invented. Event derivative jumps require splitting or a valid jump term.

Next R2 retrieves existing dense/stage/signed-residual evidence for the exact frozen warm source first. A forced-photon lift candidate must retain Nhat_j=G_j N0_j+integral G_j Shat_j and temperature-dependent CI/RR/DR/thermal feedback. Do not transplant the source-free SHEAR12 C,K,M2 numbers or rerun an unchanged ODE/atomic campaign merely to populate stages.

## Latest actual cross-repo use

CR56 compact proof at34f8a64232892679f772465eab02200805e43d47 read: seeded moving all-angle shell/current certificate, next NT_CONTINUOUS_ANGULAR_PREFIX_FRONT. Its cold source and narrow column are not warm P01 inputs.

HH62 compact proof at2410c0d8ffd62abf204c1ca38b19a64814058717 read: finite-window Coulomb numerical rate2.2056248383253494e-12cm3/s and analytic omission sum<9.819e-19 do not yet give a global quadrature/all-roundoff interval. Next PHYS30_COULOMB_FINITE_QUADRATURE_CERTIFICATE. No active HH modification in the OFF receiver.

REI115 new R7 at8bf8e3c18d607334614cfea734f9b10961fbd4d4 read: SAME SHEAR12 Gauss32 saved-node/bin errors now certified; do not return them to pending. Its Hermite/analytic-photon/block-defect method is a candidate for appropriate adaptation, not a numeric warm certificate. Owner next R8_SCOPED_JUDGMENT_AND_CONSUMER_RETURN_SELECTION.

Exa and SciSpace were actually used for bounded primary/context discovery. Hui-Gnedin1997 arXivastro-ph/9612232 metadata/abstract and actual source definitions are distinguished; no unread theorem, new fitted rate or empirical calibration is attributed. Official xAct release was verified on its own site. No source-paper PDF or font is redistributed.

## Actual evidence and durable delivery

32new source/data/contract checks passed, including6input identities. One actual cloud Wolfram15.0.1 call returned11scalar zero groups and4actual xTensor1.3.0 tensor zeros, including a covariant derivative. Submitted script SHA256688369e1380f1cad37bcde50ec437fb8f671387e06324d9afbab9afb7f9ece3e. Official archive and xTensor.m hashes match the retained1.3.0 source. No new failed CAS residual or solver warning returned. Output is a normalized observed transcription, not raw connector transport bytes. These are tests-after, not native/TDD evidence.

Native subagents NOT_RUN (not exposed), external independent scientific review NOT_RUN; same-author separate arithmetic/CAS. Source/native/ODE/HPC calls0; old scientific suites0. Optional raw Git DNS failure, A&A HTML403 and empty directory rendering are retained without inventing missing data or retries. Original receiver/parent evidence remains unchanged.

[Full Korean report](https://drive.google.com/file/d/1Pv9FsDucz2l_rHEQZ08nr4X5wa-DR6c7/view),18407bytes, SHA25692a917ba8dffd3aca58f6047a4e8347c528588cbf169b38ab9b11972e2fb400c. Standalone Dropbox completed same18407bytes, id:BSpOijBcT10AAAAAAD5JCA.

[Full reproducible archive](https://drive.google.com/file/d/140zFRyrVq17TxdWfmbBqty4QjCfOabSN/view):BASS_HE_HE17_R1_RECEIVER_CONTRACT_20261014_v1.zip,60661bytes,22members/21manifest payloads, SHA256d75dca5e13eb35b57f463566b6b42971faed75ae281d2390151818fb45c3091c. Dropbox completed same60661-byte object id:BSpOijBcT10AAAAAAD5I1w. Existing destination BASS_DERIVATION_DOSSIERS_20260912 and Drive parent1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI. Local CRC, all21payload hashes and a relocated final-ZIP check passed. No new remote restore or sharing change.

The archive contains the complete machine-readable receiver contract, original selected source files, saved data, provenance-marked probes, exact result, stage-local check code, CAS evidence and next action. Reproduce with `python checks/inspect_binding.py`; verify storage with `python checks/verify_package.py` from BASS_HE_HE17_R1_20261014. The Git file is a substantive compact result/entrypoint, not byte-identical to the longer report.

Next selected stage R2. Actual native column implementation, source-specific forward-error closure, existing HE provider/moments/moving-stage/certificate-adapter, global RUX/all-Bianchi/D2.3 and physical admission retain separate status. No new global gate, production switch, external-repo mutation, merge or heavy launch.
