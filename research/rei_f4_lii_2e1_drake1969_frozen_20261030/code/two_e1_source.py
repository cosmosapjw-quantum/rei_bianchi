#!/usr/bin/env python3
"""Li II singlet E1E1 differential spectrum from Drake/Victor/Dalgarno (1969)
joined to PR282/PR280 archived original BASS21 photoevents and static H/He/Li opacity.

Scientific scope: CONDITIONAL all-singlet spectral source, unknown singlet yield;
static frozen one-Hubble-length absorption opportunity, NOT cosmological transport,
NOT actual ionization/thermal deposition and NO new IVP.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, io, json, pathlib, tempfile, zipfile
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import simpson
ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'source/PR282_FULL.zip'
SHA_PR282 = 'a0f15cab2a283c1cfdf5c2a1fa8d2bc1fe9e232c1754cdaf4625ca0ff65107c0'
SHA_PR278 = 'df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db'
SHA_PR280 = 'fd9b8343ed2ea48b6caa9eff8aa5592d34a75fb77cfe223c81af3afbd8a21a91'
SHA_TRAJECTORY = '37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
OWNER = 'cc602e209e7deeb511ab2a1f3b2268d55206c43c'
ROOT282 = 'REI_F4_LII_M1_FROZEN_ABSORPTION_20261030/'
ROOT280 = 'REI_F4_LI1S_RADIATIVE_PHOTON_20261030/'
C = 299792458.
EV_ERG = 1.602176634e-12
E_TRIPLET_EV = 59.020723673157676
E_SINGLET_EV = 60.922559447552
THRESH = {'H_I': 13.598434599702,'He_I': 24.587389011,'He_II': 54.417765486}
CAT_GROUPS={'H_I':(1,3,5),'He_I':(7,10),'He_II':(8,11),'Li_I':(13,17)}
# Journal source: G.W.F. Drake, G.A. Victor & A. Dalgarno,
# Phys. Rev. 180, 25-32 (1969), Table II, 'Li II' column.
# Reported differential rate A(y) [s^-1 per unit y], y=E_low/(E1+E2), y in [0, 1/2].
# 1969 typeset scan extracted by Exa 2026-10-30:
# glyph 3.V9(2) transcribed as 3.79(2), 3.V4(3) as 3.74(3),
# 4.V3(3) as 4.73(3), O/0 replacements documented.
Y_TAB = np.linspace(0.0, 0.5, 21)
A_TAB = np.array([0,379,1110,1810,2420,2940,3380,3740,4060,4320,4540,
                  4730,4880,5020,5130,5220,5290,5350,5380,5410,5420],float)
SOURCE_DOI='10.1103/PhysRev.180.25'
SOURCE_SCAN='https://uwindsor.scholaris.ca/bitstreams/0cd0ebf7-0164-4c22-9aaa-71af11cfea5f/download'
SOURCE_CROSSCHECK='10.1103/PhysRevA.56.1288' # Derevianko & Johnson (1997), Li II 1.940e3 s^-1
SOURCE_RATE_1997=1940.0
PAIR_NORM = float(np.trapezoid(A_TAB,Y_TAB))

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def unpack_safe(z:zipfile.ZipFile, dest:pathlib.Path):
    if z.testzip() is not None:raise ValueError('ZIP_CRC')
    for n in z.namelist():
        parts=pathlib.PurePosixPath(n)
        if parts.is_absolute() or '..' in parts.parts:raise ValueError('ZIP_PATH')
    z.extractall(dest)

def load_original():
    raw=ARCHIVE.read_bytes()
    if sha(raw)!=SHA_PR282: raise ValueError('PR282_IMMUTABLE_SOURCE_SHA')
    with tempfile.TemporaryDirectory(prefix='rei_2e1_source_') as td:
        base=pathlib.Path(td)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            unpack_safe(z,base/'pr282')
            pr278=z.read(ROOT282+'source/REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip')
            pr280=z.read(ROOT282+'source/REI_F4_LI1S_RADIATIVE_PHOTON_20261030_FULL.zip')
        if sha(pr278)!=SHA_PR278 or sha(pr280)!=SHA_PR280:raise ValueError('NESTED_SOURCE_SHA')
        with zipfile.ZipFile(io.BytesIO(pr278)) as z:unpack_safe(z,base/'pr278')
        with zipfile.ZipFile(io.BytesIO(pr280)) as z:unpack_safe(z,base/'pr280')
        pr278p=base/'pr278';pr280p=base/'pr280'/ROOT280
        if sha((pr278p/'trajectory.npz').read_bytes())!=SHA_TRAJECTORY:raise ValueError('TRAJECTORY_SHA')
        spec=importlib.util.spec_from_file_location('two_e1_owner_native',pr278p/'code/native_full_rate.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        mod.source_manifest_check();net=mod.new_native_network()
        with np.load(pr278p/'trajectory.npz',allow_pickle=False) as n:
            data={k:n[k].copy() for k in ('z','x','Y','diagnostics','diagnostic_names')}
        with (base/'pr282'/ROOT282/'results/M1_ABSORPTION_EPOCH_193.csv').open(newline='') as f:
            m1_prev=list(csv.DictReader(f))
        with (pr280p/'results/LI1S_PHOTON_CAPACITY_EPOCH_193.csv').open(newline='') as f:
            epochs=list(csv.DictReader(f))
        with (pr280p/'results/LI1S_VACUUM_PHOTON_CAPACITY_8492.csv').open(newline='') as f:
            bins=list(csv.DictReader(f))
        if len(epochs)!=193 or len(bins)!=8492 or data['Y'].shape!=(193,21):raise ValueError('SOURCE_SHAPE')
        assert len(net.names)==21
        names=list(data['diagnostic_names'])
        H=data['diagnostics'][:,names.index('H')];nb=data['diagnostics'][:,names.index('nb_m3')]
        if (np.array([float(row['H_s']) for row in epochs])-H).__abs__().max()>1.e-26:raise ValueError('CLOCK_MISMATCH')
        # Static native source-level parity with independent sibling PR282.
        sigm,_=net.photo_cross_sections([E_TRIPLET_EV])
        frozen_m1=(nb[:,None]*data['Y']*sigm[:,0][None,:]).sum(axis=1)
        m1_original=np.array([float(row['kappa_abs_m_inv']) for row in m1_prev])
        if not np.allclose(frozen_m1,m1_original,rtol=4e-14,atol=1.e-70):
            raise ValueError('PR282_NATIVE_OPACITY_REGRESSION')
        # Distinct original bin aggregation must equal 193 archive native K rates.
        aggregated=np.bincount([int(row['epoch']) for row in bins],
           weights=[float(row['native_K_events_per_baryon_s']) for row in bins],minlength=193)
        original=np.array([float(row['K_events_per_baryon_s']) for row in epochs])
        if not np.allclose(aggregated,original,rtol=6e-14,atol=1e-70):
            raise ValueError('PR280_NATIVE_PHOTO_EVENT_AGGREGATION')
        return data,H.copy(),nb.copy(),epochs,bins,net

def nodes_weights(order=8, native_thresholds=()):
    if order<2:raise ValueError('GAUSS_ORDER')
    # Divide at exact tabular nodes and all native H/He/Li thresholds, so the
    # channel-opening discontinuities never lie inside quadrature panels.
    cuts=list(Y_TAB)
    for chi in list(THRESH.values())+list(native_thresholds):
        for y in (chi/E_SINGLET_EV,1-chi/E_SINGLET_EV):
            if 0<y<.5:cuts.append(y)
    cuts=np.array(sorted(set(cuts)))
    g,w=leggauss(order)
    pts=[];wg=[]
    for left,right in zip(cuts[:-1],cuts[1:]):
        pts.extend(left+.5*(right-left)*(g+1))
        wg.extend(.5*(right-left)*w)
    pts=np.array(pts);wg=np.array(wg)
    a=np.interp(pts,Y_TAB,A_TAB)
    spectral_mass=wg*a/PAIR_NORM
    if abs(spectral_mass.sum()-1)>4.e-14:raise AssertionError('SPECTRAL_NORMALIZATION')
    return pts,spectral_mass

def tail(y):
    """Exact piecewise-linear Li II 1969 shape survival P(Y>y)."""
    if y<=0:return 1.
    if y>=.5:return 0.
    i=int(np.searchsorted(Y_TAB,y,side='right')-1)
    t0=Y_TAB[i];f0=A_TAB[i];f1=A_TAB[i+1];dy=y-t0
    partial=f0*dy+(f1-f0)*dy*dy/(2*(Y_TAB[i+1]-t0))
    total=np.sum(.5*(A_TAB[i+1:-1]+A_TAB[i+2:]) * np.diff(Y_TAB)[i+1:]) if i<19 else 0.
    # area from y to next tab node plus all downstream bins
    first=.5*(A_TAB[i]+A_TAB[i+1])*(Y_TAB[i+1]-Y_TAB[i]) - partial
    return float((first+total)/PAIR_NORM)

def expected_photons_over_threshold(chi):
    if chi>=E_SINGLET_EV:return 0.
    if chi<=0:return 2.
    if chi < E_SINGLET_EV/2: return 1 + tail(chi/E_SINGLET_EV)
    return 1 - tail(1 - chi/E_SINGLET_EV) if chi>E_SINGLET_EV/2 else 1.


def frozen_transfer(data,H,nb,net,order):
    yp,weights=nodes_weights(order,net.transition_energy_eV)
    elow=yp*E_SINGLET_EV;ehigh=(1-yp)*E_SINGLET_EV
    photon_E=np.concatenate((elow,ehigh))
    sigma,_=net.photo_cross_sections(photon_E)
    if np.any(sigma<0):raise ValueError('NEGATIVE_SIGMA')
    Y=data['Y'];ks=(nb[:,None,None]*Y[:,:,None])*sigma[None,:,:]
    kappa=ks.sum(axis=1)
    if np.any(kappa<0) or np.any(H<=0):raise ValueError('FROZEN_NATIVE_DOMAIN')
    tau=kappa*C/H[:,None]
    pabs=-np.expm1(-tau)
    k_safe=np.where(kappa>0,kappa,1.)
    pcats={g:np.where(kappa>0,ks[:,list(ids),:].sum(axis=1)/k_safe,0.)*pabs
           for g,ids in CAT_GROUPS.items()}
    if not np.allclose(sum(pcats.values()),pabs,atol=1e-16,rtol=4e-14):raise ValueError('NATIVE_OPACITY_PARTITION')
    threshold=net.transition_energy_eV
    Ee=np.maximum(0.,photon_E[None,:]-threshold[:,None])
    primary=np.sum(ks*Ee[None,:,:],axis=1)/k_safe*pabs
    binding=np.sum(ks*threshold[None,:,None],axis=1)/k_safe*pabs
    absorbed_total=primary+binding
    energy_esc=(1-pabs)*photon_E[None,:]
    if np.max(np.abs(absorbed_total+energy_esc-photon_E[None,:]))>3e-13:
        raise AssertionError('PHOTO_ENERGY_CONSERVATION')
    n=len(yp)
    result={}
    for q,v in [('potential_ionizations',pabs),('potential_photoelectron_eV',primary),
                ('potential_bound_ionization_eV',binding),('escaped_photon_eV',energy_esc),
                ('absorbed_photon_eV',absorbed_total)]:
        result[q]=np.sum((v[:,:n]+v[:,n:])*weights[None,:],axis=1)
    for g,v in pcats.items():result[f'first_absorber_{g}']=np.sum((v[:,:n]+v[:,n:])*weights[None,:],axis=1)
    # Mean free paths/opacities remain energy resolved, never integrated as optical depth.
    return result,dict(y=yp,weight=weights,energies_eV=photon_E,
        kappa_m_inv=kappa,pabs_one_frozen_Hubble_length=pabs,
        first_absorber=pcats,mean_primary_eV=primary)

def simpson_time(y,x,h):
    from scipy.integrate import cumulative_simpson
    return float(cumulative_simpson(np.asarray(y)/h,x=x,initial=0)[-1])

def generate(order=8,source_bins=True):
    data,H,nb,epoch_rows,bin_rows,net=load_original()
    x=data['x'];z=data['z']
    rates=np.array([float(r['K_events_per_baryon_s']) for r in epoch_rows])
    forced=np.array([float(r['triplet_forced_events_per_baryon_s']) for r in epoch_rows])
    allowed=rates-forced
    if np.any(allowed<-1e-40):raise ValueError('NEGATIVE_ALLOWED_BRANCH')
    allowed=np.maximum(allowed,0.)
    pcount={g:expected_photons_over_threshold(chi) for g,chi in THRESH.items()}
    # Table II source-bound 2E1 spectrum reduces interval no-knowledge envelopes,
    # conditional on 100% vacuum relaxation (not on spin/escape):
    coeff={g:{'min_per_all_source_event':min(1.,v),'max_per_all_source_event':max(1.,v)} for g,v in pcount.items()}
    transfer,samples=frozen_transfer(data,H,nb,net,order)
    result_epoch=[]
    for i in range(193):
        row=dict(epoch=i,z=float(z[i]),x=float(x[i]),H_s=float(H[i]),n_b_m3=float(nb[i]),
                 Li1s_original_K_events_per_baryon_s=float(rates[i]),
                 forced_M1_events_per_baryon_s=float(forced[i]),
                 possible_2E1_events_per_baryon_s=float(allowed[i]),
                 conditional_all_singlet_2E1_photons_per_baryon_s=float(2*allowed[i]),
                 conditional_all_singlet_2E1_radiative_energy_eV_per_baryon_s=float(allowed[i]*E_SINGLET_EV),
                 conditional_all_singlet_2E1_potential_first_absorptions_per_baryon_s=float(allowed[i]*transfer['potential_ionizations'][i]),
                 conditional_all_singlet_2E1_primary_electrons_eV_per_baryon_s=float(allowed[i]*transfer['potential_photoelectron_eV'][i]),
                 conditional_all_singlet_2E1_ion_binding_eV_per_baryon_s=float(allowed[i]*transfer['potential_bound_ionization_eV'][i]),
                 conditional_all_singlet_2E1_unabsorbed_photon_eV_per_baryon_s=float(allowed[i]*transfer['escaped_photon_eV'][i]),
                 scoped_DAG='33/88_working|28/88_central|4/7_F4')
        for g,c in pcount.items():
            a,b=sorted((1.,c))
            row[f'{g}_conditional_ionizing_photons_MIN_per_baryon_s']=float(forced[i]+a*allowed[i])
            row[f'{g}_conditional_ionizing_photons_MAX_per_baryon_s']=float(forced[i]+b*allowed[i])
        for g in CAT_GROUPS:
            row[f'conditional_all_singlet_2E1_absorption_{g}_per_baryon_s']=float(allowed[i]*transfer['first_absorber_'+g][i])
        result_epoch.append(row)
    # Model-consistency energy check with no heating claim
    for r in result_epoch:
        assert abs(r['conditional_all_singlet_2E1_radiative_energy_eV_per_baryon_s']-sum(
           r[q] for q in ('conditional_all_singlet_2E1_primary_electrons_eV_per_baryon_s',
                          'conditional_all_singlet_2E1_ion_binding_eV_per_baryon_s',
                          'conditional_all_singlet_2E1_unabsorbed_photon_eV_per_baryon_s'))) <= 2e-13*max(r['conditional_all_singlet_2E1_radiative_energy_eV_per_baryon_s'],1e-80)
    source_shape=[]
    for i in range(193):
        for j,y in enumerate(Y_TAB):
            a=float(A_TAB[j]);p=a/PAIR_NORM
            source_shape.append(dict(epoch=i,z=float(z[i]),y_low=float(y),
                E_low_eV=float(y*E_SINGLET_EV),E_high_eV=float((1-y)*E_SINGLET_EV),
                original_table_A_per_s_per_y=a,normalized_pair_density_per_y=p,
                conditional_all_singlet_pair_source_density_per_baryon_s_per_y=float(allowed[i]*p)))
    event_shape=[]
    if source_bins:
        for r in bin_rows:
            k=int(r['epoch']);rate=float(r['native_K_events_per_baryon_s'])
            only=r['forced_triplet_only']=='True'
            if only:
                assert not r['allowed_singlet_2E1']=='True'
            row=dict(epoch=k,isotope=r['isotope'],bin_index=int(r['bin_index']),
              photon_eV=float(r['photon_eV']),original_K_event_rate_per_baryon_s=rate,
              source_forces_M1=only,possible_singlet_2E1=not only,
              singlet_2E1_pair_source_UPPER_per_baryon_s=0. if only else rate,
              conditional_singlet_2E1_potential_first_absorptions_per_baryon_s=0. if only else rate*transfer['potential_ionizations'][k],
              actual_singlet_fraction='UNBOUND',thermal_heat_erg_per_absorber_s='UNBOUND')
            event_shape.append(row)
    total={g:{'per_2E1_event_ionizing_photons':float(pcount[g]),
              'integrated_conditional_min_photons_per_baryon':simpson_time([r[f'{g}_conditional_ionizing_photons_MIN_per_baryon_s'] for r in result_epoch],x,H),
              'integrated_conditional_max_photons_per_baryon':simpson_time([r[f'{g}_conditional_ionizing_photons_MAX_per_baryon_s'] for r in result_epoch],x,H)}
           for g in THRESH}
    transferintegrals={key:simpson_time(allowed*val,x,H) for key,val in transfer.items()}
    original_events=simpson_time(rates,x,H)
    src={'source':'Drake et al. 1969 Table II Li II, 21 published nodes',
         'doi':SOURCE_DOI,'pdf':SOURCE_SCAN,'crosscheck':SOURCE_CROSSCHECK,
         'point_count':len(Y_TAB),'table_norm_per_s':PAIR_NORM,
         'published_rate_1997_per_s':SOURCE_RATE_1997,
         'table_vs_1997_rel':(PAIR_NORM-SOURCE_RATE_1997)/SOURCE_RATE_1997,
         'interpolation':'piecewise_linear_source_table; Gauss-Legendre source-opacity quadrature on threshold-split intervals',
         'ocr_ambiguities':'V glyph interpreted as 7; compare Table II integrated rate against published 1940 s^-1; original scan visual direct readback blocked',
         'actual_level_energy_eV':E_SINGLET_EV}
    summary={'schema':'REI_F4_LII_2E1_1969_SOURCE_NATIVE_FROZEN_OPACITY_V1',
             'physics_scope':'Drake1969 LiII TableII spectrum + actual source-owned BASS193 photoevents and static local native opacity; all-singlet upper conditional transfer only; no IVP or actual heat',
             'source_archive_sha256':SHA_PR282,'source_owner':OWNER,'table':src,
             'data':{'epochs':len(result_epoch),'original_Li1s_source_event_rows':len(event_shape),
                     'new_source_spectral_grid_rows':len(source_shape),
                     'new_threshold_cell_equivalents':len(event_shape)*3,
                     'reused_native_states':data['Y'].shape[1],'photo_spectral_eV_range':[0.,E_SINGLET_EV],
                     'quadrature_order':order,'frozen_source_models_count':2},
             'events_per_baryon':original_events,'LiII_2E1_conditional_threshold_photons':total,
             'LiII_2E1_all_singlet_frozen_transfer_integrals_per_baryon':transferintegrals,
             'boundaries':{'actual_singlet_yields':'NOT_SOURCE_QUALIFIED',
                           'full_LiII_2E1_line_shape_between_tab_nodes':'INTERPOLATED_TABLE',
                           'cross_section_coefficients':'SOURCE_PINNED_NUMERIC_PROJECTION_NOT_RAW_JSON_SHA',
                           'cosmological_radiative_transfer':'NOT_RUN',
                           'actual_HHe_photoionization':'NOT_INFERRED',
                           'secondary_electron_energy_deposition':'NOT_RUN',
                           'REI_IgmPhotoInput_heat_erg_per_absorber_s':'UNBOUND',
                           'R6_different_author':'NOT_RUN','C9_different_author':'NOT_RUN',
                           'new_IVPs':0,'PRODUCTION':'HOLD'},
             'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7',
                    'new_scoped_auxiliary':'1/1','canonical_delta':0,'F4':'PARTIAL','L4_ready':False,
                    'NO_MORE_IVPS':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,
                    'AUTO_NEXT_NODE':False,'PRODUCTION':'HOLD'}}
    return summary,result_epoch,source_shape,event_shape,transfer,samples

def write_rows(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def run():
    out,epochs,shape,events,transfer,samples=generate()
    r=ROOT/'results';r.mkdir(exist_ok=True)
    write_rows(r/'LI_2E1_SOURCE_EPOCH_193.csv',epochs)
    write_rows(r/'LI_2E1_SOURCE_GRID_4053.csv',shape)
    write_rows(r/'LI_2E1_EVENT_8492.csv',events)
    write_rows(r/'LI_2E1_DRAKE_1969_TABLE_21.csv',[
        {'y':float(y),'A_s_inv_per_y':float(a),'probability_per_y':float(a/PAIR_NORM)}
        for y,a in zip(Y_TAB,A_TAB)])
    with (r/'RESULT.json').open('w') as f:json.dump(out,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    print(json.dumps({'source_rows':len(events),'spectral_rows':len(shape),'epochs':len(epochs),
      'LiII_table_1969_rate_s_inv':PAIR_NORM,
      'HeII_2E1_expected_count':out['LiII_2E1_conditional_threshold_photons']['He_II']['per_2E1_event_ionizing_photons'],
      'H_I_2E1_expected_count':out['LiII_2E1_conditional_threshold_photons']['H_I']['per_2E1_event_ionizing_photons']},indent=2))
    return out
if __name__=='__main__':run()
