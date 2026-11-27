# B2: West82 원문 결속과 높은 부분파 reference

## 1. Source와 자체 계산의 경계

원문은 West–Lane–Cohen PRA26(1982)3164–3169, DOI10.1103/PhysRevA.26.3164다.
PDF4쪽 TableI는25개 (E_cm,ell,v) 공명 위치/assignment이며 sigma, resonance width, peak area가 아니다.
Fig1 전자에너지는Ry, Fig2의 gap은Hartree, Fig3의A는atomic inverse time, Fig4–6의sigma는a0²다.
서로 다른 units를 하나의atomic-unit태그로 합치지 않는다. source의Morse fit계수는 본문에 없다.
Ell 최대48, 16개label이기존ell32지원범위밖이다. 이는코드지원gap이며 각partial의물리적기여크기를알려주지는않는다.

## 2. 전자 source에서 radial 입력까지

kappa=e²/(4*pi*epsilon0), a0=hbar²/(me*kappa), Eh=me*kappa²/hbar², ta=hbar/Eh.
Rbar=R/a0, e_u=E_2psigma/Eh, e_l=E_1ssigma/Eh, dbar=d/(e*a0).
West Eq5: V/Eh=e_u-e_H1s+2/Rbar. 전자solver가핵반발을제외하면이를한번만더한다.
Eq6: A*ta=(4/(3*cbar³))*(e_u-e_l)³*|dbar|², cbar=c*ta/a0.
SI: A=(DeltaE)³ |d|²/(3*pi*epsilon0*hbar⁴*c³); Gamma=hbar*A;
W=V-i*Gamma/2. Eq6의atomic A숫자는Gamma/Eh와같지만그물리단위는같지않다.
Ry gap을Hartree숫자로잘못읽으면동일dipole에서A를8배로만든다.
이함수는주어진전자입력의변환이며 실제R격자의V/A를발명하지않는다.
원Eq11 k²[a0^-2]=mu[me]*E_cm[eV]/13.602를별도함수에그대로보존한다.
현대적일반정의k²*a0²=2(mu/me)(E/Eh)와이를자동혼합하지않는다.
B1무차원단위L=a0,E0=Eh/(2mu/me)에서는epsilon=2mu_bar*Ebar,V0=2mu_bar*Vbar,g=2mu_bar*Abar.

## 3. 원점 정칙해의정규화

첫구간[0,a]에상수V,g와q²=epsilon-V+i*g/2를선언한다. radial방정식은
u''+[q²-ell(ell+1)/x²]u=0이고정칙해는
u=x^(ell+1)*0F1(;ell+3/2;-q²x²/4).
계수 c_n=(-q²/4)^n/[n!(ell+3/2)_n]는
2n(2ell+2n+1)c_n+q²c_(n-1)=0을만족한다. 이식이급수해와정칙성을고정한다.
작은a,높은ell에서a^(ell+1)은underflow하거나인공scale거절을일으킨다.
동일연산자의해를a^(ell+1)로나눈w=(x/a)^(ell+1)F로대신한다.
w'=(ell+1)/a*(x/a)^ell*F-q²*x/(2b)*(x/a)^(ell+1)*F_next, b=ell+3/2.
아예a^(ell+1)을형성하지않으므로그정규화에의한범위오류가사라진다.
해의상수배는S와정규화된양의flux를바꾸지않는다. 원점근방을잘라내는근사가아니다.
이결과는상수/유한첫셀에대한식이며실제Coulomb핵반발2/R을정확히처리하는Frobenius해는아직아니다.

## 4. 양의flux의입사정규화

B1에서유도한P=J/(2k|C_in|²), J=int g|u|²dx를그대로사용한다.
외부Riccati-Bessel표현에서D=alpha+i beta=2 C_in(위상무관)이면P=2J/(k|D|²).
높은부분파/작은ka에서|D|²를직접형성할때넘칠수있다. J>0에대해
logP=log2+logJ-logk-2log|D|를평가하고, J=0은정확히0으로둔다.
최종양의P조차binary64에서표현할수없으면명시적NumericalFailure다. 0인물리source로치환하지않는다.
1-|S|²는여전히독립적인절대flux-defect진단이며희귀손실의기본값이아니다.
남은수치위험: 내부장벽/특수함수의큰인수,아주강한흡수,정칙해의node주변조건수,실제long-range경계.
이들이모든매개변수에서해결된productionlog-derivative/Jostsolver라고부르지않는다.

## 5. 광자에너지와상충source

West본문은방출스펙트럼계산을우회해총RCT를얻는다고명시한다. A만으로스펙트럼이나열/반동moment는정해지지않는다.
수직전자gap을광자한개의에너지로고정해정확한출사moment라고부르지않는다.
별도원격RATE작업은GM25 AppendixB.3의200–10000K근사식을가지며이는West의인쇄식/표가아니다.
새원문접근은그근사식과Westcurve를독립재적분해일치시킨것이아니다.

## 6. 검증범위

고유49개pytest와별도18complex-square-well+3rare-loss+2small-origin사례.
독립110digit mpmath Besselmatching은정해진제조연산자의S와P를검사한다.
sourceTable의공명위치와계산된공명위치를비교한것은아니다. source V/A입력이없으므로물리재계산0개.
Wolfram은정칙급수recurrence n1..5,영q도함수,logflux항등식을검산했으며독립심사를대체하지않는다.
