# PHYS19: 실제 FT03 기체의 birth-time 응답과 source 오차

2026-10-10 KST. CONTINUOUS_SOURCE_GAS_BIRTH_RESPONSE_C4_AND_CAUSAL_FEEDBACK_CONDITIONALLY_ENCLOSED.

기존 FT03 HG CaseA HHe CI/RR/twoDR, prescribed FLRW, 원 3cell/6Gauss birth와 initial family를 유지하여 [0,1.25e9] proper s의 source-only 오차를 제한했다. Checkpoint 작업이나 새 물리율 추가가 아니다. true constant-S gas 위의 birth derivative C1..C4와 actual gas time derivatives를 사용하고, finite-birth gas의 derivative jump를 spline으로 숨기지 않는다. Exact radiation moment Mphi',Mphi''와 positive photon measure의 support/mass로 gas derivative3까지 감싼다. Finite moment closure나 IVP truncation이 아니다.

원 에너지와 원자식/상수는 binary64의 exact-real 해석이다. HI cutoff 미횡단, He photo inactive지만 He nonphoto/thermal feedback retained. HH/RCT/CR OFF. Lower-limit derivatives에 a',a'',a'''가 존재하며 fixed-opacity tiny Gauss diagnostic을 복사하지 않는다.

Positive upper bounds: source-only terminal |delta xHII|<8.643437e-14, |delta T|<7.053107e-9K, |delta GammaHI|<1.405368e-24/s; source-only first-macro |delta tau|<2.011484e-19. Whole-time gas sup<1.795685e-10 differs from endpoint. Same-gas completed Gauss-cell count remainder<5.016106e-20/H is NOT total gas error: causal incomplete-cell forcing and Volterra feedback dominate endpoint bound. Old BRIDGE14 T-source upper / new upper approximately37965.8; no physical fit uncertainty reduction claimed.

Combined with unchanged BRIDGE13 time certificate: continuous constant-S minus matched native family xHII [1.2362889,1.4137188]e-8, T[-3.518428,-3.054330]e-4K, GammaHI[-2.564461,-2.245490]e-19/s. Source error sign itself is not certified. Same first-macro refinement loop is closed; next physical target Bianchi-I directional weak-shear absorption/heating and exact angular-measure conditions.

New15unit(2assertionRED/GREEN,13after), independent80digit Taylor60/sigma40/gas+opacity64 components, symbolic6, changing-hazard14, Bernstein100 exact-rational diagnostics. Core proof uses whole-domain interval bounds and288whole-time Bernstein panels, not samples. Five fresh commands exit0 after recorded45s diagnostic interruption; four result files byte-equal. Native/IVP/old proof/campaign reruns0.

Full executable code, exact inputs, interval evidence, failures and report: REI_PHYS19_COUPLED_BIRTH_RESPONSE_20261010.zip,157519bytes,50entries,49payloads, SHA25666b93eebf614cc83949abfeb167a94b94d1a2cae3024c9e1ecdf9fcd7e116737. This Git directory is a bounded publication projection; the standalone helper is not the full proof. All historical [160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD preserved.
