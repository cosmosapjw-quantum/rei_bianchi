"""Manufactured algebra checks only; no ODE, IVP, physical rate, or cohort run."""
import cmath
import json
import time
from fractions import Fraction as Q
from pathlib import Path

start = time.process_time()

def model(t, x1, x2, r):
    n1, n2 = r*x1, r*x2
    k, inj = 0.7*(1+t), 0.13*cmath.exp(0.2*t)
    alpha, beta, death = 0.11+0.03*t, 0.05, 0.17
    theta = 0.4+0.02*n2
    s = [-k*n1*n2+inj, k*n1*n2-death*n2]
    ref = alpha*r+beta*n1*n1
    return [(s[0]-x1*ref)/r, (s[1]-x2*ref)/r, ref-theta*r]

t,x1,x2,r=0.6,0.31,0.23,2.7
n1,n2=r*x1,r*x2
x=[x1,x2]
k=0.7*(1+t)
inj=0.13*cmath.exp(0.2*t)
alpha,beta,death=0.11+0.03*t,0.05,0.17
theta=0.4+0.02*n2
S=[-k*n1*n2+inj,k*n1*n2-death*n2]
R=alpha*r+beta*n1*n1
Sn=[[-k*n2,-k*n1],[k*n2,k*n1-death]]
Rn=[2*beta*n1,0.0]
theta_n=[0.0,0.02]
F=model(t,x1,x2,r)
pred=[]
for i in range(2):
    row=[Sn[i][j]-x[i]*Rn[j]-(R/r if i==j else 0.0) for j in range(2)]
    Sh_r=sum(Sn[i][j]*x[j] for j in range(2))
    Rh_r=sum(Rn[j]*x[j] for j in range(2))+alpha
    row.append((Sh_r-x[i]*Rh_r)/r-F[i]/r)
    pred.append(row)
pred.append([r*Rn[j]-r*r*theta_n[j] for j in range(2)]+[sum(Rn[j]*x[j] for j in range(2))+alpha-theta-r*sum(theta_n[j]*x[j] for j in range(2))])
h=1e-30
observed=[]
for i in range(3):
    row=[]
    for j in range(3):
        args=[x1,x2,r];args[j]+=1j*h
        row.append(model(t,*args)[i].imag/h)
    observed.append(row)
errors=[abs(pred[i][j]-observed[i][j]) for i in range(3) for j in range(3)]
St=[-0.7*n1*n2+0.2*inj,0.7*n1*n2]
Rt=0.03*r
expected_t=[(St[i]-x[i]*Rt)/r for i in range(2)]+[Rt]
observed_t=[v.imag/h for v in model(t+1j*h,x1,x2,r)]
time_errors=[abs(a-b) for a,b in zip(expected_t,observed_t)]

# Exact rational thermal cancellation; k_B=1 is a unitless manufactured check.
rr,nt,T,theta0,Qheat,Stot,Rref=Q(5),Q(7),Q(11),Q(2,3),Q(13),Q(3),Q(4)
xt=nt/rr
eth=Q(3,2)*T*xt
dxt=(Stot-xt*Rref)/rr
deth=Qheat/rr-theta0*T*xt-eth*Rref/rr
dT_from_quotient=(deth-Q(3,2)*T*dxt)/(Q(3,2)*xt)
dT_physical=Q(2,3)*Qheat/nt-Q(2,3)*theta0*T-T*Stot/nt
thermal_residual=dT_from_quotient-dT_physical

out={
    'scope':'manufactured algebra only; no IVP or physical-rate evaluation',
    'checks':{
        'dynamic_reference_state_jacobian_max_abs_error':max(errors),
        'partial_time_derivative_max_abs_error':max(time_errors),
        'thermal_reference_cancellation_exact_residual':str(thermal_residual),
        'thermal_temperature_rate_exact':str(dT_physical),
        'omitted_outer_reference_gradient_error_x1x1':abs(x1*Rn[0]),
        'omitted_diagonal_quotient_error':abs(R/r)
    },
    'status':'pass_scoped' if max(errors+time_errors)<1e-13 and thermal_residual==0 else 'fail',
    'cpu_seconds':time.process_time()-start,
    'physics_ivp_runs':0,
    'new83_runs':0,
    'ncp_runs':0
}
Path(__file__).with_name('normalization_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
