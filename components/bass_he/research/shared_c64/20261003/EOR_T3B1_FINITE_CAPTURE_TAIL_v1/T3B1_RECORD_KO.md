# BASS_HE EOR_T3B1: 유한 포획 bundle의 적분 가능한 tail

날짜: 2026-10-03 KST.
판정: FINITE_A1B6_CAPTURE_TAIL_DERIVED_AND_REFERENCE_TESTED__FULLSPACE_TRANSFER_OPEN.

첨부 T3A에서 요청한 첫 bounded substep을 수행했다. A1b의 H1s;He1s,2s,2px,2py,2pz 여섯 ETF orbital Galerkin 모형에서 공간적 국소화를 이용한 명시적 offblock 상수, 모든 차수 unitary transition bound와 큰-impact area tail을 유도했다. full P+Q Coulomb 포획, 모든 bound states, continuum, 실제 재이온화 정확도의 인증은 아니다. 원 ARSENY 재현이나 전체 프로젝트 종료를 주장하지 않는다.

## 입력과 배포 identity

과학적 부모: BASS_HE_EOR_T3A_APPLICABILITY_20261003_v1.zip
bytes: 1883177
SHA256: 75e51b287729b9c65a3f80c7217d36b4e99a570ba32bc20603ff27ae863caf4e
74개 parent payload를 실제 확인했다. A1b 원문 SHA256 99e97891c6c7a52e24a8dcabbf70afc00a2525701a6fa4d4e1438886de5dea05를 재사용했다. 기존 scientific suite는 반복하지 않았다.

새 완전한 실행 묶음: BASS_HE_EOR_T3B1_FINITE_CAPTURE_TAIL_20261003_v1.zip
bytes: 1958535
SHA256: 1b3679da446f7c76de0179c756d115baefff53295f1e4802a797fd251ba8edc2
65개 entry,64개 manifest payload. parent 원본 bytes를 포함한다.

게시 직전 remote HEAD f391ab9330e1753fa010be814ac9fa5d7d3e4bac의 별도 T3 record를 읽었다. 그 조건부 trajectory/power-tail 결과와 다음 T4 일정은 보존한다. 그 sibling archive나70개 과거 tests를 새로 회수/재실행한 것으로 세지 않는다. 이 게시물은 같은 branch에 추가되며 기존 내용을 덮어쓰지 않는다.

## 실제 유도

전자 단위 x=r/a_A,tau=t E_A/hbar, v 단위 a_A E_A/hbar. ZA=1,ZB=2, electron m_e와 infinite-nuclear-mass electronic energy, zero center acceleration 및 R=sqrt(b^2+v^2 tau^2)를 유지한다.

u=H1s, V=He의5개 ETF 열, s=V†u,d=sqrt(1-s†s),y=(u-Vs)/d. 물리 유한 projector Pi_B=VV†를 보존하고 Y=[y,V]로 직교화한다. finite 시작시각의 실제 u 좌표는(d,s)이며(1,0,...,0)이 아니다.

A1b의 F_B=(h-i∂tau)V=(-1/r_A+1/R)V를 사용하면 K_AB=[u†F_B-s†(V†F_B)]/d다. 빠진 connection을 사후 symmetrization으로 감추지 않는다. 내부 B unitary gauge에 offblock norm은 불변이다.

0<lambda<1에서 weighted orbital norm은 U²=(1-lambda)^-3, Uinv²=2/(1-lambda), V1s²=8/(2-lambda)^3, V2s²=(1+lambda+lambda²)/(1-lambda)^5, 각 V2p²=(1-lambda)^-5, bare-gradient Frobenius G²=8이다. Vlambda²는5개 norm 제곱의 합이다.

S0=U Vlambda, 0<c<1, B0=log(S0/c)/lambda,
C=Vlambda[Uinv+2UG+U(1+sqrt(5))/B0]/sqrt(1-c²).

삼각부등식 r_A+r_B>=R, Cauchy-Schwarz와 Hardy inequality로 R>=B0에서 ||K_AB||<=C exp(-lambda R)를 얻는다. lambda=c=1/2의 binary64 표시는 B0=8.5050906202286,C=273.67976203068514다. 데이터에 맞춘 상수가 아니며 B0는 이 증명의 충분조건이지 실제 물리 cutoff가 아니다.

A/B 내부 evolution을 정확히 유지한 block interaction picture의 Duhamel bound로 sqrt(p_B,6)<=min(1,2Cb K1(lambda b)/v). 이는 Born 일차근사가 아니고 energy defect 분모를 사용하지 않아 H1s-He n2 축퇴에도 성립한다.

DLMF10.32.8/.9 적분표현에서 sqrt(1+q/2)<=1+q/4를 적용해 K1(z)<=sqrt(pi/(2z))exp(-z)(1+3/(8z)), 모든 z>0의 전역 상한을 유도했다. 따라서 B>=B0에서

