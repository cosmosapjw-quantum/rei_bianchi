"""Independent finite-point check of original Rust primary_stage_step output.

Uses the pre-Rust FT03 Python rate lineage and solves only a 4D endpoint root.
No ODE history, continuum convergence, or interval certification is performed.
"""
from pathlib import Path
import json, math, sys, hashlib, argparse
import numpy as np
from scipy.optimize import root
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'intake/ft03_reference/research'))
import closure_model as atomic

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--native-output',type=Path,default=ROOT/'results/stage_stdout.jsonl')
    ap.add_argument('--result',type=Path,default=ROOT/'results/STAGE_INDEPENDENT_CHECK.json')
    args=ap.parse_args()
    cfg=json.loads((ROOT/'results/STAGE_INPUT.json').read_text())
    pre=json.loads((ROOT/'results/STAGE_PREREGISTRATION.json').read_text())
    rows=[json.loads(s) for s in args.native_output.read_text().splitlines()]
    assert len(rows)==5 and [r['case'] for r in rows]==list(range(5))
    nh,fhe,H,dt=cfg['nH'],cfg['fHe'],cfg['H_s'],cfg['dt_s']
    chi=atomic.CHI; kb,ev,c=atomic.KB,atomic.EV,atomic.C
    f0=np.array(cfg['fractions']); nodes=np.array(cfg['nodes']); energies,p0=nodes.T
    el0=f0[0]+fhe*(f0[1]+2*f0[2]); nu0=1+fhe+el0
    w0=1.5*kb*cfg['T_K']*nu0/ev
    y0=np.r_[f0,w0]; scale=np.array([1.,1.,1.,w0])
    sigma=np.array([[atomic.cross_section(s,e) for s in range(3)] for e in energies])
    def temperature(y):return 2*ev*y[3]/(3*kb*(1+fhe+y[0]+fhe*(y[1]+2*y[2])))
    def evaluate(y):
        x,he1,he2,w=y; T=temperature(y)
        atomic.check_temperature(T)
        lower=np.array([1-x,fhe*(1-he1-he2),fhe*he1]); upper=np.array([x,fhe*he1,fhe*he2])
        el=x+fhe*(he1+2*he2)
        alpha,g,_=atomic.recombination(T)
        ci_coeff=atomic.collisional(T); adr,epsdr=atomic.dr_components(T)
        opacity=c*nh*(sigma@lower)
        p=p0/(1+dt*opacity)
        photo=c*nh*sigma*lower[None,:]*p[:,None]
        ci=nh*el*lower*ci_coeff; rr=nh*el*upper*alpha
        dr=nh*el*fhe*he1*adr
        epsrr=kb*T*(1.5+g)/ev
        net=photo.sum(axis=0)+ci-rr; net[1]-=dr.sum()
        heat=float(np.sum(photo*(energies[:,None]-chi[None,:])))
        f=np.r_[net[0],(net[1]-net[2])/fhe,net[2]/fhe,
                 heat-ci@chi-rr@epsrr-dr@(epsdr/ev)-2*H*w]
        escaped=float(rr@(chi+epsrr)+dr.sum()*chi[1]+dr@(epsdr/ev))
        return dict(f=f,p=p,photo=dt*photo,ci=dt*ci,rr=dt*rr,dr=dt*dr,
                    escape=dt*escaped,work=2*H*dt*w,T=T,heat=dt*heat)
    def residual(y): return (y-y0-dt*evaluate(y)['f'])/scale
    # The reference root is constructed from independent balance equations;
    # no native endpoint or event is used to seed or define the reference.
    sol=root(residual,y0,method='hybr',options={'xtol':1e-10,'maxfev':100})
    assert sol.success, str(sol.message)
    rr=evaluate(sol.x); r0=rows[0]; native_y=np.r_[r0['fractions'],r0['w']]
    state_error=float(max(np.max(np.abs(native_y[:3]-sol.x[:3])),abs(math.log(temperature(native_y)/rr['T']))))
    assert state_error < pre['acceptance']['state_abs_and_logT']
    zero_entries=0; compared=0; max_rel=0.
    def compare(native,reference):
        nonlocal zero_entries,compared,max_rel
        a,b=np.broadcast_arrays(np.asarray(native,dtype=float),np.asarray(reference,dtype=float))
        assert np.all(np.isfinite(a)) and np.all(np.isfinite(b))
        for av,bv in zip(a.flat,b.flat):
            compared+=1
            if bv==0:
                zero_entries+=1; assert av==0,(av,bv)
            else:
                rel=abs(av-bv)/abs(bv); max_rel=max(max_rel,float(rel))
                assert rel<pre['acceptance']['event_relative'],(av,bv,rel)
    for key,rkey in [('photons','p'),('photo_events','photo'),('ci','ci'),('rr','rr'),('dr','dr'),('escape','escape'),('work','work')]:
        compare(r0[key],rr[rkey])
    native_res=float(np.max(np.abs(residual(native_y))))
    assert native_res < pre['acceptance']['independent_BE_residual_scaled']
    def binding(y):return chi[0]*y[0]+fhe*(chi[1]*y[1]+(chi[1]+chi[2])*y[2])
    en0=math.fsum([w0,binding(y0),float(energies@p0)])
    photon_r=np.asarray(r0['photo_events']); ci=np.array(r0['ci']); rec=np.array(r0['rr']); dr=np.array(r0['dr']); p=np.array(r0['photons'])
    energy_res=math.fsum([r0['w']-w0,binding(native_y)-binding(y0),float(energies@(p-p0)),r0['escape'],r0['work']])
    atom_net=photon_r.sum(axis=0)+ci-rec;atom_net[1]-=dr.sum()
    species_def=np.array([native_y[0]-y0[0],fhe*(native_y[1]-y0[1]),fhe*(native_y[2]-y0[2])])-np.array([atom_net[0],atom_net[1]-atom_net[2],atom_net[2]])
    photon_def=p0-p-photon_r.sum(axis=1)
    electron0=el0; electron1=native_y[0]+fhe*(native_y[1]+2*native_y[2])
    number_res=math.fsum([electron1-electron0,float(np.sum(p-p0)),-float(np.sum(ci)),float(np.sum(rec)),float(np.sum(dr))])
    assert abs(energy_res)/en0<pre['acceptance']['energy_scaled']
    assert np.all(p>=0) and np.all(photon_r>=0)
    assert 0<=native_y[0]<=1 and native_y[1]>=0 and native_y[2]>=0 and native_y[1]+native_y[2]<=1
    # Reverse/split invariants are tested as properties, not extra independent initial states.
    reverse=rows[1]; split=rows[2]
    for r in [reverse,split]:
        assert max(abs(np.array(r['fractions'])-native_y[:3]))<pre['acceptance']['state_abs_and_logT']
        assert abs(math.log(r['w']/r0['w']))<pre['acceptance']['state_abs_and_logT']
        for field in ['ci','rr','dr','escape','work']:compare(r[field],r0[field])
    compare(np.array(reverse['photons'])[::-1],p)
    compare(np.array(reverse['photo_events'])[::-1],photon_r)
    compare(np.array(split['photons']).reshape(-1,2).sum(axis=1),p)
    compare(np.array(split['photo_events']).reshape(-1,2,3).sum(axis=1),photon_r)
    zero=rows[3]
    assert zero['fractions']==cfg['fractions'] and zero['w']==r0['initial_w']
    assert zero['old_photons']==zero['photons'] and zero['residual']==0 and zero['iterations']==0
    assert not any(np.r_[np.asarray(zero['photo_events']).ravel(),zero['ci'],zero['rr'],zero['dr'],zero['work'],zero['escape']])
    assert rows[4]['error']=='PRIMARY_PACKET_DOMAIN' and rows[4]['unchanged'] is True
    absorbed=(photon_r*energies[:,None]).sum(axis=0)
    binding_photo=photon_r.sum(axis=0)*chi
    photoheat=(photon_r*(energies[:,None]-chi[None,:])).sum(axis=0)
    out={
      'status':'SCOPED_ACTUAL_PRIMARY_STAGE_REGRESSION_PASS',
      'fixture':cfg|{'nodes':'see STAGE_INPUT.json (96 rows)'},
      'reference':{'kind':'independent original FT03 Python rate lineage plus4D SciPy root; analytic photon elimination',
                   'root_success':bool(sol.success),'root_nfev':int(sol.nfev),'root_residual_max':float(np.max(np.abs(residual(sol.x)))),
                   'native_endpoint_used_as_root_input':False},
      'endpoint':{'fractions':r0['fractions'],'w_eV_per_H':r0['w'],'T_K':temperature(native_y),
                  'remaining_photons_per_H':math.fsum(r0['photons']),'initial_photons_per_H':math.fsum(p0),
                  'absorbed_counts_per_H':photon_r.sum(axis=0).tolist(),'CI_per_H':r0['ci'],'RR_per_H':r0['rr'],'DR_per_H':r0['dr'],
                  'absorbed_eV_per_H':absorbed.tolist(),'binding_photo_eV_per_H':binding_photo.tolist(),
                  'photoheat_eV_per_H':photoheat.tolist(),'escape_eV_per_H':r0['escape'],'thermal_work_eV_per_H':r0['work']},
      'comparisons':{'state_abs_or_logT_max':state_error,'scalar_checks_including_metamorphic':compared,
                     'zero_exact_checks':zero_entries,'max_relative':max_rel,'native_BE_residual_independent':native_res,
                     'number_budget_per_H':number_res,'species_budget_max_per_H':float(max(abs(species_def))),
                     'photon_budget_max_per_H':float(max(abs(photon_def))),
                     'energy_budget_eV_per_H':energy_res,'energy_budget_scaled':abs(energy_res)/en0,
                     'permutation_and_split_pass':True,'zero_dt_identity_pass':True,'negative_count_transactional_rejection':True},
      'limits':{'single_accepted_stage_only':True,'frozen_density_and_photon_energy':True,'gas_work_included':True,
                'radiation_work_included':False,'full_expanding_history':False,'ODE_integrations':0,'interval_certificate':False,
                'physical_provider_admission':False,'same_atomic_input_not_independent_atomic_data':True},
      'inputs_sha256':{p:sha(ROOT/p) for p in ['results/STAGE_INPUT.json','results/STAGE_PREREGISTRATION.json','research/check_actual_stage.py']}}
    out['native_output_sha256']=sha(args.native_output)
    args.result.parent.mkdir(parents=True,exist_ok=True)
    args.result.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','reference','endpoint','comparisons']},indent=2))
if __name__=='__main__':main()
