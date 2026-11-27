"""Independent tests across the material_exchange stdin boundary, from physical counts."""
import hashlib,json,math,pathlib,subprocess,sys
P=pathlib.Path(sys.argv[1]).resolve()
cell='CELL review 0 1 0.0001 0.00001 0.000001 0.5 0 0 0 1000 100 100'
rows=['cx new CX 0.5','ph new PHOT HI 1 20','cr new CR HI 2 6 0.003130800596','line new ESC 0.1 40.81332']
def run(rows,cell=cell):
  return subprocess.run([str(P)],input='\n'.join([cell,*rows])+'\n',text=True,capture_output=True,timeout=10)
r=run(rows);assert r.returncode==0,r.stderr
s={k:float(v) for k,v in (row.split() for row in r.stdout.splitlines())}
ke=1.380649e-23/1.602176634e-19; bh=13.598434599702
# Initially 111 heavy particles + 50 thermal electrons. One photoelectron thermalizes,
# two CR-ejected electrons are accounted separately. Charge exchange interchanges ions.
U0=1.5*ke*1000*161;U=U0+20-bh-.5*.0037
expected={'nHII_m3':52.5,'nDII_m3':.5,'electron_thermal_m3':51,'electron_fast_m3':2,'thermal_ev_m3':U,'T_K':U/(1.5*ke*162),'projectile_remaining_ev_m3':66.8,'photon_remaining_ev_m3':75.918668,'escaped_ev_m3':4.081332,'threshold_offset_ev_m3':.003130800596,'ionization_ev_m3':53*bh+.5*.0037,'born_kinetic_ev_m3':6}
for k,v in expected.items():assert math.isclose(s[k],v,rel_tol=5e-15,abs_tol=3e-13),(k,s[k],v)
assert abs(s['residual_ev_m3'])<2e-12
trials=[(['a new PHOT HI 1 13.599'],'SUBTHRESHOLD_PHOTON'),(['b owned PHOT HI 1 20'],'DUPLICATE_EVENT_OWNERSHIP'),(['a new PHOT HI 1 20','a new PHOT HI 1 20'],'DUPLICATE_EVENT_OWNERSHIP'),(['one new CX -0.5','two new CX 0.5'],'DEPLETED_STOCK')]
for r,reason in trials:
 t=run(r);assert t.returncode!=0 and reason in t.stderr,(r,reason,t.returncode,t.stderr)
w=run(['boundary new PHOT HI 0 13.599']);assert w.returncode==0
print(json.dumps({'binary_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'n_independent_scalar_checks':len(expected),'material_ledger_residual_ev_m3':s['residual_ev_m3'],'mixed_native_T_K':s['T_K'],'four_negative_cases':[r for _,r in trials],'zero_absorption_below_fit':True},indent=2))
