"""Read GL2022 original supplementary Table 12-28 literals from two separate PDF engines.
Never correct malformed source cells or physics-suspect tokens.
"""
from __future__ import annotations
import hashlib,re,subprocess
from pathlib import Path
import fitz

SOURCE_SHA='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754'
TEMPS=(15,55,105,255,505,1005,1505,2005,2505,3005)
TOKEN_RE=re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)\(\d+\)?')
VALID_RE=re.compile(r'^(?:\d+(?:\.\d*)?|\.\d+)\(\d+\)$')
TABLE_RE=re.compile(r'(?m)^\s*Table\s+(\d+)\s*:')
LABEL_RE=re.compile(r'^\s*\(([01]),\s*(\d+)\)\s*(.*)$')


def validate_original(pdf:Path):
    raw=pdf.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=SOURCE_SHA or len(raw)!=273554: raise ValueError('WRONG ORIGINAL GL2022 PDF')
    return sha


def blocks(text):
    marks=list(TABLE_RE.finditer(text));d={}
    for i,m in enumerate(marks):
        n=int(m.group(1))
        if 12<=n<=28:
            if n in d: raise ValueError('repeated source table')
            d[n]=text[m.end():marks[i+1].start() if i+1<len(marks) else len(text)]
    if list(sorted(d))!=list(range(12,29)):raise ValueError('not 17 exact table headings')
    return d


def parse_poppler(pdf):
    validate_original(pdf)
    result=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,check=True,text=True).stdout
    out=[]
    for table,contents in blocks(result).items():
        for line in contents.splitlines():
            m=LABEL_RE.match(line)
            if not m:continue
            v,j=int(m.group(1)),int(m.group(2)); tokens=TOKEN_RE.findall(m.group(3))
            if len(tokens)!=10: raise ValueError(('Poppler incomplete tokens',table,v,j,len(tokens),line))
            for T,token in zip(TEMPS,tokens):out.append((table,v,j,T,token))
    return out


def parse_fitz(pdf):
    validate_original(pdf)
    d=fitz.open(pdf)
    full='\n'.join(p.get_text(sort=False) for p in d)
    out=[]
    for table,contents in blocks(full).items():
        lines=[s.strip() for s in contents.splitlines() if s.strip()]
        i=0
        while i<len(lines):
            m=LABEL_RE.match(lines[i]);i+=1
            if m is None:continue
            v,j=int(m.group(1)),int(m.group(2));toks=TOKEN_RE.findall(m.group(3))
            while len(toks)<10 and i<len(lines):
                if LABEL_RE.match(lines[i]):break
                toks+=TOKEN_RE.findall(lines[i]);i+=1
            if len(toks)!=10:raise ValueError(('fitz incomplete tokens',table,v,j,toks))
            for T,tok in zip(TEMPS,toks):out.append((table,v,j,T,tok))
    return out


def source_catalog(pdf):
    a,b=parse_poppler(pdf),parse_fitz(pdf)
    if a!=b:
        first=next(((i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)
        raise ValueError(('TWO PDF ENGINES DISAGREE',len(a),len(b),first))
    result=[]
    for tab,v,j,T,token in a:
        vp=0 if tab<=22 else 1;jp=tab-12 if tab<=22 else tab-23
        result.append({'table':tab,'initial_v':v,'initial_J':j,'final_v':vp,'final_J':jp,'T_K':T,'token':token,
                       'source_token_valid':VALID_RE.fullmatch(token) is not None})
    return result

if __name__=='__main__':
    import sys,collections
    data=source_catalog(Path(sys.argv[1]));print('CELLS',len(data),'ROWS',len(data)//10,'BY_TABLE',dict(collections.Counter(x['table'] for x in data)))
    print('MALFORMED',[(x['table'],x['initial_v'],x['initial_J'],x['T_K'],x['token']) for x in data if not x['source_token_valid']])