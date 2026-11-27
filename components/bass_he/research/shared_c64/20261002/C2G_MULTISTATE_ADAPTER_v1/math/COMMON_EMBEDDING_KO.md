# C2g: 공통 물리 공간 사상과 유한 Galerkin 연산자

이 문서는 새로운 공통 공간 구현의 수학적 계약이다. 실제 계산으로 확인할 정확도와 아래의 유한 기저 항등식을 구분한다. 분자 고유상태의 유한 기저 오차, 상자 밖 꼬리, 연속체 간격 또는 원자 채널 상관관계는 이 항등식으로 증명되지 않는다.

## 1. 허용하는 좌표와 함수

입력은 동일한 전하 `ZA,ZB`, 길이 단위 `a_A`, 에너지 단위 `E_A`, 동일한 물리적 반경 `rmax`를 쓰는 O 중심 구면 부분파 hp-FEM 상태다. O는 전하 중심이고 핵의 위치는 `z_A=-ZB R/(ZA+ZB)`, `z_B=ZA R/(ZA+ZB)`이다. R가 달라도 전자 좌표의 기준 O, z축, 상자, 적분 측도는 동일하다. 서로 다른 R의 계수를 직접 내적하지 않는다.

공급자는 실수의 정적·무스핀·축대칭 Coulomb 문제에서 `m=0`과 실수 cosine `|m|=1` 대표를 반환한다. 구면 부분파는

\[
 G_{|m|}(r,\eta)=\sum_\ell u_\ell(r)A_{\ell |m|}(\eta)/r,
 \quad \int_{-1}^1 A_{\ell |m|}A_{k|m|}\,d\eta=\delta_{\ell k}.
\]

`A`에는 Condon–Shortley 위상 부호가 없다. 공통 공간의 복소수 상태는

\[
 \psi_m=G_{|m|}\frac{e^{im\phi}}{\sqrt{2\pi}},\qquad
 \psi_{-1}=\overline{\psi_{+1}}.
\]

따라서 실수 bright와 dark는 각각

\[
 \psi_b=(\psi_{+1}+\psi_{-1})/\sqrt2
       =G_1\cos\phi/\sqrt\pi,
 \quad
 \psi_d=(\psi_{+1}-\psi_{-1})/(i\sqrt2)
       =G_1\sin\phi/\sqrt\pi.
\]

에너지와 대수적 잔차는 동일한 실수 |m|=1 공급자 근에서 두 partner에 그대로 복사한다. selected뿐 아니라 guard의 모든 |m|=1 근도 ± 쌍을 만든다. 이는 정적 전자 Hamiltonian의 대칭으로부터 따르는 재구성이다. 회전 생성자, ETF 또는 시간 의존 궤적에서 두 partner가 동역학적으로 분리된다는 주장이 아니다.

현재 구현은 B 중심 또는 prolate 입력, 복소수 공급자 계수, 불일치하는 물리적 상자나 단위를 거부한다. 좌표를 무시하고 배열만 이어 붙이는 대체 경로는 없다.

## 2. 하나의 양의 물리적 적분 측도

사용할 모든 R·섹터·기저의 방사형 경계들을 합집합으로 정렬한다. 별도의 적분용 경계도 추가할 수 있다. 예를 들어 외부 층 지시함수 `r>=16`을 쓰면 `16`을 적분 경계로 추가한다. 이것은 FEM 기저를 수정하지 않는다.

각 합집합 셀에서 Gauss–Legendre 방사형 점을, η에 Gauss–Legendre 점을, φ에 `[0,2π)`의 서로 다른 균일한 점을 사용한다. 최소 차수는

\[
 n_r\ge p_{\max}+1,\qquad n_\eta\ge\ell_{\max}+1,
 \qquad n_\phi\ge2m_{\max}+1.
\]

사상 E는 함수의 격자점 값을 반환하며, 유일한 대각 가중치는

