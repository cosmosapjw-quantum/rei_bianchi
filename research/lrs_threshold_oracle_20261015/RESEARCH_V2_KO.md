# REI LRS HeII 문턱 적응 적분 및 Verner donor 연구, 2026-10-15

## 연구 대상 및 분리 상태

이 문서는 연구 브랜치 research/rei-lrs-threshold-oracle-20261015
(PR152)의 독립 기준 계산을 설명한다. v3/rux 본선, PR150 FLRW
production, 현재 NCP production checkpoint, PR151 원자 계산,
C13/C16/C17 source owner에는 수정이나 merge를 수행하지 않았다.

출발 원본 HEAD: 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
기존 oracle HEAD: 9cd36354e46b8a75e3cb70d87e78f9e3c3c2f0a7.

## R5: 정확한 에너지·각도 특성곡선과 문턱점

(-,+,+,+), 비틸트 LRS Bianchi I,
ds^2=-c^2dt^2+a^2e^-2b(dx^2+dy^2)+a^2e^4b dz^2.
X=ln(a/a0), b=(s/H) X, s/H 일정, -1/2<s/H<1.
sigma^i_j=diag(-s,-s,2s), Sigma=sqrt(3)|s|/H,
orientation=sign(s) 별도. 초기 광자 E0>0, mu0∈[-1,1].

F=(1-mu0^2)e^(2b)+mu0^2 e^(-4b),
E(X,mu0)=E0 e^-X sqrt(F),
mu(X,mu0)=mu0 e^-2b/sqrt(F).

문턱 에너지 Eth를 Xend에서 통과하는 초기방향은

 mu_crit^2 = ((Eth/E0)^2 exp(2Xend) - exp(2b))
             / (exp(-4b)-exp(2b)).

0<mu_crit^2<1인 경우 적분영역을
[-1,-mu_crit],[-mu_crit,mu_crit],[mu_crit,1]로 분할한다.
종별 문턱이 여러 개인 경우 모든 내부 절단점을 병합한다.
Wolfram Language로 F(mu_crit)=(Eth/E0)^2 exp(2Xend)
잔차가 정확히 0임을 검사했다.

고정된 방향의 종별 흡수는
A_i(mu0)=int_0^Xend N(X,mu0) kappa_i(X,mu0) dX,
kappa_i=c*n_i(X)*sigma_i(E(X,mu0))/H(X).
문턱 근처에서 적분상한 min(Xend,Xcross(mu0))가
변하므로 A_i(mu0)는 일반적으로 C0이지만 경계에서
미분이 불연속이다. 횡단하는 단순 문턱에서는
d Xcross/d mu0 = - (partial_mu0 E)/(partial_X E);
따라서 전체각도 GL의 빠른 수렴을 기대할 근거가 없다.
비물리적인 광자수 조정 대신 정확한 절단점 기준으로
구간별 적분을 진행한다.

## R2/R3: 실제 Verner (1996) donor

논문: D. A. Verner, G. J. Ferland, K. T. Korista,
D. G. Yakovlev, ApJ 465, 487 (1996), Eq. (1), Table 1,
https://doi.org/10.1086/177435
원본 원자 데이터:
https://www.pa.uky.edu/~verner/dima/photo//photo.dat
다운로드된 185행 donor 파일 SHA256:
a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389.

실제 HI/HeI/HeII fitting 계수는 원본 ASCII에서 직접 파싱한다.
표 1의 H I, He I, He II Eth는 각각 13.60, 24.59, 54.42 eV.
Verner Eq. (1)은 임계점과 종별 에너지 의존성이 있어
이전 sigma(E) ∝ E^-3의 공통 인자분해를 대체한다.
1 Mb=10^-18 cm^2=10^-22 m^2.
표의 Emax=50 keV까지 적용하며 그 밖은 오류로 거절한다.

이번 시험의 조건은 n_i=n_i0 a^-3 (고정 comoving 중성 원자수),
kappa_i0=c n_i0 sigma_i(Eth)/H0 (입력 무차원),
H(X)/H0는 양의 외부 입력이다.
광자가 각 species로 흡수된 수 A_i와 excess 열 Qheat_i,
ionization threshold/binding energy Eth A_i,
중력 적색이동·전단 work W를 각각 적분한다.
photons_end는 positive exp(-∫sum kappa dX)로 계산한다.
그 뒤 독립 A_i 합 및 에너지 work 적분의 잔차를 점검한다.
Case-A 재결합 재방출, Thomson, gas ionization feedback,
reionization QV 및 실제 cosmological history는 **미포함**.

