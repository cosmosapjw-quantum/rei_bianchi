# Unit6: external-calculation-independent research

Pinned sources: PR151 edead502 (fullSHA in intake/SOURCE_PIN.json); PR150 eb2abcac. External NCP process state was not inspected; no newer Unit5 execution result is posted in pinnedPR151.

|Programme|Reusable evidence|This unit|Remaining physical dependency|
|---|---|---|---|
|T1 Li bound|FCI/basis results|Reuse|basis error,finite-mass/relativistic treatment|
|T2 continuum|projected response/TRK diagnostics|Reuse|energy-normalized outgoing channels and exclusive cross sections|
|T3 molecular lowT|BO curves/dipoles|Reuse|channel couplings and radial scattering/reaction calculation|
|T4 daughters|actual64partial;Unit5resume8tests|A: streamed QR residual diagnostic|external64→128,refinement,T2andECoperators|
|T5 nuclear precision|quadrature/sensitivity results|Reuse|data likelihood,covariance,truncation uncertainty|
|T6 charge cascade|actualE1mixtures with2s reservoir|B: two-photon continuum and response|injection,collisions,escape/reabsorption,coupled transfer|
|T7 BBN→17|conditionalmap,actualBBNdonor|C: charge-resolvedBe7EC event bridge|charge/recombination history,rate providers,native integration|
|T8 transport|PR150SOURCE010/011scoped outputs|Readandreuse; separateowner|source-age reference/refinement andfullcoupled trajectory|

Lane dependencies: frozenA→QRcode→densecomparison→independentreview; frozenB+saved32mixtures→Ckernel/continuum→conservation/photoresponse→review; frozenC+donor→event/exposurecode→electron/charge/baryonchecks→review. All three are independent of the ongoing external Hamiltonian calculation.

No whole physicalprogramme is declaredclosed by a scoped localPASS. Stage-wise status and actual backup/publication IDs will be resolved in progress/STAGES_FINAL.json and DELIVERY_FINAL.json.
