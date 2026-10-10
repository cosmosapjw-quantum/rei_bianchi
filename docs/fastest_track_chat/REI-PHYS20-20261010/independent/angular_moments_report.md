# PHYS20 독립 검산: 실제 midpoint 각도 격자의 모멘트와 birth measure

근거 상태: **derived / numerically checked**. 역할: 후보를 검산하는 독립 기여자이며 최종 decision reviewer가 아니다. 과학 admission은 `HOLD`로 유지한다. 새 native/IVP 실행, 과거 proof 재실행, 원 저장소 변경은 모두 0회다.

## 1. 고정 소스와 검산 범위

소스는 `cosmosapjw-quantum/rei_bianchi`, branch `forward/rust-reion-kernels-20260922`, commit `718468dc75cb81fdfe0f2792aab5c8d0dbc54607`에 고정했다. 실제 각도와 source weight는 [paired_runtime.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/718468dc75cb81fdfe0f2792aab5c8d0dbc54607/rust/rei_microphysics/src/paired_runtime.rs)의 `qhat`, `g_point`, `source_weights`에서 읽었다. Blob SHA는 `70eed18b07b6dd4297d8ef8da6d7e1be8e44456e`이며 검산 script는 실행 전에 이 identity를 다시 확인한다.

`qhat`은 midpoint μ와 midpoint φ를 사용한다. `source_weights`는 `exp(-sum(H_i)*t)/g^3`를 계산한 뒤 유한 각도합으로 정상화한다. 실제 비교의 `BI`는 `H_i=(1.01,0.99,1)*1e-14 s^-1`, `FLRW`는 `H_i=(1,1,1)*1e-14 s^-1`다. 이 값들은 [paired_history.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/718468dc75cb81fdfe0f2792aab5c8d0dbc54607/rust/rei_microphysics/examples/paired_history.rs)의 `h()`에서 확인했다.

이 검산은 해당 수학적 격자의 정확 모멘트와 collisionless photon mean-energy 반응을 다룬다. Absorption/heating history, coupled gas error, physical reionization history를 실행하거나 인증한 결과가 아니다. Binary 삼각함수로 생성된 실제 native rays의 byte identity도 주장하지 않는다. 소스 공식을 Python의 binary64 `math`로 재구성한 검산과, 수학적 격자를 Decimal80의 근호로 구성한 검산을 분리했다.

## 2. 정확한 2차 및 4차 모멘트

정의는

\[
\mu_j=\frac{2j+1-N}{N},\qquad
\phi_k=\frac{2\pi(k+1/2)}{M},\qquad
\hat q=(\sqrt{1-\mu^2}\cos\phi,\sqrt{1-\mu^2}\sin\phi,\mu),
\]

이고 무게는 `1/(NM)`이다. 정규화된 각도평균을 꺾쇠로 쓴다. 유한 등차수열의 제곱합과 네제곱합에서

\[
m_2=\langle\mu^2\rangle=\frac13-\frac{1}{3N^2},\qquad
m_4=\langle\mu^4\rangle=\frac15-\frac{2}{3N^2}+\frac{7}{15N^4}.
\]

이는 `Fraction`의 직접 유한합과 독립적으로 대조했다. Azimuth 합은
`sum exp(i*l*phi_k)=0` when `M` does not divide nonzero `l`이라는 roots-of-unity identity를 사용한다. 따라서 `M>=3`에서

\[
Q_{ij}=\langle q_iq_j\rangle
=\mathrm{diag}\!\left(\frac13+\frac{1}{6N^2},\frac13+\frac{1}{6N^2},\frac13-\frac{1}{3N^2}\right).
\]

`tr Q=1`이지만 `Q=I/3`은 유한 `N`에서 성립하지 않는다. 일반 대칭 tracefree 행렬 `B`에 대해서는

\[
Q:B=-\frac{B_{zz}}{2N^2}.
\]

따라서 tracefree라는 사실만으로 이 격자의 각도평균 1차항이 사라진다고 주장할 수 없다. 선택된 `D=diag(1,-1,0)`에서는 `Q:D=0`이다. 이 방향에서는 `Qxx=Qyy`가 정확히 필요 조건을 충족한다.

