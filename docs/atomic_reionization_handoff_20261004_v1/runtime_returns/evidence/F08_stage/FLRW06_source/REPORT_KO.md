# REI-CHAT-FLRW06-20261005

## 판정

`REFERENCE_COMPLETE__NATIVE_BLOCKED`.

FLRW05가 준비한 96개 node를 실제 public Rust API에 연결하는 것이 이번 루프의 주 작업이다. 현재 runtime에서 rustc/cargo는 없으며 native preflight는 exit78, `BLOCKED_COMPILER_ABSENT`를 반환했다. 실제 native compile/call은0이다. 원본 source를 단일 rustc로 호출하고 반환을 독립 기준과 비교하는 최소 실행기를 작성했으나 Rust driver 자체는 아직 컴파일하지 못했다. Python wrapper의 문법과 manufactured protocol 테스트만 통과했다.

이번에 실제 실행한 연구는 정확한 binary64 입력의80자리 독립 finite-node 기준값, native 입력/반환 계약의 검증, 그리고 고정 에너지 bin의 두 moment 양성 영역을 지키는 정확한 선형 단계 상계다. 이 결과를 production native 성공으로 부르지 않는다. 기존 FLRW05 스펙트럼 전체 suite, 원자 데이터 전수 감사, ODE history는 재실행하지 않았다.

## 소스와 현재 상태

시작 및 연구 경계의 실제 GitHub HEAD는 `b553698a114fbff05640ab6ecb95d260410de492`였다. 이전 결과 `69fd2901257ee156f5f57ee5eea579d56d02833e` 이후3개 commit에는 F07 사전등록 및 F04 interval/actual-map certificate가 추가되었다. `runtime_returns/EXECUTION_STATE.json`, `REI-F04.json` 앞부분, `runs/rei_fastest_v1/map_certificate/checker_receipt.json`을 읽었다.

최신 반환은 외부 REI-F04를 pinned static FT03 numerical domain에 한해 completed로 기록하고 다음 작업을 REI-F05로 지정한다. Checker receipt의 최대 local bound는9.534453118819423e-9, public width는1.5867951486958153e-6이며 physical fit error는 NOT_MEASURED, scientific admission은 HOLD다. 이는 외부 보고를 읽은 수신이다. Checker를 여기서 재실행하거나 전체 증명을 재감사하지 않았고, 해당 static 인증을 이번 evolving spectrum에 이전하지 않는다. 오래된 CODEX_SYNC와 historical field의 pending 문구를 최신 상태로 사용하지 않는다.

현재 read 범위에서 homogeneous_photo_rates는 arbitrary-length positive PhotonNode 배열을 받는 native photo callback이다. PhotonInput의 absorption은 proper cm^-3/s, photons는 a³*n per reference comoving cm³다. 이전 photo API의 node는 comoving cMpc^-3다. Source binding은 별도 JSON에 보존한다. 기존 implementation body와 소비자 코드는 변경하지 않았다.

## 1. 동일한 입력을 비교하기 위한 기준값

metric signature는(-,+,+,+), 시간은 proper second, c=29979245800 cm/s를 유지한다. nH=1e-4 cm^-3, a=.5, H=5e-14 s^-1인 한 stage를 사용한다. absorber proper densities는 HI/HeI/HeII=(8e-5,5e-6,1e-6) cm^-3다. 이는 photo stage 입력이며 새로운 재결합·온도·전체 우주론 이력이 아니다.

Bin edges는13.6,24.59,54.42,100 eV다. FLRW05가 지정한 양의 exponential reconstruction에서 나온3bin/96node를 원 ZIP에서 bytes 그대로 계승했다. 원 ZIP SHA256은 c57010a6252694d537642987ac5fb0746787aadb70c9c020027f65548caa737c다.

