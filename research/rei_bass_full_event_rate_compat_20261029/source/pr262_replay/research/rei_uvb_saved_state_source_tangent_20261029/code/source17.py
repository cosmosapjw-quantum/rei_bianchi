"""Frozen-state H/D/T, He3/He4 photoionization source Jacobians.

Conditional REI PR261 Puchwein six-moment common-scale model, evaluated on
saved ON_refined PR248 state snapshots. This is NOT a trajectory derivative,
full chemistry Jacobian, native BASS reduced30 transport or tau derivative.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np

UNIT = Path(__file__).resolve().parents[1]
PARENT = UNIT.parent / 'rei_uvb_six_moment_response_20261029'
SAVED = UNIT / 'source/ON_REFINED_7_SAVED_ROWS.json'
SAVED_SHA = '7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77'
SOURCE_REI_MODEL_GIT_BLOB = '1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc'
SOURCE_SAVED_CSV_GIT_BLOB = '189c2d903e25c18bee49e0ab6add3ba1d1805e93'
SOURCE_SAVED_NUMERIC_FNV1A64 = '174743cb945f8bfe'
LABELS = ('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2',
          'He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
A = np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7],dtype=float)
Q = np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3],dtype=float)
# Exact REI external-source model.py: FAMILIES and photo_atom_{family}_{q}.
# HI isotope equality (H1/D/T) and HeI/HeII isotope equality (He3/He4)
# are the explicit old model's approximate threshold convention.
EVENTS = (
    ('H1_0','H1_1',0,13.6),
    ('D_0','D_1',0,13.6),
    ('T_0','T_1',0,13.6),
    ('He3_0','He3_1',1,24.6),
    ('He3_1','He3_2',2,54.4),
    ('He4_0','He4_1',1,24.6),
    ('He4_1','He4_2',2,54.4),
)
SRC = np.array([LABELS.index(x[0]) for x in EVENTS],dtype=int)
DST = np.array([LABELS.index(x[1]) for x in EVENTS],dtype=int)
RATE_ID = np.array([x[2] for x in EVENTS],dtype=int)
THRESHOLD = np.array([x[3] for x in EVENTS],dtype=float)
STOICH = np.zeros((17,len(EVENTS)),float)
for j,(i,k) in enumerate(zip(SRC,DST)):
    STOICH[i,j]=-1.; STOICH[k,j]=1.


def load_parent():
    path=PARENT/'code/source_response.py'
    spec=importlib.util.spec_from_file_location('pinned_pr261_source_response',path)
    if spec is None or spec.loader is None: raise ValueError('PARENT_SOURCE_MISSING')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    d,p,rows=module.load()
    return module,d,p,rows,module.geometry(d)


def saved_rows():
    if hashlib.sha256(SAVED.read_bytes()).hexdigest()!=SAVED_SHA:
        raise ValueError('SELECTED_SAVED_STATE_SHA_MISMATCH')
    obj=json.loads(SAVED.read_text())
    if obj['original_git_blob']!=SOURCE_SAVED_CSV_GIT_BLOB or tuple(obj['labels'])!=LABELS:
        raise ValueError('SAVED_STATE_SOURCE_BINDING_MISMATCH')
    if len(obj['rows'])!=7:raise ValueError('EXPECTED_SEVEN_SAVED_EPOCHS')
    last=-math.inf
    for r in obj['rows']:
        z=float(r['z']); y=np.array(r['y'],float)
        if not (2.4<=z<=4.75) or z<=last or y.shape!=(17,) or not np.isfinite(y).all() or np.any(y<0):
            raise ValueError('SAVED_STATE_DOMAIN_OR_SCHEMA')
        last=z
    canonical='\n'.join('|'.join(f'{v:.16e}' for v in [r['z'],r['elapsed_proper_s'],*r['y']]) for r in obj['rows'])+'\n'
    h=0xcbf29ce484222325
    for b in canonical.encode('ascii'):
        h=((h^b)*0x100000001b3)&((1<<64)-1)
    if f'{h:016x}'!=SOURCE_SAVED_NUMERIC_FNV1A64:
        raise ValueError('SOURCE_SAVED_NUMERIC_PROJECTION_MISMATCH')
    return obj['rows']


def source17(z,y,a,rows,port):
    """Photo-only F17, dF/dy, dF/dR6, dF/d(beta,kappa), electron and energy.

    y is 17 physical populations / Href, frozen while differentiating a.
    F is per Href/s. The P19 heating moments are eV per target/s and remain
    a separate energy port, NOT silently booked to the old pilot fast pool.
    """
    y=np.asarray(y,float);a=np.asarray(a,float)
    if y.shape!=(17,) or not np.isfinite(y).all() or np.any(y<0):raise ValueError('INVALID_Y17')
    response=port.rate_response(float(z),a,rows)
    moments=response['moments'];moments_jac=response['jac']
    rate=moments[2*RATE_ID]
    heating=moments[2*RATE_ID+1]
    event_rate=y[SRC]*rate
    F=STOICH@event_rate
    J_y=np.zeros((17,17),float)
    J_R=np.zeros((17,6),float)
    for k in range(len(EVENTS)):
        i=SRC[k];j=DST[k];m=2*RATE_ID[k]
        J_y[i,i]-=rate[k];J_y[j,i]+=rate[k]
        J_R[i,m]-=y[i];J_R[j,m]+=y[i]
    B=J_R@moments_jac
    electron=float(Q@F)
    electron_jac=Q@B
    photoheat=float(y[SRC]@heating)
    photoheat_jac=np.sum(y[SRC,None]*moments_jac[2*RATE_ID+1],axis=0)
    ionstorage=float(THRESHOLD@event_rate)
    ionstorage_jac=THRESHOLD@(y[SRC,None]*moments_jac[2*RATE_ID])
    absorbed=ionstorage+photoheat
    if not np.isfinite(F).all() or not np.isfinite(B).all():raise ArithmeticError('NONFINITE_SOURCE')
    return dict(z=float(z),F=F,J_y=J_y,J_R=J_R,B=B,events=event_rate,
                electron_rate_per_Href_s=electron,electron_jac=electron_jac,
                photoheat_eV_per_Href_s=photoheat,photoheat_jac=photoheat_jac,
                ionization_storage_eV_per_Href_s=ionstorage,ionization_storage_jac=ionstorage_jac,
                absorbed_photon_eV_per_Href_s=absorbed,
                rate_moments=moments,photo_source_only=True,physical_trajectory_derivative=False)


def source_envelopes(z,y,rows,port,geo):
    """Sharp pointwise nuisance-union bounds at fixed y for positive source observables."""
    y=np.asarray(y,float)
    p=port.p19_moments(float(z),rows)
    g_e=float(np.sum(y[SRC]*p[2*RATE_ID]))
    g_h=float(np.sum(y[SRC]*p[2*RATE_ID+1]))
    out={}
    for label,q in [('deterministic',0.),('joint2_95',port.Q_JOINT2_95)]:
        lo,hi=port.logfactor_support(float(z),q,geo)
        out[label]={'electron_per_Href_s':[g_e*10.**lo,g_e*10.**hi],
                    'photoheat_eV_per_Href_s':[g_h*10.**lo,g_h*10.**hi],
                    'logfactor_dex':[lo,hi]}
    return out


def structural_check():
    """Exact integer stoichiometric identities, before floating calculations."""
    if not np.array_equal(A@STOICH,np.zeros(len(EVENTS))):raise AssertionError('BARYON_NOT_CONSERVED')
    if not np.array_equal(Q@STOICH,np.ones(len(EVENTS))):raise AssertionError('ELECTRON_EVENT_MISMATCH')
    if not np.array_equal(np.ones(17)@STOICH,np.zeros(len(EVENTS))):raise AssertionError('NUCLEAR_NUMBER_MISMATCH')
    return True


def run_saved():
    structural_check()
    port,d,p,rows,geo=load_parent()
    results=[];Bstack=[]
    for rec in saved_rows():
        z=rec['z'];y=np.array(rec['y'],float)
        out=source17(z,y,geo['a0'],rows,port)
        Bstack.append(out['B'])
        # mu_1(J_y)=max_j(J_jj+sum_{i!=j}|J_ij|)=0 for Metzler column-conservative generator.
        mu1=np.max(np.diag(out['J_y'])+np.sum(np.abs(out['J_y']),axis=0)-np.abs(np.diag(out['J_y'])))
        results.append({
            'target_z':rec['target_z'],'saved_z':z,'elapsed_proper_s':rec['elapsed_proper_s'],
            'electron_creation_per_Href_s':out['electron_rate_per_Href_s'],
            'd_electron_creation_d_beta':float(out['electron_jac'][0]),
            'd_electron_creation_d_kappa':float(out['electron_jac'][1]),
            'photoheat_eV_per_Href_s':out['photoheat_eV_per_Href_s'],
            'ionization_storage_eV_per_Href_s':out['ionization_storage_eV_per_Href_s'],
            'absorbed_photon_eV_per_Href_s':out['absorbed_photon_eV_per_Href_s'],
            'mu1_photo_only_per_s':float(mu1),
            'baryon_source_max_abs':float(np.max(np.abs(A@out['B']))),
            'charge_source_max_abs':float(np.max(np.abs(Q@out['B']-out['electron_jac']))),
            'rank1_frobenius_residual':float(np.linalg.norm(out['B']-np.outer(out['F'],port.L10*port.tvec(z)))),
            'envelopes':source_envelopes(z,y,rows,port,geo)
        })
    stacked=np.concatenate(Bstack,axis=0)
    sv=np.linalg.svd(stacked,compute_uv=False)
    return {'schema':'REI_17_FROZEN_SOURCE_TANGENT_RESULT_V1',
            'parent_PR261':'8a3107a6477a648ad87a4db2a52240c1bea4cc42',
            'original_model_blob':SOURCE_REI_MODEL_GIT_BLOB,
            'original_saved_csv_blob':SOURCE_SAVED_CSV_GIT_BLOB,
            'selected_saved_rows_sha256':SAVED_SHA,
            'source_scopes':['ON_refined saved 17-state frozen, not solution of new P19 UVB',
                             'P19 six moments scaled by common beta/kappa, isotope equality old source',
                             'only seven photoionization transitions; Li and nuclear/CR sources unmodified'],
            'nominal_a0_beta_kappa':geo['a0'].tolist(),
            'stacked_119x2_singular_values':sv.tolist(),
            'stacked_rank_criterion':'rank2 if at least two nonzero source blocks at distinct saved redshifts',
            'entries':results,
            'actual_Da_ne':'NOT_COMPUTED',
            'actual_Da_H':'NOT_COMPUTED',
            'physical_tau_tangent':'NOT_COMPUTED',
            'new_ivp_count':0}


if __name__=='__main__':
    print(json.dumps(run_saved(),indent=2))
