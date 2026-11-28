"""HE24 first-birth cohort optical-depth controls; exact HE23 source quadrature.
Uses HE23 Verner fits, angular source nodes and original native H-density readback.
These are local/source-conditional diagnostics, not global temporal error bars.
"""
import argparse, json, pathlib, sys, math
import numpy as np

def main():
  p=argparse.ArgumentParser();p.add_argument('--he23-root',type=pathlib.Path,required=True)
  p.add_argument('--replay',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True)
  a=p.parse_args();sys.path.insert(0,str(a.he23_root/'src'))
  from he21_photo import _spectral_nodes, X_END, Hubble, C_CM_S, sigma_cm2, neutral
  gas=np.array([1e-5,1e-5,0.,0.00113]); f=neutral(gas)
  result=[]
  for n in (2,4,8,16,32,64):
    j=json.loads((a.replay/f'q+0.0000_m4_n{n}'/'STATUS.json').read_text())['result']
    nh=j['total_hydrogen_density_cm3'][0]
    mid=(.5)*X_END/n
    mids=(np.arange(n)+.5)*X_END/n
    energy,raw,_,_=_spectral_nodes(4,mid,0.,mids,0.,4,True)
    weights=raw/sum(raw)
    dt=(X_END/n)/Hubble(mid)
    hazard=(C_CM_S*nh*(sigma_cm2(energy)*f).sum(axis=1))*dt
    idx=np.argsort(hazard)
    def weighted_quantile(frac):
       cum=np.cumsum(weights[idx]);return float(hazard[idx[min(len(idx)-1,int(np.searchsorted(cum,frac)))]] )
    obs={'n':n,'dt_s':dt,'nh_cm3':nh,'tau_max':float(hazard.max()),'tau_min':float(hazard.min()),
      'tau_mean_weighted':float(np.dot(weights,hazard)),
      'tau_q50':weighted_quantile(.5),'tau_q90':weighted_quantile(.9),
      'fraction_tau_ge_0_1':float(weights[hazard>=.1].sum()),
      'fraction_tau_ge_1':float(weights[hazard>=1].sum()),
      'fraction_tau_ge_10':float(weights[hazard>=10].sum()),
      'fraction_tau_ge_30':float(weights[hazard>=30].sum()),
      'count_spectral_nodes':int(len(energy))}
    result.append(obs)
    print(json.dumps(obs,sort_keys=True))
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps({'scope':'first cohort, original Verner/50k spectral shape, midpoint neutral initial state, q0,m4','results':result},indent=2)+'\n')
if __name__=='__main__':main()
