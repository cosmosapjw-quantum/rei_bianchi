# Matter / radiation anisotropic-stress extension — actual local results

**실제 새 trajectory 606/606개가 완료되었고 실패는 0개다.** 기존 625개 history는 ODE를 다시 풀지 않고 성분별로 분해했다. 새 결과는 독립 final review와 response-fit addendum에서 **PASS_SCOPED_PRELIMINARY** 판정을 받았으며 blocking findings는 없다. [Final review](evidence/FINAL_REVIEW.md)와 [response-fit addendum](evidence/RESPONSE_FIT_ADDENDUM.md), 각각의 JSON을 참조한다. 기존 preliminary pilot의 PASS도 그대로다. 원본 `../pilot.py`, vendor와 기존 625개 raw 파일은 변경하지 않았다. 이 확장의 과학적 범위는 `CONTRACT_KO.md`, 이론 설명은 controller의 `THEORY_KO.md`에 고정되어 있다.

## 성분과 단위

모든 성분은 동일한 **comoving orthonormal normal frame**에서 정의한다:

`pi_m=diag(-p_m,-p_m,2*p_m)`, `pi_r=diag(-p_r,-p_r,2*p_r)`.

Matter는 fm=.1의 massive collisionless canonical component와 나머지 pressureless dust다. Dust의 anisotropic stress는 0이다. Radiation은 photons와 exactly massless neutrinos이며, 동일 초기 brightness와 collisionless evolution 때문에 하나의 energy vector를 공유한다. Native baryonic H/He stress, Thomson이나 stellar feedback는 추가하지 않았다.

각 saved history에 다음을 따로 저장한다.

- `p_m_J_m3`, `p_r_J_m3`: 위 frame에서의 pressure scalar, J/m³.
- `signed_Pi_m`, `signed_Pi_r`: `sqrt(3)*(8*pi*G/c²)*p_X/H²`.
- `Pi_m`, `Pi_r`: 각 signed component의 절댓값.
- `signed_Pi_total = signed_Pi_m + signed_Pi_r`.
- `Pi_total = abs(signed_Pi_total)`. 성분 magnitude의 합으로 대체하지 않는다.
- `work_m_J_m3_per_x`, `work_r_J_m3_per_x`: `-6*(s/H)*p_X`, x=ln(a/a_ref)당 anisotropic energy-work 항.

같은 순간 H가 모든 성분을 정규화한다. `Sigma=sqrt(3)*abs(s)/H`이며 tensor half-contraction norm을 유지한다. 상태는 `(Href*elapsed_seconds,b,s/Href,E0,E2,E4,E6,E8)`의 8개다. 원본 helper의 current massive moments와 radiation even matrix를 그대로 사용한다.

## 실제 계산 구성

1. **기존 625개 / 40,625 samples 분해, 새 ODE 0개.** 기존 NPZ의 massive moment, E2, H, x로 signed 성분과 실제 압력을 계산했다. Component 합과 기존 signed Pi의 최대 절대차는 **4.336808689942018e-19**다. 결과는 `decomposition/cases/*.npz`, `decomposition/histories.csv`, `decomposition/endpoints.csv`, `decomposition/decomposition_receipt.json`에 있다.
2. **새 matter slice 600개.** 기존 Sigma 25 signed values와 Pi_m의 24 nonzero signed values를 조합했다. |Pi_m0|≤.0004이고 새 조건의 radiation k는 0이다. A_m은 실제 source helper와 bracketed inversion으로 결정했다. 최대 |A_m|는 **0.8275025625756662**로 source positivity 범위 [-1,2] 안에 있다.
3. **기존 neutral control 25개 참조.** `reference_controls.json`은 old case/source/config identity, old actual k, old JSON/NPZ hash와 실제 realized component axes 및 endpoint를 보존한다. 이 행들은 **REFERENCE_REUSE**이고 새 계산이나 새 source resume가 아니다. `results/new_sweep/matter_slice_with_reference_controls.csv`는 600개 새 행과 25개 참조 행을 합친 625행 table이다. Reference의 tiny component offsets를 exact zero 또는 bitwise equivalence라고 부르지 않는다.
4. **새 mixed cancellation 6개.** Signed S0∈{0,+.004,-.004}와 signed Pi_m0=±.0004, signed Pi_r0=−signed Pi_m0를 각각 실현하여 coupled ODE를 풀었다. 별도 trajectory의 선형 합으로 만들지 않았다.

