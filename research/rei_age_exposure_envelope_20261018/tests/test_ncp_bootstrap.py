"""Exercise the shell entry point at its process boundary, not a native solver."""
import json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_ncp_entry_fetches_donor_then_passes_archive_to_preparer(tmp_path):
    checkout=tmp_path/'checkout';scripts=checkout/'scripts';scripts.mkdir(parents=True)
    shutil.copy(ROOT/'scripts/run_ncp.sh',scripts/'run_ncp.sh')
    (scripts/'fetch_donor.sh').write_text('''#!/bin/bash
set -eu
mkdir -p "$(dirname "$0")/../donors"
touch "$(dirname "$0")/../donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip"
printf 'fetch\\n' >> "$TRACE"
''')
    tools=tmp_path/'bin';tools.mkdir();trace=tmp_path/'trace'
    (tools/'python3').write_text(f'''#!{sys.executable}
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
with open(os.environ['TRACE'],'a') as f:f.write(json.dumps(args)+'\\n')
if args and args[0].endswith('prepare_native.py'):
    if '--archive' not in args:sys.exit(28)
    p=Path(args[args.index('--archive')+1])
    if not p.is_file():sys.exit(29)
''')
    (tools/'cargo').write_text('#!/bin/sh\necho mock-rust-version-for-shell-boundary-test\n')
    for p in tools.iterdir():p.chmod(0o755)
    env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'],TRACE=str(trace),HOME=str(tmp_path))
    result=subprocess.run(['bash',str(scripts/'run_ncp.sh'),str(tmp_path/'repo'),str(tmp_path/'scratch'),'time8'],env=env,capture_output=True,text=True)
    assert result.returncode==0,(result.returncode,result.stderr)
    lines=trace.read_text().splitlines()
    assert lines[0]=='fetch'
    prepare=json.loads(lines[1]);assert '--archive' in prepare
    assert any('run_refinement.py' in str(x) for x in lines)