native에 실제 전달되는 f64를 정확한 정수비로 변환해80자리 mpmath 기준을 계산했다. JSON에 표시된 짧은 decimal을 임의의 더 정확한 물리상수라고 해석하지 않는다. 원 parameter는 Verner HI/HeI/HeII fit의 기존 고정 값이며, physical threshold와 fit cutoff를 혼합하지 않는다. 공식 source는 Verner et al.1996, DOI10.1086/177435와 저자 data page다. 새 물리 fit 검증은 아니다.

각 node의 proper photon density는 n_gamma,i=N_c,i/(a*MPC_CM)^3다. 동일 measure로

Gamma_s=c sum_i n_gamma,i sigma_s(E_i),
R_s=n_s Gamma_s,
A_s=sum_i E_i dR_si,
B_s=chi_s R_s,
Q_s=sum_i(E_i-chi_s)dR_si

를 계산한다. A/B/Q의 eV를 erg로 바꿀 때 고정 EV_ERG=1.602176634e-12를 한 번만 적용한다. Heat는 큰 두 값의 뺄셈만 사용하지 않고 원 적분으로 계산한다.

FLRW05가 저장한27개 baseline events/heat/binding field와 비교했으며 nonzero18개 값의 최대 상대차는2.3871363948098301e-15였다. 기대값의 차이는 native 실행오차가 아니다. 이전 기대값을 native result로 재명명하지 않았다.

새 finite-input reference11개는 baseline3, joined96, 역순96, 분할192, a->a/2와a->2a gauge2개, zero photons, zero absorbers, exact fit thresholds다. Node 순서 및 split은 같은 수학적 measure이고, a->lambda*a와 N_c->lambda³*N_c를 동시에 바꾸면 proper rates는 불변이다. 80자리 기준에서 reorder/split의 최대 상대차는2.44e-80, 두2진수 gauge에서는0이다. 실제 f64 native summation invariance는 아직 실행하지 않았다. Zero absorber에서도 per-atom Gamma는 일반적으로0이 아니고 events는0이라는 점을 분리했다.

## 2. 주입되지 않은 실제 native sink를 검사하는 실행기

`research/run_native.py`는 기존 local repo에서 source6개를 git show로 읽고 기대 Git blob과 비교한다. scientific module5개는 변경 없이 사용하고, 원 lib.rs의 공통 type block과 필요한 module exports만 연결한 minimal root를 만든다. 전체 crate, cargo, 기존 tests, 원자 source 다운로드 또는 history는 실행하지 않는다. 동작 경로는 준비된 driver -> 실제 homogeneous_photo_rates -> 그 native bin0/1/2의 events 합 -> 실제 photon_balance다.

핵심은 photon absorption을 Python의 expected array로 채우지 않는 것이다. Input에는 source/edge/count만 들어가며 absorption은 실제 native 반환에서 조립한다. 이를 protocol test로도 확인했다. photon_balance는 independent U state를 반환하지 않으므로 에너지-stage 계산은 아직 독립 수학 기준이고 native U 소비자의 검증이 아니다.

native 입력은11개 valid +6개 invalid profile과 마지막 photon call이다. 실행 후 비교할 scalar는167개다. invalid profile은 scale0, 음의 absorber density, 음의 node count, zero-count이지만 energy>50000eV, nonfinite energy, 양의 count의 proper conversion underflow다. 각 정확한 error code를 확인하도록 했다. 이는 준비된 사례 수이며 실제 native 통과 수가 아니다.

검증기는 source/blob 일치, compile/run exit0, compiler version, input/binary/stdout hash와 실제 반환이 있어야 pointwise PASS를 만든다. Python expectation file과 manufactured protocol test는 이 gate를 닫지 않는다. 컴파일·실행 오류를 물리 오류로 합치지 않는다. 이 runtime의 preflight 결과는 exit78이며 native_calls=0이다. 직접 raw source 다운로드도 DNS 오류로 실패했고 connector 읽기는 성공했다. 설치나 전체빌드로 우회하지 않았다.

## 3. 두 moment가 양의 스펙트럼을 나타내는 조건

