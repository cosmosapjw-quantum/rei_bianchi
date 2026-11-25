"""Audit a new REC-IC AXBI native long history, streaming all ledger rows."""
import argparse,csv,hashlib,json,math
from pathlib import Path
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--donor',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);a=p.parse_args()
root=a.root;run=root/'run';q=json.loads(a.donor.read_text());fhe=q['background']['f_He'];ini=q['initial'];digest=sha(a.donor)
assert int((root/'exit_code.txt').read_text())==0
assert (run/'initial_state_id.txt').read_text()=='REC_HMLA_'+digest
ret=dict(x.split('=',1) for x in (run/'RETURN.txt').read_text().splitlines() if '=' in x)
assert ret['status']=='COMPLETE_REPRESENTED_INTERVAL'
prev=None;tau=0.;n=0;max_ne=0.;min_temp=math.inf;min_ph=math.inf
with (run/'history.csv').open() as f:
    for row in csv.DictReader(f):
        vals={k:float(v) for k,v in row.items() if k!='case_id'}
        assert all(math.isfinite(v) for v in vals.values())
        nh=vals['nH_proper_cm3']*1e6;ne=vals['ne_proper_cm3']*1e6
        x,y,z=map(vals.get,('x_HII','x_HeII','x_HeIII'))
        assert 0<=x<=1 and y>=0 and z>=0 and y+z<=1
        assert vals['temperature_K']>0 and vals['photon_n_per_H']>=0
        max_ne=max(max_ne,abs(ne-nh*(x+fhe*(y+2*z)))/max(ne,1e-300))
        min_temp=min(min_temp,vals['temperature_K']);min_ph=min(min_ph,vals['photon_n_per_H'])
        if prev is None:
            first=vals.copy();assert abs(nh/ini['n_H_m3']-1)<2e-14 and abs(x/ini['x_HII']-1)<2e-14 and abs(vals['temperature_K']/ini['T_m_K']-1)<2e-14
        else:
            t,old_ne=prev;dt=vals['time_s']-t;assert dt>0
            tau+=dt*(old_ne+ne)*.5*299792458.*6.6524587051e-29
        prev=(vals['time_s'],ne);n+=1
assert vals['zbar']==4 and n==int(ret['accepted'])+1 and max_ne<2e-14
gates=0;rows=0;worst=0.;gate_names={}
with (run/'ledgers.csv').open() as f:
    for row in csv.DictReader(f):
        rows+=1
        if row['status']=='VALUE':continue
        assert row['status']=='PASS',row
        r=abs(float(row['residual']));tol=float(row['tolerance']);assert tol>0 and r<=tol
        worst=max(worst,r/tol);gates+=1
        name=row['ledger_name'];gate_names[name]=max(gate_names.get(name,0.),r/tol)
out=dict(scope='REC_HMLA_IC_AXBI_FLRW_z20_to4_SINGLE_COARSE_LANE',status='PASS_SCOPED',binary_sha256=sha(a.binary),donor_sha256=digest,config_sha256=sha(root/'REC_q0_long.cfg'),accepted=int(ret['accepted']),attempts=int(ret['attempts']),rhs=int(ret['rhs_evaluations']),wall_s=float(ret['wall_s']),max_newton_residual=float(ret['max_newton_residual']),history_rows=n,ledger_rows=rows,ledger_gate_rows=gates,max_ledger_ratio=worst,gate_names=gate_names,max_ne_inventory_relative=max_ne,min_temperature=min_temp,min_photon_stock=min_ph,initial=first,terminal=vals,tau=tau,hashes={str(f.relative_to(root)):sha(f) for f in sorted(root.rglob('*')) if f.is_file() and f.name!='LONG_AUDIT.json'})
(root/'LONG_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print({k:out[k] for k in ('accepted','history_rows','ledger_gate_rows','max_ledger_ratio','max_ne_inventory_relative','tau','terminal')})
