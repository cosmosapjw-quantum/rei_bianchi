# B1 독립 이론·oracle 노트

작성 역할: `b1_physics_oracle`. 주 실행 코드 작성자 또는 최종 decision reviewer가 아니다.

범위는 homogeneous LRS Bianchi I, 처방된 전자 이력, cold/non-tilted/elastic Thomson, test radiation이다. metric은 \((-+++ )\), proper time은 s, 에너지는 일관된 한 단위를 사용한다. 아래 해석적 관계는 **derived**이며, 별도 JSON에 기록한 작은 계산만 **numerically checked**다. B1 전체 구현·결과의 채택은 별도 판단이다.

읽은 기준은 BASS_HE 개정 개발계획, REI `bianchi_i.rs`, bass `pol_collide.rs`, 복구된 reduced producer `model.py`와 `background.py`다. 이 노트의 수식은 해당 소스 규약에서 독립적으로 유도했다. 문헌의 결과로 재표기하지 않는다.

## 1. 정확 특성선과 좌표 부호

\[
ds^2=-c^2dt^2+a_\perp^2(dx^2+dy^2)+a_\parallel^2dz^2,
\quad a_\perp=a e^{-\beta},\quad a_\parallel=a e^{2\beta},\quad
H=\dot a/a,\quad s=\dot\beta .
\]

따라서 \(H_\perp=H-s\), \(H_\parallel=H+2s\), \(\sigma^2=3s^2\). 공간 Killing 벡터 때문에 공변 공간 운동량 \(k_i\)가 일정하고, 직교 tetrad에서 \(p_{\hat i}=k_i/a_i\)다. source 시각 0에서 target 시각 1로 가는 forward map은

\[
D_i={a_i(t_0)\over a_i(t_1)},\quad
R=\left(\sum_iD_i^2n_{0i}^2\right)^{1/2},\quad
E_1=R E_0,\quad n_{1i}=D_i n_{0i}/R.
\]

이는 REI `CharacteristicRay`의 에너지·방향 변화와 같은 규약이다. 그 API의 `pullback(g0,g1)`라는 이름에도 불구하고 입력 ray가 g0의 상태라면 반환은 위 g1 상태다. Eulerian backward interpolation에서는 target ray를 만들고 geometry 순서를 반대로 넣거나 다음 역식을 직접 써야 한다.

Comoving energy \(w=aE\)와 \(\mu=n_z\)를 쓰면 mean expansion을 정확히 제거할 수 있다. \(\Delta\beta=\beta_1-\beta_0\)일 때 target→source 역식은

\[
G(\mu_1)=\left[(1-\mu_1^2)e^{-2\Delta\beta}
               +\mu_1^2e^{4\Delta\beta}\right]^{1/2},
\quad w_0=w_1G,\quad
\mu_0={\mu_1e^{2\Delta\beta}\over G},\quad\phi_0=\phi_1.
\]

\(\Delta\beta=0\)이면 w와 방향 모두 항등이다. \(\Delta\beta>0\)에서는 longitudinal scale factor가 더 커지므로 고정된 target 에너지의 pole 광자는 더 높은 초기 에너지에서 왔다. 감소하는 초기 occupation의 pole intensity가 작아지는 부호다.

방향 Jacobian은

\[
{d\Omega_1\over d\Omega_0}={\det D\over R^3},
\qquad\det D=(a_0/a_1)^3.
\]

그러나 Eulerian occupation을 pullback할 때 이 Jacobian을 occupation에 곱하지 않는다. Jacobian은 적분 변수를 바꾸거나 ray-bundle quadrature weight를 수송할 때 사용한다. phase measure에서 \(E_1^2dE_1d\Omega_1=\det D\,E_0^2dE_0d\Omega_0\), 따라서 전체 에너지 범위에서 \(a^3n_\gamma\)가 보존된다. 이 성질은 유한 energy window의 photon count 보존을 자동 보장하지 않는다.

## 2. Intensity, occupation, screen

coherency spectral intensity를 \(J_E\)라 쓰면 collisionless invariant는 \(f=J_E/E^3\)다. 상수 정규화는 관측량 비에서 소거되지만 시간·방향에 따라 바꾸지 않는다. 고정 target E에서

\[
J_{E,1}(E_1,n_1)=R^3\,\mathcal R J_{E,0}(E_1/R,n_0)\mathcal R^T.
\]

f를 진화하면 위 \(R^3\)도 따로 곱하지 않는다. bolometric intensity는 energy 적분 때문에 forward \(R^4\)지만 monochromatic intensity에 그 인자를 쓰지 않는다. 같은 target E의 \(q_2\)는 trace f로 계산해도 정확히 같은 비다.

축대칭 meridional screen을

\[
e_\theta=(\mu\cos\phi,\mu\sin\phi,-\sqrt{1-\mu^2}),
\quad e_\phi=(-\sin\phi,\cos\phi,0)
\]

