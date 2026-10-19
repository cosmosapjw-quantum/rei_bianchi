"""Reuse a compact completed reference binary only under its exact build binding."""
from pathlib import Path
import argparse
import shutil

from run_refinement import read_json, save, sha


def prepared_sources_complete(prepared):
    prepared=Path(prepared)
    try:
        identity=read_json(prepared/'PREPARED_IDENTITY.json')
        return bool(identity['outputs']) and all((prepared/name).is_file() and sha(prepared/name)==digest
                                                for name,digest in identity['outputs'].items())
    except (OSError,KeyError,ValueError):
        return False


def reuse_compact(base,prepared,scratch):
    base,prepared,scratch=map(Path,(base,prepared,scratch))
    result=dict(base=str(base),prepared=str(prepared),status='NOT_REUSED')
    try:
        build=read_json(base/'BUILD_RECEIPT.json')
        binary=base/'positive_native.bin'
        if build.get('exit_code')!=0 or not prepared_sources_complete(prepared):
            raise ValueError('COMPACT_BASE_SOURCE_OR_BUILD_INCOMPLETE')
        if sha(prepared/'PREPARED_IDENTITY.json')!=build['prepared_identity_sha256']:
            raise ValueError('COMPACT_BASE_PREPARED_BYTES_DIFFER')
        if not binary.is_file() or sha(binary)!=build['binary_sha256']:
            raise ValueError('COMPACT_BASE_BINARY_SHA_MISMATCH')
        scratch.mkdir(parents=True,exist_ok=True)
        target=scratch/'positive_native.bin'
        if target.exists() and sha(target)!=build['binary_sha256']:
            raise FileExistsError('COMPACT_BINARY_OUTPUT_CONFLICT')
        if not target.exists():shutil.copyfile(binary,target)
        target.chmod(target.stat().st_mode | 0o100)
        if (base/'BUILD_RECEIPT.json').resolve()!=(prepared/'BUILD_RECEIPT.json').resolve():
            shutil.copyfile(base/'BUILD_RECEIPT.json',prepared/'BUILD_RECEIPT.json')
        result.update(status='REUSED_EXACT_BUILD_BINDING',binary=str(target),binary_sha256=build['binary_sha256'],
                      prepared_identity_sha256=build['prepared_identity_sha256'])
    except (OSError,KeyError,ValueError) as error:
        result['reason']=repr(error)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-complete',type=Path)
    parser.add_argument('--base',type=Path)
    parser.add_argument('--prepared',type=Path)
    parser.add_argument('--scratch',type=Path)
    args=parser.parse_args()
    if args.check_complete is not None:
        raise SystemExit(0 if prepared_sources_complete(args.check_complete) else 2)
    if any(value is None for value in (args.base,args.prepared,args.scratch)):
        parser.error('base, prepared and scratch required')
    result=reuse_compact(args.base,args.prepared,args.scratch)
    save(args.scratch/'COMPACT_BASE_REUSE.json',result)
    raise SystemExit(0 if result['status']=='REUSED_EXACT_BUILD_BINDING' else 2)


if __name__ == '__main__':
    main()
