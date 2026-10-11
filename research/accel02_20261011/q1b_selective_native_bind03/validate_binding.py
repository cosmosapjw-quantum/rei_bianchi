"""One frozen selective caller/JVP validation; no history or build."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback
import numpy as np
from caller import Caller, photon_jvp, EV, CHI, Q1B
from reconstruction import reconstruct, opacity_moments, UndefinedJacobian, TraceRequired, QuadratureNotConverged
from source_cells import table_cell_moments
from grid_cells import grid_array_sha256

UNIT = Path(__file__).resolve().parent
BASE = 'research/accel02_20261011/'
PINS = {
 BASE+'q1b_selective_c12_02/evidence/attempt2/RESULT.json':'82303c3fea4f8ff73383d7c1d717414880f6e39b596649c1be1544c65f039fd1',
 BASE+'q1b_selective_c12_02/reconstruction_selective.py':'02faaca63e765b06d2286d07cc7835f445a372681ab753ac0091640ccc0eb741',
 BASE+'q1b_selective_c12_02/validate_selective.py':'35d8415c67851cfdd1fbbb8ff292be63774d6f5266f83cacebdb1f95f6dad2d4',
 BASE+'q1b/reconstruction.py':'80a48fa9723414d6c0db31cb8a2c9287aacd1665b61a7eda5c61441bad54b4f8',
 BASE+'q1b/opacity_native.py':'6818b100e7a5331f9f244c2788813ea5ba3a746ad6c801b02e7fd1943706e9b1',
 BASE+'q1b/source_cells.py':'1200e88036d6af443d6f350d896d790953f0a04f24caa4d893b420abeb10f631',
 BASE+'q1b/grid_cells.py':'bc6e4dd6b35273dc27fc53417f4b1779c21ea6652ed1ff73cfb8d7b74e555a84',
 BASE+'q1b/native/src/main.rs':'147884bf5ed60024a265803896a7c76d50e4db9f28f4b24b69a4572e9634a2f6',
 BASE+'q1b/native/target/release/rei_q1b_cell_native_v1':'e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f',
 BASE+'n1/native/target/release/rei_n1_native':'3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac',
 'research/physical_provider_20261010/background.py':'b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d'
}
RESULT = {'unit':'Q1B3_SELECTIVE_CALLER_BINDING01','checks':[], 'JVP':[],
          'executor':'controller_direct_owner_authorized','runtime_model':'NOT_INDEPENDENTLY_OBSERVED',
          'global_admission':'HOLD','ODE':0,'build':0,'old_suite_replay':0}


def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, value):
    def convert(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        raise TypeError(type(v).__name__)
    with p.open('x') as f:json.dump(value,f,indent=2,allow_nan=False,default=convert)

def need(ok, label):
    if not ok:raise AssertionError(label)

def check(label, actual, expected, scale=None, tolerance=2e-11):
    a,b = np.asarray(actual,float),np.asarray(expected,float)
    s = np.maximum(abs(a),abs(b)) if scale is None else np.broadcast_to(np.asarray(scale,float),a.shape)
    diff = abs(a-b)
    err = np.divide(diff,s,out=np.zeros_like(diff),where=s!=0)
    zero_ok = bool(np.all(diff[s==0]==0))
    ok = bool(np.all(np.isfinite(a)) and np.all(np.isfinite(b)) and np.all(err<=tolerance) and zero_ok)
    RESULT['checks'].append({'label':label,'max_scaled':float(np.max(err)),'zero_ok':zero_ok,'tolerance':tolerance,'pass':ok})
    need(ok,'HOLD_'+label)

def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec);sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def fixture_gas(g,x,T):
    w = 1.5*1.380649e-16*T*(1+g['nHe']/g['nH']+x[0]+g['nHe']/g['nH']*(x[1]+2*x[2]))/EV
    return np.r_[x,w]

def check_native(o,d,cells,g,gas):
    nh,ne = g['nH'],g['nHe'];x,y,z = gas[:3];V = g['a_rel']**3
    lower = np.array([nh*(1-x),ne*(1-y-z),ne*y])
    K0,KE = cells[:,7:10],cells[:,10:13]
    gam = K0.sum(axis=0)/V;events = lower*gam
    check('native_Gamma',o[8:11],gam)
    check('native_photo_gas',o[:4]-d[:4],
          [events[0]/nh,(events[1]-events[2])/ne,events[2]/ne,np.sum((KE-CHI*K0)*lower)/(V*nh)])
    ndot = cells[:,5]-K0@lower
    udot = cells[:,6]-KE@lower-cells[:,2]*cells[:,4]
    check('native_Ndot',o[15::2],ndot)
    check('native_Udot',o[16::2],udot)
    check('native_absorbed_number',o[7],np.sum(K0@lower))
    check('native_source_energy',o[6],EV*np.sum(cells[:,6]))
    check('native_radiation_work',o[5]-d[5],EV*np.sum(cells[:,2]*cells[:,4]))
    check('local_cancellation',o[12:14],[0.,0.],scale=[1.,1.],tolerance=1e-12)

def run(root):
    prior = json.loads((root/(BASE+'q1b_selective_c12_02/evidence/attempt2/RESULT.json')).read_text())
    pins = dict(PINS);pins.update(prior['input_sha256'])
    pins.update({BASE+'q1b_selective_c12_02/'+p:s for p,s in prior['implementation_sha256'].items()})
    observed = {p:digest(root/p) for p in pins};RESULT['input_sha256']=observed
    need(observed==pins,'HOLD_INPUT_IDENTITY')
    RESULT['implementation_sha256']={p.name:digest(p) for p in [UNIT/'CONTRACT.json',UNIT/'caller.py',Path(__file__)]}
    source_ref = json.loads((root/(BASE+'q1b_source_ic01/evidence/RESULT.json')).read_text())
    mu=np.array(source_ref['geometry']['mu']);weights=np.array(source_ref['geometry']['weights']);R=np.ones(2)
    grids={}
    edge_pins={'candidate':'a750fdc7338f3e7a4a3e315f39dfb35aa9a990878c5f65f530456d4a2642f26e','enriched':'9f2f1435b2de47a1c4c150ec07085790ac01de9aea59d4a95a713124f54f1951'}
    for name,label in [('candidate','C02'),('enriched','E02')]:
        edges=np.array(prior['grids'][name]['edges_eV'])
        need(hashlib.sha256(edges.astype('<f8').tobytes()).hexdigest()==edge_pins[name],'HOLD_GRID_IDENTITY')
        grid={'member':'SELECTIVE_'+label,'q_edges_eV':edges.tolist(),'initial_mu':mu.tolist(),
              'angular_weights':weights.tolist(),'edge_sha256':edge_pins[name],
              'arrays_sha256':grid_array_sha256(edges,mu,weights),'energy_cells':len(edges)-1,
              'scope':'distinct from published C1/C2; copied stored edges, not regenerated'}
        save(UNIT/('GRID_SELECTIVE_'+label+'.json'),grid);grids[label]=grid
    edges=np.asarray(grids['C02']['q_edges_eV']);RESULT['grids']=grids
    physical=root/'research/physical_provider_20261010'
    hm=load('binding03_hm12',physical/'hm12_data.py');tables=hm.load_hm12()
    bg=load('binding03_background',physical/'background.py').BianchiBackground(r=0.,z_i=15.9)
    # Only t=0 constants: no time_of_redshift, interval preparation or integration.
    g=bg.at(0.);g['Tcmb_K']=2.7255*(1+15.9)
    gas=fixture_gas(g,[2e-4,0.,0.],20.)
    initial=table_cell_moments(tables['uvb'],15.9,edges,R,weights)
    N,U=initial['N'],initial['U_eV'];RESULT['initial_geometry']=g;RESULT['initial_gas']=gas
    for role,table,saved in [('IC',tables['uvb'],source_ref['data']['candidate']['initial_UVB_moments']),
                             ('source',tables['emissivity'],source_ref['data']['candidate']['source_history'][0])]:
        for label,lo in [('full',10.),('HI_ionizing',13.60),('HeI_ionizing',24.59),('HeII_ionizing',54.42)]:
            moments=table_cell_moments(table,15.9,edges,R,weights,(lo,50000.))
            check(role+'_'+label,[moments['N'].sum(),EV*moments['U_eV'].sum()],
                  [saved[label+'_number_ref'],saved[label+'_energy_ref']],tolerance=1e-12)
    caller=None
    try:
        caller=Caller()
        o,cells,moments,states,source=caller.assemble(0.,g,gas,edges,mu,R,N,U,tables,weights)
        RESULT['initial_states']=states;RESULT['initial_cells']=cells;RESULT['initial_native']=o
        K0=cells[:,7:10].reshape(2,88,3).sum(axis=0)
        KE=cells[:,10:13].reshape(2,88,3).sum(axis=0)
        actual=np.stack([K0,KE,KE-CHI*K0],axis=2)
        old=np.array(prior['native_values']['candidate_32'])
        reference=np.array(prior['native_values']['reference_32']).sum(axis=0)
        check('same_closure_L1',np.sum(abs(actual-old),axis=0),np.zeros((3,3)),scale=abs(reference),tolerance=1e-7)
        check('direct_UVB_total',actual.sum(axis=0),reference,scale=abs(reference),tolerance=1e-4)
        dark=caller.submit(0.,g,gas,[]);check_native(o,dark,cells,g,gas)
        Nb,Ub=N.copy(),U.copy();Nb[0,12]*=1.01;Ub[0,12]*=1.01
        ob,cb,_,_,_=caller.assemble(0.,g,gas,edges,mu,R,Nb,Ub,tables,weights)
        oa,ca,_,_,_=caller.assemble(0.,g,gas,edges,mu,R,N,U,tables,weights)
        need(not np.array_equal(o,ob) and not np.array_equal(cells[:,7:],cb[:,7:]),'HOLD_STALE_OPACITY')
        need(np.array_equal(o,oa) and np.array_equal(cells,ca),'HOLD_A_B_A_REPEATABILITY')
        RESULT['A_B_A']={'pass':True,'same_t':0.,'changed_cell':[0,12],'factor':1.01}
        print('CURRENT_STAGE_C02_BINDING_PASS',flush=True)
        fixed={'a_rel':1.,'b':0.,'H':0.,'s':0.,'nH':1e-3,'nHe':8e-5,'Tcmb_K':46.,'fractions':[.2,.3,.1]}
        fixedgas=fixture_gas(fixed,fixed['fractions'],5000.)
        fields=np.array([0,1,2,3,4,5,6,7,8,9,10,11,14,15,16])
        for index in [12,13,17,28,34]:
            a,b=edges[index:index+2];m=U[0,index]/N[0,index];n=1e-8;u=n*m
            def evaluate(nv,uv):
                cell=reconstruct(nv,uv,1.,a,b);need(cell.status=='INTERIOR','HOLD_JVP_CONE')
                val=caller.opacity.moments(cell,orders=(64,128),rtol=1e-7)
                row=[0.,1.,0.,nv,uv,0.,0.,*val['K0'],*val['KE']]
                native=caller.submit(0.,fixed,fixedgas,[row])
                return val,native
            baseline,onative=evaluate(n,u)
            J=np.array(baseline['jacobian_N_U'])
            for label,direction in [('amplitude',np.array([n,u])),('mean',np.array([0.,n*.25*min(m-a,b-m)]))]:
                prediction,scale,pK,sK=photon_jvp(J,direction,fixed,direction[1],0.)
                differences=[];Kdifferences=[]
                row={'cell':index,'direction_name':label,'direction':direction,'analytic':prediction,'scales':scale,'epsilons':[]}
                RESULT['JVP'].append(row)
                for eps in [2.**-8,2.**-9,2.**-10]:
                    vp,op=evaluate(*(np.array([n,u])+eps*direction))
                    vm,om=evaluate(*(np.array([n,u])-eps*direction))
                    fd=(op-om)/(2*eps)
                    kp=np.stack([vp['K0'],vp['KE']],axis=1);km=np.stack([vm['K0'],vm['KE']],axis=1)
                    fk=(kp-km)/(2*eps)
                    row['epsilons'].append({'epsilon':eps,'native_difference':fd,'moment_difference':fk})
                    check('JVP_native_'+str(index)+'_'+label+'_'+str(eps),fd[fields],prediction[fields],scale=scale[fields],tolerance=1e-7)
                    check('JVP_moments_'+str(index)+'_'+label+'_'+str(eps),fk,pK,scale=sK,tolerance=1e-7)
                    differences.append(fd);Kdifferences.append(fk)
                for j in range(2):
                    rich=(4*differences[j+1]-differences[j])/3
                    krich=(4*Kdifferences[j+1]-Kdifferences[j])/3
                    check('Richardson_native_'+str(index)+'_'+label+'_'+str(j),rich[fields],prediction[fields],scale=scale[fields],tolerance=1e-7)
                    check('Richardson_moments_'+str(index)+'_'+label+'_'+str(j),krich,pK,scale=sK,tolerance=1e-7)
        empty=reconstruct(0.,0.,1.,10.,20.);value=caller.opacity.moments(empty)
        need(value['K0']==value['KE']==[0.,0.,0.],'HOLD_EMPTY_VALUE')
        try:opacity_moments(empty,lambda q:np.ones_like(q))
        except UndefinedJacobian as exc:need('NO_JAC_AT_EMPTY' in str(exc),'HOLD_EMPTY_JAC_STATUS')
        else:raise AssertionError('HOLD_EMPTY_JAC_ALLOWED')
        try:caller.opacity.moments(reconstruct(1.,20.,1.,10.,20.))
        except TraceRequired:pass
        else:raise AssertionError('HOLD_ENDPOINT_TRACE_BYPASSED')
        a=50000.;b=a*(1+1e-12);narrow=reconstruct(1.,a+(b-a)/3,1.,a,b)
        try:opacity_moments(narrow,lambda q:(q-a)/(b-a))
        except QuadratureNotConverged as exc:need('FLOAT_Q_COORDINATE_UNRESOLVED' in str(exc),'HOLD_NARROW_REASON')
        else:raise AssertionError('HOLD_NARROW_FALSE_PASS')
        RESULT['boundary_regressions']='PASS_EMPTY_VALUE_NO_EMPTY_JAC_TRACE_REQUIRED_NARROW_REJECTED'
        RESULT['outcome']='PASS_SELECTIVE_CURRENT_STAGE_NATIVE_BINDING_AND_INTERIOR_PHOTON_JVP_SCOPED'
    finally:
        if caller is not None:
            RESULT['execution']=caller.counts.copy()
            caller.close()
    need(all(digest(root/p)==v for p,v in pins.items()),'HOLD_INPUT_CHANGED')
    RESULT['frozen_inputs_unchanged']=True


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();need(not args.output.exists(),'CREATE_ONLY_OUTPUT')
    started=time.monotonic();exit_code=0
    try:run(args.root)
    except Exception as exc:
        RESULT['outcome']='HOLD_BINDING03_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)}
        traceback.print_exc();exit_code=1
    RESULT['wall_s']=time.monotonic()-started
    save(args.output,RESULT)
    print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT.get('execution')}),flush=True)
    raise SystemExit(exit_code)
