"""Create-only, fsynced source snapshot before a bounded batch."""
import argparse,sys,io,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes,code_identity
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args()
if not a.label.isalnum():raise ValueError('alphanumeric label required')
i=code_identity();buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
 for path in i['files']:z.writestr(path,(ROOT/path).read_bytes())
atomic_create(ROOT/'provenance'/(a.label+'_CODE_SNAPSHOT.zip'),buf.getvalue())
atomic_create(ROOT/'provenance'/(a.label+'_CODE_IDENTITY.json'),json_bytes(i))
print(json_bytes({'label':a.label,'files':len(i['files']),'sha256':i['sha256']}).decode())
