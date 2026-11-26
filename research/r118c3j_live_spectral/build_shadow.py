"""Create a source-pinned disposable shadow; original native source never edited."""
import hashlib,subprocess,json,tarfile,io,sys
from pathlib import Path
D=Path(__file__).resolve().parent
REPO=D.parents[1]
BASE='d2d58e839a6bf5cdfe370da8937459b56c561ebd'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(root):
 root=Path(root);root.mkdir(exist_ok=False)
 # Exact Git archive, not current working copy. Include external compile-time source dependencies.
 paths=['rust/rei_microphysics','docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json','research/flrw_jacobian_columns_20261016/CONTRACT.json','research/r118c3b_ff_balance/gauntff.dat','research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json','research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md','research/flrw_covariant_transport_20261015']
 archive=subprocess.check_output(['git','-C',str(REPO),'archive',BASE,*paths])
 with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(root,filter='data')
 crate=root/'rust/rei_microphysics';p=crate/'src/spectral_ff.rs';orig={}
 orig[str(p.relative_to(root))]=sha(p)
 p.write_text(p.read_text()+'\n'+(D/'compton_impl.rs').read_text())
 q=crate/'src/axbi_covariant_driver.rs';orig[str(q.relative_to(root))]=sha(q);s=q.read_text()
 old='let q=sp.advance(eos.temperature_k,tc,frac,point.rhs.freefree_thermal_sink_erg_cm3_s*dt/(nh*c.ev_erg),bb,false)?;'
 assert s.count(old)==1
 s=s.replace(old,'''// C3J SHADOW ONLY: signed spectral Compton in same candidate as chemistry and FF.
            let clock=8.617333262145e-5*eos.temperature_k/510998.9499961642*299792458.*6.6524587051e-29*eos.electron_density_cm3*1e6*dt;
            let c1=sp.advance_compton(eos.temperature_k/tc,clock/2.,bb)?;
            let q=sp.advance(eos.temperature_k,tc,frac,point.rhs.freefree_thermal_sink_erg_cm3_s*dt/(nh*c.ev_erg),bb,false)?;
            let c2=sp.advance_compton(eos.temperature_k/tc,clock/2.,bb)?;
            let new_heat=-(c1+c2)*nh*c.ev_erg/dt;
            let change=new_heat-point.rhs.cmb_to_gas_erg_cm3_s;
            point.rhs.cmb_to_gas_erg_cm3_s=new_heat;
            point.rhs.thermal_micro_erg_cm3_s+=change;
            point.rhs.w_dt_erg_per_h_s+=change/nh;
            point.rhs.temperature_dt_k_s+=2.*change/(3.*c.kb_erg_k*(nh+nhe+eos.electron_density_cm3));
''')
 a=s.index('    pub fn external_trial_report(&self');b=s.index('    pub fn ff_spectral_energy',a)
 block=s[a:b];assert 'Ok((fine,comp))' in block
 split=block.replace('pub fn external_trial_report','pub fn c3j_trial_split',1).replace('Result<(DriverState,ErrorComponents),ForwardError>','Result<(DriverState,DriverState,ErrorComponents),ForwardError>',1).replace('Ok((fine,comp))','Ok((first,fine,comp))')
 s=s[:b]+split+s[b:];q.write_text(s)
 # Add research-only executable in the shadow crate.
 f=crate/'examples/c3j_live.rs';f.write_bytes((D/'live.rs').read_bytes())
 manifest=dict(base=BASE,archive_sha=hashlib.sha256(archive).hexdigest(),original_sha=orig,patched_sha={x:sha(root/x) for x in orig},example_sha=sha(f))
 (D/'SHADOW_ID.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(manifest,flush=True)
if __name__=='__main__':build(sys.argv[1])
