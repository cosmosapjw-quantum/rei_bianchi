"""Independent scalar-only review; imports no author audit or scientific code."""
from pathlib import Path
import argparse, collections, hashlib, json, math, os
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def error(a,b):return abs(a-b)
def audit(batch):
    c=load(ROOT/'CONTRACT.json'); raw=c['raw_criteria']; scaled=c['scaled_criteria']
    summary=load(batch/'BATCH_SUMMARY.json'); docs={}; identities={}; failures=[]; checks=[]
    def check(name,val,cap):
        ok=math.isfinite(val) and val<=cap
        checks.append({'name':name,'value':val,'limit':cap,'pass':ok})
        if not ok:failures.append(name)
    assert summary['status']=='ALL_WORKER_RESULTS_PASS'
    for task in summary['tasks']:
        folder=batch/task['task_id']; result=load(folder/'RESULT.json');data=load(folder/'DATA.json');inp=load(folder/'TASK_INPUT.json')
        assert task['status']=='WORKER_RESULT_PASS' and task['returncode']==0
        assert result['status']=='PASS' and result['task_id']==data['task_id']==task['task_id']==inp['task_id']
        assert digest(folder/'RESULT.json')==task['worker_result_sha256']
        assert digest(folder/'DATA.json')==result['evidence_sha256'] and (folder/'DATA.json').stat().st_size==result['evidence_bytes']
        assert digest(folder/'TASK_INPUT.json')==result['input_sha256']==task['task_sha256']
        assert data['parameters']==result['parameters']==inp['parameters']
        assert result['code_identity_sha256']==task['code_sha256']==summary['code_sha256']
        assert result['selected_backend']==task['selected_backend']
        for filename,spec in task['artifacts'].items():
            assert (folder/filename).stat().st_size==spec['bytes'] and digest(folder/filename)==spec['sha256']
        if 'state_sha256' in result:
            assert result['state_file']=='STATE.npz'
            assert digest(folder/'STATE.npz')==result['state_sha256']
            assert (folder/'STATE.npz').stat().st_size==result['state_bytes']
        check(task['task_id']+'.worker_wall',task['wall_seconds'],c['operational_limits']['task_wall_seconds']+2)
        check(task['task_id']+'.reported_wall',result['elapsed_seconds'],c['operational_limits']['task_wall_seconds'])
        docs[task['task_id']]=data
        identities[task['task_id']]={'result_sha256':digest(folder/'RESULT.json'),'data_sha256':digest(folder/'DATA.json'),'state_sha256':result.get('state_sha256')}
    pair_metrics={}; endpoints=collections.defaultdict(dict)
    for name,d in docs.items():
        p,v=d['parameters'],d['value']; kind=p['kind']
        if kind not in ('prolate','bridge'):continue
        R=v['R'];gap=v['energies'][1]-v['energies'][0]
        assert v['energies'][0]<v['energies'][1]<0
        for s in v['states']:
            check(name+'.residual',max(s['residuals'][k] for k in ('radial_discrete_relative','angular_discrete_relative')),raw['algebraic_residual_relative'])
            assert s['phase']['algorithm']==c['phase']['algorithm']
            for ax in ('radial','angular'):
                z=s['phase'][ax];assert z['dominant_value']>0
                check(name+'.phase.'+ax,z['negative_l2_fraction'],c['phase']['max_weighted_negative_L2_fraction'])
        if kind=='bridge':continue
        endpoints[R][p['profile']]=v
        direct=[v['direct'][str(q)] for q in c['operators']['direct_orders']]
        force=[v['force'][str(q)] for q in c['operators']['force_orders']]
        metrics={'R':R,'Q_O':direct[-1]['L_O_bar']/R,'Q_B':-R*R*direct[-1]['L_B_bar']}
        for lane,seq,keys in [('direct',direct,['L_O_bar','L_B_bar','p_x_bar','dipole_x','norm_g','norm_b']),('force',force,['L_O_bar','L_B_bar','T_A','T_B'])]:
            increments=[{k:error(b[k],a[k]) for k in keys} for a,b in zip(seq,seq[1:])]
            check(name+'.'+lane+'.q.raw',max(z for x in increments for z in x.values()),raw['operator_quadrature_abs'])
            for q,key,factor in [('Q_O','L_O_bar',1/R),('Q_B','L_B_bar',R*R)]:
                val=max(x[key]*factor for x in increments);metrics[lane+'_q_'+q]=val
                check(name+'.'+lane+'.q.'+q,val,scaled[q+'_quadrature_abs'])
        for q,key,factor in [('Q_O','L_O_bar',1/R),('Q_B','L_B_bar',R*R)]:
            delta=max(error(a[key],b[key]) for a in direct for b in force);metrics['direct_force_'+q]=delta*factor
            check(name+'.direct_force.'+q,delta*factor,scaled[q+'_direct_force_abs']);check(name+'.direct_force.'+q+'.raw',delta,raw['direct_torque_abs'])
        norm=max(error(d[k],1) for d in direct for k in ('norm_g','norm_b'))
        origin=max(abs(d['L_O_bar']-d['L_B_bar']-R*d['p_x_bar']/3) for d in direct)
        momentum=max(abs(d['p_x_bar']-gap*d['dipole_x']) for d in direct)
        check(name+'.norm',norm,raw['norm_error_abs']);check(name+'.origin_raw',origin,raw['origin_identity_abs']);check(name+'.momentum_raw',momentum,raw['momentum_gap_dipole_abs'])
        for q,oi,mi in [('Q_O',origin/R,momentum/3),('Q_B',R*R*origin,R**3*momentum/3)]:
            metrics['origin_'+q]=oi;metrics['momentum_'+q]=mi
            check(name+'.origin.'+q,oi,scaled[q+'_origin_abs']);check(name+'.momentum.'+q,mi,scaled[q+'_momentum_abs'])
        check(name+'.dark',max(abs(vv['L_dark_O_bar']) for vv in v['dark'].values()),raw['dark_abs'])
        assert all(x['L_O_bar']>0 and x['L_B_bar']<0 for x in direct+force)
        assert metrics['Q_O']>10*scaled['Q_O_spatial_abs'] and metrics['Q_B']>10*scaled['Q_B_spatial_abs']
        metrics['origin_B_condition']=(abs(direct[-1]['L_O_bar'])+abs(R*direct[-1]['p_x_bar']/3))/abs(direct[-1]['L_B_bar'])
        pair_metrics[name]=metrics
    quartet_metrics={}
    for R,ps in endpoints.items():
        assert set(ps)=={'base','h','p','tail'}
        base=ps['base'];rows={}
        for profile in ('h','p','tail'):
            v=ps[profile];row={}
            check(str(R)+'.'+profile+'.energy',max(error(a,b) for a,b in zip(base['energies'],v['energies'])),raw['energy_refinement_abs'])
            for lane,qmax in [('direct',32),('force',28)]:
                a,b=base[lane][str(qmax)],v[lane][str(qmax)]
                for Q,key,factor in [('Q_O','L_O_bar',1/R),('Q_B','L_B_bar',R*R)]:
                    val=error(a[key],b[key]);row[lane+'_'+Q]=val*factor
                    check(str(R)+'.'+profile+'.'+lane+'.'+Q,val*factor,scaled[Q+'_spatial_abs']);check(str(R)+'.'+profile+'.'+lane+'.'+Q+'.raw',val,raw[key.replace('_bar','')+'_refinement_abs'])
            rows[profile]=row
        for m in (0,1):
            a=base['states'][m]['actual_radial_edges'];b=ps['tail']['states'][m]['actual_radial_edges'];assert b[:len(a)]==a
        quartet_metrics[str(R)]=rows
    return {'schema':'bass-he-c2d-independent-main-recalculation-v1','pass':not failures,'failures':failures,'contract_sha256':digest(ROOT/'CONTRACT.json'),'batch_summary_sha256':digest(batch/'BATCH_SUMMARY.json'),'batch':str(batch.relative_to(ROOT)),'tasks':len(docs),'selected_states':sum(x['new_eigenstates'] for x in docs.values()),'task_kind_counts':dict(collections.Counter(x['parameters']['kind'] for x in docs.values())),'pair_metrics':pair_metrics,'quartet_metrics':quartet_metrics,'checks':checks,'identities':identities,'new_physical_evaluations':0,'independence':'stdlib scalar arithmetic over identity-verified physical DATA; no import of author audit/scientific code; scientific jobs not repeated.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('batch');p.add_argument('output');a=p.parse_args();v=audit(ROOT/a.batch)
    with (ROOT/a.output).open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('pass','failures','tasks','selected_states','task_kind_counts','pair_metrics','quartet_metrics')},indent=2))
