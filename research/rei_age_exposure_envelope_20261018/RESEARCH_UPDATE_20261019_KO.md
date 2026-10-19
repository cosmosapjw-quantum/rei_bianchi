# Age-exposure/source-age 정확도 연구 재개: 2026-10-19

## 현재 결론과 근거의 범위

PR199를 실제로 다시 읽은 결과, 재개 기준은 사용자가 전달한 `604c22823aed09063d27c68de5fe1c3e21b6d076`보다 10 commits 뒤인 `0c6b0466b10a47788f6415a8538e9d3e7a268163`이었다. 최신 DAG와 NCP raw receipts를 먼저 읽고 이미 완료된 spectral128 및 binary64 replay는 반복하지 않았다. 기존 다섯 진입 파일 중 일부가 여전히 83 tests/NOT_RUN을 표시하므로 이번 문서와 갱신된 CURRENT DAG가 현재 상태를 구분한다.

| 축 | 실제 확보된 결과 | 현재 판정 |
|---|---|---|
| q+0.1, age8, transport64→128 | 18/18 공통 pre/post 관측; He I 누적 photoevent 상대차 `0.0026607786820587805` = 0.2660778682% | 해당 유한 인접 비교의 0.5% 목표 충족. 연속극한/전체 정확도 보증은 아님 |
| q0, age64 reference, binary64/48 | 15007 RHS, 592.331 s, endpoint 도달, exit1. 광자 정규화 잔차 `1.0081783527976493e-8` | 고정 `1e-8` gate 실패를 보존. 새 RMS 재실행 없음 |
| age32 고정 native time8/16/32 | 기존 NCP 세 사례 모두 `AXBI_COVARIANT_MOMENT_FIT` | 기존 실패 보존. 새 목적의 로컬 time8 첫 실패 진단만 1회 수행 |
| 로컬 time8 첫 실패 셀 | frozen 153-input identity, Rust1.94.1 컴파일, 6.436 s 후 원래 exit1 | 평균 적합 이후 subnormal 노드 저장 양자화가 count gate를 넘는 원인 확인 |
| 새 reference 오차검사 | 명시적으로 선택하는 `block-max`; 기본 `rms` 유지 | 구현·해석해 실험·독립 검토 완료, 실제 age64에서는 미실행 |

`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`. 이전 age16→32 survivor 차이 90.13%와 native 시간격자 수렴성 HOLD는 이번 결과로 해제하지 않는다. PR171의 normalized reference와 native physical-amplitude 경로도 서로 구분한다.

## 1. 실제 광자 보존량과 저장된 항의 마지막 합산

birth 사이의 native 항등식은

\[
N'=-\sum_s P_s',\qquad D=N+\sum_sP_s-S_N=0
\]

이다. source birth는 N과 누적 source ledger에 같은 값을 더하므로 D의 정확한 값은 jump 전후에도 연속이다. positive reference는 cell 내부의 두 양수 slack

\[
L=U-q_{lo}N,\quad R=q_{hi}N-U,\quad
N=\frac{L+R}{q_{hi}-q_{lo}}
\]

의 로그를 적분한다. 로그 좌표와 별도의 누적 photo ledger를 RK 단계로 갱신하면, 연속 미분 항등식이 성립하더라도 비선형 함수 N(z)와 ledger의 합을 단계마다 정확히 보존하는 것은 아니다. 이것은 가능한 수치적 설명이며, 특정 잔차의 원인 귀속에는 실제 기록 분석이 필요하다.

`src/photon_ledger_diagnosis.py`는 기존 기록만 읽는다. 각 binary64 항을 `Fraction.from_float`로 정확한 유리수로 변환하여 source 개별 항, endpoint residual/gross, 각 birth 구간의 signed residual 증가, source jump의 pre/post 차이를 계산한다. Decimal80은 표시용이며 판정에 사용하지 않는다. 저장된 원래 assert `abs(residual) <= 1e-8*gross`와 ratio 형태의 비교도 분리한다.

\(\gamma_k=ku/(1-ku),\ u=2^{-53}\)에 의한 \(\gamma_k\sum|x_i|\)는 **이미 저장된 항을 마지막에 더하는 연산만**의 범위다. native RHS, log 좌표 재구성, adaptive 적분 전체에 대한 오차 인증이 아니다.

실제 age64 raw 70개 파일(5 JSON과 65개 accepted-coordinate 배열)을 pinned Git blob과 일치시켜 읽었다. 정확한 저장항 residual은 `1.470987072064934887e-12`, 정규화 잔차는 `1.008178364096903740e-8`로 여전히 실패다. 고정 gate 초과분 `1.1932678071267423e-14`는 마지막 합산 경계 `1.1015155320267547e-18`보다 크다. 원래 residual과 정확한 재합산 차이는 `1.6486226596064687e-20`이다. 따라서 마지막 덧셈만 교정해서 이 실패를 없앨 수 없다. 전체 적분/RHS 이력의 구체적 원인 귀속은 UNRESOLVED다.

