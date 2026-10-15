import datetime,json,resource,subprocess,sys,time
from pathlib import Path
r=Path("research/axbi_goal_20261014/driver/full/signed_continuation_001/repair_001")
a=json.loads(Path("research/axbi_goal_20261014/driver/full/SIGNED_CONTINUATION_REPAIR_AUTHORITY.json").read_text())
kind=sys.argv[1]
if kind=="release_build":
    previous=json.loads((r/"raw/test.metrics.json").read_text());text=(r/"raw/test.stdout").read_text()
    assert previous["exit_code"]==0 and "test result: ok. 1 passed; 0 failed" in text and "running 1 test" in text
argv=a["prescribed_commands"][kind]
start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
with (r/("raw/"+kind+".stdout")).open("wb") as stdout,(r/("raw/"+kind+".stderr")).open("wb") as stderr:
    result=subprocess.run(argv,stdout=stdout,stderr=stderr)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
metrics={"argv":argv,"cwd":str(Path.cwd()),"exit_code":result.returncode,"wall_s":time.monotonic()-start,"cpu_user_s":after.ru_utime-before.ru_utime,"cpu_system_s":after.ru_stime-before.ru_stime,"max_rss_kib":after.ru_maxrss,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
(r/("raw/"+kind+".metrics.json")).write_text(json.dumps(metrics,indent=2)+"\n")
print(json.dumps(metrics));sys.exit(result.returncode)
