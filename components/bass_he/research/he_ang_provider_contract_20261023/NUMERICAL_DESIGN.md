# Exact represented-input numerical design

The new reference path uses Python standard-library `Fraction`. It accepts explicit integers and rational strings and refuses binary floats/bools instead of silently rounding or clipping. The finite examples use artificial SI-tagged masses and energies selected to make every event and moment rational; they are not physical H1 constants or calibrated rates.

The independent R7 program derives support and moments without importing the new implementation. C6 integrates two new-law fixtures and compares explicit hand-derived matrices, normalization and frame formulae. An additional saved-oracle correspondence check may read the already saved R7 event data into the new accumulator if needed; it must not rerun R7 or HE-X1.

Use a finite positive joint event law as the primary exact object. This retains all first and second moment correlations and avoids an invented angular closure. Electron count2, proton count1 and measure mass Z propagate together. Generic raw-moment containers are algebraic carriers only; they do not certify positivity or representability. Zero sigma returns zero weighted moments without defining a conditional probability.

The metadata layer is a structural prerequisite checker. Actual fixture bytes are content-bound; the CLI additionally checks their known schema/kinematics against declarations. For external sources, numerical quadrature error and physical source uncertainty require separate calibrated obligations and original-content review. No numerical epsilon, raw1e-8 HE38 model tolerance or old X1 PASS supplies a new physical uncertainty.

Resource cap remains the frozen CPU10s/wall30s, per-invocationCPU2s/wall5s and AS256MiB. The fixture CLI bounds each input file to1MiB and events to256. Direct Python API inputs are trusted bounded reference inputs; the external resource wrapper remains required. No throughput claim or benchmark is made.
