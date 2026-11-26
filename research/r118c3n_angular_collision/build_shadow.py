"""Construct C3K source-pinned shadow, add signed spectrum acceptance to native split."""
import sys,hashlib,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
def build(root):
 root=Path(root)
 # Use original C3J builder logic but redirect D and source base to this cycle.
 prior=D.parent/'r118c3j_live_spectral'
 s=(prior/'build_shadow.py').read_text().replace("BASE='d2d58e839a6bf5cdfe370da8937459b56c561ebd'","BASE='c8a7fdec40971349bff082f82a39b5d75d04efb3'")
 ns={'__file__':str(D/'build_shadow.py'),'__name__':'c3k_shadow'}
 # Builder needs C3J implementation and example, archived source references in this directory.
 exec(s,ns);ns['build'](root)
 crate=root/'rust/rei_microphysics';p=crate/'src/axbi_covariant_driver.rs';s=p.read_text()
 a=s.index('    pub fn c3j_trial_split');b=s.index('    pub fn ff_spectral_energy',a)
 block=s[a:b]
 block=block.replace('Result<(DriverState,DriverState,ErrorComponents),ForwardError>','Result<(DriverState,DriverState,ErrorComponents,[f64;2]),ForwardError>')
 old='let metric=comp.legacy_metric().max(comp.rate_metric());'
 new='''let mut specerr=[0.;2];
        if let (Some(f),Some(g))=(&full.ff_spectrum,&fine.ff_spectrum){
            if f.nodes()!=g.nodes(){return Err(err("C3K_SPECTRAL_GRID"))}
            let x=f.nodes();let dl=(x[1]/x[0]).ln();
            let bb=crate::spectral_ff::blackbody_per_h(2.7255/fine.a,self.n_h0_cm3/fine.a.powi(3))?*15./std::f64::consts::PI.powi(4);
            let mut d=[0.;2];let mut n=[0.;2];let mut m=[0.;2];
            for (i,&v) in x.iter().enumerate(){
                let w=[v.powi(3)*dl,bb*v.powi(4)*dl];
                let a=f.distortion()[i];let b=g.distortion()[i];
                for k in 0..2{d[k]+=w[k]*(a-b).abs();n[k]+=w[k]*a.abs();m[k]+=w[k]*b.abs();}
            }
            specerr=[d[0]/n[0].max(m[0]).max(1e-14),d[1]/n[1].max(m[1]).max(1e-8)];
        }else if full.ff_spectrum.is_some()!=fine.ff_spectrum.is_some(){return Err(err("C3K_SPECTRAL_STATE"))}
        let metric=comp.legacy_metric().max(comp.rate_metric()).max(specerr[0]).max(specerr[1]);'''
 assert old in block;block=block.replace(old,new).replace('Ok((first,fine,comp))','Ok((first,fine,comp,specerr))')
 s=s[:a]+block+s[b:];p.write_text(s)
 # Standalone cargo package references native BASS and pinned REI shadow.
 bridge=root/'bridge';(bridge/'src').mkdir(parents=True)
 bass=Path.home()/'worktrees/bass-r109-native-20261124/_rustcore'
 (bridge/'Cargo.toml').write_text('[package]\nname="c3n_angular_bridge"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nbianchi_rustcore={path="'+str(bass)+'"}\nrei_microphysics={path="../rust/rei_microphysics"}\n[workspace]\n[profile.release]\nopt-level=3\nlto="thin"\ncodegen-units=1\n')
 (bridge/'src/main.rs').write_bytes((D/'metric_bridge.rs').read_bytes());(bridge/'src/frequency.rs').write_bytes((D/'frequency.rs').read_bytes())
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 manifest=json.loads((D/'SHADOW_ID.json').read_text());manifest['patched_sha']['rust/rei_microphysics/src/axbi_covariant_driver.rs']=sha(p);manifest['bridge_sha']=sha(bridge/'src/main.rs');manifest['frequency_sha']=sha(bridge/'src/frequency.rs');(D/'SHADOW_ID.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':build(sys.argv[1])
