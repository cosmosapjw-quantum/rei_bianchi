"""Authority-authorized unchanged BDF replay from saved data, cap3s."""
import json,math,signal,time
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/laneA'
start=time.perf_counter()
def timeout(*_):raise TimeoutError('diagnostic-only3s cap')
signal.signal(signal.SIGALRM,timeout);signal.alarm(3)
data=np.load(OUT/'kinetic_rate_table.npz');interp=PchipInterpolator(data['u'],data['log_rates'],axis=0,extrapolate=False)
history=np.genfromtxt(ROOT/'inputs/laneA/Be_history_be_kinetics_history.csv',delimiter=',',names=True)
F=PchipInterpolator(history['u'],history['Fdecay'],extrapolate=False)
br=json.loads((ROOT/'inputs/laneA/Be_result_BE_KINETICS_RESULT.json').read_text());end=float(data['u'][-1]);out=np.linspace(0,end,1025)
def coefficients(u):
    x=100001*math.exp(-float(u));logs=interp(u);beta=np.exp(logs[:3]);r=br['Ye']*br['nb0_cm-3']*x**3*np.exp(logs[3:6]);hh=br['H0_s-1']*math.sqrt(br['Omega_r']*x**4+br['Omega_m']*x**3+br['Omega_Lambda'])
    b0,b1,b2=beta;r0,r1,r2=r
    return np.array([[-b0,r0,0],[b0,-b1-r0,r1],[-r2,b1-r2,-b2-r1-r2]])/hh,r2/hh

def fun(u,y):
    m,r=coefficients(u);res=np.empty(6);res[:3]=m@y[:3]+np.array([0,0,r]);res[3:]=m@y[3:]+np.array([0,0,r*float(F(u))]);return res

def jac(u,y):
    m,_=coefficients(u);j=np.zeros((6,6));j[:3,:3]=m;j[3:,3:]=m;return j

sol=solve_ivp(fun,(0,end),np.zeros(6),method='BDF',jac=jac,rtol=3e-9,atol=3e-14,t_eval=out,dense_output=True)
np.savez(OUT/'ground_BDF_diagnostic.npz',u=sol.t,states=sol.y,last_internal_u=sol.sol.ts[-1],internal_breakpoints=sol.sol.ts)
result={'success':sol.success,'status':sol.status,'message':sol.message,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'last_output_u':float(sol.t[-1]),'time_reached_u':float(sol.sol.ts[-1]),'last_dense_state':sol.sol(sol.sol.ts[-1]).tolist(),'wall_seconds':time.perf_counter()-start,'original_measured_elapsed':'UNKNOWN','original_conservative_accounting_debit_seconds':3,'remaining_accounting_before_diagnostic_seconds':27,'cap_seconds':3,'settings_unchanged':True,'quadrature_repeated':False,'production_repeated':False}
signal.alarm(0)
(OUT/'BDF_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