65개 구간의 budget을 재구성했다. 끝의 event64, 63, 62에서 signed residual 증가가 각각 `6.6731510e-14`, `5.5372279e-14`, `5.3864840e-14`였다. 실제 source-birth 순간의 paired pre/post snapshot은 기존 관측 파일에 없어 해당 jump 검사는 MISSING으로 남긴다. 근거: `evidence/AGE64_PHOTON_LEDGER_COMPACT_20261019.json`, 전체 유리수 산술은 `evidence/AGE64_PHOTON_LEDGER_DIAGNOSIS_20261019.json`, 70개 입력 identity는 `evidence/AGE64_RAW_INPUT_HASHES_20261019.json`.

## 2. DOP853의 전체 차원 평균과 성분군별 검사

현재 설치된 SciPy1.17 DOP853 구현에서 오차 scale로 나눈 두 embedded 추정치를 e5,e3라 하고,

\[
A=\sum_i e_{5,i}^2,\qquad B=\sum_i e_{3,i}^2,\qquad
E_{rms}=|h|\frac{A}{\sqrt{n(A+0.01B)}}
\]

로 쓸 수 있다. 상태 차원 n이 커지면 다른 성분의 오차가 0인 경우에도 한 ledger의 기여가 희석된다. 동일한 RK 단계에서 완전하고 중복 없는 partition \(G_g\)에 대해

\[
A_g=\sum_{i\in G_g}e_{5,i}^2,\quad C_g=A_g+0.01B_g,\quad
E_g=|h|\frac{A_g}{\sqrt{n_g C_g}},\quad E_{block}=\max_g E_g
\]

를 사용한다. \(C_g=0\)이면 해당 값은 0이다. \(M=E_{block}\)라 두면

\[
\sum_g A_g\le\frac{M}{|h|}\sum_g\sqrt{n_gC_g}
\le\frac{M}{|h|}\sqrt{n\sum_g C_g}
\]

이므로 정확한 산술에서 \(E_{rms}\le E_{block}\)이다. h=0은 자명하다. 이 부등식은 같은 stage/scale에서 새 검사가 기존보다 느슨하지 않음을 뜻한다. 서로 다른 adaptive 경로 전체의 오차나 차원 불변성을 보증하지 않는다.

구현 partition은 gas4, 현재 활성 photon log 좌표 한 성분군, 14개의 개별 ledger scalar다. photon 성분군 내부의 평균 효과와 기존 initial-step 선택은 남아 있다. `rtol/atol`, RK 계수, dense interpolation, source schedule, 물리식과 최종 보존 gate는 바꾸지 않았다. `--error-norm rms`가 기본이고, `--error-norm block-max`만 새 모드를 사용한다. 설정·fingerprint·solver return에 모드를 기록하며, 반환 모드 불일치는 실패한다. 과거 기록의 누락된 모드는 rms로 해석한다.

### 해석해가 있는 고정 opacity 실험

\(z'=-50,\ P'=50e^z,\ e^{z(0)}=10^{-4}\), 시간 구간 [0,1]에서 \(e^z+P=10^{-4}\)가 정확하다. 동일한 first-step 0.01, rtol `2e-10`, log atol `1e-11`, ledger atol `1e-16`에서 오차가 0인 좌표만 추가했다.

| 차원 | RMS 정규화 photon residual | block-max 정규화 photon residual | RHS RMS / block-max |
|---:|---:|---:|---:|
| 2 | 7.212316139325336e-12 | 5.094733771215646e-12 | 241 / 265 |
| 144 | 4.458910183165445e-11 | 5.093852856950511e-12 | 205 / 265 |
| 1152 | 1.0938556374600845e-10 | 5.093852856950511e-12 | 181 / 265 |
| 9234 | 2.6749754476804685e-10 | 5.0939206195862904e-12 | 169 / 265 |

기존 RMS 잔차는 약 37배 증가했고 새 모드는 거의 일정했다. 이 대조 실험은 두 방법 모두 `1e-8` 안이다. 실제 Grackle nonlinear accuracy나 age64 gate 통과를 주장하지 않는다. 근거: `evidence/ERROR_CONTROL_PRESCRIBED_OPACITY_20261019.json`.

## 3. 실제 native time8 실패: 평균 적합 이후의 저장 양자화

원본 `cell_quadrature`의 exponential tilt를 \(p_i(\lambda)\propto w_i\exp[\lambda(q_i-\mu)/s]\), \(\mu=u/n\), \(s=\min(\mu-lo,hi-\mu)\)라 쓰면

\[
F(\lambda)=\sum_i p_i(\lambda)\frac{q_i-\mu}{s},\qquad
F'(\lambda)=\operatorname{Var}_{p(\lambda)}\!\left(\frac{q-\mu}{s}\right)\ge0.
\]

