# 최적화 재사용 조사와 정수 Taylor 변환 검토

관찰: 2026-10-20 02:43 UTC. 선택 범위 R2(근거·재사용)와 R6(정수 다항식 변환의 상보적 검토). 구현·solver 재실행·생산 승인은 하지 않았다.

## 실제 새 결과

VigilODE 152 branches(2 pages), 75 PRs(1 page), 최신 20 workflow metadata를 읽었다. PR71은 기존9f80e38에서64b98521까지8commits/280files가 추가됐다. 실제 CONCLUSION.json에는 별도의 achieved-error matched campaign39261895983(270calibration solves,408timing processes,42pairs)이 있다. 기존756screen과 구별한다. 이 파일을 읽었지만 raw state/timing을 이 조사에서 다시 검산하지 않았다.

PR73(3c015791)은 exact_band_cache.rs와 THEORY,48-row COST.csv를 읽었다. key는 성공한 finite factors에 대응하는 실제 rounded shift와 전체 Jacobian entries의 exact bits다. 같은 Jacobian만으로는 h가 바뀐 shifted matrix가 같지 않다는 반례가 있다. 등록 nonlinear case의 cache hit는0이다. FixedWidth2가 oldbinary보다 대략5% 빠르지만 patchedSlices 자체도 변한다. dyadic linear control은 factor134→8, Jacobian134유지다. REI에 가져올 것은 정확히 같은 입력의 비싼 계산을 재사용하는 조건이다.

PR74(15c43ce7)는 PR본문/변경파일을 읽었다. JVP-only coupled-stage companion이며 기존 scalar hazard exponent workload의 대체 라이브러리로 확인되지 않았다. 보고된19tests/800timing processes의 raw 검산을 이 조사에서 반복하지 않았다.

PR75(6c945b6c)는 residual_first.rs,THEORY,COST.csv,AUDIT.json을 읽었다. COST.csv를 독립적으로 집계하여80rows,76valid,48valid+embeddedpass,4invalid를 확인했다. saved stages에서 residual을 먼저 계산하고 실제 update가 필요할 때만 derivative를 구한다. full-space validation은 유지한다. few-mode JVP59→35,chain144→80,diffusion348→188이다. 작은 문제의 추가 dispatch/barrier는 비용이며4workers가 항상 빠르지 않다. chain384 cap64는10.754173ms,uncappedtransaction1.0023865ms로 나빠진다. 고정 cap을 최적 기본값으로 가져올 근거가 없다.

새 branch research/midcheck-three-solver-20261020의fbfb102d tree에는 measure/audit/patch/run만 있고 완료결과는 아직 없었다. run39359950752는failure,39360079278(head6f1c17a9)는in_progress였다. 이 조사 cutoff 이후 결과는 별도 fresh intake 대상이다.

Dropbox title query의13results와 /ode_solver의3entries를 읽었다. 후자는 모두Oct16자료다. Drive 'vigilode' folder query는0results이며 account-wide completeness가 아니다. REI BR06/RUN18/LRS 최신 archive들은 root의다른intakeagent에게 전달했으므로 중복 whole-download하지 않았다.

## 실제 적용할 수 있는 외부 구현

- num-bigint0.4.6: 기존 locked crate의 BigInt 연산을 재사용해 유리식 각항의 반복 gcd/reduction을 정수 recurrence로 줄인다. 해당 crate는 signed BigInt를 sign+BigUint digit vector로 구현한다. 새 임의정밀도 library를 만들 필요가 없다.
- num-rational0.4.2: 공식 소스에서 Ratio::new가 reduce()를 호출함을 확인했다. 기존 correctness path는 유지하고 S18,S19를 만들 때만 정규화할 수 있다. new_raw는정규화하지 않으므로 이 단계에서는검증된new를2회사용하는 설계가 충분하다.
- Rayon1.12.0: IndexedParallelIterator의정해진index분할/collect_into_vec,with_min_len을 expensiveindependentexp jobs에 적용할 수 있다. 병렬 map 후원래index순서의fold를유지하면합순서가바뀌지 않는다. 작은prefix의각level에과도한task를만드는것과다르다.
- VigilODE의기존pinnedaffine_transport/directedsquaring을그대로재사용한다. 신규PR73/75의관련성은exact-reuse와lazy-work/granularity의설계근거이며, 전체새solver를가져오면현재 frozen opacity 연구와다른수치방법이된다.

