# 이 문서의 역사적 시점과 현재 S09 상태

아래 C3–C5 preparation/NOT_RUN 서술은 구현 전 격리 준비 당시의 원문 기록이다. 현재 상태를 뜻하지 않는다. 이후 canonical S05에서 새32/32 검사가 PASS했고 새 저장값 그림도 첫 실행 PASS였으며, S09에서 동일 독립 review pass의 실제 결과 검토 PASS·결함0을 근거로 조건부 aperture reference를 채택했다. 현재 continuation DAG는8 complete +0 pending +3 physical open /11이다. 현재 판정·실행 근거·범위는 `RESULT.json`, `review/RESULT_REVIEW.json`, `ACCEPTANCE_KO.md`를 따른다. 이 갱신은 아래 구현이나 실행 계약을 바꾸지 않는다.

---

# APERTURE07 isolated C3–C5 preparation

Status: **NOT_RUN**. These files are outside the canonical unit. No source, test,
validation, saved-data generation or plotting script has been executed.

The root's `CONTRACT_DRAFT_KO.md` supplies the scientific contract. The applied
skill context is the actual cloud physmath-research-loop **1.3.0**, with main
SKILL.md, STAGE_SELECTION.md, references/POLICY_INTEGRATION.md,
references/CODING_LOOP.md and references/SUBAGENT_MODE.md read. Selected work is
C3–C5 preparation only. The parent forbids recursive delegation and scientific
execution during this preparation; no child agents were spawned.

## Interfaces and formula mapping

- `rational`: exact int/string/Fraction or exact stored finite float; rejects
  bool, nonfinite and unsupported scalar types.
- `AngularMap.compare`: exact signed rational comparison with the original map;
  public stopped point raises `StoppedDirectionError`. Only the boundary finder
  uses the zero auxiliary continuous limit at a=1, mu=-1.
- `AngularMap.preimage`: branch-wise rational bisection on the exact critical
  point -1/a; normalizes rational inner and outer interval unions modulo endpoint
  sets of zero continuous measure. The delta domain is [2^-80,1].
- `normalize`, `union`, `intersection`, `reflection`, `difference`, `SetBounds`:
  exact interval-set operations and conservative enclosure propagation.
- `BernsteinDensity`: nonnegative coefficients of degree 0..8; exact polynomial
  integral and linear weighted integral. Event pair APIs additionally require
  symmetric coefficients. The class does not characterize all positive polynomials.
- `BernsteinDensity.bounds`: includes exact signed mass of the uncertain region
  according to the sign of the linear weight, split at its exact rational root.
  Returns the exact rational lower/upper interval and conservative width bound.
- `pair_response`: one shared mu and reflected -mu; union of both detector
  assignments counts each event once. Returns coincidence, hit, inclusive counts,
  twice-yield represented daughters and direct shared pair-energy bounds 2E0Y.
  Separately enclosed E+ and E- are not asserted to have the same summed interval.

The parameter certificate is conditional on fixed stored gamma and a, with
1<=gamma<=10^6, 0<=a<=10^6. It does not certify the mass/energy conversion or
physical parameter uncertainties. Angular windows accept all azimuths and use
the already integrated polar marginal; azimuthal uniformity is not assumed.
Threshold/atomic measures are explicitly rejected. Zero density validates inputs
and returns zero without root searches; returned preimage is then `None`, not a
claim that the actual geometric preimage is empty.

## Prepared verification and resource path

Thirty-two unittest methods cover independent identity/fold examples, exact
Bernstein beta integrals, interval algebra, signed-weight bounds, stopped/fold
boundaries, invalid inputs, positive density, exchange, shared-event correlation,
8/16/24/40 convergence, and twelve saved native parameter rows. The final method
creates **new** rational saved data for new aperture integrals using an explicit
synthetic density. It uses only saved `source_row`, `gamma`, and `a`; DCS/error
columns are not consumed, and no historical kernel is imported or called.

`scripts/legacy_bounded_runner.py` is a byte-exact copy of the existing pinned
INTAKE01 wrapper (SHA-256
`b0f36cb3ee2f79d4fc29fa6596be37b829d299694f3fd167bf40460a3b976e8f`).
The adapter retains its cumulative CPU4s/wall15s, memory256MiB, one-thread,
one-targeted-repair policy. Its existing tighter per-child CPU3s/wall10s limits
are preserved. Preparation and dependency-manifest work remain outside the
measured envelope and are not reported as zero cost.

The separate existing plot wrapper is reused unchanged. The new three-panel
plotter imports no scientific code and reads only the new saved payload:
finite fold-bin mass; rational bound convergence; shared-event coincidence
counterexample. Its separate measured budget is CPU6s/wall15s/memory512MiB.

## Next authorized action

Root must refresh the post-publication dependency HEAD, admit/copy this source at
S05 under the frozen model, and authorize the bounded validation start. Current
test results, resource measurements, scientific admission and plot review are
**NOT_RUN**, not PASS. No Git operations or publications were performed here.
