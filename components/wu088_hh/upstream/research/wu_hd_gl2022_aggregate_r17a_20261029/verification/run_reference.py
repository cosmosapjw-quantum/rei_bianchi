"""One-time independent reference file; never imports src.aggregate."""
import json,argparse,sys
from pathlib import Path
from independent_reference import independent

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    rows,gam,alpha=independent(a.source)
    import mpmath
    o={'schema':'WU_R17A_INDEPENDENT_MPMATH_REFERENCE_V1','rows':[
        {'T_K':r['T_K'],'difference_exact':str(r['diff']),'SQM_SI_exact':str(r['SI']),'printed_displacement_exact':str(r['displacement']),
         'fit_mpmath_90digits':mpmath.nstr(r['fit_mpmath'],90),'fit_ratio_mpmath_90digits':mpmath.nstr(r['fit_ratio_mpmath'],90)}
         for r in rows],
         'two_printed_point_gamma_K_90digits':mpmath.nstr(gam,90),
         'two_printed_point_alpha_1e-10_cm3_s_90digits':mpmath.nstr(alpha,90),
         'note':'Rounded published total rates, not native state-resolved data; no source row or physical admission'}
    with a.output.open('x',encoding='utf8') as f:f.write(json.dumps(o,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
