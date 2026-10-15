"""C7 independent proper-time source-free q-ray / expanding-density ODE.
Uses physical owner H(a,q) and b(a,q) with manufactured HeII-only absorber.
It does not evolve ionization fractions or gas temperature.
"""
import sys,json,math
from pathlib import Path
from scipy.integrate import solve_ivp,quad
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/"research/source07_c1_baseline_20261014"))
from q_emission_baseline import Scenario
sc=Scenario(root)
a0=sc.ar
xmax=1.0e-5
mu0=0.60
E0=54.4203
chi=54.42;bind=54.41776
n0=2.0e-7 # cm^-3, manufactured HeII-only absorber proper density at a0
c=29979245800.
def sigma(E):
 if E<chi:return 0.
 e0,s0,ya,p=1.72,1.369e4,32.88,2.963
 x=E/e0;y=abs(x)
 return s0*(x-1)**2*y**(p/2-5.5)*(1+math.sqrt(y/ya))**(-p)*1e-18
def physics(x,q):
 a=a0*math.exp(x)
 b=sc.b(a,q)
 xper=(1-mu0**2)*math.exp(2*b)
 xpar=mu0**2*math.exp(-4*b)
 normal=xper+xpar
 energy=E0*math.exp(-x)*math.sqrt(normal)
 muzsq=xpar/normal
 H=sc.hubble(a,q)
 shear=sc.shear(a,q)
 eff=1+(shear/H)*(3*muzsq-1)
 return energy,H,eff
cases=[]
for q in (-.01,0.,.01):
 crossing=0.0
 def rate(x,constant=False):
  energy,H,eff=physics(x,q)
  n=n0 if constant else n0*math.exp(-3*x)
  return c*n*sigma(energy)/H
 def rhs(x,y):
  n,absorb,heat,work=y
  energy,H,eff=physics(x,q)
  activity=rate(x)*n
  return [-activity,activity,activity*(energy-bind),n*energy*eff]
 sol=solve_ivp(rhs,(0,xmax),[1.,0.,0.,0.],method="DOP853",rtol=2e-12,atol=3e-15,dense_output=True)
 assert sol.success
 n,a,heat,work=(float(x) for x in sol.y[:,-1])
 finalE=physics(xmax,q)[0]
 e0_res=E0-(n*finalE+a*bind+heat+work)
 dt=quad(lambda x:1/sc.hubble(a0*math.exp(x),q),0,xmax,epsabs=1e-8,epsrel=5e-13)[0]
 # Contrast constant-opacity/gas and same exact photons/geometric redshift.
 rates=quad(lambda x:rate(x,constant=False),0,xmax,epsabs=1e-10,epsrel=1e-10,points=[0,xmax])[0]
 cases.append({"q_ref":q,"proper_time_s":dt,"N_final":n,"absorbed_per_initial_photon":a,"heat_ev_per_initial_photon":heat,
               "cosmological_work_ev_per_initial_photon":work,
               "energy_end_ev":finalE,"energy_ledger_residual_ev":e0_res,
               "integrated_opacity":rates,
               "first_order_survival_check":n-math.exp(-rates),
               "fixed_initial_gas_overshoot":quad(lambda x:rate(x,constant=True),0,xmax,epsabs=1e-10)[0]-rates})
assert all(abs(z["energy_ledger_residual_ev"])<5e-8 for z in cases)
jsonpath=Path(__file__).parent/"evidence/VARIABLE_BACKGROUND_REFERENCE.json"
jsonpath.write_text(json.dumps({"scenario":sc.data["scenario_id"],"source_free":"true","gas":"manufactured frozen ion fractions, density expands as a^-3", "HeII_fit_threshold_eV":chi,
    "initial_photon_energy_eV":E0,"xmax_ln_a":xmax,"cases":cases},indent=2))
print(json.dumps(cases,indent=2))
