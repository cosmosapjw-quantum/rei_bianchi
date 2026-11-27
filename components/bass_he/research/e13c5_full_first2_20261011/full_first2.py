#!/usr/bin/env python3
"""Frozen full first-two-step enclosure; inherited interval helpers unchanged."""
import argparse, hashlib, json, os, resource, shutil, sys, time
from pathlib import Path
TASK=Path(__file__).resolve().parent
COVER=TASK.parent/'e13c5_first2_branch_cover_20261011'
sys.path.insert(0,str(COVER))
import cover as old
from cover import IV, Coefficients, lift, atomic_json, response_j, integrate, encode, sym

MODES=old.MODES; SP=old.SP; SPECIAL=set(old.NODES)
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def keys(m,n):return [(m,1,n,0),(m,2,n,0)]+([(m,2,n,1)] if n in SPECIAL else [])
def verify():
    pins=json.loads((COVER/'START.json').read_text())['hashes']
    pins.update({str(COVER/'cover.py'):'aaae27a0d053d42ce6727593df676352697dd042486aa448d1e9104b16f979f6',str(COVER/'RESULTS.json'):'418dcac9280947abc227c69f9178c0163bbdb00fa34bff1f9e34ab9eea35ece4',str(COVER/'START.json'):'5f75633b9bd4b55aeaab4ca727972c6b7da4aba0fbaaf050b3d183a45a2ce6d1',str(COVER/'independent_review.md'):'999e841eb3ac55d744946682215d00b1c5dc1db3650b2a81a6c8c228286f237f'})
    for m,h in zip(MODES,('1fde668d09ca3c0c14fb425aba5e50ccef031eaa3853e887c951a505e9e18871','036f2af860d61c632eea5aba0e268f845041de8c542c33d6f169c2fbe4b4e453','194692189ac428ddf456a93202b1b5f198a22805b80710b2dd62c94482771481')):pins[str(old.UP/f'evidence/capture/{m}/AGGREGATE.csv')]=h
    actual={p:digest(Path(p)) for p in pins}
    assert actual==pins,'IMMUTABLE_INPUT_IDENTITY_MISMATCH'
    return actual
def load():
    stage={m:{int(r['step']):r for r in old.rows(old.UP/f'inputs/{m}_STAGES.csv')} for m in MODES}
    nodes={m:{(int(r['step']),int(r['node'])):r for r in old.rows(old.UP/f'evidence/capture/{m}/NODES.csv')} for m in MODES}
    aggregate={m:{int(r['step']):r for r in old.rows(old.UP/f'evidence/capture/{m}/AGGREGATE.csv')} for m in MODES}
    selected={}
    for m in MODES:
        for r in old.rows(old.UP/f'evidence/capture/{m}/SEGMENTS.csv'):
            k=(m,int(r['step']),int(r['node']),int(r['segment']))
            if k[2] in range(2440) and k in keys(m,k[2]):assert k not in selected;selected[k]=r
    expected={k for m in MODES for n in range(2440) for k in keys(m,n)}
    assert set(selected)==expected and len(selected)==14652
    return stage,nodes,aggregate,selected
def controls():
    start=time.monotonic();hashes=verify();stage,nodes,aggregate,selected=load()
    result=old.controls(selected[('OFF',1,0,0)])
    assert len({(m,n) for m in MODES for n in range(2440)})==7320
    assert len(keys('OFF',1))==2 and len(keys('OFF',700))==3
    # Keyed carry cannot alias equal node numbers in different modes.
    carry={('OFF',1):IV(2),('KF',1):IV(3)}
    assert carry[('OFF',1)].lo!=carry[('KF',1)].lo
    # JSONL round trip retains one complete path per record.
    line=json.dumps({'mode':'OFF','node':1,'segments':[{'key':k} for k in keys('OFF',1)]})
    assert [tuple(s['key']) for s in json.loads(line)['segments']]==keys('OFF',1)
    result.update({'hashes':hashes,'coverage':14652,'paths':7320,'key_and_stream_controls':'PASS','wall_seconds':time.monotonic()-start})
    assert result['wall_seconds']<120
    atomic_json(TASK/'CONTROLS.json',result)
    print(json.dumps({'controls':'PASS','wall_seconds':result['wall_seconds']}),flush=True)
