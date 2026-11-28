# C2c 직접 연산자 및 dark 진단의 스트리밍 적분

## 범위와 불변 조건

`code/direct_stream.py`는 보존된 `prolate_fast.py`의 직접 연산자와 dark
선택규칙 진단을 배치 단위로 적분한다. Hamiltonian, 고유상태, 경계조건,
좌표계, 적분차수, 셀 분할, 관측량 정의는 바꾸지 않는다. 이 구현 작업에는
고유값 계산과 물리적 frozen-state 평가가 포함되지 않는다.

기존 두 상태의 radial/angular knot edge 합집합을 사용한다. 셀 순서는
radial 바깥 루프, angular 안쪽 루프이며, 각 셀의 `meshgrid(indexing='ij')`
및 C-order `ravel()`을 그대로 유지한다. Gauss 노드·가중치 생성과
`xl + hx*T`, `yl + hy*U`, `hx*hy*W` 연산도 기존 표현 그대로다.
모든 배치를 연결하면 원 구현의 전체 노드·가중치·patch count 배열과
각각 byte 수준의 배열 동일성을 갖는다. 이 점은 제조 시험에서 검증한다.

## 직접 적분

기존 표기에서 $c=R/2$, $M=(Z_A-Z_B)R/[2(Z_A+Z_B)]$,
$\rho=c\sqrt{(\xi^2-1)(1-\eta^2)}$, $z=c\xi\eta+M$이며,
$d\mu=R^3(\xi^2-\eta^2)d\xi d\eta/8$다.
기존 Jacobian 역변환으로 $A_\rho,A_z$를 구하고 다음 여섯 적분을 계산한다.

\[
\begin{split}
\bar L_O &= \int\frac{G}{\sqrt2}
 [z(A_\rho+A/\rho)-\rho A_z]d\mu,\\
\bar L_B &= \int\frac{G}{\sqrt2}
 [(c\xi\eta-c)(A_\rho+A/\rho)-\rho A_z]d\mu,\\
\bar p_x &= \int\frac{G}{\sqrt2}(A_\rho+A/\rho)d\mu,\\
d_x &= \int\frac{G}{\sqrt2}\rho A\,d\mu,\qquad
N_g=\int G^2d\mu,\quad N_b=\int A^2d\mu .
\end{split}
\]

직접 native 경로는 수정하지 않은 `bass_direct` ABI 1을 배치마다 호출한다.
Fortran 내부의 셀별 고정 합산 및 SIMD/OpenMP 실행 방식을 그대로 사용한다.
Python 경로는 기존 `_direct_terms`와 `_python_sum`을 호출한다. 명시적인
native 요청이 실패하면 예외를 내며 Python으로 자동 전환하지 않는다.

각 상태의 scalar B-spline evaluator는 함수 호출 시 한 번 구성한다. 각
배치에서 반복된 좌표의 unique값만 평가한 뒤 gather하는 기존 알고리즘을
재사용한다. 고밀도 2차원 basis 행렬을 만들지 않는다.

## Dark 진단

dark 상태에 대한 meridional 적분은 기존의
\[
I_d=\int G[z(A_\rho-A/\rho)-\rho A_z]d\mu
\]
이고, 실제 반환값은 수치 periodic quadrature로 계산한
\[
a_d=\frac{2\pi/N_\phi}{\sqrt2\pi}
\sum_{j=0}^{N_\phi-1}\sin(2\pi j/N_\phi)\cos(2\pi j/N_\phi)
\]
와의 곱이다. zero를 hard-code하지 않는다. 기존 bright/dark phi norm
factor도 그대로 반환한다. 이 진단은 원 구현처럼 **NumPy** 연산이다.
`backend='native'`는 native identity를 확인하지만 dark 연산의 Fortran
가속을 의미하지 않는다. 실제 backend를 metadata에 따로 기록한다.

## 저장량과 산술 순서

기본 배치는 32개 셀이며 1–64만 허용한다. 셀당 $q^2$점이므로 순간
quadrature 점 수의 상한은 $\min(P,B)q^2$이고, 전체 $Pq^2$점의 배열을
먼저 만들지 않는다. 예를 들어 $q=32,B=32$일 때 배치당 32,768점이다.
NumPy 임시 배열의 개수는 전체 셀 수에 무관하므로 주요 점 배열 저장량은
$O(Bq^2)$다. 작은 배치 합 목록의 저장량은 $O(P/B)$다. 실제 RSS 및
NCP 성능은 이 구현 시험으로 측정한 것이 아니다.

각 배치 내부는 기존 합산 방식이며, 여섯 직접 관측량과 dark meridional
적분의 배치 합은 고정 순서 `math.fsum`으로 결합한다. 전체 셀 합을 한 번에
누적하던 원 구현과 산술 결합 순서가 다르므로 결과 bitwise 동일성을
주장하지 않는다. 노드 동일성과 수치 동등성을 별도로 검증한다.

metadata의 `full_quadrature_materialized`는 작은 문제의 모든 셀이 한
배치 안에 들어가는 경우 true다. 이것은 전체 영역 크기에 비례하는
무제한 할당을 의미하지 않으며, `unbounded_domain_materialization`은
항상 false다. 실제 대형 문제에서는 전체 점 배열을 한 번에 보유하지 않는다.

## 제조 시험의 범위

`tests/test_direct_stream.py`는 고유방정식을 풀지 않은 양의 scalar
B-spline 계수 벡터를 만든다. 이들은 정규화된 물리 고유상태가 아니다.
시험은 다음을 확인한다.

- 서로 다른 knot partition을 가진 상태의 전체 tensor 노드·가중치·순서
  `array_equal` 검증.
- 56셀 제조 문제에서 batch 1, 32, 56(전체)의 직접 및 dark 적분과 기존
  전체 배열 구현 비교. 직접 적분은 Python/native 양쪽에서 확인.
- Python/native 직접 관측량의 절대차 $2\times10^{-13}$ 이하.
- 전체 quadrature materializer가 호출되지 않는다는 실행 검증.
- 잘못된 차수·배치 크기·phi 수·edge·계수·backend 및 int32 point overflow
  거부. native identity 실패 시 fallback 부재.

이 시험은 저장 방식 변경의 implementation verification이다. 작은 $R$의
상태 정확도, scaled coupling 수렴, 물리적 branch 식별 또는 C2 완료를
판정하는 증거로 사용하지 않는다.
