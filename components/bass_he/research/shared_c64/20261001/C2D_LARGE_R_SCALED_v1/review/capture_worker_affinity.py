"""Read-only affinity evidence tied to the batch's owned-process registry."""
import argparse,datetime,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 batch=(ROOT/a.batch).resolve();out=(ROOT/a.output).resolve()
 if not batch.is_relative_to(ROOT.resolve()) or not out.is_relative_to(ROOT.resolve()):raise ValueError('outside package')
 run=batch/'RUN_IDENTITY.json';rows=[]
 for owned in sorted(batch.glob('*/OWNED_PROCESS.json')):
  if (owned.parent/'TASK_EXECUTION.json').exists():continue
  record=json.loads(owned.read_bytes());leader=record['leader'];proc=Path('/proc')/str(leader['procfs_pid'])
  try:
   stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
   status=dict(line.split(':',1) for line in (proc/'status').read_text().splitlines() if ':' in line)
   cmd=(proc/'cmdline').read_bytes().split(b'\0')
   try:namespace=(proc/'ns/pid').stat().st_ino;namespace_read='AVAILABLE'
   except PermissionError:namespace=None;namespace_read='PERMISSION_DENIED_FROM_OBSERVER_NAMESPACE'
   if (int(stat[19])!=leader['start_time_ticks'] or int(status['NSpid'].split()[-1])!=leader['pid']
       or (namespace is not None and namespace!=leader['pid_namespace_inode'])
       or Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=record['boot_id'] or len(cmd)<2
       or cmd[1]!=str(ROOT/'code/task_worker.py').encode()
       or str(owned.parent/'TASK_INPUT.json').encode() not in cmd):continue
   age=float(Path('/proc/uptime').read_text().split()[0])-leader['start_time_ticks']/os.sysconf('SC_CLK_TCK')
   if age<2:continue
   rows.append({'task_id':record['task_id'],'registry_sha256':sha(owned),'procfs_pid':leader['procfs_pid'],
    'namespace_pid':leader['pid'],'namespace_inode':namespace,'namespace_inode_read':namespace_read,'start_time_ticks':leader['start_time_ticks'],
    'age_seconds':age,'threads':int(status['Threads']),'cpus_allowed_list':status['Cpus_allowed_list'].strip(),
    'identity_checks':'registry procfsPID/starttime, current boot, namespace PID, task-worker argv and exact TASK_INPUT path; namespace inode only when readable'})
  except (OSError,ValueError,KeyError,IndexError):continue
 if not rows:raise RuntimeError('NO_LIVE_OWNED_WORKER_OBSERVED')
 value={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'read_only':True,
  'batch':a.batch,'run_identity_sha256':sha(run),'workers':rows,'new_physical_evaluations':0,
  'scope':'observed masks of these live owned worker processes; not a speedup or NCP64 claim'}
 with out.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'workers':len(rows),'masks':[row['cpus_allowed_list'] for row in rows]}))

if __name__=='__main__':main()