\[
 W_{abc}=r_a^2\,w_a^{(r)}w_b^{(\eta)}w_c^{(\phi)}>0.
\]

모든 r 점은 0보다 크다. 배열 순서는 `(r, eta, phi)`이고 φ가 가장 빠르다. 다른 R 사이에서도 `CommonGrid` 객체의 동일한 가중치를 사용한다. grid·metric ID는 실제 점/가중치/경계 배열과 좌표 계약을 포함하는 SHA-256으로 고정한다. 입력 경계의 변경은 복사된 읽기 전용 grid에 전파되지 않는다.

## 3. 유한 질량 내적의 정확성

같은 m에서 `r²`는 두 상태에 들어 있는 `1/r`을 상쇄한다. 합집합 셀 안에서 `u_l u_k`는 차수 `2 p_max` 이하의 다항식이므로 위의 방사형 차수는 정확하다. m=0에서 `A_l0 A_k0`는 차수 l+k 이하이다. |m|=1에서도 각 A의 `sqrt(1-eta²)`를 곱하면 다항식이 되어 차수 l+k 이하이다. 따라서 η 차수도 정확하다.

다른 m 사이의 η 곱 자체는 다항식일 필요가 없다. 먼저 φ의 균일 합이 `e^{i(m'-m)phi}`를 정확히 소거한다. `n_phi>2m_max`이므로 가능한 m 차이가 영이 아닌 순환 alias가 되는 경우가 없다. 이로써 전체 교차 섹터 내적도 정확히 0이다.

공급자 질량 조립도 `n_r>=p+1`인 보통 Gauss–Legendre 적분을 쓰므로, 부동소수점 반올림을 제외하면 공급자 FEM 계수 질량행렬 M과 공통 물리 공간 사상은

\[
 E^\dagger W E=M
\]

을 만족한다. 새 구현은 전체 공급 근 행렬 C에 대해 `(EC)^dagger W(EC)`와 저장된 실제 `C^T M C`를 비교한다. 허용오차 `gram_identity_atol`은 호출자가 명시하며, 초과하면 Snapshot을 만들지 않는다. 이 검사는 유한 질량 사상에 관한 검사이지 고유함수 수렴 검사가 아니다.

## 4. C2f에 넘기는 Hamiltonian의 정확한 의미

공급자는 실제 조립된 실수 대칭 유한 Galerkin 약형 행렬 H로부터 `C^T H C`를 계산해 보존한다. 함수값에 점별 Coulomb 미분 연산자를 새로 적용한 결과가 아니다.

M은 Dirichlet 유한 FEM 공간에서 양의 정부호이고 위의 E는 단사이다. 따라서 공통 격자에서 유한 연산자를

\[
 H_{\rm emb}=E M^{-1} H M^{-1}E^\dagger W
\]

로 정의할 수 있다. 이는 `range(E)` 위에서 Galerkin 연산자와 같고 W-직교 여공간에서 0으로 확장한 연산자다. `W H_emb`는 Hermitian이며

\[
 (EC)^\dagger W H_{\rm emb}(EC)=C^\dagger H C
\]

가 성립한다. 각 m 섹터와 ± partner에 같은 유한 H 블록을 배치하고 selected 열을 취한 실제 행렬을 C2f `Snapshot.selected_projected_operator`로 넘긴다. 따라서 nominal `diag(E)` 모델로 대체하지 않으며, 작은 비대각 원소도 보존한다. C2f의 Gram whitening과 polar 정렬은 이 실제 유한 행렬에 합동변환을 적용한다.

여기서 정의한 여공간의 0 확장은 실제 전자 Hamiltonian의 연속체가 아니다. `finite_sector_subset`, `pointwise_PDE_H_apply=false`, `PDE_residual_certified=false`, `continuum_certificate=false`를 유지한다. 에너지 원점은 전자가 무한대에 있을 때의 전자 Coulomb 에너지 0이며 핵간 반발은 빠져 있다. 이 물리적 에너지 관례는 기저나 R가 바뀌어도 동일하고, 유한 Galerkin이라는 계산 범위는 별도 provenance로 기록한다.

