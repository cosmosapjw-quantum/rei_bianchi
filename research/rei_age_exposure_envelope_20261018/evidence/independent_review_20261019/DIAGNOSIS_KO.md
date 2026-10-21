# AXBI_COVARIANT_MOMENT_FIT 독립 진단

## 범위와 근거

이 문서는 native `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`의 실제 셀 적분 알고리즘을 읽고 수행한 유도와 경량 산술 검사를 기록한다. 검토자는 production 또는 NCP 캠페인을 실행하지 않았다. 합성 입력의 원본 알고리즘 재현 이후 구현 담당자가 같은 native-time 설정의 로컬 `time8` 진단을 실행해 첫 실패 셀을 확보했다. 검토자는 그 실제 셀을 독립적인 원본 Rust 함수 재생 및 정확한 저장항 재합산으로 확인했다. 현재 로컬 재현의 첫 실패는 subnormal 중량 저장 양자화로 판별됐다. 과거 NCP 오류 로그에는 셀 수치가 없어 두 실행이 동일한 셀에서 실패했다는 주장은 아직 하지 않는다.

입력 identity:

| 파일 | Git blob |
|---|---|
| axbi_covariant_transport.rs | `9915d05a00f9c2ad9e0346a1e61ba1d2f37822d3` |
| axbi_q_closure.rs | `cb987b615652d7f65e7d56acfb695e52141452b1` |

원본 `cell_quadrature`, `support_mean`, compensated `sum`, quadrature 상수와 `positive_reconstruct` 구현을 검사 파일에 그대로 추출했다. 출력 진단문만 추가했으며 수용 기준이나 계산 순서를 바꾸지 않았다. 컴파일러는 rustc 1.94.1, 실행 명령과 원자료는 `PROBE_RESULT.json`, `probe_exact_moment.rs`, `probe_stdout.csv`에 있다.

## 1. 평균 적합의 계산식

양수 quadrature base weight를 \(b_i\), 노드를 \(q_i\), 셀 광자 수와 에너지를 \(N,U\)라 둔다. \(q\)는 reference energy이며 저장 단위는 eV, \(N\)은 H 원자당 광자 수다. 선택된 bounded-exponential closure는 유지한다. 코드가 계산한 평균을 \(\widehat\mu\), 경계 간격을 \(s=\min(\widehat\mu-\ell,h-\widehat\mu)>0\)라 두면

\[
x_i=\frac{q_i-\widehat\mu}{s},\qquad
p_i(\lambda)=\frac{b_i e^{\lambda x_i}}{\sum_j b_j e^{\lambda x_j}},\qquad
F(\lambda)=\sum_i p_i(\lambda)x_i.
\]

\(x_i,\lambda,F\)는 무차원이다. 직접 미분하면

\[
\frac{d p_i}{d\lambda}=p_i(x_i-F),\qquad
F'(\lambda)=\sum_i p_i x_i^2-F^2
=\operatorname{Var}_{p(\lambda)}(x)\ge0.
\]

서로 다른 노드가 둘 이상이고 목표 평균이 노드의 최소값과 최대값 사이에 엄밀히 있으면 유한한 모든 \(\lambda\)에서 분산이 양수다. 또한 \(F(-\infty)=\min_i x_i<0\), \(F(+\infty)=\max_i x_i>0\)이므로 근은 유일하다. 목표가 노드 support 끝점에 있으면 이 유한근 논증은 적용되지 않는다. 이 구분은 물리 support 끝점 처리와 노드 support 검사를 혼동하지 않기 위해 필요하다.

정확한 산술에서 반환 중량이 \(N p_i\)이면

\[
\sum_i q_i Np_i-U=N s F+(N\widehat\mu-U).
\]

\(\widehat\mu=U/N\)인 정확한 산술의 경우 두 번째 항은 0이다. 기존 정지 조건 \(|F|<8\epsilon\), \(\epsilon=2^{-52}\)가 성립하면 첫 번째 항은

\[
|N s F|<8\epsilon Ns\le4\epsilon N(h-\ell)
\le4\epsilon\max(|U|,N(h-\ell)).
\]

따라서 수렴한 평균 적합 자체에는 기존 128\(\epsilon\) 에너지 기준까지 상당한 여유가 있다. 이 식은 80회 반복 후 미수렴한 경우나 부동소수점 평균 계산·중량 저장 오차를 이미 통제한 것으로 간주하지 않는다. 실제 진단에서는 \(F\)와 \(N\widehat\mu-U\), 최종 저장 중량의 결함을 분리해야 한다.

## 2. 정상수와 subnormal 수의 차이

