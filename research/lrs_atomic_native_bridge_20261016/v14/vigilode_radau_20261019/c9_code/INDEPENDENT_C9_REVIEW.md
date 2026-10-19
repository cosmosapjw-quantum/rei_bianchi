# 독립 C9 검토 — native Rei / VigilODE Radau adapter

검토자: `/root/dropbox_v15_intake`, Astra 독립 실행 문맥. 검토 대상 adapter의 작성자는 `/root/v16_bounded_coder`이다. 검토자는 앞선 VigilODE 공개 API·의존성 intake를 담당했으나, 여기의 새 Rust adapter·native child·실행기는 작성하지 않았다. 이번 C9에서는 source 읽기, 보존된 실행 자료의 hash 검증, 원시 사건·상태 자료를 이용한 Python 재계산만 수행했다. 새 native 실행, Rust source 수정, Git·cloud 변경은 수행하지 않았다.

## 판정

**선언된 19개 유한 native 설정에 대한 source·실행·회계 검토 PASS. 미해결 P0/P1 없음.** 첫 검토에서 실제로 발견한 유한차분 오류 분류 문제는 명시적 typed domain/fatal 구분으로 수정되었고, 해당 회귀와 최종 source N=4 재실행을 확인했다. 이 PASS는 보존식, API 연결, 물리 영역 검사, 실행 추적성을 확인하는 판정이다. 전 구간 source-on 시간 차수, uniform stiff 정확도, 임의 상태의 양수성, Case B, fullEoR, signed Bianchi의 승격을 포함하지 않는다.

Root의 `CONTRACT.md`가 과학적 범위의 기준이다. 원래 잘못 지정되었던 `n_mu=2`는 변경되지 않은 native angular API가 거부했으며, root가 native 최소 지원값 8로 계약을 수정했다. 초기화 실패 4건과 첫 N=4 gate는 보존된 선행 시도다. 최종 N=4 재실행은 동일한 유일 설정이며, 최종 matrix의 19개와 별도의 새 문제로 중복 집계하지 않는다.

## 1. Source·실행 결속

VigilODE 의존성은 immutable source `8a8bd409b1d96c7b7421f496d229e119fd3d284e`의 실제 공개 `OdeProblem`, `radau_step`, `radau_iia3_tableau`, `WorkCounters`를 사용한다. 이 source의 crate payload는 intake에서 최신 관측 research PR71 `0bab431e1031f86eb3ddb44371240bce49ae2376`과 동일함을 확인했다. 코드 경로는 standalone research crate의 실제 Cargo path dependency에 결속되어 있다.

새 native child의 실제 경로는 `v15_work/native_owner/rust/rei_microphysics/src/axbi_native_rhs.rs`이다. 초기 C9 작업 메시지에 있던 `v16_work/native_owner` locator는 존재하지 않으며, 실제 Cargo 경로와 root 계약은 올바른 v15 native owner를 사용한다.

| 최종 실행에 결속된 항목 | SHA256 |
|---|---|
| `implementation/src/lib.rs` | `90a55821c585c0314484053b2efecc9a255e5ef1c5b80732e9c97796c6251f13` |
| `implementation/src/main.rs` | `92b2487885a3d6f3048cf66132fd5fa5c68df2883d2cebdd958a6120e8df8926` |
| `implementation/tests/focused.rs` | `3f8832c1c7fbd323b1c62d2df32c5417338787fb3aebfeb6cbde638fc778fed4` |
| native `axbi_native_rhs.rs` | `56b88341c5d87c8a1f9a44f3bb364fcf13cefd424b5937e47693c787563480f2` |
| native `axbi_covariant_transport.rs` | `e201d5f6ad973e0ea13e4a7aaa6bfb07fef41bbd4b4104eb7911d26f4c1b66ef` |
| 최종 19개 설정의 공통 실행 바이너리 | `358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905` |
| 최종 N=4 실행 전 source archive | `10b1302f02d91480bc6f0843d3fa2880205053e30442032daf9b3479141378dc` |

`final_source_n4/inputs.json`, `sources.tar.gz`, `outcome.json`, `stdout.txt`, `stderr.txt`, `raw.json`을 직접 읽었다. archive의 637개 payload hash가 모두 입력 manifest와 일치하며, stdout·stderr 전체 byte hash도 일치한다. 종료코드는 0, truncated는 false, 원시 결과의 completed는 true이다. 최종 build 및 분류 회귀의 stdout·stderr hash도 직접 검증했다. 해당 회귀의 library/test source hash는 최종 실행 source와 동일하다.