새 계산은 mass/Tref=30, fm=.1, 24×12 Gauss3 cells, L8, 65 saved samples, zbar20→4, DOP853 rtol3e-11/atol3e-13이다. `component_pilot.py`는 parent reduced class를 상속한다. Worker의 matrix/basis를 재사용하고 amplitude inversion 중 하나의 current momentum object만 유지한다. Amplitude inversion의 각 trial A마다 원본 CanonicalMomentumFV와 그 quadrature를 다시 구성한다. Quadrature construction이 cached되어 있다고 주장하지 않으며, 재사용되는 것은 worker의 energy matrix/basis다. 거대한 ensemble state로 합치지 않는다.

## 새 검증의 관측 결과

기존 six-case/L8-L12/tolerance suite는 반복하지 않았다. 새로 prescribed된 네 원본40-state/reduced8-state 비교와 두 signed-A energy check만 실행했다.

| 검사 | 관측 최대값 | 계약 ceiling |
|---|---:|---:|
| 네 새 source/reduced 비교: b,s/H,E0,E2,signed Pi_m/Pi_r/total | 1.7031948778173682e-11 absolute | 1e-8 |
| 원본 source H² constraint relative residual | 2.220446049250313e-16 | 2e-13 |
| 두 massive directional energy identity relative residual | 1.4810608772742288e-10 | 1e-7 |
| 새 606개의 초기 component-axis realization | 4.336808689942018e-19 absolute | 1e-12 |
| 기존625 component-sum versus old signed Pi | 4.336808689942018e-19 absolute | 기록된 reconstruction check |

모든 saved energy/H는 finite positive다. 새 최소 massive cell population은 **5.485187002940815e-31**, 65시점×128 Gauss angular nodes의 최소 reconstructed massless brightness는 **0.8020344325165379**다. 이는 sampled 진단이며 global massless positivity proof가 아니다. `validation/metrics.json`과 네 comparison NPZ에 실제 source/reduced states 및 모든 수치를 보존했다.

세 표적 검사가 통과했다: actual helper inversion/positivity와 불가능 target rejection, 정확한 600+6 unique grid, 25 reference의 원래 provenance 보존. 별도 `evidence/PARENT_IMMUTABILITY_CHECK.json`은 parent six model files와 기존625×4 raw files, 합계 **2,506개 파일이 이전 manifest와 byte-identical**임을 확인한다.

## Mixed cancellation의 실제 endpoint

아래 S는 signed `sqrt(3)*s/H`다. 모든 mixed 행의 initial total signed stress는 numerical axis tolerance 안에서 0이며 각 성분은 nonzero다.

| S0 | signed Pi_m0 | S_end | signed Pi_m,end | signed Pi_r,end |
|---:|---:|---:|---:|---:|
| 0 | +.0004 | −4.908041156489128e-5 | +2.2769506379788563e-5 | −9.40362719772204e-5 |
| 0 | −.0004 | +4.907894872787359e-5 | −2.2767224435398605e-5 | +9.402953343988549e-5 |
| +.004 | +.0004 | +4.085005532989926e-4 | +2.233495941649623e-5 | −9.924939284976251e-5 |
| +.004 | −.0004 | +5.065476472736238e-4 | −2.3078835223954772e-5 | +8.845279060530251e-5 |
| −.004 | +.0004 | −5.066542916516476e-4 | +2.3205809365651725e-5 | −8.881396817038218e-5 |
| −.004 | −.0004 | −4.083821964916134e-4 | −2.245534259993618e-5 | +9.961803038276676e-5 |

이는 실제 coupled histories의 endpoint를 옮긴 표다. Component cancellation이 초기와 끝에서 동일하다고 가정하지 않는다. 상세 성분 합과 total magnitude는 endpoint CSV 및 raw NPZ에서 읽을 수 있다.

## Raw output, figures and receipts

