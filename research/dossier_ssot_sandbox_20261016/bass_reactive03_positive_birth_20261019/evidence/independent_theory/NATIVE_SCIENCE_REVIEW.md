# BASS-REACTIVE-03 native matrix 독립 과학심사

## 판정

**이 bounded control study의 native 부분은 12개 이력, 496개 accepted macrostep을 완료했다. 상수-opacity 출생 적분의 개선은 별도 exact oracle에서 인정할 수 있고, 진화하는 H/He/D native 이력에서도 광자수의 시간 격자 민감도가 크게 줄었다. 그러나 긴 구간 해 전체의 수렴은 아직 인정할 수 없다.**

특히 고정 birth refinement `r=2`에서 시간 격자를 세분하면 최종 광자수 차분은 감소하지만, 생존 광자의 평균 연령과 에너지 가중 방향 사중극 `q2`의 차분은 마지막 세 비교에서 커진다. 광자수의 안정화만으로 출생 연령 분포나 방향·에너지의 정확도를 승인하면 안 된다. 현재 연구 상태는 `PASS_SCOPED_EVIDENCE_REVIEW`이며, `LONGSPAN_SOLUTION = NOT_ADMITTED_PENDING_JOINT_TIME_BIRTH_AGE_SPECTRAL_CONVERGENCE`를 권고한다.

이 문서는 integration 담당자와 별도로, 완료된 최종 CSV와 JSON을 읽어 계산한 심사다. native 코드를 수정하거나 H/He/D 방정식을 다시 적분하지 않았다. 분석 재현 코드는 `review_native_science.py`, 전체 수치·입력 SHA-256·판정은 `NATIVE_SCIENCE_REVIEW.json`에 있다.

## 1. 자료 identity와 검사의 범위

입력은 stage의 `evidence/native` 디렉터리에 있는, 명시적으로 열거한 13개 최종 사례다. 각 JSON의 CSV SHA-256과 실제 파일을 대조하고, 완료된 사례의 `final` 객체가 CSV 마지막 행과 동일한지 검사했다. 모든 입력의 hash는 심사 전후 동일했다. 12개 성공 사례는 `exit_code=0`, 예정 행 수와 실제 행 수가 일치하며, 동일 실행 binary SHA-256을 기록한다.

```
57d2056db8d0ebafa40274bd4e254422ac24dcad4aedd4a635863b34604c8003
```

별도로 남은 `ap_n32_r2_plus.running.csv` 31행과 `off_gl4_n32.running.csv` 29행은 중간 스트림이다. 분석은 완료 JSON이 식별하는 최종 CSV만 사용했다. 이 두 파일을 새 이력이나 실패 사례로 중복 계산하지 않았다.

496개 행에 대해 54개 열의 스키마, 수치의 유한성, 양의 온도·체적, 내보낸 population·흡수 사건수·광원·reservoir의 비음수성, 누적 사건수와 광원의 단조성, 시간 표본, 연령 moment의 물리적 지지 구간을 검사했다. 평균 연령은 현재 시각까지의 경과시간 이내이고, 연령 분산은 비음수이며, 두 번째 moment는 지지 구간에 따른 상한을 만족한다. **CSV가 population으로 직접 내보내는 것은 DII다.** 나머지 종의 population positivity는 이 자료심사만으로 확장해서 주장하지 않으며, source-native solver의 수용 검사와 별도 Rust tests가 근거가 되어야 한다.

## 2. 관측량과 비교 방식

생존 광자수 $N$는 `photons_com3`이며 reference-comoving $\mathrm{m}^{-3}$ 단위다. 생존 광자의 두 연령 moment는

$$
\langle A\rangle =\frac{\texttt{survivor\_age\_com\_s}}{N},\qquad
\langle A^2\rangle =\frac{\texttt{survivor\_age2\_com\_s2}}{N}.
$$

`q2`는 원본 `bound_adaptive::photon_projection`에서 정의하는 무차원 **에너지 가중** 방향 사중극이다.

$$
q_2=\frac{\sum_c n_c E_c P_2(\mu_c)}{\sum_c n_c E_c},\qquad
P_2(\mu)=\frac{3\mu^2-1}{2}.
$$

표의 차분은 항상 fine−coarse다. 연속된 두 차분으로

$$
p_{\mathrm{mag}}=\log_2\left|\frac{v_2-v_1}{v_3-v_2}\right|
$$