19개 matrix 설정마다 위의 검증을 반복하여 실행 완료를 판정했다. 각 source archive는 637개 또는 638개 payload를 담는다. 두 manifest 간 차이는 `run_matrix.py` 추가와 `IMPLEMENTATION_HANDOFF.md` 내용뿐이며 수치 source는 동일하다. 각 run의 source archive 자체와 내부 모든 payload를 실제로 읽었다. 파일명·목록만으로 완료를 추론하지 않았다.

첫 gate의 formatting 이전 source byte snapshot은 회수 가능한 완전한 원본으로 주장하지 않는다. 그 gate의 input hash·binary hash·로그·결과는 보존되어 있으나, 최종 admission의 근거는 typed-FD 수정 후 source bytes를 실행 전에 동결한 N=4 재실행과 이어지는 matrix이다.

## 2. 기존 native source 보존

`NATIVE_PREFIX_PRESERVATION.json`은 직전 C10 frozen archive의 기존 source/Cargo 52개와 비교한 기록이다. archive SHA256은 `1c55c41bb6426afed99a8df75e08f0df1b17502926defd413fbb5a2b1d3c015d`이다.

기존 파일에서 유일하게 달라진 것은 `axbi_covariant_transport.rs`의 **40,592 byte 원문 뒤에 추가된 173 byte module hook**이다. 기존 prefix는 정확히 동일하다. default/adaptive/checkpoint, 기존 driver·physical birth·SSPRK2, MD14, Verner, Grackle, EOS source body가 유지되었다. 새 direct RHS는 이 파일의 child module로 private prepared-node 자료에 접근하며 별도의 복제 closure나 rate table을 만들지 않는다.

## 3. 실제 물리·수치 연결 검토

### Direct native photon RHS와 단위

`PreparedAbsorption::native_rates`는 실제 prepared node의 reference energy `q`, photon number per total H, native cross section, physical excess energy를 사용한다. 각 absorber의 (c n_{\rm abs}\sigma n_\ell)를 사건률 per H/s로 합산한다. 셀의 (\dot N)과 (\dot U_{\rm ref})는 node에서 직접 누적한다. energy-offset derivative 역시 (-(q-\ell)\,dP/dt)를 직접 합산하므로 FE 결과와 원상태를 빼는 방식이 들어 있지 않다.

photo gamma의 `c*n_H*number*sigma`는 absorber당 rate이며, native point provider가 absorber density를 곱하면 독립 node 사건률과 일치한다. 열은 물리 에너지 (E=q\,r(a,\mu))의 excess를 사용하고, reference-energy sink는 (q)를 사용한다. 따라서 geometry 고정 chemical segment에서 물리 광자 에너지 sink는 reference sink에 ray scale을 곱한 값이다. Native gas provider에는 proper (n_H,n_{He}), (H=0), (T_{\rm CMB}=2.7255/a)와 native photo input이 전달된다. geometry work는 별도 map이 소유한다.

고정 지지구간에서 각 양의 셀은 (N/N_0)와 ((U_{\rm ref}-\ell N)/[(u-\ell)N_0]) 두 좌표를 사용한다. 점 지지구간은 number 한 좌표, 정확히 빈 셀은 좌표를 갖지 않는다. 네 gas 좌표는 HII, HeII, HeIII, (w_{\rm eV}/w_0)이다. scale과 support는 chemical substep 안에서 고정되며, 각 다음 chemical call에서 실제 새 photon 상태로 다시 구성된다.

원시 source-on 첫 macrostep의 차원은 `[4, 84, 84]`이다. 첫 실제 birth 전에는 photon unknown이 없고, birth 직후 양의 새 셀을 반영한다. 전체 Radau 자료에는 4D segment 3개와 84D segment 195개가 있다. 84D system의 3-stage dense Newton block은 252D이며, ledger unknown을 억지로 추가하지 않는다.

### 공통 stage 가중치와 transaction

반환된 stage increment (K_i)에서 (Y_i=y_0+\sum_j A_{ij}K_j)를 복원하고, 세 stage의 native RHS·사건률을 실제로 다시 평가한다. gas와 photon은 같은 coupled state의 RHS를 사용한다. P/C/R/D, CE/RR/DR/FF, signed CMB, escape는 모두 같은 positive (b_i\Delta t)로 누적한다. 별도 중점 ledger를 섞지 않는다.

