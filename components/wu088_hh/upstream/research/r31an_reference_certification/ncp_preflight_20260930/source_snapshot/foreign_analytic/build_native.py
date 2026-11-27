"""Content-addressed trusted multi-file build; uses reviewed engineering utilities."""
from pathlib import Path
import hashlib, json, os, platform, shlex, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/engineering'))
import native_support as ns
HERE=Path(__file__).resolve().parent
SOURCES={'radial_power.cpp':ROOT/'production/radial_power/radial_power.cpp','analytic.cpp':HERE/'analytic.cpp'}
FLAGS=(*ns.FLAGS,'-fvisibility=hidden')
UNIT=b'#include "radial_power.cpp"\n#include "analytic.cpp"\n'

def checked(folder):
 folder=Path(folder);m=json.loads((folder/'manifest.json').read_text())
 if hashlib.sha256(ns.canonical(m['identity'])).hexdigest()!=folder.name:
  raise RuntimeError('analytic cache identity mismatch')
 expected=set(SOURCES)|{'unit.cpp','analytic.so','compile.stdout','compile.stderr'}
 if set(m['artifacts'])!=expected:raise RuntimeError('analytic cache artifact registry mismatch')
 for name,digest in m['artifacts'].items():
  if Path(name).name!=name or ns.sha(folder/name)!=digest:raise RuntimeError('analytic cache artifact corrupt: '+name)
 for name,digest in m['runtime_dependencies'].items():
  if ns.sha(name)!=digest:raise RuntimeError('native runtime changed; use new cache scope')
 return m

def build(cache,*,sources=None):
 """sources override is for isolated fault injection/tests, never untrusted code."""
 cache=Path(cache).resolve();cache.mkdir(parents=True,exist_ok=True)
 if platform.system()!='Linux':raise RuntimeError('Linux build profile only')
 for var in ('LD_PRELOAD','LD_LIBRARY_PATH'):
  if os.environ.get(var):raise RuntimeError(var+' must be unset')
 mapping=SOURCES if sources is None else sources
 if set(mapping)!=set(SOURCES):raise ValueError('exact source registry required')
 frozen={name:Path(path).read_bytes() for name,path in mapping.items()};frozen['unit.cpp']=UNIT
 compiler=Path(shutil.which('g++',path=ns.BUILD_ENV['PATH']) or '').resolve()
 if not compiler.is_file():raise RuntimeError('system g++ unavailable')
 with ns.locked(cache/'.build.lock'):
  stage=Path(tempfile.mkdtemp(prefix='.stage-',dir=cache))
  try:
   for name,data in frozen.items():ns.write_synced(stage/name,data)
   dep=ns.run([str(compiler),'-std=c++17','-M','-MT','unit','unit.cpp'],cwd=stage)
   headers={}
   for name in shlex.split(dep.replace('\\\n',' ').split(':',1)[1]):
    p=Path(name)
    if not p.is_absolute():
     if name not in frozen:raise RuntimeError('unsupported project include: '+name)
    else:headers[str(p.resolve())]=ns.sha(p)
   binaries={str(compiler):ns.sha(compiler)}
   for program in ('cc1plus','as','ld'):
    p=ns.run([str(compiler),'-print-prog-name='+program])
    p=Path(shutil.which(p,path=ns.BUILD_ENV['PATH']) or p).resolve();binaries[str(p)]=ns.sha(p)
   identity={'schema':1,'source_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in frozen.items()},
    'builder_sha256':ns.sha(__file__),'shared_utilities_sha256':ns.sha(ns.__file__),
    'flags':list(FLAGS),'compiler_version':ns.run([str(compiler),'--version']),
    'target':ns.run([str(compiler),'-dumpmachine']),'tools':binaries,'headers':headers,
    'build_env':ns.BUILD_ENV,'machine':platform.machine()}
   key=hashlib.sha256(ns.canonical(identity)).hexdigest();dest=cache/key
   if dest.exists():checked(dest);return dest
   argv=[str(compiler),*FLAGS,'unit.cpp','-o','analytic.so']
   cp=subprocess.run(argv,cwd=stage,env=ns.BUILD_ENV,capture_output=True,text=True,timeout=120)
   ns.write_synced(stage/'compile.stdout',cp.stdout.encode());ns.write_synced(stage/'compile.stderr',cp.stderr.encode())
   if cp.returncode:raise RuntimeError('analytic compile failed with exit '+str(cp.returncode))
   m={'identity':identity,'command':argv,'runtime_dependencies':ns.runtime_dependencies(stage/'analytic.so'),
    'artifacts':{n:ns.sha(stage/n) for n in (*frozen,'analytic.so','compile.stdout','compile.stderr')}}
   with (stage/'analytic.so').open('rb') as stream:os.fsync(stream.fileno())
   ns.write_synced(stage/'manifest.json',ns.canonical(m));ns.sync_dir(stage)
   os.rename(stage,dest);ns.sync_dir(cache);checked(dest);return dest
  except Exception as exc:
   if stage.exists():
    ns.write_synced(stage/'failure.json',ns.canonical({'error_type':type(exc).__name__,'message':str(exc),
     'stdout':getattr(exc,'stdout',None),'stderr':getattr(exc,'stderr',None)}))
    os.rename(stage,cache/('failed-'+stage.name.removeprefix('.stage-')));ns.sync_dir(cache)
   raise
  finally:
   if stage.exists():shutil.rmtree(stage)
