from pathlib import Path
import tempfile,subprocess,json,sys
r=Path.cwd();d=r/'.cuh/fastest-track/REI-F03';work=Path(tempfile.mkdtemp(prefix='rei-f03-boundary-'))
src=r'.cuh/fastest-track/REI-F03/boundaries.rs'
lib=r/'rust/rei_microphysics/target/debug/librei_microphysics.rlib'
subprocess.run(['/home/cosmosapjw/.cargo/bin/cargo','build','--manifest-path','rust/rei_microphysics/Cargo.toml','--lib','--locked'],check=True)
subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc','--edition','2021',str(src),'--extern',f'rei_microphysics={lib}','-L',str(lib.parent/'deps'),'-o',str(work/'boundaries')],check=True)
p=subprocess.run([str(work/'boundaries')],capture_output=True,text=True);print(p.stdout,end='');print(p.stderr,end='',file=sys.stderr)
(d/'boundary-result.json').write_text(p.stdout);sys.exit(p.returncode)
