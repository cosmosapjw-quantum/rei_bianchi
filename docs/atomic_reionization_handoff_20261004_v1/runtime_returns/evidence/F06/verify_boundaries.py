from pathlib import Path
import subprocess
r=Path.cwd(); d=r/'.cuh/fastest-track/REI-F06'
lib=next((r/'rust/rei_microphysics/target/debug/deps').glob('librei_microphysics-*.rlib'))
binary='/tmp/rei-f06-boundary-regression'
subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc','--edition','2021',str(d/'boundary-regression.rs'),'--extern','rei_microphysics='+str(lib),'-L','dependency='+str(lib.parent),'-o',binary],check=True)
subprocess.run([binary],check=True)
