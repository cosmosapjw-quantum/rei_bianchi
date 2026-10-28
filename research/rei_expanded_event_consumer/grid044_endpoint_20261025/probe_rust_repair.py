"""Targeted repair of observed lld thread creation failure; no re-extraction."""
import json
from pathlib import Path
import subprocess
import sys

dest=Path(sys.argv[1]);rustc=dest/'bin/rustc';probe=dest/'probe.rs'
cmd=[str(rustc),str(probe),'--edition=2021','-C','codegen-units=1',
     '-C','link-arg=-Wl,--threads=1','-o',str(dest/'probe_single_worker')]
compiled=subprocess.run(cmd,capture_output=True,text=True)
run=subprocess.run([str(dest/'probe_single_worker')],capture_output=True,text=True) if compiled.returncode==0 else None
out={'status':'RUST_PASS' if run is not None and run.returncode==0 else 'EXECUTION_FAILED',
     'command':cmd,'compile_exit':compiled.returncode,'compile_stderr':compiled.stderr,
     'probe_stdout':run.stdout if run else None,
     'diagnosis':'original lld link attempted unavailable worker creation',
     'repair':'one codegen unit and one lld link thread; no model, source or tolerance change',
     'previous_failure_receipt':'execution/toolchain01/stderr.log; TOOLCHAIN_RECEIPT.json'}
Path(__file__).with_name('TOOLCHAIN_REPAIR_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
raise SystemExit(0 if out['status']=='RUST_PASS' else 1)
