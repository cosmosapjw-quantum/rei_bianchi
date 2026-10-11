## C11 P_COLD_RESTART

Layer: validated C10 actual cold-process restore; implemented/targeted-tested C11 macro checkpoint adapter.

C10 gen1 at 2.5e10 s was loaded in an isolated fresh Python process and advanced once to 5e10 s. All saved next-boundary state components, counters, support, geometry, and all nine reconstructed checkpoint arrays matched gen2 bitwise. 9 gas RHS, 628 native SIGMA calls (61440 energies), 3.57 s. Original 21-file closure and six-slot identity verified before/after; no old trajectory replay. Harness RED import absence and GREEN3 targeted cases preserved.

C11 adaptive_checkpoint.py stores every accepted halfstep, an authoritative macro-endpoint cursor and controls/events/end/dependency binding. Generic next_segment means remaining declared interval; it is not a fixed next adaptive step. Pending midpoint restart and hidden low precision components are refused. Six new targeted cases pass, including atomic roundtrip and dependency mismatch. C10 code unchanged. C11 actual cold restart still pending a new accepted trajectory.
