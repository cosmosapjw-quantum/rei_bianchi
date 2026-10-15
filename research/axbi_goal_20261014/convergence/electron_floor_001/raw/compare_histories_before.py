#!/usr/bin/env python3
"""Completed H/He history diagnostics at frozen matched ln(a); no solver.

Input JSON descriptors bind history, abundances, config, source_identity and
terminal paths and SHA256. Missing/incomplete inputs yield null typed HOLD.
Sampled differences are not continuous suprema or numerical accuracy admission.
"""
import argparse,array,bisect,csv,hashlib,json,math,pathlib,sys,tempfile
A0=1/21;A1=1/5;L0=math.log(A0);L1=math.log(A1)
SPECIES=('H_I','H_II','He_I','He_II','He_III','electron')
FIELDS={'x_HI':'x_HI','x_HII':'x_HII','x_HeI':'x_HeI','x_HeII':'x_HeII','x_HeIII':'x_HeIII','ne_cm3':'ne_proper_cm3','Tgas_K':'temperature_K','U0_eV_per_H':'J0_photon_u_eV_per_H','U2_eV_per_H':'J2_photon_u_eV_per_H'}
CLOCK='elapsed proper seconds since zbar20'
class InputHold(Exception):
    def __init__(self,status,field):self.status=status;self.field=field;super().__init__(status+':'+field)
