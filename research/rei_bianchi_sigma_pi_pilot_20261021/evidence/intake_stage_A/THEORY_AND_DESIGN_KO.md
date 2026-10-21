# 오늘의 non-tilted Bianchi I Σ–Π pilot

## 연구 선택과 새 결과 intake

목표는 원본 REI의 자체 중력 Einstein–Vlasov/질량 없는 Boltzmann 계열을 재사용하여 z̄=20→4의 첫 물리적 초기 Σ₀–Π₀ 격자와 그림을 실제로 만드는 것이다. 현재 PR198의 최적화 대상이던 화학/광자 age-cell solver와 이번 배경 pilot은 서로 다른 계산 경로다. 두 경로의 결과·비용·허용 범위를 섞지 않는다.

GitHub에서 rei_bianchi의 branch 253개(100+100+53+빈 페이지), PR 211개(100+100+11+빈 페이지; open197), 접근 가능한 소유자 repo51개의 목록을 확인했다. 실제 내용은 목표와 관련된 PR137/140/141/142/145/147/149/198/199 및 관련 BASS 공급 경로를 선별해 읽었다. 모든 branch의 모든 파일을 감사한 것은 아니다. PR198은 3360a345…, PR199는 새 964b2e3…이다. PR199 v11 반환은 완료된 time8/16/32에서 12 scalar의 인접 차이가 줄지만 원래 .005 목표는 실패하며, 새 READY NCP 작업은 없다고 명시한다.

Dropbox 두 관련 폴더의 목록40/38개는 has_more=false까지 확인했다. Drive의 현재 백업 폴더141개 및 원래 REI_RESEARCH_BACKUPS/rei_bianchi의13개 하위 폴더는 반환된 목록 범위다. 도구가 전체 Drive 페이지 완결을 노출하지 않아 전역 전수 내용 확인으로 표현하지 않는다. 대화 검색은 실제 personal_context_search가 unavailable 오류를 반환했다. 이 범위는 검색 공백으로 보존한다.

실제 회수·해시·본문 확인한 C15 Σ–Π v2 백업은 8×64개의 따뜻한 z≈4 짧은 구간 실행이다. PR141/142 역시 제한된 native chemistry–Einstein 피드백 사례다. PR149는 고정 배경의 선형 Case-A 압력 응답이다. 이번 z20→4의 빠른 pilot에는 PR145/147의 충돌 없는 자체 중력 solver가 직접 맞는다. canonical_fv.py의 검증된 SHA256은 91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5이다. 38개 관련 원본 파일은 Git blob/크기와 일치했다. 그 중 필요한 3개 Python 파일과 원래 cosmology lock만 새 additive subtree에 원문 그대로 포함한다.

## 1. 정규화와 완결된 조건부 모델

원본 저장소 관례를 유지한다. metric(-,+,+,+), 우주 고유시간 t, a⊥=a exp(-b), a∥=a exp(2b), H=ȧ/a, s=ḃ이다. 정규직교 공간 성분은

σᶦⱼ=diag(-s,-s,2s), πᶦⱼ=diag(-p,-p,2p), p=(P∥-P⊥)/3.

|T|=sqrt(T_ab T^ab/2)를 사용하므로 Σ=√3|s|/H, Π=√3 K|p|/H²이다. K=8πG/c²는 에너지밀도 J/m³와 고유초 H를 쓰는 시간형 Einstein 계수다. κ_E=8πG/c⁴를 쓰면 같은 Π는 κ_E|π|/(H/c)²다. Frobenius norm을 택한 값은 두 축 모두 √2배이며, 기존 코드의 pi_s 압력이나 (P∥-P⊥)를 그대로 Π라고 붙이지 않는다.

ρ는 Λ를 제외한 에너지밀도, p̄는 평균압력일 때

3H²=Kρ+Λc²+3s²,
ṡ=-3Hs+Kp,
ρ̇=-3H(ρ+p̄)-6sp,
Ḣ=-K(ρ+p̄)/2-3s².

