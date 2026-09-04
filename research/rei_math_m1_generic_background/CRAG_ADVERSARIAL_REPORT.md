# M1 plot-driven CRAG adversarial audit

## Intent

Test whether the exact symbolic oracle is sensitive to the load-bearing sign of
the mixed class-B `epsilon*n*a` term rather than merely reproducing a copied
candidate expression.

## Deterministic samples

Eight integer-valued Jacobi-admissible samples are generated:

```text
four class-A controls: a=0, arbitrary symmetric n
four class-B samples:  n^{ab}a_b=0 with active mixed channel
```

For each sample the script compares the connection-derived Ricci tensor with:

1. the locked candidate formula;
2. a hostile mutation reversing only the mixed `epsilon*n*a` sign.

## Expected plot signature

```text
locked formula
  exact zero residual in all eight samples

sign mutation
  zero residual in all four class-A controls because a=0
  nonzero residual in all four class-B samples
```

The plot uses a numerical floor only to display exact zeros on a logarithmic
axis.  The machine-readable CSV and JSON retain the actual exact-zero status.

## CRAG questions

### Correctness

Do the samples satisfy the Jacobi constraint and does the locked formula agree
with the independently constructed connection curvature?  Required answer:
`8/8 exact zero` for both checks.

### Retrieval

Are the negative controls physically appropriate?  Yes: in class A the
commutator vector vanishes, so the mixed channel is structurally absent and its
sign cannot be detected there.

### Augmented/adversarial

Does the mutation become visible only when the mixed class-B channel is active?
Required answer: `4/4 class-B detections` and `4/4 class-A zeros`.

### Generation

The result predicts that future branch sentinels limited to class A cannot
validate the class-B mixed curvature term.  At least one generic class-B
fixture with nontrivial transverse `n` is mandatory in all subsequent
background regression suites.

## Claim boundary

This plot is numerical adversarial regression only.  Generic authority remains
the exact symbolic reduction modulo the Jacobi ideal.  No background evolution,
numerical stability, runtime, provider or scientific claim follows from it.
