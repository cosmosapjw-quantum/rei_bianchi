"""Hash-verified owned source ZIP restore, with actual new-crate Rust tests.

Uses the separately verified recovered Rust/registry environment, not a newly
downloaded compiler. Restores all scientific path dependencies from ZIP bytes.
Build cache is outside the restored source and may be reused for compilation.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import zipfile

root=Path(__file__).resolve().parents[1]
stage_name="research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019"
original=(root/"../../repo"/stage_name).resolve()
files={}
for part in ["Cargo.toml","Cargo.lock","README.md","src","tests","scripts"]:
    source=root/part
    candidates=[source] if source.is_file() else list(source.rglob("*"))
    for p in candidates:
        if p.is_file() and "__pycache__" not in p.parts:
            files["brperf01/photon/"+p.relative_to(root).as_posix()]=p.read_bytes()
for part in ["br06","parent","inputs","vendor/vigilode"]:
    for p in (original/part).rglob("*"):
        if p.is_file() and not any(x in p.parts for x in ["target",".git","__pycache__"]):
            files["repo/"+stage_name+"/"+p.relative_to(original).as_posix()]=p.read_bytes()
manifest={name:hashlib.sha256(content).hexdigest() for name,content in sorted(files.items())}
archive=root/"evidence/FRESH_RESTORE_SOURCE.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipped:
    for name,content in sorted(files.items()):
        zipped.writestr(name,content)
    zipped.writestr("PAYLOAD_SHA256.json",json.dumps(manifest,indent=2)+"\n")
restored=root/"evidence/fresh_restore_work"
restored.mkdir(parents=True,exist_ok=False)
with zipfile.ZipFile(archive) as zipped:
    for item in zipped.infolist():
        assert not item.filename.startswith("/") and ".." not in Path(item.filename).parts
    zipped.extractall(restored)
for name,digest in manifest.items():
    assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==digest,name
environment=os.environ.copy()
environment["CARGO_TARGET_DIR"]=str(root/"target")
with (root/"evidence/FRESH_RESTORE_TESTS.log").open("w") as output:
    completed=subprocess.run(["cargo","test","--offline","--all-targets"],
        cwd=restored/"brperf01/photon",env=environment,stdout=output,stderr=subprocess.STDOUT,check=False)
record={"archive":archive.name,"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),
        "size_bytes":archive.stat().st_size,"verified_payload_files":len(manifest),
        "restored_scientific_sources":"all new crate + BR06 + parent + native inputs + pinned VigilODE",
        "external_recovered_runtime_and_registry":"separate root stage verified Rust1.94.1 +99packages; no redownload",
        "test_command":["cargo","test","--offline","--all-targets"],
        "test_exit_code":completed.returncode,"compiled_source_is_restored_copy":True}
(root/"evidence/FRESH_RESTORE_VERIFICATION.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps(record,indent=2))
assert completed.returncode==0
