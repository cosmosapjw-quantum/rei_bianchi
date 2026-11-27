"""HE24: fixed-opacity continuous-emission vs HE23 midpoint-birth source cohort.
Source conditioned on identical original HE23 BB50K/Verner quadrature and original
native density readback. Not a replacement for coupled Case-A or a global error bar.
"""
import argparse, json, pathlib, sys
import numpy as np

def phi1_minus(tau):
    tau=np.asarray(tau,dtype=float)
    if not(np.all(np.isfinite(tau)) and np.all(tau>=0)):
        raise ValueError('HE24_TAU_NONNEGATIVE_FINITE')
    out=np.empty_like(tau)
    small=tau<1e-5
    a=tau[small]
    out[small]=1-a/2+a*a/6-a**3/24+a**4/120-a**5/720
    v=tau[~small]
    out[~small]=-np.expm1(-v)/v
    return out

def events(tau, weights, species_lam, energy, binding):
    """Each source photon is born uniform across fixed-gas proper step (or at start).
    A_i counts per emitted photon, heat_i eV per emitted photon. No chemistry.
    """
    lam_total=species_lam.sum(axis=1)
    frac=np.divide(species_lam,lam_total[:,None],out=np.zeros_like(species_lam),where=lam_total[:,None]>0)
    old=np.exp(-tau)
    uniform=phi1_minus(tau)
    a_old=weights*(1-old)
    a_uniform=weights*(1-uniform)
    A_old=(a_old[:,None]*frac).sum(axis=0)
    A_uniform=(a_uniform[:,None]*frac).sum(axis=0)
    heat_old=(a_old[:,None]*frac*(energy[:,None]-binding[None,:])).sum(axis=0)
    heat_uniform=(a_uniform[:,None]*frac*(energy[:,None]-binding[None,:])).sum(axis=0)
    return {'absorbed_midpoint':A_old,'absorbed_uniform':A_uniform,
            'heat_midpoint':heat_old,'heat_uniform':heat_uniform,
            'surviving_midpoint':float(np.dot(weights,old)),
            'surviving_uniform':float(np.dot(weights,uniform))}

def compute(he23_root, replay_root):
    sys.path.insert(0,str(he23_root/'src'))
    from he21_photo import _spectral_nodes,X_END,Hubble,C_CM_S,sigma_cm2,neutral,BIND_EV
    frac=neutral(np.array([1e-5,1e-5,0.,0.00113]))
    results=[]
    for n in (2,4,8,16,32,64):
        run=json.loads((replay_root/f'q+0.0000_m4_n{n}'/'STATUS.json').read_text())['result']
        nh=run['total_hydrogen_density_cm3'][0]
        xmid=.5*X_END/n
        step_mids=(np.arange(n)+.5)*X_END/n
        energy,raw,low,high=_spectral_nodes(4,xmid,0.,step_mids,0.,4,True)
        w=raw/raw.sum()
        dt=(X_END/n)/Hubble(xmid)
        rates=C_CM_S*nh*sigma_cm2(energy)*frac[None,:]
        tau=rates.sum(axis=1)*dt
        e=events(tau,w,rates,energy,BIND_EV)
        bias=e['absorbed_midpoint']-e['absorbed_uniform']
        obs={'n':n,'dt_s':dt,'weighted_tau':float(np.dot(w,tau)),
            'surviving_midpoint':e['surviving_midpoint'],
            'surviving_uniform':e['surviving_uniform'],
            'absorbed_midpoint':e['absorbed_midpoint'].tolist(),
            'absorbed_uniform':e['absorbed_uniform'].tolist(),
            'overabsorbed_total_fraction_of_emission':float(bias.sum()),
            'overabsorbed_species':bias.tolist(),
            'heat_midpoint_eV_per_emitted_photon':e['heat_midpoint'].tolist(),
            'heat_uniform_eV_per_emitted_photon':e['heat_uniform'].tolist(),
            'fraction_tau_ge_1':float(w[tau>=1].sum()),
            'n_spectral_nodes':len(energy),
            'number_ledger_midpoint':float(e['surviving_midpoint']+e['absorbed_midpoint'].sum()-1),
            'number_ledger_uniform':float(e['surviving_uniform']+e['absorbed_uniform'].sum()-1)}
        results.append(obs)
    return {'schema':'BASS_HE.HE24.first_cohort_uniform_source.v1',
            'source':'actual HE23 frozen first midpoint native total n_H(a), BB50K+Verner source quadrature',
            'assumption':'fixed gas, fixed local E, uniform proper-time source inside step; comparison to HE23 full-step instantaneous newborn injection; no old cohorts or chemistry response',
            'results':results}

def main():
    p=argparse.ArgumentParser();p.add_argument('--he23-root',type=pathlib.Path,required=True);p.add_argument('--replay',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True)
    a=p.parse_args()
    result=compute(a.he23_root,a.replay)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for r in result['results']:
        print(r['n'],round(r['weighted_tau'],4),round(r['surviving_midpoint'],7),round(r['surviving_uniform'],7),round(r['overabsorbed_total_fraction_of_emission'],7))
if __name__=='__main__':main()
