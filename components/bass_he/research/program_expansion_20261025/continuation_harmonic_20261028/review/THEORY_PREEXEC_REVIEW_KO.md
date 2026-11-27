# HARMONIC10 독립 이론 사전 검토 — pass 1

**판정: PASS_SCOPED_THEORY_PREEXECUTION. 현재 blocking finding 0.**
이는 frozen contract의 수학적 연결과 독립 기준식을 검토한 결과다.
새 코드·실제 suite·Wolfram 원 응답·원 plot에 대한 판정은 같은 pass의 후속 검토로 남는다.
Reviewer는 scientific program, suite, CAS, plot을 실행하지 않았다.

검토 계약 SHA256: `cb2c83dd449100761e564efbc3a44fe1dc9ac4a915e3ab5006cb9c03da012cec`.
AZIMUTH09/KINEMATIC08/APERTURE07 source 본문을 직접 읽었고 파일 identity를 JSON에 기록했다.

## 비음수성과 signed primitive

각 Bernstein 성분에 대해
q_i(t)=b0_i+bc_i cos(4πt)+bs_i sin(4πt) >= b0_i-sqrt(bc_i²+bs_i²)>=0이다.
Bernstein basis는 비음수 partition of unity이므로 전체 밀도 역시 비음수이며
상계 2B0가 성립한다. 전체 적분은 harmonic 평균이0이어서 sigma=2sum(b0)/(n+1)이다.
sigma0은 모든 b0=0과 cone에 따른 bc=bs=0을 뜻한다.

Contract의 cone 밖 양성 예는 rho0=(1+mu²)/2,rhoc=(1-mu²)/4이므로
rho0-|rhoc|=(1+3mu²)/4>0이다. 이것을 certificate-domain 밖으로 분류하는 것은 정확하다.

C primitive의 부호는 sin(h)-sin(l), S primitive는 cos(l)-cos(h)이다.
음의 Ac/As는 interval scalar multiplication의 끝점을 뒤집어 처리해야 한다.
각 harmonic 항을 양의 측도로 보거나 component별 clip하는 절차는 계약에 없다.
결합 밀도에 대한 양성성만 inner/outer set 포함에 사용한다.

## 기하·교환·회전

원 소스는 minus daughter를 F(-mu),(t+1/2)로 처리한다. Patch 중첩은 union이고,
original/shifted endpoints<=64와0/1에서 strip<=65다. Midpoint는 azimuth mask의
정확한 상수 선택이다.

짝대칭 rho_j와 half-turn 주기는 rho(-mu,t+1/2)=rho(mu,t)를 준다.
Coincidence 역시 J 아래 보존되어 odd moment integral_C mu dm=0이다.
그러므로 count2Y,pairenergyGY,각 labelenergyGY/2가 성립한다.

Geometry를 a만큼 회전한 뒤 원 geometry로 당기면 density는 rho(t+a)이다.
직접 삼각함수 전개로 bc'=bc cos4πa+bs sin4πa,
bs'=-bc sin4πa+bs cos4πa를 얻는다. a1/8에서 (bs,-bc)가 맞다.
Geometry와 법칙을 함께 회전할 때 법칙에는 역변환을 써야 한다.

## 독립 oracle 재유도

Full polar antipodal arc 두 개는 w<=1/2에서 경계 외에 겹치지 않는다.
두 arc를 직접 적분하면 contract의 Y 공식과 w1/8의 sine/cosine 조합이 나온다.
동일 full detector는 coincidence sigma,assignment2sigma,overlap sigma이다.
동일 half-circle detector는 coincidence0,both-detectors-hit sigma이다.

비분리 예에서 b_c=(1/2,-1/2,1/2)는 rho_c=mu²/2를 정확히 나타낸다.
Full polar에서는 integral rho_c dmu=1/3이므로 Y=1/4+1/(6π)이다.