최종 photon state, EOS 및 unchanged `Driver::validate`가 통과한 뒤 candidate를 commit한다. chemical 실패는 physical state·physical ledger를 보존하고 시도 수와 RHS attempt를 청구한다. birth wrapper는 macrostep 전체 clone을 사용하므로 중간 geometry map·birth 이후의 실패도 원래 physical state에 commit되지 않는다. budget 회귀는 실제 native 후보를 RHS cap으로 실패시킨 뒤 이 보존을 확인한다.

Radau callback의 domain error가 upstream Newton 전체를 종료할 수 있다는 기존 API 특성은 유지한다. 재분할이나 clipping으로 성공을 만들어내지 않는다. `radau_step`의 accepted endpoint 출력, stage replay 및 ledger commit의 순서를 검토했으며 결과에 맞춘 tolerance 완화는 없다.

### 실제 GL2 birth와 물리 clock

birth는 원래 `PhysicalBirthRule`의 node를 사용한다. 각 구간은 실제 binary64 begin/end에서 `ln_1p((end-begin)/begin)/H_FLRW(sqrt(begin*end))`로 proper dt를 얻고, geometry를 midpoint와 endpoint로 이동한다. source는 (a_0\exp(c\,\Delta\ln a))에서 native `transport.inject`를 호출하며, proper weight는 (w\,\Delta\ln a/H(a_{\rm birth}))이다.

실제 focused parity 회귀는 native SSPRK wrapper와 Radau wrapper의 birth 시각, proper weight, source number/energy, 모든 segment begin/midpoint/end/dt를 비교하고 통과했다. C9 원시 matrix audit는 다음 segment의 좌표 scale·복원된 moment에서 birth 증가량을 별도로 재구성했다. 최대 차이는 photon N (2.095\times10^{-18}/H), 물리 photon U (4.347\times10^{-17}\,\mathrm{eV/H})이다. 선언된 segment endpoint로 재구성한 gas·photon work와 native ledger의 차이는 각각 (1.581\times10^{-15}), (2.046\times10^{-16}\,\mathrm{eV/H}) 이내였다.

## 4. 발견한 구체적 결함과 수정 판정

**P1 — FD fallback이 비영역 오류까지 숨기던 문제: CLOSED.** 최초 `Context::jacobian`은 resource 오류를 제외한 모든 한 방향 평가 실패를 one-sided finite difference로 대체했다. 이는 native arithmetic failure, 잘못된 prepared state, provider/internal 오류까지 허용할 수 있어 계약의 “invalid perturbation에 한한 fallback” 조건에 어긋났다. 첫 gate에서 이 문제로 수치 결과가 손상되었다는 증거는 발견하지 않았다.

수정 후에는 `EvaluationError::{PerturbationDomain,Fatal}`로 분리된다. 명시적으로 확인한 fraction envelope, 양의 thermal coordinate, frozen photon support envelope 및 정상적으로 계산된 EOS 온도가 native `[1,10^6] K` 밖인 경우만 domain이다. coordinate shape/nonfinite, decode/EOS arithmetic, prepare, direct native rate, provider 및 resource 오류는 모두 fatal로 전파된다. `InvalidInput` 전체를 whitelist하지 않는다. base state 오류도 fallback하지 않는다.

직접 읽은 회귀는 양 방향의 fatal propagation, domain+fatal 조합 및 두 방향 domain 실패를 포함한다. `classified_focused`의 실제 결과는 분류 회귀 1개와 native focused test 6개 PASS, exit 0이다. 이 수정 후 동일 N=4 설정을 최종 source에서 한 번 다시 실행했으며, 19개 matrix는 이 최종 binary를 사용한다.

## 5. 실제 실행 규모와 독립 원시 회계

| 항목 | 실제 확인값 |
|---|---:|
| 유일 설정 | 19 |
| completed / failed / truncated | 19 / 0 / 0 |
| 저장된 accepted macro 상태 | 198 |
| Radau chemical segment / stage | 198 / 594 |
| Radau prepared node 수 | 0, 640, 704 |
| 전체 RHS attempt, FD·replay 포함 | 38,840 |
| raw native wall 합 | 9.146159986 s |
| stdout/stderr capture를 포함한 process wall 합 | 10.910020730 s |
| 보고된 Radau max component residual / scaled atol | 0.0550948176 |
| 보고된 Radau max library WRMS | 0.0108168860 |
| accepted SSPRK max FE stage tau | 0.3659839504 |

