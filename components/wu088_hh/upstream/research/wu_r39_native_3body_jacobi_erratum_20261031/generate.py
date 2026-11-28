#!/usr/bin/env python3
"""Source-bound three-body rigid-diatom PES and isotropic centrifugal barrier atlas.
No reaction S matrix, reaction cross sections, kinetic rates, or molecular non-BO correction.
Original native h3plus.f is a private user-supplied source input, not redistributed.
"""
import argparse, ctypes, csv, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss, legval

EXPECTED_NATIVE_SHA='8dbf8b7e3852d02504ba92317f79593051d689f1357263ac0891a3a24084ed8c'
EXPECTED_R38_ARCHIVE_SHA='284cb1f0ac67b81c6088c5c1ac8dcf55d816f2e45acdc3983e2af95c49de4257'
MP=1836.152673426   # electron mass, CODATA 2022 input inherited from R38
MD=3670.482967655
EH_K=315775.024804
EH_EV=27.211386245981
ELECTRON_VOLT=1.602176634e-19
BOLTZMANN=1.380649e-23
R_VALUES=(3.0,3.5,4.0,4.5,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,14.0,
          16.0,18.0,20.0,24.0,28.0,32.0,36.0,40.0,50.0,60.0,75.0,
          90.0,110.0,130.0,160.0)
N_ANGLES=32

class PES:
    def __init__(self, lib):
        self.lib=ctypes.CDLL(str(Path(lib).resolve()))
        self.lib.h2_.argtypes=[ctypes.POINTER(ctypes.c_double)]
        self.lib.h2_.restype=ctypes.c_double
        self.lib.dimh3p_.argtypes=[ctypes.POINTER(ctypes.c_double)]*6
        self.lib.dimh3p_.restype=None
    def h2(self,r):
        z=ctypes.c_double(r)
        return self.lib.h2_(ctypes.byref(z))
    def e1(self,r_ab,r_ac,r_bc):
        sides=(r_ab,r_ac,r_bc)
        if not (all(math.isfinite(x) and x>0 for x in sides) and
                2*max(sides)<sum(sides)):
            raise ValueError('invalid triangular geometry')
        z=list(map(ctypes.c_double,(*sides,0,0,0)))
        self.lib.dimh3p_(*[ctypes.byref(x) for x in z])
        if not math.isfinite(z[3].value):
            raise ArithmeticError('nonfinite original native ground-state PES')
        return z[3].value

def jacobi_sides(R,r,c,ma,mb):
    """A=-mb/(ma+mb)*r z, B=+ma/(ma+mb)*r z, C=R vector."""
    a=mb/(ma+mb);b=ma/(ma+mb)
    ac=math.sqrt(R*R+a*a*r*r+2*a*R*r*c)
    bc=math.sqrt(R*R+b*b*r*r-2*b*R*r*c)
    return r,ac,bc

def interaction(pes,R,r,c,ma,mb):
    return pes.e1(*jacobi_sides(R,r,c,ma,mb))-pes.h2(r)

def midpoint_transform(R,r,c,ma,mb):
    """Exactly translate COM-anchored Jacobi R to electronic midpoint-anchored R."""
    delta=(ma-mb)*r/(2*(ma+mb))
    rm=math.sqrt(R*R+delta*delta-2*R*delta*c)
    cm=(R*c-delta)/rm
    return rm,cm

def writer(path,header,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows)

def isotope_mass_lanes():
    return [('Hplus_HD', MP,MD,MP),('Dplus_H2',MP,MP,MD)]

