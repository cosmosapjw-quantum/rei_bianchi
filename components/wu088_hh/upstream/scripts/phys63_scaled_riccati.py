"""Run the bounded PHYS63 actual-source Riccati response diagnostics."""
from pathlib import Path
import json
import numpy as np
from wu088_hh.phys63_scaled_riccati import solve_response, born_from_central_path, direct_fundamental_control
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
encode=lambda z: {'re':float(np.real(z)),'im':float(np.imag(z))}
rows=[]
for L,T,nodes,tol in [(21,39.,128,2e-11),(24,39.,128,2e-11),(28,39.,128,2e-11),(32,39.,128,2e-11),(28,35.,128,2e-11),(28,43.,192,2e-12)]:
    r=solve_response(SRC,ells=tuple(range(L+1)),outer=T,nodes=nodes,rtol=tol)
    born=born_from_central_path(r)
    d=r['delta']
    rows.append({'L':L,'m':0,'outer':T,'angular_nodes':nodes,'rtol':tol,
        'D21_20':encode(d[21,20]),'D20_20':encode(d[20,20]),
        'prior_mpmath_Born_reference':encode(2.7660422460123427e-24+4.500676730155306e-25j),
        'Born_quadrature_relative_difference':float(np.linalg.norm(d-born)/np.linalg.norm(born)),
        'transpose_defect':float(np.max(np.abs(d-d.T))),
        'nfev':r['nfev'],'solve_seconds_excluding_Coulomb_init':r['seconds'],
        'diagonal_addition_loses_small_response':bool(np.array_equal(np.diag(np.diag(r['central_z'])+d),r['central_z'])),
        'physical_nonlinear_remainder_resolved':False})
controls=[]
for m in (1,2):
    r=solve_response(SRC,ells=tuple(range(m,29)),m=m)
    controls.append({'m':m,'L':28,'D21_20':encode(r['delta'][21-m,20-m])})
a=solve_response(SRC,ells=(0,1),outer=33,strength=1e20)
b=direct_fundamental_control(SRC)
f=solve_response(SRC,ells=(0,1),outer=33,strength=1e20,nonlinear=False)
Z=np.diag(a['central_z'])+a['delta']
control={'scope':'MANUFACTURED_SCREEN_AMPLIFICATION_1e20_NOT_PHYSICAL',
 'Z_Riccati_minus_fundamental_max_abs':float(np.max(np.abs(Z-b['Z']))),
 'fundamental_current_transport_residual':b['flux_error'],
 'resolved_nonlinear_change_relative':float(np.linalg.norm(a['delta']-f['delta'])/np.linalg.norm(a['delta']))}
out={'schema':'PHYS63_SCALED_RICCATI_V1','parent_R5':'13a9d2cacedc84d9d23cd1193837de2c75f781b5',
 'source_sha256':a['source_sha256'],'energy_Hartree':'49/200','radial_spectral_parameter':'49/100',
 'rows':rows,'m_checks':controls,'independent_second_order_control':control,
 'scope':'FINITE_ANGULAR_PROJECTED_ORIGINAL_SCREEN_RADIAL_CUTOFF_NONCERTIFYING',
 'theorem_status':'qualitative infinite-angular on-shell existence from R5; no numerical constant inferred',
 'unproved':['validated angular/radial truncation error','physical nonlinear remainder below f64 relative resolution','original xi and scattering rate'],
 'HH_R10':'OFF','NCP':'NOT_REQUIRED'}
p=ROOT/'research/hh_phys63_20261018/c5c8/results/RICCATI_RESULTS.json'
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
