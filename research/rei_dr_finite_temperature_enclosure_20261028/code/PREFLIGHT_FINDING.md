# F-PLOT1 — bounded pre-execution presentation correction

Finding source: actual root read of prepared plot_saved.py,2026-10-28. The original displayed scientific Decimal strings via first12-character slices, which could drop their exponent while retaining m³/s units. Impact: misleading displayed rates despite unchanged saved numerical data. No figure had been executed.

Smallest correction applied: Decimal .5E formatting retains sign/mantissa/exponent; left bars explicitly normalize each blue/red pair to its own clipped value; right title shortened; six individual h labels replace ambiguous1..6;0/1 ratio cues added. Rate implementation/tests/source are untouched.

Renderer availability was inspected administratively with importlib.util.find_spec only: cairosvg absent, PIL spec present. Executable lookup found /usr/bin/inkscape and /usr/bin/convert. No renderer was run, no plotting library imported, and no scientific module/test was executed. The prepared single presentation invocation now converts its SVG to PNG with the observed Inkscape executable, preserving raw renderer stdout/stderr/exit and both output identities. There is no fallback rerender. Actual PNG inspection remains pending the authorized invocation.

Before plot SHA256:98652fc9cfeddd2ed3455a7e79b68a49b0bceef33420abaac20d8e79485cb46c.
After plot SHA256:ba410df5a2099682d9c455f0d2b263fda10673aa6069893e30d04ee548f39b2a.

The external whole-command supervisor must enforce the aggregate<=1.5CPU-s presentation reservation over the plot and renderer; per-process RLIMIT_CPU alone is not an aggregate renderer limit. Actual runtime feasibility remains unmeasured. If the single bounded conversion fails or exceeds its watchdog, preserve artifacts and stop; no automatic rerun. Unknown preparation/metadata overhead remains UNKNOWN_NOT_ZERO, and no grant is inferred.
