"""Physical R38 output from unchanged native Velilla EPAPS h3plus.f and R37 source data.
Run: python -m src.run_r38 --r37 /path/WU_R37_SOURCE_ORIGINAL_20261030.zip --out /dir
"""
from __future__ import annotations
import argparse, csv, json, zipfile, hashlib, pathlib, itertools, math, re
import numpy as np
from .native_pes import NativePES, build
from .rovib import (RadialGrid, energy_levels, channels, source_minima, MU_HD, MU_H2,
                    EH_J, K_PER_EH, CM_PER_EH)

ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha256(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def write_csv(path, rows, cols):
    with pathlib.Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)

def execute(r37zip, out, step=0.0050, make_scan=True):
    out=pathlib.Path(out);out.mkdir(exist_ok=True,parents=True)
    r37zip=pathlib.Path(r37zip)
    if sha256(r37zip)!='4ea1e3e725cdc7d181ad2c155a2184b23de6c70b41b31ddcfda596277cf0a1a0':
        raise ValueError('R37 source original identity mismatch')
    lib=build()
    pes=NativePES(lib)
    extrema=source_minima(pes)
    grid=RadialGrid(step=step)
    hd=energy_levels(pes,MU_HD,range(12),2,grid)
    h2=energy_levels(pes,MU_H2,range(10),2,grid)
    allch=channels(hd,h2)
    assert len(allch)==190
    chmap={(a['initial_v'],a['initial_J'],a['product_J']):a for a in allch}
    write_csv(out/'R38_NATIVE_HD_H2_CHANNEL_THRESHOLDS_190.csv',allch,list(allch[0]))
    temp=[5,10,15,20,25,35,45,55,65,75,85,95,105,155,205,255,305,405,505,605,705,805,1005,1505,3005]
    thermal=[]
    for s in allch:
        for T in temp:
            thermal.append({'initial_v':s['initial_v'],'initial_J':s['initial_J'],
                'product_J':s['product_J'],'T_K':T,'delta_E_cm1':s['delta_E_cm1'],
                'threshold_K':s['threshold_K'],
                'Boltzmann_threshold_factor':math.exp(-s['threshold_K']/T)})
    write_csv(out/'R38_NATIVE_REACTION_THRESHOLD_THERMAL_4750.csv',thermal,list(thermal[0]))
    # native electronic PES original Fortran: 2D triangle atlas (a0, Hartree)
    surface=[]
    if make_scan:
        r_axis=np.linspace(1.30,3.40,64)
        angle_axis=np.linspace(30.,170.,65)
        for r,angle in itertools.product(r_axis,angle_axis):
            third=2*r*math.sin(math.radians(angle)/2)
            E=pes.dimh3p(float(r),float(r),float(third))[0]
            surface.append({'r12_a0':r,'r13_a0':r,'apex_angle_deg':angle,'r23_a0':third,
                            'electronic_Eh':E,'excitation_from_equilateral_cm1':(E-extrema['equilateral_Eh'])*CM_PER_EH})
        write_csv(out/'R38_NATIVE_VELILLA_PES_ISOSCELES_4160.csv',surface,list(surface[0]))
    # Original GL2022 paper Eq.(5)-(7), with independent native diatomic BO
    # nuclear rotational levels in numerator and full J0..8 denominator.
    # This remains a restricted partial sum because printed J5,7,8 are not
    # source admitted. Do not reinterpret as full author reaction rate.
    gl_token = re.compile(r"([0-9]+(?:\.[0-9]+)?)\(([0-9]+)\)")
    def parse_gl(s):
        m = gl_token.fullmatch(s)
        if m is None:raise ValueError(f"Non-numeric original GL source token: {s!r}")
        return float(m.group(1))*10.**(-int(m.group(2)))
    with zipfile.ZipFile(r37zip) as z:
        gl = json.loads(z.read('sources/GL2022_700_SOURCE.json'))
    assert gl['shape']==[10,7,10] and gl['temperature_nodes_K']==[15,55,105,255,505,1005,1505,2005,2505,3005]
    partials=[]
    for T in (55,105,255,505,1005,1505,2005,3005):
        it=gl['temperature_nodes_K'].index(T)
        weights=np.array([(2*j+1)*math.exp(-(hd[(0,j)]-hd[(0,0)])*K_PER_EH/T) for j in range(9)])
        zrot=float(np.sum(weights))
        weighted_rates={}
        for j in (0,1,2,3,4,6):
            subtotal=sum(parse_gl(gl['tokens_jprime_j_T'][jp][j][it])*(.25 if jp%2==0 else .75) for jp in range(10))
            weighted_rates[j]=float(weights[j]/zrot*subtotal)
        paper=parse_gl(gl['table11_thermal_nominal_tokens'][it]); subtotal=sum(weighted_rates.values())
        partials.append({'Tgas_K':T,'Eq5_partial_native_BO_J0to4plus6_cm3_s':subtotal,
            'Eq5_partial_native_BO_J0to4_cm3_s':sum(weighted_rates[j] for j in range(5)),
            'Zrot_native_BO_J0to8':zrot,'GL2022_printed_full_total_cm3_s':paper,
            'native_BO_partial_fraction_of_printed':subtotal/paper,
            'missing_initial_J':'5,7,8','level_energy_authority':'Velilla2008 native H2 diatomic PES, bare-proton/deuteron radial Schr (NOT GL author rotational levels)'})
    write_csv(out/'R38_GL_EQ5_NATIVE_BO_PARTIAL_8.csv',partials,list(partials[0]))
    # R37 population -> channel-resolved energy Q per first-exit event.
    energyrows=[];summary=[];group={};samekeys=('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J')
    with zipfile.ZipFile(r37zip) as z:
        filename='results/R37_CHEM_H2_PRODUCT_19200.csv'
        contents=z.read(filename).decode('utf-8')
        reader=csv.DictReader(contents.splitlines())
        count=0
        for row in reader:
            count+=1;key=tuple(row[k] for k in samekeys)
            init=int(row['initial_v0_J']);final=int(row['H2_final_J']);p=float(row['P_H2_J_before_first_exit']);channel=chmap[(0,init,final)]
            e={'Tgas_K':row['Tgas_K'],'n_Hplus_cm_minus3':row['n_Hplus_cm_minus3'],'z_boundary':row['z_boundary'],
               'spin_policy':row['spin_policy'],'initial_v0_J':init,'H2_final_J':final,
               'P_H2_J_before_first_exit':p,'Q_release_J':channel['Q_release_J'],
               'Q_weighted_J_per_initial_HD':p*channel['Q_release_J'],
               'threshold_K':channel['threshold_K'],
               'P_endothermic_H2_branch':p if channel['delta_E_Eh']>0 else 0.}
            energyrows.append(e)
            if key not in group:group[key]=[0.,0.,0.,0.,0.]
            agg=group[key];agg[0]+=p;agg[1]+=p*channel['Q_release_J'];agg[2]+=p if channel['delta_E_Eh']>0 else 0.;agg[3]+=p*abs(channel['Q_release_J']);agg[4]+=1
        assert count==19200 and len(group)==1920
        with z.open('results/R37_CHEM_VS_EXIT_1920.csv') as ff:
            other={tuple(r[k] for k in samekeys):float(r['P_H2_before_first_exit']) for r in csv.DictReader(line.decode() for line in ff)}
        assert len(other)==1920
        max_mass_defect=max(abs(v[0]-other[key]) for key,v in group.items())
    for key, v in sorted(group.items()):
        mass,q,endothermic,abse,m=v
        assert int(m)==10 and mass>0
        summary.append(dict(zip(samekeys,key))|{
            'P_H2_before_first_exit':mass,
            'expected_Q_release_J_per_initial_HD':q,
            'conditional_Q_release_J_per_reaction':q/mass,
            'conditional_Q_release_K':q/(mass*EH_J)*K_PER_EH,
            'P_endothermic_H2_branch_before_first_exit':endothermic,
            'fraction_endothermic_given_reaction':endothermic/mass,
            'expected_abs_Q_J_per_initial_HD':abse
        })
    write_csv(out/'R38_R37_H2_PRODUCT_ENERGY_19200.csv',energyrows,list(energyrows[0]))
    write_csv(out/'R38_R37_FIRST_EXIT_ENERGY_SUMMARY_1920.csv',summary,list(summary[0]))
    q00=(hd[(0,0)]-h2[(0,0)])*EH_J
    stats={
        'source':'Exact Velilla 2008 EPAPS original Fortran plus source-locked R37 first-exit H2 products',
        'native_fortran_SHA256':'8dbf8b7e3852d02504ba92317f79593051d689f1357263ac0891a3a24084ed8c',
        'supplement_zip_SHA256':'a781d3b6f7d3cdffc210f2e8abd436e7378eb3716af80eb96b102a542eaba304',
        'r37_zip_SHA256':sha256(r37zip),'units':'native Bohr, Hartree, bare nucleus masses; temperatures K; Q in J',
        'model':'finite-difference bare-nuclei 1D BO diatomic Schr v,J, no full 3-body scattering, no nonadiabatic corrections',
        'grid':vars(grid),'reduced_masses_electron':{'H2':MU_H2,'HD':MU_HD},
        'original_native_extrema':extrema,'E_HD_v0J0_Eh':hd[(0,0)],'E_H2_v0J0_Eh':h2[(0,0)],
        'reaction_v0J0_to_v0J0_Q_release_J':q00,
        'reaction_v0J0_to_v0J0_delta_E_K':-q00/EH_J*K_PER_EH,
        'channels':len(allch),'thermal_rows':len(thermal),'native_PES_points':len(surface),'GL_EQ5_native_partial_rows':len(partials),
        'r37_chemical_energy_rows':len(energyrows),'r37_chemical_energy_summaries':len(summary),
        'r37_probability_mass_max_error':max_mass_defect,
        'channel_threshold_K_range':[min(r['threshold_K'] for r in allch),max(r['threshold_K'] for r in allch)],
        'energy_release_J_range':[min(r['Q_release_J'] for r in allch),max(r['Q_release_J'] for r in allch)],
        'r37_Q_mean_conditional_J_range':[min(s['conditional_Q_release_J_per_reaction'] for s in summary),max(s['conditional_Q_release_J_per_reaction'] for s in summary)],
        'r37_fraction_endothermic_conditional_range':[min(s['fraction_endothermic_given_reaction'] for s in summary),max(s['fraction_endothermic_given_reaction'] for s in summary)]
    }
    (out/'SUMMARY.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    return stats

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--r37',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);ap.add_argument('--step',type=float,default=.0050)
    args=ap.parse_args();print(json.dumps(execute(args.r37,args.out,args.step),indent=2))
