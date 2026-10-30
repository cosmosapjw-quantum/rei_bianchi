#!/usr/bin/env python3
"""Sharp source-ordinate-free bounds within a fixed 21-knot linear Li II 2E1 model.

The physics of original BASS21 gas and kinematic photon pair is source-pinned to PR284.
Only normalization, positivity and optional monotonicity of unverified 1969 Table II
ordinates are assumed. No new IVP, no deposited heat or astrophysical photon transport.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, json, pathlib, tempfile, zipfile
import numpy as np
from scipy.integrate import simpson
from numpy.polynomial.legendre import leggauss

ROOT=pathlib.Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'source/PR284_FULL.zip'
SHA_PR284='fa3e5f2a5cc0eaaa458372dbd2d926ad6829451a16a04b1bd220b3abb26747c9'
PARENT_DIR='REI_F4_LII_2E1_PAIR_CORRELATED_20261030'
CATS=('ESC','H_I','He_I','He_II','Li_I')
KNOTS=np.linspace(0.,.5,21)
KNOT_AREAS=np.array([.0125]+[.025]*19+[.0125])
STAGES=['R'+str(i) for i in range(1,11)]+['C'+str(i) for i in range(1,11)]

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def safe_extraction(path,target):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('SOURCE_ZIP_CRC')
        for n in z.namelist():
            p=pathlib.PurePosixPath(n)
            if p.is_absolute() or '..' in p.parts:raise ValueError('SOURCE_ZIP_PATH')
        z.extractall(target)

def parent():
    if sha(UPSTREAM)!=SHA_PR284:raise ValueError('PR284_SOURCE_ZIP_SHA')
    t=tempfile.TemporaryDirectory(prefix='rei_cone_source_')
    try:
        safe_extraction(UPSTREAM,t.name)
        fp=pathlib.Path(t.name)/PARENT_DIR/'code/pair_joint.py'
        spec=importlib.util.spec_from_file_location('source_pinned_pair_284',fp)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module,t
    except Exception:
        t.cleanup();raise

def geometric_nodes(parent_module,order,thresholds):
    """Original quadrature geometry reconstructed WITHOUT any Drake A(y) ordinate."""
    if order<2:raise ValueError('ORDER')
    cuts=list(KNOTS)
    for chi in list(parent_module.THRESH.values())+list(thresholds):
        for y in (chi/parent_module.E_SINGLET_EV,1-chi/parent_module.E_SINGLET_EV):
            if 0<y<.5:cuts.append(float(y))
    cuts=sorted(set(cuts))
    g,w=leggauss(order);x=[];mass=[]
    for l,r in zip(cuts[:-1],cuts[1:]):
        x.extend(l+.5*(r-l)*(g+1))
        mass.extend(.5*(r-l)*w)
    return np.array(x),np.array(mass)

def summarize_bounds(basis,source_original=None):
    # basis shape = (20,193,5,5): 20 generated normalized spectra.
    assert basis.shape==(20,193,5,5)
    e=basis[:,:,0,0];p0=e
    p1=basis[:,:,0,1:].sum(axis=2)+basis[:,:,1:,0].sum(axis=2)
    p2=basis[:,:,1:,1:].sum(axis=(2,3))
    mean=p1+2*p2
    return {'P0':p0,'P1':p1,'P2':p2,'N':mean}

def calculate(order=8):
    pa,td=parent()
    try:
        original_rows,_,parent_summary,aux=pa.calculate(order)
        owner,owner_td=pa.read_owner()
        try:
            state,H,nb,cap,bins,net=owner.load_original()
            knots,kweights=geometric_nodes(owner,order,net.transition_energy_eV)
        finally:
            owner_td.cleanup()
        assert len(knots)==len(aux['y']) and np.max(abs(knots-aux['y']))<1e-14
        assert abs(np.sum(kweights)-.5)<3e-15
        # Compact nodal hat functions are exact for the parent piecewise-linear representation.
        hat=np.maximum(0.,1-np.abs(knots[:,None]-KNOTS[None,:])/(KNOTS[1]-KNOTS[0]))
        if abs(hat.sum(axis=1)-1).max()>2e-13:raise AssertionError('HAT_PARTITION')
        # Analytical areas of the nodal basis, no Li II published ordinates needed.
        measured_area=(hat*kweights[:,None]).sum(axis=0)
        if abs(measured_area-KNOT_AREAS).max()>1e-14:raise AssertionError('HAT_AREA')
        # Positivity cone: A0=0 and a1,...,a20 >=0. All possible normalized
        # spectra are convex mixtures of 20 individually normalized hats.
        hats=np.einsum('ki,zic,zid->kzcd',(hat[:,1:]*kweights[:,None]/KNOT_AREAS[None,1:]).T,aux['pl'],aux['ph'],optimize=True)
        # Monotone cone: A0=0, differences Delta a_j >=0. Cone rays are
        # nodal steps S_j=(0,...,0,1,...,1), j=1..20.
        step_areas=np.cumsum(KNOT_AREAS[1:][::-1])[::-1]
        step=np.cumsum((hats*KNOT_AREAS[1:,None,None,None])[::-1],axis=0)[::-1]/step_areas[:,None,None,None]
        if max(abs(hats.sum(axis=(2,3))-1).flatten())>4e-13:raise AssertionError('HAT_PROBABILITY')
        if max(abs(step.sum(axis=(2,3))-1).flatten())>4e-13:raise AssertionError('MONOTONE_PROBABILITY')
        if hats.min()<-1e-15 or step.min()<-1e-15:raise AssertionError('NEGATIVE_PROBABILITY')
        orig=aux['joint']
        # Parent source is used solely as an observational *witness* against the
        # source-agnostic envelopes; no A_TAB entry enters hats/step construction.
        A=np.asarray(owner.A_TAB,dtype=float)
        norm=np.dot(A,KNOT_AREAS)
        if A.shape!=(21,) or A[0]!=0 or np.any(np.diff(A)<0):raise ValueError('PARENT_OUTSIDE_CONE')
        rebuilt_pos=np.einsum('y,yzcd->zcd',A[1:]*KNOT_AREAS[1:]/norm,hats,optimize=True)
        rebuilt_mon=np.einsum('y,yzcd->zcd',np.diff(A)*step_areas/norm,step,optimize=True)
        reconstruction=max(abs(rebuilt_pos-orig).max(),abs(rebuilt_mon-orig).max())
        if reconstruction>6e-13:raise AssertionError('PARENT_CONVEX_RECONSTRUCTION')
        for arr in (hats,step):
            if np.any(orig < arr.min(axis=0)-4e-13) or np.any(orig > arr.max(axis=0)+4e-13):
                raise AssertionError('PARENT_OUTSIDE_ENVELOPE')
        p=summarize_bounds(hats);q=summarize_bounds(step)
        z=state['z'];x=state['x'];rates=np.array([r['conditional_all_singlet_pair_rate_per_baryon_s'] for r in original_rows]);
        if np.any(rates<-1e-40):raise ValueError('NEGATIVE_SOURCE')
        # A *single common* 2E1 spectral shape across all 193 epochs. Its
        # globally integrated linear response is bounded by extrema of the
        # integrated basis histories, not by integrating local minima/maxima.
        int_obj={}
        for name,ary in [('positive',p),('monotone',q)]:
            int_obj[name]={}
            for metric,v in ary.items():
                per_basis=simpson(v*rates[None,:]/H[None,:],x=x,axis=1)
                min_i=int(np.argmin(per_basis));max_i=int(np.argmax(per_basis))
                int_obj[name][metric]={'min':float(per_basis[min_i]),'max':float(per_basis[max_i]),'min_generator':min_i+1,'max_generator':max_i+1}
        old_int=parent_summary['integrated_conditional_events_per_baryon']
        if not (int_obj['monotone']['P2']['min']-1e-26<=old_int['two_absorbed']<=int_obj['monotone']['P2']['max']+1e-26):raise AssertionError('PARENT_INTEGRATED_P2')
        if not (int_obj['monotone']['N']['min']-1e-26<=old_int['expected_photoelectrons']<=int_obj['monotone']['N']['max']+1e-26):raise AssertionError('PARENT_INTEGRATED_N')
        epoch=[];channels=[];basis_rows=[]
        basis_summaries={'positive_hat':p,'monotone_step':q}
        for i in range(193):
            row={'epoch':i,'z':float(z[i]),'x':float(x[i]),'H_s':float(H[i]),'conditional_singlet_source_rate_per_baryon_s':float(rates[i]),'original_DAG':'working33/88|central28/88|fast4/7','no_new_IVP':0}
            for metric in ('P0','P1','P2','N'):
                rkey={'P0':'P_zero_absorbed','P1':'P_one_absorbed','P2':'P_two_absorbed','N':'mean_photoelectrons_per_singlet_pair'}[metric]
                row['PR284_'+metric]=float(original_rows[i][rkey])
                for cname,arr in [('positive',p),('monotone',q)]:
                    row[cname+'_'+metric+'_min']=float(arr[metric][:,i].min())
                    row[cname+'_'+metric+'_max']=float(arr[metric][:,i].max())
            epoch.append(row)
            for a,c1 in enumerate(CATS):
                for b,c2 in enumerate(CATS):
                    channels.append({'epoch':i,'z':float(z[i]),'low':c1,'high':c2,'PR284_conditional':float(orig[i,a,b]),
                    'positive_lower':float(hats[:,i,a,b].min()),'positive_upper':float(hats[:,i,a,b].max()),
                    'monotone_lower':float(step[:,i,a,b].min()),'monotone_upper':float(step[:,i,a,b].max())})
            for cone,vals in basis_summaries.items():
                for k in range(20):
                    basis_rows.append({'epoch':i,'z':float(z[i]),'family':cone,'generator':k+1,
                       'P0':float(vals['P0'][k,i]),'P1':float(vals['P1'][k,i]),'P2':float(vals['P2'][k,i]),'N':float(vals['N'][k,i])})
        audit={
           'scoped_claim':'Sharp within 21-knot nonnegative/optional-monotone piecewise-linear spectral families, NOT physical continuum without model assumptions',
           'parent_conditional_original_OCR':'PARENT_WITNESS_ONLY_NOT_USED_FOR_BOUND_GENERATION',
           'source_1969_pdf_visual':'NOT_VERIFIED',
           'independent_author_R6_C9':'NOT_RUN',
           'numerically_checked_reconstruction_max_error':float(reconstruction),
           'monotonicity_is_assumption':True,
           'nonlinear_covariance_bounds':'NOT_DERIVED_FROM_LINEAR_CONE_EXTREMA',
           'source_event_yield':'CONDITIONAL_ALL_SINGLET_PER_PR284',
           'full_rei17_bass21_owner':'UNBOUND'
        }
        summary={'schema':'REI_F4_LII_2E1_21KNOT_POSITIVE_CONE_V1',
           'timestamp':'2026-10-30','source_PR284_zip_sha256':SHA_PR284,'source_PR284_HEAD':'661f34c5216aa52402be6f9db5c16ab2e55ecfb3',
           'source_DR1969_ordinates':'UNVERIFIED_NOT_USED_IN_CONE_EXTREMA',
           'science':{'epochs':len(epoch),'joint_channel_rows':len(channels),'basis_rows':len(basis_rows),'positive_generators':20,'monotone_generators':20,'new_IVPs':0},
           'integrated_conditional_source_bounds':int_obj,
           'endpoints':{'first':epoch[0],'last':epoch[-1]},
           'parent_source_integrated':{'two_absorbed':old_int['two_absorbed'],'expected_photoelectrons':old_int['expected_photoelectrons'],'source_pairs':old_int['source_pairs']},
           'audit':audit,'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0,'F4':'PARTIAL','L4_ready':False}}
        return epoch,channels,basis_rows,summary,{'positive':hats,'monotone':step,'parent':orig,'state_z':z,'stage_weights':kweights}
    finally:td.cleanup()

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def write():
    epoch,channels,bases,summary,_=calculate(8)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    write_csv(out/'CONE_EPOCH_193.csv',epoch)
    write_csv(out/'CONE_CHANNEL_4825.csv',channels)
    write_csv(out/'CONE_GENERATORS_7720.csv',bases)
    (out/'RESULTS.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps({'science':summary['science'],'P2_source_global':summary['integrated_conditional_source_bounds'],'z2_monotone_P2':[epoch[-1]['monotone_P2_min'],epoch[-1]['monotone_P2_max']]},indent=2))

if __name__=='__main__':write()
