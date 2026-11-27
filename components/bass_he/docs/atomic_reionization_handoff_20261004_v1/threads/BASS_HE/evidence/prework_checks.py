"""Bounded algebra/units checks; no scientific collision or cosmology runtime."""
from decimal import Decimal, getcontext
from fractions import Fraction as F
import json
getcontext().prec=50
nu=(-1,1,0,1,-1,0)
H=(1,1,0,0,0,0); He=(0,0,1,1,1,0); charge=(0,1,0,1,2,-1)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
checks={"hydrogen_nuclei_dot_nu":dot(H,nu),"helium_nuclei_dot_nu":dot(He,nu),"charge_dot_nu":dot(charge,nu),"direct_electron_change":nu[-1]}
assert all(x==0 for x in checks.values())
chiH,chiHe1,chiHe2=F('13.6'),F('24.6'),F('54.4')
w=(0,chiH,0,chiHe1,chiHe1+chiHe2,0); Q=chiHe2-chiH
assert dot(w,nu)==-Q
for absorber,chi in [('HI',chiH),('HeI',chiHe1)]:
 residual=-Q+chi+(Q-chi)
 assert residual==0
 checks['OTS_'+absorber+'_rounded_energy_residual_eV']=str(residual)
checks['ground_defect_rounded_eV']=str(float(Q))
checks['GM25_to_KF96_ratio']=str(F('1.70e-13')/F('1e-14'))
assert checks['GM25_to_KF96_ratio']=='17'
assert F('1.70e-13')*F('1e-6')==F('1.70e-19')
assert F('1e-14')*F('1e-6')==F('1e-20')
checks['rate_cgs_to_si_factor']='1e-6'
ma=Decimal('4.001506179129'); mb=Decimal('1.00782503223')
mu=ma*mb/(ma+mb)
checks['C0_physical_mass_u_coefficient']=str(mu)
checks['integer_4_to_1_relative_difference']=str((mu-Decimal('.8'))/mu)
checks['mass_number_u_coefficient_4']=str(Decimal(4)*mb/(ma+mb))
# Exact SI kB and e; eV is e joules. This only illustrates the source grid gap.
kB=Decimal('1.380649e-23'); e=Decimal('1.602176634e-19')
kBT_eV=kB*Decimal(10000)/e
checks['kBT_at_1e4K_eV']=str(kBT_eV)
checks['Agueny_1keVu_Ecm_over_kBT_integer_mass_approx']=str(Decimal(800)/kBT_eV)
print(json.dumps({'schema':'bass-he.prework-checks.v1','status':'BOUNDED_ALGEBRA_AND_ARITHMETIC_CHECKED','checks':checks,'source_accuracy_certified':False,'B3_runtime_executed':False,'thermal_integration_executed':False,'consumer_integration_executed':False,'physical_history_executed':False,'energy_fixture':'rounded thresholds only; not production constants'},indent=2))
