"""Bounded literature/code acquisition only. Never imports or executes downloaded code."""
from __future__ import annotations
import concurrent.futures as cf
import datetime as dt
import hashlib, html, json, os, pathlib, re, shutil, subprocess, time, urllib.request, urllib.parse, zipfile
from html.parser import HTMLParser

ROOT=pathlib.Path('collected'); ROOT.mkdir(exist_ok=False)
START=time.monotonic(); DEADLINE=START+360
MAX_ITEM=100*1024*1024
UA='WU088-research-archive/1.0 (public scholarly sources; no credential or paywall bypass)'

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.pdfs=[]; self.href=None; self.text=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').lower() in ('citation_pdf_url','dc.identifier'):
            v=a.get('content','')
            if '.pdf' in v.lower(): self.pdfs.append(v)
        if tag=='a': self.href=a.get('href'); self.text=[]
    def handle_data(self,s):
        if self.href is not None: self.text.append(s)
    def handle_endtag(self,tag):
        if tag=='a' and self.href is not None:
            self.links.append((self.href,' '.join(self.text))); self.href=None

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def download(url):
    if time.monotonic()>DEADLINE: raise TimeoutError('overall acquisition cap')
    if urllib.parse.urlsplit(url).scheme not in ('http','https'):raise ValueError('non-HTTP URL')
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'})
    began=time.monotonic()
    with urllib.request.urlopen(req,timeout=20) as r:
        if r.headers.get('Content-Length') and int(r.headers['Content-Length'])>MAX_ITEM:raise ValueError('per-item byte cap')
        parts=[]; total=0
        while True:
            b=r.read(1024*1024)
            if not b:break
            total+=len(b)
            if total>MAX_ITEM or time.monotonic()-began>90 or time.monotonic()>DEADLINE:raise ValueError('byte/time cap')
            parts.append(b)
        data=b''.join(parts)
        meta={'requested_url':url,'final_url':r.url,'http_status':r.status,'retrieved_utc':now(),
              'headers':{k:r.headers.get(k) for k in ('Content-Type','Content-Length','ETag','Last-Modified')},
              'bytes':len(data),'sha256':sha(data)}
        return data,meta

def put(directory,name,data):
    p=ROOT/directory/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return str(p.relative_to(ROOT))
def kind(data):
    if data[:5]==b'%PDF-':return 'pdf'
    if data[:2]==b'PK':return 'zip'
    if data[:2]==b'\x1f\x8b':return 'tar.gz'
    if data[:6]==b'\xfd7zXZ\x00':return 'tar.xz'
    if data[:3]==b'BZh':return 'tar.bz2'
    return 'html' if b'<html' in data[:5000].lower() or b'<!doctype html' in data[:5000].lower() else 'text'
def blocked_page(data):
    s=data[:15000].lower()
    return any(x in s for x in (b'<title>just a moment',b'<title>access denied',b'<title>robot check',b'verify you are human',b'anubis_version'))

def acquire(spec):
    out=dict(spec);out['attempts']=[];out['assets']=[]
    queue=list(spec.get('urls',[])); seen=set()
    if spec.get('repo'):
        try:
            repo=spec['repo']; ref=spec.get('ref')
            if not ref:
                data,meta=download('https://api.github.com/repos/'+repo)
                info=json.loads(data);ref=info['default_branch']
                out['repo_metadata_path']=put('metadata',spec['id']+'_repository.json',data)
            data,meta=download('https://api.github.com/repos/'+repo+'/commits/'+urllib.parse.quote(ref,safe=''))
            c=json.loads(data); commit=c['sha'];out['resolved_commit']=commit;out['resolved_tree']=c['commit']['tree']['sha'];out['requested_ref']=ref
            out['commit_metadata_path']=put('metadata',spec['id']+'_commit.json',data)
            queue.insert(0,'https://codeload.github.com/'+repo+'/tar.gz/'+commit)
        except Exception as e:out['attempts'].append({'phase':'resolve_commit','error':str(e)})
    wanted=spec['wanted']
    while queue and len(seen)<7:
        url=queue.pop(0)
        if url in seen:continue
        seen.add(url)
        try:
            data,m=download(url);typ=kind(data)
            if blocked_page(data):raise ValueError('challenge/access page, not source')
            if wanted=='pdf' and typ!='pdf':
                if typ=='html':
                    fn=spec['id']+'_landing_'+str(len(out['assets']))+'.html'
                    m['path']=put('landing_pages',fn,data);m['representation']='HTML_SNAPSHOT_NOT_FULLTEXT_CERTIFIED';out['assets'].append(m)
                    parser=Links();parser.feed(data.decode('utf-8','replace'))
                    discovered=parser.pdfs+[v for v,t in parser.links if ('.pdf' in v.lower() or 'pdfft' in v.lower()) and ('pdf' in t.lower() or 'fulltext' in v.lower() or 'pdfft' in v.lower())]
                    for v in discovered[:3]:
                        resolved=urllib.parse.urljoin(m['final_url'],html.unescape(v))
                        if resolved not in seen:queue.append(resolved)
                out['attempts'].append({'url':url,'status':'WRONG_REPRESENTATION','actual':typ});continue
            if wanted=='archive' and typ not in ('zip','tar.gz','tar.xz','tar.bz2'):
                out['attempts'].append({'url':url,'status':'WRONG_REPRESENTATION','actual':typ});continue
            if typ=='zip':
                import io
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    if z.testzip() is not None:raise ValueError('bad ZIP CRC')
            m['path']=put('papers' if typ=='pdf' else 'code' if wanted=='archive' else 'documents',spec['id']+'.'+typ,data)
            m['representation']='PDF_BYTES_TITLE_NOT_YET_VERIFIED' if typ=='pdf' else 'SOURCE_ARCHIVE_SNAPSHOT' if wanted=='archive' else 'HTML_OR_TEXT_SNAPSHOT'
            out['assets'].append(m);out['status']='ACQUIRED';out['acquired_representation']=m['representation'];return out
        except Exception as e:out['attempts'].append({'url':url,'error':str(e)})
    out['status']='METADATA_ONLY' if out['assets'] else 'NOT_ACQUIRED'
    return out