를 계산하되, 이를 자동으로 정확도 차수라고 부르지 않는다. 차분 부호가 바뀌거나, 차분이 커지거나, 다른 축의 미해결 오차가 지배할 가능성이 있으면 제한된 비교 진단이다. 마지막 상대 차분도 실제 해에 대한 절대오차 상한이 아니다. $N_t$를 바꾸면 같은 `r`에서도 물리적 timestep과 광학 깊이, 패널 배치가 변하므로 이 시간 계열은 **전체 수치 경로의 Cauchy 비교**다.

## 3. 시간 해상도: 광자수는 수축하지만 연령·사중극은 미해결

모든 행은 `SIGNED_MINUS`, $T=8\times10^{12}\,\mathrm s$, birth `r=2`, 원 분광 cell mean, opacity control 4다.

| $N_t$ | $N\,[\mathrm{m}^{-3}]$ | $\langle A\rangle\,[\mathrm s]$ | $\langle A^2\rangle\,[\mathrm s^2]$ | DI 누적 사건수 | $q_2$ |
|---:|---:|---:|---:|---:|---:|
| 16 | 1.0038697846883761e−8 | 1.5123106235390816e10 | 5.598180233829896e20 | 8.763249142739327e−8 | 5.208124924104136e−8 |
| 32 | 1.0038242638797143e−8 | 1.5122165639656288e10 | 5.596737816786629e20 | 8.779035465538296e−8 | 5.207515457914419e−8 |
| 64 | 1.0038015923032241e−8 | 1.5119722975786469e10 | 5.593167017634457e20 | 8.789050462324150e−8 | 5.205776539616352e−8 |
| 128 | 1.0037907507400008e−8 | 1.5115483428885544e10 | 5.590781151864374e20 | 8.791535500718573e−8 | 5.203936302226649e−8 |

광자수 차분은 −4.55208e−13, −2.26716e−13, −1.08416e−13으로 감소한다. 크기 비의 형식적 $p_{\mathrm{mag}}$는 1.00564, 1.06431이다. 마지막 상대 차분은 −1.08006e−5, 즉 −0.00108006%다. 현재 관측은 광자수의 수축하는 시간 비교를 지지한다. 전체 2차 정확도나 이 값을 절대오차로 해석하는 주장은 지지하지 않는다.

평균 연령 차분은 −9.40596e5, −2.44266e6, −4.23955e6 s다. 마지막 상대 차분은 −0.0280477%로 작아 보이지만 차분의 크기는 커진다. $q_2$도 −6.09466e−12, −1.73892e−11, −1.84024e−11로 커지며 마지막 상대 차분은 −0.0353624%다. 두 번째 연령 moment의 차분은 감소와 증가가 섞여 안정된 차수를 보여주지 않는다. 따라서 이 세 관측량의 시간 수렴은 승인하지 않는다.

DI 시간 차분은 모두 양수이며 1.57863e−10, 1.00150e−10, 2.48504e−11이다. 두 연속 triple의 크기 비는 0.65651과 2.01082로 일치하지 않는다. 마지막 triple만 거의 2라고 해서 보편적 2차 차수를 승인할 수 없다. 마지막 DI 상대 차분은 +0.0282663%다. 온도와 DII density는 이 계열에서 더 빠른 차분 감소를 보이지만, 그 사실도 복사·연령·DI 전체 해로 확장하지 않는다.

## 4. Birth refinement: moment와 방향 정보의 개선을 직접 관찰

다음은 $N_t=32$를 고정하고 `r`만 바꾼 사례다.

| `r` | $N\,[\mathrm{m}^{-3}]$ | $\langle A\rangle\,[\mathrm s]$ | $\langle A^2\rangle\,[\mathrm s^2]$ | $q_2$ |
|---:|---:|---:|---:|---:|
| 1 | 1.0038244108519383e−8 | 1.5201222605059484e10 | 5.628021855826455e20 | 5.235705182072076e−8 |
| 2 | 1.0038242638797143e−8 | 1.5122165639656288e10 | 5.596737816786629e20 | 5.207515457914419e−8 |
| 4 | 1.0038242458076519e−8 | 1.5111739160954440e10 | 5.591933565667055e20 | 5.203561603524275e−8 |
| 8 | 1.0038242441009158e−8 | 1.5110734429370440e10 | 5.591451432184956e20 | 5.203173299603554e−8 |

`r=4→8`의 상대 차분은 광자수 −1.70023e−9, 평균 연령 −6.64912e−5, 두 번째 moment −8.62269e−5, $q_2$ −7.46283e−5다. 광자수는 거의 동일해도 연령과 방향 moment가 별도로 변한다. 이는 출생 분포를 photon number 하나만으로 대체해서는 안 된다는 요구를 native 계산에서도 뒷받침한다.

