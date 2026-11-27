"""Independent Decimal 80-digit calculation; no import from reciprocity.py."""
from decimal import Decimal as D, localcontext
from pathlib import Path
import json

with localcontext() as ctx:
    ctx.prec=80
    m=D('3727.3794118');d=D('1875.61294500')
    rows=[]
    for estr in ['213','330']:
        e=D(estr);s=m*m+2*m*e; root=s.sqrt()
        t=(s-4*d*d)/(2*d)
        k=(s-m*m)/(2*root)
        q=((s-4*d*d)/4).sqrt()
        ordered=D(2)/9*(k/q)**2
        for mu in [D(-1),D(0),D(1)/3,D(1)]:
            boost=(m+e)/root
            ep=(m+e)/2+e*q*mu/root
            em=(m+e)/2-e*q*mu/root
            pzp=e/2+boost*q*mu
            pzm=e/2-boost*q*mu
            pt2=q*q*(1-mu*mu)
            rows.append({'Egamma_MeV':str(e),'mu':str(mu),
                         'Td_MeV':str(t),'ordered_ratio':str(ordered),
                         'event_ratio':str(2*ordered),
                         'E_sum_residual_MeV':str(ep+em-(m+e)),
                         'p_z_sum_residual_MeV':str(pzp+pzm-e),
                         'mass_shell_plus_residual_MeV2':str(ep*ep-pzp*pzp-pt2-d*d),
                         'mass_shell_minus_residual_MeV2':str(em*em-pzm*pzm-pt2-d*d)})
    t=D(376)
    s=4*d*d+2*d*t
    result={'method':'independent Decimal80 direct four-vector algebra',
            'T376_to_Egamma_MeV':str((s-m*m)/(2*m)),
            'cases':rows,'inverse_330_measured':None,
            'event_normalization_admitted':False}
Path(__file__).with_name('INDEPENDENT_ORACLE.json').write_text(json.dumps(result,indent=2)+'\n')
print('cases',len(rows),'T376_to_Egamma',result['T376_to_Egamma_MeV'])
