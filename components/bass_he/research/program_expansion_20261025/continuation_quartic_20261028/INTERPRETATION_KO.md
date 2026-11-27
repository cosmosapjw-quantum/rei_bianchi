# R7/C7 — discriminating results and new CAS
## Main outcome
Fixed officialdata/windows admit a full nonnegative endpoint-free even quartic at330MeV.
N4 andN16 have the same deterministic witness b≈(0.140838303,-0.308117512,0.752692956); its exact globalminimum is positive.
The old degree4 sufficient cone excludes it because a1≈-0.611854653<0. Thus previous EMPTY and new feasible witness are compatible results for different mathematical families.
At330MeV the endpointzero family remains EMPTY_OUTER. That extra endpoint constraint is a genuine model distinction, not the old sufficient-coefficient artifact.

## Certified acceptance enclosures
The following values are rounded OUTWARD to8decimals from exact fractions. They enclose every genuine feasible distribution in the named family; they are not confidence intervals, fitted point estimates or measured reaction rates.

| EnergyMeV | Family | HEMISPHERES outer enclosure | CAPS outer enclosure |
|---:|---|---|---|
|213|FreeN16|[0.68262445,0.79669077]|[0.11121960,0.47234396]|
|258|FreeN16|[0.61837610,0.72996144]|[0.06067572,0.33548040]|
|330|FreeN16|[0.84269078,0.84492144]|[0.56910576,0.57480298]|
|213|Endpointzero exact|[0.68262445,0.74793761]|[0.11121960,0.20088783]|
|258|Endpointzero exact|[0.64371174,0.72996144]|[0.08848322,0.19563706]|
|330|Endpointzero exact|EMPTY_OUTER|EMPTY_OUTER|

FULL=1 for every actual feasible distribution. The data do not identify an overall physical event normalization or flux.

## Finite-resolution gap
213 and330MeV endpoint-free N4/N16 extrema are bracketed by outer enclosures and inner witnesses within roughly10^-14 in saved exact values; this is numerical/model-optimization precision, not experimental accuracy.
258MeV shows a meaningful remaining finitepositivity gap:
- HEMISPHERES minimum atN1 is in approximately[0.615461827,0.643711744], N4[0.615461827,0.621803216], N16[0.618376101,0.618553832].
- CAPS minimum atN1 is in approximately[0.053386442,0.088483225], N4[0.053386442,0.069247744], N16[0.060675724,0.061120271].
These paragraph values are nearest-rounded displays; exact/outward8decimal bounds are in evidence/OUTWARD_DISPLAY_BOUNDS.json.
RemainingN16 gaps are approximately0.000177731 and0.000444546 respectively. Do not call either a solved exact minimum.
For330N1, the inner set alone is empty while outer has4vertices. N4 supplies the constructive witness. An inner-only emptiness test would have produced an unjustified exclusion.

## Actual Wolfram result
One newly submitted evaluator call,timeConstraint20s, returned16literalzero identities and12literalTruecontrols; all_zero=True,all_true=True.
Checked cell/chord/normalization/endpoint/oldfolded-map/primitive/Lagrange/stationary/Jensen/Dfloor/subdivision identities and positive/negative/signed analytic controls.
No remoteCPU orremote computationwall was supplied, so both remainnull. Network wall is not a scientificCPU measure.
Current context returned documentation with semanticNoResultsFound, not a numerical result. Earlier EXFOR11contextSERVICE_ERROR remains historical; it was not erased.
The exact submittedcode and rawproviderreply are retained. This symbolic check is not a second optimization or a substitute for the nonauthor review.

## Next discrimination, without starting another loop
A later explicit task could tighten258MeV endpoint-free minimum brackets with a certified exact curved positivity formulation or further declaredresolution. This loop does not add anothermesh, degree or physicalassumption after seeingresults.
Physical input3 remainsopen; no heating/deposition/globalbinding consumer receives a manufactured value.

