# HE29 S1: conditional positive survival bounds

For a positive measure dN with mass M, mean frozen absorption rate mu, and rate support [a,b], f(lambda)=exp(-t lambda) is convex for proper age t>=0. Units: lambda s^-1, t seconds, M photons/total-H or normalized photon number.

Jensen lower L=M exp(-t mu), endpoint-chord upper U=M[(b-mu)exp(-ta)+(mu-a)exp(-tb)]/(b-a). Both sharp: Dirac at mean and endpoint mixture. At a=b, t=0 or M=0 use exact limits. Further nested rate-support partitions with actual child mass and mean raise summed L and lower summed U. Never invent child moments from insufficient parent data.

Wolfram verified f''=t^2 exp(-t lambda), endpoint identities and (mu-a)(b-mu)-(b-a)^2/4=-(a+b-2mu)^2/4. Linear interpolation gives U-L <= M t^2 exp(-ta)(mu-a)(b-mu)/2 <= M t^2 exp(-ta)(b-a)^2/8. This is not the earlier energy-local remainder incorrectly applied to a global per-band fit.

The implementation and 720 interval evaluations are conditional on the actual positive GL256 donor atoms, not rigorous continuous-energy support or interval arithmetic. A binary64 guard is explicitly diagnostic. GL512 agreement is numerical, not a proof of quadrature error. Frozen survival bounds do not certify downstream native temperature.

Additional error separation: if genuine radii ea,eb bound temporal errors, then true cross-grid difference lies in [max(0,abs(a-b)-ea-eb), abs(a-b)+ea+eb]. Radau/DOP853 agreement alone does not prove ea or eb; new same-r/same-table references are still needed.

24 focused bound tests passed, with two initial behavioral RED failures retained. Completed 90 signed-source/strip/birth-time/age cases and720 nested bounds. New native calls0. Full report/ready native reference-only runner follows in S2. Stage1 archive SHA e13ade0747059dbc1e691dcf52d6d84329aca0e00005dbd5467eea0b0b8255af.

Literature context: Mirocha et al.2012 doi:10.1088/0004-637X/756/1/94; Bayer and Teichmann arXiv:math/0502473. Own derivation and tests are not a claim of new general convexity theory.
