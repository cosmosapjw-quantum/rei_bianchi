# P1 full-history schedule binding

`build_real_schedule(source)` binds the copied 129 binary64 output times and indices 0,2,...,128 to their pinned Q0 source bytes. Output times are never regenerated. The new schedule contains 208 strictly positive hard stops: 81 source-band/redshift stops, together with 128 positive output epochs (one coincident endpoint). Initial epoch zero remains separately labelled because the existing checkpoint contract requires `0 < hard_event <= end`.

For each fixed-q cell edge, the physical source-band edges 10 eV and 50000 eV satisfy `R(t) q = E_band`. The builder uses the unchanged provider ray and the frozen source event routine's Brent settings, `xtol=1e-4 s`, `rtol=4 ulp(1)`. At exact endpoint ratio equality, the corresponding existing endpoint is used directly. Exact duplicate times aggregate all labels; nearby floating times are never shifted or merged. Emissivity redshift knots use the provider's existing inverse time map. All129 outputs are hard endpoints, so this introduces no dense interpolant.

Only the physical band edges are iterated globally. Every emissivity energy-knot crossing remains an internal source quadrature split through the original `source_precision.provider_event_times` delegate, which is unchanged. Opacity thresholds remain the existing per-cell quadrature cuts. The current arithmetic admits r=0 only; nonzero shear is rejected explicitly.

Four new targeted tests passed. The first implementation run exposed a test-oracle error: the toy asserted exact root values despite retaining the original finite Brent tolerance. The test was corrected to the inherited 1e-4 s bound; implementation and tolerance were unchanged. Initial missing-module RED and first failed oracle outputs are retained. No old tests, source-rate scans, native opacity calls, native maps, or trajectories were executed.

`schedule_window(schedule,t0,t1)` returns strict interior events and handles h=0 with an empty tuple; the controller must instead receive the full `hard_events_s` to land on endpoints. The canonical schedule hash excludes its own hash field. Root integration must bind the schedule bytes, not merely read this status.
