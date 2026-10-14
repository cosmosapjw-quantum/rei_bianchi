#!/usr/bin/env python3
"""Prepare additive exact-byte tree arguments after the actual final package gate."""
from pathlib import Path
import base64, hashlib, json, stat
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT.parent
OUT=BASE/'phys29_publication_transport'; OUT.mkdir(exist_ok=True)
PREFIX='docs/fastest_track_chat/REI-PHYS29-20261011/'
REPO='cosmosapjw-quantum/rei_bianchi'
existing=set(json.loads((BASE/'phys29_existing_blob_shas.json').read_bytes()))
package=json.loads((BASE/'phys29_finalization/FINAL_PACKAGE_RECEIPT.json').read_bytes())
assert package['status']=='FINAL_PACKAGE_VERIFY_ONLY_PASS'
records=[]; elements=[]; big={}
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc': continue
    raw=p.read_bytes(); rel=p.relative_to(ROOT).as_posix()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    mode='100755' if p.stat().st_mode&stat.S_IXUSR else '100644'
    element={'path':PREFIX+rel,'mode':mode,'type':'blob'}
    if blob in existing:
        element['sha']=blob; method='reuse existing immutable blob'
    elif p.suffix in ['.png','.zip'] or len(raw)>75000:
        element['sha']=blob; method='create immutable blob before tree'
        if blob not in big:
            args={'repository_full_name':REPO,'encoding':'base64','content':base64.b64encode(raw).decode('ascii')}
            file=OUT/(blob+'.json'); text=json.dumps(args,ensure_ascii=False,separators=(',',':')); file.write_text(text)
            big[blob]={'git_blob_sha':blob,'source_relative_path':rel,'bytes':len(raw),'argument_file':str(file),'argument_characters':len(text)}
    else:
        element['content']=raw.decode('utf-8'); method='exact raw bytes decoded to UTF-8 in tree content'
    elements.append(element)
    records.append({'relative_path':rel,'git_path':PREFIX+rel,'mode':mode,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha':blob,'method':method})
tree_file=OUT/'TREE_ELEMENTS.json'; tree_text=json.dumps(elements,ensure_ascii=False,separators=(',',':')); tree_file.write_text(tree_text)
manifest={'repository_full_name':REPO,'prefix':PREFIX,'additions':len(records),'records':records,'big_blobs':list(big.values()),
 'tree_elements_argument_file':str(tree_file),'tree_elements_characters':len(tree_text),
 'existing_blob_reuses':sum('reuse' in x['method'] for x in records),'text_read_policy':'read_bytes().decode(utf-8); preserve inherited CR exactly',
 'outer_archive_in_Git':False,'outer_archive':package['archive']}
(OUT/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='records'},ensure_ascii=False))
