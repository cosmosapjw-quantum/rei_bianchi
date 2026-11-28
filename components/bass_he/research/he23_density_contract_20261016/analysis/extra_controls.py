import sys,math,json
from pathlib import Path
sys.path.insert(0,'/root/BASS_HE_HE23_DENSITY_20261016/research/he23_density_contract_20261016/src')
from he21_photo import N_H_Z20
from he22_native_client import NativeDensityProvider,NativeRustPoint,OWNER_SOURCE_SHA
from he22_coupled import run_coupled
from he22_contract import PhotoOnlyTestDouble
from run_native import atomic_json
w=Path('/root/HE23_NCP_DENSITY_20261016');out=w/'controls';out.mkdir(exist_ok=False)
provider=NativeDensityProvider(w/'build/he22_owner_point',OWNER_SOURCE_SHA,evidence_dir=out/'raw_sourcefree')
def density(a,x):return provider(a,x).nh
def native(a,x):return NativeRustPoint(w/'build/he22_owner_point',a,density(a,x),evidence_dir=out/'raw_sourcefree')
r=run_coupled(native,m=4,steps=2,q=0.,photons=False,density_provider=density)
assert abs(r['energy_defect'])<3e-12 and abs(r['number_defect'])<3e-15
assert max(abs(v) for v in r['chemical_species_defect'])<3e-12
atomic_json(out/'NATIVE_SOURCE_FREE.json',r)
# Controlled density impact only: both runs explicitly constructed photo-only owners,
# no deliberately inconsistent native density accepted and no native PASS inferred.
records=[]
for q in [-.005,0.,.005]:
 old=lambda a,x:N_H_Z20*math.exp(-3*x)
 total=lambda a,x:provider(a,x).nh
 def solve(d):return run_coupled(lambda a,x:PhotoOnlyTestDouble(d(a,x)),m=8,steps=4,q=q,density_provider=d)
 a,b=solve(old),solve(total)
 records.append({'q':q,'historical_photo_only':a,'total_density_photo_only':b,'absorbed_delta':[y-x for x,y in zip(a['absorbed'],b['absorbed'])],'heat_delta_ev':b['heat_ev']-a['heat_ev'],'scope':'constructed photo-only density-impact control, NOT native coupled physics or observational uncertainty'})
atomic_json(out/'DENSITY_IMPACT_PHOTO_ONLY.json',records)
print('native source-free + three photo-only density-impact controls PASS')
