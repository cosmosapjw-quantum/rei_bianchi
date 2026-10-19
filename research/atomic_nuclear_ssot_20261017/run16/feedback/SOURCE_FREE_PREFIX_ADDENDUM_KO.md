# RUN16 추가 계산: 첫 source birth 이전의 native gas 경로

## 실제 새 계산과 그 범위

앞선 point-defect 검사에서 드러난 초기 보간 편향을 확인하기 위해,
원래 초기조건에서 첫 광자 birth 직전까지만 **새 5차원 gas-only IVP 세 개**를
실행했다. 대상은

\[
0\leq z\leq z_b=0.004989333151072248
\]

이고 마지막 시점은 첫 birth의 pre-activation left limit이다. 이 구간 안에는
활성 photon이 없다. 기존 RUN13 전체 gas-photon 적분이나 M2 standard/tight
이력은 재실행하지 않았다.

다섯 변수는
`x_HII, x_DII, x_HeII, x_HeIII, U/U0`다. 원래13개 species와 thermal energy로
돌리는 affine lift가 H/D/He 총량을 보존하며, 초기점은 원래14개 gas state와
정확히 같은 배열이다. 같은 `gas_rhs_server`의 mask7을 사용하고,
prescribed BASS의 `DeltaX*V/H` 변환과 원래 thermal expansion 항
`-2*DeltaX*U`를 적용했다. 이 prefix solver는 photon/depth ODE 변수를
사용하지 않으며, 원래 full `raw_rhs`도 호출하지 않는다.

이전 [85회 point 진단](execution01/RECORDED_STATE_FEEDBACK.json)은 당시
실행 지위 그대로 유지했다. 이번 addendum은 별도의 실제 IVP 실행 증거다.

## 실행한 세 control

| 계산 | nominal rtol | effective rtol | max step | accepted steps | native RHS 호출 |
|---|---:|---:|---:|---:|---:|
| Prefix A | 3e-11 | 3e-11 / sqrt(5) | z_b/4 | 4 | 62 |
| Prefix B | 6e-12 | 6e-12 / sqrt(5) | z_b/4 | 4 | 62 |
| Prefix C | 6e-12 | 6e-12 / sqrt(5) | z_b/8 | 8 | 122 |

모두 `DOP853`와 각 좌표의 `atol=1e-15/sqrt(5)`를 사용했다.
오차 norm은 이 다섯 invariant 좌표의 component-scaled L2 기준이다.
원래 40,357차원 RUN13 solver의 tolerances와 동일한 구현이라고 주장하지 않는다.

A와 B는 max-step 제한 때문에 동일한 grid와 sampled state를 주었다. 이 사실을
보존했으며, 동일한 결과만으로 discretization check를 완료하지 않았다.
추가로 한 번만 실행한 C는 maximum step을 절반으로 줄였다. C와 B의
공통 다섯 sample에서

- HI 상대 차이 최대값: `0.0` in evaluated float64 values.
- 온도 절대 차이 최대값: `3.637978807091713e-12 K`.
- 다섯 좌표의 절대 차이 최대값: `2.220446049250313e-16`.

이 비교는 관측된 finite-precision numerical agreement다. 정확해와의 rigorous
error enclosure 또는 전 구간 supremum bound가 아니다. 이 구체적인 step-size
확인을 마친 뒤 추가 native 계산은 실행하지 않았다.

## PCHIP와 실제 gas-only prefix의 차이

아래 값은 step을 절반으로 줄인 C와, 원래 tight의 초기점+12개 gas checkpoint로
정의한 componentwise PCHIP를 비교한다. 차이의 부호는 **PCHIP minus native**다.

| prefix 진행 비율 | z | HI 상대 차이 | 온도 차이 [K] |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1/4 | 0.001247333287768062 | -3.927848994944583e-7 | +0.01117420883019804 |
| 1/2 | 0.002494666575536124 | -7.855926941191527e-7 | +0.02234937007597182 |
| 3/4 | 0.003741999863304186 | -1.178423566949860e-6 | +0.03352548274961009 |
| 1 | 0.004989333151072248 | -1.571277695178175e-6 | +0.04470254583975475 |

첫 birth 직전의 실제 새 native gas-only 값은

\[
g_{\rm HI}=0.9000000534472483,
\qquad T=9999.925747777985\,\mathrm K.
\]

같은 시점의 보존-knot PCHIP는

\[
g_{\rm HI}^{\rm PCHIP}=0.8999986392972387,
\qquad T^{\rm PCHIP}=9999.970450323824\,\mathrm K.
\]

여기서 `g_HI`는 원래 `V*n_HI/n_H,0` 정규화다. HI 차이 `-1.5712777e-6`은
백분율이 아닌 무차원 상대 차이이며 약-1.571ppm이다. 온도 차이는 약0.0447K다.
이 짧은 초기 구간에서도 knot-PCHIP가 native gas trajectory와 같지 않음을
실제 계산으로 확인했다.

## 무엇을 결론 내릴 수 있는가

`NUMERICALLY_CHECKED`: 첫 source birth에서 사용할 gas 상태에 대해 위의
PCHIP 편향을 수치적으로 확인했다. Original source·input·evidence112개가
실행 전후 동일했으며, 원래 초기 gas 배열과 native executable도 그대로다.

`UNRESOLVED`: 이후 source가 작동하는 구간의 gas tube와 전체 survivor 오차.
이 prefix에는 photon이 없으므로 이 구간의 gas 편향 자체를 endpoint survivor의
직접 오차 기여라고 계산해서는 안 된다. 이 계산은 첫 birth 시점의 gas reference
오차를 알려 주며, 이후의 residual/feedback 분석으로 연결해야 한다.

이 5차원 결과는 full RUN13 transport restart checkpoint도 아니다. Native의
별도 escaped energy, CMB 및 event-ledger 좌표를 이 prefix IVP에서 적분하지
않았으므로, 그 ledger 상태까지 복원했다고 주장하지 않는다. Original full
histories와 각 ledger를 대체하지 않는다.

## 실제 호출 수와 재현 파일

이번 prefix 세 계산의 native RHS는 총246회다. 앞선 point 진단85회를 합치면
이번 feedback 작업의 총 native RHS 호출은331회다. Full native transport IVP,
기존 M2 이력 재실행 및 기존 전체 테스트 재실행은 모두0회다.

- [첫 두 prefix 계산 코드](source_free_prefix.py)
- [첫 두 계산 결과와 원래 accepted grid](prefix_execution01/SOURCE_FREE_PREFIX.json)
- [한 번의 step-halving 코드](prefix_step_halving.py)
- [새 grid와 실제 step-size 비교](prefix_stephalf_execution01/PREFIX_STEP_HALVING.json)
- [실행 영수증과 aggregate counts](PREFIX_EXECUTION_RECEIPT.json)

두 실행의 exact argv, Python/NumPy/SciPy 버전, 코드 SHA 및 실제 native 입력·응답
값은 각 JSON과 trace에 들어 있다. 실행에는 명시적인 `--source-root`,
`--gas-binary`, `--point-result`와 새 output directory를 사용한다. Step-halving
계산은 추가로 `--prefix-result`를 받아 그 이전 결과의 hash를 검증한다.

실제로 계산을 반복하지 않고 기록을 검사할 때는 위 JSON과 manifest를 읽으면
된다. `RESUME_FEEDBACK.md`가 이 feedback 하위 작업의 최신 완료 상태다.