def compute(pes,out,r38_archive):
    out.mkdir(parents=True,exist_ok=True)
    req=1.4  # deliberately fixed geometry: numerical h2 polynomial has strong cancellation near the minimum
    rvals=(1.20,req,1.60)
    x,w=leggauss(N_ANGLES)
    # Angular Legendre moments a_l=(2l+1)*[integral from -1 to +1 U*P_l dc]/2
    polys=[legval(x,[0.0]*ell+[1.0]) for ell in range(5)]
    energy_rows=[]; moments=[]; translations=[]
    nperm=0
    for label,ma,mb,mc in isotope_mass_lanes():
        for ri,r in enumerate(rvals):
            for R in R_VALUES:
                U=[]
                for c in x:
                    val=interaction(pes,R,r,float(c),ma,mb)
                    U.append(val)
                    energy_rows.append({'arrangement':label,'r_bohr':f'{r:.15g}','r_index':ri,
                        'R_bohr':f'{R:.15g}','cos_theta':f'{c:.17g}',
                        'V_minus_h2_hartree':f'{val:.17e}',
                        'V_minus_h2_K':f'{val*EH_K:.14e}'})
                    if ri==1 and R in (5.,12.,30.,75.):
                        rm,cm=midpoint_transform(R,r,float(c),ma,mb)
                        same=interaction(pes,rm,r,cm,MP,MP)
                        translations.append({'arrangement':label,'R_bohr':R,'cos_theta':f'{c:.17g}',
                            'R_midpoint_bohr':f'{rm:.17g}',
                            'residual_hartree':f'{val-same:.17e}'})
                U=np.asarray(U)
                a=[(2*ell+1)*float(np.dot(w,U*polys[ell]))/2 for ell in range(5)]
                moments.append({'arrangement':label,'r_bohr':f'{r:.15g}','r_index':ri,
                    'R_bohr':f'{R:.15g}',
                    **{f'Legendre_a{ell}_hartree':f'{a[ell]:.17e}' for ell in range(5)},
                    'C4_iso_at_R_hartree_a0_4':f'{-R**4*a[0]:.14e}',
                    'U_min_hartree':f'{np.min(U):.17e}',
                    'U_max_hartree':f'{np.max(U):.17e}'})
    writer(out/'NATIVE_PES_3BODY_JACOBI_5376.csv',list(energy_rows[0]),energy_rows)
    writer(out/'NATIVE_PES_LEGENDRE_168.csv',list(moments[0]),moments)
    writer(out/'COM_MIDPOINT_TRANSLATION_192.csv',list(translations[0]),translations)
    # Fit isotropic long-range C4 from source points, same reference r; no external fitted PES constants.
    h2ref=[m for m in moments if m['arrangement']=='Dplus_H2' and m['r_index']==1 and float(m['R_bohr'])>=60]
    radii=np.array([float(m['R_bohr']) for m in h2ref])
    c4s=np.array([float(m['C4_iso_at_R_hartree_a0_4']) for m in h2ref])
    fit=np.polyfit(1/radii**2,c4s,1)
    c4lim=float(fit[-1])
    # Rotational l for *relative* atom+diatom motion; j=0 rotor isotropic, NO spin scattering channels.
    barrier=[]
    for label,ma,mb,mc in isotope_mass_lanes():
        mu_r=ma*mb/(ma+mb)
        mu_R=mc*(ma+mb)/(ma+mb+mc)
        for ell in range(1,13):
            L=ell*(ell+1)
            rpeak=math.sqrt(4*mu_R*c4lim/L)
            Epeak=L**2/(16*mu_R*mu_R*c4lim)
            barrier.append({'arrangement':label,'orbital_l':ell,'mu_diatom_me':f'{mu_r:.12f}',
                'mu_relative_me':f'{mu_R:.12f}', 'C4_iso_hartree_bohr4':f'{c4lim:.14f}',
                'barrier_R_bohr':f'{rpeak:.14f}',
                'barrier_K':f'{Epeak*EH_K:.14f}',
                'barrier_meV':f'{Epeak*EH_EV*1000:.14f}',
                'model_status':'long_range_diagnostic' if rpeak>=20 else 'short_range_extrapolation_not_physical'})
    writer(out/'ISOTROPIC_C4_CENTRIFUGAL_24.csv',list(barrier[0]),barrier)
    # 2020 published erratum corrected Eq.(3), not a new scattering solution.
    Ts=(100.,105.,125.,150.,200.,205.,250.,255.,295.,300.,350.,400.)
    thermal=[]
    for T in Ts:
        orig=1.95e-9*math.exp(-428/T)  # 2019 published corrected final paper, superseded
        corr=9.94e-10*math.exp(-439/T)
        para=2.30e-10*math.exp(-407/T)
        ortho=7.66e-10*math.exp(-450/T)
        thermal.append({'T_K':T,'original_2019_fit_cm3_s':f'{orig:.16e}',
            'erratum_2021_corrected_total_fit_cm3_s':f'{corr:.16e}',
            'erratum_para_fit_cm3_s':f'{para:.16e}',
            'erratum_ortho_fit_cm3_s':f'{ortho:.16e}',
            'sum_separate_fits_cm3_s':f'{para+ortho:.16e}',
            'erratum_over_original_fit':f'{corr/orig:.12f}',
            'sum_fits_minus_total_fraction':f'{(para+ortho-corr)/corr:.12e}',
            'fit_source':'MNRAS_2021_erratum_doi_10.1093/mnras/staa3146'})
    writer(out/'PUBLISHED_THERMAL_ERRATUM_12.csv',list(thermal[0]),thermal)
    src_ref={}
    for lab,ma,mb,mc in isotope_mass_lanes():
        src_ref[lab]={'mu_diatom_me':ma*mb/(ma+mb),'mu_R_me':mc*(ma+mb)/(ma+mb+mc)}
    assert hashlib.sha256(r38_archive.read_bytes()).hexdigest()==EXPECTED_R38_ARCHIVE_SHA
    with zipfile.ZipFile(r38_archive) as z:
        cr=list(csv.DictReader(io.StringIO(z.read('results/BO_FD_SPECTRAL_CHANNEL_CROSSCHECK_190.csv').decode())))
    match=[]
    for row in cr:
        if int(row['HD_v'])==0 and int(row['H2_v'])==0 and int(row['HD_J'])<=6 and int(row['H2_J'])<=9:
            jp=int(row['H2_J'])
            match.append({'HD_v':0,'HD_j':row['HD_J'],'H2_vprime':0,'H2_jprime':jp,
                'R38_native_BO_delta_E_hartree':row['spectral_delta_E_hartree'],
                'R38_native_BO_threshold_K':row['spectral_threshold_K'],
                'Lepers_2021_erratum_para_ortho_group':'para' if jp%2==0 else 'ortho',
                'Lepers_2021_multiplier_for_2019_unweighted_state_rate':'.25' if jp%2==0 else '.75',
                'rate_value_available':'false',
                'source_scope':'metadata_crosswalk_only_no_GL_rate_reweighting'})
    assert len(match)==70
    writer(out/'R38_TI_QM_ERRATUM_CHANNEL_70.csv',list(match[0]),match)
    summary={'status':'exploratory_real_native_3body_pes_no_smatrix','TIQM_erratum_channel_metadata_rows':len(match),
        'fixed_reference_r_bohr':req,'source_h2_at_reference_hartree':pes.h2(req),
        'R_grid_bohr':list(R_VALUES),'r_grid_bohr':list(rvals),'N_angular_gauss':N_ANGLES,
        'native_PES_rows':len(energy_rows),'Legendre_moment_rows':len(moments),
        'COM_translation_witness_rows':len(translations),'isotropic_barrier_rows':len(barrier),
        'erratum_thermal_fit_rows':len(thermal),
        'C4_isotropic_infinite_R_frozen_r_hartree_bohr4':c4lim,
        'C4_fit_first_correction':float(fit[0]),
        'C4_fit_max_abs_residual':float(max(abs(np.polyval(fit,1/radii**2)-c4s))),
        'max_COM_midpoint_translation_abs_error_hartree':max(abs(float(v['residual_hartree'])) for v in translations),
        'isotope_masses':src_ref,
        'protected_science_limits':['bare-nuclear mass, clamped-electron BO ground PES',
            'reference r=1.4 Bohr is fixed geometry, not a certified equilibrium minimizer; not quantum rovibrational averaging','Legendre moments are geometry not true HD permanent dipole',
            'centrifugal model retains only isotropic -C4/R4 tail, omits anisotropic coupled channels',
            'no state-to-state S matrix, no reactive capture probability, no physical Q full',
            '2021 erratum thermal rates are literature-fit within 100-400 K, not reconstructed scattering'],
        'primary_sources':{'Velilla_2008':'10.1063/1.2973629',
            'Lepers_2019':'10.1093/mnras/stz1797',
            'Lepers_2021_erratum':'10.1093/mnras/staa3146',
            'GL2022':'10.1063/5.0128598'}}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--native-f',type=Path,required=True)
    ap.add_argument('--lib',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--r38-master',type=Path,required=True)
    args=ap.parse_args()
    assert hashlib.sha256(args.native_f.read_bytes()).hexdigest()==EXPECTED_NATIVE_SHA
    print(json.dumps(compute(PES(args.lib),args.out,args.r38_master),indent=2))
