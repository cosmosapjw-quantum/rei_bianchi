# THEORY09B2A: 연속 cell과 경계값에서 핵 source로의 사상

FINITE_INTERVAL_SOURCE_FAMILY_AND_ERROR_PROPAGATION_CHECKED__PHYSICAL_BOUNDARIES_OPEN. 이전57node중 energy slopes가 이미 있는[8.25,9.75]a0의13개를 사용한다. 새 전자eigen/root solve0이며 두 potential와 signed dipole의 coarse7/fine13 유리계수C1 cubic을 구성했다. Potential는 받은finite-CF slopes의Hermite, dipole는exact rational PCHIP다. Q_BO=1.5Eh, 전하·위상규약은부모와동일하고외삽은거절한다.

6개withheldnode차이와 두선언된polynomial간의Bernstein전체cell상계를구분했다. sup|Vcoarse-Vfine|의보수적상계는입사7.63675907e-9Eh,출사5.90410113e-9Eh,dipole2.33914737e-6 e a0다. 정확분자/분모는ZIP에있다. 이것은참전자곡선오차가아니며actual M4/node/slope error enclosure는null이다.

J0,E=.01Eh,명시적p-alpha nuclear reducedmass mu/me1466.8986035629084의local문제를계산했다. 이mass는이번trial의선택이며source isotope default가아니다. y=(u,u_x/kappa),kappa=sqrt(epsilon/alpha),alpha=me/(2mu),Z'=AZ,Z(b)=I에서모든경계벡터eta에대해qhat=F eta,dhat=d/(e a0),F=dhat e1^T Z다. 원점regular조건/무한원tail을임의로채우지않는다.

G=integral Fdagger F, D=integral(Ffine-Fcoarse)dagger(Ffine-Fcoarse)를실제로계산했다. ||eta||=1인 fine source norm²범위는[1.01335052528e-4,1.16351145529e-4]. 모든같은경계ray에대한상대source차이의극값은sqrt(eigen(D,Gfine))로[4.83682103e-5,5.29185787e-5]다. potential→nuclear wave항만의최대8.01525062e-7, dipole항의최대5.31055543e-5. 서로cross term이있으므로제곱오차를그냥더하지않는다. 수치eigenvalue는outward enclosure가아니다.

actual외부matching B_b가주어지면 N_b=B_b^-dagger B_b^-1, physical energy normalization은1/(pi alpha kappa)*eta^daggerG eta/(eta^daggerN_b eta)다. 현재N_b와inner방향은미정이다. localCauchy norm1을unitincidentflux로부르지않는다. N_b=I를채택해R9.75바깥tail을free로대체하지않는다.

새조건부오차식: Rcal=Ztilde'-AtildeZtilde에서C=Ztilde^-1Z는 C'=B C,B=Ztilde^-1[(A-Atilde)Ztilde-Rcal]를만족한다. Lambda=integral_x^b||B||이면||Z-Ztilde||<=||Ztilde||*(exp(Lambda)-1). actual input/defect envelope가필요하며계산된fine-coarse차이를physicaluncertainty로쓰지않는다.

동일asymptotic outgoing normalization의외부해에는L1(b)-L0(b)=-(1/alpha)integral_b^infty deltaV*(u1/u1b)*(u0/u0b)가성립한다. 안쪽regular문제는반대의+부호다. J0 integrabletail의Volterra K=integral|v|/(alpha*kappa)에서K<ln2면 |L-i*kappa|<=2*kappa*(expK-1)/(2-expK). 실제tailenvelope가없으므로숫자를만들지않는다.

검산: 기호16그룹/27성분(15math+1reportingnorm),counterexample3개. pairedlocalpropagation4설정(Taylor65dps,orders28/40 및DOP853 tolerance2개)만실행했다. 최대Taylor순서차이6.84331e-31; fine G의DOP853차이4.71738e-13,가장작은nuclear-errorGramian의상대차이3.24554e-9. 원물리scattering/native/photonmoment실행0.

첫실행은모든propagation출력을저장한뒤mpmath norm p=F API오류로요약에서종료했다. 명시적sqrt(sumabs²)로고치고저장output SHA/계산kernel AST/입력·계약hash를검증해요약만재실행했다. propagation재실행0. 최초코드·실패로그와반환exit1/0을모두보존한다. 마지막전체correctedwrapper replay는NOT_RUN,tests-after이며independent scientific review/interval certification은아니다.

전체유도25식,실행verifier/13원packet/정확계수/행렬/실패와성공로그는BASS_HE_RCT_THEORY09B2_SOURCE_20261007_v1.zip에있다. Gitprojection만으로전체실행payload가있다고간주하지않는다. archive/cloudidentity는DELIVERY_RECEIPT.json을따른다.

ParentTHEORY09B2partial,truecurveerror/innerregulartrace/outermatching/source&potentialtails/actualsigma및photonmeanOPEN. 다음THEORY09B2B_PHYSICAL_BOUNDARY_AND_TRUE_CURVE_REMAINDERS. 동일finite시험을계속추가하지않고실제missinginput에위식을연결한다. 기존root/TASKS/소비기변경0,baselineOFF,physicalHOLD,source momentsnull,HE-F2globalfalse유지. 최신consumerIGMprovider는HEAD만관측했고F09해소를추론하지않았다.
