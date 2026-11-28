"""R19 report figures. Exact 105 K source row, synthetic initial densities.
No inferred observational uncertainty, reverse rate or physical Bianchi history.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_nominal_exchange_r19_20261029.src.nominal_exchange import (
    flow_nominal, flow_constant_expansion, source_rhs)
ROOT=Path(__file__).resolve().parents[3]
PDF=Path(os.environ.get('WU_R19_SOURCE_PDF',ROOT/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'))
OUT=Path(__file__).resolve().parent

def run():
    grid=load_native_grid(PDF)
    t=np.linspace(0,3e10,180)
    n0=(1e6,1e6,0,0)
    states=np.array([flow_nominal(grid,n0,float(s)).state_m3 for s in t])
    fig,ax=plt.subplots(figsize=(7.6,4.8))
    ax.plot(t/1e10,states[:,0]/1e6,label='H+ = HD(0,2)')
    ax.plot(t/1e10,states[:,2]/1e6,label='D+ = H2(0,1)')
    ax.set(xlabel='Proper time / 10^10 s',ylabel='Number density / 10^6 m^-3',
           title='105 K printed SQM rate: isolated forward exchange')
    ax.legend();ax.grid(alpha=0.25)
    fig.text(.02,.01,'Synthetic nH+=nHD=10^6 m^-3; no physical rate uncertainty or thermal history',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    for ext in ('png','svg'):fig.savefig(OUT/f'R19_POPULATIONS.{ext}',dpi=190)
    plt.close(fig)
    theta=1e-11
    sol=solve_ivp(lambda s,y: source_rhs(grid,y,expansion_theta_s=theta),
                  (0,2e10),np.array([1e6,2e6,2e5,3e5]),method='DOP853',
                  rtol=2e-12,atol=1e-7,dense_output=True)
    assert sol.success
    ts=np.linspace(0,2e10,61)
    numerical=sol.sol(ts).T
    reference=np.array([flow_constant_expansion(grid,(1e6,2e6,2e5,3e5),float(s),theta).state_m3 for s in ts])
    residual=np.max(abs(numerical-reference),axis=1)
    fig,ax=plt.subplots(figsize=(7.6,4.8))
    ax.semilogy(ts/1e10,np.maximum(residual,1e-12),label='max_i |solve_ivp - exact flow|')
    ax.axhline(5e-5,ls='--',label='declared absolute check 5e-5 m^-3')
    ax.set(xlabel='Proper time / 10^10 s',ylabel='Absolute number-density difference [m^-3]',
           title='Numerical residual for prescribed theta = 10^-11 s^-1')
    ax.grid(alpha=.25);ax.legend()
    fig.text(.02,.01,'Independent DOP853 comparison, not physical/source uncertainty; fixed 105 K bath',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    for ext in ('png','svg'):fig.savefig(OUT/f'R19_NUMERICAL_RESIDUAL.{ext}',dpi=190)
    plt.close(fig)
    return {'schema':'wu.r19.figure_execution.v1','source_pdf_sha':grid.source_sha256,
            'synthetic_initial_m_minus3':list(n0),'theta_s_inverse':theta,
            'max_residual_m_minus3':float(residual.max()),'tolerance_m_minus3':5e-5,
            'nfev':sol.nfev,'output_files':['R19_POPULATIONS.png','R19_POPULATIONS.svg',
                                            'R19_NUMERICAL_RESIDUAL.png','R19_NUMERICAL_RESIDUAL.svg'],
            'figure_claim':'scoped nominal toy, no rate uncertainty band'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
