from pathlib import Path
import shlex,subprocess,hashlib,json,concurrent.futures,sys
base=Path(__file__).resolve().parent
items=[]
for line in (base/(sys.argv[1] if len(sys.argv)>1 else 'PACKAGE_URIS.txt')).read_text().splitlines():
 if not line.startswith("'"):continue
 url,name,size,digest=shlex.split(line);algorithm,value=digest.split(':',1)
 assert algorithm=='SHA512'
 items.append({'url':url,'name':name,'bytes':int(size),'sha512':value})
assert sum(i['bytes'] for i in items)<200*1024**2
print('packages',len(items),'bytes',sum(i['bytes'] for i in items),flush=True)
def fetch(i):
 p=base/'packages'/i['name'];subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','120','--output',str(p),i['url']],check=True)
 data=p.read_bytes();assert len(data)==i['bytes'];assert hashlib.sha512(data).hexdigest()==i['sha512'];i['sha256']=hashlib.sha256(data).hexdigest();return i
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:verified=list(pool.map(fetch,items))
(base/('EXTRA_PACKAGE_IDENTITIES.json' if len(sys.argv)>1 else 'PACKAGE_IDENTITIES.json')).write_text(json.dumps(verified,indent=2)+'\n')
for i in verified:subprocess.run(['dpkg-deb','-x',str(base/'packages'/i['name']),str(base/'root')],check=True)
print('VERIFIED_AND_EXTRACTED',len(verified),flush=True)
