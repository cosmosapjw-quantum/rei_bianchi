# BRPERF01 evidence figures

The three standalone 180 mm vector PDFs and 300 dpi PNGs are generated entirely
from retained evidence. Captions define every normalization, statistical unit
and admitted scope. `PLOT_DATA.json` stores all plotted values and constituent
timing ratios; `SOURCE_INDEX.json` pins the 24 original CSV/JSON inputs.

| Figure | Purpose | PNG | PDF |
|---|---|---|---|
| 1 | Separate performance workloads and observed ranges | `01_performance_scopes.png` | `01_performance_scopes.pdf` |
| 2 | Sampled coefficient error versus table storage | `02_rate_accuracy_memory.png` | `02_rate_accuracy_memory.pdf` |
| 3 | HOT time-grid, same-grid representation and ledger controls | `03_hot_native_control.png` | `03_hot_native_control.pdf` |

From this directory, with Python 3 and Matplotlib installed:

```bash
python3 render.py
```

The renderer resolves source paths relative to its containing BRPERF01 tree. It
uses Matplotlib 3.10.8 and Python 3.12.14 in the retained rendering record; no
Rust build, scientific test or benchmark is launched. PDF metadata may change
on regeneration. Data and layout are deterministic for the same inputs and
plotting environment; a byte-identical PDF regeneration is not claimed.

`../figure_audit/` contains the initial and residual hostile audits, numerical
display checks, source hashes used by the semantic audit, full-width layout
bounds, and 90 mm previews. The final PDFs have exactly 180 mm page width.
PNG pixel rounding yields about 179.917 mm at 300 dpi; the half-size previews
are about 89.916 mm at 300 dpi. Standard text is 14 pt or larger at 180 mm and
7 pt at 90 mm. Use the vector PDF for publication; do not shrink below the
audited 90 mm width without another legibility review.

The figures establish neither a combined end-to-end acceleration nor extra
SIMD speedup. The legacy rate table is more accurate in the recorded coefficient
probe sets. The SIMD audit distinguishes host AVX/AVX512 capability from the
particular compile-time target configuration and does not modify the frozen
source report.

Include every `figures/` and `figure_audit/` payload listed in
`../figure_audit/FIGURE_DELIVERABLE_MANIFEST.json`; exclude the Matplotlib font
cache. Publication and external backup remain the root task's responsibility.
