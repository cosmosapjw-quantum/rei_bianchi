"""Exact conditional birth moments for the frozen endpoint-zero sextic family."""
from fractions import Fraction as F

A=F('3727.3794118');M=F('1875.61294500');e=F(330)
s=A*A+2*A*e;pstar_c_squared=s/4-M*M
assert pstar_c_squared>0
b_squared=e*e*pstar_c_squared/s
K0=(A+e)/2-M

def rat(x):
    if type(x) is float:raise ValueError('binary float unsupported')
    return F(x)

def validate(coeff):
    a=list(map(rat,coeff))
    if len(a)!=3:raise ValueError('three coefficients required')
    vals=[a[0],sum(a)]
    if a[2]>0:
        z=-a[1]/(2*a[2])
        if 0<z<1:vals.append(a[0]+a[1]*z+a[2]*z*z)
    if min(vals)<0 or not any(a):raise ValueError('negative quadratic or zero density')
    return a

def G(j,t):return 2*((1-t**(2*j+1))/F(2*j+1)-(1-t**(2*j+3))/F(2*j+3))

def signed_sum(coeff,intervals):
    return (sum(c*(lo if c>=0 else hi) for c,(lo,hi) in zip(coeff,intervals)),sum(c*(hi if c>=0 else lo) for c,(lo,hi) in zip(coeff,intervals)))

def calculate(coeff,threshold):
    a=validate(coeff);lo,hi=map(rat,threshold)
    if not 0<=lo<=hi<1:raise ValueError('threshold outside acceptance domain')
    gs=[(G(j,hi),G(j,lo)) for j in range(4)];D=signed_sum(a,gs[:3]);N=signed_sum(a,gs[1:])
    if D[0]<=0:raise ValueError('denominator interval too broad/nonpositive')
    if N[0]<0:raise ValueError('numerator interval too broad/negative')
    ratios=[n/d for n in N for d in D];mu2=(min(ratios),max(ratios));variance=tuple(b_squared*x for x in mu2)
    return {'threshold':list(map(str,(lo,hi))),'Dg':list(map(str,D)),'Ng':list(map(str,N)),'mu_mean':'0','mu_second':list(map(str,mu2)),'daughter_mean_MeV':str(K0),'daughter_variance_MeV2':list(map(str,variance)),'daughter_covariance_MeV2':list(map(str,(-variance[1],-variance[0]))),'daughter_second_MeV2':list(map(str,(K0*K0+variance[0],K0*K0+variance[1]))),'pair_kinetic_total_MeV':str(2*K0),'pair_kinetic_total_variance_MeV2':'0','daughter_count_per_event':2}
