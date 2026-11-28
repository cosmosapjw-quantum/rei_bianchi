# HE-RCT-STEP01-ADDON: 실제 FT03를 호출하는 별도 정적 RCT 적분 모듈

## 판정 및 범위

`SCOPED_ADDON_NATIVE_PASS__OWNER_ADOPTION_PENDING`. 이전 설계의 C1–C4를 별도 `bass_he_rct_step_addon` Rust crate로 구현하고 실제 컴파일·실행했다. 원자율·기준값을 새로 맞추지 않았다. F08 담당 소스 예약을 침범하지 않도록 원 `ft03_controlled.rs`, `he_rct.rs`, `coupled_primary.rs`, 원 dispatcher와 원격 소비기 저장소를 수정하지 않았다. 이것은 실제 기존 FT03/RCT 함수를 의존성으로 호출하는 실행 가능한 확장 모듈이지, owner의 배포 경로가 변경됐다는 뜻은 아니다.

공급자 입력은 BASS_HE `07256778a02a18cbd796477f393c3d8dd6c3b9e4`, 관측 소비기 입력은 `8e8ea0c664e2ba2f2f8560e0c64266d206fbd50f`다. 실제 빌드 의존성은 원 native commit `41e4592aa494b48929dcd23fc8504c169a98a908`의 full crate다. 이전 REI-HE-RCT01 ZIP을 Drive에서 실제 복원해 SHA256을 맞추고, 그 FILE_MANIFEST의 vendor34개 파일을 전부 대조했다. 현재 읽은 ft03/he_rct blob는 그 복원 파일과 같지만 최신 전체 crate 또는 F08를 빌드하지는 않았다. `INPUT_PIN.json`과 `inputs/VENDOR_SHA256.json`이 그 차이를 보존한다.

## 구현

`implicit_step`에서 OFF는 실제 기존 `ft03_implicit_step`에 직접 위임한다. 새 활성 경로는 고정 proper nH,nHe>0, 단일 선택 원자율과 고정 평균 탈출 광자에너지 Ebar를 요구한다. `RctSelection`이 attempt 전체에 같은 Copy 값으로 전달되므로 full/half 사이에 source나 Ebar를 자동 변경하지 않는다.

활성 블록은 기존 양성 생멸 갱신에 다음 두 유효율을 추가한다.

    I_H_eff = I_H + k*nHe*z_guess
    D_HeIII_eff = D_HeIII + k*nH*(1-x_guess)

전자밀도를 추가로 곱하지 않는다. 광자 감소·RR·CI·DR는 원 FT03 계수를 사용한다. 후보 thermal/escape와 최종 endpoint 잔차는 모두 실제 `combined_ft03_rhs`를 호출한다. 원 source의 private helper를 수정하거나 공개로 바꾸지 않고, 외부 crate가 공개 데이터/API를 이용하는 최소 블록과 장부 검사를 구현했다. 원 물리 함수의 복사·재구현으로 검증 대상을 대체하지 않았다.

최종 endpoint 하나에서 J=dt*R를 만들고 종별 수지에 +J,+J,-J를 적용한다. 여기서 RCT는 RR/DR와 별도다. `RctIntegral`은 proper cm^-3 단위 사건수와 erg cm^-3 단위 heat, escape, chemical을 함께 담는다. 이 escape closure에서 방출·탈출 광자수는 같은 events이고 tracked-photon injection은0이다. 이 0은 source의 미지 모멘트를 채운 것이 아니다.

`adaptive_step`은 full과 두 half를 계산한 뒤 half1+half2 사건을 채택하고 full candidate 장부를 버린다. `try_adaptive_step`은 상태와 외부 누적장부의 새 값이 모두 유효할 때만 두 값을 commit한다. source-temperature 오류, 미수렴, 사건수 예산 실패, 잘못된 accumulator에서는 상태·장부가 바뀌지 않는 시험을 포함한다.

## 새 수치 결정: 사건수와 상태 오차를 분리

