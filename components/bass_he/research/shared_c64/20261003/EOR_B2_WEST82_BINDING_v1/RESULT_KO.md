# B2: West82 primary binding and high-l reference

The supplied six-page West-Lane-Cohen PRA26,3164 PDF is now recovered. Its TableI contains25 resonance energy/ell/v assignments, not sigma(E), widths or peak areas.16 assignments have ell>32, max48. We preserve source Figure1 Ry versus gap Hartree, Eqs3/5/6 and the historical Eq11 constant13.602.

New independent namespace bass_he_west82 provides source-unit transformations, a hash-bound TableI reader, and the derivative of the immutable B1 finite-range optical reference. Exact regular-origin normalization divides out first_edge^(ell+1) without forming it. Positive-loss normalization uses log incoming amplitude rather than squaring a huge number. Both changes precede the extension to supported ell<=64.

49 focused tests passed, plus18 independent complex-square-well,3 rare-loss and2 small-origin comparisons against110-digit mpmath Bessel formulas. Max18-case absolute S defect2.3743789293757334e-14; relative P defect8.439468799788361e-14. These are manufactured models, not West82 physical cross sections. Separate wheel installation passed49 tests. Full logs, source PDF/table and failures are in the private archive.

Actual molecular V(R)/A(R)/dipole grids, full partial-wave tail, physical source UQ and emitted photon spectrum remain open. Piecewiseconstant finite-range/free-exterior conditions do not certify physical long-range truncation. No Fortran/MPI/physicalRCT campaign or independent scientific review ran here.

The sibling EOR_B1_RCX_RATE_v1 commit9e3d54bf... was read and preserved. Its GM25 approximate thermal-rate source is separate from West's printed tables. The two historical wheels both expose bass_he_rcx: do not co-install them. New bass_he_west82 uses a noncolliding namespace. Next work binds the existing source-choice rate module and atomic-only export; it does not invent a new fit or heat source.

PROMOTE=HOLD; EOR_THEORY_GATE=NOT_SATISFIED; Eq55=NOT_RUN. No Bianchi-physics mutation. Final archive/publication/cloud identities are supplied in the detached delivery receipt.
