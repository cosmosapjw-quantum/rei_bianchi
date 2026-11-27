"""Bounded public-file acquisition only. Never import or execute downloaded code."""
from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path('recovery_payload')
ROOT.mkdir(exist_ok=False)
DEADLINE = time.monotonic() + 240
MAX_BYTES = 24 * 1024 * 1024
ALLOWED_HOSTS = {'www2.math.uni-wuppertal.de', 'www.cs.purdue.edu',
                 'www.bmtdynamics.org', 'bmtdynamics.org', 'cosyinfinity.org',
                 'www.cosyinfinity.org', 'www.tuhh.de'}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlparse(newurl).hostname not in ALLOWED_HOSTS:
            raise ValueError('redirect_host_not_allowlisted')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate(data, kind):
    if kind == 'pdf':
        if not data.startswith(b'%PDF-'):
            raise ValueError('not_pdf_magic')
        return {'format': 'pdf', 'pdf_magic_verified': True}
    if kind == 'postscript':
        if not data.startswith(b'%!PS'):
            raise ValueError('not_postscript_magic')
        return {'format': 'postscript', 'postscript_magic_verified': True}
    if kind == 'tar':
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as archive:
            members = archive.getmembers()
            names = [m.name for m in members]
            # Verify every stored regular member without extracting or executing.
            for member in members:
                if member.isfile():
                    f = archive.extractfile(member)
                    if f is None or len(f.read()) != member.size:
                        raise ValueError('archive_member_size_mismatch')
            return {'format': 'tar', 'archive_integrity_verified': True,
                    'member_count': len(members),
                    'top_level_directories': sorted(set(n.split('/')[0] for n in names)),
                    'members': names, 'extracted': False, 'executed': False}
    if not data.strip() or data.startswith((b'%PDF-', b'%!PS')):
        raise ValueError('not_requested_web_snapshot')
    return {'format': 'html', 'snapshot_not_full_site': True}


def acquire(spec):
    record = dict(spec, acquisition_status='NOT_ACQUIRED', assets=[], attempts=[])
    for url in spec['urls'][:6]:
        if time.monotonic() >= DEADLINE:
            record['attempts'].append({'attempted_url': url, 'utc': now(),
                'http_status_or_error': 'global_deadline', 'failure_class': 'BOUNDED_DEADLINE',
                'retryable': True, 'fallback_attempted': False})
            break
        attempt = {'attempted_url': url, 'utc': now(), 'fallback_attempted': True}
        try:
            if urllib.parse.urlparse(url).hostname not in ALLOWED_HOSTS:
                raise ValueError('initial_host_not_allowlisted')
            request = urllib.request.Request(url, headers={
                'User-Agent': 'WU088-public-literature-archive/2.0 (no scientific execution)'})
            with urllib.request.build_opener(PublicRedirect()).open(request, timeout=25) as response:
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError('asset_byte_limit')
                inspection = validate(data, spec['wanted'])
                extension = {'pdf': 'pdf', 'postscript': 'ps', 'tar': 'tgz', 'html': 'html'}[spec['wanted']]
                path = Path('files') / (spec['id'] + '.' + extension)
                (ROOT / path).parent.mkdir(exist_ok=True)
                (ROOT / path).write_bytes(data)
                record['assets'].append({
                    'source_record_id': spec['id'], 'path': str(path),
                    'bytes': len(data), 'sha256': digest(data),
                    'original_source_url': url, 'final_url': response.geturl(),
                    'original_filename': Path(urllib.parse.urlparse(response.geturl()).path).name,
                    'normalized_local_filename': path.name,
                    'acquisition_utc': now(), 'http_status': response.status,
                    'mime_type_from_http': response.headers.get('Content-Type'),
                    'http_metadata': {k: response.headers.get(k) for k in
                                      ['Content-Length', 'Last-Modified', 'ETag']},
                    'acquired_representation': spec['representation'],
                    'inspection': inspection})
                record['acquisition_status'] = 'ACQUIRED'
                attempt.update(http_status_or_error=response.status, failure_class=None, retryable=False)
                record['attempts'].append(attempt)
                break
        except urllib.error.HTTPError as error:
            code = error.code
            failure = {401: 'AUTHENTICATION_REQUIRED', 403: 'HTTP_FORBIDDEN',
                       404: 'HTTP_NOT_FOUND', 429: 'HTTP_RATE_LIMITED'}.get(code, 'HTTP_SERVER_ERROR' if code >= 500 else 'HTTP_ERROR')
            attempt.update(http_status_or_error=code, failure_class=failure,
                           retryable=code == 429 or code >= 500)
        except Exception as error:
            message = str(error)
            failure = ('NETWORK_TIMEOUT' if 'timed out' in message.lower() else
                       'DNS_FAILURE' if 'name or service' in message.lower() else
                       'WRONG_REPRESENTATION' if 'magic' in message else 'NETWORK_OR_VALIDATION_ERROR')
            attempt.update(http_status_or_error=type(error).__name__ + ': ' + message,
                           failure_class=failure, retryable=failure in ['NETWORK_TIMEOUT', 'DNS_FAILURE'])
        record['attempts'].append(attempt)
    return record