Sigma_B,6(B)<=4pi² C²/(lambda v²) exp(-2lambda B)[B²/(2lambda)+7B/(8lambda²)+65/(128lambda³)].

우변은 a_A² 단위다. 유한 v>0의 유한모형 tail이며 v→0의 thermal uniform bound는 아니다. finite-time B5 population에는 |p'_B|<=||K_AB||, physical u와 star y의 준비 오차에는 sqrt(2)||s||/sqrt(1+sqrt(1-||s||²))를 사용한다. B 내부 shell mixing의 시간오차까지 같은 bound로 승인하지 않는다.

full Coulomb로 옮기는 조건은 별도다. 같은 점근 B5 amplitude 공간에서 ||a_full-a_6||<=e_B이면 sqrt(Sigma_full)<=sqrt(Sigma_6)+sqrt(E_B), E_B=2pi∫_B^∞ b e_B²db다. e_B<=D(bref/b)^r에는 r>1이 충분하지만 실제 e_B 상한은 아직 없다. Q-mediated capture와 infinite-n summability의 정확한 제조 반례도 포함했다. finite bundle을 all-bound/continuum으로 바꾸지 않는다. R_CX는 별도 source이며 무복사 norm loss로 생성하지 않는다.

## 실제 검증과 구현 범위

65 focused tests passed.26개는 assertion red 후 green,39개는 구현 후 검증이다. 첫 simple Minkowski oracle의 rounding 문제와 runner의 --out 경로 미반영 실패를 보존하고 수정했다. 테스트 tolerance는 완화하지 않았다.

6개의 generic3x3 Hermitian pulse를 DOP853로 검사했다. commuting exact sin²에 대한 최대차2.151723244026016e-12, norm defect최대1.2581280461887445e-10. 원자 공간 적분이나 실제 분자 collision이 아니다. Wolfram은 weighted radial norms/area antiderivative/대수 항등식을 경고 없이 확인했다. 독립 심사가 아니다.

정상 CLI exit0/physical_certificate=false, physical request 및 동일output 덮어쓰기 exit2. binary64 underflow를0으로 숨기지 않는다. 봉인ZIP을 새 폴더에 풀어65개 tests를 다시 통과했고64개 payload와 parent74개 hash도 실행 뒤 일치했다. 의도적 임시 payload 변경을 검사기가 exit2로 검출했고 원본 bytes를 복원했다.

stdlib bound/CLI, NumPy frame, SciPy test-reference, manifest검사기와 complete run/return handoff를 제공한다. 전체 molecular spatial quadrature/scattering/continuum/production rate solver는 뒤의 I1-I4에서 이 대화 안에 구현할 대상이다. 새 molecular solve,physical sigma/k,Bianchi history,Fortran build,MPI,독립심사는0/NOT_RUN이다.

실측CPU quota4cores,affinity5logical CPUs,memory4GiB. binary64/complex128,no-fast-math,no-reassociation,no hidden mixed precision,explicit backend 유지. NCP에는 큰 수렴과 actual host optimization을 남긴다.

## Source와 다음 단계

DLMF의 K1 적분표현, Liu et al. CPB33(2024)083401 DOI10.1088/1674-1056/ad5322의 primary publisher 자료를 확인했다. publisher data-availability 검색에서 DOI10.57760/sciencedb.j00113.00114를 발견했지만 raw data/uncertainty/channel/license는 아직 확인하지 않아 NOT_ADMITTED다. 문헌을 본 정리의 full-Coulomb certificate로 쓰지 않는다.

다음 단일 node: EOR_T4_RATE_EVENT_ENERGY_AND_BIANCHI_INTERFACE. 원 C0 typed theory readiness를 소비하며 full T3 물리완료를 기다려야 하는 새 의존성을 만들지 않는다. full-Q/high-n/continuum은 GAP_MATRIX의 OPEN으로 남긴다.

C0 physical_ready=false; EOR_T3_whole_complete=false; EOR_THEORY_GATE=NOT_SATISFIED; independent_review=NOT_RUN; scientific_PROMOTE=HOLD; full_C2/continuum/full_H_gap/atomic_correlation=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

## 게시 의미

이 Git 파일은 additive 연구·검증·archive identity 기록이다. 완전한 제품 source/tests/math/contracts/부모원본은 SHA-bound ZIP에 있고 개별파일 전체를 Git에 게시한 것은 아니다. 승인된 Drive/Dropbox/Library 업로드의 실제 object ID,size,ACK 및 최종 commit/tree는 detached DELIVERY_RECEIPT가 소유한다. 원 source PDFs를 공개하지 않는다. 로컬 archive replay와 새 remote restore는 구분한다.