최소 양수 binary64 수를 \(\eta=2^{-1074}\)라 둔다. overflow가 없는 round-to-nearest 연산에는 상대오차 외에 최대 약 \(\eta/2\)의 절대 양자화 항이 필요하다. 최종 노드 수 \(z_i=\operatorname{fl}(Np_i)\)를 따로 저장할 때, 정확히 정규화된 \(p_i\)라 해도 \(M\)개 노드의 양자화 항은 수 합에서 최대 \(M\eta/2\) 규모까지 누적될 수 있다. Kahan 합은 이미 저장된 \(z_i\)의 양자화 오차를 제거하지 않는다.

기존 코드의 허용치는

\[
\tau_N=64\epsilon N,
\qquad
\tau_U=128\epsilon S_U,
\qquad S_U=\max(|U|,N(h-\ell)).
\]

현재 연산 순서와 ties-to-even에서 \(N\le2^{-1029}\)이면 \(\operatorname{fl}(64\epsilon N)=0\)이 될 수 있으며, \(S_U\le2^{-1030}\)이면 에너지 허용치도 0이 된다. 따라서 매우 작은 셀에서는 실질적으로 정확한 저장 수·에너지 일치가 요구된다. 정규화된 평균 적합 잔차가 0인 것만으로 이 조건이 보장되지는 않는다.

`support_mean`도 \(U-\operatorname{fl}(\ell N)\) 또는 \(\operatorname{fl}(hN)-U\)를 사용하므로 subnormal 영역에서는 \(N\widehat\mu-U\)에 \(\eta\) 규모의 항이 남을 수 있다. 입력을 임의로 scale한 뒤 다른 평균 분기를 선택하면 원본의 binary64 endpoint-equality 의미가 바뀔 수 있다.

## 3. 실제 재현 결과

86개 작은 합성 셀을 검사했다. 72개는 원래 기준을 통과했고 14개는 `AXBI_COVARIANT_MOMENT_FIT`로 거부됐다. 다른 오류는 없었다. 이는 86개 캠페인 결과나 전역 정확도 시험이 아니다.

가장 단순한 재현:

\[
\ell=1,\quad h=2,\quad N=2^{-1032},\quad U=\tfrac32N,\quad r=1.
\]

| 측정량 | 실제 결과 |
|---|---:|
| \(N\) | `2.17292368994843885e-311` |
| \(U\) | `3.25938553492265828e-311` |
| \(\beta,\lambda,F\) | 모두 정확히 0 |
| count defect | `9.88131291682493088e-324` = \(2\eta\) |
| energy defect | `1.48219693752373963e-323` = \(3\eta\) |
| 두 허용치 | 모두 0 |
| 원본 결과 | `AXBI_COVARIANT_MOMENT_FIT` |

광자 threshold에 가까운 \([13.6,24.59]\) eV support에서도 작은 subnormal \(N\)에서 같은 오류가 재현됐다. 정상 크기 \(N=1\)로 평균이 양쪽 끝점에서 각각 한 ULP 떨어진 경우, support 폭이 16 ULP인 경우는 검사한 세 에너지 위치 모두 통과했다. 이 유한 대조군은 모든 경계 입력의 안정성을 증명하지는 않으며, 현재 재현 실패에 경계 조건수보다 진폭 양자화가 직접 작용했음을 보여준다.

초기 검사 생성기의 `2.0_f64.powi(-k)`가 \(k\ge1024\)에서 0을 생성하는 문제를 발견했다. 해당 출력은 `probe_v1_invalid_power_constructor/`에 보존했고 현재 검사는 `f64::from_bits`로 정확한 이진 거듭제곱을 생성한다. 이는 진단 입력 생성기의 오류이며 native 원본의 실패로 집계하지 않았다.

## 4. 실제 로컬 native-time 첫 실패 셀

구현 담당자가 frozen 원본 입력 153개와 실패 branch 전용 진단문을 사용한 로컬 `time8`을 실행했다. 실행은 6.436초에 원래 오류로 exit 1이었다. 입력 manifest는 기존 frozen manifest와 일치하며, 원본 ZIP 바이트 검증은 `ARCHIVE_UNAVAILABLE`로 구분돼 있다. 전체 실행·준비·컴파일 근거는 연구 경로의 `evidence/native_diagnostic_smoke/`에 있다.

| 측정량 | 실제 로컬 실패 셀 |
|---|---:|
| support | `[13.600425006640696, 17.06169205541766]` |
| \(N\) | `1.18696048941491e-309` |
| \(U\) | `2.02317852329999e-308` |
| mean / gap | `17.04503680907928` / `0.01665524633837734` |
| \(\beta\) / \(\lambda\) | `103.90921210217299` / `7.921527432832202e-14` |
| \(F\) / variance | `6.769278295586412e-17` / `0.9999999999998469` |
| node 개수 | 128: subnormal 저장값 87개, 양수 확률에서 0으로 저장 41개 |
| count defect / 허용치 | \(5\eta / 3\eta\): 실패 |
| energy defect / 허용치 | \(89\eta / 116\eta\): 통과 |