4차 모멘트에는 충분조건 `M>=5`를 사용한다. 이 조건은 `M=3`의 모든 경우를 배제해야 한다는 뜻은 아니며, `M=4`를 포함하는 무조건적 확장은 불가능하다. `A=1-2m2+m4=8/15+7/(15N^4)`라고 두면

\[
\begin{aligned}
\langle q_x^4\rangle=\langle q_y^4\rangle&=\frac38 A,&
\langle q_z^4\rangle&=m_4,\\
\langle q_x^2q_y^2\rangle&=\frac18 A,&
\langle q_x^2q_z^2\rangle=\langle q_y^2q_z^2\rangle&=\frac12(m_2-m_4).
\end{aligned}
\]

홀수 지수를 가진 나머지 성분은 격자의 반사·azimuth 대칭에 의해 0이다. 특히

\[
P=q_x^2-q_y^2,\quad U=q_x^2+q_y^2,
\qquad \langle U\rangle=\frac23+\frac{1}{3N^2},\quad
\langle P^2\rangle=\frac4{15}+\frac7{30N^4}.
\]

`M=4` midpoint φ에서는 모든 ray에서 `qx²=qy²`여서 `P²=0`이다. 이 반례는 해당 grid를 임의의 4차 모멘트 검산에 사용할 수 없음을 보여준다.

## 3. 선택된 shear의 2차 mean-energy 반응

Metric signature는 `(-,+,+,+)`, proper time은 초다. 다음 prescribed geometry를 사용한다.

\[
ds^2=-c^2dt^2+\sum_i e^{2(H+\sigma D_i)t}(dx^i)^2,
\quad D=\operatorname{diag}(1,-1,0),\quad [H]=[\sigma]=\mathrm{s}^{-1}.
\]

최초 시각에 isotropic한 단색 photon cohort에서 `alpha=sigma*Delta`를 정의하면 mean FLRW redshift를 나눈 방향별 energy ratio는

\[
g(\alpha)=\sqrt{q_x^2e^{-2\alpha}+q_y^2e^{2\alpha}+q_z^2}
=1-\alpha P+\alpha^2\left(U-\frac12P^2\right)+O(\alpha^3).
\]

연속 구면 평균은 `Q=I/3`, `P²=4/15`이므로

\[
\left\langle\frac{E}{E_{\rm FLRW}}\right\rangle
=1+\frac8{15}(\sigma\Delta)^2+O((\sigma\Delta)^4).
\]

일반 tracefree 적분 shear 행렬 `B`에 대한 연속 2차항은 `(4/15)tr(B²)`이며 `D`에 대하여 `tr(D²)=2`가 위 식을 준다.

실제 midpoint 격자의 수학적 2차 계수는

\[
C_N=\frac8{15}+\frac{1}{3N^2}-\frac7{60N^4}.
\]

`M`이 4의 배수이면 `phi -> phi+pi/2`가 node permutation이며 `P -> -P`다. 따라서 `sigma -> -sigma`의 exact discrete symmetry가 성립하고 홀수항은 모두 사라진다. 이는 이상적인 수학적 grid의 정확한 결과다. Binary 삼각함수와 합산에서 이 대칭은 rounding 수준의 차이를 가질 수 있다. `M>=5`만 가정한 일반 경우에는 식의 2차 계수와 exact evenness를 구분해야 한다.

| N | Qxx=Qyy | Qzz | P² | C_N | C_N/(8/15)-1 |
|---|---:|---:|---:|---:|---:|
| 4 | 11/32 | 5/16 | 137/512 | 567/1024 | 313/8192 = 3.82080078125% |
| 8 | 43/128 | 21/64 | 2185/8192 | 8823/16384 | 1273/131072 = 0.971221923828125% |
| 16 | 171/512 | 85/256 | 34953/131072 | 140151/262144 | 5113/2097152 = 0.2438068389892578125% |

이 비율들은 **shear 2차 energy-response 계수의 angular discretization bias**다. 전체 에너지나 gas temperature 자체의 상대오차와 동일하지 않다. 절대 계수 bias는 각각 `313/15360`, `1273/245760`, `5113/3932160`이다.

### 일반 방향에 대한 반례

축대칭 `Dax=diag(-1/2,-1/2,1)`에서는

\[
\left\langle E/E_{\rm FLRW}\right\rangle_N
=1+\frac{\sigma\Delta}{2N^2}+O((\sigma\Delta)^2).
\]

