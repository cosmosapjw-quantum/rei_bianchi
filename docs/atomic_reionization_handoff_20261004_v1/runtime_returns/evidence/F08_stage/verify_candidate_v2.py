"""Conditional-stage qualification; no F08 history/admission."""
import json,subprocess,importlib.util,hashlib
from pathlib import Path
from sage.all import RealIntervalField,matrix,vector
P=Path('.cuh/fastest-track/REI-F08-STAGE');R=RealIntervalField(200)
s=importlib.util.spec_from_file_location('frozen_nonphoto','docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F04_certificate/checker.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
fixture=json.loads((P/'fixture.json').read_text());manifest=json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text());constants=json.loads(Path('docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_map_constants.json').read_text())
for f,h in manifest['source_identity'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
lib=max(Path('rust/rei_microphysics/target/release/deps').glob('librei_microphysics-*.rlib'),key=lambda p:p.stat().st_mtime)
for name,test in [('native_tests',True),('root_probe',False)]:
 a=['rustc','--edition','2021','-O',str(P/(name+'.rs')),'--extern','rei_microphysics='+str(lib),'-L','dependency=rust/rei_microphysics/target/release/deps','-o',str(P/name)]
 if test:a.insert(1,'--test')
 subprocess.run(a,check=True)
 if test:subprocess.run([str(P/name)],check=True)
probe=subprocess.run([str(P/'root_probe')],check=True,capture_output=True,text=True);(P/'root_data.json').write_text(probe.stdout);data=json.loads(probe.stdout)
class Model(m.Model):
 def __init__(self):
  super().__init__(manifest,constants);self.sigma=[[R(0) for k in range(3)] for a in range(3)];self.photo_fhe=R(fixture['stage']['f_he']);self.sig=[[R(m.bits(fixture['sigma_bits'][3*a+k])) for k in range(3)] for a in range(3)]
 def coupled(self,y,pi):
  yy=list(y)+[R(1)]*3;f=super().rhs(yy);v=[m.J(x,i) for i,x in enumerate(yy)];one=m.J(R(1));dt=m.J(R(fixture['dt_s']));lower=[one-v[0],(one-v[1]-v[2])*self.photo_fhe,v[1]*self.photo_fhe];photons=[]
  for k in range(3):
   opacity=sum((lower[a]*self.sig[a][k] for a in range(3)),m.J(R(0)))*self.c*self.nh
   pn=m.J(pi[k])/(one+dt*opacity);photons.append(pn)
   rate=[lower[a]*self.c*self.nh*self.sig[a][k]*pn for a in range(3)]
   f[0]=f[0]+rate[0];f[1]=f[1]+(rate[1]-rate[2])/self.photo_fhe;f[2]=f[2]+rate[2]/self.photo_fhe
   for a in range(3):f[3]=f[3]+rate[a]*(R(fixture['energies_ev'][k])-self.chi[a])
  f[3]=f[3]-v[3]*R(2)*R(fixture['stage']['h_mean_per_s'])
  return f[:4],photons
model=Model();y=vector(R,[R(float(x)) for x in data['centre']]);Y=[R(float(a),float(b)) for a,b in data['gas']];Pgas=[R(float(a),float(b)) for a,b in data['parent_gas']];Pi=[R(float(a),float(b)) for a,b in data['parent_photons']]
for i in range(4):
 centre=R(m.bits(fixture['gas_center_bits'][i]));r=R(fixture['gas_radii'][i]);assert Pgas[i].lower()<=(centre-r).lower() and (centre+r).upper()<=Pgas[i].upper()
for i in range(3):
 centre=R(fixture['per_h'][i]);r=R(fixture['photon_radii'][i]);assert Pi[i].lower()<=(centre-r).lower() and (centre+r).upper()<=Pi[i].upper()
T=model.temperature([m.J(v) for v in list(Y)+[R(1)]*3]).v;assert R(30000).lower()<=T.lower() and T.upper()<=R(110000).upper()
F0,_=model.coupled(y,Pi);F,ph=model.coupled(Y,Pi);h=R(fixture['dt_s']);C=matrix(R,[[R(float(x)) for x in row] for row in data['C']]);I=matrix.identity(R,4);A=I-h*matrix(R,[[f.g[j] for j in range(4)] for f in F]);B=I-C*A
K=y-C*(y-vector(R,Pgas)-h*vector(R,[f.v for f in F0]))+B*(vector(R,Y)-y)
assert all(Y[i].lower()<K[i].lower() and K[i].upper()<Y[i].upper() for i in range(4)),'COUPLED_UNIFORM_KRAWCZYK'
q=max(sum(R(m.absmax(B[i,j])) for j in range(4)).upper() for i in range(4));assert q<1,'COUPLED_UNIFORM_CONTRACTION'
for k,pn in enumerate(ph):
 a,b=data['photons'][k];assert R(float(a)).lower()<=pn.v.lower() and pn.v.upper()<=R(float(b)).upper(),'OUTGOING_PHOTON_ENCLOSURE'
result={'status':'PASS','scope':'ConditionalactualFT03coupled4gas/eliminated3packetstage only','uniform_q':float(q),'temperature_box_K':[float(T.lower()),float(T.upper())],'precision_bits':200,'point_sample_proof':False,'F05_dependency':'NOT_CLOSED_BY_THIS_RECEIPT','F08_paired_history':'NOT_EXECUTED','physical_fit_error':'NOT_MEASURED','scientific_admission':'HOLD'};(P/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
