# REI_G2B_SAVED_ENDPOINT_OWNER_BOUND

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION
WORK_THREAD_REQUIRED=false

## 목적과 고정 기준

전체 source-input tube를 다시 찾는 감사 루프가 아니다. 이번 목적은 이미 있는
두 NPZ의 실제 수치를 소비해 **G2b의 단일 endpoint 부분 경계**를 계산하는 것이다.
현재 결과를 담는 immutable Git 링크의 commit을 intake head로 읽고,
PROOF_AND_SCOPE.md와 RESULT_AND_INPUTS.json을 먼저 읽어라.
데이터/기존 소스의 기준은 parent `1244fa97b8e854ae0ced40f306cb41f28232800d`,
tree `581e304bd0aaefe784d88d5ac4f1f9494780eeed`다.
동일 endpoint 작업의 더 새 반환이 있으면 먼저 재사용하고 중복 실행하지 말라.
PR #77 O01--O10은 이미 10/10이며 다시 실행하지 않는다.

## 읽을 실제 입력

RESULT_AND_INPUTS.json의 CROSS/INITIAL/FORCING alias를 정확한 경로로 해석한다.

1. CROSS/data/VALIDATED_PUBLIC_BOXES.npz
   blob 8f67740b43c82be04f8efd521990b7b2b185afea
   선택: LOCAL_NEUTRAL_HAZARD_PRIMARY__lower / __upper, shape(4,46080).
   좌표: x_HII,x_HeII,x_HeIII,log_T. 다른 lane은 계산하지 않는다.
2. INITIAL/data/initial_material_state_z6.npz
   blob e3a2a55f1187e958276193d7368541ca11197c31
   N_HI,N_HII,N_HeI,N_HeII,N_HeIII 및 필요한 식별 필드만 읽는다.
3. FORCING/data/atomic_moments/verner_gray_and_limit_moments.csv
   blob 572a8b6d8de7fd861745047eaaba169a177aeff3.
4. 원래 G2b current의 첫 두 forcing knots는 RESULT_AND_INPUTS에 있다.
   실수 PCHIP cell hull의 보수적 상한 J_G2b<=1.4e48 box photons/s를
   사용하면 source PCHIP를 새로 실행할 필요가 없다. 원 표와 대조한다.

production 모듈은 import하지 않는다. NPZ reader는 allow_pickle=False로
사용하고 bytes와 배열 의미를 모두 확인하라. 파일명/헤더만 읽고 끝내지 말라.
이미 보존된 원본 배열과 로그를 수정하지 않는다. 무관한 패키지/host census는 없다.

## 수행할 수학·계산

고정 node totals h_i,he_i와 global totals H_H,H_He의 의미를 producer와 맞춘다.
원래 source의 binary64 합계와 exact-real 합계를 구별하여 기록한다. metadata의
nominal decimal total을 아무 확인 없이 exact sum으로 사용하지 않는다.
필요하면 동일한 고정 수치들을 exact binary rational로 해석한 연구 모델임을
명시한다. byte equality만으로 physical/source-semantic equality를 주장하지 않는다.

public fractions에서

    u_HI,i = (h_i/H_H)*(1-x_HII,i)
    u_HeI,i = (he_i/H_He)*(1-x_HeII,i-x_HeIII,i)

를 재구성한다. 독립 box가 HeII/HeIII anticorrelation을 잃어도 positive floor로
수리하지 말라. fixed-simplex 제약과 실제 저장된 추가 population enclosure를
쓰려면 그 provenance와 포함 방향을 명시한다. 실제 저장되지 않은 stage 배열을
추측하거나 원래 producer를 돌려 재생성하지 않는다.

q_HI=NH0*MPC_CM*sigma_HI,G2b,
q_HeI=NH0*YHE*MPC_CM*sigma_HeI,G2b,
D=sum_i(q_HI*u_HI,i+q_HeI*u_HeI,i).

소스의 node weight는 N에 이미 포함돼 있다. 두 번 곱하지 않는다.
G2b는 e=0이므로 (1+z)^2가 분자/분모에서 정확히 상쇄된다. 따라서 이
state-only 경계 계산에 가짜 z/tangent 입력을 만들지 않는다.

