"""Independent 80-digit finite-node oracle. Never labels output native."""
from pathlib import Path
import json, math, copy
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
C=29979245800.0; MPC=3.085677581491367e24; EV=1.602176634e-12
mp.mp.dps=80
DATA=json.loads((ROOT/'inputs/FLRW05_SELECTED_VERNER_ROWS.json').read_text())

def M(x):
    # Exactly the real value of the binary64 supplied to Rust, not an invented
    # higher precision value obtained by interpreting a shortened decimal.
    x=float(x)
    if not math.isfinite(x):raise ValueError('NONFINITE')
    p,q=x.as_integer_ratio();return mp.mpf(p)/q

def sigma(a,E):
    E=M(E);eth,emax,e0,s0,ya,p,yw,y0,y1=map(M,DATA['rows'][a])
    if E<0 or E>emax:raise ValueError('ENERGY_DOMAIN')
    if E<eth:return mp.mpf(0)
    x=E/e0-y0;y=mp.sqrt(x*x+y1*y1)
    return s0*((x-1)**2+yw*yw)*mp.exp((p/2-M(5.5))*mp.log(y)-p*mp.log1p(mp.sqrt(y/ya)))*M(1e-18)

def photo_oracle(case):
    a=M(case['mean_scale_factor']);n=list(map(M,case['n']))
    vol=(a*M(MPC))**3
    gamma=[mp.mpf(0)]*3;events=gamma.copy();heat=gamma.copy();binding=gamma.copy();energy=gamma.copy()
    for node in case['nodes']:
        e=M(node['energy_ev']);ng=M(node['n_comoving_per_cmpc3'])/vol
        for s in range(3):
            g=M(C)*ng*sigma(s,node['energy_ev']);v=n[s]*g;chi=M(DATA['binding_ev'][s])
            gamma[s]+=g;events[s]+=v;heat[s]+=v*(e-chi)*M(EV);binding[s]+=v*chi*M(EV);energy[s]+=v*e*M(EV)
    return {'gamma':gamma,'events':events,'heat':heat,'binding':binding,
            'absorbed_species':energy,'absorbed':sum(energy),'loss_comoving':vol*sum(events)}

def photon_oracle(inp,absorption):
    a=M(inp['scale_factor']);H=M(inp['hubble_s']);a3=a**3
    flux=[a3*H*M(e)*M(n) for e,n in zip(inp['edge_energy_ev'],inp['edge_n_per_cm3_ev'])]
    dc=[a3*(M(inp['source_proper_cm3_s'][g])-absorption[g])+flux[g+1]-flux[g] for g in range(3)]
    dp=[dc[g]/a3-3*H*M(inp['comoving_photons_cm3'][g])/a3 for g in range(3)]
    return {'dc':dc,'dp':dp,'flux':flux,'loss':flux[0]-flux[3],
            'source':a3*sum(map(M,inp['source_proper_cm3_s'])),'absorption':a3*sum(absorption),'residual':sum(dc)-a3*sum(map(M,inp['source_proper_cm3_s']))+a3*sum(absorption)+flux[0]-flux[3]}

def encode(x):
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    if isinstance(x,mp.mpf):return mp.nstr(x,65)
    return x