- `results/new_sweep/cases/`: 새606의 8-state+component history NPZ, identity/realization/endpoint JSON, 개별 stdout/stderr.
- `results/new_sweep/endpoints.csv`, `histories.csv`, `run.json`, `summary.json`: 새 trajectory만 606개. 참조 25개를 새 trajectory count에 더하지 않는다.
- `results/new_sweep/matter_slice_with_reference_controls.csv`: 새600+참조25의 provenance가 표시된 companion-slice table.
- `results/new_sweep/plots/matter_sigma_end_heatmaps.{png,pdf}`: 독립 shear/matter sign 네 panel, physical Sigma0/Pi_m0 axes와 공통 color scale.
- `old_history_component_decomposition.{png,pdf}`: 처음에 matter-isotropic인 기존 대표 history를 새 ODE 없이 분해. Signed 성분의 작은 값도 보이도록 symlog scale을 명시했다.
- `mixed_cancellation_components_sigma.{png,pdf}`: 여섯 mixed coupled histories의 signed matter/radiation/total과 Sigma. 각 그림의 전체 plot CSV와 plot_summary.json을 함께 저장했다.
- `receipts/`: 실제 command argv, stdout, stderr, environment, exit status. 모든 현재 command가 exit0이다.

새 sweep의 outer command wall은 **58.906940554s**, `run.json`에 기록된 trajectory-batch wall은 **14.977557074s**, aggregate child task wall은 **16.523054625s**다. Outer command에는 CSV 증거 조립도 포함된다. 이 값들은 finite budget receipt이며 detailed timing comparison이나 speedup/RSS 감소 주장이 아니다. 관측 local worker 수는 6,7,8이며 cap8을 지켰다. CPU affinity/quota, spare CPU, host/cgroup memory, 최소512MiB reserve와 명목256MiB/worker로 batch마다 자원을 다시 확인했고 BLAS/OpenMP는1, workers는 nice10이다. 명목 memory는 measured peak RSS가 아니다. 새 확장의900s wall/3600s aggregate child cap 안에서 완료되었다. 기존 V12 cap/debit는 변경하지 않았다.

## 재현 명령과 NCP

이 디렉터리에서 실행한다. 새 실행은 새 output/receipt 경로를 사용한다. 기존 분해와 완료된606을 자동 반복하지 않는다.

```bash
python ../record_command.py --receipt-dir receipts/new_check -- python -m unittest -v test_components
python ../record_command.py --receipt-dir receipts/new_validation -- python component_pilot.py validate --output validation_new
python ../record_command.py --receipt-dir receipts/new_local -- python component_pilot.py sweep --site local --max-workers 8 --wall-seconds 900 --child-seconds 3600 --output results/new_local
python ../record_command.py --receipt-dir receipts/new_plots -- python plot_components.py --run results/new_local
```

Resume는 matching new model/contract/parent6 files/reference-table/config/case identity만 허용한다. FAILED 행은 자동 재실행하지 않고 started-but-unfinished files가 있으면 중단한다. 새 물리/tolerance 정책 변경은 controller에 반환해야 한다.

`run_ncp.sh`는 source가 기존 checkout에 정상 전달된 뒤 **새606만** finite cap64/900s/3600s로 실행하고 성공 후 NCP-labeled plots를 만든다. Parent Python source/vendor와 이 디렉터리의 `reference_controls.json`, `old_representative_histories.csv`가 필요하다. 두 table에 참조 endpoint와 representative historical samples가 들어 있어 **전체 기존625 raw NPZ를 NCP에 복사할 필요가 없다.** NCP 실행 자체는 하지 않았다. Source-level cap64 지원은 actual64-core execution이나 speedup 증거가 아니다.

독립 review와 response-fit addendum은 PASS_SCOPED_PRELIMINARY로 완료되었고 numerical gate는 닫혔다. Source/validation checkpoint는 `34f93a48778a2d8a36b058e33de5302732752bae`에 게시되었다. Final delivery metadata, canonical DAG, 후속 게시와 backup은 root controller가 마무리한다. 실행 당시 `run.json`/`summary.json`에 저장된 PENDING_INDEPENDENT_REVIEW는 그 시점의 historical status이며 실행 증거를 다시 쓰지 않는다. 이 판정은 production admission, native H/He, non-LRS/general-Bianchi closure, full distribution/quadrature convergence를 의미하지 않는다.
