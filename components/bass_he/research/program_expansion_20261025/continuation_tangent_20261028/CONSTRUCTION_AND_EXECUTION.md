# R4 constructive alternatives / C4 execution DAG

## Three admissible constructions
1. Refine the existing Bernstein inner/grid outer sandwich. This reuses established proofs but zero-touching boundary polynomials can keep a finite inner-cone gap. More mesh enumeration is unnecessary if a short exact dual certificate succeeds.
2. Exact interval-SOS cone with a generic SDP solver. The quadratic cone has an exact2×2PSD representation. A numerical solver still requires certified residual/sign handling and is more machinery than needed for the already identified two minima.
3. Square boundary witness plus evaluation-functional dual. Saved N16 minima identify61deg lower/73deg upper as candidate active rows. A one-dimensional root and3×3rational identity give an independently checkable global bound. We select this route; actual signs/window/width checks determine its success.

## A completed rational construction (manufactured, not EXFOR data)
Choose nominal rows v(1/4),v(1/10), r=17/20, a=1 and q(z)=(z-17/20)^2. Then q(1/4)=9/25=:L, q(1/10)=9/16=:U. The scalar polynomial
 F(r)=U(r-1/4)^2-L(r-1/10)^2
has F(17/20)=0. At the fixed endpoints F(4/5)=-999/160000 and F(9/10)=1161/160000. Its derivative on this interval is (81/200)r-837/4000>0.
Define h=v(1/4)-(16/25)v(1/10)=(9/25,93/500,561/10000). For b=(289/400,-17/10,1), h.b=0, v(17/20).b=0 and D=d.b=427/600>0.
Choose alpha=1/4,lambda=1/2,mu=1/3 and
 k=alpha*d+lambda*h+mu*v(17/20)=(76/75,543/1000,22133/60000).
For every nonnegative q satisfying v(1/4).b>=L and v(1/10).b<=U, k.b/D>=1/4. The displayed square attains equality. This explicit construction proves the algorithmic connection before the actual data campaign, with an exact known-answer case. It is not a surrogate for the EXFOR-derived result.

## New work dependency order
Fresh survey and baseline -> exact claims/algorithm -> implemented producer+search-free verifier -> independent preexecution review -> actual source S05 publication/pin -> one new campaign -> exact certificate/source review -> one Wolfram control call and saved-only figure -> scoped admission -> S09/S10 and actual central return -> final external delivery.
The two aperture lower-bound solves are independent given the same rows/root/witness/M envelope; the implementation shares those common exact operations. No parallel scientific processes are needed for this small case. Parallel agents provided independent source survey, backup/context survey and primary literature intake. Mechanical implementation goes to requested gpt-6.1-sol, independent scientific review to a nonauthor agent. Unexposed actual model identity remains null.

## Resource and execution contracts
Use the capped single-run wrapper: CPU120s/wall300s/AS768MiB/threads1 for one new primary. This covers the whole runner CPU including startup plus waited children; network/publication/assistant overhead is not included. Keep exact command, source hashes, stdout, stderr, exit code and measured resources. At most one diagnosed targeted repair is allowed only after root authorization and within the same cumulative cap. No old reserve is replenished.
The saved-only plot gets CPU10s/wall30s/AS768MiB/threads1 and one render; no research imports or optimization. Wolfram evaluator gets a20s time constraint and one call, with remote measuredCPU/wall=null if unavailable. The prior current context SERVICE_ERROR is kept separately.

## Meaningful validation roles
C6 checks actual implementation contracts and error paths. C7 checks the equation-to-code correspondence, exact dual residuals/signs, genuine feasibility and signed moment bounds. C8 inspects exact root/enclosure width, source/reproducibility identity and measured cost. These are distinct readings of the same one primary output; no repeated campaign is implied. R6/C9 are one independent nonauthor pass with preexecution, result/figure and closeout checkpoints.

## Implementation review corrections before execution
F1: binary64 outward values converted through shortest decimal strings can round inward. Use exact decimal gridfloor/ceil and an independent Fraction-string enclosure check.
F2: subtracting a post-import runnerCPU baseline omits startup; count fullRUSAGE_SELF and waited children and check the finalwall limit.
F3: label the plotted3-digit width as approximate.
F4: prefix inherited QUARTIC12 self-relative evidence with its original sibling directory. All four are preexecution corrections; no prior science result or acceptance tolerance changes.

R4 complete: alternatives were compared and a full rational example constructed, with a selected route and explicit falsifying checks.
C4 complete: source/review/execution/publication dependencies, executor roles, budgets and stop/repair conditions are concrete.