검토자는 출력에 보존된 binary64 입력을 `f64::from_bits`로 원본 `cell_quadrature`에 다시 전달해 같은 `MOMENT_FIT`, \(F\), 노드 수, 두 defect와 tolerance를 얻었다. 별도의 정확한 유리수 재합산에서 모든 저장 중량이 실제 `fl(N*p_i)`와 일치하며,

\[
\sum_i z_i-N
=N\Big(\sum_i p_i-1\Big)+\sum_i(z_i-Np_i)
=(-0.002575257314498469+5.002575257314499)\eta
=5\eta
\]

였다. 소수 표시는 반올림이지만 등식은 `Fraction.from_float`로 정확히 확인했다. \(|F|<8\epsilon\)이고 variance도 약 1이므로 이 셀은 Newton 평균 적합의 미수렴 때문에 거부되지 않았다. 정규화된 확률 합 오차는 허용치보다 훨씬 작지만 최종 `N*p_i`의 독립 저장 반올림이 count gate를 넘긴다. energy gate는 원래 기준으로 통과한다.

독립 근거는 `CAPTURED_NATIVE_TIME8_CELL_INDEPENDENT_CHECK.json`, `captured_native_time8_cell_replay.rs`, `captured_native_time8_cell_replay_stdout.txt`다. 입력 진단 파일 SHA256은 `42d38980214852563399e2a1dd6f0e2290d3bcb110002346f11f07a615bba5d5`다. 이것은 현재 로컬 native-time 첫 실패의 판별이며 normalized PR171 reference의 age64 ledger 실패를 설명하지 않는다. closure, 상태, 두 gate를 수정하거나 admission을 발급하지 않았다.

## 5. 교정의 수학적 제약

다음은 교정 수용 조건이며 production 소스 변경이나 admission 결정은 수행하지 않았다.

1. 기존 64\(\epsilon\) 수 gate, 128\(\epsilon\) 에너지 gate 및 bounded-exponential closure를 유지한다. 허용치에 임의 absolute floor를 더하면 기존 기준의 통과로 기록할 수 없다.
2. 정규화된 \(p_i\)에서만 gate를 검사하거나 입력 \(N,U\)를 normal 범위로 옮기는 조치만으로는 최종 저장 \(Np_i\)의 subnormal 오차를 해결하지 못한다. 원래 물리 크기의 출력 중량으로 두 gate를 다시 검사해야 한다.
3. 같은 closure의 factorized 수 표현을 downstream까지 유지하는 방법은 진폭과 확률의 조기 곱셈을 줄일 수 있다. 최종 물리량을 저장할 때의 representability 의무는 남는다.
4. 기존 노드 위에서 최소 보존 보정을 검토한다면 양성성, 동일 support, 원래 수·에너지 gate 및 보정 크기를 모두 검사해야 한다. 두 노드 \(q_a<q_b\)에 대한 정확한 산술 보정식은 \(\delta_a=(q_b\Delta N-\Delta U)/(q_b-q_a)\), \(\delta_b=(\Delta U-q_a\Delta N)/(q_b-q_a)\)다. 이 식의 존재는 binary64에서의 성공이나 임의 shape 보정의 정당화를 보장하지 않는다. 실제 보정은 frozen closure와의 오차 연결을 갖춘 별도 최소 구현 결정이 필요하다.
5. broad-support 셀을 임의 delta 또는 임의 두 노드 분포로 치환하는 근거는 현재 확보되지 않았다.

## 6. 남은 판별 범위

현재 로컬 첫 실패에 필요한 입력과 저장 노드들은 확보하고 독립 재생했다. 과거 NCP 실행의 동일 셀 여부까지 확정하려면 그 실행의 첫 실패 셀 기록이 필요하다. 정확한 binary64 값은 `to_bits` 또는 왕복 가능한 17자리 출력으로 보존해야 한다.

호출 경로도 구분했다. PR171 `positive_native.rs`의 `evaluate`와 `physical`은 `normalized_decode`로 점유 셀의 `p.number[k]=1`을 만든 뒤 `prepare`를 호출한다. 따라서 위의 작은 physical amplitude로 인한 final-node 양자화는 그 normalized-reference 호출을 직접 설명하지 않는다. `matrix_owner.rs`의 native-time 경로는 실제 `c.surviving`을 `prepare`에 전달한다. 현재 로컬 `time8` 기록은 바로 이 physical-amplitude 경로에서 subnormal 저장 양자화가 실제 실패에 작용함을 보여준다.

실패 셀을 얻은 bounded 로컬 진단은 새로운 정보를 생산했다. 이 문서는 추가 동일 NCP 캠페인을 제안하지 않는다. 현재 로컬 첫 실패에서 확인된 기작과 과거 NCP의 셀 미확인 상태를 구분한다. native-time 수렴성과 age/source/spectral 정확도는 계속 미해결이며 `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다.
