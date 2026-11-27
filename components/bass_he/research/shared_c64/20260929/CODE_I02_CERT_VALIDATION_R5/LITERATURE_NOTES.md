# R5 literature notes

SciSpace searches covered interval Newton/Krawczyk zero certification, rigorous saddle-node/fold validation, and certifying-computation checker design.

Selected references:

- Breiding, Rose & Timme, “Certifying Zeros of Polynomial Systems Using Interval Arithmetic,” ACM TOMS 49 (2023), DOI 10.1145/3580277. Uses Krawczyk certification for isolated numerical zeros.
- Rump, “Verification methods: rigorous results using floating-point arithmetic” (2010), DOI 10.1145/1837934.1837937. Rigorous verification with floating-point arithmetic.
- van den Berg et al., “Rigorous verification of Hopf bifurcations via desingularization and continuation,” SIAM JADS (2021), DOI 10.1137/20M1343464. Includes rigorous saddle-node behavior.
- “Validated Saddle-Node Bifurcations and Applications to Lattice Dynamical Systems,” SIAM JADS (2016), DOI 10.1137/16M1061011.
- “Calculating Bifurcation Points with Guaranteed Accuracy” (1999): extended bifurcation systems plus Krawczyk validation.
- “A Trustworthy Proof Checker,” JAR 2004, DOI 10.1023/B:JARS.0000021013.61329.58, and “A Framework for the Verification of Certifying Computations,” JAR 2014, DOI 10.1007/S10817-013-9289-2: keep the trusted checker smaller than the producer and make acceptance checker-owned.

BASS_HE implication:
near term, CODE-I02 needs runtime-integrity checking with strict canonical identity and verifier-owned semantic revalidation. Longer term, the existing augmented discriminant system H=(F1,F2,det DzF) is a natural interval/Krawczyk target after realification to R^6; this is a distinct L2 scientific-certification program.
