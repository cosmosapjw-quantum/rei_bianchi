"""Exact PR378 integrated subset with C3U source patch and C3V DG owner.
No PR branch or production source mutation.
"""
from pathlib import Path
import sys,hashlib,json,subprocess,tarfile,io,shutil
D=Path(__file__).resolve().parent;P=D.parent/'r118c3u_positive_owner';ROOT=D.parents[1];BASE='b145729be3d9d103ef1379c9efe5f85687558bc6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root):
 root=Path(root)
 # Reuse verified C3U patch builder, pin host base to integrated PR.
 s=(P/'build_shadow.py').read_text().replace('a3cd7cdc3e7cf7c9059c3c420338bdd1d60d0b15',BASE).replace('c3u_birth_bridge','c3x_dg_bridge')
 ns={'__file__':str(D/'build_shadow.py'),'__name__':'c3v_host'};exec(s,ns);ns['build'](root)
 ar=subprocess.check_output(['git','-C',str(ROOT),'archive',BASE,'components/bass_rec/bass','components/bass_rec/rec'])
 with tarfile.open(fileobj=io.BytesIO(ar)) as t:t.extractall(root,filter='data')
 a=subprocess.check_output(['git','-C',str(ROOT),'archive',BASE,'src/rei_bianchi/microphysics/data/savin2002_charge_exchange.csv'])
 with tarfile.open(fileobj=io.BytesIO(a)) as t:t.extractall(root,filter='data')
 bridge=root/'bridge';p=bridge/'Cargo.toml';s=p.read_text();old=Path.home()/'worktrees/bass-r109-native-20261124/_rustcore'
 assert str(old) in s;s=s.replace(str(old),'../components/bass_rec/bass/_rustcore');p.write_text(s)
 for n in ['dg.rs','dg_rhs.cpp','build.rs']:shutil.copyfile(D/n,bridge/('src' if n=='dg.rs' else '')/n)
 j=D/'SHADOW_ID.json';v=json.loads(j.read_text());v.update(savin_archive_sha=hashlib.sha256(a).hexdigest(),savin_sha=sha(root/'src/rei_bianchi/microphysics/data/savin2002_charge_exchange.csv'),integrated_archive_sha=hashlib.sha256(ar).hexdigest(),integrated_bass_owned_thomson_sha=sha(root/'components/bass_rec/bass/_rustcore/src/kinetic/owned_thomson.rs'),bridge_manifest_sha=sha(p),dg_sha=sha(bridge/'src/dg.rs'),kernel_sha=sha(bridge/'dg_rhs.cpp'),build_sha=sha(bridge/'build.rs'))
 j.write_text(json.dumps(v,indent=2)+'\n');print(v,flush=True)
if __name__=='__main__':main(sys.argv[1])
