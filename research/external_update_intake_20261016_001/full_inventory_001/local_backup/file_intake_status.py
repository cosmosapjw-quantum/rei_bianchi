import json
from pathlib import Path
base = Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/external_update_intake_20261016_001/full_inventory_001/local_backup')
archive_status = {}
for line in (base / 'ARCHIVE_INDEX.jsonl').open(encoding='utf-8'):
    row = json.loads(line)
    archive_status[row['archive_path']] = row
prior_receipts = {
    '/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_SOURCE012_INPUT_INTAKE_REFRESH005_20261016_v1.zip': 'research/external_update_intake_20261016_001/refresh_005/COLLECTION_RECEIPT.json; source SHA 0ec47d4faef45e683ee1886e4665f1d57e2e8c100c1797348b06ba8f1a9ddc94; content 2c6a16f1b37412c822c8b63db5ed35416bd385ff',
    '/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_SOURCE012_STATIC_SUPPLEMENT_20261016_v1.zip': 'owner-supplied prior verified receipt; SHA bf9b14306cd65373ac63ef5915aafd577365b614f4438bdc498f8e9caabe313f; content d5131cf4f920f1514d44d12e083950de14d0407c',
    '/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_SOURCE012_POSITIVE_REFERENCE_PREPARATION_20261016_v1.zip': 'research/bass_source012_source_age_reference_20261016/preparation_001/delivery/BACKUP_RECEIPT.json; SHA ca3a3baaa8bd4e94efdde6c60a9ebc079646848673e6eed86dd15275a621c995; content 6b976d00e548f84b02f51d32cd20ad265a0d9201',
    '/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/REI_SOURCE012_HELPER_BUILD_PREPARATION_20261016_v1.zip': 'research/bass_source012_source_age_reference_20261016/preparation_002_build/delivery/BACKUP_RECEIPT.json; SHA 55437cd93c04d09a82ff5d97bfc44a8543352ac86ddc348d75aee7e9a92b26ca; content 96b9231685e1ec8060b9f27d6757e2fe61e0b01e'
}
with (base / 'RAW_INVENTORY.jsonl').open(encoding='utf-8') as source, (base / 'FILE_INTAKE_STATUS.jsonl').open('w', encoding='utf-8') as out:
    count = 0
    for line in source:
        row = json.loads(line)
        ap = row['path']
        if ap in archive_status:
            a = archive_status[ap]
            row['content_intake_status'] = a['status']
            row['archive_format'] = a['format']
            row['archive_member_count'] = a.get('member_count')
            row['archive_index_error'] = a.get('error')
        else:
            row['content_intake_status'] = 'METADATA_INVENTORIED_CONTENT_NOT_READ'
        if ap in prior_receipts:
            row['prior_verified_receipt_reused_without_rehash'] = prior_receipts[ap]
        out.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        count += 1
print(json.dumps({'rows': count, 'default_status': 'METADATA_INVENTORIED_CONTENT_NOT_READ', 'archive_statuses_joined': len(archive_status), 'prior_verified_receipts_reused': len(prior_receipts)}, separators=(',', ':')))
