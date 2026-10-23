"""Ten frozen IVPs with accepted/report and partial preservation."""
import time
CPU0,WALL0=time.process_time(),time.monotonic()
import argparse,json,traceback
import numpy as np
from scipy.integrate import solve_ivp
from trace_model import *
CASES={1:dict(name='fixedM16_attenuated',kind='fixed',M=16,attenuated=True),2:dict(name='fixedM4_thin',kind='fixed',M=4),
3:dict(name='fixedM8_thin',kind='fixed',M=8),4:dict(name='fixedM16_thin',kind='fixed',M=16),5:dict(name='splitGL8_thin',kind='split',M=8),
6:dict(name='splitGL16_thin',kind='split',M=16),7:dict(name='splitGL32_thin',kind='split',M=32),8:dict(name='splitGL16_secondary_thin',kind='split',M=16,secondary=True),
9:dict(name='bootstrapGL32_standard',bootstrap=True,standard=True),10:dict(name='bootstrapGL32_tight',bootstrap=True)}
R=BASE/'results'
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def validations(m,a,s,boot):
    z=np.column_stack([a,s])
    if boot:
        ck={'F_nonnegative':bool(z[0].min()>=-2e-12),'F_at_most_one':bool(z[0].max()<=1+2e-12),'B_nonnegative':bool(z[1].min()>=-2e-14)}
        return {'checks':ck,'all_pass':all(ck.values()),'F_range':[float(z[0].min()),float(z[0].max())],'B_range':[float(z[1].min()),float(z[1].max())]}
    mass=z[:4].sum(axis=0)-1;cr=CHARGE@z[:4]-CHARGE@m.y0[:4]-z[4]+z[5];er=BIND@z[:4]-BIND@m.y0[:4]+z[6]+z[7]-z[8]
    mx={'mass_residual':float(abs(mass).max()),'charge_residual':float(abs(cr).max()),'event_energy_residual_eV_per_Li':float(abs(er).max())}
    ck={'mass':mx['mass_residual']<=2e-10,'charge':mx['charge_residual']<=2e-10,'event_energy':mx['event_energy_residual_eV_per_Li']<=2e-9,'minimum_raw_fraction':bool(z[:4].min()>=-2e-12)}
    return {'checks':ck,'all_pass':all(ck.values()),'maxima':mx,'minimum_raw_fraction':float(z[:4].min())}