SPECS = [
    {'id': 'P04_RECOVERY', 'parent_id': 'P04', 'wanted': 'postscript',
     'representation': 'author_manuscript', 'tier': 'P2',
     'urls': ['https://www2.math.uni-wuppertal.de/wrswt/xsc/pascal-xsc/software/petras/vipaf.ps']},
    {'id': 'P06_RECOVERY', 'parent_id': 'P06', 'wanted': 'pdf',
     'representation': 'institutional_repository', 'tier': 'P2',
     'urls': ['https://www.cs.purdue.edu/homes/wxg/selected_works/section_08/085.pdf']},
    {'id': 'C14_CINTE', 'parent_id': 'P04', 'wanted': 'tar',
     'representation': 'official_source_archive',
     'urls': ['https://www2.math.uni-wuppertal.de/wrswt/xsc/pascal-xsc/software/petras/cinte.tgz']},
    {'id': 'C14_DESCRIPTION', 'parent_id': 'C14_CINTE', 'wanted': 'html',
     'representation': 'web_snapshot',
     'urls': ['https://www2.math.uni-wuppertal.de/wrswt/xsc/pascal-xsc/software/petras/description.html']},
    {'id': 'C12_OFFICIAL', 'parent_id': 'C12', 'wanted': 'html',
     'representation': 'web_snapshot',
     'urls': ['https://www.bmtdynamics.org/cosy/']},
    {'id': 'C12_MANUAL', 'parent_id': 'C12', 'wanted': 'pdf',
     'representation': 'official_manual', 'version_requested': '10.2',
     'urls': ['https://www.bmtdynamics.org/cosy/manual/COSYProgMan102.pdf']},
]


if __name__ == '__main__':
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(acquire, SPECS))
    (ROOT / 'ACQUISITION_RESULTS.json').write_text(json.dumps(results, indent=2))
    manifest = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                 'sha256': digest(p.read_bytes())} for p in sorted(ROOT.rglob('*')) if p.is_file()]
    (ROOT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2))
    with zipfile.ZipFile('recovery.zip', 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():
                archive.write(p, p.relative_to(ROOT))
    receipt = {'schema': 'WU088_PUBLIC_ACQUISITION_TRANSPORT_V2', 'utc': now(),
               'plain_archive_bytes': Path('recovery.zip').stat().st_size,
               'plain_archive_sha256': digest(Path('recovery.zip').read_bytes()),
               'github_run_id': os.getenv('GITHUB_RUN_ID'), 'github_sha': os.getenv('GITHUB_SHA'),
               'science_commands': 0, 'downloaded_code_executions': 0,
               'numerical_certificate_runs': 0, 'per_url_attempt_limit': 1,
               'legal_fallback_limit': 6, 'results': [
                   {'id': r['id'], 'status': r['acquisition_status']} for r in results]}
    Path('TRANSPORT.json').write_text(json.dumps(receipt, indent=2))
    for r in results:
        print(r['id'], r['acquisition_status'], flush=True)