CITED=json.loads(pathlib.Path('cited_urls.json').read_text())
specs=[{'id':f'URL{i+1:02d}','title':'Original report citation URL','scope':'REPORT_CITED_URL','wanted':'html','urls':[u]} for i,u in enumerate(CITED)]
papers=[
('P01','Johansson: Numerical integration in arbitrary-precision ball arithmetic','1802.07942',[]),
('P02','Johansson: Arb, efficient arbitrary-precision midpoint-radius interval arithmetic','1611.02831',[]),
('P03','On the Petras algorithm for verified integration of piecewise analytic functions','1603.03945',[]),
('P04','Petras: Self-validating integration and approximation of piecewise analytic functions',None,['https://www.sciencedirect.com/science/article/pii/S0377042701005866/pdfft?isDTMRedir=true&download=true','https://www.sciencedirect.com/science/article/pii/S0377042701005866']),
('P05','Makino Berz: Taylor models and other validated functional inclusion methods',None,['https://bt.pa.msu.edu/pub/papers/TMIJPAM03/TMIJPAM03.pdf','https://www.researchgate.net/profile/Martin-Berz/publication/247699712_Taylor_models_and_other_validated_functional_inclusion_methods/links/02e7e5373627045452000000/Taylor-models-and-other-validated-functional-inclusion-methods.pdf']),
('P06','Gautschi Varga: Error Bounds for Gaussian Quadrature of Analytic Functions',None,['https://epubs.siam.org/doi/pdf/10.1137/0720087','https://epubs.siam.org/doi/10.1137/0720087']),
('P07','Rump: Verified bounds for singular values, in particular for the spectral norm of a matrix and its inverse',None,['https://link.springer.com/content/pdf/10.1007/s10543-010-0294-0.pdf','https://www.researchgate.net/publication/225641170_Verified_bounds_for_singular_values_in_particular_for_the_spectral_norm_of_a_matrix_and_its_inverse']),
('P08','Ogita Rump Oishi: Accurate Sum and Dot Product',None,['https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf','https://epubs.siam.org/doi/pdf/10.1137/030601818']),
('P09','Mikkelsen Lopez-Villellas: How Accurate is Richardson\'s Error Estimate?',None,['https://umu.diva-portal.org/smash/get/diva2:2014645/FULLTEXT01.pdf','https://onlinelibrary.wiley.com/doi/pdf/10.1002/cpe.70305','https://onlinelibrary.wiley.com/doi/full/10.1002/cpe.70305']),
('P10','Johansson Mezzarobba: Fast and rigorous arbitrary-precision computation of Gauss-Legendre quadrature nodes and weights','1802.03948',[]),
('P11','Gonnet: A review of error estimation in adaptive quadrature','1003.4629',[])]
for sid,title,arxiv,urls in papers:
    if arxiv:urls=['https://arxiv.org/pdf/'+arxiv,'https://export.arxiv.org/pdf/'+arxiv]
    specs.append({'id':sid,'title':title,'scope':'REPORT_PAPER' if int(sid[1:])<=9 else 'PRIOR_THREAD_SUPPLEMENT','wanted':'pdf','urls':urls})
