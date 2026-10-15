#!/usr/bin/env python3
"""Focused checks of frozen numerical bridge criteria on actual output files."""
import argparse,csv,json,math
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('results',type=Path);a=p.parse_args();root=a.results
    checks=[]
    def check(name,value,limit):
        checks.append(dict(check=name,observed=value,limit=limit,passes=math.isfinite(value) and value<=limit))
    def read(name):return json.loads((root/name).read_text())
    def csvread(name):
        with (root/name).open(newline='') as f:return list(csv.DictReader(f))
    x=read('inventory17.json')
    for k in ['baryon_map_residual','nuclear_charge_map_residual','tracked_electron_charge_residual']:
        check(k,abs(x[k]),5e-14)
    check('max_isotope_sum_relative',x['max_isotope_sum_relative'],1e-12)
    check('registry_size_difference',abs(x['registry_size']-17),0.)
    pop=[float(r['Y_per_donor_baryon']) for r in csvread('inventory17.csv')]
    check('nonpositive_inventory_violation',sum(not math.isfinite(v) or v<0 for v in pop),0.)
    c=read('cascade_mixture.json')
    for r in c['mixture_moments']:
        tag=r['species']+'_'+str(r['n'])
        check('cascade_energy_'+tag,abs(r['energy_closure_eV']),max(1e-14,1e-11*r['initial_excitation_eV']))
        check('cascade_count_'+tag,abs(r['photon_crosscheck_residual']),max(1e-14,1e-11*r['E1_photon_count']))
        check('cascade_terminal_'+tag,abs(r['terminal_probability_residual']),1e-12)
        check('cascade_2s_crosscheck_'+tag,abs(r['terminal_2s_crosscheck_residual']),1e-12)
        check('cascade_terminal_bounds_'+tag,max(0.,-r['terminal_1s_probability'],-r['terminal_2s_probability'],
                                               r['terminal_1s_probability']-1,r['terminal_2s_probability']-1),1e-12)
    n=read('np_anchor_sensitivity.json')
    check('np64_vs256',n['max_64_vs_256_relative'],1e-10)
    nr=csvread('np_anchor_sensitivity.csv')
    check('np_affine_derivative',max(abs(float(r['affine_prediction_residual_m3_s'])/float(r['capture_m3_s'])) for r in nr),1e-12)
    check('np_midpoint',max(abs(float(nr[j]['capture_m3_s'])+float(nr[j+8]['capture_m3_s'])-2*float(nr[j+4]['capture_m3_s']))/
               (2*float(nr[j+4]['capture_m3_s'])) for j in range(0,len(nr),12)),1e-12)
    s=read('source_band_moments.json')
    for b in s['bands']:
        check('source_number_'+b['band'],abs(b['photon_1024_to_2048_relative']),1e-10)
        check('source_energy_'+b['band'],abs(b['energy_1024_to_2048_relative']),1e-10)
        check('source_independent_number_'+b['band'],abs(b['photon_2048_to_16384_relative']),1e-10)
        check('source_independent_energy_'+b['band'],abs(b['energy_2048_to_16384_relative']),1e-10)
    for r in s['LiI_photo_response']:
        check('photo_energy_identity_'+r['band'],abs(r['energy_identity_relative_residual']),1e-12)
        check('photo_Gamma_reference_'+r['band'],abs(r['Gamma_4096_to_16384_relative']),1e-10)
        check('photo_heating_reference_'+r['band'],abs(r['heating_4096_to_16384_relative']),1e-10)
        check('photo_nonnegative_'+r['band'],sum(r[k]<0 or not math.isfinite(r[k]) for k in
                  ['Gamma_s_inverse','heating_J_s_per_LiI','absorbed_energy_J_s_per_LiI']),0.)
    for r in s['LiI_photo_response_refinement']:
        if r['fine_n']==4096:
            check('photo_Gamma_final_'+r['band'],abs(r['Gamma_relative']),1e-10)
            check('photo_heating_final_'+r['band'],abs(r['heating_relative']),1e-10)
    result=dict(status='PASS' if all(c['passes'] for c in checks) else 'FAIL',
      claim='targeted implementation checks only; scientific admission independent',
      checks_passed=sum(c['passes'] for c in checks),checks_total=len(checks),checks=checks,
      source_coarse_quadrature_failures_preserved=sum(not r['passes_1e_minus_10'] for r in s['quadrature_refinement']),
      photo_coarse_quadrature_failures_preserved=sum(max(abs(r['Gamma_relative']),abs(r['heating_relative']))>1e-10 for r in s['LiI_photo_response_refinement']))
    (root/'CHECKS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
    raise SystemExit(result['status']!='PASS')
if __name__=='__main__':main()
