"""Audit original and three genuinely independently evolved AXBI refinements."""
import argparse,hashlib,json,csv,math
from pathlib import Path
import numpy as np
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
donor=json.loads(a.donor.read_text());q=donor['initial'];fhe=donor['background']['f_He'];digest=sha(a.donor)
data={};rows=[]
for name,root,config in [('base',a.base,a.base/'REC_q0_long.cfg')]+[(k,a.root/k,a.root/k/'config.cfg') for k in ('time','spectral','angular')]:
    run=root/'run';assert int((root/'exit_code.txt').read_text())==0
    assert (run/'initial_state_id.txt').read_text()=='REC_HMLA_'+digest
    assert (run/'config.cfg').read_bytes()==config.read_bytes()
    ret=dict(x.split('=',1) for x in (run/'RETURN.txt').read_text().splitlines() if '=' in x)
    assert ret['status']=='COMPLETE_REPRESENTED_INTERVAL'
    d=np.genfromtxt(run/'history.csv',names=True,delimiter=',',dtype=None,encoding='utf8')
    assert d['zbar'][0]==20 and d['zbar'][-1]==4 and len(d)==int(ret['accepted'])+1
    assert np.all(np.diff(d['time_s'])>0) and np.all(np.diff(d['a'])>0)
    assert np.max(abs(d['nH_proper_cm3'][0]*1e6/q['n_H_m3']-1))<2e-14
    assert abs(d['x_HII'][0]/q['x_HII']-1)<2e-14 and abs(d['temperature_K'][0]/q['T_m_K']-1)<2e-14
    assert np.all((d['x_HII']>=0)&(d['x_HII']<=1)&(d['x_HeII']>=0)&(d['x_HeIII']>=0)&(d['x_HeII']+d['x_HeIII']<=1))
    assert np.min(d['temperature_K'])>0 and np.min(d['photon_n_per_H'])>=0
    xe=d['ne_proper_cm3']/d['nH_proper_cm3'];err=float(np.max(abs(xe-(d['x_HII']+fhe*(d['x_HeII']+2*d['x_HeIII'])))/xe))
    assert err<2e-14
    tau=float(np.trapezoid(d['ne_proper_cm3']*1e6*299792458.*6.6524587051e-29,d['time_s']))
    gates=0;ng=0;ratios={}
    with (run/'ledgers.csv').open() as f:
        for row in csv.DictReader(f):
            ng+=1
            if row['status']=='VALUE':continue
            assert row['status']=='PASS',row
            v=abs(float(row['residual']));tol=float(row['tolerance']);assert tol>0 and v<=tol
            k=row['ledger_name'];ratios[k]=max(ratios.get(k,0.),v/tol);gates+=1
    assert gates==3*len(d)
    keys=('x_HII','x_HeII','x_HeIII','temperature_K','photon_n_per_H','photon_u_eV_per_H')
    r=dict(case=name,config=config.read_text(),status='PASS_SCOPED',accepted=int(ret['accepted']),rhs=int(ret['rhs_evaluations']),wall_s=float(ret['wall_s']),max_newton_residual=float(ret['max_newton_residual']),history_rows=len(d),ledger_rows=ng,gate_rows=gates,gate_ratios=ratios,max_ne_error=err,tau=tau,terminal={k:float(d[k][-1]) for k in keys},raw_root=str(root),hashes={str(f.relative_to(root)):sha(f) for f in sorted(root.rglob('*')) if f.is_file() and f.name!='LONG_AUDIT.json'})
    data[name]=d;rows.append(r);print(name,r['accepted'],tau,r['terminal'],ratios,flush=True)
base=rows[0]
for r in rows[1:]:
    d=data[r['case']];a0=data['base']['a'];x=data['base']
    r['comparison_base']={k:dict(max_absolute=float(np.max(abs(np.interp(a0,d['a'],d[k])-x[k]))),terminal_delta=r['terminal'][k]-base['terminal'][k]) for k in base['terminal']}
    r['tau_relative']=abs(r['tau']/base['tau']-1)
out=dict(status='PASS_SCOPED_ALL_REFINEMENT_RUNS',scope='FLRW primary-only conditional AXBI single-axis refinements, no physical admission',donor_sha256=digest,binary_sha256=sha(a.binary),cases=rows)
a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
