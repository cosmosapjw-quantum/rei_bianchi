"""Explicit root-backed host storage admission; never mutates block devices."""
from dataclasses import asdict, dataclass
from pathlib import Path
import os

GIB = 1024 ** 3

@dataclass(frozen=True)
class RootStorage:
    storage_mode: str
    same_filesystem_as_root: bool
    storage_device: str
    storage_fstype: str
    read_write: bool
    path_exists: bool
    path_symlink: bool
    filesystem_size_bytes: int
    filesystem_used_bytes: int
    filesystem_available_bytes: int
    filesystem_available_fraction: float
    filesystem_errors: int | None

    def receipt(self):
        return asdict(self)

def inspect_root_storage(path=Path('/srv/bass-he'), root=Path('/'), mountinfo=Path('/proc/self/mountinfo')):
    path=Path(path);root=Path(root)
    line=next((line for line in mountinfo.read_text().splitlines()
               if line.split(' - ',1)[0].split()[4]=='/'),None)
    if line is None:raise RuntimeError('BLOCKED_ROOT_STORAGE_IDENTITY')
    left,right=line.split(' - ',1);fields=right.split();source=fields[1];fstype=fields[0]
    options=left.split()[5].split(',')
    stat=os.statvfs(root);size=stat.f_blocks*stat.f_frsize;available=stat.f_bavail*stat.f_frsize
    errors_path=Path('/sys/fs/ext4')/Path(source).name/'errors_count'
    try:errors=int(errors_path.read_text()) if fstype=='ext4' else None
    except (OSError,ValueError):errors=None
    exists=path.exists();symlink=path.is_symlink()
    return RootStorage('root_backed_host',exists and not symlink and path.stat().st_dev==root.stat().st_dev,
                       source,fstype,'rw' in options and 'ro' not in options and not bool(stat.f_flag & getattr(os,'ST_RDONLY',1)),
                       exists,symlink,size,size-stat.f_bfree*stat.f_frsize,available,
                       available/size if size else 0.0,errors)

def admit_root_storage(snapshot:RootStorage,initial=True):
    if snapshot.storage_mode!='root_backed_host' or snapshot.storage_fstype!='ext4' or not snapshot.storage_device.startswith('/dev/vda'):
        raise RuntimeError('BLOCKED_ROOT_STORAGE_IDENTITY')
    if not snapshot.path_exists or snapshot.path_symlink or not snapshot.same_filesystem_as_root:
        raise RuntimeError('BLOCKED_ROOT_STORAGE_PATH')
    if not snapshot.read_write or snapshot.filesystem_errors is None or snapshot.filesystem_errors>0:
        raise RuntimeError('BLOCKED_ROOT_STORAGE_READ_ONLY_OR_ERRORS')
    floor_bytes=(20 if initial else 15)*GIB;floor_fraction=.20 if initial else .15
    if snapshot.filesystem_available_bytes<floor_bytes or snapshot.filesystem_available_fraction<floor_fraction:
        raise RuntimeError('BLOCKED_ROOT_STORAGE_HEADROOM' if initial else 'BLOCKED_STORAGE_HEADROOM')
    return snapshot.receipt()

def write_fsync_probe(path=Path('/srv/bass-he')):
    path=Path(path);probe=path/('.storage-probe-'+str(os.getpid()))
    with probe.open('xb') as f:
        f.write(b'BASS_HE_ROOT_BACKED_STORAGE_TEST\n');f.flush();os.fsync(f.fileno())
    fd=os.open(path,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    probe.unlink()
    fd=os.open(path,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