이 네 관측량은 `r=1,2,4,8`에서 모두 감소하는 차분을 보인다. 크기 비는 광자수 3.02371/3.40445, 평균 연령 2.92264/3.37537, 두 번째 moment 2.70304/3.31681, $q_2$ 2.83384/3.34800이다. 이를 현재 endpoint의 birth refinement 수축으로 인정한다. 전체 분포의 exactness, 보편적인 3차 또는 4차, 장시간 전역오차 상한까지 주장하지 않는다.

DI birth 차분은 +1.09740e−17, +2.14101e−19, −3.88841e−20이다. 마지막에 부호가 바뀌며 상대 크기는 4.42920e−13이다. 이 매우 작은 차분의 원인이 floating accumulation인지 다른 상쇄인지는 여기서 분리하지 못했다. 기록할 수 있는 것은 단일 부호의 선도오차가 지배하는 Richardson regime과 일치하지 않는다는 사실이다. 절댓값으로 계산한 5.67965와 2.46104를 DI 수렴 차수로 발표하지 않는다.

## 5. 분광·opacity·부호 전단의 독립 비교

모두 baseline $N_t=32,r=2$에 대한 상대 변화다.

| 변형 | $N$ | 평균 연령 | 두 번째 연령 moment | DI | $q_2$ |
|---|---:|---:|---:|---:|---:|
| opacity control 4→8 | −3.09835e−13 | +1.28400e−13 | +7.17569e−13 | −3.57831e−8 | −4.53173e−8 |
| OriginalCellMean→SplitPositiveGauss3 | +0.0290177% | +0.119239% | +0.332749% | −0.0309449% | +0.160905% |

Opacity control pair에서는 endpoint 광자수·연령 변화가 매우 작다. 그러나 geometry-work의 독립 적분 defect는 이 축에서 분명히 변한다. 따라서 photon number만으로 opacity/work 적분의 모든 오차가 소멸했다고 말하지 않는다. 한 분광 대비는 광자수보다 연령 moment와 방향 사중극에 더 큰 영향을 보인다. 세 단계 이상의 분광 계열이 없으므로 분광 수렴 차수나 한계값은 아직 없다.

`threshold_crossings`는 driver가 **각 macrostep**의 진단을 출력하는 열이다. 분광 분할 사례의 마지막 값과 한 단계 최대는 480이며, 32개 행의 합은 13,988이다. baseline은 전 단계 0이다. 이를 총 480회로 보고하면 틀린다. 이 진단은 transport의 표본 경로 crossing 수이며 unique physical photon 개수로 해석하지 않는다.

`SIGNED_PLUS`의 최종 $q_2=-5.207651375759672\times10^{-8}$이며 `SIGNED_MINUS`는 $+5.207515457914419\times10^{-8}$다. 두 값의 짝수 성분은 −6.79589e−13, 반대 부호 성분의 크기는 5.20758e−8로, 짝수/반대 부호 성분의 비는 1.30500e−5다. 광자수와 scalar age moment는 두 사례에서 대략 1e−14 이하의 상대 수준으로 일치한다. 이 한 쌍은 실제 donor ±shear 광선이 반대 방향 사중극을 회복하는 제한적 검증이다. 비선형 문제의 정확한 odd symmetry, shear amplitude 전체 또는 angular-grid 수렴으로 확장하지 않는다.

## 6. 기존 GL 경로와의 비교를 어디까지 해석하는가

$N_t=32$의 opt-in OFF GL2, GL4, fitted `r=2`는 각각

$$
2.559394778750123\times10^{-9},\quad
8.403585747093016\times10^{-9},\quad
1.0038242638797143\times10^{-8}
$$

의 최종 생존 광자수를 준다. OFF GL2와 GL4는 fitted 값보다 각각 74.5036%, 16.2843% 작다. 이 수치는 **진화하는 native 계산 사이의 대비**다. fitted 결과가 이 native 문제의 exact solution이라는 의미가 아니다.

별도 `RESTORED_SOURCE_FROZEN_COMPARISON.json`에서는 실제 원 source 384 cohorts를 사용하되 gas와 opacity를 동결한 해석 참조를 비교했다. 그 문제에서 $N_{\mathrm{exact}}=1.0011168643620167\times10^{-8}$이며 fitted 16개 $N_t\times r$ 조합은 binary64로 인쇄된 참조와 일치했다. 같은 동결 문제의 $N_t=32$ GL2/GL4 편향은 −74.50568%/−16.28241%다. 따라서 **원 source의 동결-opacity birth-integral 편향 개선**은 인정한다. 동결 문제와 진화 문제의 차이를 native 절대오차로 계산하지 않는다.

