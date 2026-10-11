"""Single bounded reconstruction-opacity validation; never evolves history."""
import argparse
import hashlib
import importlib.util
import json
import math
import platform
import sys
import time
import traceback
from decimal import Decimal, localcontext
from pathlib import Path
import numpy as np
from reconstruction import Reconstruction, nodes, kernels, accounting, C, EV, CHI, THRESHOLDS

PINS={
'research/accel02_20261011/q1b_source_ic01/CONTRACT.json':'a46bbfa39eab67cf65fedbb0fe2adcb083dff77a0f73d52c85ceda890cb74a0b',
'research/accel02_20261011/q1b_source_ic01/check_source_ic.py':'64f99f871aa337045a8e8b507ef082a05d1afbcee1529df78f477bb03f847c45',
'research/accel02_20261011/q1b_source_ic01/evidence/RESULT.json':'38c809fed13085a0f2aa524b6057b605af980124f562ec45c205c6a8263ec0f8',
'research/accel02_20261011/q1b_source_ic01/evidence/EXECUTION_RECEIPT.json':'825d9d6124406f6fe4eac3b38e0cf024654dbce47ff23a832eb1bba6face9d46',
'research/physical_provider_20261010/hm12_data.py':'ede512206bd6f5acc85b1c6b90fda4edc256b4dd8a70c42f9726932b6bff5121',
'research/physical_provider_20261010/sources/UVB.out':'a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc',
'research/physical_provider_20261010/sources/emissivity.out':'88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
'research/physical_provider_20261010/sources/acquisition.json':'d9f3ce2a9174587124489d17542350cf01386eec8cdd5026be0399052f2e7b2b',
'research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json':'91959c5e09073ae89afcfe14937e6bc2dc4478692143873471934f542fc1ad6d',
'research/accel02_20261011/q1a/GRID_G1.json':'13bdcc466891d0edd18cd2c645f388cc13f89a88f13a0af44a9c0b6cd7136efd',
'research/accel02_20261011/q1a/NEXT_DESIGN.md':'296421ea8846c7f137a5094fcc4745b35608efbc0e082aa02b89acd80b4d4815',
'research/accel02_20261011/q1a/review/Q1B_PROPOSAL_REVIEW.json':'9cf208e79b5f6d426d4ad820dd5fe62c9f9f2800e9a6e476d51121c6307884bc',
'research/accel02_20261011/n1/provider.py':'42aa7ce3eb1029c653d0b97e622cfc7c45456d3547ad5c9d5d8fc52ffa271c3a',
'research/accel02_20261011/n1/native/src/main.rs':'239a08b0fdbe171f21112c128602be3ad9bbaae596ada1b6791fda482e8aeb76',
'research/accel02_20261011/n1/native/target/release/rei_n1_native':'3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac',
'research/accel02_20261011/n1/ABI.json':'b402f88af2443c459b929d0907eb5432ed65a0eff4307d53d5247e95c507900d',
'research/accel02_20261011/q1a/evidence/GAUSS1_FINE/IDENTITY.json':'640e8d27cf589242fa5c2db7d92ea420da6d39dc71f2191dffa2154bac8ed1d6',
'research/accel02_20261011/integration/run_native_history.py':'06275b5dd45e9e2b67264a8265c60d83966539093797748aa99e0a5ea5985602'}
RESULT={'unit':'Q1B_RECONSTRUCTION01','failures':[], 'execution':dict.fromkeys(['native_process','SIGMA','SIGMA_energies','RATES','RHS','JAC','ODE','build','history_replay'],0),
        'retained_holds':{'Q1A_number_ledger':'FAIL','Q1A_spectral_pair':'FAIL','global_admission':'HOLD'}}

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def check(condition,outcome,detail):
    if not condition:
        RESULT['failures'].append({'outcome':outcome,'detail':detail})
        raise ValueError(outcome)