기존 default residual1e-14/max_iterations80, strict local error<2e-4, 물리적 변수의 floor1e-30, 원 invariant criterion을 유지했다. 새 사건수 검사는 다음과 같다.

    eJ = |J_full-(J_half1+J_half2)|/nH
    allowance = aJ + rJ*max(|J_full|,|J_half1+J_half2|)/nH
    eJ <= allowance 이면 사건수 gate 충족

EventControl에는 숨은 default가 없다. 이번 사전기록한 exploratory 실험값은 aJ=1e-14 events/H, rJ=2e-4다. parent/owner가 이 신규 예산을 이미 수락했다는 뜻은 아니다. 이 추가 gate는 기존 상태 gate를 대체하거나 느슨하게 하지 않는다. Step doubling은 exact ODE 오차의 엄밀한 enclosure가 아니다.

실제 T0=50000K, nH=1e-4, nHe=8.3e-6 cm^-3, fractions=(.9,.3,.6), fixed photon20/35/70eV, KF96 k=1e-14 조건에서 다음을 관측했다. Ebar=Q는 가열0인 합성 검증 입력이지 원자 광자 에너지의 예측값이 아니다.

| dt [s] | 기존 상태 차이 | eJ [events/H] | 허용 사건수 차이 | 결과 |
|---|---:|---:|---:|---|
| 1e8 | 9.55475699e-11 | 4.98798878e-18 | 1.00995970e-14 | 채택 |
| 1e9 | 9.53441104e-9 | 4.97944752e-16 | 1.09957009e-14 | 채택 |
| 1e10 | 9.33461502e-7 | 4.89543404e-14 | 1.99302549e-14 | RCT_EVENT_LOCAL_ERROR |
| 1e11 | 7.65501039e-5 | 4.17553292e-12 | 1.06782611e-13 | RCT_EVENT_LOCAL_ERROR |

네 상태 차이는 모두 기존2e-4보다 작지만 뒤 두 사건수 차이는 신규 예산의 약2.46배·39.1배다. 즉 작은 RCT 반응의 누적 사건을 제어하려면 상태변수의 기존 오차 기준만으로는 이 선택된 사건수 기준을 만족한다고 할 수 없다. 이는 실제 원자율의 중요도나 전체 재이온화 효과의 판정은 아니다.

## Underflow의 한정적 해결

기존 `RctProvider::closed_events`의 결과를 실제로 사용하되, 그 rate/chemical/heat/escape 및 dt-event 곱의 nonzero factors가0으로 떨어지면 새로운 경계에서 `RCT_PRODUCT_UNDERFLOW`로 거절한다. 물리적0인 반응물·채널은 계속0을 반환한다. overflow·비유한 입력도 별도 오류다. 이 wrapper는 원 provider 코드를 변경하지 않는다.

이는 직접 검사한 zero-product representability 조건이다. 모든 subnormal 상대오차, 작은 항의 덧셈 소실, 모든 중간 연산 또는 임의 영역의 균일 반올림 인증은 아니다. 정상적인0과 underflow0의 구분을 수치계약으로 추가한 것이며 물리 source의 미지값을0으로 만들지 않는다.

## 실제 검증과 실패 보존

먼저 8개 공개 API 시험에서 stub의 ADDON_NOT_IMPLEMENTED로 예상 assertion 실패를 확인했다. 구현 후 첫 실행에서는7개가 통과하고, dt1e10을 성공으로 예상한 half 합산 시험1개가 RCT_EVENT_LOCAL_ERROR로 실패했다. 별도 probe에서 eJ/allowance=2.45628임을 측정해 신규 gate가 올바르게 거절한다는 점을 확인했다. 허용치를 바꾸지 않고 성공 장부 시험을 dt1e9로 옮겼으며, 원dt1e10은 명시적 거절 회귀검사로 추가했다. 최초 시험과 로그는 보존했다. 이 수정은 물리모형 또는 허용오차 수정이 아니라 시험의 입력·기대값 오류 수정이다.

최종 native suite는15시험(단위2+통합13) 통과, warnings-as-errors build 통과, rustfmt 검사 통과다. 이 15개는 새 add-on의 시험이며 기존116개·mixed2/274·F04/F05 과학시험을 재실행한 것이 아니다. 기존 HE-F2C `rct_reference.py` 원문 bytes를 재사용해, 동일한 positive species 블록의 isolated RCT6입력을 원래 BE 기준해와 대조했다. 이 isolated block 검사는 full FT03에서 다른 반응을 제거했다는 주장과 구분된다.

