"""A2 focused finite sums and imported-continuum checks only."""
import math
from li_photo_driver import relative,EV,BV,BK,FIELDS

def validate(raw,moments,linegroups,mixtures,point,rows,continuum,contract):
    checks=[]
    def check(name,value,limit=0):checks.append({'name':name,'observed':value,'limit':limit,'passed':value<=limit})
    line_residual=[];source_residual=[];algebra=[];zeros=[];imported=[];negative=[]
    for key,group in linegroups.items():
        for e,p,u in group:line_residual.append(relative(u,e*p,1e-14))
    for r in moments:
        line_residual.extend([relative(r['E1_photon_count'],r['saved_E1_photon_count'],1e-14),relative(r['E1_energy_eV'],r['saved_E1_energy_eV'],1e-14)])
        m=mixtures[r['species'],r['n']]
        source_residual.extend([relative(r['combined_photon_count'],m['E1_photon_count']+2*m['terminal_2s_probability'],1e-14),relative(r['combined_energy_eV'],m['initial_excitation_eV'],1e-14)])
        for component in contract['components']:
            for band in contract['bands']:
                for shell in contract['shells']:
                    values=raw[r['species'],r['n'],band,shell,component];g,w,k,q,x=values
                    negative.extend(0 if math.isfinite(v) and v>=0 else 1 for v in values)
                    algebra.append(relative(w,k+q,1e-53))
                    if shell=='total':algebra.append(relative(q,EV*BV*g+x,1e-53))
                    if (r['continuum_source_cap_eV'] if component=='continuum' else r['E1_source_cap_eV'] if component=='E1' else r['source_cap_eV'])<BK and shell=='1s':zeros.extend(abs(v) for v in values)
                for j in range(5):
                    total=raw[r['species'],r['n'],band,'total',component][j]
                    shells=math.fsum(raw[r['species'],r['n'],band,s,component][j] for s in ['1s','2s'])
                    algebra.append(relative(total,shells,1e-35 if j==0 else 1e-53))
            for shell in contract['shells']:
                for j in range(5):
                    get=lambda b:raw[r['species'],r['n'],b,shell,component][j]
                    floor=1e-35 if j==0 else 1e-53
                    algebra.extend([relative(get('covered_total'),get('sub_Lyman')+get('upper_old'),floor),relative(get('full_total'),get('covered_total')+get('extension'),floor)])
        for band in contract['bands']:
            for shell in contract['shells']:
                for j in range(5):
                    get=lambda c:raw[r['species'],r['n'],band,shell,c][j]
                    algebra.append(relative(get('combined'),get('E1')+get('continuum'),1e-35 if j==0 else 1e-53))
    for r in rows:
        if r['component']=='continuum':
            old=continuum[r['species'],r['n'],r['band'],r['shell']]
            imported.extend(r[f]!=old[f] for f in FIELDS)
    check('pure_line_energy_and_saved_moments_max_relative',max(line_residual),1e-11)
    check('combined_source_moments_max_relative',max(source_residual),1e-8)
    check('component_shell_band_and_energy_algebra_max_relative',max(algebra),1e-11)
    check('nonfinite_or_negative_response_coefficients',sum(negative))
    check('inner_shell_below_support_exact_zero',max([0]+zeros))
    check('imported_continuum_cells_changed',sum(imported))
    check('new_maximum_energy_Decimal_log_formula_max_relative',max(relative(r['kernel_Mb'],r['Decimal_log_reference_Mb'],1e-30) for r in point),1e-11)
    check('response_row_count_difference',abs(len(rows)-1440))
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'new_finite_sum_passes':1,'A1_quadrature_reruns':0,'optional_expansion':'NONE'}
