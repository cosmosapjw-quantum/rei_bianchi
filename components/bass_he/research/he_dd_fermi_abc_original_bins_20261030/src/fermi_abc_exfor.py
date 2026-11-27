"""2015 Fermi-LAT 3-foreground-model bin data x EXFOR M0475003.

Primary output is a reported-cross-section-weighted photon flux diagnostic,
not an exclusive nuclear event rate, cosmological photon history, or heat.
Source identification is exact for a third-party Git mirror and a 6-row
verbatim subset, NOT for the inaccessible original CDS table3.dat raw bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from scipy.integrate import quad

NB_TO_CM2 = 1.e-33
C_CM_PER_S = 2.99792458e10
Q_MEV = 2*1875.61294500 - 3727.3794118
KNOTS = [201.,225.,253.,285.,320.,359.]
EXPECTED_GIT_MIRROR = '794cb6fcbef243be950613475c4254d6ab3877a4'
MODEL_PLE_IGRB = {'A':(2.32,279000.),'B':(2.28,206000.),'C':(2.26,233000.)}
COLS = ('f_igrb','basic_igrb_up','basic_igrb_down','fg_igrb_up','fg_igrb_down',
        'f_egb','basic_egb_up','basic_egb_down','fg_egb_up','fg_egb_down',
        'f_resolved','basic_resolved_up','basic_resolved_down')


@dataclass(frozen=True)
class GammaBin:
    model: str
    lo: float
    hi: float
    val: dict[str, float]


def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def load_inputs(root:Path):
    man=json.loads((root/'data/SOURCE_MANIFEST.json').read_text())
    f=(root/'data/fermi_table3_abc_6rows.txt').read_bytes()
    full=(root/'data/fermi_igrb_2015_AB_C_78row_mirror.csv').read_bytes()
    if sha256(full)!=man['78row_mirror']['sha256']:
        raise ValueError('FULL_FERMI_GIT_MIRROR_SHA256_MISMATCH')
    if hashlib.sha1(f'blob {len(full)}\0'.encode()+full).hexdigest()!=EXPECTED_GIT_MIRROR:
        raise ValueError('FULL_FERMI_GIT_MIRROR_BLOB_MISMATCH')
    all_lines=[x for x in full.decode('ascii').splitlines() if x.startswith(('A ','B ','C '))]
    if len(all_lines)!=78 or any(sum(x.startswith(m+' ') for x in all_lines)!=26 for m in ('A','B','C')):
        raise ValueError('FULL_FERMI_78_SOURCE_STRUCTURE_MISMATCH')
    six_from_full=[x for x in all_lines if x.split()[1] in ('200.0','282.8')]
    if len(six_from_full)!=6 or six_from_full!=f.decode('ascii').splitlines():
        raise ValueError('SIX_ROW_SUBSET_NOT_EXACTLY_FROM_78_MIRROR')
    s=(root/'data/exfor_M0475_SIG6.json').read_bytes()
    assert man['78row_mirror']['git_blob']==EXPECTED_GIT_MIRROR
    if sha256(f)!=man['local_six_rows']['sha256']:
        raise ValueError('FERMI_MIRROR_SIX_ROWS_SHA256_MISMATCH')
    if sha256(s)!=man['exfor_six_rows']['sha256']:
        raise ValueError('EXFOR_SIG6_TRANSCRIPTION_SHA256_MISMATCH')
    bins=[]
    for line in six_from_full:
        if not line.strip(): continue
        z=line.split()
        if len(z)!=16 or z[0] not in MODEL_PLE_IGRB:
            raise ValueError('FERMI_SCHEMA_16_COLUMNS_VIOLATION')
        m,lo,hi=z[0],float(z[1]),float(z[2]); vals=list(map(float,z[3:]))
        if not(all(math.isfinite(x) and x>=0 for x in vals)):
            raise ValueError('FERMI_NEGATIVE_OR_NONFINITE_COLUMN')
        v=dict(zip(COLS,vals,strict=True))
        # Preserve published independently reported channels. The printed resolved-source
        # column can disagree with direct EGB-IGRB subtraction for B by several percent.
        # Diagnose; never silently replace measured table values to force equality.
        bins.append(GammaBin(m,lo,hi,v))
    if [(b.model,b.lo,b.hi) for b in bins]!=[
            (m,a,b) for m in ('A','B','C') for a,b in ((200.,282.8),(282.8,400.))]:
        raise ValueError('FERMI_ORIGINAL_ENERGY_BIN_SEMANTICS_CHANGED')
    if len(bins)!=6 or man['78row_mirror']['nrecords']!=78:
        raise ValueError('SOURCE_RECORD_COUNT_MISMATCH')
    if any(b.lo<0 or b.hi<=b.lo for b in bins):
        raise ValueError('BAD_ENERGY_BOUNDS')
    ex=json.loads(s)
    if ex['raw_source_git_blob']!='c49433293921dbb012d7f1b0387745732a598efa':
        raise ValueError('EXFOR_ORIGINAL_SOURCE_SHA_NOT_MATCHED')
    if [float(z[0]) for z in ex['rows']]!=KNOTS or any(len(z)!=3 for z in ex['rows']):
        raise ValueError('SIG_MEASURED_COORDINATES_CHANGED')
    sig=[float(z[1]) for z in ex['rows']]
    err=[float(z[2]) for z in ex['rows']]
    return bins,sig,err,man


def basis(E:float)->list[float]:
    if not KNOTS[0]<=E<=KNOTS[-1]:
        raise ValueError('NO_SIG_EXTRAPOLATION')
    result=[0.]*len(KNOTS)
    for k in range(len(KNOTS)-1):
        l,h=KNOTS[k],KNOTS[k+1]
        if l<=E<=h:
            t=(E-l)/(h-l)
            result[k],result[k+1]=1.-t,t
            return result
    raise AssertionError('EXFOR_INTERVAL_MISSING')


def g(E:float,model:str,shape:str):
    if shape=='flat': return 1.
    if shape=='model_ple_igrb':
        slope,cutoff=MODEL_PLE_IGRB[model]
        return (E/100.)**(-slope)*math.exp(-E/cutoff)
    raise ValueError('UNSUPPORTED_SPECTRAL_MODEL')


def integrate(f,a,b):
    if a>=b: return 0.
    edges=[a]+[x for x in KNOTS if a<x<b]+[b]
    return sum(quad(f,x,y,epsabs=1e-12,epsrel=1e-11)[0] for x,y in zip(edges,edges[1:]))


def kernel_one_bin(b:GammaBin,shape:str):
    a,h=max(b.lo,KNOTS[0]),min(b.hi,KNOTS[-1])
    den=integrate(lambda E:g(E,b.model,shape),b.lo,b.hi)
    if den<=0: raise ValueError('INVALID_SPECTRAL_WEIGHT')
    weights=[integrate(lambda E,j=j:g(E,b.model,shape)*basis(E)[j],a,h)/den
             for j in range(len(KNOTS))]
    weights_K=[integrate(lambda E,j=j:g(E,b.model,shape)*basis(E)[j]*(E-Q_MEV),a,h)/den
               for j in range(len(KNOTS))]
    covered=integrate(lambda E:g(E,b.model,shape),a,h)/den
    assert all(x>=-1.e-14 for x in weights)
    assert abs(sum(weights)-covered)<1.e-11
    return weights,weights_K,covered


def error_vector(coeffs:list[float], errs:list[float]):
    terms=[abs(x*y) for x,y in zip(coeffs,errs,strict=True)]
    s=sum(terms)
    return dict(independent_conditional=math.sqrt(sum(v*v for v in terms)),
                unknown_corr_sd_lower=max(0.,2*max(terms)-s),
                unknown_corr_sd_upper=s)


def compute(root:Path):
    bins,sig,err,man=load_inputs(root)
    out={'schema':'BASS_HE_FERMI_2015_ABC_BIN_EXFOR_REPORTING_DIAGNOSTIC_V1',
         'source_identity':man,'units':{'rate':'s^-1 per 4He target reported-like',
         'born_K':'MeV s^-1 per 4He target reported-like',
         'flux':'photons cm^-2 s^-1 sr^-1 integrated over measured energy bin',
         'gamma_density':'cm^-3, only if locally isotropic'},
         'energy_support_MeV':[201,359],
         'Fermi_models':'correlated foreground scenario choices, not independent replicated experiments',
         'source_table_EGB_minus_IGRB_plus_reported_resolved':[{
             'model':b.model,'energy_bin_MeV':[b.lo,b.hi],
             'absolute_flux_residual':b.val['f_egb']-b.val['f_igrb']-b.val['f_resolved'],
             'relative_to_fEGB':(b.val['f_egb']-b.val['f_igrb']-b.val['f_resolved'])/b.val['f_egb']} for b in bins],
         'results':[],'kappa':None,'R_event':None,'heat_rate':None,
         'D_fast_stopping':None,'physical_activation':False,'L4':False,'production':'HOLD'}
    pref=4*math.pi*NB_TO_CM2
    for model in ('A','B','C'):
        subset=[b for b in bins if b.model==model]
        for shape in ('flat','model_ple_igrb'):
            all_weights=[kernel_one_bin(b,shape) for b in subset]
            for component in ('igrb','egb'):
                total=[0.]*len(KNOTS);kin=[0.]*len(KNOTS)
                per_bin=[];bin_basic_up=[];bin_basic_down=[]
                fg_up=0.;fg_down=0.;density=0.
                for b,(w,wK,covered) in zip(subset,all_weights,strict=True):
                    flux=b.val['f_'+component]
                    coeff=pref*sum(w[j]*sig[j] for j in range(len(KNOTS)))
                    for j in range(len(KNOTS)):
                        total[j]+=flux*pref*w[j]
                        kin[j]+=flux*pref*wK[j]
                    density+=4*math.pi*flux/C_CM_PER_S
                    bin_basic_up.append(b.val['basic_'+component+'_up']*coeff)
                    bin_basic_down.append(b.val['basic_'+component+'_down']*coeff)
                    fg_up+=b.val['fg_'+component+'_up']*coeff
                    fg_down+=b.val['fg_'+component+'_down']*coeff
                    per_bin.append({'Fermi_bin_MeV':[b.lo,b.hi],
                       'EXFOR_overlap_MeV':[max(b.lo,201.),min(b.hi,359.)],
                       'published_integrated_flux':flux,
                       'flux_relative_under_SIG_support_modeled':covered,
                       'nuclear_basis_weights_nb_per_unit':w,
                       'reported_rate_like_s_minus1_per_He':coeff*flux,
                       'source_BASIC_up':b.val['basic_'+component+'_up'],
                       'source_BASIC_down':b.val['basic_'+component+'_down'],
                       'source_FG_up':b.val['fg_'+component+'_up'],
                       'source_FG_down':b.val['fg_'+component+'_down']})
                scalar=sum(a*b for a,b in zip(total,sig,strict=True))
                Kval=sum(a*b for a,b in zip(kin,sig,strict=True))
                if not scalar>0 or not Kval>0:raise ValueError('NONPOSITIVE_SOURCE_DIAGNOSTIC')
                bup=error_vector([1,1],bin_basic_up)
                bdown=error_vector([1,1],bin_basic_down)
                exerr=error_vector(total,err)
                out['results'].append({'foreground_model':model,'component':component,
                    'within_bin_model':shape,
                    'shape_is_published_IGRB_global_fit':shape=='model_ple_igrb',
                    'EGB_use_of_IGRB_shape_is_extra_hypothesis':component=='egb' and shape!='flat',
                    'Gamma_reported_like_s_minus1_per_He':scalar,
                    'K_born_reported_like_MeV_s_minus1_per_He':Kval,
                    'observed_full_two_bin_number_density_if_isotropic_cm_minus3':density,
                    'nuclear_positive_coefficients_s_minus1_per_He_per_nb':total,
                    'EXFOR_pointwise_stat_error_propagation':exerr,
                    'Fermi_BASIC_stat_plus_instrument_up':bup,
                    'Fermi_BASIC_stat_plus_instrument_down':bdown,
                    'Fermi_FG_model_up_shift':fg_up,
                    'Fermi_FG_model_down_shift':fg_down,
                    'has_source_owned_nuclear_cross_covariance':False,
                    'has_source_owned_Fermi_cross_covariance':False,
                    'has_source_owned_spectral_shape_uncertainty':False,
                    'per_bin':per_bin})
    return out


def report_csv(res:dict,path:Path):
    fields=['foreground_model','component','within_bin_model',
            'Gamma_reported_like_s_minus1_per_He','K_born_reported_like_MeV_s_minus1_per_He',
            'observed_full_two_bin_number_density_if_isotropic_cm_minus3',
            'Fermi_FG_model_up_shift','Fermi_FG_model_down_shift']
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for x in res['results']:w.writerow({k:x[k] for k in fields})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    res=compute(args.root)
    (args.out/'FERMI_ABC_EXFOR_PHYSICAL_DIAGNOSTICS.json').write_text(json.dumps(res,indent=2)+'\n')
    report_csv(res,args.out/'FERMI_ABC_EXFOR_PHYSICAL_DIAGNOSTICS.csv')
    for x in res['results']:
        print(x['foreground_model'],x['component'],x['within_bin_model'],f"{x['Gamma_reported_like_s_minus1_per_He']:.12e}")

if __name__=='__main__':main()
