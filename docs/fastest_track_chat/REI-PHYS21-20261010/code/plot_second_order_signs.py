#!/usr/bin/env python3
"""Plot the derived PHYS21 inverse-cube diagnostic, without any gas solve."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-dir',type=Path,required=True)
    a=ap.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    paths=[a.output_dir/('PHYS21_scalar_signs.'+ext) for ext in ['png','pdf','json']]
    if any(p.exists() for p in paths):raise SystemExit('Figure output exists; choose a new directory.')
    tau=np.linspace(0,5,501)
    absorption=3*tau*(tau-4)/10
    heating=3*tau*tau/10-2*tau/5-8/15
    heat_zero=2*(1+np.sqrt(5))/3
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8.2,5.2),layout='constrained')
    ax.axhline(0,color='#5b6573',linewidth=1)
    ax.plot(tau,absorption,color='#2459a6',linewidth=2.5,label=r'Endpoint absorption: $P\lambda$')
    ax.plot(tau,heating,color='#bd5a25',linewidth=2.5,label=r'Primary heating: $P\lambda(E-\chi)$')
    for x,col in [(heat_zero,'#bd5a25'),(4,'#2459a6')]:
        ax.axvline(x,color=col,linestyle=':',linewidth=1.1,alpha=.75)
        ax.scatter([x],[0],s=38,color=col,zorder=5)
    ax.annotate(r'$\tau_Q=\frac{2}{3}(1+\sqrt{5})\simeq2.157$',xy=(heat_zero,0),xytext=(.35,1.7),
                color='#a34c20',arrowprops={'arrowstyle':'-','color':'#bd5a25','linewidth':.8})
    ax.annotate(r'$\tau_A=4$',xy=(4,0),xytext=(4.16,-.78),
                color='#2459a6',arrowprops={'arrowstyle':'-','color':'#2459a6','linewidth':.8})
    ax.scatter([.25,4],[-59/96,8/3],color='#bd5a25',s=25,zorder=5)
    ax.set(xlim=(0,5),ylim=(-1.5,5.3),xlabel=r'Baseline absorption optical depth $\tau=\lambda_0 T$',
           ylabel=r'Quadratic scalar coefficient $[\epsilon^2]\langle K\rangle/K_0$')
    ax.set_title('Scalar response depends on opacity memory',loc='left',fontweight='bold',pad=14)
    ax.grid(axis='y',alpha=.17)
    ax.legend(loc='upper left',frameon=False)
    fig.supxlabel(r'Fixed gas, $H=0$, $\sigma(E)\propto E^{-3}$, $E_b=2\chi$; '
                  r'$\Delta B(s,b)=(s-b)\,\mathrm{diag}(1,-1,0)/T$',fontsize=9)
    fig.savefig(paths[0],dpi=190)
    fig.savefig(paths[1])
    plt.close(fig)
    data={'task':'REI-PHYS21-20261010','kind':'analytic_power_law_diagnostic_curves','coefficient_convention':'epsilon^2; half of second derivative',
          'conditions':['fixed gas','H=0','constant baseline opacity','inverse-cube opacity over the full path','E_birth=2*chi','Delta B=((s-b)/T)*diag(1,-1,0)'],
          'absorption_formula':'3*tau*(tau-4)/10','heating_formula':'3*tau^2/10-2*tau/5-8/15',
          'positive_heat_zero':'2*(1+sqrt(5))/3','heat_zero_numeric':float(heat_zero),'absorption_positive_zero':4,
          'not_actual_FT03_gas_history':True,'native_runs':0,'gas_IVP_runs':0}
    paths[2].write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'figures':[str(p) for p in paths],'gas_IVP_runs':0}))


if __name__=='__main__':main()