def relative(actual,expected,tol,where,outcome='HOLD_ANALYTIC_FIXTURE'):
    error=abs(actual-expected);scaled=error/abs(expected) if expected else None
    check(scaled<=tol if expected else error==0,outcome,{'where':where,'actual':actual,'expected':expected,'scaled':scaled})
    return scaled if expected else 0.

def raw_power(a,b,p):
    """Independent Decimal80 oracle ∫q^p dlnq, no inversion machinery."""
    with localcontext() as ctx:
        ctx.prec=80
        aa,bb,pp=map(Decimal.from_float,(a,b,float(p)))
        return (bb/aa).ln() if p==0 else (bb**pp-aa**pp)/pp

def known_mean(a,b,p):
    with localcontext() as ctx:
        ctx.prec=80
        return float(raw_power(a,b,p+1)/raw_power(a,b,p))

def fixtures(edges):
    widths=np.diff(np.log(edges));cells=[(10.,20.),(float(edges[np.argmin(widths)]),float(edges[np.argmin(widths)+1])),
           (float(edges[np.argmax(widths)]),float(edges[np.argmax(widths)+1]))]
    checks=[]
    for a,b in cells:
        # Fixture cells above 50keV need R so their declared active support is whole cell.
        R=.25
        for N in (1.,1e-30):
            for p in (-8.,-1.,-2.**-30,0.,2.**-30,1.,8.):
                m=known_mean(a,b,p);rec=Reconstruction(a,b,R,N,R*N*m)
                errs=[relative(rec.oracle_moment(),N,1e-12,'inversion N'),
                      relative(rec.oracle_moment(1),N*m,1e-12,'inversion Q')]
                check(abs(rec.forward_mean-rec.mean)/(rec.b-rec.a)<=1e-12,'HOLD_RECONSTRUCTION_INVERSION','forward mean')
                checks.append({'cell':[a,b],'R':R,'N':N,'known_p':p,'p':rec.p,'iterations':rec.iterations,'doublings':rec.doublings,'errors':errs})
            for fraction in (2.**-40,.5,1.-2.**-40):
                m=a+(b-a)*fraction;U=R*N*m;observed=(U/R)/N
                check(a<observed<b,'HOLD_ANALYTIC_FIXTURE',{'target_mean':m,'observed_mean':observed,'N':N,'cell':[a,b]})
                rec=Reconstruction(a,b,R,N,U)
                checks.append({'cell':[a,b],'R':R,'N':N,'fraction':fraction,'p':rec.p,
                  'Q_error':relative(rec.oracle_moment(1),N*m,1e-12,'near endpoint Q'),'N_error':relative(rec.oracle_moment(),N,1e-12,'near endpoint N')})
        for endpoint in (a,b):
            check(((R*endpoint)/R)/1.==endpoint,'HOLD_ANALYTIC_FIXTURE','exact delta input representability')
            rec=Reconstruction(a,b,R,1.,R*endpoint)
            check(rec.delta==endpoint,'HOLD_ANALYTIC_FIXTURE','endpoint delta')
            relative(rec.oracle_moment(1),endpoint,1e-12,'delta Q')
        check(Reconstruction(a,b,R,0.,0.).empty,'HOLD_ANALYTIC_FIXTURE','empty')
    rejected=0
    invalid=[(10.,20.,1.,float('nan'),1.),(10.,20.,1.,1.,float('inf')),(10.,20.,1.,-1.,1.),
      (10.,20.,1.,1.,-1.),(10.,20.,1.,0.,1.),(10.,20.,1.,1.,9.),(10.,20.,1.,1.,21.),(20.,10.,1.,1.,15.),(10.,20.,0.,1.,15.),(40000.,80000.,1.25,1.,50000.)]
    for args in invalid:
        try:Reconstruction(*args)
        except ValueError:rejected+=1
    check(rejected==len(invalid),'HOLD_ANALYTIC_FIXTURE','invalid rejected')
    entries=[]
    for b in (40000.,50000.,60000.,80000.):
        R=50000./b
        rec=Reconstruction(40000.,80000.,R,0.,0.) if b==40000. else Reconstruction(40000.,80000.,R,1.,R*(40000.+b)/2)
        q,w=nodes(rec,32,0.)
        check(np.all((q>=rec.a)&(q<=rec.b)),'HOLD_ANALYTIC_FIXTURE','entry support')
        entries.append({'R':R,'active_upper':rec.b,'empty':rec.empty,'nodes':len(q)})
    rec=Reconstruction(10.,20.,.25,1.,.25*15.)
    relative(rec.oracle_moment(),1.,1e-12,'redshifted below10 retained')
    synthetic=[]
    for R in (1.,.5):
        for p in (-1.,0.,1.,3.):
            rec=Reconstruction(10.,40.,R,1.,R*known_mean(10.,40.,p))
            for r in (0.,1.,2.,-3.):
                for cut in (10.,17.,40.):
                    q,w=nodes(rec,32,R*cut)
                    sig=1e-18*(q/20.)**r
                    got=kernels(q,w,sig,R,1.)
                    with localcontext() as ctx:
                        ctx.prec=80
                        norm=raw_power(10.,40.,p)
                        n=Decimal(0) if cut==40. else raw_power(cut,40.,p+r)/norm
                        e=Decimal(0) if cut==40. else raw_power(cut,40.,p+r+1)/norm
                        factor=Decimal.from_float(C)*Decimal('1e-18')/Decimal(20)**Decimal.from_float(r)
                        expected=[float(factor*n),float(factor*e),float(factor*(Decimal.from_float(R)*e-n))]
                    errs=[relative(x,y,1e-12,'synthetic') for x,y in zip(got,expected)]
                    synthetic.append({'R':R,'p':p,'r':r,'cut':cut,'actual':got.tolist(),'expected':expected,'errors':errs})
    # Common particle/energy accounting is verified before any native launch.
    rec=Reconstruction(10.,40.,1.,1.,known_mean(10.,40.,0.))
    K=[]
    for ab,threshold in enumerate(THRESHOLDS):
        q,w=nodes(rec,32,threshold);K.append(kernels(q,w,np.full_like(q,1e-18),1.,CHI[ab]))
    particle_checks=[]
    for V in (1.,8.):
        for n in ((0.,0.,0.),(1.,0.,2.),(1.,2.,3.)):
            row=accounting(np.array(K),1.,V,n);changes=row['particle_changes'];events=row['events']
            check(changes['HI']+changes['HII']==0. and changes['HeI']+changes['HeII']+changes['HeIII']==0. and changes['electron']==sum(events),
                  'HOLD_COMMON_PHOTO_ACCOUNTING','stoichiometry')
            particle_checks.append({'V':V,'densities':n,**row})
    RESULT['fixtures']={'inversion':checks,'invalid_rejected':rejected,'entry':entries,'synthetic':synthetic,'below10_retained':True,'common_accounting':particle_checks}

