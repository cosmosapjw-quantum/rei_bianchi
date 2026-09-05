#!/usr/bin/env python3
"""Exceptional transverse momentum compatibility; independent research only.

The transverse operator is differentiated from the exact, byte-pinned M2 Ricci
oracle. Projectors below are oblique and are projectors only on det(L)=0.
No production solver, state projection, numerical rank tolerance, or native
runtime is defined here. All dimensional plots use an explicit reference L0.
"""
from __future__ import annotations

import argparse
import csv
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
DONOR = HERE.parent / 'rei_math_m2_spacetime_sign/derive_constraint_sign.py'
DONOR_BLOB = 'bd8c7a639628b7d44b1aaca16cd4f5a466245cda'


def _load_donor():
    raw = DONOR.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()
    if blob != DONOR_BLOB:
        raise RuntimeError('M2_DONOR_BLOB_MISMATCH')
    spec = importlib.util.spec_from_file_location('rei_m2_pinned', DONOR)
    if spec is None or spec.loader is None:
        raise RuntimeError('M2_DONOR_IMPORT_UNAVAILABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def derive() -> dict[str, Any]:
    upstream = _load_donor().derive()
    A = sp.Symbol('A', real=True, nonzero=True)
    N22,N23,N33,S12,S13 = sp.symbols('N22 N23 N33 S12 S13', real=True)
    sub = {upstream['a'][0]:A, upstream['a'][1]:0, upstream['a'][2]:0,
           upstream['n'][0,0]:0, upstream['n'][0,1]:0, upstream['n'][0,2]:0,
           upstream['n'][1,1]:N22, upstream['n'][1,2]:N23, upstream['n'][2,2]:N33,
           upstream['sigma'][0,1]:S12, upstream['sigma'][0,2]:S13}
    # Derive the geometric carrier from four-dimensional curvature first.
    carrier = sp.Matrix([upstream['Ricci'][0,2],upstream['Ricci'][0,3]])
    carrier = carrier.subs(sub, simultaneous=True).applyfunc(sp.expand)
    momentum = sp.Matrix([-upstream['E'][2,0],-upstream['E'][3,0]])
    momentum = momentum.subs(sub, simultaneous=True).applyfunc(sp.expand)
    sigma = sp.Matrix([S12,S13])
    q = sp.Matrix([upstream['q'][1],upstream['q'][2]])
    kappa = upstream['kappa']
    L = carrier.jacobian(sigma)
    det = sp.factor(L.det())
    P = -L/(6*A)
    Q = sp.eye(2)-P
    w = sp.Matrix(sp.symbols('w1 w2', real=True))
    return {'A':A,'N22':N22,'N23':N23,'N33':N33,'kappa':kappa,
            'L':L,'det':det,'P':P,'Q':Q,'sigma':sigma,'q':q,'w':w,
            'carrier':carrier,'momentum':momentum,
            'general_solution':kappa*q/(6*A)+Q*w}


def claim_boundary() -> dict[str,str]:
    return {'native_runtime':'NOT_RUN', 'BASS_native_bridge':'NOT_ADMITTED',
            'constraint_propagation':'NOT_PROVED', 'provider_export':'NOT_AUTHORIZED',
            'scope':'ALGEBRAIC_CONSTRAINT_COMPATIBILITY_ONLY',
            'visual_audit':'PENDING_DIRECT_IMAGE_INSPECTION',
            'first_interval':'NO_PASS_FIRST_CANONICAL_INTERVAL',
            'matter_interpretation':'TOTAL_NORMAL_FRAME_MOMENTUM_NOT_A_COMPLETE_MATTER_SOLUTION',
            'branch_selection':'EXACT_DETERMINANT_ZERO_NO_TOLERANCE_SWITCH',
            'projectors':'OBLIQUE_NOT_NECESSARILY_ORTHOGONAL',
            'time':'s=c*t; c retained explicitly'}


def _zero_matrix(matrix: sp.MatrixBase) -> list[str]:
    return [sp.sstr(sp.simplify(x)) for x in matrix]


def symbolic_report() -> dict[str, Any]:
    d = derive()
    A,L,D,P,Q = (d[k] for k in ['A','L','det','P','Q'])
    I = sp.eye(2)
    certificates = {
        'curvature_carrier': d['carrier']-L*d['sigma'],
        'Einstein_momentum': d['momentum']+L*d['sigma']+d['kappa']*d['q'],
        'Cayley_Hamilton': L*L+6*A*L+D*I,
        'P_defect': P*P-P+D*I/(36*A*A),
        'Q_defect': Q*Q-Q+D*I/(36*A*A),
        'LQ_defect': L*Q+D*I/(6*A),
        'QL_defect': Q*L+D*I/(6*A),
        'solution_defect': L*d['general_solution']+d['kappa']*d['q']-d['kappa']*Q*d['q']+D*d['w']/(6*A),
    }
    residuals = {k:_zero_matrix(v) for k,v in certificates.items()}
    if not all(x == '0' for values in residuals.values() for x in values):
        raise ArithmeticError('EXCEPTIONAL_CERTIFICATE_NONZERO')
    # Generic chart is used only for a symbolic rank witness, never to define
    # the branch solver: it omits N22=0, which has separate exact fixtures.
    sub = {d['N33']:(d['N23']**2-9*A*A)/d['N22']}
    Lex = L.subs(sub)
    if sp.simplify(Lex.det()) != 0 or Lex.rank() != 1:
        raise ArithmeticError('GENERIC_EXCEPTIONAL_RANK_WITNESS_FAILED')
    if sp.simplify(sp.trace(L)+6*A) != 0:
        raise ArithmeticError('TRACE_CERTIFICATE_FAILED')
    charts = []
    for b,flux in [(3,(2,0)),(-3,(2,6))]:
        s = {A:1,d['N22']:0,d['N23']:b,d['N33']:2,d['kappa']:1,
             d['q'][0]:flux[0],d['q'][1]:flux[1]}
        residual = (L*d['general_solution']+d['kappa']*d['q']).subs(s)
        if any(sp.simplify(x) != 0 for x in residual):
            raise ArithmeticError('ZERO_N22_CHART_FAILED')
        charts.append({'A_L0':1,'N22_L0':0,'N23_L0':b,'N33_L0':2,
                       'kappa_q_L0_squared':list(flux),
                       'rank':int(L.subs(s).rank()),
                       'compatibility':_zero_matrix((Q*d['q']).subs(s)),
                       'solution_residual':_zero_matrix(residual)})
    return {'schema':'rei-m2a-exceptional-symbolic-report/v1',
            'status':'PASS_REI_M2A_EXCEPTIONAL_ALGEBRA',
            'donor_blob':DONOR_BLOB,
            'matrix':[[sp.sstr(L[i,j]) for j in range(2)] for i in range(2)],
            'determinant':sp.sstr(D), 'trace':sp.sstr(sp.trace(L)),
            'exact_zero_certificates':residuals,
            'exact_zero_count':sum(len(v) for v in residuals.values()),
            'rank_one_reason':'det(L)=0 and tr(L)=-6A!=0 for real A!=0',
            'compatibility':'Q*q=0 for kappa_G!=0',
            'all_solutions':'sigma=kappa_G*q/(6A)+Q*w; rank(Q)=1 on the exceptional branch',
            'zero_N22_charts':charts, 'claim_boundary':claim_boundary()}


def condition_sweep() -> tuple[list[dict[str,str]], str]:
    # Numerical corroboration of an explicit near-exceptional family. These
    # are nondimensional algebraic inputs, not evolved cosmological states.
    import mpmath as mp
    rows = []
    with mp.workdps(80):
        max_error = mp.mpf('0')
        for exponent in range(1,10):
            delta = mp.power(10,-exponent)
            L = mp.matrix([[-3,9-delta],[1,-3]])
            bad = mp.lu_solve(L,mp.matrix([0,-1]))
            good = mp.lu_solve(L,mp.matrix([-3,1]))
            expected = mp.matrix([(9-delta)/delta,3/delta])
            bad_error = mp.norm(bad-expected,mp.inf)/mp.norm(expected,mp.inf)
            good_error = mp.norm(good-mp.matrix([1,0]),mp.inf)
            residual = mp.norm(L*bad+mp.matrix([0,1]),mp.inf)
            max_error = max(max_error,bad_error,good_error,residual)
            rows.append({'delta':mp.nstr(delta,30),
                         'bad_solution_norm_inf':mp.nstr(mp.norm(bad,mp.inf),30),
                         'good_solution_norm_inf':mp.nstr(mp.norm(good,mp.inf),30),
                         'bad_solution_relative_error':mp.nstr(bad_error,12),
                         'good_solution_absolute_error':mp.nstr(good_error,12),
                         'constraint_residual_inf':mp.nstr(residual,12)})
        if max_error >= mp.mpf('1e-60'):
            raise ArithmeticError('MPMATH_CONDITION_SWEEP_DISAGREES_WITH_EXACT_SOLUTION')
        return rows,mp.nstr(max_error,15)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report=symbolic_report()
    rows,error=condition_sweep()
    report['mpmath']={'decimal_precision':80,'rows':len(rows),
                      'max_exact_comparison_or_residual':error,'tolerance':'1e-60',
                      'scope':'dimensionless off-shell condition sweep only'}
    report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (args.output_dir/'EXCEPTIONAL_REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    with (args.output_dir/'CONDITION_SWEEP.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7.1,4.4))
    x=[float(r['delta']) for r in rows]
    ax.loglog(x,[float(r['bad_solution_norm_inf']) for r in rows],'-o',label='Incompatible limiting flux (0, 1)')
    ax.loglog(x,[float(r['good_solution_norm_inf']) for r in rows],'--s',label='Compatible flux (3, -1)')
    ax.set_xlabel(r'$\delta=\det(L_0 L)$')
    ax.set_ylabel(r'$\|L_0\Sigma_\perp\|_\infty$')
    ax.set_title('Near-exceptional algebraic constraint; not an evolution')
    ax.legend(fontsize=9)
    ax.grid(True,which='major',alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.output_dir/'EXCEPTIONAL_CONDITION.png',dpi=180)
    fig.savefig(args.output_dir/'EXCEPTIONAL_CONDITION.svg')
    plt.close(fig)
    (args.output_dir/'FIGURE_CAPTION.md').write_text(
        '# Condition sweep, algebraic diagnostic only\n\n'
        'All matrix entries are nondimensionalized with a fixed reference length L0: '
        'L0*L=[[-3,9-delta],[1,-3]], kappa_G*L0^2*q=(0,1) or (3,-1). '
        'For the incompatible limiting flux, L0*Sigma=((9-delta)/delta,3/delta); '
        'for the compatible flux, L0*Sigma=(1,0). The exact delta=0 branch is '
        'excluded from this logarithmic plot and is treated by Q*q=0 separately. '
        'No time history, matter EOS, near-A=0 accuracy, or cosmological solution is claimed. '
        'The constant curve can hide relative scale on a logarithmic axis; use the CSV for residuals. '
        'PNG/SVG are generated; direct image and reduced-print inspection remain pending.\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'exact_zero_count':report['exact_zero_count'],
                      'N22_zero_charts':2,'mpmath_rows':len(rows),'mpmath_max_error':error,
                      'first_sweep_row':rows[0],'last_sweep_row':rows[-1],
                      'plot_generated':True,'visual_audit':'PENDING_DIRECT_IMAGE_INSPECTION',
                      'native_runtime':'NOT_RUN'},sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