## C5-C8: 로컬 구현·검증

- 원래 E^-3 기준: 35개 pytest, 지난 시험 통과 유지.
- verner_angular.py 새 구현: 24개 추가 pytest, 총 59/59 통과.
- Wolfram Language와 Python의 HI,HeI,HeII 문턱 단면적 일치.
- 동일 24-ray 평가(전역 GL24 vs 경계분할 GL8 × 3):
  Xend=.61, s/H=-.03: HeII 상대오차 4.09555e-5 vs 0 (표시 정밀도).
  Xend=.61, s/H=+.03: 1.61469e-5 vs 1.12815e-16.
  기준: piecewise GL64 per interval; 정확한 해가 아니다.
- 별도 GL8/16 재귀 adaptive 구현: 각 panel의 진단오차에 따라
  분할/재계산하며 max_depth 초과시 FAIL, false PASS 없음.
- SciPy와 기존 E^-3 oracle은 변경하지 않았다.

## NCP Rust 계산, 실제 실행

실행 호스트: s1a0e5abed09, nproc=64, 메모리=125 GiB.
NCP ~/.cargo/bin/rustc 1.99.0; 비로그인 SSH 기본 PATH에는 없음.
부하를 고려해 16 workers 사용, Rust std::thread, 제3자 crate 없음.
단일 HeII Verner cross-section과 정확한 LRS 특성곡선,
문턱 분할 및 8×8 time-quadrature로 계산.
33 E0 (62..152 eV) × 17 signed s/H (-.08..+.08)
× 11 Xend (.18..+.98) = 6171 cases.
global GL24, piecewise GL8 per interval (cut 경우 3×8=24),
piecewise GL64 per interval 기준.
- 6171 계산 성공. 내부 문턱점과 유의한 HeII 흡수량이 있는
  사례는 533이며 533 모두 piecewise 방식이 개선.
- HeII 상대오차 95백분위: global 1.213848892710e-4,
  split 7.991688061571e-11.
- 최대 상대오차: global 2.119905709197e-4,
  split 2.931680061280e-9.
- 16 workers 0.556초; 1 worker 5.838초 (그 환경에서 10.5배).
- 서로 다른 worker 수의 전체 CSV SHA256 동일:
  0a5879cb713f353a7b91b6c2cc5f543478a97c297d124e5f4fcb65b4a30ba0bd
- Rust unit tests 4/4 PASS; Python–Rust 별개 구현의 원본 donor
  Verner HeII integrated absorption 대조 4사례 최대차
  4.51e-17 (절대값).

대규모 NCP 기록은 evidence/ncp_heii_sweep_20261015/.
단일 HeII 조건부 reference 이므로 production solver의
성능 또는 다종 화학의 수렴성을 주장하지 않는다.

## 이식 인터페이스 및 다음 실제 연구

PR150의 전구간 cut-cell photon transport에 붙일 경우
광자 초기방향 mu0, 물리광자 E0, H(X), n_HI/n_HeI/n_HeII(X),
sigma_i(E) donor, signed shear s/H와 물리 표준 Sigma가
일치해야 한다. 단위 변환 및 species 원자소모 ledger를
우선 비교한 뒤, 실제 gas state를 source-native로 읽을 것.
동적으로 변화하는 n_i(X)를 넣으면 기존 toy E^-3
hazard 인자분해와 고정 ratio 모델은 재사용하지 않는다.
차분 photoheating, ionization fraction 및 thermal feedback의
별도 검증이 필수다. 이 PR은 실제 native solver와 결합하지 않는다.

출판가능성 판단: 정확한 문턱-angle 해석과 조건부 benchmark는
방법론 부속 기술자료 후보, 실제 독창성·범용성·production
최종 정확성 증명은 unresolved. 관측 결과 아님.

관련 병렬 진행: rei_bianchi PR150 FLRW native solver,
PR151 원자/미시물리, PR149 Case-A escaped radiation,
WU088_HH latest PHYS51, bass_cr AOCC sweep.
이 작업은 서로 다른 가정/기여 범위를 섞지 않는다.
