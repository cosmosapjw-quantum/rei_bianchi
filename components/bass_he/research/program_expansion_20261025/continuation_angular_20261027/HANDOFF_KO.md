# ANGULAR06 다음 스레드 인계

## 읽을 순서

`RESULTS_KO.md` → `RESULT.json` → `DAG.json` → `LOOP_PROGRESS.json` → `review/RESULT_REVIEW.json`을 읽는다. 최종 source/delivery SHA와 마지막 provider ACK는 별도 `BASS_HE_ANGULAR06_CLOSEOUT_20261027.json`이 정한다. 테스트에 사용된 코드 revision은 S02 `a4745150c30af2c6a71b6b61bde0a7e17b8b9ddc`이며 실제 코드 identity는 dependency manifest에 있다. 문서·전달 tail을 더했다고 같은 테스트를 다시 실행하지 않는다.

## 실제 source와 중앙 후보

과학·결과 source S03는 `4349f3cc92543085f7135bb3b556cb9756eec9ec`, tree `eb0dfa6751badb74d2aa094ec93f32a69c1bb7bc`다. 최종 전달S04는 이source를 변경하지 않고 영수증·중앙후보·인계만 더한다. S04의 실제SHA는 최종외부closeout을 읽는다.

중앙후보17파일은 `delivery/central/payload/`, exactmanifest와독립31/31검토는같은폴더의JSON이다. 후보base는152b82cac23fedcb75a9effe0c159bae3d800c01이며 새과학계산없이HE관찰만 재적용했다.

## 확보한 결과

유한질량 CM→lab 각도 사상, signed Jacobian, 원식의 부호를 확인하는 한/두 역상, fold/stopped/threshold의 별도 처리, branch별 weighted pushforward, identical-daughter event/inclusive/hemisphere normalization을 유도하고 구현했다. 첫 검증 26/26 PASS, CPU 0.273874185/4 s, wall 0.268156042/15 s, repair 0. 새 저장자료 그림은 CPU 5.791514953/6 s PASS, wall 5.852712830/15 s, 과학 함수 호출 0이다. 독립 결과 검토는 ACCEPT_SCOPED_CONDITIONAL_ANGULAR_REFERENCE, blocking0이다.

Local ANGULAR06 DAG는 **5 complete +3 physical open /8**이다. 원 실험 정규화/liquid-He projection, full angular law와 실제 photon encounter flux, named nonthermal/deposition consumer는 아직 열려 있다. Global physical completion=null, central parent-declared27/88 delta0, L4=false, production=NOT_APPROVED, activation=false다.

## 반드시 보존할 과거 상태

- PHOTON05 S05: `251c6baa6c3359b1d6997dbce51cea65500b53d6`.
- PHOTON05 D05: `4db5ce7297a7ded4624b93721873aacc9b4ebf30`.
- PHOTON05 원24/24 PASS, plot CPU **4.40726504 >4s FAIL**, workflow **PARTIAL**, local **4complete+1partial+3physicalopen/8**.
- HE101 C8 **PARTIAL_EXPORT19/20**, reserve **0**, 원 **PASS/FAIL/FAIL**.
- 과거 과학·plot·백업 재실행/재생성 및 예산 reset/transfer 금지. ANGULAR06도 새 의존성 변경 없이 재실행하지 않는다.
- 입자수·Cv·rest/binding·nonthermal kinetic energy를 분리한다. `population_rest_energy_witness`가 binding을 한번만 소유하며 independent binding RHS 및 thermal ports는 null, birth_pool=UNASSIGNED다.

## 게시와 중앙 base

사용자는 이번 연구와 백업·게시를 요청했지만 자동 승인 심사가 공개 GitHub source push를 두 번 거절했다. 공개 저장소와 상속된 미게시 이력을 포함하는 구체적 payload에 대한 승인이 필요하다는 사유다. 인증 owner와 push권한 확인 뒤의 재시도도 차단되었고 원격 변경은0회다. 우회 API를 사용하지 않는다. source/central 모두 미게시다.

과거 중앙 후보 검토 base `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`와 이후 B3h가 반영된 실제 관측 base `152b82cac23fedcb75a9effe0c159bae3d800c01`을 구분한다. HE-only 재적용 후보·차이·독립 검토는 최종 전달 패키지에 들어간다. 다른83개노드·B3h/CR·owner/status/budget/dependencies를 보존한다. 게시가 명시적으로 재개되면 최신 HEAD/AGENTS를 다시 읽고 변경된 base에 HE delta만 재적용·검토한다. 실제 expected SHA, force=false를 사용한다. 오래된 SHA를 현재 기대값으로 가정하지 않는다.

## 다음 입력과 정지점

현재의 수학·참조 구현을 재작성할 필요가 없다. 다음 물리 입력은 원 Arends/Hartmann 문헌의 사건/입자 정규화 식과 liquid-He coincidence 실험의 projection이다. 확보 후 native EXFOR 수치를 세 정규화 convention 중 어디에 연결할지 판정한다. 별도 지정 없이 새로운 실험 law·flux·deposition을 만들거나 다음 연구 노드를 자동 시작하지 않는다.

다른 대화 검색은 Personal Context 서비스 불가로 열리지 않았다. 893 branch ref 목록 조사와 직접 의존하는 최신 기록·제한된 backup 검색을 전체 비공개 대화의 내용 조사로 표현하지 않는다.

## 복사용

```text
$physmath-research-loop로 BASS_HE ANGULAR06 인계를 읽어라.
최종 source/delivery와 backup IDs는 BASS_HE_ANGULAR06_CLOSEOUT_20261027.json을 기준으로 하라.
과학·결과sourceS03=4349f3cc92543085f7135bb3b556cb9756eec9ec; 시험sourceS02=a4745150c30af2c6a71b6b61bde0a7e17b8b9ddc다.
조건부 각도 사상·역상·weighted measure·identical-daughter normalization,26/26검증,신규plot,독립검토는 끝났다.
ANGULAR06 local5complete+3physicalopen/8; workflow PARTIAL_PUBLICATION.
새 test CPU0.273874185/4s PASS, 새plot CPU5.791514953/6s PASS,repair0이다.
PHOTON05 S05=251c6baa6c3359b1d6997dbce51cea65500b53d6, D05=4db5ce7297a7ded4624b93721873aacc9b4ebf30.
PHOTON05 24/24PASS와 plot4.40726504>4sFAIL,workflowPARTIAL,4complete+1partial+3physicalopen/8을 보존하라.
HE101 C8PARTIAL_EXPORT19/20,reserve0,원PASS/FAIL/FAIL을 보존하라.
입자수,Cv,rest/binding,nonthermal kinetic energy 및 single owner를 유지하라.
완료된 과학·plot·backup을 재실행/재생성하거나 예산을 초기화/전용하지 말라.
source/central은 미게시이고 공개push는 자동 승인 심사에서2회거절됐다. 우회하지 말라.
구체적 공개payload에 대한 게시승인이 있으면 먼저 최신HEAD/AGENTS를 읽어라.
oldcentralreviewbase1a38f94f...와 B3h반영base152b82ca...를 구분하고 최신base에HEdelta만 재적용·검토하라.
실제expectedSHA와force=false로 처리하라. 전역physicalcompletion=null,central27/88delta0,L4false다.
원 실험정규화/liquid-targetprojection,fullangularlaw/flux,nameddeposition은 열린 입력이다.
사용자가 후속 노드 또는 게시를 구체적으로 지정하기 전에는 이 체크포인트에서 정지하라.
```
