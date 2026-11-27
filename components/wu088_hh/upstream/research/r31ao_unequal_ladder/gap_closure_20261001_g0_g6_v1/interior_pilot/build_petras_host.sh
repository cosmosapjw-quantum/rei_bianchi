#!/usr/bin/env bash
# Host-only opt-in build draft; no native execution and no FLINT compilation.
set -euo pipefail
: "${WU088_BACKEND_PREFIX:?set verified pinned backend installation prefix}"
: "${WU088_BUILD_PROVENANCE:?set independently verified backend provenance JSON}"
: "${WU088_PETRAS_BUILD_OUT:?set a NEW directory for this synthetic build}"
test ! -e "$WU088_PETRAS_BUILD_OUT"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/../validated_callback/verify_build_inputs.py" "$WU088_BUILD_PROVENANCE"
export PKG_CONFIG_PATH="$WU088_BACKEND_PREFIX/lib/pkgconfig:$WU088_BACKEND_PREFIX/lib64/pkgconfig"
test "$(pkg-config --modversion flint)" = "3.4.0"
test "$(pkg-config --modversion gmp)" = "6.3.0"
test "$(pkg-config --modversion mpfr)" = "4.2.2"
mkdir "$WU088_PETRAS_BUILD_OUT"
compiler="${CXX:-c++}"
"$compiler" --version > "$WU088_PETRAS_BUILD_OUT/compiler.txt"
"$compiler" -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror -fno-fast-math -ffp-contract=off \
  $(pkg-config --cflags flint gmp mpfr) \
  "$script_dir/../validated_callback/callback.cpp" "$script_dir/petras_host.cpp" \
  "$script_dir/native_petras_synthetic.cpp" $(pkg-config --libs flint gmp mpfr) \
  -o "$WU088_PETRAS_BUILD_OUT/native_petras_synthetic"
ldd "$WU088_PETRAS_BUILD_OUT/native_petras_synthetic" > "$WU088_PETRAS_BUILD_OUT/linked_libraries.txt"
sha256sum "$WU088_PETRAS_BUILD_OUT/native_petras_synthetic" "$script_dir/petras_host.cpp" \
  "$script_dir/petras_host.hpp" "$script_dir/native_petras_synthetic.cpp" \
  "$script_dir/../validated_callback/callback.cpp" "$script_dir/../validated_callback/callback.hpp" \
  > "$WU088_PETRAS_BUILD_OUT/SHA256SUMS"
cp "$WU088_BUILD_PROVENANCE" "$WU088_PETRAS_BUILD_OUT/BACKEND_BUILD_PROVENANCE.json"
printf '%s\n' 'Built only. Check actual linked-library identities, then use the admitted host process guard to run synthetic fixtures.'
