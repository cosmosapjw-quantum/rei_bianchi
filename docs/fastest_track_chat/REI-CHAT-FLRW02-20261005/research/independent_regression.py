#!/usr/bin/env python3
"""Independent Decimal event/average oracle; reuses actual provider coefficients."""
import argparse,csv,io,itertools,json,subprocess
from decimal import Decimal,getcontext
from pathlib import Path
getcontext().prec=70
D=lambda x:Decimal(str(x))
C=D('29979245800')
EDGES=[13.598434599702,24.587389011,54.41776,200.0]
CENTERS=[20.,35.,70.]

def invoke(exe,args,rows):
    r=subprocess.run([str(exe),*args],input='\n'.join(','.join(map(str,row)) for row in rows)+'\n',text=True,capture_output=True,check=True)
    return list(csv.DictReader(io.StringIO(r.stdout)))

def cell_input(a,h,t,n,x,k=1):
    return [a,h,t,n,x,*[k*v for v in [3e-7,7e-8,2e-8]],2e-20,1e-21,5e-22,3e-22,2e-23,0,*CENTERS,*EDGES,1e-8,2e-9,3e-10,1e-12]

def oracle(v,out):
    a,H,T,n,x,*_=map(D,v);a3=a**3
    gammas=[C*D(out['sigma'+str(i)])*D(v[5+i]) for i in range(3)]
    photo=[n*(1-x)*g for g in gammas]
    rec=D(out['alpha'])*n*n*x*x;coll=D(out['ci'])*n*n*x*(1-x)
    F=[a3*H*D(v[17+i])*D(v[21+i]) for i in range(4)]
    dN=[a3*(D(v[8+i])-photo[i]-D(v[11+i]))+F[i+1]-F[i] for i in range(3)]
    dx=(sum(photo)+coll-rec)/n
    ex={'gamma':sum(gammas),'ne':n*x,'photo':sum(photo),'recombination':rec,'collision':coll,'dx':dx,'boundary_net':F[0]-F[3],'source_comoving':a3*sum(map(D,v[8:11]))}
    for i in range(3):ex['dN'+str(i)]=dN[i];ex['dn'+str(i)]=dN[i]/a3-3*H*D(v[5+i])
    gross=(sum(photo)+coll+rec)/n
    scales={k:max(abs(val),D('1e-290')) for k,val in ex.items()}
    scales['dx']=max(gross,D('1e-290'))
    for i in range(3):
        gross_ph=a3*(D(v[8+i])+photo[i]+D(v[11+i]))+F[i+1]+F[i]
        scales['dN'+str(i)]=max(gross_ph,D('1e-290'))
        scales['dn'+str(i)]=max(gross_ph/a3+3*H*D(v[5+i]),D('1e-290'))
    return ex,scales

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    plan=json.loads(Path(__file__).with_name('INDEPENDENT_EXPERIMENT_PLAN.json').read_text());g=plan['E2']['cell_grid'];maxima={};fails=[];checks=0;records=[];neg={}
    def check(name,err,point):
        nonlocal checks
        err=float(err);checks+=1;maxima[name]=max(maxima.get(name,0),err)
        if not err<=2e-12:fails.append({'check':name,'point':point,'error':err})
    for case in g['case']:
        inp=[cell_input(*v) for v in itertools.product(g['a'],g['H_s'],g['T_K'],g['nH_proper_cm3'],g['x'])]
        got=invoke(a.native,['cell',case,'1'],inp)
        assert len(got)==len(inp)
        for i,(v,o) in enumerate(zip(inp,got)):
            ex,sc=oracle(v,o);row={'case':case,'point':i,'a':v[0],'H':v[1],'T':v[2],'nH':v[3],'x':v[4]}
            for name,value in ex.items():
                error=abs(D(o[name])-value)/sc[name];check('cell_'+name,error,[case,i]);row[name+'_error']=float(error)
            check('photo_bridge',abs(D(o['photo_bridge_residual']))/max(abs(ex['photo']),D('1e-290')),[case,i])
            if v[1]>0:
                neg['extra_3Hx_max_scaled']=max(neg.get('extra_3Hx_max_scaled',0),float(3*D(v[1])*D(v[4])/sc['dx']))
                neg['comoving_3H_max_scaled']=max(neg.get('comoving_3H_max_scaled',0),float(3*D(v[1])*D(v[0])**3*D(v[5])/sc['dN0']))
            wrongrec=D(o['alpha'])*D(v[3])*D(v[4])
            truepercap=ex['recombination']/D(v[3]);neg['fixed_ne_recombination_max_scaled']=max(neg.get('fixed_ne_recombination_max_scaled',0),float(abs(wrongrec-truepercap)/sc['dx']))
            records.append(row)
    assert len(records)==144
    ph_inputs=[]
    for scale,H,m in itertools.product([.1,1.],[0.,1e-17,1e-15],[0.,1e-6,1e-3,1.]):
        ph_inputs.append([scale,H,1e-6,2e-7,3e-8,*EDGES,*[m*v for v in [1.,.2,.03,.001]],2e-20,1e-21,5e-22,1e-21,2e-22,1e-23])
    po=invoke(a.native,['photon'],ph_inputs)
    for i,(v,o) in enumerate(zip(ph_inputs,po)):
        av,H=map(D,v[:2]);av3=av**3;F=[av3*H*D(v[5+j])*D(v[9+j]) for j in range(4)]
        for j in range(3):
            gross=av3*(D(v[13+j])+D(v[16+j]))+F[j]+F[j+1];expected=av3*(D(v[13+j])-D(v[16+j]))+F[j+1]-F[j]
            check('photon_dN',abs(D(o['dN'+str(j)])-expected)/max(gross,D('1e-290')),i)
            proper=expected/av3-3*H*D(v[2+j])/av3;check('photon_dn',abs(D(o['dn'+str(j)])-proper)/max(gross/av3+3*H*D(v[2+j])/av3,D('1e-290')),i)
            if j==0 and F[0]>0:
                neg['omit_threshold_max_scaled']=max(neg.get('omit_threshold_max_scaled',0),float(F[0]/gross))
                neg['reverse_edge_sign_max_scaled']=max(neg.get('reverse_edge_sign_max_scaled',0),float(2*abs(F[1]-F[0])/gross))
    ensembles=[]
    for i in range(4):
        vs=[cell_input(.2,1e-16,10000,n,x,k) for n,x,k in [(1e-5,.1,1),(2e-4,.9,2),(5e-5,.3,3)]]
        if i==1:vs=[cell_input(.2,1e-16,10000,1e-4,x,1) for x in [0.,1.,1.]]
        weights=[.2,.5,.3] if i<2 else [2.,1.,4.];q=.4;qd=(i-1)*1e-17;irt=2e-16
        args=['ensemble','A',str(i%2),str(q),str(qd),str(irt)]
        e=invoke(a.native,args,[[w,*v] for w,v in zip(weights,vs)])[0]
        cs=invoke(a.native,['cell','A',str(i%2)],vs);ors=[oracle(v,o)[0] for v,o in zip(vs,cs)]
        w=list(map(D,weights));wn=sum(w);n=sum(wj*D(v[3]) for wj,v in zip(w,vs));a3=D('.2')**3
        XM=sum(wj*D(v[3])*D(v[4]) for wj,v in zip(w,vs))/n;XV=sum(wj*D(v[4]) for wj,v in zip(w,vs))/wn
        md=sum(wj*D(v[3])*o['dx'] for wj,v,o in zip(w,vs,ors))/n
        ed=sum(wj*sum(o['dN'+str(j)] for j in range(3)) for wj,o in zip(w,ors))/(a3*n)
        src=sum(wj*sum(map(D,v[8:11])) for wj,v in zip(w,vs))/n
        recomb=sum(wj*o['recombination'] for wj,o in zip(w,ors))/n
        ci=sum(wj*o['collision'] for wj,o in zip(w,ors))/n
        ot=sum(wj*sum(map(D,v[11:14])) for wj,v in zip(w,vs))/n
        bd=sum(wj*o['boundary_net'] for wj,o in zip(w,ors))/(a3*n)
        gross=sum(map(abs,[src,recomb,ci,ot,bd,ed,md,D(qd),D(q)*D(irt)]))
        expected={'XV':XV,'XM':XM,'XMdot':md,'etadot':ed,'source_perH':src,'recomb_perH':recomb,'coll_perH':ci,'other_perH':ot,'boundary_perH':bd,'defect_direct':D(qd)-src+D(q)*D(irt)}
        for name,value in expected.items():check('ensemble_'+name,abs(D(e[name])-value)/(max(abs(value),D('1e-290')) if name in ('XV','XM') else gross),i)
        check('ensemble_inventory',abs(D(e['combined_residual']))/gross,i);check('ensemble_defect',abs(D(e['defect_residual']))/gross,i)
        neg['XM_minus_XV_max']=max(neg.get('XM_minus_XV_max',0),float(abs(XM-XV)))
        ensembles.append({'fixture':i,'XV':float(XV),'XM':float(XM),'eta_dot_s':float(ed),'filling_defect_s':float(expected['defect_direct']),'geometry':'Q and Qdot supplied externally; diagnostic only'})
    bandN=1e-6;a0=.1;H=1e-16;left=2*bandN/(EDGES[1]-EDGES[0])
    ambiguity_inputs=[[a0,H,bandN*a0**3,0,0,*EDGES,v,0,0,0,0,0,0,0,0,0] for v in [left,0.]]
    amb=invoke(a.native,['photon'],ambiguity_inputs)
    ambiguity={'same_proper_bin_count':bandN,'descending_triangle_left_nE':left,'parabolic_hump_left_nE':0.0,'comoving_dot_triangle':float(amb[0]['dN0']),'comoving_dot_hump':float(amb[1]['dN0']),'status':'EXPECTED_NONUNIQUENESS_DETECTED' if float(amb[0]['dN0'])<0 and float(amb[1]['dN0'])==0 else 'FAIL'}
    if ambiguity['status']=='FAIL':fails.append({'check':'boundary_underdetermination'})
    for name,error in neg.items():
        if error<=2e-12:fails.append({'check':'negative_control_not_detected','name':name})
    a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/'independent_cell_points.csv').open('w',newline='') as f:
        cw=csv.DictWriter(f,fieldnames=list(records[0]));cw.writeheader();cw.writerows(records)
    result={'experiment':'E2+E2X','status':'PASS' if not fails else 'FAIL','cell_points':144,'photon_points':24,'ensemble_fixtures':4,'decimal_precision':70,'checks':checks,'max_errors':maxima,'negative_controls_detected':neg,'boundary_ambiguity':ambiguity,'ensemble_examples':ensembles,'failures':fails,'limits':plan['E2']['no_claim'],'provider_coefficients':'reused inputs; no new fit/source-accuracy claim'}
    (a.out/'INDEPENDENT_REGRESSION_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return bool(fails)
if __name__=='__main__':raise SystemExit(main())
