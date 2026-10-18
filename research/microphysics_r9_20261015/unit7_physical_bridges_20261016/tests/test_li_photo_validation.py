"""Focused finite-contract checks, called once by the numerical driver."""
import math

def validate(raw,moments,cross,convergence,comparisons,independent,mixtures,delta):
    from li_photo_driver import relative,EV,BV,BK,FIELDS,sigma,ph1,ph2
    checks=[]
    def check(name,value,limit=0): checks.append({'name':name,'observed':value,'limit':limit,'passed':value<=limit})
    check('cross_section_Decimal_log_formula_max_relative',max(relative(r['sigma_Mb'],r['Decimal_reference_Mb'],1e-30) for r in cross),1e-11)
    check('128_256_response_max_relative',max(r['relative_128_256'] for r in convergence),1e-8)
    check('legacy_64_39_and_sub_Lyman_max_relative',max(r['relative_difference'] for r in comparisons),1e-8)
    check('independent_full_G_W_K_max_relative',max(v for r in independent for m in r['scaled_mixture_checks'] for v in m['relative_G_W_K']),1e-8)
    closures=[]; source_errors=[]; nonnegative=[]; unchanged=[]
    for m in mixtures:
        sp=m['species']; n=m['n']; de=delta[sp]; p=m['terminal_2s_probability']
        source_errors.append(relative(p*de,m['terminal_2s_energy_eV'],1e-14))
        for band in ['sub_Lyman','upper_old','extension','covered_total','full_total']:
            for shell in ['1s','2s','total']:
                values=raw[sp,n,256,band,shell]; g,w,k,q,x=values
                nonnegative.extend(-v for v in values)
                closures.append(relative(w,k+q,1e-53))
                if shell=='total': closures.append(relative(q,EV*BV*g+x,1e-53))
            for j in range(5):
                closures.append(relative(raw[sp,n,256,band,'total'][j],sum(raw[sp,n,256,band,s][j] for s in ['1s','2s']),1e-35 if j==0 else 1e-53))
        for j in range(5):
            full=raw[sp,n,256,'full_total','total'][j]
            parts=sum(raw[sp,n,256,b,'total'][j] for b in ['sub_Lyman','upper_old','extension'])
            closures.append(relative(full,parts,1e-35 if j==0 else 1e-53))
        if de<BK:
            unchanged.extend(abs(v) for v in raw[sp,n,256,'extension','total'])
            unchanged.extend(abs(a-b) for a,b in zip(raw[sp,n,256,'full_total','total'],raw[sp,n,256,'covered_total','total']))
    for r in moments:
        if r['quadrature_nodes']==256 and r['band']=='full_source':
            source_errors.extend([relative(r['photon_count'],2*r['P_2s'],1e-14),relative(r['energy_eV'],r['P_Delta_eV'],1e-14)])
    check('shell_energy_band_closure_max_relative',max(closures),1e-11)
    check('source_photon_energy_and_reservoir_max_relative',max(source_errors),1e-8)
    check('nonnegative_response_violation',max([0]+nonnegative))
    check('subedge_species_extension_and_full_change_exact_zero',max(unchanged))
    truths=[sigma(5.391,'2s')==0,sigma(math.nextafter(BV,-math.inf),'2s')==0,sigma(BV,'2s')>0,
        sigma(math.nextafter(BK,-math.inf),'1s')==0,sigma(BK,'1s')==ph1(BK,'1s'),sigma(BK,'2s')==ph1(BK,'2s'),
        sigma(math.nextafter(BK,-math.inf),'2s')==ph2(math.nextafter(BK,-math.inf)),all(sigma(e,'3')==0 for e in [BV,BK,80,max(delta.values())]),
        all(raw['LiIII_infinite_mass',n,256,'extension','total'][0]>0 for n in [3,5,10,12])]
    check('branch_and_occupied_shell_truth_table_failures',sum(not x for x in truths))
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'validation_passes':1,'optional_expansion':'NONE'}