로 둔다. n은 고정 meridional plane 안에서 이동한다. e_phi의 spacetime covariant derivative는 0이고, e_theta의 derivative는 photon ray와 time 방향 성분만 가져 screen projection이 0이다. 따라서 이 screen의 optical rotation은 **정확히 0**이다. 두 diagonal screen occupation \(f_\theta,f_\phi\)를 역특성선에 따라 그대로 옮길 수 있다. target의 3×3 coherency tensor는 target screen으로 재구성한다. source 3×3 tensor를 target 방향에서 단순 재투영하는 것과 다르다.

\[
I=f_\theta+f_\phi,\qquad Q_S=f_\theta-f_\phi,
\qquad U_S=2\Re f_{\theta\phi}.
\]

여기서 Q_S는 재이온화 filling factor Q와 다르다. 축대칭·거울대칭의 unpolarized IC에서는 U_S=V=0이 계속 유지된다. pole에서 screen gauge는 유일하지 않으므로 Gauss–Legendre처럼 pole을 피하는 quadrature가 편하다.

## 3. Native Thomson과 독립 축대칭 행렬

native 연산자는 \(\partial_\tau J=-J+KJ\),
\(KJ=(3/8\pi)\Pi\,[\int Jd\Omega],\Pi\)이며
\(d\tau=c\sigma_T n_e\,dt\)다. 고정 energy에서 작용하므로 occupation과 spectral intensity 모두 같은 K를 쓸 수 있다.

축대칭이면 \(M=\int Jd\Omega=\mathrm{diag}(m_\perp,m_\perp,m_\parallel)\)이고

\[
m_\perp=\pi\int_{-1}^{1}(\mu^2f_\theta+f_\phi)d\mu,
\qquad m_\parallel=2\pi\int_{-1}^{1}(1-\mu^2)f_\theta d\mu.
\]

따라서 독립 reference의 충돌 RHS는

\[
\partial_\tau f_\theta=-f_\theta+{3\over8\pi}
 [\mu^2m_\perp+(1-\mu^2)m_\parallel],\qquad
\partial_\tau f_\phi=-f_\phi+{3\over8\pi}m_\perp.
\]

이 식을 작은 Gauss–Legendre grid의 **직접 2N×2N 행렬**로 만들고 scipy matrix exponential을 적용하면 native rank-9 세 계수 구현과 다른 oracle을 얻는다. 같은 물리 핵과 quadrature를 공유하지만 native packing/고유공간/three-term 구현은 공유하지 않는다.

Native에 full 3D 방향을 공급할 경우 φ를 1개만 두고 2π weight를 주면 tensor 적분이 잘못된다. GL N_mu≥3, periodic N_phi≥5면 4차 다항식을 적분할 수 있으며 N_phi=8이 작은 안전 선택이다. 4개 azimuth는 cos(4phi)를 alias하므로 일반 rank-9 고유값 확인에는 불충분하다. 이번 축대칭 state에서 quadrature·screen 재구성 후 native를 실제 호출하고, 다시 scalar screen으로 환원하는 경로를 확인해야 한다.

## 4. 예상 null, 부호, 저차 oracle

등방 unpolarized IC와 등방 source에서는 F/M/M_F의 q2,p_L=0이다. 같은 IC의 B0는 q2를 만들 수 있으나 p_L=0이다. 축대칭 B/B_F의 U_S,V도 0이다. 이 null은 작은 양의 임의 바닥값으로 바꾸지 않는다.

초기 occupation F(w)가 정확히 상수이면 비등방 redshift도 occupation을 바꾸지 못하므로 B/B0에서도 q2,p_L가 모두 0이다. 이는 spectral intensity \(I_E\propto E^3\)에 해당한다. 따라서 실제 smooth benchmark F(w)의 slope가 있는 에너지 구간이 신호 비교에 필요하다. R15 integrated emissivity로 F(w)를 새로 추정하지 않는다.

후속 source 확인: 복구된 `inputs/upstream_bass/bianchi/q/modeb.py::planck_state`의 기존 isotropic 기본 IC는 dimensionless T=1인 Planck occupation이다. 초기 이후 방출은 0으로 고정한다. 이번 Eulerian 좌표 \(y=(a/a_i)E/(k_BT_i)\)는 초기 energy scale로 나눈 mean-a comoving energy이며 기존 코드의 방향 의존 conserved-momentum 좌표 q와 전 구간에서 같은 변수가 아니다. 초기 β=0에서 IC 함수만 일치시킨다. T_i는 scale parameter이고 관측 CMB 온도를 새로 가정하지 않는다.

작은 shear에서 \(I=F+i_2P_2\), \(Q_S=q(1-\mu^2)\)로 두면

\[
\delta=m_\parallel-m_\perp={2\pi\over5}(-i_2+4q),
\quad {d\over d\tau}\begin{pmatrix}i_2\\q\end{pmatrix}
=\begin{pmatrix}-9/10&-2/5\\-3/20&-2/5\end{pmatrix}
\begin{pmatrix}i_2\\q\end{pmatrix}.
\]

