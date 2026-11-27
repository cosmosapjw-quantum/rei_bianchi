# Literature notes: certificate checker architecture

SciSpace searches used natural-language questions on self-validating numerical computation and proof/certificate checking.

## Selected references

1. L. B. Rall, "Numerical Computation with Validation," 1988. DOI: 10.1007/978-3-0348-6303-2_33.
   - Valid numerical computation should return a result with a validity guarantee or explicitly fail to validate.

2. George C. Necula, "Proof-carrying code," POPL 1997. DOI: 10.1145/263699.263712.
   - Consumer owns the safety policy; producer supplies evidence; consumer validates evidence with a small checker.

3. Kurt Mehlhorn and Pascal Schweitzer, "Progress on Certifying Algorithms," 2010. DOI: 10.1007/978-3-642-14553-7_1.
   - Certifying algorithms return output plus witness that a checker can verify independently of the complex producer.

4. Kevin K. H. Cheung, Ambros Gleixner, Daniel E. Steffy, "Verifying Integer Programming Results," IPCO 2017; arXiv:1611.08832.
   - Solver output is accompanied by certificates checked by a separate verification tool using a small set of inference rules.

## BASS_HE design takeaway

The checker should own the acceptance relation. A producer-provided `passed` flag is metadata, not authority. The current certificate is not a formal proof object, so the least invasive strong design is verifier-owned semantic recomputation of the current endpoint, cached by exact content identity, plus strict payload integrity checks.