def run_case(i):
    spec=CASES[i].copy();name=spec.pop('name');boot=spec.pop('bootstrap',False);standard=spec.pop('standard',False)
    if (R/(name+'.json')).exists() or (R/(name+'_partial.json')).exists():raise RuntimeError('EXISTING_CASE_NO_AUTOMATIC_RETRY '+name)
    m=Bootstrap() if boot else Trace(**spec);splits=m.splits()
    if boot:rt=np.unique(np.r_[np.linspace(0.,splits[-1],401),splits,m.bath.star]);atol=np.array([2e-12,1e-14])
    else:rt=np.unique(np.r_[m.bath.report_eta[11:],m.rates.endpoint_roots,np.linspace(.44,.74,401)]);atol=np.r_[np.repeat(2e-12,4),np.repeat(2e-11,5),np.repeat(2e-14,m.size-9)]
    rtol=2e-9
    if not standard:rtol/=100;atol/=100
    ts=[float(splits[0])];ys=[m.y0.copy()];samples=np.full((m.size,len(rt)),np.nan);samples[:,rt==splits[0]]=m.y0[:,None]
    meta={'case_id':i,'name':name,'kind':'bootstrap' if boot else spec['kind'],'M':32 if boot else spec['M'],'conditional_bath':'secondary log-PCHIP' if spec.get('secondary') else 'primary log-Hermite',
          'state_size':m.size,'state_labels':['F','B'] if boot else ['LiI','LiII','LiIII','LiIV','CA','CR','Qgas_eV_per_Li','Eesc_eV_per_Li','Eabs_eV_per_Li']+(['tau10ray_'+str(j) for j in range(16)] if spec.get('attenuated') else []),
          'status':'RUNNING','method':'Radau','jacobian':'exact state Jacobian','rtol':rtol,'atol':atol.tolist(),'segments':[],
          'scope':'prescribed thermal/electron bath; no coupled gas/photon trajectory','fixed_ray_endpoint_convention':'donor interior-side source fit, actual-eta energy',
          'requested_worker':'gpt-6.1-sol/high','observed_runtime_identity':'not exposed by tools'}
    cpu,wall=time.process_time(),time.monotonic()
    try:
        for lo,hi in zip(splits[:-1],splits[1:]):
            m.segment=(float(lo),float(hi));sc,sw=time.process_time(),time.monotonic()
            sol=solve_ivp(m.rhs,(lo,hi),ys[-1],method='Radau',jac=m.jac,rtol=rtol,atol=atol,dense_output=True)
            ts.extend(sol.t[1:].tolist());ys.extend(sol.y[:,1:].T.copy());mask=(rt>=lo)&(rt<=sol.t[-1])
            if np.any(mask):samples[:,mask]=sol.sol(rt[mask])
            meta['segments'].append({'lo':float(lo),'hi':float(hi),'last_eta':float(sol.t[-1]),'success':bool(sol.success),'message':sol.message,'accepted_nodes':len(sol.t),'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'solver_CPU_s':time.process_time()-sc,'solver_wall_s':time.monotonic()-sw})
            np.savez_compressed(R/(name+'_partial.npz'),accepted_eta=np.array(ts),accepted_Y=np.array(ys).T,report_eta=rt,report_Y=samples,split_eta=splits)
            meta['CPU_s_so_far']=time.process_time()-cpu;meta['wall_s_so_far']=time.monotonic()-wall;dump(R/(name+'_partial.json'),meta)
            if not sol.success:raise RuntimeError(sol.message)
        accepted=np.array(ys).T
        if not np.all(np.isfinite(samples)):raise RuntimeError('MISSING_OR_NONFINITE_REPORT')
        arrays={'eta':rt,'Y':samples,'accepted_eta':np.array(ts),'accepted_Y':accepted,'split_eta':splits}
        if boot:arrays.update(F=samples[0],B=samples[1])
        else:arrays.update(fractions=samples[:4],mass_residual=samples[:4].sum(axis=0)-1,charge_residual=CHARGE@samples[:4]-CHARGE@m.y0[:4]-samples[4]+samples[5],event_energy_residual_eV_per_Li=BIND@samples[:4]-BIND@m.y0[:4]+samples[6]+samples[7]-samples[8])
        np.savez_compressed(R/(name+'.npz'),**arrays);meta['validation']=validations(m,accepted,samples,boot);meta['status']='COMPLETED' if meta['validation']['all_pass'] else 'VALIDATION_FAILED'
    except Exception:meta['status']='FAILED';meta['exception']=traceback.format_exc()
    meta['CPU_s']=time.process_time()-cpu;meta['wall_s']=time.monotonic()-wall;meta['accepted_nodes_total']=len(ts)
    for k in ['nfev','njev','nlu']:meta[k+'_total']=sum(x[k] for x in meta['segments'])
    dump(R/(name+'.json'),meta);print(json.dumps({k:meta[k] for k in ['case_id','name','status','CPU_s','wall_s','accepted_nodes_total']}),flush=True)
    return meta['status']=='COMPLETED'
def main():
    p=argparse.ArgumentParser();p.add_argument('cases',type=int,nargs='+');a=p.parse_args()
    if not json.loads((R/'preflight.json').read_text())['all_pass']:raise RuntimeError('PREFLIGHT_NOT_PASSED')
    for i in a.cases:
        if not run_case(i):return 1
    return 0
if __name__=='__main__':raise SystemExit(main())

