#!/usr/bin/env python3
"""Package committed STATE04 source, inherited dependencies and a real Git bundle.

No source module or scientific test is imported/executed; no network operation.
Run once after root commits the reviewed closeout and pins actual HEAD.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

BASE="ac6042a6b0610b09d0576538767ee0299389a5eb"
PROGRAM="research/program_expansion_20261025"
UNIT=PROGRAM+"/continuation_state_20261027"
LEGACY_DRIFT02_FILES = ('AGENTS.md',
 'research/he34_sandbox_certified_relaxation_20261022/data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json',
 'research/he34_sandbox_certified_relaxation_20261022/results/NEUTRAL_TRANSPORT.json',
 'research/he34_sandbox_certified_relaxation_20261022/src/neutral_transport.py',
 'research/he_ang_finitemass_cba_20261025/CLAIM_GATE.json',
 'research/he_ang_finitemass_cba_20261025/evidence/execution/RESOURCE_LEDGER.json',
 'research/program_expansion_20261025/CENTRAL_REFERENCE.json',
 'research/program_expansion_20261025/HANDOFF_KO.md',
 'research/program_expansion_20261025/REPO_CHARTER_KO.md',
 'research/program_expansion_20261025/TASK_ASSIGNMENT.json',
 'research/program_expansion_20261025/continuation_20261025/DAG.json',
 'research/program_expansion_20261025/continuation_20261025/HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261025/LOOP_PROGRESS.json',
 'research/program_expansion_20261025/continuation_20261025/RESULT.json',
 'research/program_expansion_20261025/continuation_20261025/RESULTS_KO.md',
 'research/program_expansion_20261025/continuation_20261025/VALIDATION_ADDENDUM_01.json',
 'research/program_expansion_20261025/continuation_20261025/VALIDATION_CONTRACT.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/BACKUP_ACK.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/PREFLIGHT.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/PUBLICATION.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/SOURCE_ARCHIVE_RECEIPT.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/SOURCE_REMOTE_VERIFICATION.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/BASE_METADATA.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/DELTA_VALIDATION.first_attempt.raw.log',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/DELTA_VALIDATION.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/DELTA_VALIDATION.raw.log',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/INDEPENDENT_REVIEW.json',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/REAPPLY_NOTE.md',
 'research/program_expansion_20261025/continuation_20261025/delivery/central/validate_delta.py',
 'research/program_expansion_20261025/continuation_20261025/evidence/CENTRAL_HE_DAG_BASELINE.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/DELIVERY_PREPARATION_NOTES.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/PREFLIGHT.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/inherited/HE101_CLAIM_GATE.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/inherited/HE101_FINAL_BACKUP_ACK.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/inherited/HE101_RESOURCE_LEDGER.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/01_exchange/FINISH.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/01_exchange/START.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/01_exchange/stderr.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/01_exchange/stdout.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/02_pair_source/FINISH.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/02_pair_source/START.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/02_pair_source/stderr.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/02_pair_source/stdout.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/03_species/FINISH.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/03_species/START.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/03_species/stderr.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/03_species/stdout.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/FINISH.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/START.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/exchange_closure_at_failure.py',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/stderr.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/stdout.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/04_exchange/test_exchange_closure_at_failure.py',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/05_exchange/FINISH.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/05_exchange/START.json',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/05_exchange/stderr.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/05_exchange/stdout.txt',
 'research/program_expansion_20261025/continuation_20261025/evidence/validation/RESOURCE_LEDGER.json',
 'research/program_expansion_20261025/continuation_20261025/exchange/HHE_INDEPENDENT_REVIEW.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/PAIR_INDEPENDENT_REVIEW.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/PROVENANCE.json',
 'research/program_expansion_20261025/continuation_20261025/exchange/THEORY_KO.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/exchange_closure.py',
 'research/program_expansion_20261025/continuation_20261025/exchange/source_snapshots/HE33_THEORY.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/source_snapshots/HE36_THEORY.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/source_snapshots/HE38_DERIVATION.md',
 'research/program_expansion_20261025/continuation_20261025/exchange/test_exchange_closure.py',
 'research/program_expansion_20261025/continuation_20261025/pair_source/CONTRACT.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/INTAKE_RESULT.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/RAW_IDENTITIES.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/SELECTED_H_HE_SOURCE.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/SOURCE_INTAKE_NOTES.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/THEORY_KO.md',
 'research/program_expansion_20261025/continuation_20261025/pair_source/h_he_intake.py',
 'research/program_expansion_20261025/continuation_20261025/pair_source/reviews/INDEPENDENT_REVIEW_FINAL.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/reviews/INDEPENDENT_REVIEW_INITIAL.json',
 'research/program_expansion_20261025/continuation_20261025/pair_source/test_h_he_intake.py',
 'research/program_expansion_20261025/continuation_20261025/pair_source/upstream/COPYING',
 'research/program_expansion_20261025/continuation_20261025/pair_source/upstream/COPYING.LESSER',
 'research/program_expansion_20261025/continuation_20261025/pair_source/upstream/CapitelliIntegrals.cpp',
 'research/program_expansion_20261025/continuation_20261025/pair_source/upstream/CapitelliIntegrals.h',
 'research/program_expansion_20261025/continuation_20261025/reviews/RUNNER_REVIEW.md',
 'research/program_expansion_20261025/continuation_20261025/run_validation.py',
 'research/program_expansion_20261025/continuation_20261025/sources/SOURCE_PROVENANCE.json',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/he34_neutral_transport_subset.json',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/he34_neutral_transport_theory.md',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/mutationpp_collisions.xml',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/rec_atomic_model.json',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/rec_atomic_network.py',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/rec_hd_adapter_contract.json',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/wu78_atomic_network.py',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/wu79_atomic_sources.md',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/wu79_source_evidence.json',
 'research/program_expansion_20261025/continuation_20261025/sources/raw/wu_chem_fixtures.json',
 'research/program_expansion_20261025/continuation_20261025/species/AUTHOR_FREEZE.json',
 'research/program_expansion_20261025/continuation_20261025/species/BUILD_STDERR.txt',
 'research/program_expansion_20261025/continuation_20261025/species/BUILD_STDOUT.txt',
 'research/program_expansion_20261025/continuation_20261025/species/EXPLICIT_TRANSPORT_SOURCE_INVENTORY.json',
 'research/program_expansion_20261025/continuation_20261025/species/PREBUILD_SOURCE_OBSERVATION.json',
 'research/program_expansion_20261025/continuation_20261025/species/README_KO.md',
 'research/program_expansion_20261025/continuation_20261025/species/SOURCE_BUILD_PROCESS.json',
 'research/program_expansion_20261025/continuation_20261025/species/SOURCE_EXTRACTION_RECEIPT.json',
 'research/program_expansion_20261025/continuation_20261025/species/SPECIES_PROVIDER_REGISTRY.json',
 'research/program_expansion_20261025/continuation_20261025/species/consumer_inventory.py',
 'research/program_expansion_20261025/continuation_20261025/species/test_consumer_inventory.py',
 'research/program_expansion_20261025/continuation_20261027/ALL_SPECIES_SUPPLIER_PLAN_KO.md',
 'research/program_expansion_20261025/continuation_20261027/DAG.json',
 'research/program_expansion_20261025/continuation_20261027/HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261027/LOOP_PROGRESS.json',
 'research/program_expansion_20261025/continuation_20261027/MODEL_CONTRACT.json',
 'research/program_expansion_20261025/continuation_20261027/README.md',
 'research/program_expansion_20261025/continuation_20261027/RESULT.json',
 'research/program_expansion_20261025/continuation_20261027/RESULTS_KO.md',
 'research/program_expansion_20261025/continuation_20261027/THEORY_KO.md',
 'research/program_expansion_20261025/continuation_20261027/VALIDATION_CONTRACT.json',
 'research/program_expansion_20261025/continuation_20261027/delivery/PUBLICATION_BLOCK.json',
 'research/program_expansion_20261025/continuation_20261027/delivery/build_source_zip.py',
 'research/program_expansion_20261025/continuation_20261027/evidence/BACKUP_PREFLIGHT.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/BASELINE.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/CODE_REVIEW_INITIAL.md',
 'research/program_expansion_20261025/continuation_20261027/evidence/INDEPENDENT_REVIEW_FINAL.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/INDEPENDENT_REVIEW_FINAL.md',
 'research/program_expansion_20261025/continuation_20261027/evidence/INHERITED_PRESERVATION.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/NEUTRAL_MASS_CONVERSION.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/PR102_INHERITED_RECEIPT.md',
 'research/program_expansion_20261025/continuation_20261027/evidence/PRE_EXECUTION_READ.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/PRE_PUBLICATION_READ.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/ROOT_SOURCE_REVIEW.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/SOURCE_DIAGNOSTIC.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/VALIDATION_CONSOLE.txt',
 'research/program_expansion_20261025/continuation_20261027/evidence/validation/01_tests/FINISH.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/validation/01_tests/START.json',
 'research/program_expansion_20261025/continuation_20261027/evidence/validation/01_tests/stderr.txt',
 'research/program_expansion_20261025/continuation_20261027/evidence/validation/01_tests/stdout.txt',
 'research/program_expansion_20261025/continuation_20261027/evidence/validation/RESOURCE_LEDGER.json',
 'research/program_expansion_20261025/continuation_20261027/run_validation.py',
 'research/program_expansion_20261025/continuation_20261027/sources/CONSUMER_PROJECTION.json',
 'research/program_expansion_20261025/continuation_20261027/sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json',
 'research/program_expansion_20261025/continuation_20261027/sources/NIST_HTTP_RECEIPTS.json',
 'research/program_expansion_20261025/continuation_20261027/sources/PRIMARY_SOURCE_POINTERS.json',
 'research/program_expansion_20261025/continuation_20261027/sources/README_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/SOURCE_INTAKE_RESULT.json',
 'research/program_expansion_20261025/continuation_20261027/sources/SOURCE_MANIFEST.json',
 'research/program_expansion_20261025/continuation_20261027/sources/TESTED_DEPENDENCIES_01.json',
 'research/program_expansion_20261025/continuation_20261027/sources/build_consumer_projection.py',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/OVERLAY.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/README_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/SOURCE_MANIFEST.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/AGENTS.md',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/C9_FINAL.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/PROVIDER_ROWS.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/SCIENTIFIC_ADMISSION.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/coverage.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/provider_catalog.json',
 'research/program_expansion_20261025/continuation_20261027/sources/r3_update/raw/target6_overlay.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/CR_HE4_EXTERNAL_HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/HE_PREVIOUS_FIXTURE_INVENTORY.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/REC_HD_H5_HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_AGENTS.md',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_bare_masses.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_coverage.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_events.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_nuclear_catalogue_manifest.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_providers.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R1_species.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_HANDOFF_KO.md',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_SCIENTIFIC_ADMISSION.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_coverage.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_events.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_providers.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_species.json',
 'research/program_expansion_20261025/continuation_20261027/sources/raw/WU_R2_targets.json',
 'research/program_expansion_20261025/continuation_20261027/src/finite_drift.py',
 'research/program_expansion_20261025/continuation_20261027/src/mass_binding.py',
 'research/program_expansion_20261025/continuation_20261027/src/source_diagnostic.py',
 'research/program_expansion_20261025/continuation_20261027/tests/test_finite_drift.py',
 'research/program_expansion_20261025/continuation_20261027/tests/test_mass_binding.py',
 'research/program_expansion_20261025/continuation_20261027/tests/test_source_diagnostic.py')


def git(repo,*args):
    result=subprocess.run(["git","-C",str(repo),*args],capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()


def create(path,raw):
    if path.exists():
        if path.read_bytes()!=raw:
            raise ValueError("Existing unequal artifact: "+str(path))
        return
    with path.open("xb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--source",required=True)
    parser.add_argument("--output-directory",type=Path,required=True)
    args=parser.parse_args();repo=args.repo.resolve();source=args.source
    if not re.fullmatch("[0-9a-f]{40}",source):
        raise ValueError("Exact source commit SHA required")
    if git(repo,"rev-parse","HEAD").decode().strip()!=source:
        raise ValueError("Source must equal the committed actual HEAD")
    git(repo,"merge-base","--is-ancestor",BASE,source)
    tree=git(repo,"rev-parse",source+"^{tree}").decode().strip()
    entries={}
    for row in git(repo,"ls-tree","-r","-z","--full-tree",source).split(b"\0"):
        if not row:continue
        metadata,path=row.split(b"\t",1);mode,kind,blob=metadata.decode().split();name=path.decode()
        if name=="AGENTS.md" or name.startswith(PROGRAM+"/") or name in LEGACY_DRIFT02_FILES:
            if name.lower().endswith(".pdf"):continue
            if kind!="blob" or mode not in {"100644","100755"}:
                raise ValueError("Expected regular committed source file: "+name)
            entries[name]=(mode,blob)
    required=set(LEGACY_DRIFT02_FILES)|{"AGENTS.md",UNIT+"/RESULT.json",UNIT+"/RESULTS_KO.md",UNIT+"/DAG.json",UNIT+"/LOOP_PROGRESS.json",UNIT+"/HANDOFF_KO.md",UNIT+"/delivery/build_source_zip.py",UNIT+"/evidence/CODE_REVIEW_POST_EXECUTION.json",UNIT+"/evidence/SCIENTIFIC_ACCEPTANCE.json",UNIT+"/delivery/FOURTH_APPROVAL_RESULT.json",UNIT+"/delivery/preflight/PREFLIGHT.json"}
    if required-set(entries):raise ValueError("Missing committed dependencies: "+repr(sorted(required-set(entries))))
    files,modes={},{}
    for name,(mode,blob) in sorted(entries.items()):
        raw=git(repo,"show",source+":"+name)
        if hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()!=blob:
            raise ValueError("Committed blob mismatch: "+name)
        files[name]=raw;modes[name]=mode
    tested=json.loads(files[UNIT+"/evidence/TESTED_DEPENDENCIES_01.json"])
    for item in tested["files"]:
        raw=files[item["path"]]
        if len(raw)!=item["bytes"] or sha(raw)!=item["sha256"]:
            raise ValueError("Recorded tested input changed: "+item["path"])
    args.output_directory.mkdir(parents=True,exist_ok=True)
    output=args.output_directory.resolve()
    bundle_name="BASS_HE_ac6042_to_"+source[:8]+".bundle"
    with tempfile.TemporaryDirectory(prefix="state04_bundle_",dir=output) as temporary:
        bundle=Path(temporary)/bundle_name
        git(repo,"bundle","create",str(bundle),"HEAD","^"+BASE)
        git(repo,"bundle","verify",str(bundle))
        heads=git(repo,"bundle","list-heads",str(bundle)).decode().splitlines()
        if not any(line.split()[0]==source for line in heads):raise ValueError("Bundle does not bind requested HEAD")
        bundle_raw=bundle.read_bytes()
    bundle_member="_git/"+bundle_name
    files[bundle_member]=bundle_raw;modes[bundle_member]="100644"
    context={"schema":"HE_STATE04_SOURCE_CONTEXT_V1","unit_id":"HE-EXP-STATE-04","repository":"cosmosapjw-quantum/BASS_HE","source_commit":source,"source_tree":tree,"bundle_base_prerequisite":BASE,"bundle_member":bundle_member,"bundle_sha256":sha(bundle_raw),"legacy_DRIFT02_filename_set_count":len(LEGACY_DRIFT02_FILES),"source_scope":"Committed whole program_expansion plus original DRIFT02 dependency filenames and root AGENTS; current committed bytes","excluded":"PDF","scientific_execution":False,"source_published":False,"restore":["Extract the ZIP into an empty directory and read STATE04 HANDOFF/RESULT/review/raw evidence.","To restore Git history, use a repository containing base ac6042 and fetch the bundled HEAD. The Git bundle is a real base..HEAD delta, not a claim that prerequisites are embedded.","Reuse saved validation; do not replay unchanged science by default."]}
    files["ARCHIVE_CONTEXT.json"]=encoded(context)
    manifest={"schema":"HE_STATE04_SOURCE_ARCHIVE_MANIFEST_V1","source_commit":source,"source_tree":tree,"legacy_DRIFT02_dependency_filenames":list(LEGACY_DRIFT02_FILES),"committed_source_file_count":len(entries),"files":[{"path":name,"bytes":len(raw),"sha256":sha(raw),"git_blob":entries[name][1] if name in entries else None} for name,raw in sorted(files.items())],"manifest_self_hash":"Excluded; bound by outer receipt"}
    files["SOURCE_MANIFEST.json"]=encoded(manifest)
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w",compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
        for name,raw in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_STORED;info.external_attr=int(modes.get(name,"100644"),8)<<16
            archive.writestr(info,raw)
    archive_raw=buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
        if archive.testzip() is not None or archive.namelist()!=sorted(files):raise ValueError("ZIP CRC/member order mismatch")
        for name,raw in files.items():
            saved=archive.read(name)
            if len(saved)!=len(raw) or sha(saved)!=sha(raw):raise ValueError("ZIP member mismatch: "+name)
    name="BASS_HE_HE_EXP_STATE04_SOURCE_20261027_"+source[:8]+".zip"
    archive_path=output/name
    receipt={"schema":"HE_STATE04_SOURCE_ARCHIVE_RECEIPT_V1","status":"PASS_BASIC_SOURCE_BUNDLE_ZIP_VERIFICATION","source_commit":source,"source_tree":tree,"archive":{"filename":name,"path":str(archive_path),"bytes":len(archive_raw),"sha256":sha(archive_raw),"members":len(files)},"bundle":{"filename":bundle_name,"bytes":len(bundle_raw),"sha256":sha(bundle_raw),"base_prerequisite":BASE},"checks":{"committed_tree_blobs":True,"original_179_filename_set_included":True,"tested_inputs_unchanged":True,"actual_Git_bundle":True,"ZIP_STORED_sorted_fixeddate":True,"CRC_and_member_hashes":True},"scientific_executions":0,"external_writes":0,"builder_sha256":sha(Path(__file__).read_bytes())}
    create(archive_path,archive_raw);create(output/bundle_name,bundle_raw)
    create(archive_path.with_suffix('.manifest.json'),encoded(manifest));create(archive_path.with_suffix('.receipt.json'),encoded(receipt))
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=="__main__":main()
