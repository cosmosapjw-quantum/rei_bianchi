from pathlib import Path
import sys,json,os,tarfile,hashlib,shutil,subprocess
from support import R,E,OLD,REPO,L,REVIEW,sha,ref,write,run
NODE=L/'w3_coverage_contract_20261002_v1'
sys.path.insert(0,str(NODE));import runtime_adapter as a
c=a.c
fast=c.module(L/'ncp64_acceleration_20261001_v1/backend_build/build_fast.py','r2_original_fast');prior,gate,hp=fast.modules()
extract=c.module(REVIEW/'release_extract.py','r2_release_candidate')
def fidelity(arc,dest):
 rows=[]
 with tarfile.open(arc) as t:
  for m in t:
   p=dest/m.name.rstrip('/');st=p.lstat()
   expected_mode=0o755 if m.isdir() or m.mode&0o111 else 0o644
   assert not p.is_symlink() and (p.is_dir() if m.isdir() else p.is_file()),m.name
   assert type(m.mtime) is int and st.st_mtime_ns==m.mtime*10**9,m.name
   assert st.st_mode&0o777==expected_mode,m.name
   row=dict(path=m.name,archive_type='dir' if m.isdir() else 'file',archive_mode=m.mode,extracted_mode=st.st_mode&0o777,archive_mtime_seconds=m.mtime,extracted_mtime_ns=st.st_mtime_ns,bytes=m.size)
   if m.isfile():
    data=t.extractfile(m).read();assert p.read_bytes()==data,m.name
    row['sha256']=hashlib.sha256(data).hexdigest()
   rows.append(row)
 return dict(archive=ref(arc),members=rows,content_and_recorded_mtime_exact=True,mode_policy='Original pinned extractor normalization retained: executable files/directories 0755, other files 0644; ownership not restored',archive_raw_modes_preserved=all(x['archive_mode']==x['extracted_mode'] for x in rows),mode_policy_verified=True)
def make_environment():
 pre=prior.preflight(REPO/'backend_sources',R/'backend')
 for key,name in {'makeinfo':str(OLD/'prep_r1/tooling/bin/makeinfo'),'autom4te':'autom4te','autoheader':'autoheader','aclocal':'aclocal','perl':'perl','ar':'ar','ranlib':'ranlib'}.items():
  p=name if name.startswith('/') else shutil.which(name,path='/usr/bin:/bin')
  if p is None:raise ValueError('missing genuine bootstrap dependency '+name)
  pre['tools'][key]=p;pre['tool_identities'][key]=ref(Path(p))
 rp=hp.plan(hp.detect());cfg=fast.configuration(prior,rp,2)
 env=prior.clean_environment(R/'backend',R/'backend/prefix',pre['tools'],cfg)
 return pre,rp,cfg,env
if __name__=='__main__':
 probe=R/'metadata_probe';probe.mkdir(exist_ok=False);out=[]
 for name,spec in prior.SOURCES.items():
  arc=REPO/'backend_sources'/spec['archive'];assert sha(arc)==spec['sha256'] and arc.stat().st_size==spec['size']
  extract.safe_extract(arc,probe/name,expected_sha256=spec['sha256'],expected_root=spec['root'])
  out.append(fidelity(arc,probe/name))
 write('EXTRACTION_METADATA_FIDELITY.json',dict(extractor=ref(REVIEW/'release_extract.py'),archives=out,unsupported_mtimes=[],links_or_special=[],source_ownership_restrictions_unchanged=True))
 mpfr=probe/'mpfr'/prior.SOURCES['mpfr']['root'];queries=[]
 for target,deps in [('Makefile.in',['Makefile.am','configure.ac','aclocal.m4']),('configure',['configure.ac','aclocal.m4'])]:
  f=probe/(target+'.query.mk');f.write_text(str(mpfr/target)+': '+' '.join(str(mpfr/d) for d in deps)+'\n\t@echo UNEXPECTED_REGENERATION\n')
  rc=run('fresh_mpfr_query_'+target.replace('.','_'),['/usr/bin/make','-rR','-q','-f',str(f),str(mpfr/target)])
  assert rc==0;queries.append(dict(target=target,exit_status=rc))
 write('MPFR_DEPENDENCY_QUERY.json',dict(queries=queries,package_make_or_configure_executed=False,source_changes=False))