def main():
    base=json.loads((ROOT/'inputs/FLRW05_NATIVE_CALL_VECTORS.json').read_text())
    cases=[]
    for i,c in enumerate(base['calls']):
        cases.append({'id':f'bin{i}','mean_scale_factor':c['mean_scale_factor'],'n':c['n'],'nodes':c['nodes']})
    joined=copy.deepcopy(cases[0]);joined['id']='joined96';joined['nodes']=sum([c['nodes'] for c in cases],[]);cases.append(joined)
    rev=copy.deepcopy(joined);rev['id']='reversed96';rev['nodes'].reverse();cases.append(rev)
    split=copy.deepcopy(joined);split['id']='split192';split['nodes']=sum([[dict(node,n_comoving_per_cmpc3=node['n_comoving_per_cmpc3']/2)]*2 for node in joined['nodes']],[]);cases.append(split)
    for factor in [0.5,2.0]:
        v=copy.deepcopy(joined);v['id']=f'gauge{factor}';v['mean_scale_factor']*=factor
        for node in v['nodes']:node['n_comoving_per_cmpc3']*=factor**3
        cases.append(v)
    for typ in ['zero_photons','zero_absorbers']:
        v=copy.deepcopy(joined);v['id']=typ
        if typ=='zero_photons':
            for node in v['nodes']:node['n_comoving_per_cmpc3']=0.0
        else:v['n']=[0.0]*3
        cases.append(v)
    v=copy.deepcopy(joined);v['id']='thresholds';v['nodes']=[{'energy_ev':r[0],'n_comoving_per_cmpc3':1e63} for r in DATA['rows']];cases.append(v)
    refs={c['id']:photo_oracle(c) for c in cases}
    errors=[]
    for i,c in enumerate(base['calls']):
        old=c['expected_from_python_NOT_native'];r=refs[f'bin{i}']
        for oldk,newk in [('events_proper_per_cm3_s','events'),('heat_erg_per_cm3_s','heat'),('binding_erg_per_cm3_s','binding')]:
            for ov,rv in zip(old[oldk],r[newk]):
                if rv:errors.append(abs(M(ov)-rv)/abs(rv))
                else:assert ov==0
    base_r=refs['joined96']; invariant=[]
    for key in ['reversed96','split192','gauge0.5','gauge2.0']:
        rr=refs[key]
        diff=max([abs(v-w)/abs(v) for k in ['gamma','events','heat','binding','absorbed_species'] for v,w in zip(base_r[k],rr[k]) if v])
        invariant.append({'variant':key,'max_relative_physical_output_difference':diff})
        assert diff<mp.mpf('1e-75')
    photon=photon_oracle(base['photon_balance_input'],[sum(refs[f'bin{i}']['events']) for i in range(3)])
    invalid=[]
    for key in ['scale_zero','negative_density','negative_node','out_of_domain_even_zero_count','nonfinite_energy','positive_count_conversion_underflow']:
        v=copy.deepcopy(cases[0]);v['id']=key;v['expect_error']=True;v['nodes']=v['nodes'][:1]
        if key=='scale_zero':v['mean_scale_factor']=0.0
        elif key=='negative_density':v['n'][0]=-1.0
        elif key=='negative_node':v['nodes'][0]['n_comoving_per_cmpc3']=-1.0
        elif key=='out_of_domain_even_zero_count':v['nodes'][0]={'energy_ev':50001.0,'n_comoving_per_cmpc3':0.0}
        elif key=='nonfinite_energy':v['nodes'][0]['energy_ev']='NaN'
        else:v['nodes'][0]['n_comoving_per_cmpc3']=1e-300
        v['expected_error']={'scale_zero':'MEAN_SCALE_FACTOR_INVALID','negative_density':'HOMOGENEOUS_NONFINITE_OR_NEGATIVE','negative_node':'HOMOGENEOUS_NONFINITE_OR_NEGATIVE','out_of_domain_even_zero_count':'VERNER_ENERGY_DOMAIN','nonfinite_energy':'PHOTON_ENERGY_INVALID','positive_count_conversion_underflow':'PHOTON_CONVERSION_UNDERFLOW'}[key]
        invalid.append(v)
    payload={'kind':'PREPARED_NATIVE_CASES_NOT_EXECUTED','cases':cases+invalid,'photon_input':base['photon_balance_input'],
      'photon_absorption_owner':'Native sums from outputs bin0/bin1/bin2, never Python expected sinks',
      'tolerance':{'relative':3e-12,'expected_exact_zero_absolute':0.0}}
    (ROOT/'inputs/CASES.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/NODE_REFERENCE_80DIGIT.json').write_text(json.dumps(encode({'kind':'INDEPENDENT_MATH_NOT_NATIVE','valid_cases':len(cases),'invalid_native_cases_prepared':len(invalid),'references':refs,'photon':photon}),indent=2)+'\n')
    summary={'status':'FINITE_INPUT_REFERENCE_CHECKED_NATIVE_BLOCKED','input_nodes':96,'valid_reference_cases':len(cases),'invalid_native_cases_prepared':len(invalid),'max_relative_change_from_FLRW05_expected':max(errors),'invariances':invariant,'native_calls':0}
    (ROOT/'results/REFERENCE_SUMMARY.json').write_text(json.dumps(encode(summary),indent=2)+'\n')
    print(json.dumps(encode(summary),indent=2))
if __name__=='__main__':main()
