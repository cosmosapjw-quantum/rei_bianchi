#!/usr/bin/env python3
"""Offline independent replay. No network, no mutation of the original ZIP."""
import hashlib, pathlib, subprocess, sys, zipfile
archive, out, affine, test, lock = map(pathlib.Path, sys.argv[1:6])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == "60d05e181aa74f5da81be1e30cdf8f3edbe2cccc52044753e0992483a4c41cf9", "Wrong C07 source archive"
out.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    selected = [n for n in z.namelist() if '/focused_bundle/' in n and not n.endswith('/')]
    for name in selected:
        rel = name.split('/focused_bundle/', 1)[1]
        target = out/rel
        assert out.resolve() in target.resolve().parents
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(name))
files = {'igm_rates.rs':'dc3cc028a41ac852d94835372ce13545389d1c3a', 'rate_table.rs':'8bdbe9ec651c4a3560cf9078856bb790a8e47a6b', 'igm_thermal.rs':'5bde309d28c21567769a80575d929dd70c42f597'}
src=out/'rust/rei_microphysics/src'
for name,want in files.items():
    got=subprocess.check_output(['git','hash-object',str(src/name)],text=True).strip()
    assert got==want,(name,got,want)
shutil = __import__('shutil')
shutil.copyfile(affine,src/'joint_affine.rs')
assert subprocess.check_output(['git','hash-object',str(src/'joint_affine.rs')],text=True).strip()=='05c6fe32890eb335a3987082a134ac2c7fcd6feb'
shutil.copyfile(test,out/'rust/rei_microphysics/tests/c8_rate_study.rs')
print('SOURCE_RESTORE_PASS',len(selected))

shutil.copyfile(lock, out/'rust/rei_microphysics/Cargo.lock')