고정 bin [L,R],0<L<R에서 N=integral p(E)dE [photons/H], U=integral E p(E)dE [eV/H]를 둔다. 비음성 measure가 있으려면

N>=0, m_L=U-LN>=0, m_R=RN-U>=0

이어야 한다. 이 조건은 어떤 양의 measure의 존재에는 충분하다. 실제로 endpoint weights

w_L=(RN-U)/(R-L), w_R=(U-LN)/(R-L)

를 사용하면 N과U를 정확히 재현한다. 합과 에너지 moment, m_L+m_R=(R-L)N의 항등식을 symbolic 검산했다. 다만 endpoint atom representation은 일반적인 원 스펙트럼과 같지 않다. FLRW05의 finite exponential 밀도는 N>0일 때 엄격한 interior를 요구하고, boundary mean에는 explicit delta path가 필요하다.

고정된 stage RHS(dN,dU)를 사용한 한 forward-Euler 단계에서는 q=(N,m_L,m_R), dq=(dN,dU-LdN,RdN-dU)가 각각 affine하게 변한다. 따라서

h_max=min_{dq_j<0} q_j/(-dq_j)

가 closed cone 안에 남는 필요충분 상계다. 음의 dq가 없으면 유한 상계가 없고, q_j=0,dq_j<0이면 양의 timestep 자체가 허용되지 않는다. 0<=h<=h_max에서 모든 margin이 비음성이며, finite h_max를 초과하면 적어도 한 face를 넘는다.

이것은 frozen stage의 선형 moment-domain 조건이다. Local truncation error, 안정성, implicit root, 온도범위 또는 physical spectral accuracy의 상계가 아니다. 실제 native 적분기를 Euler로 바꾸거나 원 timestep gate를 완화하지 않았다. 경계 equality에서는 vacuum 또는 delta 등 별도의 표현이 필요할 수 있다. Higher-order/multistage positivity는 각 stage와 convex-combination 조건 등을 별도로 검증해야 한다.

순수 absorption만 있을 때 mean energy m=U/N의 변화는 dm/dt=-Cov_p(E,k(E))다. 낮은 에너지를 선택적으로 흡수하면 평균이 높아질 수 있다. 양의 exact attenuation은 support를 보존하지만 선형 Euler update는 같은 도함수로 upper moment face를 넘어갈 수 있다. 이 covariance 항등식도 symbolic 검산했다.

## 4. 양의 광자수만으로는 부족한 정확한 반례

[10,20]eV에서 p=0.1 photon/H/eV, 즉 N=1,U=15eV/H를 놓는다. H=1/tstar, 최상단 유입0, 최하단 donor trace=p라면 scaled time tau=t/tstar에 대해

dN/dtau=-1, dU/dtau=-25eV/H.

광자수만 보면 h/tstar<=1이지만 두 moment cone은 h/tstar<=1/3을 요구한다. h/tstar=1/2에서 N1=1/2>0, U1=5/2eV/H여서 평균에너지가5eV가 된다. 남은 photon을 [10,20] bin 안의 양의 measure로 표현할 수 없다. 이는 원 native source의 버그가 아니라 number-only timestep 판정의 반례다.

초기 count-only research helper가 h=1을 반환하는 실패를 먼저 실행하고, cone의 세 face를 적용한 수정에서1/3이 나오는 동일 시험을 통과시켰다. red/green 로그와 원 count-only helper를 보존했다. 다른 protocol tests는 후속 tests-after이며 전체 Rust 개발의 TDD 증거라고 하지 않는다.

정확 유리수240개에서는 finite positive bound212개, unbounded13개, outward boundary15개가 나왔다. 각각 경계/바로 전/바로 후의 margin 부호 또는 양의 작은 h의 실패를 검사했다. Floating-point roundoff에 대한 outward interval certificate를 만든 것은 아니다.

## 5. 기존96-node stage에 대한 실제 수치