정확한 Fraction 산술 또는 실제 directed-rounding 산술로 D_lower를 계산한다.
중간 float 연산 뒤 마지막 nextafter만 붙인 결과를 인증으로 취급하지 않는다.
부득이한 표시용 float 변환과 계산 경계를 분리한다. 상속 pchip_bounds helper의
일반 rounding 주장은 이번 증명의 전제가 될 수 없다.

D_lower>0이면

    L_G2b <= 2*Jmax*max(q_HI,q_HeI)/D_lower

및 가능하면 current component enclosures를 반환한다. 이는 고정 endpoint
입력집합에 대한 조건부 실수식 경계이며, 그 endpoint를 만든 discrete solver,
whole-step/whole-trajectory enclosure 또는 Rust production의 신규 인증이 아니다.
D_lower<=0이면 부호·최소 neutral margin·최악 node와 합계의 실제 수치를 보존하고
ENDPOINT_REPRESENTATION_INSUFFICIENT를 반환한다. 이는 물리적 중성량이 음수거나
실제 source가 발산했다는 뜻이 아니다. 읽기/환경 오류와 구별한다.

source-site는 보존된 두 half-step 중 second-half thermal_t1_final의 population
input이다. t=duration(0)/2048, half interval=[duration/4096,duration/2048].
다른 source site 또는 연속시간 tube로 확대하지 않는다. saved public-box의
포함성 자체는 과거 근거에 조건부임을 명시하며, 이 계산만으로 재인증하지 않는다.

## 작은 검사와 반환

실행 가능한 작은 연구용 consumer만 이 새 research directory 아래에 추가한다.
구현 전에 새 입력/부호/범위 검사를 만들고 실제 결과를 보존한다. 범위 내 오류는
증거를 남기며 자율 수정한다. 기존 성공 suite를 회귀라는 이유로 다시 돌리지 않는다.
최소 새 검사는 positive D case, nonpositive lower-bound case, fixed-totals/no-double-weight,
source group mask 및 위 normalized-current derivative의 독립 rational 예다.
정적 rounding 반례를 실행 검산하려면 해당 helper 함수만 isolated namespace에
읽어 검사하고 scalar imports만 사용한다. 전체 package import나 production 실행이
아니다. 이를 실제로 하지 않았다면 NOT_RUN으로 남긴다.

가능한 runtime에서 endpoint neutral margins와 D contributions를 나타내는
그림을 생성하고 직접 읽어라. 수치적 경계 증명은 샘플 plot로 대체하지 않는다.
실행하지 못한 plot/CAS를 완료했다고 쓰지 않는다.

반환: exact source/input identities, 사용한 normalization·산술, 실제 command/exit/
timeout/stdout/stderr, 각 새 검사 결과, D_lower와 conditional L 또는 정확한 부족
원인, 같은 assistant의 순차 수학/코드 검토 여부, 변경 파일 목록.
증거와 executable source commit을 구분한다. Git 일반 텍스트 결과 및 고정 handoff
링크를 REI-only non-force child/Draft에 게시하고 직접 main conversation으로 반환한다.
출처가 분명한 작은 기존 데이터 계산이 목적이며, 새 governance framework는 만들지 않는다.

## 금지와 불변

O01--O10 및 #73--#76 replay, 새 GitHub Actions workflow/dispatch/re-run,
BG02/native/GCC/XZ/Ubuntu Snapshot, 설치/rootfs/provider census,
BASS/REC/HTT repository 접근/변경, production imports/locks/Section-0/attempt refs/
leases/controllers/workers, canonical pilot/first interval, ready/merge/forcepush 금지.
게시 commit에는 [skip ci]. 기존 y0 RHS, y0/y0/yp 분모, (F0+F1)/2,
네 independent sites, source의 HeII/H 규약 및 exhausted one-shot budget는 보존한다.
전체 OTS/원자율·thermal inverse·exact-flow rho·provider는 이번 목표가 아니다.
이 파일 게시만으로 local process를 자동 실행했다고 하지 않는다.