이에 따라 C=3H²-Kρ-Λc²-3s²에 대해 Ċ=0이다. σ:π=6sp를 빼면 이 보존 관계가 깨진다. Wolfram Language에서 두 norm 제곱3s²/3p², 수축6sp, Ċ=0, <P₂²>=1/5, 초기 Σ 변환을 실제 계산해 일치했다. 첫 실행은 기호 S,A의 undefined 경고를 포함했으며, 결과는 의도한 자유기호식이다. 별도 깨끗한 평가와 원문 결과를 evidence에 보존한다.

두 magnitude만으로 일반 non-tilted Bianchi I의 초기 텐서 방향과 응력 조성은 정해지지 않는다. 이번 pilot은 LRS, reflection-even, 광자·질량 없는 중성미자의 공통 W=1+kP₂, 처음 isotropic인 massive FD 성분을 고정한다. eps_sigma와 eps_pi를 별도 좌표로 유지한다. fm=.1은 기존 Ω_m에서 차감한 비바리온 성분이며 m/Tref=30, 24×12 canonical cells, Gauss3를 사용한다. Ω_b, Ω_m, Ω_r, Λ, H0 및 z20→4 clock은 원래 lock 그대로다. 자유 팽창으로 massive stress가 발생하면 Einstein 방정식에 계속 들어간다.

## 2. 물리적 초기 축의 역변환

초기 massive quadrature의 정규화와 isotropy를 실제 fields로 확인한다. q=s₀/Href=eps_sigma Σ₀/sqrt(3-Σ₀²). 공통 massless P₂ amplitude k는 E₂(0)=k/5이고 p_rad(0)=ρ_rad(0)k/15이므로

signed Π₀ = B(Σ₀) k,
B=(√3/5) [H0² Ω_r/a_ref⁴]/H_initial².

massive quadrature가 만드는 기계 정밀도 수준의 초기 pi_s offset까지 계산하여 target에서 빼고 k를 정한다. 초기 반환 fields가 목표 Σ₀,Π₀를 각각 절대1e-12 이내 실현하는지 확인한다. Σ₀∈[0,.004], Π₀∈[0,.001]의 각13개 격자에서 비영 값의 두 부호를 독립 선택한다. 영점은 중복 제거하여 총625개 서로 다른 초기 조건이다. 최대 |k|≈.4736658로 원본 |k|≤.5 범위에 들어간다.

## 3. 최적화의 수학적 근거

원본40차원 상태는 geometry4개 및 γ/ν의 energy/number 각 L+1=9개다. 이번 조건에서 (i) u_th=0, (ii) 충돌이 없고 초기 γ/ν energy가 같아 항상 동일, (iii) 짝 parity 공간이 불변, (iv) number multipole은 geometry와 energy에 feedback하지 않는다. 필요한 관측량을 계산하는 상태는 (τ,b,v,E₀,E₂,E₄,E₆,E₈)의8개로 줄어든다. τ=Href·elapsed_t, v=s/Href이며 x=ln(a/a_ref)이다.

원본의 energy matrix M에서 짝수 block을 취하고 w=s/H=Href v/H라 두면 E′=w M_even E, b′=w이므로 E(b)=exp(b M_even)E(0)라는 추가적인 조건부 항등식도 얻는다. 구현은 안정적인 기존 DOP853 형태를 유지한8상태 ODE를 사용한다. 행렬 지수화를 매 RHS에 추가하는3상태 대안은 이번 pilot의 별도 구현 범위에 넣지 않았다. 이는 향후 선택 가능한 정확한 reduction이다.

