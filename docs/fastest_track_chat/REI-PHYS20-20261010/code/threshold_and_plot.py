#!/usr/bin/env python3
"""One smoothness counterexample and a plot of existing directional evidence."""
import argparse
import json
from pathlib import Path
import numpy as np


def cusp_coefficient(epsilon, n=48):
    # Exact positive-domain boundaries for r>1; using expm1 avoids subtracting
    # two almost equal energies. This is an isotropic E_FLRW=threshold line,
    # and is deliberately NOT the actual 13.7 eV FT03 initial spectrum.
    eps=np.longdouble(epsilon)
    mu,wmu=np.polynomial.legendre.leggauss(n)
    xp,wp=np.polynomial.legendre.leggauss(n)
    mu,wmu,xp,wp=(np.asarray(a,dtype=np.longdouble) for a in (mu,wmu,xp,wp))
    pi=np.longdouble(str(np.pi))
    phi0=np.arcsin(1/np.sqrt(1+np.exp(2*eps)))
    half=(pi-2*phi0)/2
    phi=pi/2+half*xp
    delta=(1-mu[:,None]**2)*(np.cos(phi)[None,:]**2*np.expm1(-2*eps)+np.sin(phi)[None,:]**2*np.expm1(2*eps))
    rminus=delta/(np.sqrt(1+delta)+1)
    # Two identical positive phi intervals, each of length pi-2phi0.
    integral=np.sum(wmu[:,None]*wp[None,:]*rminus)*half*2/(4*pi)
    return float(integral/eps)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--kernel',required=True,type=Path)
    ap.add_argument('--fig-dir',required=True,type=Path)
    a=ap.parse_args()
    if a.output.exists(): raise SystemExit('Output exists; choose a new path.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    eps=[1e-2,1e-3,1e-4,1e-5,5e-6]
    cs=[cusp_coefficient(e) for e in eps]
    limit=2/(3*np.pi)
    extrap=2*cs[-1]-cs[-2]
    discrepancy=abs(extrap-limit)
    convergence=all(abs(cs[i+1]-limit)<abs(cs[i]-limit) for i in range(len(cs)-1))
    checks=[{'name':'cusp_linear_abs_epsilon_limit','pass':discrepancy<1e-9,'absolute_discrepancy':discrepancy},
            {'name':'one_sided_convergence_to_exact_coefficient','pass':convergence}]
    a.output.write_text(json.dumps({'task':'REI-PHYS20-20261010','role':'THRESHOLD_COUNTEREXAMPLE_NOT_ACTUAL_FT03_LINE',
      'E_threshold_units':1,'response':'(E-E_threshold)_+','shear_eigenvalues':'(+epsilon,-epsilon,0)',
      'method':'physical birth angle GL48x48; exact positive-phi domain; longdouble stable r-1',
      'expected_coefficient':'2/(3*pi)','expected_numeric':limit,
      'values':[{'abs_epsilon':e,'mean_positive_energy_over_abs_epsilon':c} for e,c in zip(eps,cs)],
      'linear_richardson_limit':extrap,'checks':checks,'failure_count':sum(not x['pass'] for x in checks),
      'rigorous_enclosure':False,'native_IVP_old_proofs':0},indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    k=json.loads(a.kernel.read_text())
    rec=next(r for r in k['records'] if r['birth_s']=='0' and r['direction']=='x_axis')
    v=rec['analytic_first_variation']
    phi=np.linspace(0,360,361)
    quadr=np.cos(np.deg2rad(2*phi))
    fig,axs=plt.subplots(1,2,figsize=(11.6,4.5),sharex=True)
    colors=['#235789','#c45b27']
    for ax,stem,scale,title in [(axs[0],'event',1e7,'Absorption event rate'),(axs[1],'heat',1e5,'Primary heating rate')]:
        ax.plot(phi,float(v['delta_log_'+stem+'_per_photon'])*quadr*scale,color=colors[0],lw=2,label='Per emitted photon')
        ax.plot(phi,float(v['delta_log_observed_angle_'+stem])*quadr*scale,color=colors[1],lw=2,ls='--',label='Per present solid angle')
        ax.axhline(0,c='0.4',lw=.7)
        ax.set(xlim=(0,360),xticks=[0,90,180,270,360],xlabel=r'Equatorial azimuth $\varphi$ (degrees)',title=title,
               ylabel=fr'First-order fractional change $\times 10^{{{int(np.log10(scale))}}}$')
        ax.grid(alpha=.2)
        ax.legend(frameon=False,fontsize=9)
    fig.suptitle('Bianchi-I directional response — frozen-neutral-fraction diagnostic',fontsize=13)
    fig.text(.5,.02,r'$E_b=13.7\ \mathrm{eV}$, $b=0$, $t=1.25\times10^9\ \mathrm{s}$, $(H_x-H,H_y-H,H_z-H)=(1,-1,0)\times10^{-16}\ \mathrm{s}^{-1}$',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.075,1,.94])
    a.fig_dir.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.fig_dir/'PHYS20_directional_response.png',dpi=180)
    fig.savefig(a.fig_dir/'PHYS20_directional_response.pdf')
    plt.close(fig)
    print(json.dumps({'cusp_checks':len(checks),'failures':sum(not x['pass'] for x in checks),'cusp_extrap_abs_difference':discrepancy,'figure_directory':str(a.fig_dir)}))
    if not all(c['pass'] for c in checks): raise SystemExit(1)


if __name__=='__main__':main()
