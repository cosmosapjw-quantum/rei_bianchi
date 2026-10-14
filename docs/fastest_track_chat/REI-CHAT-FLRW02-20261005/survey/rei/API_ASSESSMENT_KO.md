# FLRW 세 식: 실제 REI source 정찰

선택 branch `forward/rust-reion-kernels-20260922`, HEAD `9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa`, tree `27d5c5653b6a85b43bf86f6ca5913f90b9e05106`, draft PR83이다. 마지막 변경은 앞선 REC-PB02 백업 영수증 게시다. recursive tree는 완전하며 AGENTS.md가 없다. F04나 FLRW02 새 구현/반환 경로는 관측되지 않았다. 기존 F03 완료 기록과 FLRW01 계약을 읽었으며 그 시험을 재실행하지 않았다.

현재 Rust crate 전체 24파일을 `inputs/rei_crate/`에 materialize했다. Cargo edition2021, dependencies 없음이다. Git blob SHA-1 24/24 일치하며 `CRATE_INTAKE_CHECK.json`에 SHA256/bytes도 기록했다.

| 식/작업 | 실제 source/API | 현재 확인된 범위 | 필요한 새 경계 |
|---|---|---|---|
| 국소 H/He rate | `hhe_events.rs::hhe_rhs(&HHeModel,&HHeState)` | 3종분율 RHS, 3x3 종별 photon absorption, 3개 collision/RR event, thermal/escape energy; H=0 constant synthetic fixture | 실제 API 출력으로 순수 H x² sink/분율 dilution cancellation과 기준식 연결 |
| 기하/광자수 변환 | `homogeneous_rates.rs::homogeneous_photo_rates(provider,n_absorber,a,nodes)` | comoving cMpc^-3를 proper cm^-3로 한번 변환, source-pinned sigma, 흡수 owner/heat/binding | 팽창에 따른 bin flux·threshold exit는 없음; 새 explicit adapter 필요 |
| 기존 4군 redshift | `group_rates.rs::photon_rates(state,emissivity,p)` | N comoving cMpc^-3; group kappa, r=H*redshift_coeff, 이웃군 feed; 총합 loss는 r0*N0 | lowgroup HI effective-MFP owner가 포함됨. homogeneous HI sigma owner와 중복 금지; arbitrary redshift_coeff는 물리 spectrum의 edge trace 인증 아님 |
| 종별 Gamma | `group_rates.rs::gamma_species` | N만 (1+z)^3로 변환; species cross section 합 | table opacity를 조회하지 않으므로 effective-MFP total count를 이 species Gamma와 항상 동일시할 수 없음 |
| global filling | 현재 선택 crate에 QV/XM/two-phase API 없음 | homogeneous fractional x만 존재 | 분율을 QV로 개명하지 말 것. sharp phase geometry/volume boundary 또는 명시적인 manufactured closure 필요 |

`hhe_rhs`의 H 성분은 `(1-xH)*(sum(c*sigma*Nproper)+ne*beta)-xH*ne*alpha`를 실제 실행한다. `ne=nH*xH+nHe*(xHeII+2*xHeIII)`이며 nHe=0에서 RR은 alpha*nH*xH²다. 결과의 종별 event 배열과 photon RHS는 같은 평가점의 장부이므로, 이 실제 output을 독립 oracle와 비교하면 단순 식 재기록을 넘어선 검증이 된다. source thermal/escaping-energy owner는 instantaneous Case-A toy이며 emitted ionizing photon NUMBER를 제공하지 않는다.

F03 implicit map은 BE endpoint에서 7좌표 residual을 평가하고 full/two-half 비교로 step을 받는다. F00 과거 four-site 설계와 구분된다. F03 반환은 63 crate tests, 세 refinement, 512 accepted/9 rejected 큰-trial run을 기록하지만 uniform state box/uniqueness/remainder/public width는 미평가다. F04가 다음이라는 현재 상태는 보존한다.

## 이번 구현에 적합한 제한된 증분

별도 `flrw_recovery` 모듈에서 기존 hhe_rhs 호출의 실제 국소 source와 종별 event를 재사용한다. source block 밖의 명시적인 FLRW proper/comoving photon 변환 및 bin-edge transfer를 새 ledger로 연결한다. 임의의 effective-MFP owner를 더하지 않고 homogeneous explicit opacity 모형임을 구분한다. 새 adapter와 frozen finite 입력만 먼저 검증하고, 이후 actual native RHS를 반복 호출하는 작은 prescribed expansion pure-H 시간진화를 독립 적분과 대조할 수 있다. 이는 전체 F03 열화학/geometry solver를 자동 확장하거나 F04를 닫는 작업이 아니다.

filling 식은 두 수준으로 구분한다. 고정 volume weights의 cells에서 XM=sum(w*nH*x)/sum(w*nH)와 평균 recombination은 실제 hhe_rhs outputs로 계산할 수 있다. 그러나 이 cell 정보와 x만으로 moving ionized boundary의 dotQV는 결정되지 않는다. QV를 fractional x의 threshold 평균으로 정의해 sharp physical filling으로 승격하지 않는다. 명시적으로 정한 sharp two-phase manufactured fixture에서 dI=1, 같은 T/electron/clumping, 적절한 storage/loss/CaseB 조건을 고정한 후 표준 Q식을 확인한다. `dotQV=s-reff-lz-aother+iextra-doteta-dotXi`를 그대로 계산하는 helper는 독립적인 Q dynamical consumer가 아니라 inventory identity helper다.

최신 사용자 세 식 검증 요청은 이번 scoped 작업을 실행할 근거다. 원 PB02/FT07 deferred 상태를 무관하게 재우선화하지 않는다. 새 작업의 source identity와 실제 실행 결과를 별도로 기록하여 REI-F04 full interval gate, physical EoR history, filling geometry admission과 구분한다.

## 유지할 실패/조건

- 분율·comoving/per-H count에 -3H를 중복 적용하지 않는다.
- Case-B OTS와 explicit ground RR photon을 중복하지 않는다.
- escaping energy에서 ionizing photon 개수를 추론하지 않는다.
- arbitrary band-average hazard는 실제 spectral threshold-edge reconstruction의 증거가 아니다.
- QV=XM은 dI=1 등 조건부이며 모든 평균 ionization fraction에 적용되지 않는다.
- [160,161] historical FAIL, tick160, local<2e-4, public width<2e-3을 유지한다.
- 기존 published suites는 변경 경계의 구체적 위험이 있을 때만 재실행한다.
