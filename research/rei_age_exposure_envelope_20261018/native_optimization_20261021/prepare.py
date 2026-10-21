"""Generate an opt-in native V10 overlay, preserving all immutable donor files."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile,subprocess,os
HERE=Path(__file__).resolve().parent;TASK=HERE.parent
sys.path.insert(0,str(TASK/'src'))
from prepare_native import prepare as base_prepare
from run_refinement import sha,save
from native_inputs import load_manifest

def replace(text,old,new):
    if text.count(old)!=1:raise ValueError('OVERLAY_ANCHOR:'+old[:70])
    return text.replace(old,new,1)

def restore(dest,repo=None,c10=None):
    manifest=load_manifest(TASK)
    if dest.exists():
        for name,row in manifest['files'].items():
            if sha(dest/name)!=row['sha256']:raise ValueError('RESTORED_INPUT_CHANGED:'+name)
        return dest
    payloads={}
    with zipfile.ZipFile(c10) if c10 else __import__('contextlib').nullcontext() as archive:
        for name,row in manifest['files'].items():
            if archive:data=archive.read('archive_only/runtime_base/native_original_35d9747/'+name)
            else:data=subprocess.check_output(['git','-C',str(repo),'show',manifest['native_sha']+':'+name],env=dict(os.environ,GIT_NO_LAZY_FETCH='1'))
            if len(data)!=row['size'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('FROZEN_INPUT:'+name)
            payloads[name]=data
    for name,data in payloads.items():
        p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return dest

def generate(inputs,dest):
    if dest.exists():raise ValueError('PREPARED_DEST_MUST_BE_ABSENT')
    identity=base_prepare(TASK,dest,native_input_dir=inputs)
    core=dest/'rust/rei_microphysics/src/axbi_covariant_transport.rs';s=core.read_text()
    anchor='        return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));'
    injection='''        if std::env::var("REI_SUBNORMAL_REPAIR").ok().as_deref()==Some("subnormal-barycenter") {
            if let Some(nodes)=rei_barycenter(lo,hi,n,u,energy_scale) {
                let cd=(sum(nodes.iter().map(|x|x.1))-n).abs();
                let ed=(sum(nodes.iter().map(|x|x.0*x.1))-u).abs();
                let count=REI_REPAIRS.fetch_add(1,std::sync::atomic::Ordering::Relaxed)+1;
                REI_MAX_REPAIRED_BITS.fetch_max(n.to_bits(),std::sync::atomic::Ordering::Relaxed);
                if count==1 {eprintln!("REI_BARYCENTER_FIRST n_bits={:016x} u_bits={:016x} lo_bits={:016x} hi_bits={:016x} q_bits={:016x} old_count={:.17e} new_count={:.17e} old_energy={:.17e} new_energy={:.17e} count_gate={:.17e} energy_gate={:.17e}",n.to_bits(),u.to_bits(),lo.to_bits(),hi.to_bits(),nodes[0].0.to_bits(),count_defect,cd,energy_defect,ed,64.0*f64::EPSILON*n,128.0*f64::EPSILON*energy_scale);}
                diagnostics.max_count_relative_defect=diagnostics.max_count_relative_defect.max(cd/n);
                diagnostics.max_energy_relative_defect=diagnostics.max_energy_relative_defect.max(ed/energy_scale);
                return Ok(nodes);
            }
        }
'''
    s=replace(s,anchor,injection+anchor)+(HERE/'accessors.rs').read_text();core.write_text(s)
    owner=dest/'rust/rei_microphysics/examples/matrix_owner.rs';s=owner.read_text()
    s=replace(s,'    prepared: Vec<PreparedAbsorption>,','    prepared: std::sync::Arc<Vec<PreparedAbsorption>>,')
    old='''        for p in &self.prepared {
            let r = p.evaluate(absorbers, nh, dt)?;'''
    s=replace(s,old,'''        let results=self.d.transport.rei_ordered_cohort_evaluate(std::sync::Arc::clone(&self.prepared),absorbers,nh,dt)?;
        for r in results {''')
    s=replace(s,'    let context = Context { d, old, prepared };','    let context = Context { d, old, prepared:std::sync::Arc::new(prepared) };')
    s=replace(s,'            return Ok(next);','            rei_observe_accepted(&context,&next,dt)?;\n            return Ok(next);')
    for side in ('false','true'):
        old=f'            t.push((x, {side}, s.clone()));'
        s=replace(s,old,f'''            if std::env::var_os("REI_FULL_TRACE").is_some() || common_mesh(old.gas_owner.a,to,&[8],1).iter().any(|v|v.to_bits()==x.to_bits()) {{
                t.push((x, {side}, s.clone()));
            }}''')
    s+='\n'+(HERE/'observer.rs').read_text();owner.write_text(s)
    native=dest/'rust/rei_microphysics/examples/positive_native.rs';s=native.read_text().replace('.clamp(1, 48);','.clamp(1, 64);')
    # Always report repair totals on normal return and error unwind from main.
    anchor='fn main() -> Result<(), Box<dyn std::error::Error>> {'
    guard='''struct ReiStatsGuard;
impl Drop for ReiStatsGuard {fn drop(&mut self) {let (count,max_bits)=rei_microphysics::axbi_covariant_transport::rei_repair_stats();eprintln!("REI_REPAIR_TOTAL count={} maximum_mass_bits={:016x}",count,max_bits);}}
'''
    s=replace(s,anchor,guard+anchor+'\n    let _rei_stats=ReiStatsGuard;');native.write_text(s)
    identity.update(schema='rei.native_v10.prepared.v1',v10_options='parallel-order-preserving;compact-trace;opt-in-barycenter;accepted-BE-observer',source_files={p.name:sha(p) for p in [HERE/'prepare.py',HERE/'accessors.rs',HERE/'observer.rs']})
    for name in identity['outputs']:identity['outputs'][name]=sha(dest/name)
    save(dest/'PREPARED_IDENTITY.json',identity);return identity

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--repo',type=Path);p.add_argument('--c10',type=Path)
    a=p.parse_args()
    if bool(a.repo)==bool(a.c10):p.error('choose exactly one offline source --repo or --c10')
    inputs=restore(a.runtime/'native153',a.repo,a.c10);r=generate(inputs,a.runtime/'prepared');print(json.dumps(dict(status='PREPARED_NO_PHYSICS',files=len(r['outputs']))))
if __name__=='__main__':main()