RHS 수는 “native point 계산 완료 수”와 같은 의미로 바꾸지 않는다. wrapper budget은 decode 이전에 attempt를 청구하며, finite-difference 및 accepted-stage replay 호출도 포함한다. 최초 N=4 자료의 네 chemical step은 각 193 attempts, 합계 772였다. 한 step은 84D Jacobian의 base+양 방향 169 attempts, 21 library RHS calls 및 3 replay calls와 일치한다.

`audit_fixed_gate.py`와 `audit_matrix.py`는 실제 JSON의 binary64 round-trip 값을 Decimal60으로 올려 계산한다. 보고된 energy residual 또는 affine audit column을 독립 endpoint 회계의 입력으로 사용하지 않는다. 원시 P/C/R/D와 CE/RR/DR/FF/CMB/escape를 공통 stage weight로 다시 적분하고, endpoint fraction·w·전체 photon N/U 배열에서 별도로 계산한다. 실제 q=0 geometry에서 (U=\sum U_{\rm ref}a_{\rm ref}/a)를 사용했다. 배열 합과 별도 pool inventory도 대조했다.

아래는 각 이력의 초기 상태부터 모든 accepted endpoint까지 재구성한 **누적 prefix 198개 전체의 최대 절댓값**이다. 한 macrostep 잔차와 누적 잔차를 혼동하지 않는다.

| 독립 회계 | 최대 누적 잔차 |
|---|---:|
| HII 사건 변화, per H | (8.74\times10^{-17}) |
| HeII 사건 변화, per H | (9.16\times10^{-18}) |
| HeIII 사건 변화, per H | (1.44\times10^{-18}) |
| 전자 사건 변화, per H | (9.59\times10^{-17}) |
| photo binding = \(\sum\chi_jP_j\), eV/H | (3.21\times10^{-17}) |
| binding 변화, eV/H | (1.45\times10^{-15}) |
| escape 독립 분해, eV/H | (1.95\times10^{-20}) |
| thermal + gas work, eV/H | (8.01\times10^{-15}) |
| gas + binding + escape + work − CMB − photo input, eV/H | (8.19\times10^{-15}) |
| 전체 photon number + absorption − birth, per H | (7.82\times10^{-17}) |
| 전체 physical photon energy + photo input + photon work − birth, eV/H | (9.26\times10^{-16}) |
| photon + gas + binding + escape + work − CMB − source energy, eV/H | (8.19\times10^{-15}) |

사용한 (Y=.2454/[4(1-.2454)]\)와 threshold `[13.598434599702,24.587389011,54.41776] eV`는 실제 source에서 읽었다. 전자수는 (x+Y(y+2z)), binding은 (\chi_Hx+Y[\chi_{HeI}y+(\chi_{HeI}+\chi_{HeII})z]\)이다. capture binding과 RR/DR thermal cooling을 분리하고, CI binding 증가와 CI thermal sink를 같은 사건으로 연결했다. signed CMB는 gas 유입을 양으로 사용했다.

기존 V14 CSV와 달리 이번 raw에는 모든 active photon N/U 배열이 있으므로 이 **선언된 native finite inventory**의 수·물리 에너지는 독립적으로 감사할 수 있다. passive pool과 boundary 수·에너지는 실제로 모두 0이다. 다른 boundary 상황을 검증했다는 의미가 아니다. stage node의 개별 값과 per-cell RHS vector 전체는 저장되지 않았으므로 각 셀 derivative를 원시 파일만으로 독립 재평가했다고 주장하지 않는다. 단, node의 독립 event/binding/heat totals와 native gas event rates는 대조했다.

## 6. 유한 refinement 자료의 해석 범위

`INDEPENDENT_REFINEMENT_SCREEN.json`은 저장된 19개 endpoint만으로 계산한 실제 차분과 log2 비율을 보존한다. root의 최종 과학적 분석을 대체하는 차수 인증이 아니다.