같은 photo measure와 high-energy donor trace에서 dN을 조립하고, 독립 U 방정식 dU=-A-HU+R*Phi_R-L*Phi_L을 계산했다. Bin N은 원 PhotonInput을 유지하고 U는 동일 node 에너지 합으로 구성했다. 입력 N과 node N의 차이는 최대1.635e-17/H로 별도 기록했다.

| bin/eV | count-only h/s | moment-cone h/s | 제한 face |
|---|---:|---:|---|
|13.6–24.59|1.11302092646e11|9.71802535429e10|RN-U|
|24.59–54.42|7.42836706649e11|5.75910596379e11|RN-U|
|54.42–100|5.13205614237e12|3.43391739965e12|U-LN|

각 bin에서 이 두 제한의 중간 h를 택하면 N은 여전히 양수지만 해당 에너지 face가 음수가 된다. 이 숫자는 prescribed single photo stage의 기준이며, 최종 solver timestep이나 physical history 예측이 아니다.

모든 bin을 합한 U=1.29154133914909617eV/H,
흡수 에너지율=7.60538533239288915e-12eV/H/s,
binding=6.20478806779739797e-12,
heat=1.40059726459549118e-12,
work=6.45770669574548103e-14,
최저 경계 energy exit=9.73200651514921003e-14다.

같은 source/count/energy measure에서 sum(dU)+A+work+Emin*Phi_min-Emax*Phi_max=0을80자리 연산으로 확인했다. residual 약1.85e-92eV/H/s는 수학적 합산 일치이며 실험적 정확도나 실제 native 연산오차가 아니다. 에너지 장부의 선형성은 moment cone의 이탈을 막아주지 않는다는 점이 이번 추가결과다.

## 6. 검증·산출물·남은 것

최종 fresh runner는 새 reference, stage/cone,14개 unit/protocol tests, Python syntax의 네 명령을 실행한다. Native preflight의 exit78은 성공 명령에 포함하지 않는다. Protocol tests의 제조 반환은 파일로 실제 native 증거처럼 저장하지 않는다. No ODE, no old suite, no native compile/call.

완료: 입력 identity 보존,80자리 finite-node 기준,17개 native 입력과167-scalar comparison 준비, 원 native sink만 연결하는 최소 driver/runner, exact moment-cone bound와240개 유리수 검산, 기존 stage의 에너지 수지와 세 bin 부호 반례.

열림: 준비한 Rust driver의 컴파일/실행, 실제 API 반환 비교, independent U native consumer, accepted-stage coupled history, geometric QV, continuum spectral projection error, atomic physical accuracy, expanding interval/root/remainder. 외부 static F04 수신의 완료와 이 항목들은 서로 다르다.

다음 task는 여전히 FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION이다. 필요한 최소 실행은 NEXT_HANDOFF_KO.md의 단일 rustc probe다. Compiler가 없는 이 스레드에서 재검토 계약만 반복하는 것을 native 완료로 대체하지 않는다. 원 F00/F03/FT03, 과거[160,161] FAIL와 tick160, strict local<2e-4/public width<2e-3, physical HOLD를 보존한다.

## 원전·실행 문서

Verner, Ferland, Korista & Yakovlev1996, ApJ465,487, DOI10.1086/177435. 저자 parameter/formula 배포: https://www.pa.uky.edu/~verner/photo.html . 기존 고정 factual H/He rows만 사용하며 source 자체의 재감사는 하지 않았다.

Rust 공식 rustc command-line 설명: https://doc.rust-lang.org/rustc/command-line-arguments.html . Minimal module compile은 whole-crate integration test와 별개의 범위다.

Repo 원전과 pin: SOURCE_BINDING.json. 외부 F04/F07 수신: CONCURRENT_SOURCE_ACK.json. 로컬 실행 원장: results/FINAL_VERIFICATION.json. 최종 게시·백업 identity는 별도 publication receipt를 따른다.
