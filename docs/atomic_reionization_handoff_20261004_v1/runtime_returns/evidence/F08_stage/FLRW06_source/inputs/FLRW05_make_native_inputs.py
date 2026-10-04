"""Prepare inputs for existing native public interfaces. Does NOT run Rust."""
import json,pathlib
import numpy as np
from spectral import fit_bin,mean01,rate_moments,fv_rates,THRESHOLDS
ROOT=pathlib.Path(__file__).resolve().parents[1]
HEAD='752e360a80e8622bcbaffae54183258b2e67b810'
MPC_CM=3.085677581491367e24
EV_ERG=1.602176634e-12

def make():
    a=.5;nH=1e-4;nHc=a**3*nH;nabs=[8e-5,5e-6,1e-6];H=5e-14
    specs=[fit_bin(lo,hi,n,n*(lo+(hi-lo)*mean01(l))) for lo,hi,n,l in
           [(13.6,24.59,.05,-2),(24.59,54.42,.008,1),(54.42,100,.001,3)]]
    calls=[];absorption=[]
    for i,b in enumerate(specs):
        e,w=b.quadrature(32,THRESHOLDS);r=rate_moments(b,nabs,32)
        # EXACTLY the units accepted by homogeneous_photo_rates, cMpc^-3.
        nodes=[{'energy_ev':float(E),'n_comoving_per_cmpc3':float(P*nHc*MPC_CM**3)} for E,P in zip(e,w)]
        calls.append({'bin_index':i,'function':'homogeneous_photo_rates','provider':'AtomicProvider::reference()',
          'n':nabs,'mean_scale_factor':a,'nodes':nodes,
          'expected_from_python_NOT_native':{'events_proper_per_cm3_s':(nH*r['count_rate']).tolist(),
           'heat_erg_per_cm3_s':(nH*EV_ERG*r['heat_rate']).tolist(),
           'binding_erg_per_cm3_s':(nH*EV_ERG*r['binding_rate']).tolist(),
           'absorbed_erg_per_cm3_s':float(nH*EV_ERG*r['absorbed_energy_rate'].sum()),
           'photon_loss_comoving_per_cmpc3_s':float(nHc*MPC_CM**3*r['count_rate'].sum())},
          'quadrature_input_error':{'N_per_H':r['quadrature_N']-b.number,'U_eV_per_H':r['quadrature_U']-b.energy}})
        absorption.append(float(nH*r['count_rate'].sum()))
    fv=fv_rates(specs,H,nabs)
    photon_input={'scale_factor':a,'hubble_s':H,'comoving_photons_cm3':[nHc*b.number for b in specs],
      'edge_energy_ev':[b.lo for b in specs]+[specs[-1].hi],
      'edge_n_per_cm3_ev':(nH*fv['trace_per_H_eV']).tolist(),
      'source_proper_cm3_s':[0.,0.,0.],'absorption_proper_cm3_s':absorption}
    payload={'kind':'PREPARED_INPUTS_AND_PYTHON_EXPECTATIONS_NOT_NATIVE_EXECUTION','source_commit':HEAD,
      'homogeneous_photo_rates_blob':'d5aedfd37485b33c82a4cf0ee1d854099a517842',
      'photon_balance_blob':'b25f1ea0d85d7d78b8dfa8b63661423f567a6764',
      'calls':calls,'photon_balance_input':photon_input,
      'photon_balance_expected_from_python':{'comoving_dot_cm3_s':(nHc*fv['dN']).tolist(),
         'proper_dot_cm3_s':(nH*fv['dN']-3*H*nH*np.array([b.number for b in specs])).tolist()},
      'missing_native_capability':'independent bin energy U and its shared stage ledger are not implemented by the existing number-only photon_balance',
      'rate_normalization':'per-H weights times nHc*MPC_CM^3 for old node API, but N*nHc for new PhotonInput',
      'native_calls':0}
    (ROOT/'inputs/NATIVE_CALL_VECTORS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    return {'bins':3,'quadrature_nodes':sum(len(c['nodes']) for c in calls),'native_calls':0}
if __name__=='__main__':print(json.dumps(make()))