massive canonical cell population은 conserved Killing momentum 좌표에서 이미 상수다. 이를 다시 시간 적분하지 않으며 원본 positive moment helper를 재사용한다. quadrature와 M_even은 worker 안에서 재사용하고 output history의 massive diagnostics는 원본 bounded moment_batch를 이용해 벡터화할 수 있다. adaptive IVP 사이의 독립성을 유지하여 case 단위 process parallelism을 적용한다. SciPy의 vectorized=True는 독립 parameter ensemble 스위치가 아니므로 켜지 않는다.

이 변화의 확정 가능한 이득은 ODE 상태40→8, energy block 중복 제거, immutable object 준비의 worker당 재사용이다. wall-speedup과 RSS 감소는 이번 요청에서 측정하지 않는다. borrowed-cell의 과거 느려진 비율을 이 새 경로의 성능으로 바꾸어 주장하지 않는다.

## 4. 최소 정확도 확인과 가용 자원

full original source6개 비교, L8↔L12의 두 corner, tolerance/10의 한 corner, 초기 축과 massive energy identity가 이번 변경에 필요한 표적 검증이다. 세부 기준은 PILOT_CONTRACT.md에 고정했다. 대규모 benchmark와 완료된 native10/19/84 이력의 반복은 하지 않는다.

NCP 목표64CPU/128GiB는 최대 요청량이다. scheduler는 affinity, cgroup quota, 사용 가능한 메모리와 짧은 CPU idle 관측으로 실제 worker 수를 정하고 batch 사이 재평가한다. 다른 작업 존재만으로 전체중단하지 않으며, unrelated process를 종료하지 않는다. BLAS/OpenMP는 worker당1thread로 제한한다. nominal memory256MiB/worker는 admission 추정이며 RSS 측정치가 아니다. 새 pilot wall900s/aggregate solve3600s 한도는 구 V12의 cap180/debit200.39897231891518과 별도다.

현재 sandbox key는 실제 부재, 연결된 Desktop Commander는 월 사용량 소진을 반환했다. 이번 NCP는 미실행이며 샌드박스의 실제 pilot 결과만 host를 표시하여 게시한다. 사용자의 후속 Codex는 지정 ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22로 연결하여 같은 additive code를 실행할 수 있다.

## 5. 재사용한 원전/도구

- Agullo, Olmedo, Sreenath, Phys.Rev.D101,123531 (2020), §II, equations14–18 및 anisotropic-source footnote: https://arxiv.org/html/2003.08428v2 . 논문의 full-contraction shear와 여기 half-contraction의 √2 대응을 명시했다.
- Aluri et al., JCAP12(2013)003: https://arxiv.org/abs/1210.3159 . SciSpace 실제 검색으로 anisotropic-source Bianchi I 연구를 확인했으며 모델 closure를 이 논문으로 임의 교체하지 않았다.
- Calogero–Heinzle, CQG24(2007)5173: https://arxiv.org/abs/0706.3823 . 물질 closure별 dynamics가 달라진다는 문헌 비교에 사용하며 elastic closure를 이번 collisionless 결과에 섞지 않는다.
- SciPy solve_ivp 공식 문서: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html . DOP853 및 vectorized semantics.
- SciPy parallel execution 공식 문서: https://docs.scipy.org/doc/scipy/tutorial/parallel_execution.html . process pool과 BLAS threadpool 제어.
- Exa 실제 두 검색5+5 결과 슬롯과 원문 fetch, SciSpace 실제10개 반환(중복 포함), Wolfram context 및 실제 language evaluator. 검색 결과 개수는 독립 검증 논문 개수가 아니다.

## 연구 판정의 적용 범위

실제 실행과 독립 검토가 끝나면 preliminary source-equivalent collisionless LRS pilot으로 판정한다. 이 결과가 직접 채우는 것은 물리적 Σ₀–Π₀ 격자, sign-resolved 자체 중력 진화와 구현 경량화다. 원래 HHe/EoR convergence HOLD, pressure/recoil/emitter closure, general non-LRS orientation, polarization 및 production NOT_ISSUED는 해당 별도 목표의 기존 상태를 유지한다.
