"""Persistent explicit-file publication plumbing; no scientific imports."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import time

HELPER=Path('/workspace/scratch/9d364a030876/research27b/repo/research/rei_expanded_event_consumer/cr_integrated_return_20261027/delivery/stage_snapshot.py')

def packet_entry(path):
    path=Path(path)
    data=path.read_bytes()
    return {'path':str(path),'content':data.decode('utf-8'),'bytes':len(data),
            'sha256':hashlib.sha256(data).hexdigest(),
            'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}

def execute(request):
    operation=request['op']
    if operation=='prepare':
        paths=[]
        for item in request.get('writes',[]):
            path=Path(item['path']);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(item['content'].encode('utf-8'));paths.append(str(path))
        paths.extend(request.get('reads',[]))
        packet={'files':[packet_entry(p) for p in dict.fromkeys(paths)]}
        if request.get('packet_path'):
            path=Path(request['packet_path']);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(packet,ensure_ascii=True,separators=(',',':'))+'\n',encoding='ascii')
        return {'packet':packet}
    if operation=='pack':
        old_argv,old_stdin=sys.argv,sys.stdin
        output=io.StringIO();errors=io.StringIO();code=0
        try:
            sys.argv=[str(HELPER)]+request['argv'];sys.stdin=io.StringIO(request.get('stdin',''))
            with contextlib.redirect_stdout(output),contextlib.redirect_stderr(errors):
                try:runpy.run_path(str(HELPER),run_name='__main__')
                except SystemExit as exc:code=exc.code if isinstance(exc.code,int) else (0 if exc.code is None else 1)
        finally:
            sys.argv,sys.stdin=old_argv,old_stdin
        return {'exit_code':code,'stdout':output.getvalue(),'stderr':errors.getvalue()}
    if operation=='read':
        path=Path(request['path']);offset=request.get('offset',0);size=request.get('size',16000)
        with path.open('r',encoding='ascii') as stream:
            stream.seek(offset);chunk=stream.read(size);following=stream.tell()
        return {'path':str(path),'offset':offset,'next_offset':following,'content':chunk,'eof':len(chunk)<size}
    raise ValueError('unknown operation')

if sys.stdin.isatty():
    import termios
    settings=termios.tcgetattr(sys.stdin.fileno());settings[3]&=~(termios.ECHO|termios.ICANON)
    settings[6][termios.VMIN]=1;settings[6][termios.VTIME]=0
    termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,settings)
startup=time.process_time()
print(json.dumps({'event':'ready','pid':os.getpid(),'startup_CPU_s':startup,
                  'budget_owner':'PRESENTATION','startup_charged_once':True}),flush=True)
last=startup
for line in sys.stdin:
    try:
        request=json.loads(line)
        result=execute(request)
        result.update(status='OK',request_id=request.get('id'))
    except BaseException as exc:
        result={'status':'ERROR','error':repr(exc)}
    cumulative=time.process_time()
    result.update(cumulative_process_CPU_s_before_output=cumulative,
                  operation_CPU_s_since_previous_report=cumulative-last,
                  budget_owner='PRESENTATION',report_tail='included in next operation; final tail UNKNOWN_NOT_ZERO')
    last=cumulative
    print(json.dumps(result,ensure_ascii=True,separators=(',',':')),flush=True)