def hashfile(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def bound(spec,role):
    desc=spec.get(role,{})
    if not desc.get('path') or not desc.get('sha256'):raise InputHold('HOLD_INPUT_IDENTITY_MISSING',spec.get('id','?')+'.'+role)
    p=pathlib.Path(desc['path'])
    if not p.is_file():raise InputHold('HOLD_INPUT_MISSING',str(p))
    if hashfile(p)!=desc['sha256']:raise InputHold('BYTE_IDENTITY_MISMATCH_FROZEN_REDUCTION_INPUT',str(p))
    return p
def finite(value,field):
    x=float(value)
    if not math.isfinite(x):raise InputHold('HOLD_INVALID_SAVED_VALUE',field)
    return x

def load_case(spec):
    paths={role:bound(spec,role) for role in ['history','abundances','config','source_identity','terminal']}
    terminal=dict(line.split('=',1) for line in paths['terminal'].read_text().splitlines() if '=' in line)
    if terminal.get('status')!='COMPLETE_REPRESENTED_INTERVAL':raise InputHold('UNKNOWN_INCOMPLETE_HISTORY',str(paths['terminal']))
    cfg=dict(line.split('=',1) for line in paths['config'].read_text().splitlines() if '=' in line)
    if float(cfg.get('end_zbar','nan'))!=4.0:raise InputHold('UNKNOWN_FULL_INTERVAL_NOT_COMPLETED',str(paths['config'])+'.end_zbar')
    if spec.get('clock_origin')!=CLOCK:raise InputHold('HOLD_CLOCK_ORIGIN_MISSING_OR_DIFFERENT',spec['id']+'.clock_origin')
    series={name:array.array('d') for name in ['L','time_s','xe',*FIELDS,*('Y_'+k for k in SPECIES)]}
    history_times=[];history_nh=array.array('d')
    with paths['history'].open() as f:
        for row in csv.DictReader(f):
            if row['case_id']!=spec['id']:raise InputHold('HOLD_CASE_ID_MISMATCH',str(paths['history']))
            a=finite(row['a'],'a');t=finite(row['time_s'],'time_s')
            if a<=0 or (series['L'] and (math.log(a)<=series['L'][-1] or t<=series['time_s'][-1])):raise InputHold('HOLD_MISSING_OR_INVALID_ORDERED_ROW',str(paths['history']))
            series['L'].append(math.log(a));series['time_s'].append(t);history_times.append(t)
            nh=finite(row['nH_proper_cm3'],'nH');ne=finite(row['ne_proper_cm3'],'ne')
            if nh<=0 or ne<0:raise InputHold('HOLD_DENSITY_DOMAIN',str(paths['history']))
            history_nh.append(nh);series['xe'].append(finite(ne/nh,'computed xe'))
            for name,column in FIELDS.items():series[name].append(finite(row[column],column))
            for name in ['x_HI','x_HII','x_HeI','x_HeII','x_HeIII']:
                if not 0<=series[name][-1]<=1:raise InputHold('HOLD_FRACTION_DOMAIN',name)
            if abs(series['x_HI'][-1]+series['x_HII'][-1]-1)>1e-12 or abs(series['x_HeI'][-1]+series['x_HeII'][-1]+series['x_HeIII'][-1]-1)>1e-12:raise InputHold('HOLD_ELEMENT_FRACTION_SUM',spec['id'])
            if series['Tgas_K'][-1]<=0:raise InputHold('HOLD_TEMPERATURE_DOMAIN',spec['id'])
    if not history_times:raise InputHold('UNKNOWN_EMPTY_HISTORY',str(paths['history']))
    if series['L'][0]!=L0 or series['L'][-1]!=L1 or history_times[0]!=0:raise InputHold('UNKNOWN_FULL_INTERVAL_OR_ORIGIN_NOT_COVERED',spec['id'])
    if len(history_times)!=int(terminal.get('accepted','-2'))+1:raise InputHold('HOLD_MISSING_ACCEPTED_ROWS',spec['id'])
    if float(terminal.get('a','nan'))!=A1:raise InputHold('UNKNOWN_TERMINAL_ENDPOINT',spec['id'])
    index=0;pending={};pending_t=None;factors=None
    def commit(t,block):
        nonlocal index,factors
        if set(block)!=set(SPECIES) or index>=len(history_times) or t!=history_times[index]:raise InputHold('HOLD_ABUNDANCE_HISTORY_ALIGNMENT',spec['id'])
        nh=block['H_I']['n']+block['H_II']['n'];nhe=sum(block[k]['n'] for k in ['He_I','He_II','He_III']);nb=nh+4*nhe
        if nh<=0 or nhe<=0 or not math.isfinite(nb):raise InputHold('HOLD_SELECTED_HHE_INVENTORY',spec['id'])
        f=(nh/nb,nhe/nb)
        if factors is None:factors=f
        if max(abs(x-y) for x,y in zip(f,factors))>1e-12:raise InputHold('HOLD_CHANGING_ELEMENT_INVENTORY',spec['id'])
        for k in SPECIES:
            y=block[k]['Y']
            if y<0 or abs(y-block[k]['n']/nb)>1e-12:raise InputHold('HOLD_BARYON_NORMALIZATION',k)
            series['Y_'+k].append(y)
        if abs(sum(block[k]['A']*block[k]['Y'] for k in SPECIES)-1)>1e-12:raise InputHold('HOLD_A_Y_SUM',spec['id'])
        if abs(nh/history_nh[index]-1)>1e-12:raise InputHold('HOLD_HISTORY_H_DENSITY_ALIGNMENT',spec['id'])
        for species,name,denominator in [('H_I','x_HI',nh),('H_II','x_HII',nh),('He_I','x_HeI',nhe),('He_II','x_HeII',nhe),('He_III','x_HeIII',nhe)]:
            if abs(block[species]['n']/denominator-series[name][index])>1e-12:raise InputHold('HOLD_HISTORY_IONIC_ALIGNMENT',species)
        expected_ne=block['H_II']['n']+block['He_II']['n']+2*block['He_III']['n']
        if abs(block['electron']['n']-expected_ne)/nh>1e-12:raise InputHold('HOLD_CHARGE_CENSUS',spec['id'])
        if abs(block['electron']['n']/nh-series['xe'][index])>1e-12:raise InputHold('HOLD_HISTORY_ELECTRON_ALIGNMENT',spec['id'])
        index+=1
    with paths['abundances'].open() as f:
        for row in csv.DictReader(f):
            if row['run_id']!=spec['id'] or row['normalization_registry']!='BASELINE_H_HE_CHARGE_AND_BARYON_V1':raise InputHold('HOLD_CASE_OR_REGISTRY_MISMATCH',str(paths['abundances']))
            t=finite(row['time_s'],'abundance time');k=row['species_id']
            if pending_t is not None and t!=pending_t:commit(pending_t,pending);pending={}
            if k in pending:raise InputHold('HOLD_DUPLICATE_SPECIES_ROW',spec['id'])
            n=finite(row['nproper'],'nproper')
            if n<0:raise InputHold('HOLD_NEGATIVE_SAVED_DENSITY',k)
            pending_t=t;pending[k]={'n':n,'Y':finite(row['Ybaryon'],'Y'),'A':int(row['A'])}
    if pending:commit(pending_t,pending)
    if index!=len(history_times):raise InputHold('HOLD_MISSING_ABUNDANCE_ROWS',spec['id'])
    # Bind only read-only frozen completed artifacts, not a changing live CSV.
    for role,p in paths.items():
        if hashfile(p)!=spec[role]['sha256']:raise InputHold('HOLD_INPUT_CHANGED_DURING_REDUCTION',str(p))
    return {'id':spec['id'],'series':series,'factors':factors,'config':cfg,'spec':spec}

def grid():
    result=[L0+(j/1000)*math.log(21/5) for j in range(1001)];result[0]=L0;result[-1]=L1;return result

def interp(xs,ys,x):
    j=bisect.bisect_left(xs,x)
    if j<len(xs) and xs[j]==x:return ys[j]
    if j==0 or j==len(xs):raise InputHold('HOLD_EXTRAPOLATION_REQUIRED',str(x))
    w=(x-xs[j-1])/(xs[j]-xs[j-1]);return (1-w)*ys[j-1]+w*ys[j]

def crossings(case,threshold):
    s=case['series'];x=s['x_HII'];events=[]
    if x[0]==threshold:events.append({'time_s':s['time_s'][0],'zbar':20.0,'left_row':0,'right_row':0,'theta':0.0,'kind':'INITIAL_EXACT_THRESHOLD'})
    for i in range(len(x)-1):
        if x[i]<threshold<=x[i+1]:
            w=(threshold-x[i])/(x[i+1]-x[i]);L=(1-w)*s['L'][i]+w*s['L'][i+1];t=(1-w)*s['time_s'][i]+w*s['time_s'][i+1]
            event={'time_s':t,'zbar':math.exp(-L)-1,'left_row':i,'right_row':i+1,'theta':w,'kind':'UPWARD_BRACKET','left_x_HII':x[i],'right_x_HII':x[i+1],'left_time_s':s['time_s'][i],'right_time_s':s['time_s'][i+1],'left_ln_a':s['L'][i],'right_ln_a':s['L'][i+1]}
            if not events or t!=events[-1]['time_s']:events.append(event)
    return {'target':threshold,'crossing_status':'REACHED' if events else 'NOT_REACHED','first':events[0] if events else None,'additional_upward_crossings':events[1:],'covered_zbar':[20.0,4.0],'note':'No pre-initial crossing inferred when already above threshold' if x[0]>threshold else None}

def floor(name,case):
    if name.startswith('x_') or name=='xe':return 1e-7
    if name=='Tgas_K':return .01
    if name.startswith('Y_'):
        species=name[2:];h,he=case['factors']
        return 1e-7*(h+3*he if species=='electron' else h if species.startswith('H_') else he)
    return None

def compare(reference,candidate):
    if max(abs(x-y) for x,y in zip(reference['factors'],candidate['factors']))>1e-12:raise InputHold('HOLD_UNMATCHED_BARYON_INVENTORY',candidate['id'])
    coords=grid();observables=[k for k in reference['series'] if k not in ['L','time_s']];rows=[];summary=[]
    for name in observables:
        diffs=[]
        for j,L in enumerate(coords):
            a=A0 if j==0 else A1 if j==1000 else math.exp(L);z=1/a-1
            r=interp(reference['series']['L'],reference['series'][name],L);c=interp(candidate['series']['L'],candidate['series'][name],L);diffs.append(c-r)
            rows.append({'candidate':candidate['id'],'reference':reference['id'],'comparison_coordinate':'ZBAR','sample':j,'ln_a':L,'candidate_zbar':z,'reference_zbar':z,'candidate_time_s':interp(candidate['series']['L'],candidate['series']['time_s'],L),'reference_time_s':interp(reference['series']['L'],reference['series']['time_s'],L),'observable':name,'candidate_value':c,'reference_value':r,'difference':c-r,'numerical_error_estimate':None,'interpolation_error_estimate':None,'error_kind':'EMPIRICAL_RESOLUTION_NOT_YET_ESTIMATED','absolute_resolution_floor':floor(name,reference),'result_class':'RESOLUTION_LIMITED'})
        j=max(range(len(diffs)),key=lambda i:abs(diffs[i]));summary.append({'candidate':candidate['id'],'reference':reference['id'],'observable':name,'sampled_sup_absolute_difference':abs(diffs[j]),'sample_at_sup':j,'signed_difference_at_sup':diffs[j],'endpoint_difference':diffs[-1],'initial_difference':diffs[0],'absolute_resolution_floor':floor(name,reference),'interpolation_uncertainty':'UNKNOWN','evolution_refinement_uncertainty':'UNKNOWN','result_class':'RESOLUTION_LIMITED','norm_kind':'1001_SAMPLED_INTERPOLATED_NOT_CONTINUOUS_SUPREMUM'})
    milestone=[]
    for threshold in [.1,.5,.9]:
        r=crossings(reference,threshold);c=crossings(candidate,threshold);rf=r['first'];cf=c['first']
        milestone.append({'reference':reference['id'],'candidate':candidate['id'],'x_HII_target':threshold,'reference_status':r['crossing_status'],'candidate_status':c['crossing_status'],'reference_crossing_time_s':rf['time_s'] if rf else None,'candidate_crossing_time_s':cf['time_s'] if cf else None,'reference_crossing_zbar':rf['zbar'] if rf else None,'candidate_crossing_zbar':cf['zbar'] if cf else None,'delta_time_s':cf['time_s']-rf['time_s'] if cf and rf else None,'delta_zbar':cf['zbar']-rf['zbar'] if cf and rf else None,'reference_crossings':r,'candidate_crossings':c,'interpolation_uncertainty':'UNKNOWN'})
    return rows,summary,milestone

def write_csv(path,rows):
    if not rows:return
    with path.open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def run(manifest_path,output,kind_override=None):
    output=pathlib.Path(output)
    if output.exists():raise RuntimeError('Existing reduction directory; choose new output, nooverwrite')
    output.mkdir(parents=True);base={'input_manifest':str(manifest_path),'input_manifest_sha256':hashfile(manifest_path),'reducer_source_sha256':hashfile(__file__),'comparison_coordinate':'ZBAR','grid_samples':1001,'interpolation':'Piecewiselinearinln(a) onconsecutivesavedacceptedneighbors','interpolation_uncertainty':'UNKNOWN','scientific_admission':'NOT_ISSUED','solver_runs':0,'metrics':None,'milestones':None}
    try:
        manifest=json.loads(pathlib.Path(manifest_path).read_text());kind=kind_override or manifest.get('comparison_kind','PAIRED')
        if kind not in ['PAIRED','REFINEMENT','SOURCE','IC']:raise InputHold('HOLD_COMPARISON_KIND',kind)
        ref=load_case(manifest['reference']);candidate=load_case(manifest['candidate'])
        def config_value(value):
            if value in ['true','false']:return value=='true'
            try:return float(value)
            except (TypeError,ValueError):return value
        changed={k for k in ref['config'].keys()|candidate['config'].keys() if config_value(ref['config'].get(k))!=config_value(candidate['config'].get(k))}
        resource={'max_steps','max_attempts','max_rhs','max_wall_s','spectra_every_accepted','output_budget_mib'}
        numerical={'local_target','energy_subdivisions','n_mu'}
        if kind=='PAIRED' and not changed<={'q_ref'}|resource:raise InputHold('HOLD_PAIRED_OTHER_INPUTS_CHANGED',str(sorted(changed)))
        if kind=='REFINEMENT':
            if not changed<=numerical|resource or len(changed&numerical)!=1:raise InputHold('HOLD_REFINEMENT_AXIS_OR_PHYSICAL_INPUTS',str(sorted(changed)))
        if kind in ['SOURCE','IC']:
            allowed={'escape_fraction'} if kind=='SOURCE' else {'initial_temperature_k'}
            if not changed<=allowed|resource or not changed&allowed:raise InputHold('HOLD_ROBUSTNESS_OTHER_INPUTS_CHANGED',str(sorted(changed)))
            if not manifest.get('assumption_reference'):raise InputHold('HOLD_ROBUSTNESS_ASSUMPTION_REFERENCE_MISSING',kind)
        rows,summary,milestones=compare(ref,candidate);write_csv(output/'sampled_comparisons.csv',rows);write_csv(output/'comparison_summary.csv',summary)
        write_csv(output/'milestones.csv',[{k:v for k,v in row.items() if k not in ['reference_crossings','candidate_crossings']} for row in milestones])
        base.update(status='DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED',comparison_kind=kind,metrics=summary,milestones=milestones,immutable_input_descriptors={'reference':manifest['reference'],'candidate':manifest['candidate']},assumption_reference=manifest.get('assumption_reference'),robustness_semantics='Namedmodel sensitivity, notposterior orsignedshearrobustness' if kind in ['SOURCE','IC'] else None)
    except InputHold as e:base.update(status=e.status,missing_or_invalid_field=e.field,metrics=None,milestones=None,scientific_integrity_failure='NOT_ESTABLISHED_BY_THIS_SIGNAL')
    except (KeyError,ValueError) as e:base.update(status='HOLD_INPUT_SCHEMA',missing_or_invalid_field=str(e),metrics=None,milestones=None)
    (output/'REDUCTION_RECEIPT.json').write_text(json.dumps(base,indent=2)+'\n');print(base['status']);return base

# Meaningful synthetic check: independently known linear functions, distinct
# proper clocks at common z, multiple upward crossings, exact endpoints, no
# extrapolation, and typed missing-completion behavior. No cosmological solver.
def self_test():
    xs=[L0,L0+(L1-L0)/2,L1];ys=[2,5,8]
    assert len(grid())==1001 and grid()[0]==L0 and grid()[-1]==L1
    for q in grid():assert abs(interp(xs,ys,q)-(2+6*(q-L0)/(L1-L0)))<3e-15
    try:interp(xs,ys,L0-1e-3)
    except InputHold:pass
    else:raise AssertionError('extrapolation admitted')
    s={'L':[L0,L0+.3*(L1-L0),L0+.6*(L1-L0),L1],'time_s':[0,30,60,100],'x_HII':[0,.6,.4,1]}
    c={'series':s};m=crossings(c,.5);assert m['crossing_status']=='REACHED' and len(m['additional_upward_crossings'])==1
    assert abs(m['first']['time_s']-25)<1e-12
    expected_L=L0+.25*(L1-L0);assert abs(m['first']['zbar']-(math.exp(-expected_L)-1))<1e-12
    n=crossings({'series':dict(s,x_HII=[0,.03,.04,.05])},.9);assert n['first'] is None and n['crossing_status']=='NOT_REACHED'
    initial=crossings({'series':dict(s,x_HII=[.5,.5,.4,.7])},.5);assert initial['first']['kind']=='INITIAL_EXACT_THRESHOLD' and len(initial['additional_upward_crossings'])==1
    above=crossings({'series':dict(s,x_HII=[.6,.6,.7,.8])},.5);assert above['first'] is None
    ref={'id':'R','factors':(.75,.0625),'series':{'L':array.array('d',xs),'time_s':array.array('d',[0,50,100]),'x_HII':array.array('d',[0,.5,1]),'Tgas_K':array.array('d',[10,15,20])}}
    cand={'id':'C','factors':ref['factors'],'series':{'L':array.array('d',xs),'time_s':array.array('d',[0,100,200]),'x_HII':array.array('d',[0,.5,1]),'Tgas_K':array.array('d',[11,16,21])}}
    rows,summary,_=compare(ref,cand);assert len(rows)==2002 and summary[1]['sampled_sup_absolute_difference']<1.00000000000001
    last=rows[-1];assert last['candidate_zbar']==4 and last['reference_zbar']==4 and last['candidate_time_s']==200 and last['reference_time_s']==100
    assert last['numerical_error_estimate'] is None and last['result_class']=='RESOLUTION_LIMITED'
    root=pathlib.Path(__file__).resolve().parent/'raw';root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as d:
        p=pathlib.Path(d);m=p/'input.json';m.write_text(json.dumps({'reference':{'id':'MISSING'},'candidate':{'id':'MISSING'}}));result=run(m,p/'out')
        assert result['status']=='HOLD_INPUT_IDENTITY_MISSING' and result['metrics'] is None
    with tempfile.TemporaryDirectory(dir=root) as d:
        d=pathlib.Path(d);spec={'id':'FIXTURE','clock_origin':CLOCK}
        history=d/'history.csv';abundance=d/'abundances.csv'
        header=['case_id','a','time_s','nH_proper_cm3','ne_proper_cm3',*FIELDS.values()]
        with history.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=header);writer.writeheader()
            for i,a in enumerate([A0,math.sqrt(A0*A1),A1]):
                x=[.1,.5,.9][i];row={'case_id':'FIXTURE','a':a,'time_s':i*50,'nH_proper_cm3':1,'ne_proper_cm3':x,'x_HI':1-x,'x_HII':x,'x_HeI':1,'x_HeII':0,'x_HeIII':0,'temperature_K':10+i,'J0_photon_u_eV_per_H':0,'J2_photon_u_eV_per_H':0};writer.writerow(row)
        with abundance.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['run_id','time_s','species_id','nproper','Ybaryon','A','normalization_registry']);writer.writeheader()
            for i,x in enumerate([.1,.5,.9]):
                for k,n,A in [('H_I',1-x,1),('H_II',x,1),('He_I',.1,4),('He_II',0,4),('He_III',0,4),('electron',x,0)]:writer.writerow({'run_id':'FIXTURE','time_s':i*50,'species_id':k,'nproper':n,'Ybaryon':n/1.4,'A':A,'normalization_registry':'BASELINE_H_HE_CHARGE_AND_BARYON_V1'})
        for role,data in [('config','end_zbar=4\nq_ref=0\n'),('source_identity','SYNTHETIC_SELF_TEST_NOT_PHYSICS'),('terminal','status=COMPLETE_REPRESENTED_INTERVAL\na=0.2\naccepted=2\n')]:
            path=d/(role+'.txt');path.write_text(data);spec[role]={'path':str(path),'sha256':hashfile(path)}
        spec['history']={'path':str(history),'sha256':hashfile(history)};spec['abundances']={'path':str(abundance),'sha256':hashfile(abundance)}
        loaded=load_case(spec);assert len(loaded['series']['L'])==3 and abs(loaded['series']['Y_H_II'][-1]-.9/1.4)<1e-15
        t=pathlib.Path(spec['terminal']['path']);t.write_text('status=STOPPED_CHECKPOINTED\n');spec['terminal']['sha256']=hashfile(t)
        try:load_case(spec)
        except InputHold as e:assert e.status=='UNKNOWN_INCOMPLETE_HISTORY'
        else:raise AssertionError('incomplete completion admitted')
    print('SYNTHETIC_SELF_TEST_PASS; interpolation/crossings/clocks/null-HOLD;0solver')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--manifest');ap.add_argument('--output');ap.add_argument('--kind',choices=['PAIRED','REFINEMENT','SOURCE','IC']);ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:self_test()
    elif args.manifest and args.output:run(args.manifest,args.output,args.kind)
    else:ap.error('Use --self-test or--manifest FILE --output NEW_DIRECTORY')
