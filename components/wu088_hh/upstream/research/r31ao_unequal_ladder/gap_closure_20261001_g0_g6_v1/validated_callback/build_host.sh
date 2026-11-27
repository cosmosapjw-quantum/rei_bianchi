#!/usr/bin/env bash
# Local host only: builds this synthetic executable, never FLINT/dependencies.
set -euo pipefail
: "${WU088_BACKEND_PREFIX:?set the verified pinned backend installation prefix}"
: "${WU088_BUILD_PROVENANCE:?set path to independently verified backend provenance JSON}"
: "${WU088_BUILD_OUT:?set a NEW directory for this build}"
test ! -e "$WU088_BUILD_OUT"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/verify_build_inputs.py" "$WU088_BUILD_PROVENANCE"
export PKG_CONFIG_PATH="$WU088_BACKEND_PREFIX/lib/pkgconfig:$WU088_BACKEND_PREFIX/lib64/pkgconfig"
test "$(pkg-config --modversion flint)" = "3.4.0"
test "$(pkg-config --modversion gmp)" = "6.3.0"
test "$(pkg-config --modversion mpfr)" = "4.2.2"
mkdir "$WU088_BUILD_OUT"
compiler="${CXX:-c++}"
"$compiler" --version > "$WU088_BUILD_OUT/compiler.txt"
"$compiler" -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror -fno-fast-math \
  $(pkg-config --cflags flint gmp mpfr) \
  "$script_dir/callback.cpp" "$script_dir/assembly.cpp" "$script_dir/native_synthetic.cpp" \
  $(pkg-config --libs flint gmp mpfr) -o "$WU088_BUILD_OUT/native_synthetic"
ldd "$WU088_BUILD_OUT/native_synthetic" > "$WU088_BUILD_OUT/linked_libraries.txt"
sha256sum "$WU088_BUILD_OUT/native_synthetic" "$script_dir/callback.cpp" \
  "$script_dir/callback.hpp" "$script_dir/assembly.cpp" "$script_dir/assembly.hpp" \
  "$script_dir/native_synthetic.cpp" > "$WU088_BUILD_OUT/SHA256SUMS"
cp "$WU088_BUILD_PROVENANCE" "$WU088_BUILD_OUT/BACKEND_BUILD_PROVENANCE.json"
printf '%s\n' 'Built only. Verify ldd paths against approved provenance before executing native_synthetic.'
