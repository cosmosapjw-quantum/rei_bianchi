"""Bounded controls for new HE38 dependencies only; no inherited suite replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os,platform,resource,sys,time,traceback
import numpy as np

BASE=Path(__file__).resolve().parent
def stamp(): return datetime.now(timezone.utc).isoformat()
def hashes():
    return {str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(BASE.rglob('*.py')) if '__pycache__' not in str(p)}


def run():
    import h1_finite_mass as h
    from h1_finite_mass.he36.vendor.rei_resolved_local import Unresolved
    checks=[]
    def check(name,condition,detail=None):
        if not bool(condition): raise AssertionError(name+': '+str(detail))
        checks.append({'name':name,'passed':True,'detail':detail})
    def reject(name,fn):
        try: fn()
        except (ValueError,ArithmeticError,Unresolved): check(name,True)
        else: raise AssertionError('missing rejection: '+name)
    def defect(actual,expected):
        a=np.asarray(actual);b=np.asarray(expected);scale=max(float(np.max(np.abs(a))),float(np.max(np.abs(b))))
        return 0. if scale==0 else float(np.max(np.abs(a/scale-b/scale)))
    ev=h.FiniteMassModel().evaluate([2000.,20000.,200000.])
    check('distinct_finite_mass_identity',ev.identity!=h.model.donor.MODEL_IDENTITY)
    check('native_relative_energy_metadata',ev.energy_mapping==h.ENERGY_MAPPING and ev.reduced_mass_kg==h.MU_KG)
    for attr in ('temperature_K','moments_SI','stf_coefficients_m3_s','heat_per_pair_J_m3_s'):
        array=getattr(ev,attr)
        reject('immutable_'+attr,lambda a=array:a.setflags(write=True))
    for bad in (True,[2000.,True],[2000.,float('nan')],[2000.+0j],['2000'],[],[[2000.]],1999.,200001.):
        reject('temperature_reject_'+repr(bad),lambda v=bad:h.FiniteMassModel().evaluate(v))
    reject('mixed_bool_cross_section',lambda:h.sigma_m2([20.,True]))
    reject('mixed_bool_transfer',lambda:h.transfer_u(20.,[0.5,True]))
    zero=np.zeros((3,3));ne=4e5;nh=6e5
    shape_e=np.array([[1.,0.2,0.1],[0.2,-.3,-.15],[.1,-.15,-.7]])
    shape_h=np.array([[-.2,.1,-.2],[.1,.6,.15],[-.2,.15,-.4]])
    max_heat=max_stf=max_rotation=0.
    for temp in (2000.,20000.,200000.):
        pe=1e-4*ne*h.KB_J_K*temp*shape_e
        ph=2e-4*nh*h.KB_J_K*temp*shape_h
        src=h.finite_mass_source(temp,ne,nh,pe,ph)
        heat_error=defect(np.sum(src.heat_sources_W_m3),src.Q)
        stf_error=defect(np.sum(src.stf_sources_Pa_s,axis=0),src.J)
        max_heat=max(max_heat,heat_error);max_stf=max(max_stf,stf_error)
        check('species_heat_sum_'+str(temp),heat_error<3e-14,heat_error)
        check('species_STF_sum_'+str(temp),stf_error<3e-14,stf_error)
        check('number_mass_charge_'+str(temp),
              defect(np.dot([h.ME_KG,h.MH_KG,h.MP_KG],src.number_sources_m3_s),0.)==0. or
              abs(float(np.dot([h.ME_KG,h.MH_KG,h.MP_KG],src.number_sources_m3_s)))<1e-14*h.MP_KG*src.volumetric_event_rate)
        check('number_charge_'+str(temp),src.number_sources_m3_s[0]==src.number_sources_m3_s[2])
        angle=.38;rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
        rotated=h.finite_mass_source(temp,ne,nh,rot@pe@rot.T,rot@ph@rot.T)
        rotation_error=defect(rotated.J,rot@src.J@rot.T)
        max_rotation=max(max_rotation,rotation_error)
        check('rotation_covariance_'+str(temp),rotation_error<1e-13,rotation_error)
        check('STF_not_recovered_by_cancellation_'+str(temp),defect(src.J,h.finite_mass_source(temp,ne,nh,pe*1e-100,ph*1e-100).J/1e-100)<2e-14)
        reject('immutable_species_source_'+str(temp),lambda a=src.stf_sources_Pa_s:a.setflags(write=True))
    pe=1e-4*ne*h.KB_J_K*20000.*shape_e;ph=2e-4*nh*h.KB_J_K*20000.*shape_h
    for dens in (float('nan'),float('inf'),-1.,True):
        reject('bad_density_'+repr(dens),lambda d=dens:h.finite_mass_source(20000.,d,nh,pe,ph))
    reject('non_STF',lambda:h.finite_mass_source(20000.,ne,nh,np.eye(3),ph))
    reject('asymmetric_STF',lambda:h.finite_mass_source(20000.,ne,nh,[[1,1,0],[0,-1,0],[0,0,0]],ph))
    reject('mixed_bool_STF',lambda:h.finite_mass_source(20000.,ne,nh,[[True,0.,0.],[0.,-1.,0.],[0.,0.,0.]],ph))
    reject('missing_linear_contract',lambda:h.finite_mass_source(20000.,ne,nh,pe,ph,linear_response=False))
    reject('absent_electron_with_stress',lambda:h.finite_mass_source(20000.,0.,nh,pe,ph))
    reject('absent_neutral_with_stress',lambda:h.finite_mass_source(20000.,ne,0.,pe,ph))
    reject('nonzero_underflow_rejected',lambda:h.finite_mass_source(20000.,1e-250,1e-250,zero,zero))
    reject('overflow_rejected',lambda:h.finite_mass_source(20000.,1e300,1e300,zero,zero))
    for en,hn,p_e,p_h in ((0.,nh,zero,ph),(ne,0.,pe,zero),(0.,0.,zero,zero)):
        src=h.finite_mass_source(20000.,en,hn,p_e,p_h)
        check('zero_reactant_source_'+str((en,hn)),src.volumetric_event_rate==0 and np.count_nonzero(src.stf_sources_Pa_s)==0 and np.count_nonzero(src.heat_sources_W_m3)==0)
    max_momentum=max_energy=0.;event_count=0
    n1=np.array([1.,2.,-2.])/3.;n2=np.array([-2.,1.,2.])/3.
    for mass in (h.ME_KG,10*h.ME_KG,h.MP_KG,1e6*h.ME_KG):
        neutral=mass+h.ME_KG;total=neutral+h.ME_KG;eta=h.ME_KG/total;zeta=neutral/total;mu=h.ME_KG*zeta
        for energy_ev in (14.,40.,1000.):
            g=np.array([np.sqrt(2*energy_ev*h.EV_J/mu),0.,0.]);boost=np.array([1300.,-2500.,700.])
            ve=boost+zeta*g;vh=boost-eta*g
            transfer=float(h.transfer_u(energy_ev,.4))
            event=h.event_kinematics(ve,vh,transfer,n1,n2,ion_mass_kg=mass)
            # Normalize momentum error by the sum of incoming magnitude, so
            # a nearly cancelling COM does not create a false relative error.
            pscale=h.ME_KG*np.linalg.norm(ve)+neutral*np.linalg.norm(vh)
            perror=float(np.linalg.norm(event.outgoing_momentum_kg_m_s-event.incoming_momentum_kg_m_s)/pscale)
            eerror=abs((event.outgoing_kinetic_energy_J+event.ionization_energy_J)/event.incoming_kinetic_energy_J-1)
            max_momentum=max(max_momentum,perror);max_energy=max(max_energy,eerror);event_count+=1
            check('event_momentum_'+str(event_count),perror<3e-14,perror)
            check('event_energy_'+str(event_count),eerror<3e-14,eerror)
            check('artificial_mass_label_'+str(event_count),(mass==h.MP_KG)==(event.mass_scope=='physical_CODATA2022_proton'))
    reject('invalid_event_direction',lambda:h.event_kinematics(ve,vh,transfer,[2.,0.,0.],n2))
    y=np.zeros(21);y[1]=.6;y[2]=.4
    scopes=dict(thermal_inventory_scope=h.ALL_RETAINED_THERMAL,charge_census_scope=h.NEUTRAL_21_STATE_CENSUS)
    src=h.h1_ci_source(20000.,y,1e6,pe,ph,**scopes)
    check('donor_and_native_rate',defect(src.event_tensor_source.volumetric_event_rate,src.volumetric_event_rate)<1e-13)
    check('single_heat_owner',defect(src.reservoir_sources_W_m3['dEth'],src.Q)<1e-13)
    check('physical_not_frozen_ne_Jacobian',src.physical_abundance_jacobian_s[2,2]>0 and src.frozen_ne_abundance_jacobian_s[2,2]==0)
    check('donor_frozen_jacobian',defect(src.frozen_ne_abundance_jacobian_s,src.event_row_frozen_ne['jacobian'])<1e-13)
    tangent=np.zeros(21);tangent[1]=-1.;tangent[2]=1.;eps=1e-5
    plus=h.h1_ci_source(20000.,y+eps*tangent,1e6,pe,ph,**scopes)
    minus=h.h1_ci_source(20000.,y-eps*tangent,1e6,pe,ph,**scopes)
    fd=(plus.abundance_source_s-minus.abundance_source_s)/(2*eps)
    check('physical_jacobian_normalized_manifold',defect(fd,src.physical_abundance_jacobian_s@tangent)<1e-8)
    check('thermal_census',src.thermal_particle_density_m3==1.4e6 and src.dot_T_reaction_K_s<0)
    reject('missing_thermal_declaration',lambda:h.h1_ci_source(20000.,y,1e6,pe,ph))
    wrong=y.copy();wrong[0]=.1
    reject('other_species_unresolved',lambda:h.h1_ci_source(20000.,wrong,1e6,pe,ph,**scopes))
    boolstate=y.tolist();boolstate[0]=False
    reject('bool_state',lambda:h.h1_ci_source(20000.,boolstate,1e6,pe,ph,**scopes))
    yn=np.zeros(21);yn[1]=1.
    atn=h.h1_ci_source(20000.,yn,1e6,zero,ph,**scopes)
    check('boundary_zero_source_nonzero_physical_derivative',atn.volumetric_event_rate==0 and atn.physical_abundance_jacobian_s[2,2]>0)
    vacuum=h.h1_ci_source(20000.,y,0.,zero,zero,**scopes)
    check('vacuum_temperature_undefined',vacuum.dot_T_reaction_K_s is None)
    provenance=json.loads((BASE/'DONOR_PROVENANCE.json').read_text())
    for entry in provenance['files']:
        check('byte_preserved_'+entry['destination_relative'],hashlib.sha256((BASE/entry['destination_relative']).read_bytes()).hexdigest()==entry['sha256'])
    return dict(status='PASS',controls=len(checks),checks=checks,model_identity=h.MODEL_IDENTITY,
        maxima=dict(species_heat_relative=max_heat,species_STF_relative=max_stf,rotation_relative=max_rotation,
                    event_momentum_normalized=max_momentum,event_energy_relative=max_energy),
        event_kinematics_cases=event_count,old_suite_replays=0,old_IVP_replays=0,new_IVP=0,
        scope='new finite-mass event/partition/STF, new wrapper domains, affected donor attachment only')


if __name__=='__main__':
    start=stamp();attempt=BASE/'attempts'/('attempt_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    attempt.mkdir(parents=True)
    metadata=dict(started_utc=start,pid=os.getpid(),python=sys.version,executable=sys.executable,
                  platform=platform.platform(),numpy=np.__version__,cwd=os.getcwd(),argv=sys.argv,
                  input_sha256=hashes(),old_suites_replayed=0,new_IVP=0)
    (attempt/'START.json').write_text(json.dumps(metadata,indent=2)+'\n')
    wall=time.perf_counter();cpu=time.process_time();code=0
    try: result=run()
    except Exception as exc:
        code=1;result=dict(status='FAIL',exception=repr(exc),traceback=traceback.format_exc())
    result.update(finished_utc=stamp(),wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,
                  max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,exit_code=code)
    (attempt/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (BASE/'LATEST_ATTEMPT.json').write_text(json.dumps({'path':str(attempt.relative_to(BASE)),'status':result['status']},indent=2)+'\n')
    print(json.dumps({'attempt':str(attempt),'status':result['status'],'controls':result.get('controls'),
                      'cpu_seconds':result['cpu_seconds'],'exception':result.get('exception')}))
    if code: print(result['traceback'])
    sys.exit(code)
