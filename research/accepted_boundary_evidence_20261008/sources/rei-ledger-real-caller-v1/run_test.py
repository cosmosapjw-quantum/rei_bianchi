import os,pathlib,sys
r=pathlib.Path(__file__).resolve().parent
bs=[p for p in(r/'target/debug/deps').glob('real_native_receiver-*')if p.is_file()and p.suffix==''and os.access(p,os.X_OK)]
b=max(bs,key=lambda p:p.stat().st_mtime_ns);os.execv(b,[str(b),*sys.argv[1:]])
