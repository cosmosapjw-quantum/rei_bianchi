- **MINOR — avoidable rejection of finite constant/identity powers.** [interval_ad.rs:122](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/interval_ad.rs:122) evaluates the general derivative formula, including `x*x`, for `p=0` and `p=1`. My probe confirmed `Err(IntervalError)` at positive points `1e-200`, `1e200`, the minimum subnormal, and `f64::MAX`, although the exact values, gradients, and Hessians are finite. The square either underflows into a zero-containing denominator or overflows. [interval_math.rs:129](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/interval_math.rs:129) also rejects scalar `f64::MAX.powf(1)` through `ln → exp`. After validating the complete input and positive domain, special-case Jet powers zero/one as constant one/identity; special-case scalar power one as identity. This is conservative false rejection, **not an unsound enclosure**, and does not invalidate the frozen moderate-range witnesses.

The remaining inspected formulas support the stated enclosure construction: outward basic arithmetic, exact binary reduction, bounded Taylor/atanh tails, and full product/chain/inverse Hessian rules. I found no additional defect within this review.

I executed one bounded probe, compiling the pinned source into a temporary library and linking against it. Compile, link, and execution each exited zero. Quotient mixed partials, exponential/product mixed partials, malformed Hessian rejection, signed zero, subnormal multiplication, overflow rejection, and extreme negative exponential bounds passed their assertions.

Evidence: [source](/tmp/rei-f04-interval-review-20261005-5u_llgm1/probe.rs), [exact argv](/tmp/rei-f04-interval-review-20261005-5u_llgm1/argv.json), [stdout](/tmp/rei-f04-interval-review-20261005-5u_llgm1/2.stdout.txt), and [identity/hashes](/tmp/rei-f04-interval-review-20261005-5u_llgm1/hashes.json). Telemetry used task `REI-F04`.

HEAD matched `d0653167609e7ce5302b14738c384acf19c618e4`; all seven frozen file hashes matched before and after execution. I inspected the frozen tests, validator, and oracle; I did **not** rerun the full validator or edit repository files. This review establishes neither universal correctness nor the actual HHe/root/remainder certificate. Final validation and admission remain with the parent.

<oai-mem-citation>
<citation_entries>
MEMORY.md:3360-3361|note=[kept review focused on numerical correctness and reproducibility]
MEMORY.md:3371-3371|note=[respected trusted local research scope]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