## 5. 상태 선택과 출처

기본 selected는 m=0의 정렬된 0기반 ordinal `1,2,3`과 |m|=1의 ordinal `0`이다. 나머지 공급 근은 guard다. m=0에서 6개, |m|=1에서 3개를 공급하면 총 12열, selected 5열, guard 7열이 된다. m=0 ordinal 0은 ground 표시를 가진다. 이 선택은 유한 R에서 명시한 후보일 뿐 큰 R의 원자 채널과 상관관계가 증명되었다는 뜻이 아니다.

실제 각 sector NPZ의 byte 수와 SHA-256, source ID, 원래 ordinal ID를 JSON binding 파일에 기록한다. binding 파일도 실제 생성한 byte들의 SHA-256을 갖는다. C2f source digest는 이 binding 파일의 digest다. 만들 때와 사용할 때 모두 sector 파일을 정확한 digest로 다시 읽고, 전달받은 메모리상의 스칼라·메타데이터·계수·행렬을 그 파일 내용과 비교한다. 같은 norm을 가진 두 계수열을 메모리에서 교체하는 경우도 거부한다. 다른 파일을 그 출처처럼 표시하지 않는다.

`write_source_binding`은 같은 디렉터리 임시 파일을 fsync한 후 create-only hardlink로 원자적으로 공개하고 디렉터리를 fsync한다. 기존 결과를 덮어쓰지 않는다. selected/guard의 모든 source ID와 ± 재구성 여부를 별도 provenance에 남긴다.

## 6. API와 자원 사용

```python
grid = build_common_grid(
    all_states_across_R,
    radial_order=7, eta_order=32, phi_count=5,
    extra_radial_knots=(16.0,), max_points=2_000_000,
)
write_source_binding((archive0, archive1), binding_path, source_id="R4/base")
result = snapshot_from_archives(
    (archive0, archive1), grid,
    source_binding_path=binding_path, gram_identity_atol=1e-11,
)
snapshot = result.snapshot
```

상태별 계산은 `u_l(r)`와 `A_lm(eta)`를 분리해서 행렬곱으로 meridional 값을 구한 뒤 Fourier 위상을 붙인다. `l × 전체 3D 격자` 중간 배열은 만들지 않는다. 필요한 최종 `N × nstate` 프레임과 Snapshot의 방어적 복사는 존재하며, `grid.allocation_estimate(nstate)`는 이 배열 크기를 명시한다. 이 추정치는 측정된 RSS나 엄밀한 프로세스 메모리 상한이 아니므로 실행기의 별도 자원 감시가 필요하다.

## 7. 새 제조해 검증

`tests/test_common_embedding.py`는 분자 eigensolve 없이 `u=sqrt(30) r(1-r)`, 반경 1의 제조해를 사용한다. 서로 다른 비중첩 방사형 mesh와 정규화 angular basis에서 norm, 모든 m 교차 Gram, ± conjugacy, bright/dark 정규화, 동일 물리 함수의 cross-R 내적을 검증한다. 독립적으로 알려진 `<r²>=2/7`과 `P(r>=1/2)=1/2`도 확인한다.

거부 검사에는 미지원 원점/단위, 부족한 적분 차수/Fourier alias, 점 수 예산, 틀린 경계값, 복소수 공급 계수, 미등록 mesh, 상이한 R의 단일 Snapshot, 질량 형식 불일치, 바뀐 파일 byte, 조작된 binding, 읽은 뒤 바뀐 메타데이터와 같은 norm 계수 교체가 포함된다. 이 새 17개 검사는 모두 통과했다. 이는 구현 범위의 증거이고 물리적 고유상태 오차의 정량 인증은 아니다.
