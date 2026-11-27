# CODE-I02 CERT_VALIDATION R5 research summary

Fresh repository survey (2026-09-29 KST):
- main: 6ef63136d14dbe68a1c9eff4a43fece78cd87b35
- PR15: ac04d2a9e62120a0da4377ddf92451fde0c44431, tree 5697bfb7b2ceae5854499a8132b44e573672df85
- PR17 pre-R5 basis: a0b81a2cd65f223798fc26d6e62b69117f3e6c30, tree 0e68846bb35965714d67d637708384c18b266b8a
- no newer PR than #17 in the recent repository inventory.

Therefore the R4 semantic-admission implementation has NOT been applied to PR15. Gates remain:
CODE_I02_CLOSED=false; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.

## New R5 cache-soundness finding

Do not memoize admission with a raw nested Python tuple, even through functools.lru_cache(typed=True).

Observed counterexample:
(1,0,0) == (1.0,0,0) == (True,0,0), with the same tuple hash in the observed interpreter. A typed lru_cache invoked on those tuple arguments executed the underlying function only once.

This can reintroduce the same representation-aliasing class that CODE-I02 is repairing.

Required cache identity:
key(x)=SHA256(V || C(x)),
where C is a deterministic canonical byte encoding over the accepted endpoint domain and V binds verifier/policy revision. Persistent caches must include transitive scientific/verifier source identity. Existing src/bass_he/geometry.py already provides a useful pattern: deterministic _canonical(...), allow_nan=False, content-addressed EvidenceCache, key/payload hash verification, and an explicit requirement that caller include transitive source identity.

Near-term recommendation: use an in-process canonical-byte/digest cache for the semantic admission result. If persistent EvidenceCache is used, include exact verifier/scientific source revision in its key. Never use a caller-supplied digest alone as cache authority.

## Immediate R4/R5 implementation remains bounded

The independent hostile rereview still governs:
- F01 Important: NaN/-Inf/negative/string matching-error values can reach first anchor.
- F02 Important: stored JSON binding identity may differ while Python equality passes; validator hashes reconstructed expected binding rather than stored canonical bytes.
- F03 Minor: truthy non-boolean passed is admitted.

R4 research additionally found truthy/nonboolean simple_fold and numeric-string tolerance/probe/error aliases.

Required repair:
1. verifier-owned policy tolerance/probe scale;
2. stored/expected binding compared by canonical bytes;
3. binding_sha256 verified against stored canonical bytes;
4. strict finite/nonnegative admission scalars;
5. fresh current-endpoint spectral_certificate(simple_fold) and pair-membership recomputation;
6. exact canonical cache key, not raw Python tuple;
7. persistent cache key includes verifier/source identity;
8. stored diagnostics remain non-authoritative unless explicitly promoted.

## Future L2 fold certificate, research only

The current exceptional-point locator already solves the complex augmented system
H(p,lambda,R)=(F1,F2,det DzF)=0.

At a rank-one fold, in adapted coordinates DzF=diag(a,0), a!=0. Let alpha be parameter transversality and beta null-direction curvature. The augmented Jacobian has form
[[a,0,m],[0,0,alpha],[q,a beta,r]]
and Wolfram verified det(DH)=-a^2 alpha beta.

For complex J=A+iB, realification [[A,-B],[B,A]] satisfies det(J_R)=|det J|^2 (Wolfram symbolic check for generic 2x2 J). Hence H:C^3->C^3 can be realified to a 6-real-dimensional root problem.

Literature retrieved through SciSpace supports a future interval/Krawczyk path:
- Breiding, Rose & Timme, ACM TOMS 2023, DOI 10.1145/3580277: Krawczyk certification of isolated zeros.
- Rump 2010, DOI 10.1145/1837934.1837937: rigorous verification with floating-point arithmetic.
- van den Berg et al., SIAM JADS 2021, DOI 10.1137/20M1343464: rigorous bifurcation validation.
- Validated Saddle-Node Bifurcations, SIAM JADS 2016, DOI 10.1137/16M1061011.
- Calculating Bifurcation Points with Guaranteed Accuracy (1999): extended systems plus Krawczyk validation.

Do not implement L2 now. BASS_HE-specific blockers remain: interval exclusion of every continued-fraction denominator from zero, rigorous second derivatives/AD for D H, and a separate validated-continuation certificate tying named ordinal states to the two local sheets.

Next canonical node: implement bounded R4 semantic admission with the R5 canonical-cache refinement, then obtain a fresh independent rereview.
