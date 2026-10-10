from pathlib import Path
import subprocess,tempfile
r=Path.cwd();lib=max((r/'rust/rei_microphysics/target/debug/deps').glob('librei_microphysics-*.rlib'),key=lambda p:p.stat().st_mtime_ns)
code='use rei_microphysics::{AtomicProvider,PhotonNode,homogeneous_photo_rates};fn main(){let p=AtomicProvider::reference();for (n,e,np) in [(1e-310,70.,1e300),(1e300,50000.,1e-240),(1e-304,70.,1e300),(1e300,13.6,1e-240)] {let q=homogeneous_photo_rates(&p,[n,0.,0.],1.,&[PhotonNode{energy_ev:e,n_comoving_per_cmpc3:np}]);println!("n={n:e} E={e} N={np:e} candidate={q:?}");assert!(q.is_err(),"precision-losing intermediate underflow must reject instead of returning inconsistent photon/species ledgers");}}'
with tempfile.TemporaryDirectory() as t:
 d=Path(t);(d/'main.rs').write_text(code);subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc','--edition','2021',str(d/'main.rs'),'--extern','rei_microphysics='+str(lib),'-L','dependency='+str(lib.parent),'-o',str(d/'check')],check=True);subprocess.run([str(d/'check')],check=True)
print('Four direct Rust opacity/gamma zero/subnormal ledger regressions PASS')
