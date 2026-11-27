"""Fresh-context data-layer check without importing the physical implementation."""
import csv,math,json,pathlib
r=pathlib.Path(__file__).resolve().parents[1];D=r/'data'
def load(name):
 with (D/name).open() as f:return list(csv.DictReader(f))
a=load('FASTD_INTEGRATED_50.csv');b=load('FLRW_IONIZED_HHE_5.csv');v=load('FASTD_VALIDATION_50.csv');s=load('FASTD_PROFILE_4050.csv');rates=load('FASTD_EPOCH_RATES_40.csv')
assert (len(a),len(b),len(v),len(s),len(rates))==(50,5,50,4050,40)
for row in a:
 x=lambda k:float(row[k])
 assert math.isclose(x('Q_e_MeV')+x('Q_p_MeV')+x('Q_alpha_MeV'),x('deltaK_MeV'),rel_tol=0,abs_tol=1e-8)
 assert math.isclose(x('K0_MeV')-x('K_terminal_MeV'),x('deltaK_MeV'),rel_tol=0,abs_tol=1e-13)
 assert math.isclose(x('tau_reference_p_1mb'),x('exposure_p_cm2')*1e-27,rel_tol=1e-12)
 assert math.isclose(x('stop_over_Hubble'),x('t_stop_s')*next(float(p['H_s']) for p in b if float(p['z'])==x('z')),rel_tol=1e-12)
 assert x('Q_e_MeV')>=0 and x('Q_ion_MeV')>=0
 assert x('stop_over_Hubble')<.002
for row in b:
 n=float(row['n_e_m3']);assert math.isclose(n,float(row['n_p_m3'])+2*float(row['n_a_m3']),rel_tol=1e-13)
for row in v:
 assert float(row['max_160_320_rel'])<1e-5
assert set(float(row['z']) for row in a)=={1e4,3e4,1e5,3e5,1e6}
print('PASS rows (background,integrals,rates,profiles,validation):',*(len(x) for x in (b,a,rates,s,v)))
print('PASS all energy conservation, neutrality, geometry, Hubble, quadrature, positive-transfer constraints')
