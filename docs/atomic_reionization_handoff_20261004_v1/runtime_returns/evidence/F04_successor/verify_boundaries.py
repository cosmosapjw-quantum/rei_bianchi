from pathlib import Path
import subprocess,json,tempfile
r=Path.cwd();d=r/'.cuh/fastest-track/REI-F04';cargo='/home/cosmosapjw/.cargo/bin/cargo';subprocess.run([cargo,'build','--manifest-path','rust/rei_microphysics/Cargo.toml','--locked'],check=True)
libs=list((r/'rust/rei_microphysics/target/debug/deps').glob('librei_microphysics-*.rlib'));lib=max(libs,key=lambda p:p.stat().st_mtime_ns)
with tempfile.TemporaryDirectory(prefix='rei-f04-underflow-') as t:
 binary=Path(t)/'probe';subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc','--edition=2021',str(d/'review-probe.rs'),'--extern','rei_microphysics='+str(lib),'-L','dependency='+str(lib.parent),'-o',str(binary)],check=True);subprocess.run([str(binary)],check=True)
