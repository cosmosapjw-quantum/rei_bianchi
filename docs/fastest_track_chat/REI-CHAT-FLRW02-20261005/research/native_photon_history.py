#!/usr/bin/env python3
"""E3 controlled photon trajectory; every RHS goes through actual native CLI."""
import argparse,csv,json,subprocess,sys
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Native:
    def __init__(self,exe):
        self.p=subprocess.Popen([str(exe),'photon'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.header=self.p.stdout.readline().strip().split(',');self.calls=0;self.max_inventory=0.
    def eval(self,row):
        self.p.stdin.write(','.join(format(float(v),'.17g') for v in row)+'\n');self.p.stdin.flush()
        line=self.p.stdout.readline()
        if not line:raise RuntimeError(self.p.stderr.read())
        d=dict(zip(self.header,map(float,line.strip().split(','))));self.calls+=1
        scale=sum(abs(d['F'+str(i)]) for i in range(4))+abs(d['source_comoving'])+abs(d['absorption_comoving'])
        self.max_inventory=max(self.max_inventory,abs(d['residual'])/max(scale,1e-290));return d
    def close(self):
        self.p.stdin.close();self.p.wait(timeout=10)
        if self.p.returncode:raise RuntimeError(self.p.stderr.read())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    plan=json.loads(Path(__file__).with_name('INDEPENDENT_EXPERIMENT_PLAN.json').read_text())['E3']
    a0,H,p,end=plan['a0'],plan['H_s'],plan['p'],plan['s_end'];edges=np.array(plan['energy_edges_eV'])
    integrals=(edges[:-1]**(1-p)-edges[1:]**(1-p))/(p-1)
    N0=plan['N0_comoving_cm3']*integrals/integrals.sum();native=Native(args.native)
    def rhs(s,N):
        a=a0*np.exp(s);amplitude=N[0]/integrals[0]
        nE=amplitude*edges**(-p)/a**3
        d=native.eval([a,H,*N,*edges,*nE,0,0,0,0,0,0])
        return np.array([d['dN'+str(i)]/H for i in range(3)])
    results=[];histories=[]
    for steps in [16,32,64]:
        h=end/steps;N=N0.copy();hist=[np.r_[0.,N]]
        for k in range(steps):
            s=k*h;k1=rhs(s,N);k2=rhs(s+h/2,N+h*k1/2);k3=rhs(s+h/2,N+h*k2/2);k4=rhs(s+h,N+h*k3)
            N=N+h*(k1+2*k2+2*k3+k4)/6;hist.append(np.r_[s+h,N])
        hist=np.array(hist);exact=N0[None,:]*np.exp((1-p)*hist[:,0,None]);err=np.max(np.abs(hist[:,1:]-exact)/exact)
        results.append({'method':'RK4','steps':steps,'max_relative_error':float(err),'end_N':N.tolist()});histories.append(hist)
    sample=np.linspace(0,end,101)
    sol=solve_ivp(rhs,(0,end),N0,method='DOP853',rtol=1e-11,atol=1e-20,t_eval=sample)
    if not sol.success:raise RuntimeError(sol.message)
    exact=N0[:,None]*np.exp((1-p)*sample[None,:]);doperr=float(np.max(np.abs(sol.y-exact)/exact))
    native.close();errors=[x['max_relative_error'] for x in results]
    checks={'rk4_monotonic':errors[0]>errors[1]>errors[2],'rk4_finest_below_1e-7':errors[2]<1e-7,'dop853_below_1e-9':doperr<1e-9,'inventory_below_2e-12':native.max_inventory<2e-12}
    args.out.mkdir(parents=True,exist_ok=True)
    with (args.out/'photon_history.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['s_Ht','a','N0_native','N1_native','N2_native','N_total_native','N_total_exact','n_proper_total_native'])
        for i,s in enumerate(sample):w.writerow([s,a0*np.exp(s),*sol.y[:,i],sum(sol.y[:,i]),sum(exact[:,i]),sum(sol.y[:,i])/(a0*np.exp(s))**3])
    fig,ax=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
    ax[0].plot(sample,np.exp((1-p)*sample),color='#18599b',label='Comoving number: exact')
    ax[0].plot(sample[::5],sol.y[:,::5].sum(axis=0)/N0.sum(),'o',markersize=3,color='#c25831',label='Native RHS + DOP853')
    ax[0].plot(sample,np.exp(-(p+2)*sample),'--',color='#53805b',label='Proper density: exact')
    ax[0].set(xlabel=r'$s=Ht$',ylabel='Number / initial number',title='Finite fixed-energy band; p = 3')
    ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
    ax[1].loglog([16,32,64],errors,'o-',color='#18599b',label='RK4, actual native RHS')
    ax[1].loglog([16,64],[errors[0],errors[0]/4**4],':',color='gray',label=r'$\propto n_{step}^{-4}$')
    ax[1].axhline(doperr,color='#c25831',ls='--',label='DOP853 max error')
    ax[1].set(xlabel='Time steps',ylabel='Max relative error',title='Analytic reference and refinement');ax[1].legend(fontsize=8);ax[1].grid(alpha=.2,which='both')
    fig.suptitle('Controlled FLRW photon-number recovery (no absorption, prescribed spectrum)',fontsize=12)
    fig.savefig(args.out/'flrw_photon_recovery.png',dpi=180);fig.savefig(args.out/'flrw_photon_recovery.svg');plt.close(fig)
    out={'experiment':'E3','kind':'exploratory','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'native_rhs_calls':native.calls,'rk4':results,'rk4_error_ratios':[errors[0]/errors[1],errors[1]/errors[2]],'dop853':{'rtol':1e-11,'atol':1e-20,'nfev':sol.nfev,'max_relative_error':doperr},'max_native_inventory_gross_flux_scaled':native.max_inventory,'initial_comoving_bins':N0.tolist(),'physics':plan,'runtime':{'python':sys.version.split()[0],'scipy':scipy.__version__,'numpy':np.__version__}}
    (args.out/'PHOTON_HISTORY_RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return not all(checks.values())
if __name__=='__main__':raise SystemExit(main())
