"""Frozen new fixtures: binary64, mp50/80, independent Eq6 quad4.

Only the bounded runner may launch this after root GO. All mp digits are saved;
old science modules, datasets, and solver campaigns are never imported.
"""
import csv
import datetime
import json
import math
from pathlib import Path
import traceback
import mpmath as mp
import cba

UNIT=Path(__file__).resolve().parents[1]
FIX=json.loads((UNIT/'evidence/preparation/FIXTURES.json').read_text())
TOL=json.loads((UNIT/'FROZEN_CONTRACT.json').read_text())['acceptance']
RESULTS=UNIT/'results'
REPORT={'schema':'HEANG_CBA_ANALYSIS_V1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'model':'fixed-centre labelled direct CBA; exchange absent',
        'generic':[],'quad4':[],'tiny_transfer':[],'normalization':[],'illustration':[],
        'acceptance':TOL,'source_data_recalculation':False,'old_science_replay':0,
        'scope':'Finite fixtures only; no full-domain/outward or physical provider certificate'}


def cjson(z):
    return {'real':float(z.real),'imag':float(z.imag)}


def mpjson(z):
    return {'real':mp.nstr(mp.re(z),85),'imag':mp.nstr(mp.im(z),85)}


def scaled(value,reference):
    return abs(value-reference)/max(mp.mpf(1),abs(reference))


def save(name='ANALYSIS_PARTIAL.json'):
    RESULTS.mkdir(exist_ok=True)
    (RESULTS/name).write_text(json.dumps(REPORT,indent=2,allow_nan=False)+'\n')


def mpreal(x):
    # Preserve the exact binary64 fixture input, then evaluate at chosen digits.
    return mp.mpf(x)


def mp_formula(lam,q,pvec,eta):
    lam,eta=mpreal(lam),mpreal(eta)
    q,pvec=[mpreal(v) for v in q],[mpreal(v) for v in pvec]
    p=mp.sqrt(sum(v*v for v in pvec)); A=sum(v*v for v in q)+lam*lam
    B=A+2*sum(a*b for a,b in zip(q,pvec))-2j*lam*p
    C=mp.exp(1j*eta*(mp.log(A)-mp.log(B))); I=4*mp.pi*C/A
    K=2*I*((1-1j*eta)*lam/A+1j*eta*(lam-1j*p)/B)
    return I,K


def mp_matched(lam,delta,pvec):
    lam=mpreal(lam); delta=[mpreal(v) for v in delta];pvec=[mpreal(v) for v in pvec]
    p=mp.sqrt(sum(v*v for v in pvec));eta=lam/p
    A=sum((a-b)**2 for a,b in zip(delta,pvec))+lam*lam
    dd=sum(v*v for v in delta); B=dd+(lam-1j*p)**2
    C=mp.exp(1j*eta*(mp.log(A)-mp.log(B)))
    return 16*mp.pi*lam*C*(dd-(1+1j*eta)*sum(a*b for a,b in zip(delta,pvec)))/(A*A*B)


