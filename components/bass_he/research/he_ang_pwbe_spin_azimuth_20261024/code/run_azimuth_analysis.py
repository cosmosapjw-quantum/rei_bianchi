"""Fresh six-geometry source-formula quadrature, not a global solid-angle integral."""
import json
import math
from pathlib import Path
import platform
import sys
import numpy as np
import pwbe

UNIT=Path(__file__).resolve().parents[1]
LEVELS=[64,256,1024,2048]
FIXTURES=[('G1',100.,40.,1.,.2),('G2',100.,40.,.8,.6),
          ('G3',100.,40.,-.4,.75),
          ('G4',100.,40.,239/(2*math.sqrt(23800)),161/(2*math.sqrt(16000))),
          ('G5',100.,49.75,.5,.5),('G6',100.,49.75,1.,-1.)]


def raw_source_tdcs(E0,EB,muA,muB,phi):
    """Independent literal FIAS Eqs19-20 vector amplitudes + frozen spin trace.

    Uses Cartesian vectors and direct nuclear subtraction, independently of
    production positive-gap, rationalized difference and closed-azimuth code.
    """
    EA=E0-.5-EB
    k0,kA,kB=np.sqrt(2*np.array([E0,EA,EB]))
    v0=np.array([0.,0.,k0]);vA=np.array([kA*np.sqrt(1-muA*muA),0.,kA*muA])
    vB=np.stack([kB*np.sqrt(1-muB*muB)*np.cos(phi),
                 kB*np.sqrt(1-muB*muB)*np.sin(phi),np.full_like(phi,kB*muB)],axis=-1)
    q=v0-vA-vB; q2=np.sum(q*q,axis=-1)
    transferA=float(np.dot(v0-vA,v0-vA));transferB=np.sum((v0-vB)**2,axis=-1)
    source_pref=8*np.sqrt(2)/(2*np.pi)**3
    D=source_pref/transferA*((1+q2)**-2-(1+kB*kB)**-2)
    X=source_pref/transferB*((1+q2)**-2-(1+kA*kA)**-2)
    return (2*np.pi)**4*(kA*kB/k0)*(.25*(D+X)**2+.75*(D-X)**2)


def main():
    UNIT.joinpath('results').mkdir(exist_ok=True)
    records=[];checks=[]
    for name,E0,EB,ma,mb in FIXTURES:
        closed=pwbe.pwbe_azimuth(E0,EB,ma,mb)
        levels=[]
        for N in LEVELS:
            phi=2*np.pi*np.arange(N)/N
            raw=raw_source_tdcs(E0,EB,ma,mb,phi)
            Kbar=float(np.mean(raw));Cbar=float(np.mean(raw*np.cos(phi)))
            cos=Cbar/Kbar
            # Independent raw-source law divided by the closed normalization.
            # API denominator itself is separately checked at nonconstant geometry.
            pdf=raw/(2*np.pi*closed['Kbar'])
            normalization=float(2*np.pi*np.mean(pdf))
            row={'N':N,'raw_source_Kbar':Kbar,'raw_source_Cbar':Cbar,
                 'raw_source_cos_phi':cos,'Kbar_relative_error':abs(Kbar-closed['Kbar'])/closed['Kbar'],
                 'conditional_cos_absolute_error':abs(cos-closed['cos_phi']),
                 'conditional_normalization':normalization,'normalization_error':abs(normalization-1)}
            levels.append(row)
        final=levels[-1]
        passed=(final['Kbar_relative_error']<=1e-10 and final['conditional_cos_absolute_error']<=1e-10
                and final['normalization_error']<=1e-10 and closed['M0']>=0
                and abs(closed['cos_phi'])<=1+2e-12)
        checks.append(passed)
        records.append({'id':name,'E0':E0,'EB':EB,'muA':ma,'muB':mb,
                        'closed':closed,'levels':levels,'finite_case_acceptance':passed})
    # Saved diagnostic curves and pointwise heatmap, not integrated over mu/energy.
    phi=np.linspace(0,2*np.pi,1025)
    _,E0,EB,ma,mb=FIXTURES[3]
    pdf=[pwbe.conditional_azimuth_pdf(E0,EB,ma,mb,float(t))['pdf'] for t in phi]
    raw=raw_source_tdcs(E0,EB,ma,mb,phi)
    rawpdf=raw/(2*np.pi*records[3]['closed']['Kbar'])
    mus=np.linspace(-1,1,41)
    heat=[[pwbe.pwbe_azimuth(100,40,float(a),float(b))['Kbar'] for a in mus] for b in mus]
    spin_phi=np.linspace(0,2*np.pi,361)
    singlet=[];triplet=[];unpolarized=[]
    for t in spin_phi:
        p=pwbe.pwbe_point(100,49.75,.5,.5,float(t))
        pref=(2*math.pi)**4*p['geometry']['kA']*p['geometry']['kB']/p['geometry']['k0']
        singlet.append(pref*.25*p['spin']['singlet'])
        triplet.append(pref*.75*p['spin']['triplet'])
        unpolarized.append(p['K'])
    result={'unit':'HE-ANG-PWBE-SPIN-AZIMUTH','status':'FINITE_ANALYSIS_COMPLETE_PENDING_C9',
        'model':pwbe.METADATA,'source_table_values_used':0,'old_science_runs':0,
        'fixtures':records,'all_six_pass':all(checks),'periodic_levels':LEVELS,
        'quadrature_independence':'literal raw vector FIAS Eqs19-20 amplitudes, direct nuclear subtraction, independent NumPy trapezoid; closed production uses Eqs8-10',
        'acceptance':{'final_Kbar_relative':1e-10,'final_conditional_cos_absolute':1e-10,'normalization_absolute':1e-10},
        'diagnostics':{'G4_phi':phi.tolist(),'G4_pdf':pdf,'G4_raw_source_pdf':rawpdf.tolist(),
                       'heat_mu':mus.tolist(),'heat_Kbar':heat,'equal_phi':spin_phi.tolist(),
                       'equal_weighted_singlet':singlet,'equal_weighted_triplet':triplet,'equal_K':unpolarized},
        'scope':'finite frozen geometries and pointwise grid; no global angle/energy integral, no physical accuracy bound, no empirical fit',
        'versions':{'Python':sys.version,'platform':platform.platform(),'NumPy':np.__version__}}
    (UNIT/'results/AZIMUTH_ANALYSIS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'all_six_pass':all(checks),'fixtures':[{k:r[k] for k in ['id','finite_case_acceptance']}|{'final':r['levels'][-1]} for r in records]},indent=2))
    return 0 if all(checks) else 1


if __name__=='__main__':raise SystemExit(main())
