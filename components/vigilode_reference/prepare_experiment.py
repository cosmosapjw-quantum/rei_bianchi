"""Prepare a detached historical HE29 or HH native experiment using the unified source tree."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


REFERENCE = Path(__file__).resolve().parent
COMPONENTS = REFERENCE.parent
PIN = "a21d573980f66fe02891bd216153443b5352f921"
URL = "https://github.com/cosmosapjw-quantum/vigilode.git"
HE = COMPONENTS / "bass_he/research/he29_survival_budget_20261018"
HH = COMPONENTS / "wu088_hh/upstream/native"
LANES = {
    "he29": HE / "vigilode_20261019/rust_bridge",
    "he29_packed": HE / "optimization_20261020/rust_bridge",
    "hh69": HH / "phys69_vigilode",
    "hh70": HH / "phys70_optimized",
}


def copy_hh(source: Path, prefix: Path) -> Path:
    copied = Path(shutil.copytree(source, prefix / source.name))
    manifest = copied / "Cargo.toml"
    text = manifest.read_text()
    for crate in ("rodas5p-core", "rodas5p-integrators"):
        binding = f'{crate} = {{ git = "{URL}", rev = "{PIN}"'
        if text.count(binding) != 1:
            raise ValueError(f"Unexpected historical binding for {crate}")
        text = text.replace(binding, f'{crate} = {{ path = "../vigilode/crates/{crate}"')
    manifest.write_text(text)
    lock = copied / "Cargo.lock"
    record = f'source = "git+{URL}?rev={PIN}#{PIN}"\n'
    if lock.read_text().count(record) != 3:
        raise ValueError("Expected exactly three upstream VigilODE package sources")
    lock.write_text(lock.read_text().replace(record, ""))
    return copied


def prepare(lane: str, destination: Path) -> Path:
    if destination.exists():
        raise FileExistsError(f"Choose a new destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as private:
        staged = Path(private) / "experiment"
        staged.mkdir()
        (staged / "vigilode").symlink_to(REFERENCE, target_is_directory=True)
        if lane.startswith("hh"):
            first = copy_hh(LANES["hh69"], staged)
            copied = first if lane == "hh69" else copy_hh(LANES["hh70"], staged)
        else:
            copied = Path(shutil.copytree(LANES[lane], staged / "rust_bridge"))
        staged.rename(destination)
    return destination / copied.name / "Cargo.toml"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", choices=LANES)
    parser.add_argument("destination", type=Path)
    options = parser.parse_args()
    print(prepare(options.lane, options.destination.resolve()))