계수는 `N=4,8,16`에서 각각 `1/32`, `1/128`, `1/512`다. 연속 구면평균의 1차항은 0이다. 이 `Dax`는 `Dxy`의 rotation이 아니라 다른 eigenvalue spectrum이다. 같은 eigenvalues를 가진 회전 반례로 `Drot=diag(1,0,-1)`을 택해도 평균 1차항은 `-sigma*Delta/(2N²)`로 나타난다. 따라서 문제는 축대칭 모델에만 국한되지 않는다.

## 4. Birth Jacobian: 연속 결과와 유한 grid 결과의 구별

이 절의 `b`는 **출생 proper time [s]**이며 metric anisotropy parameter가 아니다. `beta=sigma*b`, `alpha=sigma*Delta`다. 고정 reference 방향 `q`에서 출생 이후 energy ratio는

\[
r(\hat q;\beta,\alpha)=\frac{g(\beta+\alpha)}{g(\beta)}
=1-\alpha P+\alpha^2\left(U-\frac12P^2\right)
+2\alpha\beta(U-P^2)+O(\sigma^3).
\]

출생 시각의 **물리적 각도**에서 isotropic한 source는 `dOmega_b=J_b dOmega_q`, `J_b=g(beta)^(-3)`로 pull back 해야 한다. 전개는

\[
J_b=1+3\beta P+\beta^2\left(-3U+\frac{15}{2}P^2\right)+O(\beta^3).
\]

연속 sphere에서는 `integral J_b dOmega_q/(4pi)=1`이고, 변수변환 `q -> n_b`에 의해

\[
\langle J_b r\rangle_q=\left\langle g(\hat n_b;\alpha)\right\rangle_{n_b}
\]

가 **정확히** 성립한다. 오른쪽은 출생시각 `b`에 의존하지 않는다. 이 independence는 constant directional rates, birth-physical isotropy 및 collisionless cohort에 대한 결과다.

반면 `q` labels에 균등하게 방출하는 잘못된 모델에서는 연속 mean energy에

\[
\langle r\rangle_q=1+\frac8{15}\alpha^2+\frac45\alpha\beta+O(\sigma^4)
\]

가 생긴다. 따라서

\[
\text{uniform-q mean}-\text{physical-isotropic mean}
=\frac45\sigma^2b\Delta+O(\sigma^4).
\]

여기서 짝수 차수 remainder는 `Dxy`의 회전 대칭을 사용한다. `b,Delta>=0`이면 잘못된 uniform-q source의 leading artifact는 양수다. 이 식은 `sigma*b`와 `sigma*(b+Delta)`가 작은 동일 Taylor 영역에서 해석한다. Correct continuum model 자체는 임의 `b`에서 정확한 변수변환으로 정의된다.

**중요한 제한:** 실제 유한 grid의 `J_b/sum J_b` 정상화는 연속 각도적분과 동일하지 않다. 2차까지

\[
\begin{aligned}
\langle r\rangle_{N,\mathrm{uniform}}
&=1+C_N\alpha^2+
\left(\frac45+\frac{2}{3N^2}-\frac7{15N^4}\right)\alpha\beta+O(\sigma^4),\\
\langle r\rangle_{N,J}
&=1+C_N\alpha^2+
\left(\frac{2}{3N^2}-\frac7{6N^4}\right)\alpha\beta+O(\sigma^4).
\end{aligned}
\]

이는 `<J>`의 정상화를 포함해 얻은 식이다. `O(beta²)`의 constant term은 numerator와 denominator에서 취소되지만 `alpha*beta`의 response covariance는 남는다. 두 모델 차이는

\[
\langle r\rangle_{N,\mathrm{uniform}}-\langle r\rangle_{N,J}
=\left(\frac45+\frac7{10N^4}\right)\alpha\beta+O(\sigma^4).
\]

| N | Correct normalized-J mean의 bΔ residual coefficient | Uniform-q minus normalized-J coefficient |
|---|---:|---:|
| 4 | 19/512 = 0.037109375 | 411/512 = 0.802734375 |
| 8 | 83/8192 = 0.0101318359375 | 6555/8192 = 0.8001708984375 |
| 16 | 339/131072 = 0.00258636474609375 | 104859/131072 = 0.80001068115234375 |
| continuum | 0 | 4/5 |

