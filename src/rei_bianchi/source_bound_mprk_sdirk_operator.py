"""Fail-closed seam for the not-yet-materialized Rust four-site replay ABI.

The repository currently has bounded Rust implicit certificates, but no native
ABI that recomputes all four source-bound MPRK22--SDIRK2 sites.  This module is
therefore intentionally non-constructible.  It gives adapters a stable typed
failure instead of accepting a synthetic fixture or silently falling back to a
Python/JAX numerical path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, NoReturn


RUST_THERMAL_REPLAY_ABI_MISSING: Final[str] = "RUST_THERMAL_REPLAY_ABI_MISSING"


class RustThermalReplayAbiMissing(RuntimeError):
    """Raised until the real source-bound four-site Rust ABI is pinned."""

    code: Final[str] = RUST_THERMAL_REPLAY_ABI_MISSING

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        super().__init__(
            f"{self.code}: no pinned native Rust ABI recomputes and certifies "
            "population_t0, population_t1_predictor, thermal_tgamma, and "
            "thermal_t1_final; synthetic fixtures and Python/JAX fallbacks are forbidden"
        )


class SourceBoundMprkSdirkOperator:
    """Reserved production operator type; no successful constructor exists yet."""

    def __new__(cls, *args: object, **kwargs: object) -> NoReturn:
        repo_root = args[0] if args else kwargs.get("repo_root", Path.cwd())
        raise RustThermalReplayAbiMissing(Path(repo_root))

    @classmethod
    def from_repo(cls, repo_root: Path, **_: object) -> NoReturn:
        """Fail typed until an immutable, real four-site replay ABI is available."""

        raise RustThermalReplayAbiMissing(Path(repo_root))


__all__ = [
    "RUST_THERMAL_REPLAY_ABI_MISSING",
    "RustThermalReplayAbiMissing",
    "SourceBoundMprkSdirkOperator",
]
