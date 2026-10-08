import pathlib,os,sys
r=pathlib.Path(__file__).resolve().parent
binaries=[p for p in (r/'target/debug/deps').glob('ledger_sidecar-*')if p.is_file()and p.suffix==''and os.access(p,os.X_OK)]
p=max(binaries,key=lambda p:p.stat().st_mtime_ns)
os.execv(p,[str(p),*sys.argv[1:]])
