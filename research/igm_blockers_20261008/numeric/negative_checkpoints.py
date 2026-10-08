import json,subprocess,tempfile,shutil,hashlib
from pathlib import Path
r=Path(__file__).parent.resolve();exe=r/'progressive-support/driver/target/release/rei_progressive_support';raw=Path('/home/cosmosapjw/Documents/Codex/2026-10-07/task-4/duration-unprojected-20261008/progressive-support/h0008-coarse')
results=[]
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);bad=t/'h0008-coarse';bad.mkdir();shutil.copy(raw/'CONTEXT.bin',bad/'CONTEXT.bin');shutil.copy(raw/'MIGRATION.json',bad/'MIGRATION.json');b=bytearray((raw/'HEAD').read_bytes());b[-1]^=1;(bad/'HEAD').write_bytes(b)
 for label,parent,n in [('wrong_immutable_head',bad,48),('wrong_partial_n',raw,96)]:
  out=t/label;p=subprocess.run([str(exe),'migrate-partial',str(parent),str(out),str(n),'20'],capture_output=True,text=True);results.append({'test':label,'exit':p.returncode,'output':p.stderr.strip(),'no_output_created':not out.exists(),'passed':p.returncode==2 and not out.exists()})
 # Canonical decoder refuses omitted/duplicated tracked payload and damaged envelope before science.
 original=(r/'coarse'/'HEAD').read_bytes()
 magic=original[:original.index(b'\n')+1]
 def rehash(b):
  body=b[len(magic)+65:];return magic+hashlib.sha256(body).hexdigest().encode()+b'\n'+body
 epoch=bytearray(original);body=len(magic)+65;ctxsize=int.from_bytes(epoch[body:body+8],'little');stateoffset=body+8+ctxsize+16;epoch[stateoffset:stateoffset+8]=__import__('struct').pack('<d',0.)
 omitted=bytearray(original);ledgerstart=len(omitted)-760;omitted[ledgerstart+2*56+16:ledgerstart+2*56+32]=b'\0'*16
 for label,b in [('missing_loss',bytes(omitted)),('duplicate_loss',original+original[-32:]),('wrong_epoch',bytes(epoch))]:
  root=t/label;root.mkdir();(root/'HEAD').write_bytes(rehash(b));p=subprocess.run([str(exe),'resume','unused',str(root),'48','11'],capture_output=True,text=True);results.append({'test':label,'exit':p.returncode,'output':p.stderr.strip(),'passed':p.returncode==2 and ('MISSING_OWNER_LOSS_OR_COEFFICIENT' if label=='missing_loss' else 'NEW_ACCEPTED_CLOCK') in p.stderr,'science_after_startup':p.stderr.endswith('COUNTS=[1, 1, 0]\n')})
(r/'NEGATIVE_CHECKPOINTS.json').write_text(json.dumps({'passed':all(x['passed'] for x in results),'tests':results},indent=2)+'\n');print(json.dumps({'passed':all(x['passed'] for x in results),'tests':len(results)}));raise SystemExit(0 if all(x['passed'] for x in results) else 1)
