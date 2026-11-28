"""Independent scalar/identity review. Standard library only; no solver imports.
Reads completed fixed C2c initial+followup evidence; deliberately rejects extra
batches, incomplete tasks or a fallback rather than silently changing scope.
"""
from pathlib import Path
import datetime,hashlib,json,math,zipfile
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def rawsha(b):return hashlib.sha256(b).hexdigest()
def packed(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def check(x,message):
    if not x:raise AssertionError(message)
def gate(g,k,x):g[k]=bool(x)
c=read('CONTRACT.json');raw=c['raw_criteria'];sc=c['scaled_criteria'];allg={};docs={};runs=[];source_pins={};ids={}
check(sha('CONTRACT.json')==read('provenance/CONTRACT_IDENTITY.json')['sha256'],'contract identity')
for name,n in [('MAIN',16),('FOLLOWUP',24)]:
    base=Path('evidence')/(name+'_MPI');summ=read(base/'BATCH_SUMMARY.json');launch=read(Path('evidence')/(name+'_MPI_LAUNCH.json'));pf=read(Path('evidence')/(name+'_MPI_PREFLIGHT.json'))
    pin=read('provenance/'+name+'_CODE_IDENTITY.json');source_pins[name]=pin['sha256']
    check(rawsha(packed(pin['files']))==pin['sha256']==summ['code_sha256'],'source aggregate')
    with zipfile.ZipFile(ROOT/('provenance/'+name+'_CODE_SNAPSHOT.zip')) as z:
        for p,h in pin['files'].items():check(rawsha(z.read(p))==h,'source snapshot '+p)
    manifest_path='inputs/'+name+'_TASKS.json';manifest=read(manifest_path)
    check(sha(manifest_path)==summ['manifest_sha256']==launch['manifest_sha256'],'manifest identity')
    check(len(summ['tasks'])==n==len(manifest['tasks']),'task count')
    check(summ['status']=='ALL_WORKER_RESULTS_PASS','batch status')
    check(launch['returncode']==0 and launch['preflight_passed'] and launch['source_unchanged'] and launch['cleanup_complete'] and not launch['timed_out'],'launch outcome')
    check(summ['worker_count']==1 and pf['layout']['workers']==1,'actual worker layout')
    check(pf['layout']['per_worker_memory_bytes']==int(1.5*2**30) and pf['layout']['memory_headroom_fraction']>=.2,'resource envelope')
    check(pf['host']['memory_accounting_policy']=='clean-file-half-v1','memory policy')
    check(all(launch['memory_events_delta'][k]==0 for k in ('oom','oom_kill','oom_group_kill')),'OOM outcome')
    expected={t['task_id']:t for t in manifest['tasks']}
    for ex in summ['tasks']:
        folder=base/ex['task_id'];rr=read(folder/'RESULT.json');d=read(folder/'DATA.json');inp=read(folder/'TASK_INPUT.json');tx=read(folder/'TASK_EXECUTION.json')
        check(ex==tx and ex['status']=='WORKER_RESULT_PASS','execution identity/status')
        check(inp==expected[ex['task_id']] and rr['input_sha256']==sha(folder/'TASK_INPUT.json'),'input identity')
        check(rr['status']=='PASS' and rr['parameters']==d['parameters']==inp['parameters'],'result params')
        check(sha(folder/'RESULT.json')==ex['worker_result_sha256']==ex['artifacts']['RESULT.json']['sha256'],'result hash')
        check(sha(folder/'DATA.json')==rr['evidence_sha256'] and (ROOT/folder/'DATA.json').stat().st_size==rr['evidence_bytes'],'data hash')
        check(rr['code_identity_sha256']==pin['sha256'] and rr['selected_backend']==ex['selected_backend'],'source/native binding')
        if 'state_file' in rr:check(sha(folder/'STATE.npz')==rr['state_sha256'] and (ROOT/folder/'STATE.npz').stat().st_size==rr['state_bytes'],'state hash')
        check(ex['wall_seconds']<=c['operational_limits']['task_wall_seconds'] and rr['elapsed_seconds']<=c['operational_limits']['task_wall_seconds'],'task wall')
        check(ex['process_cleanup']['status']=='NO_LIVE_OWNED_MEMBERS','task cleanup')
        check(d['task_id'] not in docs,'unique task')
        d['_result']=rr;d['_folder']=folder;docs[d['task_id']]=d;ids[str(folder/'DATA.json')]=sha(folder/'DATA.json')
    runs.append({'name':name,'tasks':n,'wall_seconds':launch['elapsed_seconds'],'source_sha256':pin['sha256'],'memory_events_delta':launch['memory_events_delta'],'preflight':True,'cleanup_complete':True})
# Independently re-evaluate both operator lanes and spatial quartet.
point_rows=[]
for R in c['new_R']:
    pairdocs={d['parameters']['profile']:d for d in docs.values() if d['parameters']['kind']=='prolate' and d['parameters']['R']==R}
    check(set(pairdocs)=={'base','h','p','tail'},'complete quartet')
    vs={k:d['value'] for k,d in pairdocs.items()};g={};pairrows={}
    for name,v in vs.items():
        check(pairdocs[name]['parameters']['tier']==0,'no fallback')
        ds=[v['direct'][str(q)] for q in (16,24,32)];fs=[v['force'][str(q)] for q in (12,20,28)];gap=v['energies'][1]-v['energies'][0];a={}
        for lane,ss,keys in [('direct',ds,('L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b')),('force',fs,('L_O_bar','L_B_bar','T_A','T_B'))]:
            a[lane+'_q_raw']=max(abs(u[k]-w[k]) for u,w in zip(ss,ss[1:]) for k in keys)
            a[lane+'_q_scaled']=max(abs(u['L_O_bar']-w['L_O_bar']) for u,w in zip(ss,ss[1:]))/R**3
            gate(g,name+'_'+lane+'_quadrature',a[lane+'_q_raw']<=raw['operator_quadrature_abs'] and a[lane+'_q_scaled']<=sc['L_O_quadrature_abs'])
        a['direct_force_LO_raw']=max(abs(d['L_O_bar']-f['L_O_bar']) for d in ds for f in fs);a['direct_force_LO_scaled']=a['direct_force_LO_raw']/R**3
        a['direct_force_LB_raw']=max(abs(d['L_B_bar']-f['L_B_bar']) for d in ds for f in fs)
        a['momentum_raw']=max(abs(d['p_x_bar']-gap*d['dipole_x']) for d in ds);a['momentum_scaled']=a['momentum_raw']/(3*R**2)
        a['origin_raw']=max(abs(d['L_O_bar']-d['L_B_bar']-R*d['p_x_bar']/3) for d in ds);a['origin_scaled']=a['origin_raw']/R**3
        a['norm']=max(abs(d[k]-1) for d in ds for k in ('norm_g','norm_b'))
        a['residual']=max(s['residuals'][k] for s in v['states'] for k in ('radial_discrete_relative','angular_discrete_relative'))
        a['dark']=max(abs(d['L_dark_O_bar']) for d in v['dark'].values())
        gate(g,name+'_lane',max(a['direct_force_LO_raw'],a['direct_force_LB_raw'])<=raw['direct_torque_abs'] and a['direct_force_LO_scaled']<=sc['L_O_direct_force_abs'])
        gate(g,name+'_momentum',a['momentum_raw']<=raw['momentum_gap_dipole_abs'] and a['momentum_scaled']<=sc['momentum_induced_L_O_abs'])
        gate(g,name+'_origin',a['origin_raw']<=raw['origin_identity_abs'] and a['origin_scaled']<=sc['origin_identity_abs'])
        gate(g,name+'_norm_residual_dark',a['norm']<=raw['norm_error_abs'] and a['residual']<=raw['algebraic_residual_relative'] and a['dark']<=raw['dark_abs'])
        gate(g,name+'_positive_resolved',gap>0 and all(e<0 for e in v['energies']) and min(d['L_O_bar'] for d in ds+fs)>10*R**3*sc['L_O_spatial_abs'])
        pairrows[name]=a
    base=vs['base'];spatial={}
    for name in ('h','p','tail'):
        v=vs[name];e=max(abs(a-b) for a,b in zip(base['energies'],v['energies']));gate(g,name+'_energy',e<=raw['energy_refinement_abs']);spatial[name]={'energy_abs':e}
        for lane,q in [('direct','32'),('force','28')]:
            lo=abs(v[lane][q]['L_O_bar']-base[lane][q]['L_O_bar']);lb=abs(v[lane][q]['L_B_bar']-base[lane][q]['L_B_bar'])
            spatial[name][lane]={'LO_abs':lo,'LB_abs':lb,'LO_scaled':lo/R**3};gate(g,name+'_'+lane+'_spatial',lo<=raw['L_O_refinement_abs'] and lb<=raw['L_B_refinement_abs'] and lo/R**3<=sc['L_O_spatial_abs'])
    gate(g,'tail_inner_prefix',all(vs['tail']['states'][m]['actual_radial_edges'][:65]==base['states'][m]['actual_radial_edges'] for m in (0,1)))
    Q=base['direct']['32']['L_O_bar']/R**3
    point_rows.append({'R':R,'Q':Q,'relative_to_coefficient':Q/c['coefficient']['value']-1,'pairs':pairrows,'spatial':spatial,'gates':g,'pass':all(g.values())})
allg['point_quartets']=all(x['pass'] for x in point_rows)
# Spherical direct derivative observables, independent angular refinement.
anchor={};ag={};R=.125
for label in ('l72','l96'):
    d=docs['observe_'+label];v=d['value'];qrows=[v['direct'][str(q)] for q in (14,22,30)];gap=v['energies'][1]-v['energies'][0]
    qraw=max(abs(a[k]-b[k]) for a,b in zip(qrows,qrows[1:]) for k in ('L_O_bar','L_B_bar','p_x_over_minus_i_hbar','dipole_x'))
    qscaled=max(abs(a['L_O_bar']-b['L_O_bar']) for a,b in zip(qrows,qrows[1:]))/R**3
    mom=max(abs(a['p_x_over_minus_i_hbar']-gap*a['dipole_x']) for a in qrows)
    origin=max(abs(a['L_O_bar']-a['L_B_bar']-(R/3)*a['p_x_over_minus_i_hbar']) for a in qrows)
    gate(ag,label+'_q',qraw<=raw['operator_quadrature_abs'] and qscaled<=sc['spherical_L_O_quadrature_abs'])
    gate(ag,label+'_momentum',mom<=raw['momentum_gap_dipole_abs'] and mom/(3*R**2)<=sc['momentum_induced_L_O_abs'])
    gate(ag,label+'_origin',origin<=raw['origin_identity_abs'] and origin/R**3<=sc['origin_identity_abs'])
    check(v['sectors']==[0,1] and all(p>0 for p in v['phase_probes']),'anchor phases')
    for m,ref in enumerate(d['parameters'][k] for k in ('left','right')):
        sf=Path(ref['folder']);rr=read(sf/'RESULT.json');sv=read(sf/'DATA.json')['value']
        check(sha(sf/'RESULT.json')==ref['result_sha256'] and sha(sf/'STATE.npz')==ref['state_sha256'],'anchor binding')
        check(sv['energy']==v['energies'][m] and sv['state_sha256']==v['states'][m]['state_sha256'],'anchor state scalar binding')
        gate(ag,label+'_state'+str(m),sv['residual']<=raw['algebraic_residual_relative'] and abs(sv['mass_norm']-1)<=raw['norm_error_abs'])
    anchor[label]={'LO':qrows[-1]['L_O_bar'],'energies':v['energies'],'q_raw':qraw,'q_scaled':qscaled,'momentum_scaled':mom/(3*R**2),'origin_scaled':origin/R**3}
pbase=docs['R0p125_base']['value'];ad=abs(anchor['l96']['LO']-pbase['direct']['32']['L_O_bar']);ai=abs(anchor['l96']['LO']-anchor['l72']['LO']);ae=max(abs(a-b) for a,b in zip(anchor['l96']['energies'],pbase['energies']))
gate(ag,'agreement',ad<=raw['independent_spherical_L_O_abs'] and ad/R**3<=sc['spherical_L_O_agreement_abs']);gate(ag,'increment',ai<=raw['independent_spherical_increment_abs'] and ai/R**3<=sc['spherical_L_O_increment_abs']);gate(ag,'energy',ae<=raw['independent_spherical_energy_abs'])
anchor.update(agreement_scaled=ad/R**3,increment_scaled=ai/R**3,energy_max_abs=ae,gates=ag,pass_=all(ag.values()));allg['anchor']=all(ag.values())
# Six independently integrated physical local edge-sector groups.
overlaps=[]
for j,edge in enumerate(c['continuation']['edges']):
    for m in (0,1):
        vs=[docs[f'edge{j}_m{m}_q{q}']['value'] for q in (16,24,32)]
        for v in vs:
            mean=(v['left_domain_overlap']+v['right_domain_overlap'])/2;norm=math.sqrt(v['self_norm_left']*v['self_norm_right']);check([v['R_left'],v['R_right']]==edge and v['m']==m,'edge identity');check(abs(mean-v['overlap'])<1e-14 and abs(mean/norm-v['normalized_overlap'])<1e-14,'overlap arithmetic')
        increments=[max(abs(a[k]-b[k]) for k in ('left_domain_overlap','right_domain_overlap','normalized_overlap')) for a,b in zip(vs,vs[1:])]
        direction=max(abs(v['left_domain_overlap']-v['right_domain_overlap']) for v in vs);normerr=max(abs(v[k]-1) for v in vs for k in ('self_norm_left','self_norm_right'));last=vs[-1];mag=abs(last['normalized_overlap']);ok=max(increments+[direction,normerr])<=1e-7 and .5<=mag<=1+1e-7
        overlaps.append({'edge':edge,'m':m,'increments':increments,'direction_max':direction,'norm_error_max':normerr,'normalized_overlap':last['normalized_overlap'],'phase':1 if last['overlap']>=0 else -1,'pass':ok})
allg['continuation']=all(x['pass'] for x in overlaps)
# Registered four native/reference comparisons; no repeated integration.
parity=[]
for i,case in enumerate(c['parity_cases']):
    actual=docs['parity_'+str(i)]['value'];kind=case['kind']
    if i==0:ref=read('frozen/R0p25_base/RESULT.json')['operators']['direct']['24']
    elif i in (1,2):ref=docs['R0p03125_base']['value'][kind][str(case['order'])]
    else:ref=docs['edge0_m0_q24']['value']
    keys={'direct':('L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b'),'force':('L_O_bar','L_B_bar','T_A','T_B','gap'),'overlap':('overlap','normalized_overlap','left_domain_overlap','right_domain_overlap','directional_difference_abs','self_norm_left','self_norm_right','max_self_norm_error_abs')}[kind]
    delta=max(abs(actual[k]-ref[k]) for k in keys);scaled=None if i==3 else abs(actual['L_O_bar']-ref['L_O_bar'])/case['R']**3
    parity.append({'case':i,'max_raw':delta,'scaled_LO':scaled,'pass':delta<=raw['native_reference_operator_abs'] and (scaled is None or scaled<=sc['native_parity_abs'])})
allg['parity']=all(x['pass'] for x in parity)
counts={kind:sum(d['parameters']['kind']==kind for d in docs.values()) for kind in sorted({d['parameters']['kind'] for d in docs.values()})};states=sum(d['new_eigenstates'] for d in docs.values());wall=sum(x['wall_seconds'] for x in runs)
check(counts=={'prolate':12,'sphere':4,'sphere_observe':2,'overlap':18,'parity':4},'actual attempted task inventory');check(states==28,'selected states')
allg['budgets']=states<=56 and wall<=1800 and counts['prolate']<=24 and counts['sphere']<=8 and counts['overlap']<=30 and counts['parity']<=4
allg['execution_identity']=True
final=read('evidence/FINAL_AUDIT.json');check(final['contract_sha256']==sha('CONTRACT.json'),'final contract');check(final['stop']=='SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED' and all(final['gates'].values()),'published scoped stop');check(all(allg.values()),'independent scientific checks')
check(final['budgets']['new_selected_states']==states and final['budgets']['active_batch_wall_seconds']==wall,'final budget report')
check(final['global_gates']==c['gates'] and not final['global_gates']['full_C2_closed'] and final['global_gates']['scientific_PROMOTE']=='HOLD','claim ceiling')
out={'status':'ACCEPT_SCOPED_SMALL_R_SCALED_SEQUENCE','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'contract_sha256':sha('CONTRACT.json'),'final_audit_sha256':sha('evidence/FINAL_AUDIT.json'),'review_script_sha256':sha('review/C2C_INDEPENDENT_REVIEW_RECALCULATE.py'),'independent_physical_runs':0,'independent_scalar_recalculation':True,'solver_or_root_analyzer_imports':False,'gates':allg,'points':point_rows,'anchor':anchor,'continuation':overlaps,'parity':parity,'budgets':{'attempted_completed_tasks':40,'failed_physical_tasks':0,'counts_by_kind':counts,'new_selected_eigenstates':states,'requested_spherical_Ritz_roots':8,'active_batch_wall_seconds':wall,'max_rss_mib':max(d['_result']['max_rss_kib']/1024 for d in docs.values()),'fallbacks':0},'runs':runs,'execution_source_sha256':source_pins,'verified_data_sha256':ids,'limitations':['Finite registered sequence and empirical discretization/consistency checks only','Independent spherical anchor atR=.125 only with separately declared weaker precision','No quantitative rigorous Big-O constant/radius, continuum enclosure, full-C2, collision propagation, Eq55 or production promotion','NCP64 physical scaling NOT_RUN','Current resource availability is an estimate, not reservation; observed two1-worker batches completed with no OOM events'],'delivery_review':'Publication and provider upload receipts are root-owned and outside scientific admission.'}
outfile=ROOT/'review/C2C_INDEPENDENT_REVIEW_FINAL.json'
with outfile.open('x') as f:json.dump(out,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':out['status'],'gates':allg,'anchor_agreement_scaled':ad/R**3,'anchor_increment_scaled':ai/R**3,'min_overlap':min(abs(x['normalized_overlap']) for x in overlaps),'max_overlap_increment':max(max(x['increments']) for x in overlaps),'max_parity_raw':max(x['max_raw'] for x in parity),'budgets':out['budgets']},indent=2))