실제 포착된 셀은 `n=1.18696048941491e-309`, `u=2.02317852329999e-308`, lo `13.600425006640696`, hi `17.06169205541766`이다. \(|F|=6.769278295586412e-17\)로 기존 정지 기준 \(8\epsilon=1.7763568394002505e-15\)보다 작고 variance는 약 1이다. Newton 미수렴으로 설명할 근거가 없다.

\(\eta=2^{-1074}\)를 최소 양수 binary64 값으로 놓으면, 저장 결과는 다음과 같다.

| 관측량 | 실제 값 | 원래 gate |
|---|---:|---:|
| 128개의 양수 확률 중 subnormal 저장값 | 87개 | — |
| 양수 확률이 0으로 저장된 노드 | 41개 | — |
| photon count defect | \(5\eta\) | \(3\eta\): 실패 |
| energy defect | \(89\eta\) | \(116\eta\): 통과 |

저장된 노드 \(z_i=\operatorname{fl}(np_i)\)의 정확한 유리수 분해는

\[
\sum_i z_i-n
=n\left(\sum_i p_i-1\right)+\sum_i(z_i-np_i)
=(-0.0025752573+5.0025752573)\eta=5\eta
\]

이다. 표시 소수만 반올림했으며 등식 자체는 정확히 확인했다. 독립 검토자는 입력 bit pattern을 원본에서 추출한 Rust 함수에 다시 넣어 같은 오류와 수치를 재현했다.

따라서 **현재 로컬 time8 첫 실패는 정규화 이후 개별 노드의 저장 양자화 문제**다. 과거 NCP stderr에는 해당 셀 수치가 없으므로 동일 셀에서의 실패라고 단정하지 않는다. PR171 normalized reference는 prepare 입력 n을 1로 정규화하므로 이 결과를 age64의 photon ledger 실패 원인으로 대체하지 않는다.

원본 physics SHA는 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, transport blob은 `9915d05a00f9c2ad9e0346a1e61ba1d2f37822d3`이다. 정확한 GitHub 141 crate files + 12 external includes로 153-input manifest SHA `ab90ff29ec8b13b1bf6b31aa075be563d4ceab68f34b7255f107306fc750e4d3`를 재구성했다. 이는 원본 ZIP 전체 bytes의 재확인과는 구별한다.

진단은 task copy의 이미 실패가 결정된 branch에서 첫 1건만 JSON으로 출력하고 원래 `AXBI_COVARIANT_MOMENT_FIT`를 반환한다. 교정 검토가 끝나기 전 기존 time16/32 캠페인을 반복하지 않는다.

## 4. 검증 및 게시 범위

신규 targeted stdlib unittest는 photon 진단 11개, error control 9개, moment 진단 3개가 통과했다. 기존 85 PASS + 1 optional skip은 원격 이력을 재사용하며, 이 세트 전체를 이번 환경에서 다시 실행했다고 주장하지 않는다. Python3.12.14, NumPy2.3.5, SciPy1.17.0, C++17 g++13.3.0, Rust1.94.1의 현재 실제 작동을 확인했다. pytest는 이 환경에서 없었으나 새 검증은 stdlib unittest로 수행했다.

독립 검토는 `evidence/independent_review_20261019/INDEPENDENT_REVIEW.json`에 범위와 SHA를 기록한다. 모델 요청 역할은 Astra가 과학 계약·판정·독립 검토, gpt-6.1-sol이 기계적 구현이다. 요청 모델과 별개인 실행 서비스 identity를 추정하여 적지 않는다.

최신 Drive/Dropbox 목록과 새 binary64 ZIP metadata는 현재 도구로 확인했다. 샌드박스 signed URL 다운로드는 실제 네트워크 제한으로 실패했고, 연결된 Desktop Commander의 process 호출은 월간 사용량 제한을 반환했다. 이전 blocker를 상속한 판단이 아니며, 해당 경로는 재시도하지 않는다. 백업 payload readback 여부와 새 upload 결과는 delivery receipt에 별도로 기록한다.

## 참고 및 재현 위치

- 기존 NCP 결과: `evidence/ncp_20261018T132700Z/spectral128_vs_transport64.json`, `evidence/ncp_20261018T150300Z/BINARY64_AGE64_48_SUMMARY.json`.
- 새 실제 로컬 진단: `evidence/native_diagnostic_smoke/MOMENT_DIAGNOSTIC_RESULT.json` 및 보존된 stderr/RECEIPT.
- 독립 실제 셀 재생: `evidence/independent_review_20261019/CAPTURED_NATIVE_TIME8_CELL_INDEPENDENT_CHECK.json`.
- [SciPy1.17 DOP853 문서](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.DOP853.html), 설치된 `_estimate_error_norm` source SHA `e34d82cbf3e908af7a8be53174af596759c0fc06555d868588c5b86f2f746c2d`.
- [Hairer 공식 software 안내](https://www.unige.ch/~hairer/software.html).

owner checkout, PR150/R9 및 별도 BASS HHeD lane에는 변경을 적용하지 않는다. 현재 PR의 실제 parent 위에 이 연구 경로만 fast-forward로 게시한다.
