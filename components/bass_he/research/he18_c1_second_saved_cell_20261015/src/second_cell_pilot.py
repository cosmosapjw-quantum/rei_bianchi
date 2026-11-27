#!/usr/bin/env python3
"""HE18 C1: pinned warm P01 second-saved-cell execution baseline (exploratory).

This evaluates the actual archived R4 warm FT03/HM12 RHS on a NEW second-cell
piecewise-linear and cubic Hermite reconstruction. It does not integrate a new
scientific IVP or certify whole-cell error, provider roundoff or foreground.
No changes to active rei_bianchi/Codex checkout or source numerics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from warm_source_reference import Source, Hval, PLval, L, EV, KB, FF, C

ROOT=Path(__file__).resolve().parents[1]
PINS={
    'P01_STATE.npz':'3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be',
    'emissivity.out':'88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
    'ENDPOINT_MEMORY_R7.json':'aaca8a993a951894bda57cdf29ac7f0fffb8d78e092c87f8356176fe451a9a39',
}

def q(v):
    if isinstance(v,(np.longdouble,float,np.float64)):
        return Q(*float(v).as_integer_ratio())
    return Q(v)

def identity_and_incoming():
    for f,digest in PINS.items():
        content=(ROOT/'inputs'/f).read_bytes()
        if hashlib.sha256(content).hexdigest()!=digest:
            raise ValueError('SOURCE_IDENTITY_MISMATCH:'+f)
    obj=json.loads((ROOT/'inputs/ENDPOINT_MEMORY_R7.json').read_text())
    errors=[Q(x) for x in obj['photon_error_end_raw_exact']]
    gas=[Q(x) for x in obj['gas_error_end_scaled']]
    if obj['source_interval_s']!=['0','6250000000'] or len(errors)!=2904 or len(gas)!=4:
        raise ValueError('INCOMING_SCOPE_OR_VECTOR_SHAPE_INVALID')
    if any(x<0 for x in errors+gas) or obj['next_cell_majorants'] is not None:
        raise ValueError('INCOMING_SIGN_OR_NEXT_CELL_CERTIFICATE_INVALID')
    return obj,errors,gas

def source_probe(cell=1, points=(0., .125, .25, .5, .75, .875, 1.)):
    obj,photon_errors,gas_errors=identity_and_incoming()
    src=Source()
    if cell!=1:raise ValueError('ONLY_NEXT_SAVED_CELL_IS_SELECTED')
    start,end=src.times[cell],src.times[cell+1]
    h=end-start
    if start!=L(6250000000) or end!=L(12500000000):
        raise ValueError('TIME_IDENTITY_MISMATCH')
    left,right=src.y[:,cell].copy(),src.y[:,cell+1].copy()
    m0,info0=src.rhs(start,left)
    m1,info1=src.rhs(end,right)
    # Fixed numerical evaluation convention: float64 slopes, as archived HE17 R4.
    slopes=[v.astype(np.float64).astype(L) for v in (m0,m1)]
    ref0,ref1=slopes
    sc=np.array([1,1,1,32],dtype=L)
    norm_phot=float(np.sum(left[4:],dtype=L))
    rows=[]
    for z0 in points:
        t=start+h*L(z0)
        if not (start<=t<=end):raise ValueError('TIMING_INTERPOLATION')
        for label in ('PL','HERMITE'):
            if label=='PL': y,der=PLval(left,right,h,L(z0))
            else:y,der=Hval(left,right,ref0,ref1,h,L(z0))
            exact,details=src.rhs(t,y)
            res=der-exact
            rows.append(dict(kind=label,u=float(z0),time_s=float(t),
                     max_scaled_gas_residual_s_inv=float(np.max(np.abs(res[:4])/sc)),
                     photon_L1_residual_per_initial_stock_s_inv=float(np.sum(np.abs(res[4:]),dtype=L)/norm_phot),
                     Tgas_K=float(details['T']),
                     min_photon_population=float(np.min(y[4:])),
                     gas_values=list(map(float,y[:4]))))
    # A whole-cell positivity certificate for the FIXED polynomial using exact
    # dyadic Bernstein control points. This proves positivity only, not residual.
    hh=q(h)
    b0=[q(a) for a in left];b1=[q(left[i])+hh*q(ref0[i])/3 for i in range(len(left))]
    b2=[q(right[i])-hh*q(ref1[i])/3 for i in range(len(left))];b3=[q(a) for a in right]
    controls=(b0,b1,b2,b3)
    photon_nonnegative=all(min(ctrl[i] for ctrl in controls)>=0 for i in range(4,len(left)))
    simplex=all(0<=c[0]<=1 and 0<=c[1] and 0<=c[2] and c[1]+c[2]<=1 for c in controls)
    ctemp=2*Q('1.602176634e-19')/(3*Q('1.380649e-23'));ff=Q(3,38)
    temp_domain=all(Q(30000)*(1+ff+c[0]+ff*(c[1]+2*c[2]))<=ctemp*c[3]<=Q(110000)*(1+ff+c[0]+ff*(c[1]+2*c[2])) for c in controls)
    # Source C is in cm/s and nH in cm^-3; output cm^-2 ×1e4 -> m^-2.
    # Hermite gas column is *one* reconstructive diagnostic, not the original IVP.
    def column_gauss(n):
        nd,wd=np.polynomial.legendre.leggauss(n)
        nd=(nd.astype(L)+1)/2;wd=wd.astype(L)/2
        accum=L(0)
        for zz,ww in zip(nd,wd):
            g=Hval(left[:4],right[:4],ref0[:4],ref1[:4],h,zz)[0]
            nh=src.env(start+h*zz)[0]
            chi=g[0]+FF*(g[1]+2*g[2])
            accum+=ww*nh*chi
        return C*L('1e4')*h*accum
    c12=column_gauss(12);c24=column_gauss(24)
    # Fast conditional diagnostic. No numerical quadrature error certificate.
    sigma=L('6.6524587051e-29')
    tau24=sigma*c24
    # Readonly saved-state baseline, a different reconstruction.
    nstart=src.env(start)[0]*(left[0]+FF*(left[1]+2*left[2]))
    nend=src.env(end)[0]*(right[0]+FF*(right[1]+2*right[2]))
    cPL=C*L('1e4')*h*(nstart+nend)/2
    # Incoming error is not allowed to disappear on entering new cell.
    report={
      'schema':'bass-he-he18-c1-next-saved-cell-pilot-v1',
      'scope':'HE18 second saved cell; exploratory source-matched RHS/reconstruction baseline',
      'stage':'C1','source':'warm P01 FT03/HM12 Case A; non-tilted LRS Bianchi I',
      'source_commit':'a5c958c414dea41216b445c05f58df837f05cacb',
      'input_hashes':PINS,'cell_s':[str(int(start)),str(int(end))],
      'initial_4gas':[float(v) for v in left[:4]],
      'final_4gas':[float(v) for v in right[:4]],
      'slopes_binary64_SHA256':hashlib.sha256(np.r_[ref0.astype(float),ref1.astype(float)].tobytes()).hexdigest(),
      'endpoint_temperature_K':[float(info0['T']),float(info1['T'])],
      'data':rows,
      'gas_residual_max_by_reconstruction':{label:max(r['max_scaled_gas_residual_s_inv'] for r in rows if r['kind']==label) for label in ('PL','HERMITE')},
      'photon_residual_max_by_reconstruction':{label:max(r['photon_L1_residual_per_initial_stock_s_inv'] for r in rows if r['kind']==label) for label in ('PL','HERMITE')},
      'Bernstein_exact_control_points':{'photon_nonnegative':photon_nonnegative,'gas_simplex':simplex,'warm_temperature_interval':temp_domain},
      'column_center_recon':{'Hermite_GL12_m2':str(c12),'Hermite_GL24_m2':str(c24),
            'rule_difference_m2':str(abs(c24-c12)),
            'old_stored_proper_ne_PL_m2':str(cPL),
            'reconstruction_bias_m2':str(c24-cPL),
            'Hermite_GL24_tau':str(tau24)},
      'incoming_first_cell':{'gas_error_scaled_exact':[str(v) for v in gas_errors],
           'photon_error_count':len(photon_errors),
           'photon_error_sha256':PINS['ENDPOINT_MEMORY_R7.json'],
           'positive_photon_error_components':sum(x>0 for x in photon_errors),
           'zero_incoming_error_assumed':False},
      'source_RHS_evaluations':src.rhs_calls,'old_ivp_integrations':0,
      'native_production_invocations':0,
      'whole_cell_residual_certified':False,
      'true_second_cell_tau_interval':None,
      'true_full_history_tau_interval':None,
      'true_binary64_provider_error_bound':None,
      'error_majorants_second_cell':None,
      'scientific_admission':'EXPLORATORY_ONLY',
      'next_stage':'C2'
    }
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=ROOT/'results/C1_SECOND_CELL_PILOT.json')
    a=ap.parse_args();report=source_probe()
    if a.out.exists():raise SystemExit('Output already exists, refusing overwrite')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['cell_s','endpoint_temperature_K','gas_residual_max_by_reconstruction','photon_residual_max_by_reconstruction','Bernstein_exact_control_points','source_RHS_evaluations','scientific_admission']},indent=2))
if __name__=='__main__':main()