probe는 dt4개와 Ebar=Q-1,Q,Q+1의3합성 입력으로12개 implicit 시나리오와 full/half1/half2 총36끝점을 기록했다. 동일 시나리오의 adaptive 판정은6채택·6거절이다. 사례별 예상 판정이며 거절을 solver 실패로 집계하지 않는다.

별도 Python/mpmath90자리 식 구현은 Rust evaluator를 호출하지 않고 원 FT03의 RR/CI/DR/광흡수 및 RCT 식을 계산했다. 36끝점의 BE잔차를 대조하고 각 fullstep에 대해 old state부터 시작하는 independent numerical root solve12개를 수행했다. 최대 scaled endpoint residual=3.9444481109741e-16, native/root scaled difference=1.19691829563317e-16, RCT 사건수 상대차=1.27002428987038e-15다. 사전 checker 기준은 각각5e-14,5e-14,2e-12다. 이 checker의 author와 addon author는 같고 새로운 독립 과학 검토는 NOT_RUN이다. 서로 다른 식/산술 계산경로이지 fresh reviewer 또는 interval uniqueness proof가 아니다.

## 재현과 source ownership

전체 ZIP에는 unchanged vendor34파일, addon, 고정밀 oracle, 실패·성공 로그와 identity manifest를 담는다. 도구체인 및 compiled target은 제외한다. Rust1.94.1은 사용자가 준 archive를 이전 pinned SHA와 대조해 새 prefix에 설치했으며 제공 환경 스크립트와 같은 경로다. GPG 공개키를 확보하지 않았으므로 새 서명 검증 성공은 주장하지 않는다. official release page 확인은 실행 파일의 서명 인증과 별개다.

    source /path/to/rust_1_94_1_env.sh
    bash run_checks.sh /absolute/path/to/new-evidence-directory

mpmath1.3.0이 필요하다. 이미 사용한 출력 디렉터리를 덮어쓰지 않는다. `--locked --offline`으로 지정된 local path dependency만 빌드한다. CLI 옵션의 의미는 Cargo 공식문서를 확인했지만 bitwise reproduction 또는 다른 host에서 동일한 binary hash를 보장하지 않는다.

원 vendor34파일은 최종 실행 뒤에도 해시가 모두 같고 consumer remote mutation=0이다. F08/coupled source 소유권 예약과 CURRENT_FASTEST_STATE는 보존한다. 다음은 owner가 이 실행 패키지와 추가 event/underflow 계약을 검토해 채택하고 실제 F08/static dispatcher에 연결할지 결정하는 일이다. 새 설계 재작성이나 같은 mixed gate 재실행은 다음 작업이 아니다.

HE-F2 global=false, HE-F3 WAIT_REI_F09_RESULT, baseline RCT OFF, physical HOLD, source moments null, Eq55 NOT_RUN, legacy PARKED_OPEN을 유지한다. FT03-GM25 공통 온도영역 부재도 바뀌지 않았다. 이번 prototype은 current F08 whole-crate나 팽창 S0/우주론 이력·physical fit accuracy를 인증하지 않는다.

재현 runner 검증 범위: shell syntax는 확인했고 위 구성 명령을 개별 실행했다. runner 전체를 한 번에 실행하는 별도 반복은 하지 않았다.

## 게시 상태

커밋 객체3355cd79252deb325b9e1290d618885947f0fcf8과 tree9c247bf039fd48341eec3479a8e6010451c793d2는 생성됐다. force=false 브랜치 갱신은 OpenAI tool safety-status 판별 단계에서 차단됐다. 직후 원격 branch는954790c6ba834ba098e7442800893c9dff823d02로 불변이었다. 다른 write경로로 우회하거나 완료로 보고하지 않는다. PUBLICATION_STATUS.json이 이 상태를 소유한다. 이는 과학/numerical failure가 아니며 전체 실행 source/evidence는 본 ZIP으로 전달한다.
