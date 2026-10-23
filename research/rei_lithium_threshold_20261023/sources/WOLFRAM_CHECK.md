# Independent Wolfram check recorded by the Astra controller

Status: actual independent kernel evaluation completed before numerical execution.
This file records the controller's observed input/output supplied to the packaging
worker; the packaging worker did not rerun or reinterpret the calculation.

Tool: `mcp__codex_apps__wolfram_wolframlanguageevaluator`.
Requested `timeConstraint`: 15 seconds. Runtime model identity was not exposed.

The first attempt failed to produce roots because the ReplaceAll expression
was not parenthesized correctly. The corrected input below completed:

```wolfram
Clear[u];
poly = ((-7 a u^3 + (p-7) a u^2 + 11u + (11-p)) /.
        {a -> 1501/100, p -> 979/200});
roots = NSolve[poly == 0, u, Reals];
positive = Select[roots, (u /. #) > 0 &];
{poly, roots,
 N[(3107/1000)*(1501/100)*u^2 /. positive, 15],
 FullSimplify[(Exp[delta]-1) Exp[-delta] == 1-Exp[-delta],
              Assumptions -> delta > 0]}
```

Actual completed output:

```wolfram
{1221/200 + 11*u - (631921*u^2)/20000 - (10507*u^3)/100,
 {{u -> 0.37926614319392365}},
 {6.708263233652781},
 True}
```

The unique returned real root is positive. The corresponding energy is in eV
under the source-fit conversion E=(3.107)(15.01)u². The last result independently
checks the exponential identity used in the attenuation comparison bound.
The sigma value and adoption of 1.66e-18 cm² remain tied to the physical source
row and bounded domain in THEORY_CONTRACT.md and the independent mathematical
intake. This symbolic check supplies no new IVP result or numerical admission.
