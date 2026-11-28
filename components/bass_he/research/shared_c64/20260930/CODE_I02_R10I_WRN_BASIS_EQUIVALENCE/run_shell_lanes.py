"""Two bounded R10I shell lanes from stored R10G/R10F Delta only."""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, sys, traceback
import numpy as np
from audit_support import BLOCKS, BRANCH_NAMES, propagate
from endpoint_quadrature import nodes, reduce
from eta_rotation import velocity
from run_equivalence import atomic, sha

HERE=pathlib.Path(__file__).resolve().parent
LANES=(('AUTHOR_REDUCED_SL_CPC','STRAIGHT','CPC'),('AUTHOR_REDUCED_COUL_AUTHOR','COULOMB','AUTHOR'))

def run(out,run_root,repo,rotation_results,summary):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    run_root=pathlib.Path(run_root);repo=pathlib.Path(repo)
    sm=json.loads(pathlib.Path(summary).read_text())
    if sm['verdict']!='WRN_BASIS_NOT_EQUIVALENT' or sm['numeric_gate']!='PASS':
        raise ValueError('R10I_REPRESENTATION_GATE_NOT_OPEN')
    manifest=json.loads((HERE/'QUERY_MANIFEST.json').read_text())
    report=json.loads((run_root/'RETURN_REPORT.json').read_text())
    assert report['converged'] and report['evaluations']==60 and report['counts']['new_delta_calls']==300
    tablepath=run_root/'restored/review/EXACT_NODE_TABLE.json'
    assert sha(tablepath)==manifest['r10g_exact_table_sha256']
    table=json.loads(tablepath.read_text())
    old={(row['branch'],row['rho_hex']):float.fromhex(row['delta_hex']) for row in table['rows']}
    pre=json.loads((run_root/'restored/review/CUTPOINT_QUERY_PRECOMMITTED.json').read_text())
    outer_nodes=pre['node_hex'][15:]
    assert len(outer_nodes)==240 and set(outer_nodes)==set(manifest['outer_rho_hex'])
    new=set(manifest['first_rho_hex'])
    delta=dict(old)
    cache=list((run_root/'geometry_cache').glob('*.json'))
    assert len(cache)==300
    for path in cache:
        obj=json.loads(path.read_text());key,rec=obj['key'],obj['record']
        canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        assert hashlib.sha256(canon(key)).hexdigest()==path.stem
        assert hashlib.sha256(canon(rec)).hexdigest()==obj['record_sha256']
        assert key['source']=='496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba'
        assert key['depth']==96 and key['panels']==32 and key['rho_hex'] in new
        pair=(key['branch'],key['rho_hex'])
        assert pair not in delta
        delta[pair]=float.fromhex(rec['delta_hex'])
    assert len(delta)==1335
    rotation=json.loads(pathlib.Path(rotation_results).read_text())['records']
    assert len(rotation)==3270
    rmap={(x['trajectory'],x['cutoff'],x['energy_keV_u'],x['N'],x['l'],x['rho_hex']):np.array(x['author_reduced_probability']) for x in rotation}
    assert len(rmap)==len(rotation)
    rho_hex=manifest['first_rho_hex']+outer_nodes
    assert len(rho_hex)==300 and len(set(rho_hex))==300
    E=np.tile([.5,5.],len(rho_hex));v=velocity(E)
    d=np.zeros((len(rho_hex),5),float)
    from arseny_reimpl.eq50_scoped import ordered_scoped_branches
    branches=ordered_scoped_branches()
    assert [b.name for b in branches]==list(BRANCH_NAMES)
    expected_pairs=0
    for i,hx in enumerate(rho_hex):
        rho=float.fromhex(hx)
        for k,b in enumerate(branches):
            if rho<=b.support_cutoff:
                value=delta[(b.name,hx)]
                assert math.isfinite(value) and value>=0
                d[i,k]=value;expected_pairs+=1
    assert expected_pairs==1260
    p=np.zeros((len(rho_hex)*2,5))
    for i,hx in enumerate(rho_hex):
        rho=float.fromhex(hx)
        for k,b in enumerate(branches):
            if rho<=b.support_cutoff:p[2*i:2*i+2,k]=np.exp(-2*d[i,k]/v[2*i:2*i+2])
    integrands={}
    for name,tr,cut in LANES:
        mats=np.broadcast_to(np.eye(10),(len(E),10,10)).copy()
        for N,l,indices in BLOCKS:
            for i,hx in enumerate(rho_hex):
                rho=float.fromhex(hx)
                for j,energy in enumerate((.5,5.)):
                    rc=((l+.5)**2-(.5 if cut=='CPC' else 0))/3
                    a=2/(.8*1836.153*float(v[2*i+j])**2)
                    active=(rho<rc if tr=='STRAIGHT' else a+math.hypot(a,rho)<rc)
                    if active:
                        key=(tr,cut,energy,N,l,hx)
                        mats[2*i+j,np.asarray(indices)[:,None],indices]=rmap[key]
        assert np.max(abs(mats.sum(1)-1))<5e-13
        y=propagate(p,mats)
        integrands[name]=y[:,np.arange(10)!=2].reshape(len(rho_hex),18)
    values=np.concatenate([integrands[name] for name,_,_ in LANES],axis=1)
    assert values.shape==(300,36) and np.all(np.isfinite(values)) and np.min(values)>=-2e-13
    lookup=dict(zip(rho_hex,values))
    assert len(lookup)==300
    scale=float.fromhex('0x1.bb83cf2cf95d4p-8')
    def qpanel(ax,bx):
        a,b=float.fromhex(ax),float.fromhex(bx)
        q=nodes(a,b);rho=scale*np.sinh(q)
        hx=[float(x).hex() for x in rho]
        assert set(hx)<=new
        vals=np.array([lookup[x] for x in hx])
        h,e=reduce(a,b,(math.pi*scale*scale*np.sinh(2*q))[:,None]*vals)
        return {'q_left_hex':ax,'q_right_hex':bx,'rho_hex':hx,'high':h.tolist(),'error':e.tolist()}
    final_panels=[qpanel(a,b) for a,b in report['q_intervals']]
    qend=float.fromhex(report['q_intervals'][-1][1]);mid=qend/2
    initial_panels=[qpanel(float(0).hex(),mid.hex()),qpanel(mid.hex(),qend.hex())]
    cuts=[float.fromhex(x) for x in pre['cutpoint_hex']]
    outer=[]
    for i,(a,b) in enumerate(zip(cuts[1:-1],cuts[2:])):
        hx=outer_nodes[15*i:15*(i+1)]
        vals=np.array([lookup[x] for x in hx])
        h,e=reduce(a*a,b*b,math.pi*vals)
        outer.append({'left_hex':a.hex(),'right_hex':b.hex(),'rho_hex':hx,'high':h.tolist(),'error':e.tolist()})
    assert len(outer)==16
    tail=sum((np.array(x['high']) for x in outer),np.zeros(36))
    te=sum((np.array(x['error']) for x in outer),np.zeros(36))
    def grid(panels):
        h=tail+sum((np.array(x['high']) for x in panels),np.zeros(36))
        e=te+sum((np.array(x['error']) for x in panels),np.zeros(36))
        tol=1e-10+2e-4*abs(h)
        return h,e,tol
    h0,e0,t0=grid(initial_panels);h1,e1,t1=grid(final_panels)
    initial_pass=bool(np.all(e0<=t0));final_pass=bool(np.all(e1<=t1))
    change=abs(h1-h0);stable=bool(np.all(change<=.25*t1))
    gate={'schema':'bass_he.r10i.two_lane_endpoint_gate.v1',
          'status':'PASS' if initial_pass and final_pass and stable else 'UNRESOLVED_NO_NEW_QUERY_AUTHORIZED',
          'initial_36_pass':int(np.sum(e0<=t0)),'final_36_pass':int(np.sum(e1<=t1)),
          'successive_grid_pass':stable,'max_initial_normalized_error':float(np.max(e0/t0)),
          'max_final_normalized_error':float(np.max(e1/t1)),
          'max_normalized_grid_change':float(np.max(change/t1)),
          'first_rho_reused':60,'outer_rho_reused':240,'delta_pairs_reused':expected_pairs,
          'new_rho_queries':0,'new_delta_calls':0,'initial_leaves':2,'final_leaves':3,
          'integral':h1.tolist(),'error_estimate':e1.tolist(),'tolerance':t1.tolist(),
          'claim':'EMBEDDED_NUMERICAL_ESTIMATE_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE'}
    atomic(out/'RAW_INTEGRANDS.json',{'rho_hex':rho_hex,'lane_order':[x[0] for x in LANES],'components':values.tolist()})
    atomic(out/'INTERVALS.json',{'initial_q':initial_panels,'final_q':final_panels,'outer_u':outer})
    atomic(out/'NUMERICAL_GATE.json',gate)
    if gate['status']!='PASS':
        print(json.dumps({k:gate[k] for k in ('status','initial_36_pass','final_36_pass','max_final_normalized_error','max_normalized_grid_change')},indent=2))
        return gate
    sys.path[:0]=[str(repo),str(repo/'src')]
    from scripts.r10a_rho_freeze import _shell_summary
    oldlanes=json.loads((repo/'research/shared_c64/20260930/CODE_I02_R10G_ENDPOINT_RESOLUTION/EXECUTION/20260930T1226KST/FIVE_LANE_RESULT.json').read_text())['lanes']
    original={'AUTHOR_REDUCED_SL_CPC':'SL_CPC','AUTHOR_REDUCED_COUL_AUTHOR':'COUL_AUTHOR'}
    oracle_root=repo/'research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST'
    oracle=json.loads((oracle_root/'APPENDIX_A_ORACLE.json').read_text())
    scale_cm=json.loads((oracle_root/'APPENDIX_A_COMPARISON.json').read_text())['a0_squared_cm2']
    shell={};appendix={}
    for k,(name,_,_) in enumerate(LANES):
        shell[name]={};logs=[];dominant=[];rows=[]
        for j,energy in enumerate(('0.5','5.0')):
            vec=np.zeros(10);err=np.zeros(10);keep=np.arange(10)!=2
            vec[keep]=h1.reshape(2,2,9)[k,j];err[keep]=e1.reshape(2,2,9)[k,j]
            shells=_shell_summary(vec);shell_err=_shell_summary(err)
            base=oldlanes[original[name]][energy]['Z2_shell_areas_a0sq']
            base_err=oldlanes[original[name]][energy]['Z2_shell_error_estimate_a0sq']
            cells={}
            for label,value in shells.items():
                diff=value-base[label]
                material=(base[label]>0 and abs(diff)/base[label]>.01 and abs(diff)>10*(shell_err[label]+base_err[label]))
                cells[label]={'a0sq':value,'error_estimate_a0sq':shell_err[label],
                              'original_clean_a0sq':base[label],'difference_a0sq':diff,'material_vs_clean':material}
                model=value*scale_cm;author=oracle['shell_capture_cm2'][energy][label]
                if model<=0 or author<=0:raise ValueError('APPENDIX_CELL_NONPOSITIVE')
                lr=math.log(model/author);logs.append(lr)
                if label in ('2','3'):dominant.append(lr)
                rows.append({'energy_keV_u':float(energy),'shell_n':int(label),
                             'model_cm2':model,'author_cm2':author,'model_over_author':model/author})
            shell[name][energy]=cells
        appendix[name]={'all_six_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in logs)/6)),
                        'dominant_n2_n3_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in dominant)/4)),
                        'rows':rows,'classification':'AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'}
    atomic(out/'SHELL_TOTALS.json',{'classification':'DIRECT_CORDIR_RESEARCH_SHELL_TOTAL_NOT_C_S_AT_SUBSHELL',
                                   'lanes':shell,'gate_status':gate['status']})
    atomic(out/'APPENDIX_A_DIAGNOSTIC.json',{'classification':'AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION',
                                           'lanes':appendix,'gate_status':gate['status']})
    print(json.dumps({'status':gate['status'],'final_36_pass':gate['final_36_pass'],
                      'max_final_normalized_error':gate['max_final_normalized_error'],
                      'max_normalized_grid_change':gate['max_normalized_grid_change'],
                      'appendix_rms':{name:{x:y for x,y in row.items() if x.endswith('_rms')} for name,row in appendix.items()}},indent=2))
    return gate

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True);p.add_argument('--r10g-run',required=True);p.add_argument('--repo',required=True)
    p.add_argument('--rotation-results',required=True);p.add_argument('--rotation-summary',required=True)
    a=p.parse_args()
    try:run(a.out,a.r10g_run,a.repo,a.rotation_results,a.rotation_summary)
    except Exception:
        atomic(pathlib.Path(a.out)/'SHELL_FAILURE.json',{'status':'R10I_SHELL_EXECUTION_FAILED','traceback':traceback.format_exc()})
        raise