Mixed-polar 모델에서 F(mu)>=0 iff mu>=-k, k=40/51이다.
첫 assignment의 mu 구간은[k,1], 둘째는[-1,-k]이고 각 azimuth 길이는1/8이다.
따라서
Y=(1-k)/8+(1-k³)/(12π),
H_A=(1+k)/8+(1+k³)/(12π), H_B=Y다.
Global marginal harmonic1/3으로 대신한 naive 결과와의 차이는
(k-k³)/(12π)>0이므로 이 예가 분리화 오류를 실제로 구별한다.
여기서는 해당 수식을 독립적으로 유도했으며 수치 suite를 실행하지 않았다.

Degree8 계수 (-1)^i/2는 (1-2x)^8/2=mu^8/2이고 짝대칭과 cone 경계 조건을 만족한다.
증가 topology의 주어진8개 interior polar window는 비자명 boundary를 가지므로
실행에서 nonzero boundary bisections를 요구하는 조건은 적절하다.

## 총 오차와52회 경계

Cone에서 |rho_c|,|rho_s|<=rho0이므로 임의 E에 대해 |Ac(E)|,|As(E)|<=sigma다.
한 strip의 inner 또는 outer 적분 interval 폭은 최대2sigma2^-84이고,
두 interval의 합과 P개 strip은 a_num<=4sigmaP2^-84다.

참 outer-inner 적분 차는 모든 primitive membership가 결정되지 않은 영역에만 있으므로
B*a_E 이하이다. Upper outer와 lower inner의 산술 오차를 각 interval 폭으로 감싸면
returned width<=B*a_E+a_num을 얻는다. [0,sigma]와 교차하면 폭은 증가하지 않는다.

B/sigma<=9,N<=8이므로 기본 delta>=1/(1440*2^40)다.
길이2 root bracket에 대해 2/2^52 <=1/(1440*2^40)은2880<=4096과 같아 성립한다.
Fold 시작 길이는1이다. Geometric error sigma2^-41와 arithmetic error
260sigma2^-84의 합은 sigma2^-40보다 작다.
수동 delta, count/energy scaling, conditional ratio는 각각 계약대로 별도로 다뤄야 한다.

## Rational trig certificate

tan(2atan1/5)=5/12, tan(4atan1/5)=120/119이며
tan(4atan1/5-atan1/239)=(28680-119)/(28441+120)=1이다.
각도 범위가 첫 사분면에 있으므로 Machin 식을 얻는다.

Atan alternating remainder는16/(49*5^49)+4/(17*239^17)이다.
2^-96 grid 바깥 반올림의 폭 증가를 더해도 pi.width<2^-94이다.
r<1/4의 argument interval 폭은2^-95보다 작다. Midpoint를2^-96 grid에
내려 반올림한 오차를 더해도 argument_error<2^-94이다.
w<2에서 sin/cos의 유한 Taylor remainder와 derivative bound1을 합하고2^-88
grid로 바깥 반올림하면 제시된 sine/cosine width<2^-86의 보수적 경계가 성립한다.
각 quadrant의 교환/부호 변환은 exact interval operation이어야 한다.

분자 폭은 최대2^-85, 분모4pi>12와 폭<2^-92를 쓰면 C/S의 폭은
2^-85/12+2*2^-92/144보다 작으므로2^-84보다 작다.
동일 phase endpoint의 차는 exact0 shortcut으로 처리해야 full/half arc의
정확0이 유지된다. 이것과 actual width checks는 뒤의 코드·결과 검토 대상이다.

## 보존과 다음 검토

세 물리 입력과 unique population_rest_energy_witness, null thermal ports,
UNASSIGNED birth_pool, global completion null/L4false/production NOT_APPROVED가 보존된다.
이 연구는 선언된 측도 참조이며 strong no-go나 문헌 신규성 성과를 제안하지 않는다.
기존 실패를 재실행하거나 예산을 옮기는 변경도 없다.

이 pass의 다음 행동은 frozen contract에 맞는 implementation/static 검토,
실제 한 suite와 한 CAS의 원 결과, 저장값 plot 원본을 읽고 scoped adoption을 판정하는 것이다.
