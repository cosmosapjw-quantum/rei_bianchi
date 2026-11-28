from pathlib import Path
import os,json,sys
from common import E,write
def observation():
 cg=Path('/proc/self/cgroup').read_text();root=Path('/sys/fs/cgroup');leaf=root/cg.strip().split(':')[-1].lstrip('/');values=[]
 for p in (leaf,*leaf.parents):
  if not p.is_relative_to(root):break
  row={'path':str(p)}
  for name in ('cpu.max','cpu.stat','memory.max','memory.current','memory.peak','memory.events','cgroup.controllers','cgroup.subtree_control','cgroup.procs'):
   row[name]=(p/name).read_text() if (p/name).exists() else None
  row['sibling_memory_current']={str(q.parent):q.read_text() for q in p.parent.glob('*/memory.current')};values.append(row)
  if p==root:break
 return dict(pid=os.getpid(),ppid=os.getppid(),uid=os.getuid(),gid=os.getgid(),status=Path('/proc/self/status').read_text(),uid_map=Path('/proc/self/uid_map').read_text(),gid_map=Path('/proc/self/gid_map').read_text(),membership=cg,mountinfo=Path('/proc/self/mountinfo').read_text(),namespace={n:os.readlink('/proc/self/ns/'+n) for n in ('mnt','cgroup','user','pid')},affinity=sorted(os.sched_getaffinity(0)),ancestors=values,meminfo=Path('/proc/meminfo').read_text())
if __name__=='__main__':
 o=observation()
 if sys.argv[1]=='child':print(json.dumps(o))
 else:write(E/(sys.argv[1]+'.json'),o)