따라서 discrete Jacobian은 uniform-q source의 leading O(1) artifact를 제거하지만, 정확한 birth-time independence를 유한 midpoint grid에서 보장하지 않는다. 남은 항은 O(N^-2) 각도오차다. 이를 물리적 source memory로 해석해서는 안 된다.

## 5. 실제 검산 결과와 재현

표의 모든 분수는 표준 라이브러리 `Fraction`의 정확 계산으로 생성했다. 별도 Decimal80 검산에서는 φ32를 π 삼각함수 대신 반복 반각 근호와 rotation recurrence로 생성하고 `exp`, `sqrt`로 exact characteristic formula를 평가했다. Native code는 호출하지 않았다.

- `N=4,8,16`, `M=32`, `epsilon=1e-6`에서 energy 2차항, axial 1차항, uniform source cross term, normalized-J residual, 두 source의 차이를 독립 direct-function evaluation으로 확인했다. 최대 계수 오차는 `2.681e-13` 이하였고 고정 허용치는 `1e-9`였다. 이 차이는 유한 epsilon의 고차 Taylor 항을 포함한다.
- Selected-shear sign symmetry의 Decimal80 차이는 세 grid 모두 `0E-79`였다. 이는 위 permutation 유도를 보조하는 수치 결과이며 임의 입력이나 native rounding에 대한 보증이 아니다.
- 실제 소스 공식의 binary64 Python 재구성에서 Q 최대 절대 차이는 `5.552e-17`, P² 최대 절대 차이는 `1.666e-16` 이하였다. Rust binary와의 bitwise 대조는 하지 않았다.
- 독립 Newton–Legendre8 × φ32 angular probe에서 `epsilon=0.01,0.001,0.0001`을 사용했다. Continuum energy coefficient는 `8/15`로, uniform-minus-physical coefficient는 `4/5`로 수렴했다. 마지막 계수 차이는 각각 `2.540e-10`, `2.667e-9`였다. Correct physical-birth mean과 birth-zero mean의 차이는 마지막 probe에서 `4.377e-34`였다. 이 quadrature 진단을 certified continuum remainder bound로 표시하지 않는다.
- 최초 실행은 exit 0이었고 개발 중 실제 assertion failure는 없었다. Generic-STF cancellation, exact discrete birth invariance 및 uniform-q isotropy가 성립하지 않는다는 반례는 결과 파일에 `negative_controls`로 보존했다. 이 과학적 반례를 검산 script의 실패와 혼동하지 않는다.

재현 명령은 새 출력 디렉터리를 사용한다. 기존 evidence는 덮어쓰지 않는다.

```bash
python verify_angular_moments.py --output-dir NEW_OUTPUT_DIRECTORY \
  --pin-root /workspace/scratch/603081e41728/rei_recon_pinned/fastest_718468dc
```

`angular_moments_results.json`에 exact fractions, 전체 수치 잔차, source/script SHA256, Python version 및 제한을 기록했다. `EXECUTION.json`, `verification.stdout.log`, `verification.stderr.log`에 실제 명령·exit를 보존했다.

## 6. PHYS20에서 허용되는 결론

1. Tracefree shear의 scalar angle-average 1차 상쇄는 continuum isotropy와 유효한 각도 moment identity를 조건으로 하는 결과다. 실제 midpoint grid는 현재 x/y shear에서는 이를 보존하지만 모든 STF 방향에서 보존하지 않는다.
2. Selected x/y shear의 mean-energy leading effect는 2차이며, 실제 angular discretization은 그 2차 계수 자체에 위의 정확한 bias를 준다. 이 항과 native rounding을 구분한다.
3. Physical-angle isotropic birth를 fixed-q labels에 균등 source로 대체하면 인공적인 `sigma²*b*Delta` 의존성이 생긴다. Correct source Jacobian은 필수이고, 유한 angular quadrature의 잔여오차는 별도로 유지한다.
4. 이 에너지 계산을 absorption/heating의 전체 오류로 곧바로 변환할 수 없다. 그 후속은 threshold 미횡단·smooth cross section·동일 scalar gas background·causal opacity history 및 source measure 조건을 명시한 별도 커널 유도를 필요로 한다.

최종 승격은 이 검산에 참여하지 않은 decision reviewer의 범위 판정에 남긴다. 기존 `physicalHOLD`, `[160,161]FAIL`, `tick160`, auxiliary escape FAIL은 변경하지 않는다.
