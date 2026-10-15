#!/usr/bin/env python3
"""Finite command capture for AX02/AX13 preparation; no solver dispatch."""
import json, pathlib, resource, subprocess, sys, time
base=pathlib.Path(sys.argv[1]); label=sys.argv[2]; argv=sys.argv[3:]
base.mkdir(parents=True,exist_ok=True)
t0=time.monotonic(); before=resource.getrusage(resource.RUSAGE_CHILDREN)
with (base/(label+'.stdout')).open('wb') as out, (base/(label+'.stderr')).open('wb') as err:
 p=subprocess.run(argv,stdout=out,stderr=err)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
r=dict(argv=argv,cwd=str(pathlib.Path.cwd()),exit=p.returncode,wall_seconds=time.monotonic()-t0,cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,max_rss_kib=after.ru_maxrss)
(base/(label+'.json')).write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r)); sys.exit(p.returncode)