행렬의 고유값은 −1,−3/10으로 native의 quadrupolar decay와 일치한다. \(u=\ln(a/a_i)\), \(r=s/H\), \(v=d\tau/du\), \(D_F=d\ln F/d\ln w\)를 쓰면 normalized amplitudes A=i2/F, B=q/F는

\[
{d\over du}\begin{pmatrix}A\\B\end{pmatrix}
=\begin{pmatrix}2rD_F\\0\end{pmatrix}
 +v\begin{pmatrix}-9/10&-2/5\\-3/20&-2/5\end{pmatrix}
 \begin{pmatrix}A\\B\end{pmatrix},\quad q_2=A/5+O(\beta^2).
\]

무충돌에서는 \(q_2=(2\Delta\beta/5)D_F+O(\beta^2)\). Planck occupation이면 \(D_F=-y/(1-e^{-y})\), \(y=E/(k_BT)\). 이는 유도된 slope 관계이며 실제 초기 spectrum이 Planck으로 확인되기 전 입력 선택의 근거로 삼지 않는다. 감소하는 F, 양의 beta에서 q2<0이고 초기 Thomson polarization은 Q_S>0으로 생성된다.

실제 beta≈0.059를 1차 oracle과 정확히 일치시킬 필요는 없다. O(beta²)가 존재한다. 필요하면 같은 처방 beta만 작은 epsilon으로 축소한 **수치 진단**에서 oracle과 비교하고, 이를 별도 GR 배경의 물리 재채택으로 표시하지 않는다.

## 5. 전자 이력의 공통 clock 재투영

복구 producer는 균등 u fine cell마다 midpoint H,n을 고정하고 capped Q ODE의 analytic integral \(\int Qdu\)를 저장 τ에 사용한다. 이 의미를 보존하면 F history를 B clock으로 옮긴 fine cell depth는

\[
\Delta\tau_{F\to B,i}
=\Delta\tau_{F,i}
{H_F(u_{i+1/2})\over H_B(u_{i+1/2})}
\times {\sigma_{T,\mathrm{consumer}}\over\sigma_{T,\mathrm{producer}}}.
\]

B의 기존 depth도 같은 sigma_T 상수비만 적용한다. 이는 original Q(u) integral, density midpoint, \(dt_B=du/H_B\)를 보존한 재투영이다. N4의 F ne_eff를 순간 밀도처럼 B의 시간 셀에 복사하는 것이 아니다. coarse cell은 대응 fine depth의 합이다. 새로운 interpolation 선택이 필요하면 기존 producer 의미에서 벗어나는 영향과 refinement를 따로 기록한다. 완료된 Q ODE를 다시 적분할 이유가 없다.

## 6. 결합·정확도·비용 조언

처방 beta의 정확 Liouville submap과 native exact collision을 Strang으로 결합하면 좋은 작은 후보가 된다. 하나의 cell에서 총 τ가 같아도 Liouville과 collision이 교환하지 않으므로 내부 time ordering 오차는 남는다. midpoint u에 맞춰 두 Liouville 부분의 beta 증가량을 각각 사용하고, collision에는 해당 cell의 총 depth를 쓴다. grid refinement는 원래 u fine cell 경계를 묶거나 나누면 provenance가 간단하다.

각도 16–32 × azimuth 8 정도에서 pilot을 시작할 수 있다. scalar screen occupation을 수송하면 큰 3×3 배열의 interpolation을 피한다. 에너지 spectrum은 단순 저차 선형 보간을 매 step 반복하면 누적 diffusion이 생길 수 있어, smooth spectral/Chebyshev 또는 충분한 order의 방법과 energy domain 확인이 필요하다. 선택 자체보다 B0 exact pullback 및 paired response refinement가 판별 기준이다.

같은 geometry의 B,B_F를 같은 grid와 operation으로 진화한다. delta state를 동시에 진화하면 작은 history response의 roundoff와 common interpolation 차이를 줄일 수 있지만 필요성은 실제 크기로 판단한다. 정확 collision difference는 \(e^{x_B C}-e^{x_F C}\)의 expm1 형태로 계산할 수 있다. 작은 결과라는 이유만으로 고정밀이나 NCP를 시작하지 않는다.

최소 해석 검사는 B0 exact spectrum/q2, isotropic null, native-vs-dense collision 및 polarization positivity, time/angular/energy의 **paired observable** refinement다. final→refined 값 차이는 관측된 수치 민감도이지 엄밀 오차 상계가 아니다. history difference의 10%를 만족했는지 별도로 기록한다. 큰 B−M 신호의 수렴으로 작은 history 차이까지 분해됐다고 말하지 않는다.

이 노트는 validation design을 제공했으므로 작성자는 B1 최종 PROMOTE를 독립 승인하지 않는다.
