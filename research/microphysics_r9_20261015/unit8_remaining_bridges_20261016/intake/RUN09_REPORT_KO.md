# RUN09: 동일 원자·기하 입력의 출생 광원 표본 세분

RUN08 다음 DAG `P4-S4C-SOURCE-SUPPORT-CONVERGENCE`의 출생시간 축을 실행했다. 시작일 2026-10-17, 샌드박스 전용. 원본 45-node/26-node DAG 와 실패 이력은 `provenance/RUN08.zip` 안의 조상 archive 에 보존했다.

## 판정과 요약

**PASS_SCOPED_NATIVE_BIRTH_SUPPORT_SCAN_NO_CONTINUUM_BOUND.** 원래 native graded GL4 panel 을 각각 r=1,2,4,6 개로 나눠 40, 80, 160, 240 개 출생시각을 만들고, 각 유한 광원에 대해 동일 retarded photon–H/He/D 공동 ODE 를 풀었다. 양의 가중치와 전체 48 셀·8 각도 support, BASS 기하와 원자자료 및 초기조건은 바꾸지 않았다. 네 source support 에 대한 7 개 수치 설정을 완료했다. r8 의 320 개 출생 packet 은 생성했지만 공동 계산이 outer 45 s 에서 중단돼 endpoint 가 없고 채택하지 않았다.

총 생성 광자수는 support 사이 binary64 수준에서 같지만, 생존수·종별 흡수·기체 상태의 차이는 같지 않다. r4→r6 의 더 엄격한 적분 비교에서 생존수 상대 차이는 3.47192e-11, HeI/HeII 흡수 상대 차이는-4.03399e-8/-3.25277e-8 이다. 이는 두 유한 근사의 차이이며 continuum 오차 상계가 아니다. Finest r6 는 진단용 reference 이지 연속 광원의 정확해가 아니다.

추가로 원전 GL4 remainder 를 적용한 선형 고정-opacity 상계와, GL4 순간 주입의 비선형 상태가 일반적으로 8 차 정확도를 갖지 않는 명시적 제조 반례를 유도·검산했다. 실제 우주론 결과에서 관측한 2.4 부근 등의 차수를 이 단순 반례의 계수와 동일시하지 않았다.

## 1. SSOT, 물리 입력과 독립성

