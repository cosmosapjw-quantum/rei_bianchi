import json,pathlib,sys,time
raw,mode,method,n=sys.argv[1:]
if mode=='slow':time.sleep(2)
failed=mode=='fail'
pathlib.Path(raw).write_text(json.dumps({'completed':not failed,'wall_s':0.01,'native_rhs_attempts_including_fd_replay':7,'kind':'PROCESS_TEST_STUB'}))
raise SystemExit(1 if failed else 0)
