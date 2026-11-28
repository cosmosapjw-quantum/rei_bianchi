#!/usr/bin/env python3
"""One frozen serial branch cover; fixed captured gas, no native execution."""
import csv, hashlib, json, resource, sys, tarfile, time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REC=Path('/tmp/E13C5-DyIbg0hn')
BASE=REC/'BASS_HE_E13C4_LOCAL_REMAINDER_ENCLOSURE_20261010_v1'
PILOT=REC/'E13C5_OFF700_THREE_SEGMENT_INCOMING_ANCHOR_PILOT'
sys.path.insert(0,str(BASE/'code'));sys.path.insert(0,str(PILOT))
import directed_interval as di
from directed_interval import IV,response_j
from local_enclosure import Coefficients,lift,atomic_json
from pilot import integrate,encode,sym
SP=('HI','HeI','HeII');MODES=('OFF','KF','GM');NODES=(0,700,1620,2344);ORDER=((1,0),(2,0),(2,1))
UP=BASE/'inputs/e13c3/inputs/e13c2/inputs/upstream_e13c1'
ARC=Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS03_20261010_RECOVERY/BASS_HE_E13C5_OFF700_PILOT_REVIEWED_20261011.tar.gz')
ZIP=Path('/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C4_LOCAL_REMAINDER_ENCLOSURE_20261010_sha_5498d936ee7d.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open() as f:return list(csv.DictReader(f))
def decode(x):
    if isinstance(x,dict):
        if set(x)=={'lo','hi'}:return IV(x['lo'],x['hi'])
        return {k:decode(v) for k,v in x.items()}
    if isinstance(x,list):return [decode(v) for v in x]
    return x
def check(x):
    if isinstance(x,IV):assert x.lo.is_finite() and x.hi.is_finite() and x.lo<=x.hi
    elif isinstance(x,dict):
        for v in x.values():check(v)
    elif isinstance(x,(list,tuple)):
        for v in x:check(v)
def total(d,pref):return sum((d[pref+'_'+s+('_eV' if pref!='A' else '')] for s in SP),IV(0))
def add(d,e):
    for k,v in e.items():d[k]=d.get(k,IV(0))+v
def captured(r,eps):
    z={'Z_eV':lift(r['red'])/eps,'QN':lift(r['qn']),'QE_eV':lift(r['qe'])/eps}
    for s,chi in zip(SP,(13.598434599702,24.587389011,54.41776)):
        z['A_'+s]=lift(r['A_'+s]);z['B_'+s+'_eV']=lift(r['B_'+s])/eps
        z['H_'+s+'_eV']=z['B_'+s+'_eV']-lift(chi)*z['A_'+s]
    return z
def branch(r):
    assert float(r['h'])>0,'H_ZERO_OR_NEGATIVE'
    assert sum(float(r['lambda_'+s]) for s in SP)>0,'L_ZERO_OR_NEGATIVE'
    assert float(r['outn'])==float(r['oute'])==0,'NONZERO_OUTFLOW'
    if float(r['source_on'])==0:assert float(r['q'])==0,'SOURCE_OFF_Q_NONZERO'
def controls(sample):
    t=time.monotonic();stock=F(0);A=F(0);B=F(0);Z=F(0);anchor=F(0);init=F(0);initE=F(0);endE=F(0)
    endings=[]
    for p,w in ((F(1),F(1)),(F(2),F(3))):
        p0=p;init+=w*p;initE+=w*8*p
        for j,(e0,e1) in enumerate(((F(8),F(4)),(F(6),F(3)))):
            pn=p/2;a=p/2;b=e0*p*F(3,8);z=b
            A+=w*a;B+=w*b;Z+=w*z
            if j==0:anchor+=w*(6-e1)*pn
            p=pn
        stock+=w*p;endE+=w*3*p;endings.append(p)
    count=stock-init+A;energy=endE-initE+B+Z-anchor
    assert (stock,A,B,Z,anchor)==(F(7,4),F(21,4),F(231,8),F(231,8),F(7))
    assert count==energy==0 and energy+anchor==7
    # Resetting second incoming stock loses half of the weighted first endpoint.
    reset=-sum((w*p/2 for p,w in ((F(1),F(1)),(F(2),F(3)))),F())
    assert reset==F(-7,2)
    swapped=F(1)*endings[1]+F(3)*endings[0]
    unweighted=sum(endings,F());assert swapped!=stock and unweighted!=stock
    rejects=[]
    for field,val in (('h','0'),('lambda_HI','0'),('outn','1')):
        r=dict(sample)
        if field=='lambda_HI':
            for s in SP:r['lambda_'+s]='0'
        else:r[field]=val
        try:branch(r)
        except AssertionError as e:rejects.append(str(e))
        else:raise AssertionError('INVALID_BRANCH_NOT_REJECTED')
    assert time.monotonic()-t<60
    return {'method':'exact Fraction, exp(-ln2)=1/2','stock':str(stock),'A':str(A),'B':str(B),'Z':str(Z),'anchor':str(anchor),'count':str(count),'energy':str(energy),'omit_anchor':str(energy+anchor),'reset_carry':str(reset),'swapped_stock':str(swapped),'unweighted_stock':str(unweighted),'invalid_branch_rejections':rejects,'elapsed_seconds':time.monotonic()-t}
def main():
    resource.setrlimit(resource.RLIMIT_AS,(1024*1024**2,1024*1024**2));di.configure(60);start=time.monotonic()
    pins={ZIP:'5498d936ee7d25b1322c6c4bb3b15315e6c31e4ec148076fe1682d068dc8fc67',ARC:'fbf8cd26e87cdffe83f236d4bc646b2c6ffab9a4ac408b83b1fef09ec7d72020',BASE/'code/local_enclosure.py':'fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370',BASE/'code/directed_interval.py':'ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5',BASE/'inputs/SIX_CONTROLS.json':'2f543b128bdb6efe020868475619765d1a08f47c102cf0b9e5f65cb615c146dd',PILOT/'pilot.py':'104eb217e32266289fbffc5e3349b72390bc36e9392ca016c8e35edbaa157f83',PILOT/'RESULTS.json':'75648e29291c3c364c2d8a0c859710d95074f1c12c5d910c61a4856465034b96'}
    hashes={str(p):sha(p) for p in pins};assert all(hashes[str(p)]==h for p,h in pins.items()),'IMMUTABLE_IDENTITY_MISMATCH'
    inputs=[UP/f'evidence/capture/{m}/{f}.csv' for m in MODES for f in ('SEGMENTS','NODES')]+[UP/f'inputs/{m}_STAGES.csv' for m in MODES]
    with tarfile.open(ARC,'r:gz') as tf:
        for p in inputs:
            b=tf.extractfile(str(p.relative_to(REC))).read();assert hashlib.sha256(b).hexdigest()==sha(p),'ARCHIVE_INPUT_MISMATCH'
            hashes[str(p)]=sha(p)
    atomic_json(ROOT/'START.json',{'hashes':hashes,'N':128,'precision':60,'serial':True,'primary_invocations':1,'limit_seconds':180,'memory_limit_MiB':1024,'native_runs':0,'gas_advances':0,'old_continuous_solves':0,'six_control_replays':0,'full_first2_runs':0,'independent_review':'PENDING'})
    eps=lift(1.602176634e-12);reuse=decode(json.loads((PILOT/'RESULTS.json').read_text()));reused={tuple(r['key']):r for r in reuse['segments']}
    stage={m:{int(r['step']):r for r in rows(UP/f'inputs/{m}_STAGES.csv')} for m in MODES}
    nodes={m:{(int(r['step']),int(r['node'])):r for r in rows(UP/f'evidence/capture/{m}/NODES.csv')} for m in MODES}
    selected={}
    for m in MODES:
        for r in rows(UP/f'evidence/capture/{m}/SEGMENTS.csv'):
            k=(m,int(r['step']),int(r['node']),int(r['segment']))
            if k[2] in NODES and (k[1],k[3]) in ORDER:assert k not in selected;selected[k]=r
    expected={(m,s,n,g) for m in MODES for n in NODES for s,g in ORDER};assert set(selected)==expected and len(selected)==36
    atomic_json(ROOT/'CONTROLS.json',controls(selected[('OFF',1,0,0)]))
    paths=[];computed=0;classes=set();subset={m:{} for m in MODES}
    for m in MODES:
      for node in NODES:
        ks=[(m,s,node,g) for s,g in ORDER];initial=lift(selected[ks[0]]['f0']);initialE=lift(selected[ks[0]]['e0']);weight=lift(selected[ks[0]]['weight']);assert weight.lo>0
        cumulative={};caps={};corrections={};anchor=IV(0);prev=None;outputs=[];stepc={};stepa=IV(0);stepcaps={}
        for index,k in enumerate(ks):
            r=selected[k];branch(r);assert lift(r['weight']).lo==weight.lo
            mask={s:float(r['e_mid'])>=cut for s,cut in zip(SP,(13.6,24.59,54.42))}
            c=Coefficients({'row':r,'stage':stage[m][k[1]],'mask':mask,'source_on':float(r['source_on'])==1})
            classes.add((node,index,tuple(mask.values()),c.source_on,bool(float(r['anchored']))))
            Ia=IV(0) if index==0 else prev-c.f0
            if index==0 or k[1]!=ks[index-1][1]:stepinitial=initial if index==0 else prev;stepE=c.e0;stepc={};stepa=IV(0);stepcaps={}
            if k in reused:
                old=reused[k];J=old['J'];g=old['g'];rem=old['remainder'];frozen=old['frozen'];cap=old['captured'];corrected=old['corrected'];S=old['S'];rad=old['midpoint_radii'];Pend=old['Pend'];DP=old['DP'];c.domain=old['domain']
                assert (Ia-old['Ia']).contains(0),'REUSED_CARRY_MISMATCH'
            else:
                J,bounds,rad=integrate(c);S=IV(abs(Ia).hi)+bounds['B_r'];j0=response_j(c.L,c.h);je=c.e0*response_j(c.L+1,c.h)
                g={'P1':(-c.L*c.h).exp(),'Z_eV':je,'QN':IV(0),'QE_eV':IV(0)};rem={'P1':S*bounds['H_h'],'Z_eV':S*bounds['H_E'],'QN':IV(0),'QE_eV':IV(0)}
                FN=c.f0*j0+c.qf*(c.h-j0)/c.L;FE=c.f0*je+c.e0*c.qf*(response_j(IV(1),c.h)-response_j(c.L+1,c.h))/c.L
                frozen={'Z_eV':FE,'QN':c.qf*c.h,'QE_eV':c.e0*c.qf*response_j(IV(1),c.h)};cap=captured(r,eps)
                for i,s in enumerate(SP):
                    for pref,gg,ff in (('A',c.lf[i]*j0,c.lf[i]*FN),('B',c.lf[i]*je,c.lf[i]*FE),('H',c.lf[i]*(je-c.chi[i]*j0),c.lf[i]*(FE-c.chi[i]*FN))):
                        label=pref+'_'+s+('_eV' if pref!='A' else '');g[label]=gg;frozen[label]=ff;rem[label]=S*bounds['effective_'+pref+'_'+s]
                corrected={label:J[label]+g[label]*Ia+sym(rem[label]) for label in g}
                Pf=c.f0*g['P1']+c.qf*j0;Pend=Pf+corrected['P1'];DP=Pend-lift(r['n']);computed+=1
            moments={label:frozen[label]+corrected[label] for label in frozen};fmcap={label:frozen[label]-cap[label] for label in frozen}
            add(cumulative,moments);add(stepc,moments);add(caps,cap);add(stepcaps,cap);add(corrections,{label:fmcap[label]+corrected[label] for label in frozen})
            count=Pend-initial+total(cumulative,'A')-cumulative['QN'];energy=c.endpoint_E*Pend-initialE*initial+total(cumulative,'B')+cumulative['Z_eV']-cumulative['QE_eV']-anchor
            scount=Pend-stepinitial+total(stepc,'A')-stepc['QN'];senergy=c.endpoint_E*Pend-stepE*stepinitial+total(stepc,'B')+stepc['Z_eV']-stepc['QE_eV']-stepa
            assert all(x.contains(0) for x in (count,energy,scount,senergy)),'LEDGER_CONTAINMENT_FAILURE'
            seam=IV(0)
            if index<2:seam=(lift(selected[ks[index+1]]['e0'])-c.endpoint_E)*Pend;anchor+=seam
            if index<2 and ks[index+1][1]==k[1]:stepa+=seam
            node_reduction=None
            if index==0 or index==2:
                nr=nodes[m][(k[1],node)];nc=captured(nr,eps);node_reduction={label:stepcaps[label]-nc[label] for label in stepcaps};node_reduction['P']=lift(r['n'])-lift(nr['n']);node_reduction['U_erg']=lift(r['u'])-lift(nr['u'])
            out={'key':k,'origin':'REUSED_REVIEWED_OFF700' if k in reused else 'NEW','Ia':Ia,'Pend':Pend,'DP':DP,'S':S,'J':J,'g':g,'remainder':rem,'continuous_minus_frozen':corrected,'frozen_minus_captured':fmcap,'frozen':frozen,'captured':cap,'captured_segment_to_node_reduction':node_reduction,'weighted_moments':{label:weight*v for label,v in moments.items()},'weighted_endpoint':weight*Pend,'weighted_anchor_to_next':weight*seam,'energy_endpoint_minus_captured_erg':eps*c.endpoint_E*Pend-lift(r['u']),'count_ledger':count,'energy_ledger':energy,'step_count_ledger':scount,'step_energy_ledger':senergy,'anchor_to_next':seam,'source_on':c.source_on,'mask':mask,'anchored':bool(float(r['anchored'])),'domain':c.domain,'midpoint_radii':rad}
            check(out);outputs.append(encode(out));prev=Pend
            atomic_json(ROOT/'CHECKPOINT.json',{'completed_paths':paths,'current_path':outputs,'new_segments_completed':computed,'elapsed_seconds':time.monotonic()-start})
            print(json.dumps({'key':k,'origin':out['origin'],'elapsed_seconds':time.monotonic()-start,'count_contains_zero':count.contains(0),'energy_contains_zero':energy.contains(0)}),flush=True)
            assert time.monotonic()-start<180,'PRIMARY_TIME_LIMIT'
        weighted={label:weight*v for label,v in cumulative.items()};weighted['P_final']=weight*Pend;weighted['anchor']=weight*anchor;add(subset[m],weighted)
        paths.append({'mode':m,'node':node,'weight':encode(weight),'segments':outputs,'weighted_reduction':encode(weighted),'cumulative_correction':encode(corrections)})
    assert computed==33 and len(paths)==12
    atomic_json(ROOT/'RESULTS.json',{'status':'PASS_MECHANICAL_PENDING_ASTRA','scope':'12 selected captured paths only','paths':paths,'selected_subset_weighted_reductions':encode(subset),'transition_classes':[str(x) for x in sorted(classes)],'segments':36,'new_segments':computed,'reused_segments':3,'elapsed_seconds':time.monotonic()-start,'max_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'display_floors':{'number':'1e-25','energy_eV':'1e-24'},'acceptance':{**{f'A{i:02}':'PASS_MECHANICAL' for i in range(1,9)},'A09':'PENDING_FRESH_ASTRA'},'holds':['physical','production','full_first2','new_gas_evolution','actual_photon_heat_recoil','receiver_adoption']})
if __name__=='__main__':main()
