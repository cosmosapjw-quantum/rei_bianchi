# Equation to implementation

| Physics/derived equation | Owner | Evidence |
|---|---|---|
| Eq85 σ(E), SDCS andG=1/(16π²) | lc_provider/lc_ionization.py sigma_m2,sdcs_m2_per_eV,tdcs_m2_per_eV_sr2 | SOURCE_ADMISSION.json; provider6groups |
| p(Upsilon|E), exact inverseCDF | transfer_pdf_per_eV,transfer_u | independent normalization/energy controls |
| α=CθE2(x),β=Cθ²e^-x,γ=β(I+2θ),δ=β(I²+4Iθ+6θ²) | LCModel.evaluate | originalσv80digit quadrature; rawGL96 |
| inclusiveU=E−I,D=∫εP2dμ; number2 | theory/DERIVATION.md | directCartesianangular controls,Wolfram |
| Q=−Ir,J=−nHκ₂π_e | net bridge h1_ci_source | scoped bridge tests/receipt atC6–C7 |
| dI=+I,dEth=−I,complete netS_event | pinned HE36 attach_event_tensor/REI ResolvedEvent | oneownertrace+ledger checks |
| F_H0=−nBαY_H0Y_H+,F_H+=−F_H0 | physicalJacobian separatefrom frozen-n_e donor | finite-difference check |
| P2 envelope lower4Iβ/(15θ²),upper2(3γ−Iβ)/(15θ²) | diagnostic/run_diagnostic.py |129savedrows and independentproof |
| temperature particle dilution | conditional thermal_rhs | all-retained-thermal census required |

Paths are relative to components/ unless otherwise shown. Deferred process
providers and gasclosure are not replaced by zero entries in this mapping.