- Fixed geometry Radau N=2,4,8,16에서 주요 HII/HeII/N/U/w/T/P_HI 채널의 연속 관측 비율은 약 4.89–4.97이며, HeIII는 약 4.925와 5.025이다. 이 실제 native 설정에서 5차에 가까운 감소를 관측했다고 보고할 수 있다.
- Fixed geometry SSPRK N=8,16,32의 같은 채널은 약 1.987–2.165이다. 기존 SSPRK의 이 유한 coupled control에서 2차에 가까운 감소를 관측했다고 보고할 수 있다.
- Source-on GL2 Radau N=4,8,16의 gas 채널에는 단일 공통 차수를 부여하지 않는다. 예를 들어 HeIII 연속 차이는 (2.08\times10^{-17},-6.94\times10^{-18}\), w 차이는 (-8.62\times10^{-14},-3.77\times10^{-14}\,\mathrm{eV/H})이다. HeIII의 단순 log2 비율 1.585를 물리 시간 차수로 해석하지 않는다. photon N과 U도 각각 약 3.486과 4.129라는 서로 다른 유한 비율을 보이므로 wrapper 전반의 일반 4차 또는 5차 승격은 부적절하다.
- Seeded-disabled GL2 Radau는 N/HII/U와 gas의 HeII/T 등에서 다른 유한 비율을 보인다. 기존 geometry composition까지 포함한 전체 wrapper를 단일 Radau 차수로 부르지 않는다.
- 가장 미세한 Radau를 사용할 때에도 그 자체의 인접 refinement와 절대 차이를 함께 표시해야 한다. 엄밀한 reference error bound나 uniform stiff 정확도가 새로 생긴 것은 아니다.

이번 자료는 negative CMB transfer만 포함한다. 이전 signed-CMB 제조 검산을 새 native positive-CMB 이력으로 재집계하지 않는다. optional large-optical-depth probe와 추가 refinement는 실행되지 않았다.

## 7. 보고·전달 시 유지할 한계

Raw `config.newton_atol_scaled=1e-13`은 Radau Newton 설정이다. 실제 SSPRK 비교기는 unchanged source clock의 nonlinear tolerance `1e-15`를 사용한다. 두 방법의 tolerance를 같은 값으로 서술하면 안 된다. SSPRK 중간 START 로그의 budget counter는 사용하지 않은 Radau budget을 표시하므로, 실제 SSPRK 비용은 완료 로그·raw endpoint의 native counter에서 읽는다.

메모리 공간 부족으로 C9 read-only shell이 두 차례 sandbox mount 준비 단계에서 exit 101을 냈다. 이는 native 수치 실패가 아니다. 검토자는 어떤 자료도 삭제하지 않았으며, 허가된 read-only 접근을 계속한 뒤 확보된 공간에서 감사 산출물을 저장했다. 이 오류를 물리 campaign의 실패·완료 수에 섞지 않았다.

C9 산출물은 `v16_work/c9_code/`에 보존되어 있다. 최종 Git publication, 다중 cloud 백업 및 NCP 실행 표시는 root의 C10 전달 단계에서 결속한다. 본 검토가 새로운 Git HEAD나 NCP 실행 완료를 대신 주장하지 않는다.

## 근거 파일

- `CONTRACT.md`: root의 유한 범위·수치·물리 계약.
- `NATIVE_PREFIX_PRESERVATION.json`: 기존 source/Cargo 52개와 직전 C10 archive의 비교.
- `FIRST_GATE_SOURCE_BINDING.json`: 첫 gate의 실제 byte/hash와 formatting 시점의 차이를 보존.
- `FINAL_SOURCE_N4_INDEPENDENT_AUDIT.json`: 최종 source N=4 원시 독립 재계산.
- `MATRIX_INDEPENDENT_RAW_AUDIT.json`: 전체 19개 실행 receipt/source payload 검증과 사건·열·전자·photon inventory 감사.
- `INDEPENDENT_REFINEMENT_SCREEN.json`: 실제 endpoint의 유한 차분, 미세 채널의 부호와 절대 크기 포함.
- `implementation/receipts/classified_focused/`: typed-FD 수정 회귀 1개와 focused native tests 6개, 실제 stdout/stderr/exit/source hashes.
- `implementation/receipts/final_source_n4/` 및 `MATRIX_RECEIPT.json`이 지시하는 18개 추가 directory: exact source archives, executable hashes, stdout, stderr, actual exits, raw results.

