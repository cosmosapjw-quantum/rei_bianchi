#!/usr/bin/env bash
# Host-only opt-in build. Does not build libraries or execute the fixture.
set -euo pipefail
: "${WU088_BACKEND_PREFIX:?set pinned FLINT/GMP/MPFR sidecar prefix}"
: "${WU088_BUILD_PROVENANCE:?set verified backend record JSON}"
: "${WU088_CACHE_BUILD_OUT:?set a NEW absolute directory for this build}"
test "${WU088_CACHE_BUILD_OUT:0:1}" = /
test ! -e "$WU088_CACHE_BUILD_OUT"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONDONTWRITEBYTECODE=1
python3 "$script_dir/verify_inputs.py" --prefix "$WU088_BACKEND_PREFIX" --record "$WU088_BUILD_PROVENANCE"
export PKG_CONFIG_PATH="$WU088_BACKEND_PREFIX/lib/pkgconfig"
export PKG_CONFIG_LIBDIR="$WU088_BACKEND_PREFIX/lib/pkgconfig"
export LD_LIBRARY_PATH="$WU088_BACKEND_PREFIX/lib"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test "$(pkg-config --modversion flint)" = 3.4.0
test "$(pkg-config --modversion gmp)" = 6.3.0
test "$(pkg-config --modversion mpfr)" = 4.2.2
mkdir "$WU088_CACHE_BUILD_OUT"
compiler="${CXX:-g++}"
"$compiler" --version > "$WU088_CACHE_BUILD_OUT/compiler.txt"
# Baseline and cached entrypoints share this identical translation-unit build.
# Do NOT separately compile old callback.cpp (already included once).
"$compiler" -std=c++17 -O3 -Wall -Wextra -Wpedantic -Werror \
    -fno-fast-math -fno-associative-math -fno-unsafe-math-optimizations -ffp-contract=off \
    $(pkg-config --cflags flint gmp mpfr) \
    "$script_dir/cached_callback.cpp" "$script_dir/native_cache_synthetic.cpp" \
    $(pkg-config --libs flint gmp mpfr) -o "$WU088_CACHE_BUILD_OUT/native_cache_synthetic" \
    > "$WU088_CACHE_BUILD_OUT/compiler_stdout.log" 2> "$WU088_CACHE_BUILD_OUT/compiler_stderr.log"
ldd "$WU088_CACHE_BUILD_OUT/native_cache_synthetic" > "$WU088_CACHE_BUILD_OUT/linked_libraries.txt"
python3 "$script_dir/verify_inputs.py" --prefix "$WU088_BACKEND_PREFIX" --record "$WU088_BUILD_PROVENANCE" \
    --binary "$WU088_CACHE_BUILD_OUT/native_cache_synthetic" \
    --compiler "$compiler" \
    --ldd-report "$WU088_CACHE_BUILD_OUT/linked_libraries.txt" \
    --output "$WU088_CACHE_BUILD_OUT/BUILD_READY.json"
printf '%s\n' 'Built and linked bytes checked. Native equality and benchmark have NOT run.'