def run():
    for f in FIX['generic']:
        args=(f['lambda'],f['qvec'],f['pvec'],f['eta'])
        I,K=cba.nordsieck_i(*args),cba.overlap_k(*args)
        with mp.workdps(50): r50=mp_formula(*args)
        with mp.workdps(80):
            r80=mp_formula(*args)
            errors=[scaled(mp.mpc(v),r) for v,r in zip((I,K),r80)]
            digit_errors=[scaled(a,b) for a,b in zip(r50,r80)]
            # Independent fixed-eta lambda derivative. Eta stays separate.
            lam,q,pvec,eta=args
            def independent_I_at_lambda(l):
                pp=mp.sqrt(sum(mpreal(v)**2 for v in pvec))
                A=sum(mpreal(v)**2 for v in q)+l*l
                B=A+2*sum(mpreal(a)*mpreal(b) for a,b in zip(q,pvec))-2j*l*pp
                return 4*mp.pi/A*mp.exp(1j*mpreal(eta)*(mp.log(A)-mp.log(B)))
            fixed_eta_derivative=-mp.diff(independent_I_at_lambda,mpreal(lam))
            derivative_error=scaled(fixed_eta_derivative,r80[1])
            row={'fixture':f,'I_binary64':cjson(I),'K_binary64':cjson(K),
                 'I_mp50':mpjson(r50[0]),'K_mp50':mpjson(r50[1]),'I_mp80':mpjson(r80[0]),'K_mp80':mpjson(r80[1]),
                 'binary64_scaled_errors':[float(e) for e in errors],
                 'mp50_vs80_scaled_errors':[mp.nstr(e,30) for e in digit_errors],
                 'fixed_eta_derivative_scaled_error':mp.nstr(derivative_error,30),
                 'pass':all(e<=TOL['binary64_scaled_complex'] for e in errors)
                        and all(e<=TOL['mp50_vs80_formula_relative_or_abs_scaled'] for e in digit_errors)
                        and derivative_error<=TOL['mp50_vs80_formula_relative_or_abs_scaled']}
        REPORT['generic'].append(row);save()

    for f in FIX['quad4']:
        with mp.workdps(50):
            lam,p,eta,qz,qp=[mpreal(f[n]) for n in ['lambda','p','eta','qz','qperp']]
            b=(lam+1j*qz)/2;d=qp*qp/4
            A=qp*qp+qz*qz+lam*lam;s=A/(2*(lam+1j*qz))
            def integrand(xi):
                return mp.exp(-s*xi)*mp.hyp1f1(1j*eta,1,1j*p*xi)*(xi+1/b-d*xi/(b*b))
            parts=[mp.quad(integrand,[a,z]) for a,z in [(0,1),(1,4),(4,12),(12,mp.inf)]]
            original_integral=mp.pi/(2*b)*sum(parts)
            closed=mp_formula(f['lambda'],[f['qperp'],0,f['qz']],[0,0,f['p']],f['eta'])[1]
            error=scaled(original_integral,closed)
            row={'fixture':f,'Eq6_mp50':mpjson(original_integral),'Eq2_mp50':mpjson(closed),
                 'integration_segments':['0..1','1..4','4..12','12..infinity'],
                 'raw_integral_parts':[mpjson(v) for v in parts],
                 'scaled_error':mp.nstr(error,40),'pass':error<=TOL['mp50_quadrature_relative_or_abs_scaled']}
        REPORT['quad4'].append(row);save()

    tiny=FIX['tiny_transfer']
    for name,direction in tiny['directions'].items():
        for k in tiny['powers']:
            t=10.**(-k);delta=[t*v for v in direction];pvec=tiny['pvec'];lam=tiny['lambda']
            stable=cba.matched_overlap(lam,delta,pvec)
            q=[a-b for a,b in zip(delta,pvec)]
            generic=cba.overlap_k(lam,q,pvec,lam/math.hypot(*pvec))
            with mp.workdps(80):
                ref=mp_matched(lam,delta,pvec)
                error=abs(mp.mpc(stable)-ref)/abs(ref) if ref else abs(stable)
                generic_error=abs(mp.mpc(generic)-ref)/abs(ref) if ref else abs(generic)
                row={'direction':name,'power':k,'t_binary64':t,'delta':delta,
                     'stable_binary64':cjson(stable),'generic_binary64':cjson(generic),'mp80stable':mpjson(ref),
                     'stable_true_relative_error':float(error),'generic_true_relative_error_DIAGNOSTIC_ONLY':float(generic_error),
                     'K_div_t_or_t2_DIAGNOSTIC_ONLY':mpjson(ref/mpreal(t)**(1 if name=='parallel' else 2)),
                     'pass':error<=TOL['matched_tiny_transfer_relative']}
            REPORT['tiny_transfer'].append(row);save()

    for eta in FIX['normalization_etas']:
        Nc=cba.coulomb_normalizer(eta);S=cba.sommerfeld_strength(eta)
        with mp.workdps(80):
            e=mpreal(eta);exact_N=mp.exp(mp.pi*e/2)*mp.gamma(1-1j*e)/(2*mp.pi)**mp.mpf('1.5')
            exact_S=1 if e==0 else 2*mp.pi*e/(-mp.expm1(-2*mp.pi*e))
            errN=scaled(mp.mpc(Nc),exact_N);errS=scaled(mpreal(S),exact_S)
            errStrength=scaled(mpreal(abs(Nc)**2),exact_S/(2*mp.pi)**3)
            row={'eta':eta,'Nc_binary64':cjson(Nc),'Nc_mp80':mpjson(exact_N),'S_binary64':S,'S_mp80':mp.nstr(exact_S,85),
                 'Nc_scaled_error':float(errN),'S_scaled_error':float(errS),'strength_scaled_error':float(errStrength),
                 'pass':max(errN,errS,errStrength)<=TOL['normalized_strength_relative_or_abs_scaled']}
        REPORT['normalization'].append(row);save()

    illustration=FIX['illustration'];U=illustration['nominal_eV_per_Hartree']
    angle_sc=math.radians(illustration['scattered_theta_degree'])
    Ei=illustration['incident_eV']/U;EB=illustration['ejected_eV']/U
    for angle in range(-180,181,5):
        theta=math.radians(angle);nb=(math.sin(theta),0.,math.cos(theta));nf=(math.sin(angle_sc),0.,math.cos(angle_sc))
        row={'oriented_ejected_angle_degree':angle,'units':'a0^2/(eV sr^2), nominalU27.2'}
        for model in ['cba','plane']:
            v=cba.direct_tdcs(Ei,EB,(0,0,1),nf,nb,model)
            ratio=math.sqrt(2*v['Ef'])*math.sqrt(2*EB)/math.sqrt(2*Ei)
            tdcs_delta=(2*math.pi)**4*ratio*abs(v['T_delta'])**2
            coeff_error=abs(v['tdcs_au']-tdcs_delta)/max(1.,abs(tdcs_delta))
            row[model+'_tdcs_au']=v['tdcs_au'];row[model+'_tdcs_per_eV']=v['tdcs_au']/U
            row[model+'_F']=cjson(v['F']);row[model+'_delta_state_scaled_error']=coeff_error
        row['pass']=all(row[m+'_delta_state_scaled_error']<=TOL['binary64_scaled_complex'] for m in ['cba','plane'])
        REPORT['illustration'].append(row)
    save()
    categories=['generic','quad4','tiny_transfer','normalization','illustration']
    REPORT['checks_by_category']={k:{'rows':len(REPORT[k]),'passed':sum(r['pass'] for r in REPORT[k])} for k in categories}
    REPORT['pass']=all(r['pass'] for k in categories for r in REPORT[k])
    REPORT['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save('ANALYSIS.json')
    with (RESULTS/'ILLUSTRATION.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['oriented_ejected_angle_degree','cba_tdcs_au','plane_tdcs_au','cba_tdcs_per_eV','plane_tdcs_per_eV'])
        writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in REPORT['illustration'])
    print(json.dumps({'pass':REPORT['pass'],'checks':REPORT['checks_by_category']}))
    return 0 if REPORT['pass'] else 1


if __name__=='__main__':
    try:
        raise SystemExit(run())
    except Exception as exc:
        REPORT['exception']={'class':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        save('ANALYSIS_FAILURE.json')
        raise
