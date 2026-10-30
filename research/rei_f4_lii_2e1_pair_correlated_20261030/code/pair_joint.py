#!/usr/bin/env python3
"""Source-conditional correlated Li II 2E1 photon-pair absorption on saved BASS193 gas.

No IVP, no actual emission yield, no cosmological radiation transfer or gas heating.
The original Drake 1969 Li II printed table image is NOT independently verified;
this calculation is conditional on PR283's frozen 21-entry transcription.
"""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import zipfile
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHA_283 = '91c4c9f8cc5daa12f65e41e910b7de6d402096c13a817d88f72c7ac68d52355a'
SRC283 = ROOT/'source/PR283_FULL.zip'
ORIGINAL_GIT_HEAD = 'e6b026757ddceb7fcd227229c0eb71391751e771'
CATEGORIES = ('ESC', 'H_I', 'He_I', 'He_II', 'Li_I')


def sha(path): return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def read_owner():
    if sha(SRC283) != SHA_283:
        raise ValueError('PR283_SOURCE_ZIP_SHA_MISMATCH')
    tmp = tempfile.TemporaryDirectory(prefix='rei_pair_source_')
    try:
        root = pathlib.Path(tmp.name)
        with zipfile.ZipFile(SRC283) as z:
            if z.testzip() is not None: raise ValueError('PR283_CRC_FAIL')
            for info in z.infolist():
                name = pathlib.PurePosixPath(info.filename)
                if name.is_absolute() or '..' in name.parts: raise ValueError('ZIP_PATH_TRAVERSAL')
            z.extractall(root)
        ancestor = root/'REI_F4_LII_2E1_SOURCE_SPECTRAL_ABSORPTION_20261030'
        mod_path = ancestor/'code/two_e1_source.py'
        spec = importlib.util.spec_from_file_location('frozen_PR283_native_owner', mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, tmp
    except Exception:
        tmp.cleanup()
        raise


def calculate(order=8):
    m, tmp = read_owner()
    try:
        data, H, nb, capacities, spectral_events, net = m.load_original()
        z = data['z']; x = data['x']; Y = data['Y']
        assert Y.shape == (193, 21)
        y,w = m.nodes_weights(order,net.transition_energy_eV)
        n = len(y)
        E = np.concatenate((y*m.E_SINGLET_EV, (1-y)*m.E_SINGLET_EV))
        sigma,_ = net.photo_cross_sections(E)
        assert sigma.shape == (21,2*n)
        k_species = nb[:,None,None]*Y[:,:,None]*sigma[None,:,:]
        kappa = np.sum(k_species,axis=1)
        if np.any(kappa < 0) or np.any(H <= 0): raise ValueError('UNPHYSICAL_GAS')
        tau = kappa*m.C/H[:,None]
        p_abs = -np.expm1(-tau)
        p_survive = np.exp(-tau)
        safe = np.where(kappa>0,kappa,1)
        prob = np.zeros((len(z),2*n,len(CATEGORIES)))
        prob[:,:,0] = p_survive
        for c,ids in m.CAT_GROUPS.items():
            j = CATEGORIES.index(c)
            prob[:,:,j] = (k_species[:,list(ids),:].sum(axis=1)/safe)*p_abs
        if np.max(np.abs(prob.sum(axis=2)-1))>6e-14:raise AssertionError('PHOTON_PARTITION')
        # Conditional on photon energies and frozen gas, absorption events factor;
        # on averaging y their outcomes are coupled by E_hi = E_s-E_lo.
        pl=prob[:,:n,:];ph=prob[:,n:,:]
        joint=np.einsum('n,ina,inb->iab',w,pl,ph,optimize=True)
        if np.max(np.abs(joint.sum(axis=(1,2))-1))>3e-13:raise AssertionError('PAIR_NORM')
        marglo=joint.sum(axis=2); marghi=joint.sum(axis=1)
        indep=marglo[:,:,None]*marghi[:,None,:]
        total_variation=.5*np.abs(joint-indep).sum(axis=(1,2))
        p0=joint[:,0,0]
        p1=joint[:,0,1:].sum(axis=1)+joint[:,1:,0].sum(axis=1)
        p2=joint[:,1:,1:].sum(axis=(1,2))
        expectation=p1+2*p2
        variance=p1+4*p2-expectation**2
        if np.max(np.abs(p0+p1+p2-1))>3e-13:raise AssertionError('NABS_PARTITION')
        if np.min(variance)<-1e-13:raise AssertionError('NABS_VARIANCE')
        p2ind=(1-marglo[:,0])*(1-marghi[:,0])
        covariance=p2-p2ind
        # Original PR283 first-moment source-only calculation must be conserved.
        original_first,_ = m.frozen_transfer(data,H,nb,net,order)
        if np.max(np.abs(expectation-original_first['potential_ionizations']))>8e-13:
            raise AssertionError('PR283_PHOTON_FIRST_MOMENT')
        # Lower-energy photon E <= E_s/2 = 30.46eV < 54.42eV HeII threshold;
        # hence no low-photon HeII absorption in source native model.
        if np.max(np.abs(joint[:,CATEGORIES.index('He_II'),:]))>1e-15:
            raise AssertionError('HEII_LOW_PHOTON_FORBIDDEN')
        K=np.array([float(row['K_events_per_baryon_s']) for row in capacities])
        Kforced=np.array([float(row['triplet_forced_events_per_baryon_s']) for row in capacities])
        Ksinglet=np.maximum(0.,K-Kforced)
        # hypothetical all-singlet branch in permitted K source, never actual yield
        source_p0=Ksinglet*p0;source_p1=Ksinglet*p1;source_p2=Ksinglet*p2
        time_exposure=lambda rates: m.simpson_time(rates,x,H)
        result=[];grid=[]
        for i in range(len(z)):
            r=dict(epoch=i,z=float(z[i]),x=float(x[i]),H_s=float(H[i]),n_b_m3=float(nb[i]),
                   original_BASS_K_rate_per_baryon_s=float(K[i]),
                   conditional_all_singlet_pair_rate_per_baryon_s=float(Ksinglet[i]),
                   P_zero_absorbed=float(p0[i]),P_one_absorbed=float(p1[i]),P_two_absorbed=float(p2[i]),
                   P_two_independent_marginals=float(p2ind[i]),
                   event_correlation_covariance=float(covariance[i]),
                   two_photon_joint_TV_vs_marginal_independence=float(total_variation[i]),
                   mean_photoelectrons_per_singlet_pair=float(expectation[i]),
                   photoelectron_count_variance_per_pair=float(variance[i]),
                   conditional_pair_source_zero_absorbed_per_baryon_s=float(source_p0[i]),
                   conditional_pair_source_one_absorbed_per_baryon_s=float(source_p1[i]),
                   conditional_pair_source_two_absorbed_per_baryon_s=float(source_p2[i]),
                   conditional_pair_source_photoelectrons_per_baryon_s=float(Ksinglet[i]*expectation[i]),
                   original_working_DAG='33/88',original_central_DAG='28/88',physical_fast_DAG='4/7',new_IVPs=0)
            result.append(r)
            for a,ca in enumerate(CATEGORIES):
                for b,cb in enumerate(CATEGORIES):
                    grid.append(dict(epoch=i,z=float(z[i]),low_photon_outcome=ca,high_photon_outcome=cb,
                                     probability_per_singlet_pair=float(joint[i,a,b]),
                                     product_of_unconditional_marginals=float(indep[i,a,b]),
                                     correlation_defect=float((joint-indep)[i,a,b]),
                                     conditional_source_event_rate_per_baryon_s=float(Ksinglet[i]*joint[i,a,b]),
                                     valid_source_transcription='PR283_OCR_PARTIAL'))
        # Two photons jointly photoionize H I/He I: integer outcomes of frozen static process.
        p_both_HHe=joint[:,1:3,1:3].sum(axis=(1,2))
        pr283_norm=m.PAIR_NORM
        summary={
           'schema':'REI_F4_LII_2E1_CORRELATED_PHOTON_PAIR_V1',
           'source_owner':'cosmosapjw-quantum/rei_bianchi PR283 source-qualified CONDITIONAL model',
           'source_archive_sha256':SHA_283,
           'read_only_parent_head':ORIGINAL_GIT_HEAD,
           'source_assumption':'Drake1969 LiII 21-grid OCR transcription from PR283 not direct visual verified',
           'model_assumption':'homogeneous frozen BASS gas at each epoch for one proper Hubble length; conditional independence of absorption given y; unknown singlet branching artificially set 1 among allowed sources',
           'physical_source_ionizations_not_inferred':True,
           'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','delta':0,'F4':'PARTIAL','L4_ready':False},
           'shape':{'epochs':len(result),'joint_channel_cells':len(grid),'photons_per_pair':2,'outcome_categories':list(CATEGORIES),'Gauss_order':order,'quadrature_points_per_half':n},
           'source_table':{'doi':'10.1103/PhysRev.180.25','integrated_rate_s_inv':float(pr283_norm),'visual_scan':'UNVERIFIED'},
           'extrema':{},'integrated_conditional_events_per_baryon':{
             'zero_absorbed':float(time_exposure(source_p0)),
             'one_absorbed':float(time_exposure(source_p1)),
             'two_absorbed':float(time_exposure(source_p2)),
             'expected_photoelectrons':float(time_exposure(Ksinglet*expectation)),
             'both_H_or_He_photons_absorbed':float(time_exposure(Ksinglet*p_both_HHe)),
             'two_absorbed_independent_marginal_approx':float(time_exposure(Ksinglet*p2ind)),
             'source_pairs':float(time_exposure(Ksinglet))},
           'boundaries':{'actual_pair_emission':'UNBOUND','full_radiative_transfer':'NOT_RUN','gas_heat':'UNBOUND','REI17_BASS21_thermal_clock':'UNBOUND','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','native_subagent':'NOT_AVAILABLE','new_IVPs':0,'NO_MERGE':True,'NO_FORCE_PUSH':True,'AUTO_NEXT_NODE':False,'NO_BUDGET_RESET':True}}
        for key,v in [('p_two',p2),('covariance',covariance),('joint_TV',total_variation),('mean_electrons',expectation),('p_both_HHe',p_both_HHe)]:
            max_idx=int(np.argmax(v));min_idx=int(np.argmin(v))
            summary['extrema'][key]={'min':float(v[min_idx]),'z_min':float(z[min_idx]),'max':float(v[max_idx]),'z_max':float(z[max_idx])}
        return result,grid,summary,{'y':y,'weights':w,'joint':joint,'pl':pl,'ph':ph,'indep':indep,'tau':tau}
    finally:
        tmp.cleanup()


def write():
    rows,grid,summary,aux=calculate()
    output=ROOT/'results';output.mkdir(exist_ok=True)
    for name,data in [('PAIR_EPOCH_193.csv',rows),('PAIR_OUTCOMES_4825.csv',grid)]:
        with (output/name).open('w',newline='',encoding='utf8') as f:
            writer=csv.DictWriter(f,data[0].keys());writer.writeheader();writer.writerows(data)
    (output/'RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
    print(json.dumps({'epochs':len(rows),'joint_rows':len(grid),'P2_first':rows[0]['P_two_absorbed'],
        'P2_last':rows[-1]['P_two_absorbed'],'cov_first':rows[0]['event_correlation_covariance'],
        'cov_last':rows[-1]['event_correlation_covariance'],
        'integrated':summary['integrated_conditional_events_per_baryon']},indent=2))

if __name__=='__main__':write()
