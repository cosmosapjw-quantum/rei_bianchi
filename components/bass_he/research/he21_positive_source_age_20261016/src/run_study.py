"""Bounded, independently repeatable source-cohort Python study (not NCP/Rust)."""
from __future__ import annotations
import csv, dataclasses, hashlib, json, math, os, pathlib, sys, time
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from he21_photo import run, temperature, X_END, SOURCE_N_PER_H, Y_HE

QS=(-0.005,0.,0.005)
MS=(4,8,16)
NT=(4,8,16)

def one(params):
    m,n,q=params
    x=run(m,n,q)
    r=dataclasses.asdict(x)
    r['temperature_final_K']=temperature(x.gas_final)
    r['total_absorbed_per_H']=sum(x.absorbed)
    r['total_absorbed_fraction']=r['total_absorbed_per_H']/x.source_count
    r['relative_photon_number_defect']=abs(x.number_defect)/x.source_count
    r['relative_energy_defect']=abs(x.energy_defect)/(x.source_energy_ev+x.initial_gas_u_ev)
    return r

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def main():
    root=pathlib.Path(__file__).resolve().parents[1]
    out=root/'results';out.mkdir(exist_ok=True)
    jobs=[(m,n,q) for q in QS for n in NT for m in MS]
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        result=list(pool.map(one,jobs))
    elapsed=time.perf_counter()-start
    result.sort(key=lambda x:(x['q'],x['steps'],x['m']))
    for row in result:
        if not(all(v>=0 for v in row['absorbed']) and
               row['max_support_crossing']==0 and
               row['relative_photon_number_defect']<3e-12 and
               row['relative_energy_defect']<3e-12 and
               abs(row['electron_defect'])<3e-12 and
               row['source_shape_energy_defect']<2e-12):
            raise AssertionError(('failed physics',row))
    with (out/'HE21_PHOTO_ONLY_27.csv').open('w',newline='') as f:
        keys=['q','m','steps','temperature_final_K','total_absorbed_fraction','absorbed_HI','absorbed_HeI','absorbed_HeII',
              'heat_ev','work_photon_ev','binding_delta_ev','relative_photon_number_defect','relative_energy_defect','max_support_crossing']
        writer=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");writer.writeheader()
        for row in result:
            writer.writerow(dict(q=row['q'],m=row['m'],steps=row['steps'],temperature_final_K=row['temperature_final_K'],
                total_absorbed_fraction=row['total_absorbed_fraction'],
                absorbed_HI=row['absorbed'][0],absorbed_HeI=row['absorbed'][1],absorbed_HeII=row['absorbed'][2],
                heat_ev=row['heat_ev'],work_photon_ev=row['work_photon_ev'],binding_delta_ev=row['binding_delta_ev'],
                relative_photon_number_defect=row['relative_photon_number_defect'],relative_energy_defect=row['relative_energy_defect'],
                max_support_crossing=row['max_support_crossing']))
    qc=[r for r in result if r['q']==0.]
    ordered={str(n):{str(m):r['absorbed'][0] for r in qc if r['steps']==n for m in (r['m'],)} for n in NT}
    best=[r for r in qc if r['m']==16 and r['steps']==16][0]
    report={
      'schema':'bass_he.he21.local_reference.v1',
      'status':'LOCAL_PYTHON_IMPLEMENTATION_VERIFIED_PHOTO_ONLY',
      'not_executed':['NCP HE21 native Rust','original Grackle Case A RHS','full dynamic EoR'],
      'he20_source_commit':'ccd9125e6776f3f8d3388d70c6675873464c5f30',
      'cr72_reuse_source':'e91ffe368c4e6db64c4b6c5962566302a33402b6',
      'rei152_verner_fit_source':'bbbd18b5c16eff70bc32ba4296360dceb9060ec4',
      'verner_donor_full_raw_sha_as_reported':'a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389',
      'only_three_verner_table_rows_used':True,
      'physics_approximations':['constant photon emission per logarithmic scale-factor step',
                                'isotropic birth directions in local comoving frame',
                                'photo-only implicit endpoint gas; no CI/RR/DR/Compton',
                                'midpoint opacity and geometrical source-age drift',
                                'small z20 to 19.998 LRS prescribed background, no Einstein feedback'],
      'cases':len(result),'processes':3,'elapsed_s':elapsed,'source_total_per_H':SOURCE_N_PER_H,
      'X_end_ln_a':X_END,'helium_number_ratio':Y_HE,
      'max_relative_number_defect':max(x['relative_photon_number_defect'] for x in result),
      'max_relative_energy_defect':max(x['relative_energy_defect'] for x in result),
      'max_absolute_electron_defect':max(abs(x['electron_defect']) for x in result),
      'support_straddle_count':sum(x['max_support_crossing'] for x in result),
      'max_source_count_defect_per_stage':max(x['source_shape_number_defect'] for x in result),
      'max_source_energy_defect_per_stage':max(x['source_shape_energy_defect'] for x in result),
      'q0_absorbed_HI_by_m_and_time':ordered,
      'q0_m16_t16':best,
      'sha_files':{a:sha(root/a) for a in ['src/he21_photo.py','src/run_study.py','tests/test_he21.py','results/HE21_PHOTO_ONLY_27.csv']},
    }
    (out/'RESULT_STATUS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['q0_m16_t16','sha_files']},indent=2,sort_keys=True))
    print('Q0_M16_T16:',json.dumps({k:best[k] for k in ('temperature_final_K','absorbed','heat_ev','work_photon_ev','relative_energy_defect')}))

if __name__=='__main__':main()