repos=[('C01','flintlib/flint','v3.4.0','PROJECT_PIN_NOT_INSTALL'),('C02','flintlib/flint','v3.6.0','UPSTREAM_SURVEY_NOT_ADOPTION'),('C03','flintlib/arb',None,'HISTORICAL_ARCHIVE'),('C04','numpy/numpy','v2.3.5','HISTORICAL_PRODUCER_REFERENCE'),('C05','CAPDGroup/CAPD',None,'SURVEY_SNAPSHOT_NOT_BUILD'),('C06','spockcc/ccpe2025-richardson',None,'SURVEY_PAPER_REPRODUCIBILITY_CODE'),('C07','chebfun/chebfun',None,'PRIOR_THREAD_METHOD_REFERENCE')]
for sid,repo,ref,role in repos:specs.append({'id':sid,'title':repo,'scope':'SURVEY_CODE','wanted':'archive','urls':[],'repo':repo,'ref':ref,'role':role})
assets=[
('C08','MPFR 4.2.2 release','archive',['https://www.mpfr.org/mpfr-4.2.2/mpfr-4.2.2.tar.xz','https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.2.tar.xz']),
('C09','GMP 6.3.0 release','archive',['https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz','https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz']),
('C10','MPFI 1.5.4 release','archive',['https://perso.ens-lyon.fr/nathalie.revol/software/mpfi-1.5.4.tar.gz','https://perso.ens-lyon.fr/nathalie.revol/mpfi-1.5.4.tar.gz','https://gitlab.inria.fr/mpfi/mpfi/-/archive/1.5.4/mpfi-1.5.4.tar.gz']),
('D01','FLINT 3.4.0 manual','pdf',['https://flintlib.org/doc/flint-3.4.0.pdf','https://flintlib.org/flint-3.4.0.pdf']),
('D02','MPFR 4.2.2 manual','pdf',['https://www.mpfr.org/mpfr-4.2.2/mpfr.pdf']),
('D03','SysV AMD64 ABI 0.99','pdf',['https://refspecs.linuxfoundation.org/elf/x86_64-abi-0.99.pdf']),
('D04','GMP 6.3.0 manual','pdf',['https://gmplib.org/gmp-man-6.3.0.pdf']),
('D05','Trefethen Chebyshev coefficient bound exposition','html',['https://www.chebfun.org/examples/approx/EntireBound.html']),
('D06','INTLAB acquisition and license conditions','html',['https://www.tuhh.de/ti3/rump/intlab/Obtain_INTLAB.shtml']),
('D07','FLINT3.4 acb_calc source documentation','text',['https://raw.githubusercontent.com/flintlib/flint/v3.4.0/doc/source/acb_calc.rst']),
('D08','FLINT3.4 acb_hypgeom source documentation','text',['https://raw.githubusercontent.com/flintlib/flint/v3.4.0/doc/source/acb_hypgeom.rst']),
('D09','MPFR4.2.2 upstream detached signature','text',['https://www.mpfr.org/mpfr-4.2.2/mpfr-4.2.2.tar.xz.asc']),
('D10','GMP6.3.0 upstream detached signature','text',['https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz.sig'])]
for sid,title,wanted,urls in assets:specs.append({'id':sid,'title':title,'scope':'PINNED_DOC_OR_DEPENDENCY','wanted':wanted,'urls':urls})
put('provenance','acquisition_requests.json',json.dumps(specs,indent=2).encode())
results=[]
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(acquire,specs):
        results.append(result)
        print(result['id'],result['status'],sum(a.get('bytes',0) for a in result['assets']),flush=True)
        (ROOT/'ACQUISITION_RESULTS.json').write_text(json.dumps(results,indent=2))
results.extend([
 {'id':'C11','title':'INTLAB implementation','scope':'SURVEY_CODE','status':'NOT_ACQUIRED_LICENSE_OR_REGISTRATION_REQUIRED','assets':[],'note':'Official acquisition conditions retained; no registration, license acceptance or payment performed.'},
 {'id':'C12','title':'Taylor models / COSY lineage implementation','scope':'SURVEY_CODE','status':'NO_EXACT_IMPLEMENTATION_IDENTIFIED_BY_SURVEY','assets':[],'note':'Method paper targeted. Do not invent a version or substitute an unrelated implementation.'}])
(ROOT/'ACQUISITION_RESULTS.json').write_text(json.dumps(results,indent=2))
manifest=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(ROOT.rglob('*')) if p.is_file()]
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile('acquired.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(ROOT))
subprocess.run(['openssl','cms','-encrypt','-binary','-aes-256-cbc','-in','acquired.zip','-outform','DER','-out','payload.cms','recipient.pem'],check=True)
receipt={'schema':'WU088_ARCHIVE_TRANSPORT_V1','created_utc':now(),'task':'public-source acquisition only; no downloaded code executed','github_run_id':os.getenv('GITHUB_RUN_ID'),'github_sha':os.getenv('GITHUB_SHA'),'plain_archive_bytes':pathlib.Path('acquired.zip').stat().st_size,'plain_archive_sha256':sha(pathlib.Path('acquired.zip').read_bytes()),'encrypted_bytes':pathlib.Path('payload.cms').stat().st_size,'encrypted_sha256':sha(pathlib.Path('payload.cms').read_bytes()),'request_count':len(specs),'result_count':len(results),'acquired_count':sum(r['status']=='ACQUIRED' for r in results),'science_commands':0,'downloaded_code_executions':0,'contains_private_inputs':False}
pathlib.Path('TRANSPORT.json').write_text(json.dumps(receipt,indent=2))
pathlib.Path('acquired.zip').unlink();shutil.rmtree(ROOT)
print(json.dumps(receipt),flush=True)