def metric(a,b,scale=None):
    a,b=np.asarray(a),np.asarray(b);diff=a-b
    denom=float(np.sum(abs(b))) if scale is None else float(scale)
    err=float(np.sum(abs(diff)))
    return {'L1_error':err,'reference_L1':denom,'scaled':err/denom if denom else None,'exact_zero':bool(np.all(a==0) and np.all(b==0)),
            'signed_differences':diff.tolist()}

def assertmetric(m,tol,outcome,detail):
    check(m['scaled']<=tol if m['reference_L1'] else m['exact_zero'],outcome,{'where':detail,**m})

def run(root):
    observed={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in PINS}
    RESULT['input_sha256']=observed
    check(observed==PINS,'HOLD_INPUT_FILE_IDENTITY','18 pins')
    source=json.loads((root/'research/accel02_20261011/q1b_source_ic01/evidence/RESULT.json').read_text())
    grids={n:np.asarray(source['data'][n]['edges_eV'],float) for n in ('candidate','enriched')}
    for name,e in grids.items():
        check(len(e)==(88 if name=='candidate' else 175) and np.isfinite(e).all() and np.all(np.diff(e)>0) and e[0]==10. and e[-1]==168999.99999999997,
              'HOLD_GRID_SCHEMA_OR_DOMAIN',name)
    check(np.array_equal(grids['enriched'][::2],grids['candidate']),'HOLD_GRID_SCHEMA_OR_DOMAIN','enriched parents')
    RESULT['grid_sha256']={n:hashlib.sha256(e.astype('<f8').tobytes()).hexdigest() for n,e in grids.items()}
    fixtures(grids['candidate'])
    print('ANALYTIC_FIXTURES_PASS',flush=True)
    hm=load('q1br_hm12',root/'research/physical_provider_20261010/hm12_data.py');uv=hm.load_hm12()['uvb']
    recon={}
    for name,edges in grids.items():
        rows=[]
        for a,b in zip(edges[:-1],edges[1:]):
            hi=min(float(b),50000.)
            N=uv.moment(float(a),hi,15.9,power=0,proper_photons=True) if hi>a else 0.
            Q=uv.moment(float(a),hi,15.9,power=1,proper_photons=True) if hi>a else 0.
            rec=Reconstruction(float(a),float(b),1.,N,Q)
            relative(rec.oracle_moment(),N,1e-12,'UVB cell N','HOLD_RECONSTRUCTION_INVERSION')
            relative(rec.oracle_moment(1),Q,1e-12,'UVB cell Q','HOLD_RECONSTRUCTION_INVERSION')
            rows.append(rec)
        recon[name]=rows
    # Queue all SIGMA abscissae first, so cap check occurs before starting native.
    plans={};allq=[]
    for name,rows in recon.items():
        for order in (16,32):
            entries=[]
            for i,rec in enumerate(rows):
                for absorber,threshold in enumerate(THRESHOLDS):
                    q,w=nodes(rec,order,threshold)
                    start=len(allq);allq.extend(q.tolist())
                    entries.append((i,absorber,q,w,start,len(allq)))
            plans[(name,order)]=entries
    knots=uv.energies_eV
    panels=np.unique(np.r_[10.,50000.,knots[(knots>10.)&(knots<50000.)],THRESHOLDS,
                          grids['enriched'][(grids['enriched']>10.)&(grids['enriched']<50000.)]])
    for order in (16,32):
        x,w=np.polynomial.legendre.leggauss(order);entries=[]
        for a,b in zip(panels[:-1],panels[1:]):
            la,lb=math.log(a),math.log(b);q=np.exp((la+lb)/2+x*(lb-la)/2)
            weights=w*(lb-la)/2*uv.photon_number_log(q,15.9)
            start=len(allq);allq.extend(q.tolist());entries.append((q,weights,start,len(allq)))
        plans[('reference',order)]=entries
    # SIGMA returns all three absorbers: reuse exactly identical abscissae.
    uniqueq,inverse=np.unique(np.asarray(allq),return_inverse=True)
    RESULT['quadrature_abscissae']={'requested_entries':len(allq),'unique_SIGMA_energies':len(uniqueq)}
    check(len(uniqueq)<=65536,'HOLD_EXECUTION_RESOURCE_OR_CAP',{'SIGMA_energies':len(uniqueq)})
    native_mod=load('q1br_native_provider',root/'research/accel02_20261011/n1/provider.py')
    native=None;sigmas=[]
    try:
        native=native_mod.Native(root/'research/accel02_20261011/n1/native/target/release/rei_n1_native')
        RESULT['execution']['native_process']=1
        for start in range(0,len(uniqueq),4096):
            batch=uniqueq[start:start+4096]
            check(RESULT['execution']['SIGMA']<16,'HOLD_EXECUTION_RESOURCE_OR_CAP','SIGMA message cap')
            RESULT['execution']['SIGMA']+=1;RESULT['execution']['SIGMA_energies']+=len(batch)
            value=native.call('SIGMA',batch)
            check(len(value)==3*len(batch) and np.all(value>=0),'HOLD_NATIVE_SIGMA_EXECUTION','ABI finite nonnegative')
            sigmas.extend(value.reshape(-1,3).tolist())
        native.close();native=None
    except Exception as exc:
        if native is not None:
            native.proc.kill();native.proc.wait()
        if not str(exc).startswith('HOLD_'):
            check(False,'HOLD_NATIVE_SIGMA_EXECUTION',str(exc))
        raise
    sigma=np.asarray(sigmas)[inverse];values={}
    for (name,order),entries in plans.items():
        if name=='reference':
            K=np.zeros((len(entries),3,3))
            for i,(q,w,start,end) in enumerate(entries):
                for ab,threshold in enumerate(THRESHOLDS):
                    active=q>=threshold
                    K[i,ab]=kernels(q[active],w[active],sigma[start:end,ab][active],1.,CHI[ab])
        else:
            K=np.zeros((len(recon[name]),3,3))
            for i,ab,q,w,start,end in entries:K[i,ab]=kernels(q,w,sigma[start:end,ab],1.,CHI[ab])
        values[(name,order)]=K
    reference=values[('reference',32)].sum(axis=0)
    RESULT['metrics']={};RESULT['native_values']={f'{name}_{order}':K.tolist() for (name,order),K in values.items()}
    for ab in range(3):
        for j,label in enumerate(('K0','K1','H')):
            key=f'{("HI","HeI","HeII")[ab]}_{label}';den=float(np.sum(abs(values[('reference',32)][:,ab,j])))
            metrics={'reference_quadrature':metric(values[('reference',16)][:,ab,j],values[('reference',32)][:,ab,j],den)}
            assertmetric(metrics['reference_quadrature'],1e-8,'HOLD_REFERENCE_QUADRATURE',key)
            for name in recon:
                metrics[name+'_quadrature']=metric(values[(name,16)][:,ab,j],values[(name,32)][:,ab,j])
                assertmetric(metrics[name+'_quadrature'],1e-8,'HOLD_RECONSTRUCTION_QUADRATURE',key+' '+name)
                metrics[name+'_accuracy']=metric([values[(name,32)][:,ab,j].sum()],[reference[ab,j]],den)
                assertmetric(metrics[name+'_accuracy'],1e-4,'HOLD_INITIAL_UVB_RECONSTRUCTION_ACCURACY',key+' '+name)
            child=values[('enriched',32)][:,ab,j].reshape(-1,2).sum(axis=1)
            metrics['enriched_parent']=metric(child,values[('candidate',32)][:,ab,j],den)
            assertmetric(metrics['enriched_parent'],1e-4,'HOLD_INITIAL_UVB_RECONSTRUCTION_ACCURACY',key+' enriched parent')
            RESULT['metrics'][key]=metrics
    RESULT['accounting']=[]
    for name in recon:
        K=values[(name,32)].sum(axis=0)
        for V in (1.,8.):
            for densities in ((0.,0.,0.),(1.,0.,2.),(1.,2.,3.)):
                RESULT['accounting'].append({'grid':name,'V':V,'densities':densities,**accounting(K,1.,V,densities)})
    return 'PASS_RECONSTRUCTION_OPACITY_COMPONENT_PENDING_INDEPENDENT_REVIEW'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    started=time.monotonic()
    try:outcome=run(args.root)
    except Exception as exc:
        traceback.print_exc();outcome=str(exc) if str(exc).startswith('HOLD_') else 'HOLD_EXECUTION_RESOURCE_OR_CAP'
        RESULT['error_type']=type(exc).__name__;RESULT['error']=str(exc)
        if not RESULT['failures']:RESULT['failures'].append({'outcome':outcome,'detail':str(exc)})
    RESULT['outcome']=outcome;RESULT['wall_s']=time.monotonic()-started
    RESULT['environment']={'python':sys.version,'numpy':np.__version__,'platform':platform.platform()}
    RESULT['implementation_sha256']={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ('reconstruction.py','validate_reconstruction.py','CONTRACT.json')}
    with args.output.open('x') as f:json.dump(RESULT,f,indent=2,allow_nan=False)
    print(outcome,flush=True);sys.exit(0 if outcome.startswith('PASS_') else 1)
