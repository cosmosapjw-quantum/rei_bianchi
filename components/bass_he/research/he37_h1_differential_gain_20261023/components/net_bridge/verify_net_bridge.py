"""Affected HE37 source/event bridge checks; no prior suite or IVP replay."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,os,platform,resource,sys,time,traceback,shutil
import numpy as np
import scipy
from h1_net import *
from h1_net.lc_ionization import LCModel,I_J,KB_J_K,MODEL_IDENTITY
from h1_net.he36.vendor.rei_resolved_local import thermal_rhs

ROOT=Path(__file__).resolve().parent
LABELS={'thermal_inventory_scope':ALL_RETAINED_THERMAL,'charge_census_scope':NEUTRAL_21_STATE_CENSUS}

def state(x=.3):
    y=np.zeros(21);y[1]=1-x;y[2]=x;return y

def relative(a,b):
    a=np.asarray(a);b=np.asarray(b);scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))))
    return 0. if scale==0 else float(np.max(np.abs(a/scale-b/scale)))

def close(a,b,gate=2e-12):
    d=relative(a,b);assert d<=gate,(d,gate,a,b);return d

def evaluate(T=20000.,x=.3,nb=1e6,pi=None):
    return h1_ci_source(T,state(x),nb,np.zeros((3,3)) if pi is None else pi,**LABELS)

def scalar_conservation():
    rows=[]
    for T in (2000.,20000.,200000.):
        y=state(.37);nb=2e6;out=h1_ci_source(T,y,nb,np.zeros((3,3)),**LABELS)
        alpha=float(LCModel().evaluate(T).alpha_m3_s[0]); r=(nb*y[1])*(nb*y[2])*alpha
        expected=np.zeros(21);expected[1]=-r;expected[2]=r
        errs=[close(out.R_species,expected),close(out.Relectron,r),close(out.Rpart,r),
              close(out.Q,-I_J*r),close(np.trace(out.S)/2,out.Q),
              close(out.reservoir_sources_W_m3['dI'],-out.Q),
              close(out.Q,out.reservoir_sources_W_m3['dEth'])]
        assert out.Rnucleus==0 and float(MASS_NUMBER@out.R_species)==0
        assert float(IONIC_CHARGE@out.R_species)==out.Relectron
        assert out.status=='POSITIVE'
        assert out.event_row_frozen_ne['reservoir_sources']['dI']>0
        assert np.linalg.eigvalsh(out.S).max()<0,'net sink must not be clipped'
        rows.append({'T_K':T,'rate_m3_s':out.volumetric_event_rate,'Q_W_m3':out.Q,'max_normalized_defect':max(errs)})
    return {'controls':rows}

def tensor_rotation():
    T=20000.;nb=3e5;x=.23;ne=nb*x
    pi=ne*KB_J_K*T*2e-3*np.array([[1.,.23,-.17],[.23,-.4,.31],[-.17,.31,-.6]])
    theta=.61;R=np.array([[math.cos(theta),-math.sin(theta),0.],[math.sin(theta),math.cos(theta),0.],[0.,0.,1.]])
    base=evaluate(T,x,nb,pi);rot=evaluate(T,x,nb,R@pi@R.T)
    expected=-nb*(1-x)*base.kappa2_m3_s*pi
    errs=[close(base.J,expected),close(rot.J,R@base.J@R.T),close(rot.S,R@base.S@R.T),close(rot.Q,base.Q)]
    direct_per_event=-2*I_J/3*np.eye(3)-(base.kappa2_m3_s/base.alpha_m3_s)*(pi/ne)
    errs.append(close(base.per_event_tensor_J,direct_per_event))
    errs.append(close(np.trace(base.per_event_tensor_J)/2,-I_J))
    err_donor=np.max(np.abs(base.J-base.event_tensor_source.J))/np.max(np.abs(base.S))
    assert err_donor<2e-13
    return {'max_relative_defect':max(errs),'donor_STF_projection_absolute_normalized_to_full_source':float(err_donor),'pi_over_ne_kT_Frobenius':base.electron_grad_relative_norm}

def physical_jacobian():
    records=[]
    for x in (.17,.64):
        T=20000.;nb=7e4;out=evaluate(T,x,nb)
        expected=np.zeros((21,21));a=nb*out.alpha_m3_s
        expected[1,1]=-a*x;expected[1,2]=-a*(1-x);expected[2,:]=-expected[1,:]
        analytic=close(out.physical_abundance_jacobian_s,expected)
        # The pure-H manifold has dY_H=-dx,dY_p=dx, so finite difference stays admissible.
        h=2**-18
        fd=(evaluate(T,x+h,nb).abundance_source_s-evaluate(T,x-h,nb).abundance_source_s)/(2*h)
        tangent=np.zeros(21);tangent[1]=-1;tangent[2]=1
        d=close(fd,out.physical_abundance_jacobian_s@tangent,3e-9)
        assert out.event_row_frozen_ne['jacobian'][2,2]==0
        assert out.physical_abundance_jacobian_s[2,2]>0
        records.append({'x':x,'analytic_relative':analytic,'finite_difference_tangent_relative':d,
                        'physical_J_pp':out.physical_abundance_jacobian_s[2,2],
                        'frozen_ne_donor_J_pp':out.event_row_frozen_ne['jacobian'][2,2]})
    return {'controls':records,'finite_difference_gate':3e-9,'physical_scope':PHYSICAL_JACOBIAN_SCOPE,'donor_scope':FROZEN_NE_JACOBIAN_SCOPE}

def zero_states():
    a=evaluate(x=0.);b=evaluate(x=1.,pi=np.diag([1e-20,-1e-20,0.]));c=evaluate(nb=0.)
    assert [a.status,b.status,c.status]==['ZERO_ELECTRON','ZERO_TARGET','ZERO_DENSITY']
    for out in (a,b,c):
        assert out.event_row_frozen_ne is None and out.event_tensor_source is None
        assert np.array_equal(out.R_species,np.zeros(21)) and np.array_equal(out.J,np.zeros((3,3)))
        assert out.Q==out.Rpart==out.volumetric_event_rate==0.
    assert a.physical_abundance_jacobian_s[2,2]>0
    assert b.physical_abundance_jacobian_s[2,1]>0
    assert c.dot_T_reaction_K_s is None and c.dot_T_status=='UNDEFINED_VACUUM_TEMPERATURE'
    assert a.dot_T_reaction_K_s==b.dot_T_reaction_K_s==0.
    return {'statuses':[a.status,b.status,c.status],'zero_electron_activation_jacobian_retained':True,'vacuum_temperature_not_defined':True}

def rejection_contracts():
    y=state();zero=np.zeros((3,3));cases=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,ArithmeticError,OverflowError) as e:cases.append({'name':name,'type':type(e).__name__,'message':str(e)})
        else:raise AssertionError('missing rejection '+name)
    for T in (1999.,200001.,True,float('nan'),1+1j,[20000.]):
        reject('invalid_temperature_'+repr(T),lambda T=T:h1_ci_source(T,y,1e6,zero,**LABELS))
    for nb in (-1.,float('inf'),True,1+0j):
        reject('invalid_density_'+repr(nb),lambda nb=nb:h1_ci_source(20000.,y,nb,zero,**LABELS))
    reject('thermal_scope_missing',lambda:h1_ci_source(20000.,y,1e6,zero,charge_census_scope=NEUTRAL_21_STATE_CENSUS))
    reject('census_scope_missing',lambda:h1_ci_source(20000.,y,1e6,zero,thermal_inventory_scope=ALL_RETAINED_THERMAL))
    extra=y.copy();extra[10]=1e-10
    reject('other_species',lambda:h1_ci_source(20000.,extra,1e6,zero,**LABELS))
    scaled=y*2
    reject('unnormalized_pure_H',lambda:h1_ci_source(20000.,scaled,1e6,zero,**LABELS))
    for yy in (np.zeros(20),np.full(21,float('nan')),np.array([True]*21),y.astype(str)):
        reject('invalid_Y_'+str(np.asarray(yy).dtype),lambda yy=yy:h1_ci_source(20000.,yy,1e6,zero,**LABELS))
    mixed=y.tolist();mixed[0]=False
    reject('mixed_bool_Y',lambda:h1_ci_source(20000.,mixed,1e6,zero,**LABELS))
    for pi in (np.eye(3),np.ones((2,2)),np.array([[0,1,0],[0,0,0],[0,0,0]]),np.full((3,3),float('inf'))):
        reject('invalid_pi',lambda pi=pi:h1_ci_source(20000.,y,1e6,pi,**LABELS))
    mixedpi=zero.tolist();mixedpi[0][0]=False
    reject('mixed_bool_pi',lambda:h1_ci_source(20000.,y,1e6,mixedpi,**LABELS))
    reject('nonzero_pi_no_electrons',lambda:evaluate(x=0.,pi=np.diag([1.,-1.,0.])))
    return {'rejected':len(cases),'cases':cases}

def representability():
    cases=[]
    for nb in (1e-200,1e250):
        try:evaluate(nb=nb)
        except (ArithmeticError,OverflowError) as e:cases.append({'nb':nb,'type':type(e).__name__,'message':str(e)})
        else:raise AssertionError('nonzero unrepresentable source was silently accepted')
    return {'rejected_nonzero_underflow_overflow':cases}

def thermal_and_immutability():
    y=state(.29);pi=np.diag([1.,-1.,0.])*1e-19;before=(y.copy(),pi.copy());nb=4e5;T=20000.
    out=h1_ci_source(T,y,nb,pi,**LABELS)
    alternate=thermal_rhs(y,out.abundance_source_s,IONIC_CHARGE,T,0.,out.Q/nb)
    difference=close(out.dot_T_reaction_K_s,alternate['dot_T_K_s'])
    assert np.array_equal(y,before[0]) and np.array_equal(pi,before[1])
    arrays=(out.Y21,out.electron_pi_Pa,out.R_species,out.J,out.S,out.physical_abundance_jacobian_s,
            out.physical_rate_gradient_s,out.event_row_frozen_ne['source'])
    for arr in arrays:
        try:arr.setflags(write=True)
        except ValueError:pass
        else:raise AssertionError('mutable result array')
    try:out.reservoir_sources_W_m3['dEth']=0
    except TypeError:pass
    else:raise AssertionError('mutable reservoir owner')
    return {'temperature_source_K_s':out.dot_T_reaction_K_s,'independent_EOS_relative_defect':difference,
            'immutable_arrays':len(arrays),'input_preserved':True,'heat_owner_equal':out.Q==out.reservoir_sources_W_m3['dEth']}

GROUPS={'scalar_conservation':scalar_conservation,'tensor_rotation':tensor_rotation,
        'physical_jacobian':physical_jacobian,'zero_states':zero_states,
        'rejection_contracts':rejection_contracts,'representability':representability,
        'thermal_and_immutability':thermal_and_immutability}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--groups',nargs='*',choices=tuple(GROUPS));args=parser.parse_args()
    chosen=list(GROUPS) if not args.groups else args.groups
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=ROOT/'attempts'/('attempt_'+stamp);out.mkdir(parents=True)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('h1_net/**/*.py'))}
    hashes['verify_net_bridge.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    start={'command':' '.join(sys.argv),'cwd':str(Path.cwd()),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'groups':chosen,'hashes':hashes,'model_identity':MODEL_IDENTITY,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
           'platform':platform.platform(),'new_IVP':0,'old_suite_replay':0,'new_benchmark':0,'new_render':0}
    (out/'START.json').write_text(json.dumps(start,indent=2)+'\n');clock=time.perf_counter();rows=[]
    for name in chosen:
        t=time.perf_counter()
        try:detail=GROUPS[name]();row={'group':name,'status':'PASS','detail':detail}
        except Exception as exc:
            row={'group':name,'status':'FAIL','exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        row['seconds']=time.perf_counter()-t;rows.append(row)
    result={**start,'results':rows,'passed':sum(r['status']=='PASS' for r in rows),'failed':sum(r['status']=='FAIL' for r in rows),
            'elapsed_seconds':time.perf_counter()-clock,'maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    result['exit_code']=0 if result['failed']==0 else 1
    if result['failed']:
        (out/'failed_source').mkdir()
        shutil.copy2(ROOT/'h1_net/net_source.py',out/'failed_source/net_source.py')
        shutil.copy2(Path(__file__),out/'failed_source/verify_net_bridge.py')
    temp=out/'RESULT.json.tmp';temp.write_text(json.dumps(result,indent=2)+'\n')
    with temp.open('rb') as f:os.fsync(f.fileno())
    temp.replace(out/'RESULT.json')
    print(json.dumps({'receipt':str(out/'RESULT.json'),'passed':result['passed'],'failed':result['failed'],'seconds':result['elapsed_seconds'],'results':rows},indent=2))
    return result['exit_code']

if __name__=='__main__':sys.exit(main())
