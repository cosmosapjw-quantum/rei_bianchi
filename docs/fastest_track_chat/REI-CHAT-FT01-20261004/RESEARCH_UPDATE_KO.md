# REI-CHAT-FT01-20261004: 이론·경량 수치 연구 1회차

## 상태와 산출물

이 연구 단위는 완료했다. canonical REI-F00~F09의 production 구현/admission/물리 구간 인증을 완료했다는 뜻은 아니다. 기존 TASKS.json의 REI-L01(휴면 정밀·확장 lane)은 활성화하지 않았다.

입력 HEAD: 4af2912ce73fdb1240db74d420a0a48fe686af0b. 기준 code commit: 0100b1dfa023928d67602877876b586fea319d13. branch는 forward/rust-reion-kernels-20260922이며 새 branch나 merge를 만들지 않는다. 두 commit 사이의 3개 commit은 handoff docs 추가이며 active Rust crate 변경은 없었다. 기존 연구의 전수 재감사나 정수 사건회계 재실행은 하지 않았다.

이 GitHub 폴더에는 연구 요약, machine-readable 결과, 다음 작업, 패키지 영수증을 게시한다. 전체 보고서 REPORT_KO.md, 독립 연구 스크립트 3개, 입력 원본, 실행 로그, 상세 결과, 연구 DAG와 hash manifest를 포함한 23-file 재현 패키지는 PACKAGE_RECEIPT.json의 Drive/Dropbox ZIP에 있다. ZIP은 업로드 뒤 변경하지 않았다. ZIP 안 TASK_RETURN의 publication=PENDING은 패키지 동결 당시 상태이며, 이후 업로드 상태는 이 폴더의 PACKAGE_RECEIPT.json으로 읽는다. GitHub에 production solver를 이식한 것은 아니다.

## A. 수소 상수율 oracle: 빼기로 중성 노출량을 만들지 않는다

I=sum I_q, R>=0, k=I+R, h>=0, z=kh이고 dx/dt=I(1-x)-Rx라고 하자. k>0에서

A=(1-exp(-z))/k, B=h-A,
J_ion=x0*A+(I/k)*B,
J_neutral=(1-x0)*A+(R/k)*B.

사건수는 N_q=I_q*J_neutral, N_rec=R*J_ion이며 sum N_q-N_rec=x1-x0이다. 정확 실수 연산에서 A,B와 두 exposure는 비음성이다. 작은 z에서는 B=h-A를 직접 계산하지 않는다:

B/h=sum_{j=1}^{16} (-1)^(j+1) z^j/(j+1)! + remainder,
|remainder|<=z^17/18! (0<=z<=0.5).

A에는 expm1을 사용한다. R/k를 1-I/k로 재구성하지 않는다. 최대 실수 급수 절단오차는 1.191651e-21이며 floating rounding까지 포함한 구간증명은 아니다. k=0 또는 h=0은 별도 identity 처리한다.

실제 반례: x0=1, I=R=1 s^-1, h=1e-16 s에서 naive h-J_ion은 binary64로 0이 되지만 새 표현은 4.999999999999999e-33 s를 준다. 468개 사례(z=1e-24~1e3), 100자리 기준값 대비 최대 positive exposure/event 상대오차는 5.051700272520017e-16이다. 전 binary64/subnormal/overflow domain 인증은 아니다.

## B. 이번 합성 ODE의 정확 유리수 온도 domain certificate

CONTROLLED_FIXTURE 원본은 T-independent 양의 충돌계수를 쓴다. 따라서 종 반응의 양성만으로 열에너지 양성을 주장할 수 없다: u=0에서도 endothermic collisional loss가 남을 수 있다. floor나 clipping을 추가하지 않고 주어진 IC와 시간창에 대한 양의 에너지 여유를 증명했다.

tau=t/t_end, f=nHe/nH=0.083, e=ne/nH=x+f(y+2z), nu=1+f+e, w=u/(nH*eV_erg)로 둔다. 종 simplex와 photon positivity로 e<=e_max=1+2f, nu_min=1+f, nu_max=2+3f가 성립한다. 모든 비영 흡수 채널의 photoheat는 비음성이다.

L=t_end*nH*e_max*(C_H*chi_H+f*C_HeI*chi_HeI+f*C_HeII*chi_HeII),
lambda=t_end*nH*(e_max/nu_max)*(alpha_H+f*max(alpha_HeII,alpha_HeIII)).