## 7. 보존과 geometry-work: 서로 다른 진단

Rust가 출력한 작은 잔차를 그대로 인용하는 데 그치지 않고, CSV의 개별 열을 80-digit Decimal로 합산해 다음을 독립 재구성했다.

$$
N+N_{\rm absorbed}-N_{\rm source},
$$

$$
E_{\gamma}+E_{\rm thermal}+E_{\rm binding}
+E_{\rm escaped}+E_{\rm CMB}
-E_{\rm initial}-E_{\rm source}-W_{\rm geometry}.
$$

496개 행의 최대 상대 잔차는 photon number 9.70008e−15, 전체 에너지 9.76659e−16이다. species 흡수 사건의 합과 전체 흡수수의 차이를 source count로 정규화한 최대 잔차는 5.05677e−16이다. 전체 에너지 잔차를 작은 source energy로 정규화하면 최대 2.18564e−10이다. 분모가 다르므로 전체 에너지 스케일의 잔차와 구분해야 한다.

별도로 `maxW`는 ledger로 얻은 photon geometry work와 독립 적분 work의 차이를 source energy로 정규화한, 현재까지 최대값이다. 시간 계열에서

| $N_t$ | `maxW` |
|---:|---:|
| 16 | 2.43572046e−6 |
| 32 | 8.61189715e−7 |
| 64 | 2.58811458e−7 |
| 128 | 6.75274333e−8 |

로 감소한다. $N_t=32$에서 opacity 4→8이면 8.61190e−7→2.60796e−7이다. 보존 장부는 매우 잘 닫히지만 독립 work 적분 defect는 유한하고 해상도에 의존한다. 작은 장부 잔차를 시간·연령·분광 정확도의 대용으로 사용하지 않는다.

## 8. 정확한 실패 분류

`ap_cx_worklimit`은 내부 CX 상대 허용오차 1e−14, 절대 허용오차 1e−16에서 첫 단계 시작 시각 0에 종료했다.

```
FAILED_AT step=1 t=0 Cx(WorkLimit)
```

`exit_code=2`, accepted 결과 행은 0개다. 판정은 `RESOURCE_LIMIT_CX / NUMERICAL_WORK_BUDGET_EXHAUSTED_NOT_PHYSICAL_NO_SOLUTION`이다. 이를 수렴 실패, 물리적 해 부재, 음수 population 발생, birth 방법의 실패로 바꾸지 않는다. 동시에 이 사례를 성공한 12개 이력에 포함하거나 더 엄격한 CX 허용오차에서 동일 해를 검증했다고 주장하지 않는다.

## 9. 다음 DAG에 대한 권고

현재 bounded unit은 상수 문제의 AP 출생 적분, 양의 다중 cohort 표현, native 통합과 제한된 민감도 개선이라는 범위에서 종료할 수 있다. 다음 과학 노드는 **birth-age/time 상호작용을 분리하는 작은 교차 계열**이어야 한다. 더 세밀한 고정 `r`에서 최소 세 시간 격자를 비교하고, 한 개 이상의 교차 `r` 비교를 추가하여 평균 연령·두 번째 moment·$q_2$의 차분이 실제로 수축하는지 검사하는 것이 직접적인 다음 단계다.

추가로 실제 cohort 또는 보존된 spectral/angular group별 age 분포 진단을 사용해야 한다. 낮은 차수의 몇 moment가 가까운 것만으로 분포 수렴을 인정할 수 없다. threshold를 포함한 분광 분할은 독립된 세 단계 이상의 검증이 필요하다. 현재 angular grid는 하나이고 geometry는 one-way BASS donor이므로 `BI-SIGNED`, `FLRW-CONV`, `SA-01/02`, `FULL_EOR`를 이 native matrix만으로 해제할 근거는 없다. H/He/D의 보편적 2차 정확도와 양방향 Einstein feedback도 미입증/미구현 상태로 유지한다.

## 재현

복원한 stage를 첫 번째 인자로 지정한다. 프로그램은 입력을 읽기만 하고 결과 JSON 하나를 지정한 출력 경로에 쓴다.

```bash
python3 review_native_science.py /path/to/restored/stage/evidence/native NATIVE_SCIENCE_REVIEW.json
```

기대 summary는 `PASS_SCOPED_EVIDENCE_REVIEW`, completed 12, accepted macrosteps 496, resource limit cases 1이다. 이 재현은 자료 검산이며 full Rust tests, strict Clippy, restore 실행 및 원격 backup 검증을 대체하지 않는다.