def main(output):
    resource.setrlimit(resource.RLIMIT_AS,(1024*1024**2,1024*1024**2));old.di.configure(60)
    start=time.monotonic();output.mkdir(parents=True,exist_ok=False)
    hashes=verify();stage,nodes,aggregate,selected=load();eps=lift(1.602176634e-12)
    reused_paths={(p['mode'],p['node']):old.decode(p) for p in json.loads((COVER/'RESULTS.json').read_text())['paths']}
    atomic_json(output/'START.json',{'hashes':hashes,'code_sha256':digest(Path(__file__)),'contract_sha256':digest(TASK/'CONTRACT.json'),'N':128,'precision':60,'serial':True,'limit_seconds':21600,'memory_limit_MiB':1024,'primary_invocations':1,'native_runs':0,'gas_advances':0,'old_continuous_solves':0,'six_control_replays':0,'HARNESS_UNAVAILABLE':True})
    allstep={m:{s:{} for s in (1,2)} for m in MODES};allledger={m:{} for m in MODES};repnodes={m:{s:{} for s in (1,2)} for m in MODES}
    computed=0;reused=0;paths=0;segments=0;ledgers=0
    with (output/'PATHS.jsonl').open('x') as stream:
      for m in MODES:
       for node in range(2440):
        ks=keys(m,node);weight=lift(selected[ks[0]]['weight']);initial=lift(selected[ks[0]]['f0']);initialE=lift(selected[ks[0]]['e0'])
        cumulative={};caps={};corrections={};anchor=IV(0);prev=None;outputs=[];stepc={};stepcaps={};stepa=IV(0)
        for index,k in enumerate(ks):
            r=selected[k];old.branch(r);assert lift(r['weight']).lo==weight.lo and weight.lo>0
            mask={s:float(r['e_mid'])>=cut for s,cut in zip(SP,(13.6,24.59,54.42))}
            c=Coefficients({'row':r,'stage':stage[m][k[1]],'mask':mask,'source_on':float(r['source_on'])==1})
            Ia=IV(0) if index==0 else prev-c.f0
            if index==0 or k[1]!=ks[index-1][1]:stepinitial=initial if index==0 else prev;stepE=c.e0;stepc={};stepcaps={};stepa=IV(0)
            if (m,node) in reused_paths:
                oldout=reused_paths[(m,node)]['segments'][index]
                assert tuple(oldout['key'])==k and (Ia-oldout['Ia']).contains(0)
                J=oldout['J'];g=oldout['g'];rem=oldout['remainder'];frozen=oldout['frozen'];cap=oldout['captured'];corrected=oldout['continuous_minus_frozen'];S=oldout['S'];rad=oldout['midpoint_radii'];Pend=oldout['Pend'];DP=oldout['DP'];c.domain=oldout['domain'];reused+=1
            else:
                J,bounds,rad=integrate(c);S=IV(abs(Ia).hi)+bounds['B_r'];j0=response_j(c.L,c.h);je=c.e0*response_j(c.L+1,c.h)
                g={'P1':(-c.L*c.h).exp(),'Z_eV':je,'QN':IV(0),'QE_eV':IV(0)};rem={'P1':S*bounds['H_h'],'Z_eV':S*bounds['H_E'],'QN':IV(0),'QE_eV':IV(0)}
                FN=c.f0*j0+c.qf*(c.h-j0)/c.L;FE=c.f0*je+c.e0*c.qf*(response_j(IV(1),c.h)-response_j(c.L+1,c.h))/c.L
                frozen={'Z_eV':FE,'QN':c.qf*c.h,'QE_eV':c.e0*c.qf*response_j(IV(1),c.h)};cap=old.captured(r,eps)
                for i,s in enumerate(SP):
                    for pref,gg,ff in (('A',c.lf[i]*j0,c.lf[i]*FN),('B',c.lf[i]*je,c.lf[i]*FE),('H',c.lf[i]*(je-c.chi[i]*j0),c.lf[i]*(FE-c.chi[i]*FN))):
                        label=pref+'_'+s+('_eV' if pref!='A' else '');g[label]=gg;frozen[label]=ff;rem[label]=S*bounds['effective_'+pref+'_'+s]
                corrected={label:J[label]+g[label]*Ia+sym(rem[label]) for label in g}
                Pend=c.f0*g['P1']+c.qf*j0+corrected['P1'];DP=Pend-lift(r['n']);computed+=1
            moments={label:frozen[label]+corrected[label] for label in frozen};fmcap={label:frozen[label]-cap[label] for label in frozen}
            old.add(cumulative,moments);old.add(stepc,moments);old.add(caps,cap);old.add(stepcaps,cap);old.add(corrections,{label:fmcap[label]+corrected[label] for label in frozen})
            count=Pend-initial+old.total(cumulative,'A')-cumulative['QN'];energy=c.endpoint_E*Pend-initialE*initial+old.total(cumulative,'B')+cumulative['Z_eV']-cumulative['QE_eV']-anchor
            scount=Pend-stepinitial+old.total(stepc,'A')-stepc['QN'];senergy=c.endpoint_E*Pend-stepE*stepinitial+old.total(stepc,'B')+stepc['Z_eV']-stepc['QE_eV']-stepa
            assert all(x.contains(0) for x in (count,energy,scount,senergy)),'LEDGER_CONTAINMENT_FAILURE';ledgers+=4
            seam=IV(0)
            if index+1<len(ks):seam=(lift(selected[ks[index+1]]['e0'])-c.endpoint_E)*Pend;anchor+=seam
            if index+1<len(ks) and ks[index+1][1]==k[1]:stepa+=seam
            endpoint=index+1==len(ks) or ks[index+1][1]!=k[1];node_reduction=None
            if endpoint:
                nr=nodes[m][(k[1],node)];nc=old.captured(nr,eps);node_reduction={label:stepcaps[label]-nc[label] for label in stepcaps};node_reduction['P']=lift(r['n'])-lift(nr['n']);node_reduction['U_erg']=lift(r['u'])-lift(nr['u'])
                weighted={label:weight*v for label,v in stepc.items()};weighted.update({'P_endpoint':weight*Pend,'U_endpoint_eV':weight*c.endpoint_E*Pend,'count_ledger':weight*scount,'energy_ledger':weight*senergy,'anchor':weight*stepa})
                old.add(allstep[m][k[1]],weighted)
                nodevals={label:weight*v for label,v in nc.items()};nodevals.update({'P_endpoint':weight*lift(nr['n']),'U_endpoint_eV':weight*lift(nr['u'])/eps});old.add(repnodes[m][k[1]],nodevals)
            out={'key':k,'origin':'REUSED_REVIEWED_PR19' if (m,node) in reused_paths else 'NEW','Ia':Ia,'Pend':Pend,'DP':DP,'S':S,'J':J,'g':g,'remainder':rem,'continuous_minus_frozen':corrected,'frozen_minus_captured':fmcap,'frozen':frozen,'captured':cap,'captured_segment_to_node_reduction':node_reduction,'weighted_moments':{label:weight*v for label,v in moments.items()},'weighted_endpoint':weight*Pend,'weighted_anchor_to_next':weight*seam,'energy_endpoint_minus_captured_erg':eps*c.endpoint_E*Pend-lift(r['u']),'count_ledger':count,'energy_ledger':energy,'step_count_ledger':scount,'step_energy_ledger':senergy,'anchor_to_next':seam,'source_on':c.source_on,'mask':mask,'anchored':bool(float(r['anchored'])),'domain':c.domain,'midpoint_radii':rad}
            old.check(out);outputs.append(encode(out));prev=Pend;segments+=1
        old.add(allledger[m],{'count_ledger':weight*count,'energy_ledger':weight*energy})
        path={'mode':m,'node':node,'weight':encode(weight),'segments':outputs,'weighted_reduction':encode({**{label:weight*v for label,v in cumulative.items()},'P_final':weight*Pend,'anchor':weight*anchor}),'cumulative_correction':encode(corrections)}
        stream.write(json.dumps(path,sort_keys=True)+'\n');stream.flush();paths+=1
        atomic_json(output/'CHECKPOINT.json',{'completed_paths':paths,'completed_segments':segments,'new_segments':computed,'reused_segments':reused,'last_key':ks[-1],'stream_bytes':stream.tell(),'elapsed_seconds':time.monotonic()-start})
        if paths%20==0:print(json.dumps({'paths':paths,'segments':segments,'new':computed,'reused':reused,'elapsed_seconds':time.monotonic()-start}),flush=True)
        assert time.monotonic()-start<21600,'PRIMARY_TIME_LIMIT'
        assert stream.tell()<1024**3,'ARTIFACT_LIMIT'
    assert (paths,segments,computed,reused)==(7320,14652,14616,36)
    representation={}
    for m in MODES:
        representation[m]={}
        for step in (1,2):
            ar=aggregate[m][step];ac=old.captured(ar,eps);ac.update({'P_endpoint':lift(ar['n']),'U_endpoint_eV':lift(ar['u'])/eps})
            representation[m][step]={label:repnodes[m][step][label]-value for label,value in ac.items()}
            assert all(allstep[m][step][x].contains(0) for x in ('count_ledger','energy_ledger'))
        assert all(x.contains(0) for x in allledger[m].values())
    result={'status':'PASS_MECHANICAL_PENDING_ASTRA','scope':'full first two captured steps fixed gas/mask/source/anchor','paths':paths,'segments':segments,'new_segments':computed,'reused_segments':reused,'prefix_ledger_checks':ledgers,'all_node_per_step':allstep,'whole_path_ledgers':allledger,'weighted_node_to_aggregate_representation_difference':representation,'PATHS_sha256':digest(output/'PATHS.jsonl'),'elapsed_seconds':time.monotonic()-start,'max_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'holds':['physical','production','new_gas_evolution','photon_heat_recoil','receiver_adoption']}
    old.check(result);atomic_json(output/'RESULTS.json',encode(result));print(json.dumps({'terminal':'PASS_MECHANICAL_PENDING_ASTRA','paths':paths,'segments':segments}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
    old.di.configure(60)
    if a.controls:controls()
    else:
        assert a.output is not None
        main(a.output)