첫 thermal zero 도달 전 w'>=-L-lambda*w이므로 0<=tau<=1에서 w>=w0*(1-lambda)-L>0이다. 비교정리와 exp(-a)>=1-a, (1-exp(-a))/a<=1을 사용한다. 첫 zero 도달을 배제하므로 전 시간창에서 성립한다. 총에너지 회계와 비음성 binding/photon/escape reservoir로 w<=E_total,0도 얻는다.

모든 decimal 입력을 정확 Fraction으로 평가하여, t=0~1e12 s에서 4800 K<T(t)<36000 K를 증명했다. 더 좁은 유리수 경계의 근사값은 4867.6158861133445 K와 35284.17044268757 K이다. 상세 numerator/denominator는 ZIP의 results/rational_domain_certificate.json에 있다.

이는 정확 연속 합성 ODE의 domain 증명이다. numerical implicit map의 root/local-error/public-width 증명, Grackle 물리율 또는 팽창/Bianchi/inherited history 인증으로 이전하지 않는다.

## C. 독립 합성 기준해와 실제 검증 범위

정지·균질 H/He 다섯 종+세 단색 photon group, source=0, Case-A escape, primary-only라는 원 fixture 정의를 그대로 계산했다. 7개 독립 동역학 상태와 누적 ledger를 쓴 DOP853/Radau, 그리고 다른 상태표현(다섯 종 직접 진화)을 쓰는 독립 60-working-digit RK4를 비교했다. RK4는 128/256/512/1024분할이다. 60자리 working precision은 60자리 정확도 보증이 아니다.

최종 합성 기준값:
- x_HII=0.222219324352
- x_HeII=0.116285729818
- x_HeIII=0.001637763521
- T=9375.31002891 K

DOP853-Radau scaled endpoint 차이 최대 1.5543122344752192e-15. RK4 refinement 차이비 17.04459, 16.52966은 4차 수렴과 일관적이다. Richardson-DOP853 fractions/lnT 차이 최대 3.2431462713859372e-15. float 종/광자 ledger 최대 잔차는 6.38378239159465e-16이다. 수치적 일치 및 수렴 증거이며, rigorously enclosed ODE solution은 아니다.

중요: T-independent rate 때문에 6D chemistry+photon subsystem은 thermal 변수와 독립이다. 따라서 이 합성 시험만으로 온도 되먹임, 실제 stiffness, thermal bifurcation을 검증했다고 주장하지 않는다. 원 fixture는 보존하고 후속 온도 의존 시험을 별도로 설계한다.

## D. 대표 rate의 열좌표 도함수

beta(T)=A*sqrt(T)*exp(-B/T), theta=ln T, r=B/T이면 beta_theta=beta*(1/2+r), beta_theta_theta=beta*(1/4+r^2)이다. T=K*w/nu에서

beta_w=beta*(1/2+r)/w,
beta_nu=-beta*(1/2+r)/nu,
beta_ww=beta*(r^2-r-1/4)/w^2,
beta_w_nu=-beta*(r^2+1/4)/(w*nu),
beta_nu_nu=beta*(r^2+r+3/4)/nu^2.

SymPy로 7개 항등식을 exact zero 확인했다. nu의 population 미분과 ne*ns prefactor 곱미분은 별도로 적용한다. lnT에서의 양의 이차미분을 전체 state Hessian의 PSD로 오인하지 않는다. 전체 Grackle 도함수 admission이나 실제 map의 uniform bound는 아니다.

## 유지한 경계와 다음 연구

physical_provider_admitted=false, first_physical_interval_certified=false, Bianchi_history_runs=0. cargo build/test, scripts/verify_repo.py, MPI/GPU 및 46080-node 실행은 모두 0이다. 연구 전용 Python 스크립트는 production runtime/JAX 복원이 아니다.

strict local error<2e-4, public width<2e-3, 기존 [160,161] 실패 2.1245050576368385e-4와 tick-160 prefix는 유지했다. HomogeneousBoundFree와 InheritedEffectiveMfp는 혼합하지 않는다. 이번 7D toy state를 실제 Bianchi parent로 선언하지 않는다.

다음 ready 연구: REI-CHAT-FT02_PROVIDER_DOMAIN. 이미 잠긴 Grackle 3.4.1/Verner의 선택 H/He 함수만 source-domain/unit/case/branch/derivative/reference-point에 대응시킨다. 실제 residual과 source-site가 미정이면 그 항만 unresolved로 남기며, 문헌·저장소 전수 재조사는 하지 않는다.
