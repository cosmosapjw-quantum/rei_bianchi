import os
from pathlib import Path
import pytest
from wu088_hh.backup import dual_backup


def fake_rclone(tmp):
    tool=tmp/'rclone';tool.write_text('''#!/usr/bin/env python3
import pathlib,sys,time,os,shutil
root=pathlib.Path(os.environ['FAKE_REMOTE']);args=sys.argv[1:]
if args[0]=='listremotes':print('gdrv: drive\\ndbx: dropbox');sys.exit(0)
if args[0]=='copyto':
 src,dst=args[-2:];remote,name=dst.split(':',1);p=root/remote/pathlib.Path(name).name;p.parent.mkdir(parents=True,exist_ok=True)
 (root/(remote+'.entered')).touch()
 if os.environ.get('SYNC_PEERS')=='1':
  end=time.monotonic()+3
  while not all((root/(r+'.entered')).exists() for r in ('gdrv','dbx')):
   if time.monotonic()>end:sys.exit(9)
   time.sleep(.005)
 if remote==os.environ.get('FAIL_REMOTE'):sys.exit(5)
 if p.exists() and p.read_bytes()!=pathlib.Path(src).read_bytes():sys.exit(6)
 if not p.exists():shutil.copyfile(src,p)
 sys.exit(0)
if args[0]=='cat':
 remote,name=args[1].split(':',1);p=root/remote/pathlib.Path(name).name
 sys.stdout.buffer.write(b'corrupt' if remote==os.environ.get('CORRUPT_REMOTE') else p.read_bytes());sys.exit(0)
sys.exit(2)
''');tool.chmod(0o755);return str(tool)


def run(tmp,monkeypatch,**env):
    remote=tmp/'remote';remote.mkdir();monkeypatch.setenv('FAKE_REMOTE',str(remote))
    for k,v in env.items():monkeypatch.setenv(k,v)
    source=tmp/'delta.zip';source.write_bytes(b'bounded evidence content')
    return dual_backup(source,{'google_drive':'gdrv:scope/delta.zip','dropbox':'dbx:scope/delta.zip'},tmp/'receipt.json',rclone_bin=fake_rclone(tmp))


def test_providers_progress_concurrently(tmp_path,monkeypatch):
    r=run(tmp_path,monkeypatch,SYNC_PEERS='1')
    assert r['dual_raw_readback_verified'] is True
    assert r['status']=='DUAL_RAW_READBACK_VERIFIED'


def test_partial_provider_failure_not_acknowledged(tmp_path,monkeypatch):
    r=run(tmp_path,monkeypatch,FAIL_REMOTE='dbx')
    assert r['dual_raw_readback_verified'] is False
    assert r['providers']['google_drive']['status']=='REMOTE_OBJECT_PRESENT_RAW_READBACK_VERIFIED'
    assert r['providers']['dropbox']['status']=='FAILED_OR_UNVERIFIED'


def test_corrupt_readback_is_not_success(tmp_path,monkeypatch):
    assert run(tmp_path,monkeypatch,CORRUPT_REMOTE='dbx')['dual_raw_readback_verified'] is False


def test_wrong_provider_type_rejected_before_upload(tmp_path,monkeypatch):
    monkeypatch.setenv('FAKE_REMOTE',str(tmp_path))
    source=tmp_path/'a.zip';source.write_bytes(b'a')
    with pytest.raises(ValueError,match='provider'):
        dual_backup(source,{'google_drive':'dbx:a','dropbox':'dbx:b'},tmp_path/'receipt.json',rclone_bin=fake_rclone(tmp_path))
    assert not (tmp_path/'dbx.entered').exists()
