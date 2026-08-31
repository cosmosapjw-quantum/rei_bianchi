#!/bin/bash
set -euo pipefail
unset LD_PRELOAD LD_LIBRARY_PATH RUSTFLAGS RUSTDOCFLAGS RUSTC_WRAPPER CC CFLAGS LDFLAGS
export PATH=/usr/bin:/bin

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
REPO_ROOT=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)
OUTPUT_DIR=${1:?usage: build_and_test.sh OUTSIDE_WORKTREE_OUTPUT_DIR}
if [[ -L "$OUTPUT_DIR" ]]; then
    echo "refusing a symlink build-output directory" >&2
    exit 64
fi
OUTPUT_DIR=$(realpath -m -- "$OUTPUT_DIR")

while IFS= read -r record
do
    [[ "$record" == worktree\ * ]] || continue
    WORKTREE=${record#worktree }
    case "$OUTPUT_DIR/" in
        "$WORKTREE/"*)
            echo "refusing to place Rust build products inside a Git worktree" >&2
            exit 64
            ;;
    esac
done < <(git -C "$REPO_ROOT" worktree list --porcelain)
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR=$(CDPATH= cd -- "$OUTPUT_DIR" && pwd -P)

RUSTC_BIN=${RUSTC:-/workspace/scratch/6f83d977af18/toolchains/rust-1.94.1-prefix/bin/rustc}
if [[ ! -x "$RUSTC_BIN" ]]; then
    RUSTC_BIN=/mnt/data/rust-1.94.1-prefix/bin/rustc
fi
if [[ ! -x "$RUSTC_BIN" ]]; then
    echo "Rust 1.94.1 compiler not found" >&2
    exit 69
fi
if [[ $(sha256sum "$RUSTC_BIN" | awk '{print $1}') != \
    "ef6d716e5d1c6c93def277c0afa037c21e7a74f7de3aed4ee0700646c3301b1d" ]] || \
   [[ $("$RUSTC_BIN" --version) != "rustc 1.94.1 (e408947bf 2026-03-25)" ]]; then
    echo "refusing an unlocked Rust compiler" >&2
    "$RUSTC_BIN" --version >&2
    exit 65
fi
RUST_SYSROOT=$("$RUSTC_BIN" --print sysroot)
for locked_file in \
    "e51e2f6796ac2730a11744a0d3e126e6b1e60d43e2e602a091551b1ad1a9ba2f $RUST_SYSROOT/lib/librustc_driver-83018425804cb0fc.so" \
    "158c711c64147bb127a2a5174df22718d26b755560a1487945e7c788c947986f $RUST_SYSROOT/lib/libLLVM.so.21.1-rust-1.94.1-stable"
do
    printf '%s\n' "$locked_file" | sha256sum --check --status || {
        echo "Rust compiler closure mismatch: ${locked_file#* }" >&2
        exit 65
    }
done
RUST_STDLIB="$RUST_SYSROOT/lib/rustlib/x86_64-unknown-linux-gnu/lib"
STDLIB_CLOSURE=$(
    cd "$RUST_STDLIB"
    find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}'
)
if [[ "$STDLIB_CLOSURE" != \
    "1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799" ]]; then
    echo "Rust standard-library closure mismatch" >&2
    exit 65
fi

PYTHON_BIN=${PYTHON:-/usr/bin/python3}
if [[ ! -x "$PYTHON_BIN" ]] || \
   [[ $(sha256sum "$PYTHON_BIN" | awk '{print $1}') != \
    "a92f0f95e883390c7256b2e441484aac06b1002dbe1d924141a77c8d82f96223" ]]; then
    echo "refusing an unlocked Python validation driver" >&2
    exit 65
fi
for locked_file in \
    "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae /usr/lib/x86_64-linux-gnu/libmpfr.so.6" \
    "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804 /usr/lib/x86_64-linux-gnu/libgmp.so.10" \
    "6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234 /usr/bin/cc" \
    "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c /usr/bin/ld"
do
    printf '%s\n' "$locked_file" | sha256sum --check --status || {
        echo "native build authority mismatch: ${locked_file#* }" >&2
        exit 65
    }
done

SOURCE="$SCRIPT_DIR/source_bound_thermal.rs"
ORACLE="$SCRIPT_DIR/verify_fraction_corners.py"
TEST_BINARY="$OUTPUT_DIR/source_bound_thermal_tests"
LIBRARY="$OUTPUT_DIR/librei_source_bound_thermal.so"
if [[ -e "$TEST_BINARY" || -L "$TEST_BINARY" || -e "$LIBRARY" || -L "$LIBRARY" ]]; then
    echo "refusing to overwrite a pre-existing Rust build product" >&2
    exit 64
fi
SOURCE_SHA256=$(sha256sum "$SOURCE" | awk '{print $1}')
ORACLE_SHA256=$(sha256sum "$ORACLE" | awk '{print $1}')
if [[ "$SOURCE_SHA256" != \
    "c4dd1f21200faab60e239e96b56d1eb3d2691c47dc3d3a4991af7565ce0a9d51" ]] || \
   [[ "$ORACLE_SHA256" != \
    "83a77d2bc56261caaf4c5d07475b4eb97430de142a658aaa14b6d58b696ee497" ]]; then
    echo "source or independent-oracle authority mismatch" >&2
    exit 65
fi
COMMON=(
    --edition=2021
    -D warnings
    -C debuginfo=0
    --remap-path-prefix="$REPO_ROOT"=/rei_bianchi
)

export SOURCE_DATE_EPOCH=0
unset PYTHONHOME PYTHONPATH PYTHONSTARTUP PYTHONINSPECT PYTHONSAFEPATH
"$RUSTC_BIN" "${COMMON[@]}" --test "$SOURCE" -o "$TEST_BINARY"
"$TEST_BINARY" --test-threads=1
"$RUSTC_BIN" --edition=2021 --crate-type=cdylib --crate-name=rei_source_bound_thermal \
    -C opt-level=3 \
    -C codegen-units=1 \
    -C strip=symbols \
    -C embed-bitcode=no \
    -C metadata="$SOURCE_SHA256" \
    -C linker=/usr/bin/x86_64-linux-gnu-gcc \
    --remap-path-prefix="$REPO_ROOT"=/rei_bianchi \
    -L native=/usr/lib/x86_64-linux-gnu \
    -C link-arg=-Wl,--build-id=none \
    -C link-arg=-Wl,--disable-new-dtags \
    -C link-arg=-Wl,-rpath,/usr/lib/x86_64-linux-gnu \
    -C link-arg=-Wl,-l:libmpfr.so.6 \
    -C link-arg=-Wl,-l:libgmp.so.10 \
    "$SOURCE" -o "$LIBRARY"
ORACLE_OUTPUT=$("$PYTHON_BIN" -I -S "$ORACLE" "$LIBRARY")
if [[ "$ORACLE_OUTPUT" != "fraction_corner_oracle=PASS families=96 corner_systems=6144" ]]; then
    echo "fraction corner oracle did not produce the locked PASS receipt" >&2
    printf '%s\n' "$ORACLE_OUTPUT" >&2
    exit 66
fi
printf '%s\n' "$ORACLE_OUTPUT"
if [[ $(sha256sum "$SOURCE" | awk '{print $1}') != "$SOURCE_SHA256" ]] || \
   [[ $(sha256sum "$ORACLE" | awk '{print $1}') != "$ORACLE_SHA256" ]]; then
    echo "source or independent oracle changed during build/test" >&2
    exit 67
fi

sha256sum "$SOURCE" "$ORACLE" "$LIBRARY"
