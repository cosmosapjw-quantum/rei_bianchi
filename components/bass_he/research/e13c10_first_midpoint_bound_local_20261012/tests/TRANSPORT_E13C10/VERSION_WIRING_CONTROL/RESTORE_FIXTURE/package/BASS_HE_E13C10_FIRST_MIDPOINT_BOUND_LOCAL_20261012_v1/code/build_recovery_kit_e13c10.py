#!/usr/bin/env python3
"""Assemble a deterministic E13C10 kit from finalized, byte-pinned evidence.

Does not restore archives, rehash the large COMPLETE archive, import science,
upload files, alter the sealed package, or authorize new NCP work. For identical
source bytes and --stamp, kit payloads and ZIP ordering/timestamps are fixed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
import zipfile

from restore_transfer_e13c10 import (CHUNK_BYTES, PACKAGE_ROOT, PACKAGE_SCHEMA,
    load_json, pin, safe_relative, save, valid_pin, validate_transfer, verify_file)


KIT_SCHEMA = 'bass-he-e13c10-recovery-kit-manifest-v1'
TRANSFER_NAME = 'BASS_HE_E13C10_TRANSFER_MANIFEST.json'
HELPER_NAME = 'restore_transfer_e13c10.py'


def load(path):
    return load_json(Path(path).read_bytes())


def require(test, message):
    if not test:
        raise ValueError(message)


def copy_payload(source, destination, expected):
    verify_file(source, expected)
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    count = 0
    with source.open('rb') as src, destination.open('xb') as dst:
        for data in iter(lambda: src.read(CHUNK_BYTES), b''):
            dst.write(data)
            digest.update(data)
            count += len(data)
        dst.flush()
        os.fsync(dst.fileno())
    actual = {'bytes': count, 'sha256': digest.hexdigest()}
    require(actual == valid_pin(expected), 'source changed during kit copy: ' + str(source))
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--delivery-dir', type=Path, required=True,
                        help='final COMPLETE build directory containing BUILD_RECEIPT.json and transfer manifest')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stamp', required=True, help='fixed UTC stamp YYYYMMDDTHHMMSSZ')
    parser.add_argument('--handoff', type=Path,
                        help='defaults to sealed package/NCP_HANDOFF_INTERNAL_KO.md')
    parser.add_argument('--backup-locations', type=Path,
                        help='optional owner-recorded actual locations with archive bytes/SHA and parts pins')
    parser.add_argument('--restore-output', type=Path,
                        help='optional completed ACTUAL E13C10 restore directory; copies receipts/logs only')
    parser.add_argument('--extra-file', action='append', default=[], metavar='RELATIVE=PATH',
                        help='optional small evidence payload; never a package mutation')
    args = parser.parse_args()
    started = time.monotonic()
    if not re.fullmatch(r'\d{8}T\d{6}Z', args.stamp):
        raise ValueError('canonical UTC stamp required')
    assembled = datetime.strptime(args.stamp, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).isoformat()
    package = args.package.resolve()
    if (not package.is_dir() or package.name != PACKAGE_ROOT or args.package.is_symlink()):
        raise ValueError('actual regular E13C10 package required')
    output = args.output_dir.resolve()
    if output.exists() or args.output_dir.is_symlink():
        raise FileExistsError('fresh kit output required; preserve prior attempts')
    if output.is_relative_to(package):
        raise ValueError('kit output must be outside sealed package')
    output.mkdir(parents=True, exist_ok=False)
    stage = 'FINALIZED_INPUT_EVIDENCE'
    try:
        delivery = args.delivery_dir.resolve()
        build_path = delivery / 'BUILD_RECEIPT.json'
        transfer_path = delivery / TRANSFER_NAME
        build, transfer = load(build_path), load(transfer_path)
        validate_transfer(transfer)
        require(build.get('schema') == 'bass-he-e13c10-delivery-build-receipt-v1'
                and build.get('status') == 'PASS_ALL_ARCHIVED_PAYLOAD_BYTES',
                'successful actual E13C10 COMPLETE build required')
        require(build['archive'] == valid_pin(transfer['archive']), 'build/transfer archive pin mismatch')
        verify_file(transfer_path, build['transfer_manifest'])
        manifest_path = package / 'PACKAGE_MANIFEST.json'
        verify_file(manifest_path, build['package_manifest'])
        require(build['package_manifest'] == transfer['package_manifest'], 'package manifest pin mismatch')
        package_manifest = load(manifest_path)
        require(package_manifest.get('schema') == PACKAGE_SCHEMA
                and package_manifest.get('package_root') == PACKAGE_ROOT,
                'actual sealed E13C10 package manifest required')
        package_pins = package_manifest['files']
        for key in ('scientific_kernel_calls', 'MPI_invocations', 'NCP_execute_invocations', 'automatic_retries'):
            require(build.get(key) == 0, 'unexpected invocation in COMPLETE builder receipt: ' + key)
        state_path = package / 'CURRENT_STATE.json'
        verify_file(state_path, package_pins['CURRENT_STATE.json'])
        state = load(state_path)
        require('new_NCP_work_units' in state and state['new_NCP_work_units'] == [],
                'this zero-work kit requires explicit empty new_NCP_work_units')
        handoff = args.handoff.resolve() if args.handoff else package / 'NCP_HANDOFF_INTERNAL_KO.md'
        handoff_relative = handoff.relative_to(package).as_posix()
        verify_file(handoff, package_pins[handoff_relative])
        helper = package / 'code' / HELPER_NAME
        verify_file(helper, transfer['restore_helper'])
        verify_file(helper, package_pins['code/' + HELPER_NAME])
        require(transfer['restore_helper']['relative_path'] == HELPER_NAME, 'kit helper name mismatch')
        for name in ('build_complete_e13c10.py', 'build_recovery_kit_e13c10.py'):
            verify_file(package / 'code' / name, package_pins['code/' + name])
        verify_file(Path(__file__), package_pins['code/build_recovery_kit_e13c10.py'])
        sources = {
            HELPER_NAME: (helper, valid_pin(transfer['restore_helper'])),
            TRANSFER_NAME: (transfer_path, pin(transfer_path)),
            'BUILD_RECEIPT.json': (build_path, pin(build_path)),
            'CURRENT_STATE.json': (state_path, package_pins['CURRENT_STATE.json']),
            'NCP_HANDOFF_INTERNAL_KO.md': (handoff, package_pins[handoff_relative]),
            'NEXT_DAG.json': (package / 'NEXT_DAG.json', package_pins['NEXT_DAG.json']),
            'build_complete_e13c10.py': (package / 'code/build_complete_e13c10.py', package_pins['code/build_complete_e13c10.py']),
            'build_recovery_kit_e13c10.py': (package / 'code/build_recovery_kit_e13c10.py', package_pins['code/build_recovery_kit_e13c10.py']),
        }
        remote_status = 'LOCATIONS_IN_EXTERNAL_OWNER_HANDOFF; no remote operation by this builder'
        if args.backup_locations:
            locations = load(args.backup_locations)
            require(valid_pin(locations['archive']) == valid_pin(transfer['archive']),
                    'backup locations name a different complete archive')
            location_parts = locations.get('parts', [])
            if location_parts:
                require(len(location_parts) == len(transfer['parts']), 'backup locations part count mismatch')
                for located, actual in zip(location_parts, transfer['parts']):
                    require(located.get('index') == actual['index'] and valid_pin(located) == valid_pin(actual),
                            'backup locations part order/identity mismatch')
            sources['BACKUP_LOCATIONS.json'] = (args.backup_locations, pin(args.backup_locations))
            remote_status = 'COPIED_OWNER_LOCATION_RECORD; no remote readback or redownload by this builder'
        actual_restore_status = 'NOT_PROVIDED_TO_KIT_BUILDER; restoration not inferred from upload or build'
        if args.restore_output:
            restored = args.restore_output.resolve()
            receipt_path = restored / 'RESTORE_RECEIPT.json'
            restored_receipt = load(receipt_path)
            require(restored_receipt.get('schema') == 'bass-he-e13c10-restore-receipt-v1'
                    and restored_receipt.get('status') == 'PASS_COMPLETE_RESTORE', 'successful actual E13C10 restore required')
            require(restored_receipt.get('archive') == transfer['archive'], 'restored complete archive mismatch')
            require(restored_receipt.get('external_transfer_manifest_sha256') == pin(transfer_path)['sha256'],
                    'restore transfer manifest mismatch')
            for key in ('scientific_kernel_calls', 'MPI_invocations', 'NCP_execute_invocations', 'automatic_retries'):
                require(restored_receipt.get(key) == 0, 'unexpected invocation in actual restore receipt: ' + key)
            require(restored_receipt.get('prior_restore_helper_invocations') == 1,
                    'actual restore did not invoke exactly one pinned predecessor helper')
            nested = restored_receipt['hydrated_E13C9']
            require(nested.get('returncode') == 0, 'actual predecessor hydration did not succeed')
            sources['ACTUAL_RESTORE_RECEIPT.json'] = (receipt_path, pin(receipt_path))
            for key, relative in (('receipt', 'runtime/E13C9/RESTORE_RECEIPT.json'),
                                  ('stdout', 'E13C9_HYDRATE.stdout'), ('stderr', 'E13C9_HYDRATE.stderr')):
                verify_file(restored / relative, nested[key])
                name = 'restore_evidence/' + ('E13C9_RESTORE_RECEIPT.json' if key == 'receipt' else Path(relative).name)
                sources[name] = (restored / relative, valid_pin(nested[key]))
            actual_restore_status = 'COPIED_ACTUAL_BYTE_MATCHED_E13C10_HYDRATION_RECEIPT; no repeat restoration'
        for item in args.extra_file:
            if '=' not in item:
                raise ValueError('--extra-file needs RELATIVE=PATH')
            relative, path = item.split('=', 1)
            safe_relative(relative)
            if relative in sources or relative in {'README_KO.md', 'KIT_PROVENANCE.json', 'KIT_MANIFEST.json'}:
                raise ValueError('duplicate or reserved kit payload name: ' + relative)
            source = Path(path).resolve()
            identity = pin(source)
            if identity['bytes'] > 16 * 1024 ** 2:
                raise ValueError('extra kit evidence must be at most 16 MiB')
            sources[relative] = (source, identity)

        stage = 'COPY_SMALL_KIT_PAYLOADS'
        directory = output / 'RECOVERY_KIT_CONTENTS'
        directory.mkdir(exist_ok=False)
        source_pins = {}
        for relative, (source, identity) in sorted(sources.items()):
            safe_relative(relative)
            actual = copy_payload(source, directory / relative, identity)
            source_pins[relative] = actual
        transfer_pin = pin(transfer_path)
        archive_pin = valid_pin(transfer['archive'])
        helper_pin = valid_pin(transfer['restore_helper'])
        parts_rows = '\n'.join('| %d | %d | `%s` | `%s` |' %
                              (p['index'], p['bytes'], p['canonical_name'], p['sha256']) for p in transfer['parts'])
        readme = f'''# BASS_HE E13C10 recovery kit

이 kit와 E13C10 COMPLETE ZIP 하나 또는 manifest의 모든 조각을 받으면
추가 과학 입력 첨부 없이 predecessor 전체를 복구할 수 있다.
새 NCP 중량 작업은 **0개**다. 완료·채택·미실행의 정확한 범위는 함께 들어 있는
`CURRENT_STATE.json`, `NCP_HANDOFF_INTERNAL_KO.md`, `NEXT_DAG.json`을 따른다.
복구 도구는 과학 코드, MPI, benchmark, 서버 확보를 실행하지 않는다.

## 외부 handoff에서 먼저 확인할 identity

이 kit ZIP 자체의 bytes/SHA는 외부 최종 handoff가 제공한다. kit 내부에
자기 ZIP hash를 넣지 않는다. 외부 handoff의 pin과 다운로드한 실제 bytes를
확인한 뒤 압축을 푼다. 내부 파일의 주요 pin은 다음과 같다.

| 파일 | Bytes | SHA-256 |
|---|---:|---|
| `{HELPER_NAME}` | {helper_pin['bytes']} | `{helper_pin['sha256']}` |
| `{TRANSFER_NAME}` | {transfer_pin['bytes']} | `{transfer_pin['sha256']}` |
| `{transfer['archive']['canonical_name']}` | {archive_pin['bytes']} | `{archive_pin['sha256']}` |

실제 원격 위치는 제공된 `BACKUP_LOCATIONS.json` 또는 외부 owner handoff를 따른다.
이 builder는 업로드나 원격 재다운로드를 수행하지 않았다.

## Drive 조각

| 순서 | Bytes | Canonical name | SHA-256 |
|---:|---:|---|---|
{parts_rows}

파일명에 `.bin`이 붙어도 변경할 필요가 없다. Helper는 실제 bytes/SHA로 조각을
찾고 manifest 순서로 결합한다. 원본 다운로드 이름과 파일은 보존한다.

## 복구 명령

실제 파일 소실 또는 복구 필요가 있을 때 아래 두 source mode 중 하나만 실행한다.
현재 디렉터리는 압축을 푼 kit, 다운로드 디렉터리는 `../downloads`, 출력은 아직
존재하지 않는 `../RESTORED_E13C10_ATTEMPT01`이라고 가정한다.

```bash
python3 -B ./{HELPER_NAME} \\
  --manifest ./{TRANSFER_NAME} \\
  --manifest-sha256 {transfer_pin['sha256']} \\
  --parts-dir ../downloads \\
  --output-dir ../RESTORED_E13C10_ATTEMPT01 \\
  --hydrate
```

COMPLETE ZIP을 받은 경우 위 `--parts-dir ../downloads` 대신 다음 인자를 사용한다.

```bash
--archive ../downloads/{transfer['archive']['canonical_name']}
```

출력은 `<output>/package/{PACKAGE_ROOT}`이며, 이전 E13C9 복구는
`<output>/runtime/E13C9`다. 그 아래의 `runtime/E13C8`에 E13C8이 복구되고,
원래 E13C7 입력과 완료된 heavy return은 그 E13C8 출력의
`runtime/E13C7_INPUT`, `runtime/E13C7_NCP_RETURN`에 있다.

이 COMPLETE ZIP은 `dependencies/E13C9_COMPLETE.zip`과
`dependencies/E13C9_RECOVERY_KIT.zip`을 이미 포함한다. E13C9의 고정 helper가
그 안에 포함된 E13C8과 더 오래된 입력/반환을 한 번씩 펼친다.
새 과학 계산은 수행하지 않는다.

성공 상태는 `RESTORE_RECEIPT.json`의 `PASS_COMPLETE_RESTORE`다.
실패하면 `FIRST_FAILURE.json`, stdout/stderr, 기존 다운로드와 부분 출력을
보존한다. 자동 재시도나 기존 출력 덮어쓰기는 없다. 원인을 수정한 후 새 출력
디렉터리로 재개한다. `--hydrate`를 생략하면 E13C10의 모든 outer payload만
검증·추출하며 predecessor ZIP을 펼치지 않는다.

복구 경로 검증의 고정 제한은 ZIP당 50,000 members, expanded bytes 2 GiB,
embedded manifest 16 MiB다. Traversal·symlink·중복 member/JSON key 등은 거부한다.
해시는 byte identity 근거이며 과학적 승격, provider attestation 또는 새 실행
권한의 근거가 아니다. 포함된 영수증을 실제 수행 범위와 함께 읽는다.

## 이 kit에 포함된 확인 범위

- 원격 위치: `{remote_status}`
- 실제 복구 기록: `{actual_restore_status}`
- kit 조립: 작은 파일 복사와 실제 kit payload bytes 검증만 수행한다.
- COMPLETE archive 재해시, 대용량 복구 반복, science/MPI/NCP 실행은 0이다.
'''
        with (directory / 'README_KO.md').open('x', encoding='utf-8') as stream:
            stream.write(readme)
        provenance = {'schema': 'bass-he-e13c10-kit-provenance-v1', 'assembled_utc': assembled,
            'source_files_copied_unchanged': source_pins,
            'external_transfer_manifest_sha256': transfer_pin['sha256'],
            'complete_archive': archive_pin, 'new_NCP_heavy_tasks': 0,
            'remote_verification_scope': remote_status, 'actual_restore_scope': actual_restore_status,
            'assembly_complete_archive_rehashes': 0, 'assembly_helper_executions': 0,
            'assembly_scientific_kernel_calls': 0, 'assembly_MPI_invocations': 0,
            'assembly_NCP_execute_invocations': 0, 'assembly_external_mutations': 0,
            'sealed_package_modifications': 0,
            'self_identity_authority': 'External final handoff supplies the actual kit ZIP bytes/SHA.'}
        save(directory / 'KIT_PROVENANCE.json', provenance)
        paths = sorted(p for p in directory.rglob('*') if p.is_file())
        payload_pins = {p.relative_to(directory).as_posix(): pin(p) for p in paths}
        kit_manifest = {'schema': KIT_SCHEMA, 'files': payload_pins,
            'external_transfer_manifest_sha256': transfer_pin['sha256'],
            'complete_archive_sha256': archive_pin['sha256'], 'new_heavy_tasks': 0,
            'kit_self_identity_authority': 'EXTERNAL_FINAL_HANDOFF',
            'manifest_self_entry': 'EXCLUDED_TO_AVOID_SELF_REFERENCE'}
        kit_manifest_path = directory / 'KIT_MANIFEST.json'
        save(kit_manifest_path, kit_manifest)
        paths.append(kit_manifest_path)
        paths.sort()
        expected = dict(payload_pins)
        expected['KIT_MANIFEST.json'] = pin(kit_manifest_path)
        stage = 'KIT_WRITE_AND_VERIFY'
        temporary = output / ('BASS_HE_E13C10_RECOVERY_KIT_' + args.stamp + '.building.zip')
        with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
            for path in paths:
                relative = path.relative_to(directory).as_posix()
                info = zipfile.ZipInfo(relative, date_time=(2026, 10, 12, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                zipped.writestr(info, path.read_bytes())
        with zipfile.ZipFile(temporary) as zipped:
            names = zipped.namelist()
            require(len(names) == len(set(names)) and set(names) == set(expected), 'actual kit member mismatch')
            for name, identity in expected.items():
                raw = zipped.read(name)
                require({'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()} == identity,
                        'actual archived kit payload mismatch: ' + name)
        identity = pin(temporary)
        archive = output / ('BASS_HE_E13C10_RECOVERY_KIT_' + args.stamp + '_sha_' + identity['sha256'][:12] + '.zip')
        os.link(temporary, archive)
        temporary.unlink()
        report = {'schema': 'bass-he-e13c10-kit-build-receipt-v1', 'status': 'PASS_ALL_ACTUAL_KIT_PAYLOAD_BYTES',
            'archive': {'path': str(archive), 'canonical_name': archive.name, **identity},
            'kit_contents_directory': str(directory), 'archive_members': len(expected),
            'payload_files': len(payload_pins), 'verified_archived_payloads': expected,
            'package_manifest': build['package_manifest'], 'transfer_manifest': transfer_pin,
            'complete_archive_rehashes': 0, 'large_restore_repeats': 0, 'helper_executions': 0,
            'scientific_kernel_calls': 0, 'MPI_invocations': 0, 'NCP_execute_invocations': 0,
            'external_mutations': 0, 'sealed_package_modifications': 0, 'automatic_retries': 0,
            'elapsed_seconds': time.monotonic() - started,
            'publication': 'NOT_PERFORMED_BY_KIT_ASSEMBLY',
            'self_reference_policy': 'This build receipt is external to the kit.'}
        save(output / 'RECOVERY_KIT_BUILD_RECEIPT.json', report)
        print(json.dumps({'status': report['status'], 'archive': report['archive'],
                          'archive_members': report['archive_members'],
                          'receipt': str(output / 'RECOVERY_KIT_BUILD_RECEIPT.json')}, indent=2))
        return 0
    except BaseException as error:
        save(output / 'FIRST_FAILURE.json', {'schema': 'bass-he-e13c10-kit-build-failure-v1',
            'status': 'FAIL_PRESERVED_NO_AUTOMATIC_RETRY', 'stage': stage,
            'error_type': type(error).__name__, 'error': str(error), 'automatic_retries': 0,
            'scientific_kernel_calls': 0, 'MPI_invocations': 0, 'NCP_execute_invocations': 0,
            'complete_archive_rehashes': 0, 'large_restore_repeats': 0,
            'elapsed_seconds': time.monotonic() - started})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
