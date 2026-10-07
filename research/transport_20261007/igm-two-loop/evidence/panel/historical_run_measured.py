import subprocess,resource,time,json,sys,pathlib
prefix=pathlib.Path(sys.argv[1]);argv=sys.argv[2:]
t=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
prefix.with_suffix('.log').write_bytes(p.stdout)
prefix.with_suffix('.json').write_text(json.dumps({'argv':argv,'exit_code':p.returncode,'wall_seconds':time.monotonic()-t,'cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'peak_rss_kib':after.ru_maxrss},indent=2)+'\n')
print(p.stdout.decode()); print('exit',p.returncode)
