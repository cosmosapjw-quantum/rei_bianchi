"""Independent PDF text-engine source readback; not a distinct-author audit."""
from pathlib import Path
import hashlib
import json
import re
import fitz
SOURCE=Path(__file__).resolve().parents[1]/'sources/GL2022_CSIC_supplement.pdf'
RECORD=Path(__file__).resolve().parents[1]/'sources/GL2022_700_SOURCE.json'
TOK=re.compile(r'^(?:\d+(?:\.\d*)?|\.\d+)\(\d{2}\)$')

def read_independent():
    doc=fitz.open(str(SOURCE))
    text='\n'.join(p.get_text('text') for p in doc)
    positions=list(re.finditer(r'\bTable\s+(\d+)\s*:',text))
    chunks={}
    for i,m in enumerate(positions):
        k=int(m.group(1))
        if k in chunks:raise AssertionError('duplicate table '+str(k))
        chunks[k]=text[m.end():positions[i+1].start() if i+1<len(positions) else len(text)]
    data=[]
    for table in range(1,11):
        chunk=chunks[table]
        lines=chunk.splitlines()
        rows=[]
        for jj in range(7):
            tags=[i for i,l in enumerate(lines) if l.strip()==f'(0,{jj})']
            if len(tags)!=1:raise AssertionError(f'PDF independent row initialJ={jj} table={table}: {tags}')
            i=tags[0]
            following=[l.strip() for l in lines[i+1:i+13] if TOK.fullmatch(l.strip())]
            if len(following)<10:raise AssertionError(f'PDF independent token parsing failed j{jj} table{table}: {following}')
            rows.append(following[:10])
        data.append(rows)
    return data

if __name__=='__main__':
  original=json.loads(RECORD.read_text())
  independent=read_independent()
  mismatches=[(jp,j,t,x,y) for jp in range(10) for j in range(7) for t,(x,y) in enumerate(zip(independent[jp][j],original['tokens_jprime_j_T'][jp][j])) if x!=y]
  print(json.dumps({'parser':'pymupdf PyMuPDF textual extraction, not OCR','source_SHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'checked':700,'mismatches':len(mismatches),'first_mismatches':mismatches[:5]},indent=2))
  if mismatches:raise SystemExit(1)
