import dataclasses,hashlib,json,math,sys,unittest
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));import photon_dd as m
D=Decimal;PI=D('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986');A=D('3727.3794118');M=D('1875.61294500');N=(0.,0.,1.);CONV=m.CONVENTION

def dsin(x):
 term=x;total=x
 for i in range(1,80):
  term=-term*x*x/D((2*i)*(2*i+1));total+=term
  if abs(term)<D('1e-78'):break
 return total
def dcos(x):
 term=D(1);total=term
 for i in range(1,80):
  term=-term*x*x/D((2*i-1)*(2*i));total+=term
  if abs(term)<D('1e-78'):break
 return total
def reference(a,mass,e,theta):
 # Independent literal-based CM four-vector and direct Lorentz matrix along z.
 with localcontext() as c:
  c.prec=80;a=D(str(a));mass=D(str(mass));e=D(str(e));theta=D(str(theta))*PI/D(180);w=(a*a+2*a*e).sqrt();es=w/2;k=(es*es-mass*mass).sqrt();beta=e/(a+e);gamma=1/(1-beta*beta).sqrt();ux=dsin(theta);uz=dcos(theta)
  out=[]
  for sign in (D(1),D(-1)):
   ex=gamma*(es+beta*sign*k*uz);q=(sign*k*ux,D(0),gamma*(sign*k*uz+beta*es));kin=ex-mass;stress=tuple(tuple(q[i]*q[j]/ex for j in range(3)) for i in range(3));out.append((ex,q,kin,stress))
  return out
class PhotonControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.packet=m.source_rows();cls.rows=cls.packet['raw_values']['rows']
 def event(self,index=0,phi=0):return m.native_event(index+1,phi,0.,mass_convention=CONV)['event']
 def approx(self,x,y,scale=4000):self.assertLessEqual(abs(float(x)-float(y)),5e-13*abs(float(y))+64*sys.float_info.epsilon*scale)
 def test_01_source_identity(self):
  raw=(ROOT/'sources/NIST_CODATA_2022_allascii.txt').read_bytes();self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(40801,'77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67'));self.assertEqual(len(self.rows),12);self.assertEqual(self.packet['units'],{'EN':'MEV','ANG-CM':'ADEG','DATA-CM':'NB/SR','ERR-S':'NB/SR'})
 def test_02_literal_mass(self):
  lines=(ROOT/'sources/NIST_CODATA_2022_allascii.txt').read_text().splitlines();self.assertIn('3727.379 4118',lines[14]);self.assertIn('1875.612 945 00',lines[87]);d=json.loads((ROOT/'MODEL_CONTRACT.json').read_text())['canonical_mass_inputs'];self.assertEqual((d['alpha_rest_MeV'],d['deuteron_rest_MeV'],d['alpha_printed_standard_uncertainty_MeV'],d['deuteron_printed_standard_uncertainty_MeV']),('3727.3794118','1875.61294500','0.0000012','0.00000058'));self.assertIsNone(d['covariance'])
 def test_03_threshold(self):
  with localcontext() as c:
   c.prec=80;delta=2*M-A;eth=(4*M*M-A*A)/(2*A);e=self.event();self.approx(e.rest_deficit,delta);self.approx(e.threshold,eth)
   with self.assertRaises(m.ContractError):m.kernel(float(A),float(M),float(delta),N,N)
 def test_04_native_fourvectors(self):
  for i,row in enumerate(self.rows):
   v=row['values'];ev=self.event(i);ref=reference(A,M,v['EN'],v['ANG-CM'])
   for x,y in zip((ev.plus,ev.minus),ref):
    self.approx(x.energy,y[0]);[self.approx(a,b) for a,b in zip(x.momentum_energy,y[1])]
 def test_05_mass_shells(self):
  for i in range(12):
   ev=self.event(i)
   for p in (ev.plus,ev.minus):self.assertLessEqual(abs(p.energy**2-sum(x*x for x in p.momentum_energy)-ev.M**2),256*sys.float_info.epsilon*(p.energy**2+sum(x*x for x in p.momentum_energy)+ev.M**2))
 def test_06_conservation(self):
  for i in range(12):
   ev=self.event(i);eps=sys.float_info.epsilon;energy_terms=(ev.plus.energy,ev.minus.energy,-ev.A,-ev.photon_energy);self.assertLessEqual(abs(math.fsum(energy_terms)),256*eps*sum(abs(x) for x in energy_terms))
   for j in range(3):
    terms=(ev.plus.momentum_energy[j],ev.minus.momentum_energy[j],-ev.photon_energy*ev.n[j]);self.assertLessEqual(abs(math.fsum(terms)),256*eps*sum(abs(x) for x in terms))
   # Mutation witnesses: omitting incoming photon momentum or a daughter is detectable.
   self.assertGreater(abs(ev.plus.momentum_energy[2]+ev.minus.momentum_energy[2]),256*eps*(ev.plus.energy+ev.minus.energy+ev.A+ev.photon_energy));self.assertGreater(abs(ev.plus.energy-ev.A-ev.photon_energy),256*eps*(ev.plus.energy+ev.A+ev.photon_energy))
 def test_07_rotation(self):
  n=(0.6,0.8,0.0);u=(0.0,0.6,0.8);rot=lambda v:(v[2],v[0],v[1]);order=(2,0,1);e=m.kernel(float(A),float(M),213,n,u);r=m.kernel(float(A),float(M),213,rot(n),rot(u))
  for x,y in ((e.plus,r.plus),(e.minus,r.minus)):
   self.approx(x.energy,y.energy)
   for i in range(3):
    self.approx(y.momentum_energy[i],x.momentum_energy[order[i]])
    for j in range(3):self.approx(y.stress[i][j],x.stress[order[i]][order[j]],400)
 def test_08_exchange(self):
  x=m.kernel(float(A),float(M),213,N,(0.6,0.,0.8));y=m.kernel(float(A),float(M),213,N,(-0.6,0.,-0.8));self.assertEqual(x.plus,y.minus);self.assertEqual(x.minus,y.plus);self.assertEqual(x.material_stress,y.material_stress)
 def test_09_azimuth(self):
  x=self.event(0,0);y=self.event(0,math.pi/2);self.approx(x.plus.energy,y.plus.energy);self.approx(x.plus.momentum_energy[0],y.plus.momentum_energy[1]);self.approx(y.plus.momentum_energy[0],0)
 def test_10_threshold(self):
  x=m.kernel(2,2,3,N,N);self.assertEqual((x.threshold,x.kappa),(3.,0.))
  for daughter in (x.plus,x.minus):
   self.assertEqual(daughter.energy,2.5);self.assertEqual(daughter.momentum_energy,(0.,0.,1.5));self.assertEqual(daughter.kinetic,0.5)
  self.assertEqual(x.plus.momentum_energy[2]+x.minus.momentum_energy[2],3.)
  # Rest deficit alone omits threshold recoil and is not an admissible event.
  self.assertEqual(x.rest_deficit,2.);self.assertGreater(x.threshold,x.rest_deficit)
  with self.assertRaises(m.ContractError):m.kernel(2,2,math.nextafter(3,0),N,N)
  with self.assertRaises(m.ContractError):m.kernel(2,2,x.rest_deficit,N,N)
 def test_11_near_threshold(self):
  e=3+2**-20;x=m.kernel(2,2,e,N,(1.,0.,0.));rr=reference(2,2,str(e),90);self.approx(x.plus.energy,rr[0][0],10);self.approx(x.plus.momentum_energy[0],rr[0][1][0],10)
 def test_12_scalar_domain(self):
  for a,mass,e in ((0,2,3),(-1,2,3),(4,2,3),(2,0,3),(2,2,0),(True,2,3),(2,float('nan'),3),(2,2,float('inf'))):
   with self.assertRaises(m.ContractError):m.kernel(a,mass,e,N,N)
 def test_13_vector_domain(self):
  for n,u in [((0,0),N),((0,0,2),N),(N,(0,False,1)),(N,(0,0,float('nan')))]:
   with self.assertRaises(m.ContractError):m.kernel(2,2,3,n,u)
 def test_14_representation(self):
  with self.assertRaises(m.ContractError):m.kernel(1e308,1e308,1e308,N,N)
  with self.assertRaises(m.ContractError):m.kernel(5e-324,1,3,N,N)
  with self.assertRaises(m.ContractError):m.kernel(2,2,5e-324,N,N)
  with self.assertRaises(m.ContractError):m.adapter(2,2,4,N,N,1e308,mass_convention='SYNTHETIC_CONTROL')
  with self.assertRaises(m.ContractError):m.adapter(2,2,4,N,N,5e-324,mass_convention='SYNTHETIC_CONTROL')
 def test_15_count(self):
  s=m.adapter(2,2,4,N,N,3,mass_convention='SYNTHETIC_CONTROL');self.assertEqual((s['Gamma_photon'],s['Gamma_alpha'],s['Gamma_deuteron'],s['material_count']),(-3,-3,6,3));self.assertEqual(-4*3+2*6,0);self.assertEqual(-2*3+6,0)
 def test_16_energy_owner(self):
  for f in (0,1e6):
   s=m.adapter(float(A),float(M),213,N,(0.6,0.,0.8),f,mass_convention=CONV);self.approx(s['photon_energy_source_W_m3']+s['population_rest_energy_witness_W_m3']+s['material_kinetic_source_W_m3'],0,1e-4)
   if f:self.assertGreater(abs(s['photon_energy_source_W_m3']+2*s['population_rest_energy_witness_W_m3']+s['material_kinetic_source_W_m3']),64*sys.float_info.epsilon*(abs(s['photon_energy_source_W_m3'])+abs(s['material_kinetic_source_W_m3'])))
 def test_17_SI_conversions(self):
  f=1e6;s=m.adapter(2,2,4,N,N,f,mass_convention='SYNTHETIC_CONTROL')
  with localcontext() as c:
   c.prec=80;self.approx(s['photon_energy_source_W_m3'],float(-D(4)*D('1e6')*D('1.602176634e-13')),1e-6);self.approx(s['photon_momentum_source'][2],float(-D(4)*D('1e6')*D('1.602176634e-13')/D('299792458')),1e-15)
 def test_18_stress_trace(self):
  e=self.event();
  for p in (e.plus,e.minus):self.approx(sum(p.stress[i][i] for i in range(3)),p.energy-e.M**2/p.energy);self.assertNotEqual(p.stress[0][0],p.momentum_energy[0]**2)
 def test_19_stress_reference(self):
  for i,row in enumerate(self.rows):
   e=self.event(i);v=row['values'];r=reference(A,M,v['EN'],v['ANG-CM'])
   for p,ref in zip((e.plus,e.minus),r):
    for j in range(3):
     for k in range(3):self.approx(p.stress[j][k],ref[3][j][k],400)
  n=(0.6,0.8,0.);u=(0.,0.6,0.8);rot=lambda v:(v[2],v[0],v[1]);order=(2,0,1);a=m.kernel(float(A),float(M),213,n,u);b=m.kernel(float(A),float(M),213,rot(n),rot(u))
  for x,y in ((a.plus,b.plus),(a.minus,b.minus)):
   for j in range(3):
    self.approx(y.momentum_energy[j],x.momentum_energy[order[j]])
    for k in range(3):self.approx(y.stress[j][k],x.stress[order[j]][order[k]],400)
 def test_20_NR(self):
  for i in range(12):
   e=self.event(i)
   for p in (e.plus,e.minus):self.approx(sum(x*x for x in p.momentum_energy)/(2*e.M)-p.kinetic,p.nr_excess,200)
 def test_21_native_observables(self):
  observed=json.loads((ROOT/'sources/PHOTON05_SOURCE_OBSERVATIONS.json').read_text())['EXFOR_reused_packet']['source_rows'];self.assertEqual(len(observed),12)
  for i,row in enumerate(self.rows):
   self.assertEqual(row['values'],observed[i]['values']);self.assertEqual(row['source_row_1based'],observed[i]['source_row_1based'])
   n=m.native_event(i+1,0,0,mass_convention=CONV);self.assertEqual(n['values'],row['values']);self.assertEqual(n['source_row'],row['source_row_1based']);self.assertEqual(n['units'],self.packet['units']);self.assertFalse(n['DCS_or_ERROR_used_as_event_flux']);self.assertFalse(n['half_factor_applied'])
  self.assertEqual((self.rows[0]['values']['DATA-CM'],self.rows[0]['values']['ERR-S']),('0.22','0.04'))
 def test_22_zero_flux_validation(self):
  for row,phi,conv in ((0,0,CONV),(True,0,CONV),(1,float('nan'),CONV),(1,0,'wrong')):
   with self.assertRaises(m.ContractError):m.native_event(row,phi,0,mass_convention=conv)
  with self.assertRaises(m.ContractError):m.adapter(2,2,2,N,N,0,mass_convention='SYNTHETIC_CONTROL')
  with self.assertRaises(m.ContractError):m.adapter(2,2,4,N,N,0,mass_convention=CONV)
  with self.assertRaises(m.ContractError):m.native_event(1,0,0,mass_convention='SYNTHETIC_CONTROL')
 def test_23_null_ownership(self):
  s=m.adapter(2,2,4,N,N,1,mass_convention='SYNTHETIC_CONTROL')
  for k in ('independent_binding_rhs','Gamma_thermal','Cv','species_heating','thermal_deposition','global_species_ID_mapping'):self.assertIsNone(s[k])
  self.assertEqual(s['birth_pool'],'UNASSIGNED');self.assertFalse(s['physical_global_consumer_admitted']);self.assertFalse(s['physical_rate_admitted']);self.assertEqual(s['mass_convention'],'SYNTHETIC_CONTROL');self.assertTrue(s['synthetic_control']);physical=m.native_event(1,0,0,mass_convention=CONV)['source'];self.assertEqual(physical['mass_convention'],CONV);self.assertFalse(physical['synthetic_control'])
 def test_24_saved_native(self):
  results=[]
  for i in range(12):
   d=m.native_event(i+1,0.,0.,mass_convention=CONV);ev=d.pop('event');d['event']=dataclasses.asdict(ev);d['same_momentum_NR_relative_excess']=[x.nr_excess/x.kinetic for x in (ev.plus,ev.minus)];d['four_momentum_residual']=[ev.plus.energy+ev.minus.energy-ev.A-ev.photon_energy]+[ev.plus.momentum_energy[j]+ev.minus.momentum_energy[j]-ev.photon_energy*ev.n[j] for j in range(3)];shell=[x.energy**2-sum(q*q for q in x.momentum_energy)-ev.M**2 for x in (ev.plus,ev.minus)];scale=[x.energy**2+sum(q*q for q in x.momentum_energy)+ev.M**2 for x in (ev.plus,ev.minus)];d['mass_shell_residuals']=shell;d['mass_shell_max_normalized_residual']=max(abs(v)/a for v,a in zip(shell,scale));results.append(d)
  synthetic=dataclasses.asdict(m.kernel(2,2,3,N,N));flux=m.adapter(2,2,4,N,N,1,mass_convention='SYNTHETIC_CONTROL');p=ROOT/'evidence/validation/SAVED_PLOT_DATA.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'source':'EXFOR_M0475002','native_phi_rad':0,'native':results,'synthetic_threshold':synthetic,'synthetic_near_threshold':dataclasses.asdict(m.kernel(2,2,3+2**-20,N,(1.,0.,0.))),'synthetic_unit_flux':flux,'physical_rate_admitted':False},indent=2)+'\n')
