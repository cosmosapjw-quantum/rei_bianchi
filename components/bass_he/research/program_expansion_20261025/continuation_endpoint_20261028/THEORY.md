# ENDPOINT14: endpoint-preserving degree sensitivity and certified aperture bounds

Root derivation,2026-10-28. All scientific inputs and the finite execution scope are fixed in CONTRACT.md. The following arguments apply to the whole true degree-six family, even when a finite outer positivity approximation contains nonphysical surrogate vertices.

## 1. Factorization and the exact model relation
An even sextic f(mu)=b0+b1mu²+b2mu⁴+b3mu⁶ corresponds to q(z),z=mu². If q(1)=0, polynomial division gives a unique quadratic r with q(z)=(1-z)r(z). With r=a0+a1z+a2z² the coefficient map is b=(a0,a1-a0,a2-a1,-a2). For0<=z<1, q>=0 iff r>=0; continuity gives the necessary r(1)>=0. Conversely r>=0 makes q>=0 includingz=1. Degreeatmostfour is equivalent toa2=0. This identifies the inheritedquarticendpointfamily as a literal subsetofT6.

## 2. A containing coefficient box and nonzero normalization
For selected dataangles46,61,87, certifiedintervals arepairwise separatedby g=1/5 and liebelow1/2. Each true selected qvalue is between0and1/2. Hence0<=r(z_i)=q(z_i)/(1-z_i)<=1. Lagrangeinterpolation gives
r(z)=sum_i r(z_i)(z-z_j)(z-z_k)/((z_i-z_j)(z_i-z_k)).
Each denominator hasmagnitude>=g²=1/25; the three numeratorcoefficients haveabsolute bounds(1,2,1). Therefore |a|<=(75,150,75); B=160containsallT6members.

The normalization is
D=integral_-1^1(1-mu²)(a0+a1mu²+a2mu⁴)dmu=(4/3)a0+(4/15)a1+(4/35)a2.
From the coefficientmap, |b1|<=2B,|b2|<=2B,|b3|<=B, giving |f'(mu)|<=18B on[-1,1]. At the nominal87degreepoint, f>=L*=7/50. For delta=L*/(36B), the intervalofradiusdelta liesinside[-1,1] and f>=L*/2there. Nonnegativityeverywhereelseimplies
D>=(2delta)(L*/2)=L*²/(36B)=49/14400000.
Consequently T6 isclosedandbounded inR³, and the aperture ratioiscontinuousonT6. A verifiedwitnessestablishesnonemptiness, henceattainmentofbothminimumandmaximum.

## 3. Certified transformed data rows
ForZ=[zl,zh] containingtheexactnominalz, define c_j=(1-z)z^j,j=0,1,2. OnZsubset[0,1], independentpositivefactorbounds give
c_j in[zl^j(1-zh),zh^j(1-zl)].
Letm_jbethemidpointandw_jthewidth. Foranysigneda in thecontainingbox,
|sum a_jc_j-sum a_jm_j|<=sum|a_j|w_j/2<=Bsumw_j/2=epsilon.
Thus expanded rowsL-epsilon<=m.a<=U+epsilonarenecessaryandcontractedrowsL+epsilon<=m.a<=U-epsilonaresufficient. Allfourdataanglesareused. The intervalfactorproductsneednotbeoptimal; theirprovedcontainmentissufficient.

## 4. Reusing geometry through its proved shape
The inherited physical lab map is
F(mu)=gamma(mu+kappa)/sqrt(1-mu²+gamma²(mu+kappa)²),
where s=A²+2Ae,gamma=(A+e)/sqrt(s),R=(s-4M²)/s,kappa=e/((A+e)sqrt(R)). For H=s-4M²>0 and K=e²-(A+e)²R<0,0<kappa<1. Differentiation gives
F'(mu)=gamma(1+kappa*mu)/(1-mu²+gamma²(mu+kappa)²)^(3/2)>0.
ThusFmaps[-1,1]increasinglyonto[-1,1]. The exactsignsofthepolynomial/rationalH,Kwiththefixedrestenergiesarecheckedinthenewcampaign; no square-rootpreimage searchisneeded.

For detectorwindowsA=[nu0,1],B=[-1,-nu0]andfullazimuth,nu0=0or1/2, letalpha=F^-1(nu0),beta=F^-1(-nu0). AplusandBminusrequiresmu>=alphaandmu>=-beta. The oppositeassignmentrequiresmu<=betaandmu<=-alpha. Their unionisC=[-1,-t]union[t,1],t=max(alpha,-beta). SinceF(0)>0and-nu0<=0,beta<0,sot>=0;surjectivitygivest<=1. Thisisthesame-eventunion,not a product ofindependentprobabilities.

