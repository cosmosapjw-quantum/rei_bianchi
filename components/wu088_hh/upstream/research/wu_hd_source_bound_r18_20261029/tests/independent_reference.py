"""Independent pypdf/Decimal reference; imports no R18 production module."""
from decimal import Decimal, localcontext
import hashlib
import io
import json
import os
from pathlib import Path
import re
import time
from pypdf import PdfReader

leaf=Path(__file__).resolve().parents[1]
source=Path(os.environ["WU_R18_SOURCE_PDF"])
start_cpu=time.process_time();start_wall=time.monotonic()
raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=="a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754"
page=PdfReader(io.BytesIO(raw)).pages[5].extract_text(extraction_mode="layout")
section=page.split("Table 2:",1)[1].split("Table 3:",1)[0]
rows=[line for line in section.splitlines() if re.match(r"^\s*\(0,\s*2\)",line)]
assert len(rows)==1
tokens=re.findall(r"[0-9]+\.[0-9]+\([0-9]+\)",rows[0])
temps=[15,55,105,255,505,1005,1505,2005,2505,3005]
actual=json.loads((leaf/"results/NATIVE_ROW_COMPUTED.json").read_text())
oracle=json.loads((leaf/"reviews/r18_source/INDEPENDENT_SOURCE_REVIEW.json").read_text())
assert len(tokens)==len(actual["cells"])==10
checks=[]
with localcontext() as context:
    context.prec=128
    for i,(token,cell) in enumerate(zip(tokens,actual["cells"])):
        mantissa,exponent=token[:-1].split("(")
        si=Decimal(mantissa).scaleb(-int(exponent)-6)
        n,d=si.as_integer_ratio()
        got=cell["nominal_m3_s_exact"]
        assert n*int(got["denominator"])==d*int(got["numerator"])
        assert token==cell["original_token"]==oracle["cells"][i]["source_token"]
        assert temps[i]==cell["temperature_K"]==oracle["cells"][i]["temperature_K"]
        checks.append({"T_K":temps[i],"token":token,"SI_crossmultiplication":"PASS"})
out={"schema":"wu.r18.independent_reference.v1","algorithm":"pypdf original PDF extraction + Decimal exact scaleb/as_integer_ratio, independent integer crossmultiplication",
     "production_imports":0,"tests":len(checks),"checks":checks,"exit_code":0,
     "source_pdf_sha256":hashlib.sha256(raw).hexdigest(),
     "cpu_seconds":time.process_time()-start_cpu,"wall_seconds":time.monotonic()-start_wall,
     "pypdf_version":__import__("pypdf").__version__}
(leaf/"results/REFERENCE.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:out[k] for k in ["tests","exit_code","cpu_seconds","wall_seconds","pypdf_version"]}))

