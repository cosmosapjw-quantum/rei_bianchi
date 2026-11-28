"""Durable cumulative source ZIPs; no scientific computation or result mutation."""
from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1]
STAGES={
2:['authority/LITERATURE_MAP.md','src/API_SPEC.md'],
3:['theory/DERIVATION_KO.md','verification/REFERENCE_CONTRACT.json'],
4:['theory/ALTERNATIVES.md','EXECUTION_LEDGER.json'],
5:['src/aggregate.py','src/cli.py','verification/independent_reference.py','verification/run_reference.py','verification/compare_saved.py'],
6:['tests/test_aggregate.py','reviews/PHYS_MATH_CODE_AUDIT.md','README.md','results/TESTS.log','results/TESTS.time'],
7:['verification/WOLFRAM_SCOPED_CHECK.wl','verification/WOLFRAM_RESULT.json','results/PRIMARY.json','results/REFERENCE.json','results/INDEPENDENT_ASSESSMENT.json','results/PRIMARY.time','results/REFERENCE.time'],
8:['verification/render_saved.py','figures/VISUAL_REVIEW.md','figures/GL2022_PRINTED_TOTAL_RATE.svg','figures/GL2022_PRINTED_TOTAL_RATE.png','figures/GL2022_PRINTED_HALF_WIDTH.svg','figures/GL2022_PRINTED_HALF_WIDTH.png','results/RENDER.time'],
9:['theory/REUSABLE_STATEMENT.md','SCIENTIFIC_DECISIONS.json'],
10:['REPORT_KO.md','HANDOFF_KO.md','CLOSEOUT.json','checkpoints/build_stages.py']
}
# Stage proof/coding already performed and tested; checkouts represent durable disclosure/publication boundaries.
assert all((P/name).is_file() for grp in STAGES.values() for name in grp)
chosen=['CONTRACT.json','authority/PUBLISHED_TWO_POINT_TRANSCRIPTION.json','authority/SOURCE_SCOPE.md','checkpoints/S01.json','checkpoints/S01_MANIFEST.json']
for n in range(2,11):
    sn=f'S{n:02d}'
    work=2*n if n<=8 else (17 if n==9 else 19)
    stages={'R':f'R{n}','C':f'C{n}' if n!=9 else 'C9_NOT_RUN_NATIVE_DIFFERENT_AUTHOR'}
    meta={
     'schema':'WU_R17A_SCIENTIFIC_STAGE_RECEIPT_V1','checkpoint':sn,'selected_stage':stages,
     'cumulative_scoped_workflow_completed':f'{work}/20','WU_DAG':'33/48','central_REI_DAG':'28/88',
     'new_DAG_nodes':0,'native_physical_input':'INPUT_PENDING','new_physical_admission':False,
     'independent_native_C9':'NOT_RUN' if n>=9 else 'FUTURE','work_evidence':STAGES[n],
     'delivery_state_at_source_creation':'ACTUAL_REMOTE_PROVIDER_ACKS_RECORDED_SEPARATELY',
     'note':'Completed old R16/R17 source C9 was NOT replayed. The published aggregate source cannot replace the native state row.'
    }
    (P/f'checkpoints/{sn}.json').write_text(json.dumps(meta,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    chosen+=STAGES[n]+[f'checkpoints/{sn}.json']
    man={key:{'bytes':(P/key).stat().st_size,'sha256':hashlib.sha256((P/key).read_bytes()).hexdigest()} for key in chosen}
    manifest_path=f'checkpoints/{sn}_MANIFEST.json'
    (P/manifest_path).write_text(json.dumps({'schema':'WU_R17A_STAGE_MANIFEST_V1','checkpoint':sn,'members':man},indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    chosen.append(manifest_path)
    fn=P/f'delivery/WU_R17A_{sn}_SOURCE_20261029.zip'
    with zipfile.ZipFile(fn,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
     for key in chosen:
      info=zipfile.ZipInfo(key,date_time=(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
      z.writestr(info,(P/key).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(fn) as z:
     assert z.testzip() is None
     for key,meta in man.items():
      assert hashlib.sha256(z.read(key)).hexdigest()==meta['sha256']
    print(sn,work,'DAG 33/48',fn.stat().st_size,len(chosen),hashlib.sha256(fn.read_bytes()).hexdigest())