Thezerothmonomialmomentisk0=2(1-t). A savedcertificatek0lo<=k0<=k0hi thereforeimplies
tlo=1-k0hi/2<=t<=1-k0lo/2=thi.
The newweightedbasis(1-mu²)mu^(2j)isnonnegativeon[-1,1],anditsunionmomentis
G_j(t)=2[(1-t^(2j+1))/(2j+1)-(1-t^(2j+3))/(2j+3)].
SinceG'_j(t)=-2(1-t²)t^(2j)<=0,k_jliesin[G_j(thi),G_j(tlo)]. Thiscomputesnewdegree-sixinformationusingtheprovedshapewithoutreexecutingtheoldgeometryalgorithm. Thej=0,1,2unweightedmomentformula2(1-t^(2j+1))/(2j+1)iscomparedtosavedmomentsascompatibilityevidence. Shapeproof,notmereagreementofmoments,justifiestheinference.

## 5. Inner and outer positivity polyhedra
On eachcell[l,h]ofNuniformsubintervals, writez=l+(h-l)t. The quadraticBernsteincontrolsare
beta0=r(l), beta1=a0+a1(l+h)/2+a2*l*h, beta2=r(h),
r(z)=beta0(1-t)²+2beta1*t(1-t)+beta2*t².
Allnonnegativecontrolsare sufficientforr>=0throughoutthecell. Nodalnonnegativityisnecessary. Combinecontracteddata,box,DfloorandcellcontrolsintoPinner_N; combineexpandeddata,box,DfloorandnodesintoPouter_N. Then
Pinner_N subset T6 subset Pouter_N.
ForN1,4,16, subdivisionofcontrolsisaconvexcombinationandoutergridsarenested,soinner1subsetinner4subsetinner16andouter16subsetouter4subsetouter1. Thecodechecksactualfiniteinclusionsusingallverticesandtargetconstraints,withcompleteenumerationprovidedbythenextargument.

## 6. Exhaustive vertex certificates
Eachpolytopeisboundedbythebox. EveryvertexinR³hasthreeindependentactiveconstraintnormals; thisalsoholdsforverticesoflower-dimensionalboundedpolyhedrawhenallambientconstraintsareincluded. Enumeratealltriples, solveeachnonsingularsystemexactly, retainonlycandidatessatisfyingeveryinequality, anddeduplicateexactvectors. Thereforethelistcontainsallvertices. A boundednonemptypolytopehasatleastonevertex; anemptylistafterexhaustioncertifiesemptinessofthatpolytopeonly.
Theindependentreaderchecksrecordedmatrix/RHSconstruction,vertexconstraints,activewitnesses,countsandscientificboundswithoutre-enumerating. Completenessadditionallydependsoninspectionoftheproducer'sexhaustiveloop; itisnotclaimedthatavertexlistaloneprovescompleteness.

## 7. Signed moment bounds and attained witnesses
For eachsigneda,klo<=k<=khi gives
nlo=sum a_j*(klo_j ifa_j>=0 elsekhi_j),
nhi=sum a_j*(khi_j ifa_j>=0 elseklo_j).
nloisconcaveandnhiisconvexina. Ifa=sumlambda_v*vwithlambda_v>=0,sumlambda=1andD(v)>0,thenomega_v=lambda_vD(v)/D(a)areprobabilityweights. Concavitygivesnlo(a)/D(a)>=sumomega_v*nlo(v)/D(v); convexitygivestheoppositeinequalityfornhi. Hence theouterglobalcontainmentrangeis[min_Vout nlo/D,max_Vout nhi/D],optionallyintersectedwith[0,1]forphysicalprobabilities.
Everyinnervertexisatruefeasiblewitness. Thepreselectedrationalcandidate,ifitpassesalltrue-rowchecks,isalsoone. Theirindividualintervalsyieldupperboundsonthetrueminimumandlowerboundsonthetruemaximum. Combiningtheseattainedwitnessboundswithouterboundsbracketseachtrueextremum. Finitebracketgapsremainquantitativeoutput,notassumedzero.

## 8. Constructive degree distinction
Thefixedcandidateadmits
r(z)=(33/25)(z-25/264)²+170627/1320000>0,
soq(z)=(1-z)r(z)>=0andequalstozeroatz=1. Itsnormalizationis14297/52500>0anda2nonzero. Actualnominalwindowmembershipisverifiedusingthecertifiedintervalrows,notroundedcosines. Ifsuccessful,thiswitnessandtheinheritedemptyT4certificateestablishdifferentfeasibilityunderthesamedata/endpointconditionswhendegreeisraisedfromfourtosix.
Thiscomparisondoesnotselectaphysicalmultipolelaw. Itshowswhichpartoftheconditionalexclusiondependsonpolynomialdegree. EXFOR11'sfiniteglobalBernsteinconeemptinessandQUARTIC12'sfullquarticendpointemptinessremainvalidintheirrespectivescopes. Physicalnormalization,mediumresponse,fluxhistoryandnonthermalbindinginputsremainasrecordedinCONTRACT.md.
