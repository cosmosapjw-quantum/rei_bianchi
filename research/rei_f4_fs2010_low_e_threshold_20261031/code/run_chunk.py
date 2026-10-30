from pathlib import Path
import hashlib,sys,json,time
import thresholds as t
ROOT=Path(__file__).resolve().parents[1]
sel=json.loads((ROOT/'evidence/SELECTION.json').read_text())
i=int(sys.argv[1]);ids=sel['groups'][i]
s=time.monotonic();a,b,p=t.run(False,select=ids)
o=ROOT/'results'/'chunks'/('chunk%02d'%i);o.mkdir(parents=True,exist_ok=True)
a.to_csv(o/'AGG192.csv',index=False,float_format='%.17g')
b.to_csv(o/'KERNEL.csv',index=False,float_format='%.17g')
(o/'STATS.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
print(json.dumps({'chunk':i,'epochs':ids,'emission_arrival_rows':len(b),'arrivals':len(a),'physical_primary_eV':p['primary_electron_eV_per_b'],'source_fraction':p['selected_source_fraction'],'elapsed_sec':time.monotonic()-s,'output':str(o)},indent=2))
