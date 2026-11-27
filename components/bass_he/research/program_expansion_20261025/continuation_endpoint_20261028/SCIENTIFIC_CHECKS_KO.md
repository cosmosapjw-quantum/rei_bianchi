# R7/C7 — degree sensitivity와실제기호검산

## 실제구성적결과
사전고정한a=(1411/10000,-1/4,33/25)의정확한rminimum은170627/1320000>0,위치는z=25/264다. q=(1-z)r로양끝q(1)=0이며fullmu표현에서f(-1)=f(1)=0이다. D=14297/52500>0,모든계수box와denominatorfloor를만족한다. 네330MeVnominalDCS창모두interval-certifiedinside=True다. a2=33/25nonzero이므로기존endpointquartic부분가족a2=0의외부에있다.

따라서같은nominaldata창과endpointzero를유지해도degree<=4의inheritedEMPTY와degree<=6의실제feasible은다른결과다. 기존quartic의배제는해당차수조건안에서보존된다. EXFOR11의globalBernstein충분조건cone의EMPTY도그원래cone범위에서보존된다.

## Same-eventgeometry재사용검산
실제K<0를유리수로확인해monotonebranch와C=[-1,-t]union[t,1]의proof조건을확인했다. 저장k0에서복구한threshold로만든기존j=0,1,2monomialmomentbounds는HEMISPHERES/CAPS모두**세성분exactequality=True**였다. 이는새weightedmoment의compatibilitycontrol이며geometryshape를proof없이moment하나로추정한것이아니다. 새preimage/geometry/trigonometrysolvercall은0이다.

N16fullfamily외부포함범위의바깥방향12자리표시는다음과같다.

| Geometry | Physical range enclosure | Minimum-bracket exact width (approx) | Maximum-bracket exact width (approx) |
|---|---|---:|---:|
|HEMISPHERES|[0.747050288674,0.783542448014]|7.696712203527597e-15|4.381139846926824e-15|
|CAPS|[0.317079169073,0.404464291607]|1.422475782906539e-14|1.0097284931301006e-14|
|FULL|[1,1]|0|0|

N1CAPSmaximumbracket폭은0.012228846675262136이며,N4/N16에서는위의약1e-14폭으로감소했다. 두해상도의exact내부/외부정점과결과를보존했다. N16범위전체는허용된angularfamily에서변하는aperture분율의포함범위이고,각endpoint를감싼약1e-14폭은계산certificate정밀도다. 두개념과실험적ERR-S민감도창을구별한다.

## 실제Wolfram평가
새evaluator**1회**,timeConstraint20s에서**14literalzero+16True**,all_literal_zero/all_literal_true=True,isError=false를받았다. 이번응답에는providerwarningmessage가없다. Endpointfactorization,normalization,weightedprimitive,cellBernsteinidentity,candidate완전제곱과normalization,네rationalintervalwindowchecks,H>0/K<0를검산했다.
제출source는CAS_SUBMITTED.wl,원시응답은evidence/WOLFRAM_RAW.json이다. RemoteCPU와remotecomputationwall은제공되지않아null이다. Context1회는documentation와일부semanticNoResultsFound를반환했으며evaluator결과와분리했다. Context원응답은대화tooltranscript에있고로컬status파일은실제관찰요약만기록한다.

## 물리적해석
차수확장은기존끝점배제가modelclosure에의존함을실제증인으로보여준다. 이결과는330MeV의measuredspin/polarizationlaw를선택하지않는다. 새로운absoluteeventnormalization,liquid-Heresponse,photonflux/history,nonthermalbirth/deposition/thermalizationpayload는추가하지않았다. 세physical입력은open이며중앙28/88,HEdelta0와null/offfields를유지한다.
