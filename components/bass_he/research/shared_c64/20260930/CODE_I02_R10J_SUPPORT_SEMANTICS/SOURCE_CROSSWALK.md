# R10J source-line crosswalk

Basis: PR17 `8a240af8f490a9fe519a15b837d9678bfed53405`. Original author `arseny.f` has 2,816 CRLF lines and SHA256 `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`. It was read outside the clean-room tree, never compiled or executed. The code was NOT redistributed in this package.

| Item | Author source lines | Meaning and scope |
|---|---|---|
| Stored radius | 1174-1175, 1188-1192 | `NRQ=NRO+1`; final slot stores state indices, `RB(J,NRQ)=DREAL(RQ)` |
| Author support selection | 1591-1593 | Header read followed by unconditional `JRO=JRQ` |
| Printed mode | 1600-1603 | Alternative `JRQ-1` prints extended support; active `JRQ` prints `LESS THEN RE(RC)` |
| Restore of radii | 1633-1645 | Each SPRO entry is copied to RBI without a new radius convention |
| Initial-state radial upper bound | 1655-1658 | For incident H(1s), IIN identifies j=3; largest incident radius supplies ROM minus EPS7 |
| Inbound gate and update | 1896-1910 | `RO>SPRO(JRO)` skips event; exp(-2 Delta0/v); reversible row update |
| Outbound gate and update | 1967-1984 | Reverse event order; same support; upper-shell CQ=0 produces an absorbing event |
| Event sort | 1214, 1228, 1237, 1243-1247 | Sort by real radius then reverse stored order, giving outer-to-inner approach |
| Printed Eq.(52) | CPC PDF p.12 | Different convention: support through Re(Rc)+Im(Rc) |
| Actual benchmark label | CPC PDF p.18 | Appendix explicitly prints IMPACT PARAMETER LESS THEN RE(RC) |
| Current clean-room | src/arseny_reimpl/eq50_scoped.py | support_cutoff returns R.real+R.imag |
| Current sparse action | src/bass_he/transport.py | absorbing upper events on both passes; same outer-to-inner approach order |

For the incident H(1s) column, before every changed inbound upper event the receiving population is zero. Hence the inbound reversible/absorbing distinction is null on this input, not an equality of full matrices. The R10I full-WRN non-equivalence likewise remains valid, while the current approach reaches only m=0 rotation columns.

The old R10H midpoint diagnostic used the extended support and an extended ROMAX. Its small JMAX effect is valid only for that integrand. It was NOT a literal audit of the complete author run. The omission was in our comparison contract, not newly introduced by the current user run.

No source says the real-radius step cutoff is physically preferable. Source-code reproduction and physical modeling must remain separate.
