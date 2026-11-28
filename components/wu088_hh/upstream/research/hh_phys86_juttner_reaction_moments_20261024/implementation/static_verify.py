"""Static source/request checks only. This is not a Wolfram syntax or science run."""
from pathlib import Path
import hashlib,json
U=Path(__file__).resolve().parents[1]
P=U.parent/'hh_phys85_nuclear_particle_ownership_20261024'
def balance(text):
    stack=[];i=0;comment=0;string=False;escape=False
    while i<len(text):
        if comment:
            if text[i:i+2]=='(*': comment+=1;i+=2;continue
            if text[i:i+2]=='*)': comment-=1;i+=2;continue
            i+=1;continue
        c=text[i]
        if string:
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='"': string=False
            i+=1;continue
        if text[i:i+2]=='(*': comment=1;i+=2;continue
        if c=='"': string=True;i+=1;continue
        if c in '[{(': stack.append(c)
        elif c in ']})':
            if not stack or stack.pop()!={']':'[','}':'{',')':'('}[c]: raise ValueError('Unbalanced delimiters')
        i+=1
    if stack or string or comment: raise ValueError('Incomplete delimiters/string/comment')
files=[]
for name in ['recovery','moments']:
    code=(U/f'implementation/{name.upper()}_CLOUD_CODE.wl').read_text();balance(code)
    req=json.loads((U/f'implementation/{name.upper()}_REQUEST_ARGUMENTS.json').read_text())
    assert req=={'code':code,'timeConstraint':60}
    assert 'BeginPackage[' not in code and 'Parallel' not in code and 'NDSolve' not in code
    assert 'PLACEHOLDER' not in code
    files.append({'request':name,'code_bytes':len(code.encode()),'sha256':hashlib.sha256(code.encode()).hexdigest()})
original=(P/'implementation/repair_01/CLOUD_REFERENCE_CODE.wl').read_bytes()
marker=b'(* Concatenate after frozen JSON assignment, event_owner.wl and verifier.'
core=original.split(marker)[0]
assert (U/'source/phys85_repair01_core.wl').read_bytes()==core
assert (U/'implementation/RECOVERY_CLOUD_CODE.wl').read_bytes().startswith(core)
order=json.loads((U/'source_data/PHYS85_EXPECTED_ORDER.json').read_text())
assert len(order['assertion_labels'])==1017
assert hashlib.sha256('\n'.join(order['assertion_labels']).encode()).hexdigest()==order['label_sha256']
result={'status':'PASS_STATIC_ONLY','scientific_executions':0,'wolfram_syntax_evaluation':'NOT_RUN','files':files,'parent_core_unchanged':True,'transport_max_escaped_bytes':8000,'size_method':'Runtime full escaped-envelope measurement; no truncation or split calls. Raw scientific rational lengths not evaluated locally.'}
(U/'verification/STATIC_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