추가후보도원문문서로확인했다. std::simd는공식stable문서에서도nightly-only experimental이다. wide는SIMD types를제공하지만 reduce_add/reduce_mul의연산순서를비결정적이라고문서화한다. pulp는runtime CPU detection에따른동등한SIMD dispatch를제공한다. 따라서순서민감한directed reduction은그대로유지하고, 독립lane계산을후보로분리해야한다. approximateSIMDexp를기존certifiedexp대신쓰는것은이변환의정확도계약을충족하지않는다.

rug1.30/MPFR4.2.2는arbitraryprecision과Round::Up/Down, correctlyrounded transcendental의유효한대안이다. 다만 GMP/MPFR nativebuild와다른출력interval을도입하며, 현재순수Rustpolynomial의gcd병목을먼저제거할수있다. faer는중대형matrix용이므로scalar rationalexp비용의직접해법이아니다. 이는패키지성능일반판정이아니라현재연산의적합성판정이다.

## 독립 R6: 정수 recurrence

원함수의입력tau는무차원이며tau>=0이다. 기존range reduction후r=p/q∈[0,1/2],q>0으로둔다. N0=D0=P0=1이고

D_j=j q D_(j-1), P_j=(-p)P_(j-1), N_j=j q N_(j-1)+P_j.

귀납으로D_j=j!q^j, P_j=(-p)^j이며,

N_j/D_j = N_(j-1)/D_(j-1) + (-p)^j/(j!q^j)
         = Σ(k=0..j)(-r)^k/k!.

따라서새S18,S19는원BigRational Taylor와유리수로완전히같다. 양의term크기비r/(j+1)<=1/2이므로alternatingseries로S19<=exp(-r)<=S18. 기존rational_interval이각유리수의exactvalue와f64candidate를비교하고, 기존directedsquare를동일횟수수행하면최종interval끝점도원동작과같다. 정수overflow는BigInt범위에서발생하지않으며비용은allocation/growth이다. 연산단순화의속도향상은실측전미확인이다.

경계조건은원tau0=[1,1],tau>=752=[0,eta],0<tau<752의범위축소/halving수를유지하면처리된다. 새연산은물리계수,sourcebirth,반응량,수치허용오차를바꾸지않는다. eagerexpcache의전수parallelfill은각entry의purefunction평가만병렬화하고key/index/foldorder를유지해야한다. 수학적동등성이있어도개발시exact-bitparity를직접확인하는것이목표변경의가장작은검증이다.

검토결론: 이정수recurrence와orderedparallelmap설계는명시된불변량하에서구성적으로타당하다. 실제implementationdiff/실측은root의C9pass로연결된다. 이번검토가그미실행결과를대신하지않는다.

## 문헌·도구 provenance

SciSpace질문: How can rigorously bounded exponential functions be evaluated efficiently with fixed-point arithmetic, directed rounding, range reduction and parallel batching while retaining interval guarantees?

Priest(1997), Fast table-driven algorithms for interval elementary functions, DOI10.1109/ARITH.1997.614892 및 Kulisch&Snyder(2011), exactdotproduct, DOI10.1007/S00607-010-0127-7을발견했다. 이들은관련문헌후보/abstract수준이다. KIT fulltext는CRAWL_NOT_FOUND였으므로미독상세정리를인용하지않는다. 이번recurrence정당화는위의직접유도에근거한다.

실제사용한primarydocumentation:
- https://docs.rs/num-rational/0.4.2/src/num_rational/lib.rs.html
- https://docs.rs/num-bigint/0.4.6/num_bigint/
- https://docs.rs/rayon/1.12.0/rayon/iter/trait.IndexedParallelIterator.html
- https://doc.rust-lang.org/stable/std/simd/
- https://docs.rs/wide/latest/wide/struct.f64x4.html
- https://docs.rs/pulp/latest/pulp/
- https://docs.rs/rug/1.30.0/rug/float/enum.Round.html
- https://docs.rs/rug/1.30.0/rug/struct.Float.html
- https://www.mpfr.org/mpfr-current/mpfr.html
- https://docs.rs/faer/latest/faer/

Repo source/results URLs are fixed by INTAKE.json.new_heads and sources/ files. PR73: https://github.com/cosmosapjw-quantum/vigilode/pull/73 ; PR75: https://github.com/cosmosapjw-quantum/vigilode/pull/75 .

skill_context_used: physmath-research-loop1.3.0 actualSKILL.md, references/POLICY_INTEGRATION.md,SUBAGENT_MODE.md,THEORY_LOOP.md read. SelectedR2/R6 only; nochildreview, noimplementation, noextraauditloop. Originaluserobjectiveandfrozenaccuracyretained.

PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.

