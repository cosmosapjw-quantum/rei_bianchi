# BASS_HE C0A3: 원자 표 보간과 유한 구간 함수형

2026-10-03. 원자물리 데이터 전용. rei_bianchi의 기하/유체/수송 코드는 변경하지 않았다.

Archive: BASS_HE_EOR_C0A3_INTERPOLATION_RATE_20261003_v1.zip
Bytes: 3286152
SHA256: 3d10ecc4e57f6b9c894a962c4e97ffcfa97b664eb36429ceb5eda39b2d230a1e
ZIP entries64, manifest payloads63. CRC와 새 디렉터리의63개 해시를 시험 전후 검증했다.

원 C0A2 parent archive a2060d7842636fb5d08cfbb27c263d30ef78728bae0ebf4bda734c5f11697eb1을 보존한다. 부모 raw4CSV와 native package bytes 동일. 이 단계에 앞서 기존 branch에 C0A2 public12개 파일과 backup 기록을 게시했고 Drive/Dropbox의 ACK/object/size를 확인했다. 원 Dropbox 동명3160090byte 사본은 건드리지 않고 현재3172184byte parent는 SHA suffix로 구분했다. 이전 실패 receipt는 보존한다.

새 코드: opt-in linear_E/loglog, native-node token 보존, own-grid와 scope-anchor/결측/외삽 거부, disjoint component sums, exact-rational union-knot order check, 양의 endpoint weights에 의한 선형보간 Maxwell 함수형, 명시적 E_cm/native scale 및 reduced mass 조건부 partial-rate, create-only CLI. linear_E는 기본 물리 모형을 승인한 것이 아니다. loglog rate integration은 이번 단위에서 미구현이다.

양의 weight는 w0=integral_a^b x exp(-x)(b-x)/(b-a) dx, w1=integral_a^b x exp(-x)(x-a)/(b-a) dx다. a>=0,b>a에서 positive이며 합은 (1+a)e^-a-(1+b)e^-b다. 짧은 panel은 차분 대신 직접 급수로 계산한다. explicit E_cm=s*epsilon일 때 theta_native=theta_J/s, k_D=sqrt(8theta_J/(pi mu))*F_D. 수치결과는 조건부 finite-support 값이고 full/tail은null이다. support-weight로 재정규화하지 않는다.

실제 자료662개 paper-domain midpoint의 linear/loglog 최대 상대차는0.36390975822205335, H1s->He1s epsilon3.125에서다. 이것은 방법민감도이지 source uncertainty가 아니다. 원743 sample은 그대로 보존했다. 총량과 제공partial의 PWL 순서는 H1s28개/H2s27개 unionknots에서 정확유리수로 확인했으며 이를 source UQ/누락고n/ionization에 배정하지 않는다.

새 focused tests81개 PASS:50개 실제 RED→GREEN,31개 후속검증. 전체payload716 midpoint 양성,743 native token,8개80digit Maxwell-weight oracle(최대상대차1.9550198962512063e-16),9개60digit source-functional quadrature(최대상대차8.66338048513772e-17),반례/단위/결측/범위/full-rate/underflow/CLI 검사를 포함한다. 별도 wheel 설치와 새 archive extraction에서81개씩 재현했으며 반복을 새고유시험으로 세지 않는다. 과거52/43/67/90 scientific suite는 반복하지 않았다.

Wolfram 최초 Limit 경고는 보존했고 regularized 계수/적분 검사에서 경고없는0과small-cell coefficients를 확인했다. SciSpace의 좁은 검색은 직접근거를 반환하지 않아 새 source를 import하지 않았다. 독립scientific review는NOT_RUN이다.

배포: 이 namespace에는 새 기능코드/81개시험소스/설정/설명서9개와 본기록1개를 공개한다. 원자료 및 전체수학/계약/실패로그는 SHA-bound privateZIP에 있다. 공개tests도 private source/inputlock이 필요하며 sourcePDF/CSV를 publicGit에 재배포하지 않는다. 같은branch additive/non-force이며 최종Git/cloud object identity는 detached receipt가 소유한다.

Gate: C0physical_ready=false, EOR_THEORY_GATE=NOT_SATISFIED, scientific_PROMOTE=HOLD, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED. sourceUQ/isotope/per-u/license/미제공6개quantity/low-energy R_CX/ION secondary/recoil/photonmoments는OPEN이다. 실제scattering/newFortran/MPI/cosmological history는0이다.

NEXT=EOR_C0A4_ATOMIC_CONVENTION_AND_REQUIRED_MOMENT_SOURCE_BINDING. 실제sourcemetadata와 원자moment를 결속하고,가능한 source/atomic product-code 작업을 여기서 진행한다. NCP는지금선행조건이아니다. 큰등록수렴/충돌영역계산/실제병렬성능검증때넘기며 missingmetadata를CPU문제로분류하지않는다.
