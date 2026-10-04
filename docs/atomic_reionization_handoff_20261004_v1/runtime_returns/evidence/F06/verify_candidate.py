from pathlib import Path
import subprocess,json
r=Path.cwd();d=r/'.cuh/fastest-track/REI-F06';cargo='/home/cosmosapjw/.cargo/bin/cargo';manifest='rust/rei_microphysics/Cargo.toml'
for test in ['bianchi_i','radiation_conservation']:subprocess.run([cargo,'test','--manifest-path',manifest,'--test',test,'--locked'],check=True)
print(json.dumps({'status':'PASS','scope':'R1 exact bounded geometry/positive packet remap only','scientific_admission':'HOLD'}))
