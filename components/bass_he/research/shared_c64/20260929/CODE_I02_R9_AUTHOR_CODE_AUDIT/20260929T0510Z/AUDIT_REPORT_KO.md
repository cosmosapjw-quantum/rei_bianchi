# R9 ARSENY author-code normalization audit

## Identity and method

The public Mendeley Version 1 dataset DOI [10.17632/n43srxwdnm.1](https://data.mendeley.com/datasets/n43srxwdnm/1) identifies the ARSENY program, CC BY 4.0. Direct `api.data.mendeley.com` anonymous retrieval returned HTTP 401; the dataset page's public `/public-api` supplied the same Version 1 metadata and files. The provider ZIP is 19,714 bytes, SHA256 `48a06833600ae1789ba853945d9b878837ffd9c95d08c085a3875c12cd41bc67`, matching provider metadata. Its three members match individually fetched files and their provider hashes. Raw FORTRAN remains in isolated /tmp storage and private backup, outside Git and clean-room source.

PR15 HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c` and PR17 intake HEAD `a2adeb9bd44b7fe682c742bb44f413505dca8ef3` were fresh-checked. R8's authorized PDF identity and page audit were inherited; the PDF was not redistributed or reanalyzed.

## Decision

The distributed author code uses factor two directly on the stored STCKLBR2 Delta in both SECTION traversals. No intervening scale change was found. The printed CPC Eq.(52) factor-one elementary matrix probability and distributed author matrix implementation therefore disagree under the visible data-flow. The author expression matches printed Eq.(55)'s factor-two form on the stored parameter, though the Eq.(55) text names the Q-series while the code applies the expression to all accepted stored branches.

This does not authorize a clean-room default change. The numerical contour discretization, impact-parameter handling, and paper notation still need an explicit scientific policy decision. The present gate stays HOLD.

## Findings and limits

| Severity | ID | Finding | Claim ceiling |
| --- | --- | --- | --- |
| Important | I1 | Printed Eq.(52) uses factor one, while author SECTION uses factor two for the matrix row updates (arseny.f:1904–1910,1978–1984). | Static source mismatch; no runtime/physical agreement claim. |
| Important | I2 | STCKLBR2 stores a Delta grid and spline derivatives (arseny.f:1284–1306,1195–1198), but SECTION uses first sample `CMES(1)` for every impact `RO` (1888–1904,1967–1978). | Static dependency finding; numerical effect unmeasured. |
| Minor | M1 | No Eq.(43) linear or squared minimum-gap approximation is implemented; ITYPE11 stores zero (456–459,1181,1193–1208). | Neither gap power can be attributed to the author source. |

STCKLBR2 accumulates segmentwise absolute imaginary contributions (1301), so this audit does not assert exact mathematical equivalence to every continuous Eq.(56) contour convention. It also did not execute a particular branch or establish how often ITYPE11 occurs.

## Gate ledger

`CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`. No clean-room production file, tolerance, or default changed. Author code was neither compiled nor run; no Eq.(55) production, Eq.(50)/(54) change, 56-action replay, worker sweep, CODE-I02 rereview, or L2 work occurred.
