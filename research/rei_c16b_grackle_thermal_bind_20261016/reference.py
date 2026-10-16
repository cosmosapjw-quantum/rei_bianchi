"""Independent Python continuous H/He+photon ODE, unchanged literal-C rates.

No native time integrator is called. Frozen geometry, Case A, all owner terms.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, importlib.util, json, math, os, subprocess, time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/reference'
EV=1.602176634e-12
KB=1.380649e-16
C=2.99792458e10
CHI=np.array([13.598434599702,24.587389011,54.41776])
EPS=np.finfo(float).eps
SOURCE=ROOT/'intake/source_samples/rei_bianchi_PR154/research/rei_c16_photo_reaction_20261016/source_aware.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='f4c5ff49f9e09a2123f3830160e857beb9c224deafc9ff379d6199829013bbf4'
spec=importlib.util.spec_from_file_location('immutable_photo_reference',SOURCE)
photo_reference=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=photo_reference
spec.loader.exec_module(photo_reference)

class Coefficients:
    def __init__(self,library=OUT/'grackle_reference.so'):
        self.lib=ctypes.CDLL(str(library));self.fn=self.lib.c16b_reference_coefficients
        self.fn.argtypes=[ctypes.c_double,ctypes.POINTER(ctypes.c_double)];self.fn.restype=ctypes.c_int
    def __call__(self,t):
        values=(ctypes.c_double*17)()
        if self.fn(t,values):raise ValueError(f'C coefficient T domain {t!r}')
        a=np.array(values)
        low=t/11605.<=.8
        return dict(ci_cm3_s=a[:3],rr_cm3_s=a[3:6],dr_cm3_s=float(a[6]),ce_erg=a[7:10],rr_cooling_erg_cm3_s=a[10:13],dr_raw_cooling_erg_cm3_s=float(a[13]),freefree_erg_cm3_s=float(a[14]),dr_cooling_erg_cm3_s=float(a[16]),k4_total=float(a[15]),ci_floor_cm3_s=np.where(low & (a[:3]==1e-20),a[:3],0.),ce_cap_erg=np.where(np.array([118348.,13179.,473638.])/t>math.log(1e30),a[7:10],0.),dr_excluded_erg_cm3_s=float(a[13]) if low else 0.,dr_low_branch=low)

def thermal(fractions,t,nh,nhe):
    x,y,z=fractions;ne=nh*x+nhe*(y+2*z)
    return 1.5*KB*t*(nh+nhe+ne)/nh

class Physics:
    def __init__(self,nh,nhe,tcmb,energies,coefficients=None):
        self.nh=float(nh);self.nhe=float(nhe);self.tcmb=float(tcmb)
        self.energies=np.asarray(energies,dtype=float);self.coefficients=coefficients or Coefficients()
        self.sigma=np.array([[photo_reference.verner_mb(i,float(e))*1e-18 for i in range(3)] for e in self.energies])
    def point(self,state):
        x,y,z,w,*photons=map(float,state);photons=np.array(photons)
        nh,nhe=self.nh,self.nhe;ne=nh*x+nhe*(y+2*z);particles=nh+nhe+ne
        t=2*nh*w/(3*KB*particles)
        if not(np.isfinite(state).all() and 0<=x<=1 and y>=0 and z>=0 and y+z<=1 and w>0 and (photons>=0).all()):
            raise ValueError(f'Python reference inadmissible state {state}')
        rates=self.coefficients(t)
        absr=np.array([nh*(1-x),nhe*(1-y-z),nhe*y]);ions=np.array([nh*x,nhe*y,nhe*z])
        gamma=C*nh*np.sum(photons[:,None]*self.sigma,axis=0)
        heat=C*nh*EV*np.sum(photons[:,None]*self.sigma*(self.energies[:,None]-CHI),axis=0)
        pe=absr*gamma;ci=ne*absr*rates['ci_cm3_s'];rr=ne*ions*rates['rr_cm3_s'];dr=ne*ions[1]*rates['dr_cm3_s']
        ci_sink=CHI*EV*ci;rr_sink=ne*ions*rates['rr_cooling_erg_cm3_s'];dr_sink=ne*ions[1]*rates['dr_cooling_erg_cm3_s']
        ce=np.array([ne*absr[0],ne*ne*ions[1],ne*ions[1]])*rates['ce_erg']
        ff=ne*(ions[0]+ions[1]+4*ions[2])*rates['freefree_erg_cm3_s']
        forward=pe+ci;net_h=forward[0]-rr[0];net_he1=forward[1]-rr[1]-dr;net_he2=forward[2]-rr[2]
        dne=net_h+net_he1+net_he2
        species=np.array([-net_h,net_h,-net_he1,net_he1-net_he2,net_he2,dne])
        fractions=np.array([net_h/nh,(net_he1-net_he2)/nhe if nhe else 0.,net_he2/nhe if nhe else 0.])
        arad=8*math.pi**5*KB**4/(15*(6.62607015e-27)**3*C**3)
        cmb_coeff=4*6.6524587051e-25*arad*KB/(9.1093837139e-28*C)
        cmb=cmb_coeff*ne*self.tcmb**4*(self.tcmb-t)
        photo_heat=float(np.sum(absr*heat));photo_bind=float(np.sum(CHI*EV*pe));capture=float(np.sum(CHI*EV*rr)+CHI[1]*EV*dr)
        radiative=float(np.sum(rr_sink)+dr_sink+np.sum(ce)+ff)
        micro=photo_heat-float(np.sum(ci_sink))-radiative+cmb
        binding=photo_bind+float(np.sum(ci_sink))-capture;escape=capture+radiative
        d_w=micro/nh;d_t=2*nh*d_w/(3*KB*particles)-t*dne/particles
        pdot=-C*(self.sigma@absr)*photons
        low=t/11605.<=.8
        floors=np.where(low & (rates['ci_cm3_s']==1e-20),rates['ci_cm3_s'],0.)
        caps=np.where(np.array([118348.,13179.,473638.])/t>math.log(1e30),rates['ce_erg'],0.)
        result=dict(fraction_dt=fractions,species_chemical_cm3_s=species,w_dt_erg_per_h_s=d_w,temperature_dt_k_s=d_t,photo_events_cm3_s=pe,ci_events_cm3_s=ci,rr_events_cm3_s=rr,dr_events_cm3_s=dr,ci_thermal_sink_erg_cm3_s=ci_sink,rr_thermal_sink_erg_cm3_s=rr_sink,dr_thermal_sink_erg_cm3_s=dr_sink,ce_thermal_sink_erg_cm3_s=ce,freefree_thermal_sink_erg_cm3_s=ff,thermal_micro_erg_cm3_s=micro,binding_micro_erg_cm3_s=binding,escape_erg_cm3_s=escape,cmb_to_gas_erg_cm3_s=cmb,photo_input_erg_cm3_s=photo_bind+photo_heat,expansion_work_erg_cm3_s=0.,ci_floor_events_cm3_s=ne*absr*floors,ce_cap_cooling_erg_cm3_s=np.array([ne*absr[0],ne*ne*ions[1],ne*ions[1]])*caps,excluded_dr_cooling_erg_cm3_s=ne*ions[1]*(rates['dr_raw_cooling_erg_cm3_s'] if low else 0.))
        return dict(d=np.r_[fractions,d_w,pdot],temperature=t,nh=nh,nhe=nhe,tcmb=self.tcmb,actual_energy_ev=self.energies,rhs=result,rates=rates,photo=dict(gamma_s=gamma,heat_erg_per_absorber_s=heat))

class NativeServer:
    def __init__(self,binary,q=0.,helium=True):
        self.command=[str(binary),'rhs','.1',str(q),'1' if helium else '0']
        self.stderr=(OUT/f'native_server_q{q}_he{int(helium)}.stderr').open('w')
        self.process=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
    def point(self,state):
        self.process.stdin.write(' '.join(format(float(x),'.17e') for x in state)+'\n');self.process.stdin.flush()
        line=self.process.stdout.readline()
        if not line:raise RuntimeError(f'native server exited {self.process.poll()}')
        return json.loads(line)
    def close(self):
        self.process.stdin.close();self.process.wait(timeout=5);self.stderr.close()

def serializable(value):
    if isinstance(value,dict):return {k:serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serializable(v) for v in value]
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    return value

def compare_point(native,reference,case):
    checks=[]
    native=dict(native);native['photo']={k:native[k] for k in ['gamma_s','heat_erg_per_absorber_s']}
    native['rates']=dict(native['rates'],k4_total=native['rates']['rr_cm3_s'][1]+native['rates']['dr_cm3_s'])
    native['derivative']={'d':native['d']};reference=dict(reference,derivative={'d':reference['d']})
    for group in ['rates','rhs','photo','derivative']:
        if group not in native:continue
        for key,a in reference[group].items():
            if key not in native[group]:continue
            aa=np.asarray(native[group][key],float).ravel();bb=np.asarray(a,float).ravel()
            if aa.shape!=bb.shape:raise ValueError(f'shape {group}.{key}')
            for i,(actual,want) in enumerate(zip(aa,bb)):
                exactzero=actual==0 or want==0
                rel=abs(actual-want)/max(abs(actual),abs(want)) if actual or want else 0.
                # Cancellation quantities also receive a gross-term roundoff bound.
                cancellation=key in ['fraction_dt','species_chemical_cm3_s','w_dt_erg_per_h_s','temperature_dt_k_s','thermal_micro_erg_cm3_s','binding_micro_erg_cm3_s']
                gross=sum(float(np.sum(np.abs(v))) for k,v in reference['rhs'].items() if ('_events_' in k)) if 'fraction' in key or 'species' in key else sum(float(np.sum(np.abs(reference['rhs'][k]))) for k in ['photo_input_erg_cm3_s','thermal_micro_erg_cm3_s','binding_micro_erg_cm3_s','escape_erg_cm3_s','cmb_to_gas_erg_cm3_s'])
                # Direct values must meet the source-locked relative tolerance; gross cancellation is reported separately.
                passed=(actual==want) if exactzero else rel<=1e-10
                checks.append(dict(case=case,field=group+'.'+key,index=i,native=float(actual),reference=float(want),relative_error=float(rel),structural_zero=exactzero,pass_=bool(passed),cancellation_gross=float(gross) if cancellation else None))
    return checks

# Integrals: escape,CMB,thermal,binding,photo input,sourceU,sourceN,photo[3],CI[3],RR[3],DR.
INTEGRALS=['escape_ev_per_h','cmb_ev_per_h','thermal_micro_ev_per_h','binding_micro_ev_per_h','photo_input_ev_per_h','source_ev_per_h','source_n_per_h',*[f'photo_events_{i}' for i in range(3)],*[f'ci_events_{i}' for i in range(3)],*[f'rr_events_{i}' for i in range(3)],'dr_events']

def integrate(physics,initial,horizon,rtol=1e-9,times=None,source=None,edges=()):
    initial=np.asarray(initial,float);w0=initial[3];state=np.r_[initial,np.zeros(len(INTEGRALS))];state[3]/=w0
    checkpoints=[];stats={'nfev':0,'njev':0,'nlu':0};begun=time.monotonic()
    def unpack(packed):
        full=np.zeros(7+len(INTEGRALS));full[active]=packed
        for k in log_modes:
            full[k]=log_scales[k]*math.exp(full[k])
            if full[k]==0.:raise FloatingPointError('Positive log-photon mode underflowed; no clipping admitted')
        return full
    def fun(t,packed):
        scaled=unpack(packed)
        physical=scaled[:7].copy();physical[3]*=w0;p=physics.point(physical);r=p['rhs'];birth=np.zeros(3) if source is None else np.asarray(source(segment_midpoint),float)
        dy=p['d'].copy();dy[3]/=w0;dy[4:7]+=birth
        energy=lambda k:r[k]/(physics.nh*EV)
        integ=[energy('escape_erg_cm3_s'),energy('cmb_to_gas_erg_cm3_s'),energy('thermal_micro_erg_cm3_s'),energy('binding_micro_erg_cm3_s'),energy('photo_input_erg_cm3_s'),float(birth@physics.energies),float(sum(birth)),*(r['photo_events_cm3_s']/physics.nh),*(r['ci_events_cm3_s']/physics.nh),*(r['rr_events_cm3_s']/physics.nh),r['dr_events_cm3_s']/physics.nh]
        if time.monotonic()-begun>290:raise TimeoutError('reference per-campaign wall budget290s')
        full=np.r_[dy,integ]
        for k in log_modes:
            # Positive homogeneous photon modes: d log(N/N0)/dt=-c*kappa.
            x,y,z=physical[:3];absorbers=np.array([physics.nh*(1-x),physics.nhe*(1-y-z),physics.nhe*y])
            full[k]=-C*float(physics.sigma[k-4]@absorbers)
        return full[active]
    edges=sorted(set([0.,float(horizon),*[float(e) for e in edges if 0<e<horizon]]))
    histories=[];dense_segments=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        segment_midpoint=(lo+hi)/2
        birth=np.zeros(3) if source is None else np.asarray(source(segment_midpoint),float)
        excluded=[k for k in range(4,7) if state[k]==0. and birth[k-4]==0.]
        active=np.array([k for k in range(len(state)) if k not in excluded])
        log_modes=[k for k in range(4,7) if state[k]>0. and birth[k-4]==0.]
        log_scales={k:state[k] for k in log_modes}
        packed=state.copy()
        for k in log_modes:packed[k]=0.
        eval_times=None if times is None else np.array([v for v in times if lo<=v<=hi])
        if eval_times is not None:eval_times=np.unique(np.r_[eval_times,hi])
        sol=solve_ivp(fun,(lo,hi),packed[active],method='Radau',rtol=rtol,atol=1e-12,t_eval=eval_times,dense_output=True)
        for k in stats:stats[k]+=getattr(sol,k)
        if not sol.success:raise RuntimeError(sol.message)
        state=unpack(sol.y[:,-1])
        dense_segments.append(dict(lo=lo,hi=hi,active=active.tolist(),log_modes=log_modes,log_scales=log_scales,w0=w0,pieces=[dict(t_old=v.t_old,t=v.t,h=v.h,y_old=v.y_old.tolist(),Q=v.Q.tolist()) for v in sol.sol.interpolants]))
        for t,y in zip(sol.t,sol.y.T):
            yy=unpack(y);yy[3]*=w0;histories.append([float(t),*yy.tolist()])
        checkpoints.append(dict(lo=lo,hi=hi,message=sol.message,endpoint=float(sol.t[-1])))
    physical=state[:7].copy();physical[3]*=w0;integral=dict(zip(INTEGRALS,state[7:].tolist()))
    def binding(g):x,y,z=g[:3];return CHI[0]*x+(physics.nhe/physics.nh)*(CHI[1]*y+(CHI[1]+CHI[2])*z)
    initial_energy=float(initial[4:7]@physics.energies+initial[3]/EV+binding(initial));final_energy=float(physical[4:7]@physics.energies+physical[3]/EV+binding(physical))
    residual=final_energy-initial_energy+integral['escape_ev_per_h']-integral['cmb_ev_per_h']-integral['source_ev_per_h']
    scale=abs(initial_energy)+abs(final_energy)+abs(integral['escape_ev_per_h'])+abs(integral['cmb_ev_per_h'])+abs(integral['source_ev_per_h'])
    photon=float(sum(physical[4:7])-sum(initial[4:7])-integral['source_n_per_h']+sum(integral[f'photo_events_{i}'] for i in range(3)))
    electron=lambda g:g[0]+(physics.nhe/physics.nh)*(g[1]+2*g[2])
    charge=electron(physical)-electron(initial)-sum(integral[f'photo_events_{i}']+integral[f'ci_events_{i}']-integral[f'rr_events_{i}'] for i in range(3))+integral['dr_events']
    return dict(endpoint=physical,temperature=physics.point(physical)['temperature'],history=histories,dense_segments=dense_segments,history_columns=['time_s','xHII','yHeII','zHeIII','w_erg_per_h','N20','N40','N80',*INTEGRALS],integrals=integral,stats=stats,wall_seconds=time.monotonic()-begun,rtol=rtol,atol_scaled=1e-12,segments=checkpoints,ledgers=dict(energy_residual_ev_per_h=residual,energy_scale_ev_per_h=scale,energy_normalized=abs(residual)/scale if scale else abs(residual),photon_number_residual=photon,electron_residual=charge))

def dense_state(reference,t):
    for segment in reference['dense_segments']:
        if segment['lo']<=t<=segment['hi']:
            piece=next(p for p in segment['pieces'] if p['t_old']<=t<=p['t'])
            x=(t-piece['t_old'])/piece['h'];q=np.asarray(piece['Q']);packed=np.asarray(piece['y_old'])+q@np.power(x,np.arange(1,q.shape[1]+1))
            full=np.zeros(7+len(INTEGRALS));full[segment['active']]=packed
            for k in segment['log_modes']:full[k]=float(segment['log_scales'].get(str(k),segment['log_scales'].get(k)))*math.exp(full[k])
            full[3]*=segment['w0'];return full
    raise ValueError('Requested reference time outside dense solution')

def error_norm(initial,reference,native,physics,emitted=0.):
    a=np.asarray(native,float);b=np.asarray(reference,float);initial=np.asarray(initial,float)
    temp=physics.point(a)['temperature'];tref=physics.point(b)['temperature'];t0=physics.point(initial)['temperature']
    return float(max(np.max(abs(a[:3]-b[:3])),abs(a[3]-b[3])/max(initial[3],b[3]),abs(temp-tref)/max(t0,tref),sum(abs(a[4:7]-b[4:7]))/max(sum(initial[4:7])+emitted,1e-8)))

def native_state(row):
    n=int(row['transport_cells']);photons=row['photons']
    counts=[sum(photons[i*n:(i+1)*n]) for i in range(3)]
    if abs(sum(counts)-row['photon_number'])>1e-12*max(row['photon_number'],1e-30):
        raise ValueError('Native photons populate more than the three delta rays; not the delta ODE model')
    return np.r_[row['fractions'],row['w'],counts]

def campaign(binary,manifest,reuse_reference=False,refresh_case=None):
    fixtures=json.loads(manifest.read_text());native_dir=manifest.parent;records=[]
    for fixture in fixtures:
        name=fixture['name']
        if fixture['source']=='Md14':
            records.append(dict(case=name,status='NOT_COMPARED_DIFFERENT_SPECTRAL_MODEL',reason='Native MD14 continuous spectrum is not represented by three delta nodes; native refinement owns this axis.'));continue
        paths=sorted(native_dir.glob(name+'_n[0-9]*.jsonl'))
        paths+=sorted((native_dir.parent/'temporal_refine').glob(name+'_n[0-9]*.jsonl'))
        paths+=sorted((native_dir.parent/'temporal_refine1024').glob(name+'_n[0-9]*.jsonl'))
        paths+=sorted((native_dir.parent/'pulse_repair').glob(name+'_n[0-9]*.jsonl'))
        import re
        paths=[p for p in paths if re.fullmatch(re.escape(name)+r'_n[0-9]+',p.stem)]
        if not paths:
            records.append(dict(case=name,status='NOT_RUN_NATIVE_HISTORY_MISSING'));continue
        native_rows={int(p.stem.rsplit('_n',1)[1]):[json.loads(l) for l in p.read_text().splitlines()] for p in paths}
        native_paths={int(p.stem.rsplit('_n',1)[1]):p for p in paths}
        initial_row=native_rows[min(native_rows)][0];initial=native_state(initial_row)
        physics=Physics(initial_row['nh'],initial_row['nhe'],initial_row['tcmb'],initial_row['actual_delta_energies_ev'])
        horizon=fixture['horizon_s'];times=sorted(set([r['time_s'] for rows in native_rows.values() for r in rows]+[horizon*k/512 for k in range(513)]))
        source=None;edges=[]
        if fixture['source'].startswith('Pulse'):
            import re
            vals=dict((k,float(v)) for k,v in re.findall(r'(on|off|rate): ([0-9.eE+\-]+)',fixture['source']))
            edges=[vals['on'],vals['off']]
            source=lambda t,values=vals: np.array([.5,.3,.2])*values['rate'] if values['on']<=t<values['off'] else np.zeros(3)
        if reuse_reference and name!=refresh_case:
            reference=json.loads((OUT/(name+'_radau.json')).read_text());tight=json.loads((OUT/(name+'_radau_tight.json')).read_text())
        else:
            reference=integrate(physics,initial,horizon,rtol=1e-9,times=times,source=source,edges=edges)
            (OUT/(name+'_radau.json')).write_text(json.dumps(serializable(reference),indent=2)+'\n')
            tight=integrate(physics,initial,horizon,rtol=1e-10,times=times,source=source,edges=edges)
            (OUT/(name+'_radau_tight.json')).write_text(json.dumps(serializable(tight),indent=2)+'\n')
        emitted=tight['integrals']['source_n_per_h'];tight_norm=error_norm(initial,tight['endpoint'],reference['endpoint'],physics,emitted)
        trajectory={float(r[0]):np.array(r[1:8]) for r in tight['history']}
        emitted_by_time={float(r[0]):float(r[8+INTEGRALS.index('source_n_per_h')]) for r in tight['history']}
        comparisons=[]
        for n,rows in sorted(native_rows.items()):
            errors=[];fixed_errors=[]
            for row in rows:
                t=row['time_s']
                if 'dense_segments' in tight:
                    values=dense_state(tight,t);at=values[:7];current_emitted=values[7+INTEGRALS.index('source_n_per_h')]
                elif t not in trajectory:
                    nearest=min(trajectory,key=lambda v:abs(v-t))
                    if abs(nearest-t)>128*EPS*max(horizon,1.):raise ValueError('Cached reference lacks required common time')
                    t=nearest
                    at=trajectory[t];current_emitted=emitted_by_time[t]
                else:at=trajectory[t];current_emitted=emitted_by_time[t]
                err=error_norm(initial,at,native_state(row),physics,current_emitted);errors.append(err)
                observation=t/horizon*32
                if abs(observation-round(observation))<1e-9:fixed_errors.append(err)
            endpoint=error_norm(initial,tight['endpoint'],native_state(rows[-1]),physics,emitted)
            comparisons.append(dict(n=n,endpoint_error=endpoint,max_common_time_error=max(errors),max_fixed_t32_observation_error=max(fixed_errors),fixed_observation_count=len(fixed_errors),final_temperature=rows[-1]['temperature'],reference_temperature=tight['temperature'],native_history_path=str(native_paths[n]),history_source_sha256=hashlib.sha256(native_paths[n].read_bytes()).hexdigest()))
        order=None
        if len(comparisons)>=2 and comparisons[-1]['endpoint_error']>1e-10:
            order=math.log(comparisons[-2]['endpoint_error']/comparisons[-1]['endpoint_error'],2)
        common_order=math.log(comparisons[-2]['max_fixed_t32_observation_error']/comparisons[-1]['max_fixed_t32_observation_error'],2) if len(comparisons)>=2 and comparisons[-1]['max_fixed_t32_observation_error']>1e-10 else None
        finest=comparisons[-1]['endpoint_error'];decreasing=all(b['endpoint_error']<a['endpoint_error'] for a,b in zip(comparisons[:-1],comparisons[1:]))
        required=name in ['recomb8000','collision1e5','mixed1e4']
        passed=(finest<=.005 and comparisons[-1]['max_fixed_t32_observation_error']<=.005 and decreasing and order is not None and .7<=order<=1.4 and common_order is not None and .7<=common_order<=1.4) if required else True
        tightening_pass=tight_norm<.01*finest or tight_norm<1e-7
        status=('PASS_MECHANICAL_CRITERIA' if required else 'CONTROL_COMPARISON_RECORDED') if passed and tightening_pass else 'HOLD_MEASURED_CRITERIA'
        if not required and finest>.005:status='CONTROL_VALIDATED_ACCURACY_NOT_ADMITTED'
        record=dict(case=name,status=status,required_smooth_family=required,accuracy_gate='endpoint AND max fixed original t32 observation norm <=.005; endpoint and fixed-grid orders .7..1.4 for required smooth families; each native grid maximum also reported',comparison_reference_rtol=1e-10,comparison_reference_reason='Preauthorized tighter reference meets all-time ledger target; baseline1e-9 retained as coarser reference control',comparisons=comparisons,finest_two_order=order,finest_two_common_time_order=common_order,strictly_decreasing=decreasing,reference_tightening_norm=tight_norm,reference_tightening_pass=tightening_pass,reference_ledgers=tight['ledgers'],reference_stats=reference['stats'],reference_tight_stats=tight['stats'],source_schedule=fixture['source'],physical_energies_ev=physics.energies.tolist(),initial=initial.tolist())
        records.append(record)
        (OUT/'trajectory_summary.json').write_text(json.dumps(serializable(records),indent=2)+'\n')
        print(name,record['status'],'error',finest,'order',order,flush=True)
    (OUT/'trajectory_summary.json').write_text(json.dumps(serializable(records),indent=2)+'\n')
    summarize_refinements(native_dir.parent)
    audit_reference_ledgers(records)
    return records

def summarize_refinements(native_root):
    results=[]
    def ends(path):
        with path.open() as stream:
            first=json.loads(next(stream));last=first
            for line in stream:
                if line.strip():last=json.loads(line)
        return first,last
    def difference(a,b,initial):
        scale_n=max(initial['photon_number']+b['source_n']-initial['source_n'],1e-8)
        scale_u=max(initial['photon_energy_ev_per_h']+b['source_u']-initial['source_u'],1e-8)
        values=dict(fractions_max_abs=float(np.max(abs(np.array(a['fractions'])-b['fractions']))),thermal_relative=abs(a['w']-b['w'])/max(initial['w'],b['w']),temperature_relative=abs(a['temperature']-b['temperature'])/max(initial['temperature'],b['temperature']),photon_number_normalized=abs(a['photon_number']-b['photon_number'])/scale_n,photon_energy_normalized=abs(a['photon_energy_ev_per_h']-b['photon_energy_ev_per_h'])/scale_u,angular_moment_normalized=float(np.max(abs(np.array(a['angular_energy_moments'])-b['angular_energy_moments'])))/scale_u)
        values['max_normalized']=max(values.values());return values
    for folder in ['refinement','cohort_refinement']:
        directory=native_root/folder
        if not directory.exists():continue
        for axis,levels in [('spectral_sub',[16,32,64]),('angular_mu',[8,16,32]),('transport_cells',[32,64,128])]:
            paths=[directory/f'{axis}{n}.jsonl' for n in levels]
            if not all(p.exists() for p in paths):continue
            rows=[ends(p) for p in paths];finest=rows[-1][1]
            to_finest=[difference(row[1],finest,row[0]) for row in rows]
            successive=[difference(rows[i][1],rows[i+1][1],rows[i][0]) for i in range(2)]
            diff=[v['max_normalized'] for v in successive]
            reduced=diff[1]<diff[0] or max(diff)<1e-7
            results.append(dict(campaign=folder,axis=axis,levels=levels,comparisons_to_finest=to_finest,successive_differences=successive,finest_neighbor_pass=diff[-1]<=.005,successive_reduction_or_below_floor=reduced,observed_mechanical_gate=diff[-1]<=.005 and reduced,initials=[{k:r[0][k] for k in ['a','q_ref','b','photon_number','photon_energy_ev_per_h','temperature','source_n','source_u','transport_cells','source_subdivisions','native_angles']} for r in rows],endpoints=[{k:r[1][k] for k in ['fractions','w','temperature','photon_number','photon_energy_ev_per_h','angular_energy_moments','invariants']} for r in rows],files=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],claim_scope='finite measured grid differences; no equality to three-node Radau or continuum-error claim'))
    (OUT/'refinement_observations.json').write_text(json.dumps(serializable(results),indent=2)+'\n')

def audit_reference_ledgers(records):
    reports={}
    for case in records:
        if 'comparisons' not in case:continue
        name=case['case'];initial=np.array(case['initial']);native=json.loads(Path(case['comparisons'][0]['native_history_path']).read_text().splitlines()[0]);ratio=native['nhe']/native['nh'];energy=np.array(case['physical_energies_ev'])
        binding=lambda g:CHI[0]*g[0]+ratio*(CHI[1]*g[1]+sum(CHI[1:])*g[2])
        electron=lambda g:g[0]+ratio*(g[1]+2*g[2])
        e0=[float(initial[4:7]@energy),initial[3]/EV,binding(initial)]
        reports[name]={}
        for suffix in ['radau','radau_tight']:
            reference=json.loads((OUT/f'{name}_{suffix}.json').read_text());rows=[]
            for row in reference['history']:
                g=np.array(row[1:8]);v=dict(zip(INTEGRALS,row[8:]));pe=sum(v[f'photo_events_{i}'] for i in range(3));ci=sum(v[f'ci_events_{i}'] for i in range(3));rr=sum(v[f'rr_events_{i}'] for i in range(3));dr=v['dr_events'];es=[float(g[4:7]@energy),g[3]/EV,binding(g)]
                er=sum(es)-sum(e0)+v['escape_ev_per_h']-v['cmb_ev_per_h']-v['source_ev_per_h'];escale=sum(abs(k) for k in e0+es)+abs(v['escape_ev_per_h'])+abs(v['cmb_ev_per_h'])+abs(v['source_ev_per_h'])
                nr=sum(g[4:7])-sum(initial[4:7])-v['source_n_per_h']+pe;nscale=sum(abs(g[4:7]))+sum(abs(initial[4:7]))+abs(v['source_n_per_h'])+abs(pe)
                cr=electron(g)-electron(initial)-pe-ci+rr+dr;cscale=abs(electron(g))+abs(electron(initial))+abs(pe)+abs(ci)+abs(rr)+abs(dr)
                rows.append(dict(time_s=row[0],energy_residual_ev_per_h=er,energy_scale_ev_per_h=escale,energy_normalized=abs(er)/escale if escale else abs(er),photon_residual_per_h=nr,photon_scale_per_h=nscale,photon_normalized=abs(nr)/nscale if nscale else abs(nr),electron_residual_per_h=cr,electron_scale_per_h=cscale,electron_normalized=abs(cr)/cscale if cscale else abs(cr)))
            maximum={k:max(v[k] for v in rows) for k in ['energy_normalized','photon_normalized','electron_normalized']};maximum['all_within_1e-10']=all(v<=1e-10 for v in maximum.values());reports[name][suffix]=maximum
            (OUT/f'{name}_{suffix}_all_time_ledgers.json').write_text(json.dumps(serializable(rows),indent=2)+'\n')
    (OUT/'reference_ledger_summary_both_tolerances.json').write_text(json.dumps(reports,indent=2)+'\n')
    return reports

def main():
    p=argparse.ArgumentParser();p.add_argument('--point-binary',type=Path);p.add_argument('--manifest',type=Path);p.add_argument('--point-only',action='store_true');p.add_argument('--skip-point',action='store_true');p.add_argument('--reuse-reference',action='store_true');p.add_argument('--refresh-case');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if not a.point_binary:raise SystemExit('--point-binary required')
    if a.skip_point:
        assert json.loads((OUT/'point_summary.json').read_text())['failures']==0
        records=campaign(a.point_binary,a.manifest,a.reuse_reference,a.refresh_case)
        if any(r['status'].startswith('HOLD') for r in records):raise SystemExit(3)
        return
    allchecks=[];raw=[]
    for q in [0.,-.1,.1]:
        for helium in [True,False]:
            server=NativeServer(a.point_binary,q,helium)
            try:
                probe=server.point([.31,.23 if helium else 0.,.17 if helium else 0.,1e-12,0.,0.,0.]);physics=Physics(probe['nh'],probe['nhe'],probe['tcmb'],probe['actual_energy_ev'])
                for t in [10.,100.,8000.,1e4,1e5]:
                    f=[.31,.23 if helium else 0.,.17 if helium else 0.];w=thermal(f,t,physics.nh,physics.nhe)
                    for photons in [[0.,0.,0.],[.03,.02,.01]]:
                        state=np.r_[f,w,photons];native=server.point(state);ref=physics.point(state);case=f'q{q}_he{int(helium)}_T{t}_photo{int(bool(sum(photons)))}';allchecks+=compare_point(native,ref,case);raw.append(dict(case=case,state=state,native=native,reference=ref))
            finally:server.close()
    (OUT/'point_raw.json').write_text(json.dumps(serializable(raw),indent=2)+'\n');(OUT/'point_checks.json').write_text(json.dumps(serializable(allchecks),indent=2)+'\n')
    summary=dict(cases=len(raw),checks=len(allchecks),failures=sum(not x['pass_'] for x in allchecks),max_relative_error=max(x['relative_error'] for x in allchecks),coefficient_authority='unchanged pinned literal-C Grackle bodies; independent Python full RHS',scientific_admission='NOT_ISSUED')
    (OUT/'point_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
    if summary['failures']:raise SystemExit(2)
    if a.manifest:
        records=campaign(a.point_binary,a.manifest,a.reuse_reference,a.refresh_case)
        if any(r['status'].startswith('HOLD') for r in records):raise SystemExit(3)

if __name__=='__main__':main()
