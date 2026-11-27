# HE31: H/He electron donor와 prepared canonical FV moments

## 목표와 source authority

HE30의 완료된 237개 z=20→2 궤적은 그대로 재사용한다. 이 단위는 다음 기능을
실제 코드와 경량 검증으로 완성한다.

1. H/He 이온분율과 핵 밀도에서 proper electron density를 구성하고, 단위·물리
   구간·입력 SHA를 검사하는 불변 donor.
2. 기존 PR147 full40 CanonicalFVSpecies의 photon-only Thomson hook에 donor를
   연결하는 실행기. massive matter / photon / neutrino의 signed stress를 각각 저장한다.
3. 같은 canonical FV quadrature의 고정 운동량·가중치를 준비하여 매 RHS의
   임시 배열과 반복 연산을 줄이는 binary64 evaluator.
4. 원래 solver·단위·초기 좌표를 보존한 작은 검사, 실제 donor control, resource-aware
   NCP 실행·재개·그림 코드, Git 게시와 독립 백업.

기준 BASS_HE snapshot은 `e173f373cd481864d0395e3a7a76520615a80e1a`이다.
solver 과학 계보는 rei_bianchi PR147
`3b85dedce84d37b3e165da00685a8a984950aafe`이며, 이 저장소의
`research/he29_rei_pilot_20261021/vendor/`에 보존된 세 원본을 변경하지 않는다.
HE30 공유 실행기의 CPU/quota/memory/lease 정책을 함수 API로 재사용한다.

## 물리·수치 계약

`a`는 평균 부피 scale factor, `x=ln(a/a_ref)`, proper time은 초다.
`D=diag(-1,-1,2)`, `sigma=s D`, `pi_X=p_X D`이다.
`Sigma_F=sqrt(6)|s|/H`, `P_X=(8 pi G/c²)sqrt(6)p_X/H²`, `Pi_X=|P_X|`.
`P_rad=P_gamma+P_nu`; `Pi_total=|P_m+P_rad|`를 사용한다.
massive matter는 원래의 비바리온 collisionless fraction fm=.1, m/Tref=30이다.
electron donor의 baryonic nuclei와 massive matter sector를 동일시하지 않는다.

전자 census는 `ne=nH*xHII+nHe*(xHeII+2*xHeIII)`다. 단위와 proper/comoving
구분은 입력 manifest에 필수다. 균질 보존 핵에 대해 a³nH, a³nHe의 일관성을
검사한다. 새 보간은 `ln(a)`에서 comoving ne의 PCHIP이며, knot 값과 영값,
비음수성과 핵당 전자 수의 상한을 보존한다. 입력 지지 구간 밖은 거절한다.
허용하는 endpoint 교정은 명시한 binary64 roundoff 이내의 경계 반올림뿐이다.

Thomson rate는 기존 solver 상수 그대로 `GammaT=c_cgs sigmaT_cm² ne_cm^-3`이고,
log-scale clock의 rate는 `GammaT/H`다. photon energy/number multipole만 직접
충돌항을 받는다. 기존 unpolarized scalar closure의 coefficient는
`(0,1,9/10,1,...)`이다. polarization 생성과 재결합을 포함하는 확장은 별도 모델이다.
donor는 일방향 prescribed input이며 자신의 화학을 새 Bianchi 해에 되먹이지 않는다.

기본 resolution은 기존 nominal L=8, 24×12 cells, Gauss3, DOP853
rtol=3e-11, atol=3e-13이다. 경량 검사는 이 계약의 영향 범위만 다룬다.
상세 성능 benchmark, 완료된 237-case sweep의 재실행은 이번 단위에 필요하지 않다.

## 실제 donor 범위와 완료 기준

조사에서 확인한 native H/He 및 B1 R15/HG97-B actual history는 z=20→4이다.
기존 source generator에도 z>=4 guard가 있다. 원본의 guard나 source identity를
바꿔 z=2 donor가 존재한다고 기록하지 않는다. 이 단위는 실제20→4 donor를
재사용한 검증과, 실제20→2 입력이 들어오면 추가 구현 없이 실행 가능한 consumer를
완성한다. manufactured20→2 input은 계약 시험에서만 사용한다.

NCP에 넘길 것은 고정 source/input/config, 실행 명령과 반환 계약이다. 그곳에서
문헌 조사나 알고리즘 재작성은 필요하지 않다. 실제 z=2 H/He source의 채택·생성은
구체적으로 기록할 다음 연구 의존성이고 기존 HE30 z=2 그림의 완료를 변경하지 않는다.

## 운영과 근거

다른 세션이 실행 중이어도 관측된 가용 자원으로 독립 사례를 실행한다. max64,
reserve2 CPU/16GiB, native threads1, 공통 CPU/case lease와 실제 cgroup 제한을
사용한다. 실패/부분 결과를 보존하고 성공 identity만 재사용한다.
단계별 산출물은 DAG와 ledger에 연결하고 같은 의미 있는 snapshot을 여러
단계가 공유할 수 있다. Git commit과 백업 provider ACK를 과학 검증과 구별한다.
