"""Point-only original-owner and ACCEL03 response comparison; no ODE calls."""
import ast
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from kinetic import PreparedKinetic

path=ROOT/'vendor/reference_canonical_fv.py'
tree=ast.parse(path.read_text())
definitions=[n for n in tree.body if isinstance(n,ast.ClassDef)
             and n.name in ('FVMoments','CanonicalMomentumFV')]
assert len(definitions)==2
scope={'np':np,'math':math,'leggauss':leggauss,'dataclass':dataclass}
exec(compile(ast.Module(body=definitions,type_ignores=[]),str(path),'exec'),scope)
Owner=scope['CanonicalMomentumFV']
spec=importlib.util.spec_from_file_location('accel03',ROOT/'vendor/moment_response.py')
accel=importlib.util.module_from_spec(spec);spec.loader.exec_module(accel)
rows=[]
for A in (-.8,0.,.8):
    original=Owner(30.,A,12,12,gauss_order=3)
    prepared=PreparedKinetic(A,-A)
    for x,b in ((0.,0.),(.5,.04),(1.9,-.06)):
        old=original.moments(x,b);new=prepared.moments(x,b)
        differences={k:abs(new[k]-v) for k,v in
                     [('rho_m',old.rho),('pbar_m',old.pbar),('pi_m',old.pi_s)]}
        response=accel.moment_response(prepared.q2,prepared.mu2[0],
                                      prepared.weights,prepared.mass,x,b)
        differences['ACCEL03_J0']=abs(response['J0']-new['rho_m'])
        differences['ACCEL03_J2_over3']=abs(response['J2']/3-new['pi_m'])
        h=1e-5
        dpi_db=(prepared.moments(x,b+h)['pi_m']-
                prepared.moments(x,b-h)['pi_m'])/(2*h)
        derivative_relative=abs(dpi_db-response['J2_b']/3)/(abs(dpi_db)+1e-30)
        assert max(differences.values())<1e-14
        assert derivative_relative<1e-8
        rows.append({'A':A,'x':x,'b':b,'absolute_differences':differences,
                     'ACCEL03_derivative_relative':derivative_relative})
result={'status':'PASS','original_owner_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'ACCEL03_sha256':hashlib.sha256((ROOT/'vendor/moment_response.py').read_bytes()).hexdigest(),
        'comparisons':rows,'new_ODE':0,'scope':'same finite quadrature point values and exact response; not continuum certificate'}
target=ROOT/'verification/RETAINED_OWNER_COMPARISON.json'
target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','points':len(rows),'max_abs':max(max(r['absolute_differences'].values()) for r in rows),
                  'max_derivative_rel':max(r['ACCEL03_derivative_relative'] for r in rows),'new_ODE':0}))
