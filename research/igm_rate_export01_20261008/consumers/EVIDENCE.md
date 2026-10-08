# BASS and REC schema-only return

Scope: DAG `BASS-OBS-SCHEMA01` and `REC-INITIAL-SCHEMA01`, based on handoff `inputs/BASS_REC_INTAKE.json`, `DAG.json`, and `RECEIVER_CONTRACT.json`. These adapters do not call or edit BASS, REC, the IGM solver, observers, or providers. No historical SYNC02/SYNC03 campaign is rerun. Real short IGM histories and late-IGM radiation/initial data remain **NOT_PROVIDED**; physical admission remains **HOLD** and REC consumer Gate I remains **DEFERRED_CONSUMER**.

`schemas.py` accepts exact rational strings or integers for synthetic schema fixtures. `bass_observable()` requires strictly increasing source-owned normal seconds, corresponding exact ln(a) epochs, proper nuclear densities with H/He fraction denominators, frame authority and a caller-owned optical-depth tail. The endpoint-linear reconstruction converts `n_e = n_H*x_HII + n_He*(x_HeII+2*x_HeIII)` from proper cm^-3 to m^-3 by 10^6 once, and applies fixed D once in `q_t=c*sigma_T*n_e*D`. A supplied frozen-cell q_t preserves the supplied rate without applying D or a density conversion again. No t(z), a^-3, filling factor, physical between-node reconstruction or observer calibration is inferred. The result declares units, reconstruction, authorities and application counts; it does not integrate optical depth.

`rec_initial()` requires an exact epoch, proper nuclear/electron densities, species and electron fractions, separately supplied Tgas/Trad in K, gas/radiation/clock/frame authorities, and a blackbody or explicitly identified spectral model. Electron density and fraction are checked by exact rational equality. It neither constructs matched histories nor extends the source-pinned pure-H one-temperature/He consumer admission domain. Missing epoch, temperature, radiation authority and spectrum identity are typed errors.

Commands and exits:

- `python3 -m unittest discover -s research/igm_rate_export01_20261008/consumers -p 'test_*.py' -v` — exit 0, 7 tests PASS; repeated once after preserving explicit output units/D/constants.
- Positive cases: exact density/rate arithmetic, supplied-cell rate unchanged, REC state intact, input dictionaries unmodified.
- Negative cases: density convention and double conversion; D applied twice; missing/nonincreasing normal clock and missing exact epochs; negative observer tail; missing radiation authority/temperature/epoch/frame/spectrum; inconsistent electron density; actual-history claims rejected in this schema-only lane.

Additional observer calls: 0. Additional provider calls: 0. No actual scientific history was computed. Existing production defaults/source/closure/tolerances are untouched.

## PR88 singleton compatibility intake

Read `research/igm_rate_export_receiver_20261008/observed/EXPORT01.json` and its copied `repo/research/igm_rate_receiver01_20261008/adapter.py`; no observer rerun. Packet observation ID is `1623af1f8e661047f0b339c614ea90ae61b8b50f8f0a961158ea1591b0a9db25`, source producer commit is `8477bae16accaf3de168669aafd2f31eac2ca811`, accepted transaction `committed-2`, exact binary64 epoch is preserved by the receiver as an exact rational. Compatible prospective mapping is gas `[h,y,z,w]` → `[x_HII,x_HeII,x_HeIII,w_erg/H]`, background positions 3/4 → proper n_H/n_He, with electrons derived by the stated nuclei formula. Input binary64 values would need `Fraction.from_float` rational-string conversion, never decimal truncation or changed gas state.

This singleton has neither two or more explicit normal-time edges nor a caller observer tail/reconstruction/frame authority: **BASS short history NOT_PROVIDED**. Its spectral six moments are not a REC blackbody or temperature/radiation authority; **REC radiation and matched late-IGM history NOT_PROVIDED**. Source EOS can support a separately declared Tgas calculation, but does not supply Trad or a new admitted initial condition. No singleton is duplicated to invent an interval.

The packet preserves REI sigma_T=6.6524587051e-25 cm^2, whereas the BASS intake reference uses 6.6524587e-29 m^2. The schema therefore requires explicitly supplied c, sigma_T and their authority, and preserves them in output; it does not silently choose between these constants. The synthetic positive test uses the BASS intake value. Final focused test command above exits 0 (7/7) after this compatibility improvement. Actual integration remains blocked on producer-owned clock/history/radiation/frame/tail data, not on a new observer/provider calculation.
