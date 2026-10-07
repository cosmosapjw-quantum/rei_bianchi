# Stored-log-coordinate source export convention

2026-10-07. Pre-execution clarification agreed with the implementing root. This is a declaration of the finite numerical geometry, not a change of the true logarithm of a physical energy into an exactly representable number.

Authoritative source anchors are the supplied binary64 values Lmin=log(13.7), Lmax=log(20), and Lc=log(13.6). For each observation h, store the actual binary64 swept face B=fl(h+Lc) and source upper front. The mathematical oracle treats those supplied anchors and B as exact inputs. Set w=max(0,B-Lmin), D=Lmax-Lmin using high-precision exact differences of those inputs. Then

    out_N = q [min(w,D)^2/2 + D max(w-D,0)]

is the correct continuous swept-measure result. Its derivative with respect to B is q clamp(B-Lmin,0,D), so it has quadratic onset and no persistent-node jump. Exact zero is legitimate if and only if B<=Lmin under this fixture.

This convention must retain, rather than suppress, the finite geometry discrepancy

    delta_B = exact(B) - [exact(h)+exact(Lc)].

The source ledger refers to duration h. Therefore the event geometry and ledger times can differ by that explicit rounding amount. Budget tests and independent owner comparison must quantify the effect in the selected matrix. A passing comparison cannot be interpreted as proof of exact physical continuum geometry at every real time, especially for tiny positive h where a front can alias its initial coordinate.

Cutoff outflow energy uses the stored Ec=13.6 eV. The difference between exact Ec and exp(exact Lc), and the analogous source-band roundtrips, are separate recorded arithmetic discrepancies. No tolerance-dependent event band, nextafter displacement, arbitrary absolute floor, or use of high-precision log(exact physical-energy input) solely when it makes a borderline zero pass is justified.

This contract is mathematically adequate for a finite, prescribed-stage continuous-export control. The production physical lower-boundary problem and full cosmological source conventions remain separate integration gates.
