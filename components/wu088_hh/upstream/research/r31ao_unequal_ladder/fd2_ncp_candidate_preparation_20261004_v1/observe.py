from support import *
def observation():
 root=Path('/sys/fs/cgroup');cg=Path('/proc/self/cgroup').read_text();leaf=root/cg.strip().split(':')[-1].lstrip('/');values=[]
 for p in (leaf,*leaf.parents):
  if not p.is_relative_to(root):break
  row=dict(path=str(p))
  for name in ('cpu.max','memory.max','memory.current','memory.peak','memory.events','cpu.stat','cgroup.procs','cgroup.controllers','cgroup.subtree_control'):
   row[name]=(p/name).read_text() if (p/name).exists() else None
  row['sibling_memory_current']={str(q.parent):q.read_text() for q in p.parent.glob('*/memory.current')};values.append(row)
  if p==root:break
 return dict(pid=os.getpid(),ppid=os.getppid(),uid=os.getuid(),gid=os.getgid(),status=Path('/proc/self/status').read_text(),membership=cg,namespace={n:os.readlink('/proc/self/ns/'+n) for n in ('mnt','cgroup','user','pid')},affinity=sorted(os.sched_getaffinity(0)),ancestors=values,meminfo=Path('/proc/meminfo').read_text(),mountinfo=Path('/proc/self/mountinfo').read_text(),uid_map=Path('/proc/self/uid_map').read_text())
if __name__=='__main__':write(E/(sys.argv[1]+'.json'),observation())
