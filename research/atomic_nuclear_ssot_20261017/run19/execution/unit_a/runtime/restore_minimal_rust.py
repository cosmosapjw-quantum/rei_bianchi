"""Reproducible minimal install from the exact supplied archive; no network.

This portable recipe was added after the recorded successful installation.
The current executed install/probe remains install_and_probe.py and its receipt.
"""
import argparse,hashlib,json,pathlib,shutil,subprocess,tarfile,time
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--archive',type=pathlib.Path,required=True)
p.add_argument('--work-dir',type=pathlib.Path,required=True)
p.add_argument('--prefix',type=pathlib.Path,required=True)
a=p.parse_args();a.archive=a.archive.resolve();a.work_dir=a.work_dir.resolve();a.prefix=a.prefix.resolve()
if a.work_dir.exists() or a.prefix.exists():raise SystemExit('create-only work-dir/prefix required')
if not a.prefix.is_relative_to(a.work_dir):raise SystemExit('prefix must be inside new work-dir')
expected='294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40'
h=hashlib.sha256()
with a.archive.open('rb')as f:
    for chunk in iter(lambda:f.read(4<<20),b''):h.update(chunk)
if h.hexdigest()!=expected:raise SystemExit('supplied archive hash mismatch')
a.work_dir.mkdir(parents=True);stage=a.work_dir/'selected_distribution';stage.mkdir()
components={'rustc','cargo','rust-std-x86_64-unknown-linux-gnu'}
metadata={'install.sh','components','rust-installer-version','version','git-commit-hash','git-commit-info','LICENSE-APACHE','LICENSE-MIT','COPYRIGHT'}
top='rust-1.94.1-x86_64-unknown-linux-gnu';files=[];total=0;t=time.perf_counter()
with tarfile.open(a.archive,'r|xz')as tar:
    for count,member in enumerate(tar,1):
        rel=pathlib.PurePosixPath(member.name)
        if count>100000 or rel.is_absolute() or '..'in rel.parts or not rel.parts or rel.parts[0]!=top:
            raise SystemExit('unsafe archive path/count')
        if not(member.isfile()or member.isdir()):raise SystemExit('archive link/special file refused')
        if len(rel.parts)<2 or not member.isfile():continue
        inner=pathlib.Path(*rel.parts[1:])
        if inner.parts[0]not in components and str(inner)not in metadata:continue
        total+=member.size
        if total>700*(1<<20):raise SystemExit('selected size budget exceeded')
        dest=stage/inner;dest.parent.mkdir(parents=True,exist_ok=True)
        source=tar.extractfile(member)
        with dest.open('xb')as out:shutil.copyfileobj(source,out,4<<20)
        if dest.stat().st_size!=member.size:raise SystemExit('truncated member')
        dest.chmod(0o755 if member.mode&0o111 else 0o644)
        files.append({'path':str(inner),'bytes':member.size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
argv=['sh',str(stage/'install.sh'),'--prefix='+str(a.prefix),
    '--components=rustc,cargo,rust-std-x86_64-unknown-linux-gnu','--disable-ldconfig']
r=subprocess.run(argv,cwd=a.work_dir,capture_output=True,timeout=30)
(a.work_dir/'install.stdout.txt').write_bytes(r.stdout);(a.work_dir/'install.stderr.txt').write_bytes(r.stderr)
receipt={'schema':'REI_RUN19_PORTABLE_RUNTIME_RESTORE_V1','archive_sha256':expected,
    'signature_verified':False,'selected_files':files,'selected_bytes':total,'prefix':str(a.prefix),
    'argv':argv,'exit_code':r.returncode,'wall_seconds':time.perf_counter()-t,'network_calls':0,'science_builds':0,'ivps':0}
(a.work_dir/'RESTORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'exit_code':r.returncode,'prefix':str(a.prefix),'selected_bytes':total},indent=2))
raise SystemExit(r.returncode)