- Parent archive SHA256: `d67ecd6d1f75b5617f6bcc05f8764779f9055eba977770c032db1372476f5b39`;198payload hashes 를 검증했다.
- RUN08 Git branch HEAD 를 현재 connector 로 확인: `8b61e9d733713a49bce3b28be2192ae5d7fe11bc`. 이전 원자 owner PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`를 다른 branch 의 최신 rate 로 조용히 교체하지 않았다.
- BASS121 SIGNED_MINUS, X=ln(a/a_ref), a_ref=1/21, X=.7.. .7004. 실제 source-only Einstein–Vlasov donor 의 a,b,H 와 고유시간 사용. 새 gas/photon stress 에 의한 Einstein 반작용은 없다.
- MD14_Z002_FESC_BB50K_13P6_100_V1, fesc=.2,13.6..100eV, original48cell mean,GL8 directions,original seed359.22363635035254,growth2. Original10graded panels 를 고정했다.
- 기존 Grackle/Verner/Savin/DAtomicProvider, H/He/D gas RHS, original chi and fit threshold guards, CMB bath2.7255/a K 를 유지했다.
- T0=10000K,HII=DII=.1,He4 charges(.8,.15,.05),D/H=2.5e-5,YHe=.245,D defect.0037eV 는 기존 제조 입력이다. REC donor/실측 isotope spectroscopy 또는 full17 nuclear network 를 채택한 것이 아니다.
- 기존 Rust 파일 81 개의 동일성을 확인했다. 이 중 lib.rs 는 기존 전체 내용 뒤에 RUN09 주석과 모듈 선언만 추가했고, 나머지 파일은 바이트 단위로 동일하다. 원본 owner 모듈 12 개도 이 집합에 포함된다. 기존 입력 파일 13 개와 retarded_integrator.py 및 gas_integrator_parent.py 두 개도 바이트 단위로 동일하다. 숫자는 `UNCHANGED_SOURCE_RUN09.json`으로 확인했다.

공동 ODE 와 native gas rate 는 원본을 재사용했다. 새 독립성은 출생 support construction, scalar MD14 시간모멘트 적분, MP60 제조 해, ODE tolerance 및 full/reflection representation 대조다. RUN08 의 Radau 대조는 보존된 근거이며 RUN09 의 새 support 를 Radau 로 다시 적분한 것은 아니다. 독립 연구자/native subagent 는 NOT_RUN 이다.

## 2. 시간적분 오차와 source support 오차

기하·에너지·각도 표본을 고정하고, 출생 quadrature 가 정한 양의 measure 를 mu_r 라 쓰자. 동일 유한 mu_r 에 대한 공동 ODE 해를 y_r, 수치 결과를 y_(r,tol)라 하면 관측량 차이는

O(y_(r,tol))-O(y_cont) = [O(y_(r,tol))-O(y_r)] + [O(y_r)-O(y_cont)].

첫 항은 유한 source 에 대한 solver 오차이고, 둘째 항에는 아직 모르는 연속 출생 근사 오차가 있다. 이번은 r 을 바꿀 때 각 y_r 를 먼저 공동 적분하고, r4/r6 에서 tolerance 만 바꿔 첫 항의 영향을 따로 진단한다. 두 tolerance 일치나 adjacent r 차이가 rigorous enclosure 가 되는 것은 아니다. 에너지·각도 continuum 은 이번 식에서 별도 고정된 근사다.

기존 초기 부피 기준 comoving 상태 Y=d n,U=d u,d=(a/a0)^3 와 코호트별 P_alpha=B_alpha exp(-tau_alpha)를 그대로 사용한다. t 는 s, E 와 chi 는 eV, n 은 proper m^-3 이며 c, k_B 와 1eV=1.602176634e-19J 를 유지한다. 이전 코호트의 birth a,b,mu,E 가 정하는 Killing ray, tau_X=(c/H)sum n_lower sigma(E), gas/photospecies 사건, 열에너지의 -2U, gas/photon geometric work 는 모두 RUN08 그대로다. photon source only 가 아니라 기체가 동적으로 반응하는 계산이다.

## 3. 새 native source refinement

남은 출생 수명 v=(t1-tb)/(t1-t0)에 대한 original panel [a,b]를

[a+j(b-a)/r, a+(j+1)(b-a)/r], j=0,...,r-1

로 분할하고 각 child 에 동일 positive GL4 를 사용한다. 각 새 node 의 실제 고유 출생시각 tb=t1-v dt 에서 원본 source_births(tb,dt*w)를 호출한다. source spectrum/angle label 과 optical seed 는 동일하다. 가중치 clipping, tail 제거,사후 정규화는 없다. r1 은 원본 emit_births 를 직접 호출해 arithmetic identity 를 보존한다.

원본 r1=(tb,Eb,mub,Ncom) tuple491520bytes 의 SHA256 `7d29d5c9dda88befd5141a9257170f70d96bcbd6937a2de14a159ac1e3d6a134`가 다시 일치했다. r2,r4,r6 는 30720,61440,92160 개 physical cohorts 를 갖는다. 원래 무틸트 LRS +/-mu exact reflection quotient 만 적용해 각각 15360,30720,46080 개 optical-depth groups 로 공동 적분했다. 각도 격자를 4 개로 근사한 것이 아니다.

새 API 는 source_support.rs 의 refined_panels,refined_birth_nodes,emit_refined_births 다. max_panels 는 최종 child panel 수까지 제한하며 subdivisions0/65 이상 또는 예산 초과를 거절한다. parent model/source files 는 수정하지 않았다. source_support_server.rs 는 parent exporter 에서 CLI subdivision 과 emitter 호출만 바꾼 생성 관계를 기록했다.

### 선형 고정-opacity GL4 상계

f(v)=exp(-tau v), tau>=0 에 대해 panel 폭 h 의 exact-arithmetic GL4 remainder 는

0 <= integral_a^b f-Q4 <= h(tau h)^8 exp(-tau a)/1778112000.

한 panel 을 r 등분하면 각 child 폭은 h/r 이고 exp(-tau a_child)<=exp(-tau a)이므로, child bound 합은 parent bound/r^8 이하이다. 이는 고정된 선형 kernel 의 상계이며 가변 gas feedback, moving threshold,nonlinear source-impulse solution 의 8 차 전역 정확도를 뜻하지 않는다. 실제 binary64 상계 계산을 outward-rounded interval certificate 라 부르지 않는다. NIST DLMF3.5 의 Gauss remainder 와 Wolfram 계수검산을 참조했다.

## 4. 광원 모멘트가 맞아도 비선형 상태는 다른 반례

차원 없는 별도 제조계 q'=1-q²,q(0)=0 를 사용했다. 연속 source 의 해는 q(t)=tanh(t)다. 하나의 길이 h panel 에서 GL4 nodes c_i,weights w_i 를 양의 순간 주입으로 적용하고, 주입 사이에는 정확한 q'= -q² 흐름 q→q/(1+q Delta t)를 사용한다.

C(u)=sum_(c_i<=u)w_i 라 두면 작은 h 에서

q_imp(h)=h-h³ integral_0^1 C(u)²du+O(h^5),
q_cont(h)=h-h³/3+O(h^5).

GL4 의 sum w_i c_i²=1/3 을 쓰면 integral u C(u)du=1/3 이다. 따라서

D=integral_0^1 [C(u)-u]²du=integral C²du-1/3>0,
q_imp-q_cont=-D h³+O(h^5).

D 가 양수인 것은 finite step CDF 가 연속함수 u 와 거의 모든 곳에서 같을 수 없기 때문이다. 실제 GL4 에 대해 MP60 값 D=.00679355009641720266306431556698428759404282650014975008358393. Local error/h³는 h=.1,.01,.001,.0001 에서-D 로 접근했고, global [0,1] panel16→32→64 에서 관측차수는 2 로 접근했다(최종 1.99994648). source 의 0..7 차 모멘트 residual 은 3.12e-61 이하였다.

이는 source moment exactness 만으로 nonlinear state 의 8 차 정확도를 주장할 수 없다는 구체적인 반례다. 실제 HHeD 의 2.44 등 관측차수를 이 toy 의 동일 계수나 universal order theorem 으로 해석하지 않는다. 일반 물리 no-go 또는 문헌상 novelty 주장은 없다.

## 5. 실제 source 의 independent scalar measure 검증

원본 axbi_sources.rs 의 MD14 comoving emissivity 식을 별도 Python 으로 옮기고, 기존 Python BASS dt/dX=1/H 에서 scalar 적분했다. Spectrum/angle 은 원본 fraction 합을 그대로 보존한다. 생성광자수 reference 는 6.006145028193166e-5 comoving m^-3 이며 모든 native packet 과의 상대차이는 최대 2.7190e-14 이다. Dimensionless elapsed proper time 의 0..7 모멘트 최대 상대차이는 1.8602e-11 이었다. 이 숫자에는 큰 elapsed-time 수의 차감과 원본 clock 보간의 유한 산술도 포함되므로 이를 GL4 truncation 만의 값으로 부르지 않는다.

Normalized cumulative source CDF 의 최대 차이는 40/80/160/240births 에서 각각.0605722/.0302885/.0151448/.0100967 이었다. 이 normalization 은 진단용이며 physical packet 을 재정규화하지 않았다. 총 질량·모멘트 일치와 source 가 실제 주입되는 시간순서의 근사가 다르다는 것을 정량화한다. CDF 오차를 특정 관측량의 직접 오차 상계로 승격하지 않는다.

## 6. 실제 공동 적분 결과

네 support(r1,2,4,6)의 paired DOP853(rtol3e-11), r4/r6 의 tight3e-12, r2 의 full 3e-12 와 paired 3e-11 대조는 표현과 허용오차가 동시에 다르므로, 순수한 표현 오차라고 부르지 않는다. Reflection 의 수학적 동일성과 parent RUN08 의 Radau 대조를 재사용했고, 새 support 의 ray parity 와 count 를 회귀 검사했다.

세 점 기반 진단에서 생존수는 r2, r4, r6 의 power-law fit 약 8.04, T·H I·He I 는 약 2.44–2.45 였다. 이는 서로 다른 양의 현저히 다른 거동을 보여주지만, 거친 격자의 fit 을 정확한 점근 차수나 Richardson 오차 상계로 쓰지 않는다. 모든 누적 사건이 같은 차수에 도달했다고 주장하지 않았다.

일곱 설정의 최대 회계 잔차는 광자수 2.2901e-11, 초기 에너지 기준 2.9639e-14, 주입 에너지 기준 1.6446e-11, H 종별 사건 검사 9.9920e-16 이다. 가장 세밀한 r6 의 tight 결과에서는 광자수 3.9992e-12, 주입 에너지 기준 3.2619e-12 였다. 보존 잔차를 상태 정확도의 대용으로 사용하지 않는다.

## 7. 중단, 실제 비용과 검증

r8 의 122,880 개 physical cohort, 320 개 출생시각 packet 은 성공적으로 생성했지만 공동 적분은 outer 45 s 한도에서 중단됐다. Endpoint 와 result.json, 완료된 process RSS 기록은 없다. 점검 시 살아 있는 solver process 도 없었다. 이 경로의 결과는 모든 채택 통계에서 제외했으며 같은 실행을 반복하지 않았다. r6 은 더 작은 별도 support 로 범위를 좁힌 실행이다. 원래 source 나 물리 입력, 수락 기준을 바꿔 강제로 통과시키지 않았다.

완료된 일곱 설정의 solver 내부 실행시간 합은 88.286589333 s 다. Export, 입력 검사, Python 준비, 설치·컴파일·시험, 중단, 복원 시간은 제외한다. r4 의 standard/tight 완료 process 시간은 14.06/15.13 s, r6 은 23.03/26.49 s 였다. 완료된 실행의 최대 process RSS 는 1,269,668 KiB, 약 1.21 GiB 다. r8 중단 후의 memory.current 약 2.7 GiB 는 cache 를 포함한 시점값이며 process peak 라고 보고하지 않는다. 계산은 4 GiB 샌드박스에서 Cargo build job 1, BLAS thread 1 로 수행했다.

Rust 테스트는 151/151, 기존 145 개와 신규 6 개가 통과했다. Python 은 신규 7 개와 기존 8 개가 통과했다. Strict Clippy 와 신규 코드에 한정한 rustfmt 검사도 통과했다. 핵심 subdivision 기능에서는 예상한 80 개 대신 40 개 node 가 반환되는 실패를 실제 관측한 뒤 구현해 통과시켰다. 다른 회귀까지 모두 TDD 였다고 주장하지 않는다. 최초 시험의 모호한 부동소수점 타입 compile error 와 새 Python 시험의 미닫힌 파일 ResourceWarning 을 보존했고, 각각 명시적 f64 및 Path.read_text 로 교정했다. 원자 rate 나 허용오차 수락 기준을 완화한 것은 아니다.

최종 full archive 의 복원 검증은 별도 새 디렉터리에서 manifest, source identity, build, tests, lint 및 대표 r2 paired joint endpoint 재실행으로 구성한다. 실제 종료코드와 일치 여부는 archive 밖 DELIVERY_RECEIPT.json 에 기록한다. 이 보고서의 복원 절차 설명은 실행 영수증을 대신하지 않는다. 전체 일곱 설정을 clean restore 에서 반복한다는 계약은 아니다. 최종 업로드한 ZIP 에는 자신의 hash 나 새 원격 객체 ID 를 다시 삽입하지 않는다.

## 8. 다음 최소 과학 작업과 보존

다음 노드는 **P4-S4C-SPECTRAL-EDGE-SUPPORT**다. r4 출생 표본은 r6 과의 관측 차이 및 실제 비용을 근거로 선택한 제한된 작업 입력이며, 절대 오차가 인증된 값은 아니다. 우선 H/D 문턱을 포함한 원래 첫 source cell 만 양의 에너지 구적법으로 세분해 공동 적분하고, 종별 사건·가열·생존수를 비교한다. 전체 147 개 spectral node 를 즉시 모든 출생·각도와 곱해 자원을 소모하지 않는다. 셀별 광자수는 유지하되, 에너지 모멘트와 문턱 교차가 어떻게 바뀌는지 별도로 기록해야 한다. 스펙트럼 세분 효과가 이번 r4/r6 출생 표본 차이와 비슷해질 때는 r6 출생 표본을 대조로 추가한다.

연속 출생의 엄밀한 오차 상계, 전체 spectral/angular continuum, 전체 donor 구간, Einstein reaction feedback, full EoR, FLRW-CONV, BI-SIGNED, ISO-COUPLE full 과 미완료 Li/Be/nuclear T1–T8 은 HOLD 다. 원본 45-node·26-node DAG 는 조상 archive 에서 보존한다.

매 연구 턴의 GitHub 실제 소스 변경분과 Drive·Dropbox 전체 백업을 수행하는 사용자 지시는 유지한다. 실제 새 객체 ID 와 업로드·hash 대조·재다운로드·실행 복원 수준은 외부 전달 영수증이 권위다. 본 보고서에는 원격 저장 성공을 선기입하지 않는다. 사용자 local/Codex/NCP/SSH 와 native independent actor 실행은 NOT_RUN 이다.

문헌과 CAS 의 역할은 LITERATURE_AND_CAS.md, 실제 수치는 evidence/, 변경 없는 물리 소스는 contracts/UNCHANGED_SOURCE_RUN09.json, 각 source packet 은 inputs/refined/r*.identity.json 에서 추적한다.
