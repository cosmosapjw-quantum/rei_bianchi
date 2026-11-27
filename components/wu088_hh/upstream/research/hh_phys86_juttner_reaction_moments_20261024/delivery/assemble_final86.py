#!/usr/bin/env python3
"""Assemble a create-only external PHYS86 final delivery JSON from actual receipts."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

BASE = '696eca5cf9f1fcbf722370833535f4144af0a54a'
PROVIDERS = ('Drive', 'Dropbox')
SENSITIVE_KEY = re.compile(r'url|token|password|secret|authorization|cookie|header|credential|signed.?link', re.I)
URL = re.compile(r'https?://[^\s<>"\']+', re.I)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def pairs(items):
    out = {}
    for key, value in items:
        require(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def no_constant(value):
    raise ValueError('nonfinite JSON number forbidden')


def parse(raw):
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=no_constant)
    require(isinstance(value, dict), 'JSON object required')
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(path):
    p = Path(path).absolute()
    require(stat.S_ISREG(p.lstat().st_mode), 'regular non-symlink input required')
    return p


def hash_file(path):
    h, count = hashlib.sha256(), 0
    with regular(path).open('rb') as src:
        while data := src.read(1024 * 1024):
            h.update(data)
            count += len(data)
    return count, h.hexdigest()


def scrub(value, path='', redactions=None):
    if redactions is None:
        redactions = []
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            where = path + '/' + key
            if SENSITIVE_KEY.search(key) or key.lower() in ('request', 'request_contents'):
                redactions.append(where)
                out[key] = '[REDACTED_TRANSPORT_OR_SECRET_FIELD]'
            else:
                out[key] = scrub(item, where, redactions)
        return out
    if isinstance(value, list):
        return [scrub(item, path + '/' + str(i), redactions) for i, item in enumerate(value)]
    if isinstance(value, str) and URL.search(value):
        redactions.append(path)
        return URL.sub('[URL_REMOVED]', value)
    return value


def read_json(path, allow_request=False):
    p = regular(path)
    # Never ingest the live transport request that contains the private signed URL.
    name = p.name.lower()
    require(allow_request or not ('url' in name and ('tmp' in name or 'temporary' in name)),
            'transport request / temporary URL file cannot be embedded')
    raw = p.read_bytes()
    obj = parse(raw)
    require(allow_request or set(obj) != {'url', 'name', 'expected_bytes', 'expected_sha256'}, 'live downloader request cannot be embedded')
    return p, raw, obj


def successful_upload(value):
    if isinstance(value, dict):
        if value.get('success') is True or value.get('upload_success') is True or value.get('status') == 'completed':
            return True
        return any(successful_upload(v) for v in value.values())
    if isinstance(value, list):
        return any(successful_upload(v) for v in value)
    return False


def nested_values(value, keys):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, (str, int)):
                found.append(item)
            found.extend(nested_values(item, keys))
    elif isinstance(value, list):
        for item in value:
            found.extend(nested_values(item, keys))
    return found


def select_upload(value, provider):
    if isinstance(value.get(provider.lower()), dict):
        return value[provider.lower()]
    if isinstance(value.get(provider), dict):
        return value[provider]
    return value


def assemble(args):
    config_path, config_raw, config = read_json(args.request, allow_request=True)
    output = Path(args.output).absolute()
    require(not output.exists(), 'create-only output already exists')
    required = {'repo', 'head', 'tree', 'base', 'stage', 'evidence_identity_path', 'status_path',
                'pack_receipt_path', 'providers', 'stage_history_paths', 'freeze_check_paths', 'provenance_paths'}
    require(required <= set(config), 'required request keys missing: ' + ','.join(sorted(required - set(config))))
    require(config['base'] == BASE, 'fixed PHYS85 base mismatch')
    require(re.fullmatch('[0-9a-f]{40}', config['head']) and re.fullmatch('[0-9a-f]{40}', config['tree']), 'explicit full Git SHA1 identities required')
    require(config['stage'] == 'FINAL', 'final delivery requires a FINAL package')
    repo = Path(config['repo']).resolve()
    commit_raw = subprocess.check_output(['git', '-C', str(repo), 'cat-file', '-p', config['head']])
    header = commit_raw.split(b'\n\n', 1)[0].decode('utf-8').splitlines()
    trees = [line[5:] for line in header if line.startswith('tree ')]
    parents = [line[7:] for line in header if line.startswith('parent ')]
    require(trees == [config['tree']], 'actual Git object tree mismatch')
    subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', BASE, config['head']], check=True)
    sources = []
    payload_by_path = {}

    def attachment(path, role, bind_public=True):
        p, raw, obj = read_json(path)
        require(p != output and output.name not in str(p), 'future external JSON self-reference forbidden')
        if bind_public and p.is_relative_to(repo):
            member = 'repo/' + p.relative_to(repo).as_posix()
            require(member in payload_by_path, 'public input absent from final manifest: ' + member)
            record = payload_by_path[member]
            require((len(raw), sha(raw)) == (record['bytes'], record['sha256']), 'public input differs from final commit bytes: ' + member)
        removed = []
        clean = scrub(obj, redactions=removed)
        meta = {'role': role, 'source_path': str(p), 'bytes': len(raw), 'sha256': sha(raw),
                'redacted_field_paths': removed}
        sources.append(meta)
        return obj, {'provenance': meta, 'receipt': clean}

    pack, pack_embedded = attachment(config['pack_receipt_path'], 'final_pack', bind_public=False)
    require(pack.get('status') == 'PACK_CREATED', 'final pack did not succeed')
    for key in ('commit', 'tree', 'base', 'stage'):
        require(pack.get(key) == config['head' if key == 'commit' else key], 'final pack identity mismatch: ' + key)
    expected_size, expected_sha = pack['archive_bytes'], pack['archive_sha256']
    require(hash_file(pack['archive']) == (expected_size, expected_sha), 'local final ZIP differs from pack receipt')
    require(set(config['providers']) == set(PROVIDERS), 'exactly Drive and Dropbox provider inputs required')
    provider_docs, downloaded_paths, manifests = {}, [], []
    for provider in PROVIDERS:
        spec = config['providers'][provider]
        require(set(spec) == {'upload_receipt_path', 'download_receipt_path', 'restore_receipt_path'}, 'provider input path keys mismatch')
        uploaded, uploaded_doc = attachment(spec['upload_receipt_path'], provider + '_upload', bind_public=False)
        selected_upload = select_upload(uploaded, provider)
        require(successful_upload(selected_upload), provider + ' successful upload ACK absent')
        require(Path(pack['archive']).name in nested_values(selected_upload, {'name', 'file_name', 'title'}), provider + ' upload ACK archive filename mismatch')
        require(any(isinstance(v, str) and v for v in nested_values(selected_upload, {'id', 'file_id'})), provider + ' upload ACK provider ID absent')
        returned_sizes = nested_values(selected_upload, {'size', 'file_size_bytes'})
        require(not returned_sizes or all(v == expected_size for v in returned_sizes), provider + ' upload ACK size mismatch')
        download, download_doc = attachment(spec['download_receipt_path'], provider + '_whole_GET', bind_public=False)
        require(download.get('status') == 'PASS_SINGLE_FULL_GET_REOPENED_BYTES', provider + ' full GET not PASS')
        require(download.get('operation') == 'download' and download.get('get_attempts') == 1 and download.get('automatic_retries') == 0,
                provider + ' must bind exactly one GET without automatic retry')
        require(download.get('http_status') == 200 and download.get('complete_response_read') is True, provider + ' incomplete GET')
        for field in ('expected_bytes', 'actual_bytes', 'bytes_received', 'bytes_written'):
            require(download.get(field) == expected_size, provider + ' GET length mismatch: ' + field)
        require(download.get('expected_sha256') == download.get('actual_sha256') == expected_sha, provider + ' GET SHA mismatch')
        restored, restored_doc = attachment(spec['restore_receipt_path'], provider + '_actual_restore', bind_public=False)
        require(restored.get('status') == 'RESTORE_VERIFIED' and restored.get('operation') == 'restore', provider + ' restore not PASS')
        for key in ('commit', 'tree', 'base', 'stage'):
            require(restored.get(key) == pack.get(key), provider + ' restore identity mismatch: ' + key)
        require((restored.get('archive_bytes'), restored.get('archive_sha256')) == (expected_size, expected_sha), provider + ' restored archive mismatch')
        downloaded = Path(download['output_path']).resolve()
        require(downloaded == Path(restored['archive']).resolve(), provider + ' GET and restore archive paths differ')
        require(not downloaded.samefile(pack['archive']), provider + ' download must be distinct from original local ZIP')
        require(hash_file(downloaded) == (expected_size, expected_sha), provider + ' downloaded file no longer matches')
        downloaded_paths.append(downloaded)
        counts, expected_counts = restored['counts'], pack['counts']
        wanted = {'whole_zip_sha256_checked': 1, 'member_crc_checked': expected_counts['members_including_manifest'],
                  'payload_sha256_checked': expected_counts['payload_members'], 'git_blob_sha1_checked': expected_counts['repository_blobs'],
                  'extracted_members_rehashed': expected_counts['members_including_manifest'],
                  'historical_dependency_whole_bytes_checked': expected_counts['historical_dependencies'],
                  'nested_historical_restore_executions': 0}
        require(all(counts.get(k) == v for k, v in wanted.items()), provider + ' actual restoration counts incomplete')
        manifest_path = Path(restored['extracted_directory']) / 'MANIFEST.json'
        raw_manifest = regular(manifest_path).read_bytes()
        require(sha(raw_manifest) == pack['manifest_sha256'], provider + ' extracted full manifest SHA mismatch')
        manifest = parse(raw_manifest)
        for key in ('commit', 'tree', 'base', 'stage'):
            require(manifest.get(key) == pack.get(key), provider + ' full manifest identity mismatch')
        manifests.append((raw_manifest, manifest))
        provider_docs[provider] = {'upload': uploaded_doc, 'single_full_GET': download_doc, 'actual_full_restore': restored_doc}
    require(downloaded_paths[0] != downloaded_paths[1] and not downloaded_paths[0].samefile(downloaded_paths[1]), 'two distinct actual provider download files required')
    require(manifests[0][0] == manifests[1][0], 'provider extracted manifests differ')
    manifest = manifests[0][1]
    payload_by_path.update({item['path']: item for item in manifest['payload']})
    identity, identity_doc = attachment(config['evidence_identity_path'], 'controller_evidence_identity')
    statuses, statuses_doc = attachment(config['status_path'], 'controller_final_status')
    # Science admission belongs to the controller. Cross-bind its exact bytes and declared
    # descriptor; this mechanical helper neither upgrades nor downgrades those claims.
    require(isinstance(identity.get('descriptor'), dict), 'controller identity descriptor absent')
    canonical = json.dumps(identity['descriptor'], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    require(sha(canonical) == identity.get('evidence_identity_SHA256'), 'controller evidence descriptor SHA256 mismatch')
    require(identity['descriptor'].get('status') == statuses, 'controller evidence identity and final status differ')
    require(statuses.get('HH_R10') == 'OFF' and statuses.get('production_admission') == 'NOT_ISSUED', 'root admission sentinels differ')
    require(config['freeze_check_paths'], 'final freeze receipt required')
    freeze_docs = []
    for path in config['freeze_check_paths']:
        obj, embedded = attachment(path, 'final_byte_freeze')
        require(obj.get('status') == 'PASS' or str(obj.get('status', '')).startswith('PASS_'), 'freeze check not PASS')
        require(not obj.get('mismatches'), 'freeze check contains mismatches')
        freeze_docs.append(embedded)
    stage_docs = [attachment(p, 'historical_stage_ACK')[1] for p in config['stage_history_paths']]
    require(stage_docs, 'actual stage history receipts required')
    provenance_docs = [attachment(p, 'provenance')[1] for p in config['provenance_paths']]
    additional_docs = [attachment(p, 'additional_json')[1] for p in config.get('additional_json_paths', [])]
    document = {'schema': 'PHYS86_FINAL_DELIVERY_V1', 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'repository': 'cosmosapjw-quantum/WU088_HH', 'branch': config.get('branch'), 'pull_request': config.get('pull_request'),
        'identity': {'final_HEAD': config['head'], 'tree': config['tree'], 'parents': parents, 'PHYS85_base_HEAD': BASE,
            'evidence_identity_SHA256': identity['evidence_identity_SHA256'], 'identity_kind': identity.get('identity_kind'),
            'completed_science_identity': statuses.get('completed_science_identity')},
        'claim': statuses_doc, 'controller_evidence_identity': identity_doc,
        'final_zip': {'filename': Path(pack['archive']).name, 'bytes': expected_size, 'sha256': expected_sha,
            'payload_counts': pack['counts'], 'pack_receipt': pack_embedded, 'full_manifest': manifest,
            'manifest_sha256': pack['manifest_sha256'], 'providers': provider_docs},
        'stage_history_ACKs': stage_docs, 'final_freeze_checks': freeze_docs, 'provenance': provenance_docs,
        'additional_json_evidence': additional_docs, 'input_receipt_manifest': sources,
        'assembly_provenance': {'request_bytes': len(config_raw), 'request_sha256': sha(config_raw),
            'helper_sha256': sha(Path(__file__).read_bytes()), 'scientific_executions': 0, 'network_operations': 0,
            'validation_scope': 'Cross-bind existing exact pack, upload ACKs, two single full GET receipts, complete restore counts, extracted manifests, root status and byte-freeze evidence; no scientific evaluation.'},
        'delivery_status': 'FINAL_ZIP_DUAL_FULL_GET_AND_RESTORE_VERIFIED',
        'completed_science_identity': statuses.get('completed_science_identity'), 'scientific_completion_claim': statuses.get('scientific_completion_claim'),
        'HH_R10': statuses.get('HH_R10'), 'production_admission': statuses.get('production_admission'),
        'json_self_reference_policy': 'This immutable external JSON excludes its own future hash, provider IDs, upload acknowledgements and readback results. Root binds those exact bytes externally after creation.',
        'redaction_policy': 'No live URLs, transport request contents, response headers, credentials or secret fields are embedded. Raw input hashes identify the original receipts; sanitized receipts are marked by redacted field paths.'}
    # Final scrub includes optional config metadata and manifest strings.
    document = scrub(document)
    encoded = (json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')
    with output.open('xb') as out:
        out.write(encoded)
    require(output.read_bytes() == encoded, 'created JSON reopen mismatch')
    return {'status': 'FINAL_DELIVERY_JSON_CREATED', 'output': str(output), 'bytes': len(encoded),
            'sha256': sha(encoded), 'completed_science_identity': statuses.get('completed_science_identity'), 'scientific_completion_claim': statuses.get('scientific_completion_claim'),
            'source_receipts': len(sources), 'providers_whole_GET_and_restore': 2,
            'external_json_upload_or_readback': 'NOT_PERFORMED_BY_ASSEMBLER'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, help='JSON containing actual final identity and explicit receipt paths')
    parser.add_argument('--output', required=True, help='fresh external final delivery JSON path')
    args = parser.parse_args()
    try:
        receipt = assemble(args)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        # Do not print input content, URLs, secret values, or arbitrary exception text.
        print(json.dumps({'status': 'ASSEMBLY_FAILED', 'error_type': type(exc).__name__,
                          'reason': str(exc) if isinstance(exc, ValueError) else 'See actual receipt inputs and preserved new output, if any.',
                          'existing_outputs_overwritten': False}, ensure_ascii=False, indent=2))
        return 1


if __name__ == '__main__':
    sys.exit(main())
