# REI 다음 한정 연구: 실제 event-free flux-response 항

ROLE=LOCAL_CODEX
RETURN_TO=MAIN_CONVERSATION
WORK_THREAD_REQUIRED=false

이 인계는 이번 log-denominator 연구를 반복 실행하거나 production ABI를 새로 구현하라는 지시가 아니다. 주 대화가 source 검토·유도·정확 fixture 검산을 마친 뒤, 실제 보존된 local state/tube와 interval 계산이 필요할 때만 사용한다. 먼저 이 파일이 게시된 정확 commit과 동일 작업의 최신 결과를 확인하여 중복하지 않는다.

## 이미 마련된 입력

PR #74 mapping source: `032b59372e55bdbb86860e8075206bd0026f7be1`, tree `7220d791d614d34e63097e3115c8036fcfcb8e94`. 그 mapping 및 SOURCE_BINDINGS.json을 재사용한다. 이 디렉터리 PROOF_AND_SCOPE.md와 실제 실행 뒤 게시된 CHATGPT_HANDOFF_KO.md를 읽는다. 옛 MPRK 및 모든 production source/test/허용오차는 변경하지 않는다.

새 핵심식은, h 고정일 때

    delta v = P delta b + h P K(delta F) D^-1 v
              + (I-P) diag(v) (delta d/d).

분모-only 항은 ||.||_(1,w)에서 <=2M||delta d/d||_infinity다. 이것을 전체 rate/Jacobian bound로 오인하지 않는다. predictor/gamma의 b=d=y0, corrector의 b=y0,d=yp와 실제 flux 평균을 유지한다. 이미 검산된 generic identity를 편의상 다시 돌리지 않는다.

## 다음 산출물 하나

관련 로컬에 보존된 실제 population/source context 또는 기존 event-free enclosure를 찾아 exact identity와 함께 읽고, 한 개의 명시적 event-free positive tube에서 남은 flux-response 항의 계산 가능한 상계를 구축하거나 정확히 어느 입력이 부족한지 제시한다. 논문용 수치나 첫 구간 전체를 만들지 않는다.

1. 현재 source의 실제 flux dependencies를 사용한다. photo-current는 per-atom Gamma와 다르며, node owner normalization은 다른 node population에 의존할 수 있다. 합성 flux law를 실제 rate라고 바꾸지 않는다.
2. fixed site/time/forcing, population·temperature 범위, branch cell, positive denominator/normalization margin과 norm scaling을 명시한다. CELL_LOWER_STRICT 점프·min/max active-set·floor 경계를 가로지르면 하나의 smooth derivative bound로 처리하지 않는다.
3. 실제 가능한 독립 perturbation 방향을 먼저 고정하고 delta F와 total response의 denominator 항을 각각 계산한다. 평균값 정리를 쓰려면 점 JVP가 아니라 tube 전체 derivative enclosure를 제공한다. 값이 없으면 UNKNOWN으로 남긴다.
4. local interval/고정밀 연구 코드는 기존 설치 패키지로 실행할 수 있다. 보호된 production importer/guard/worker나 46,080-node pilot은 호출하지 않는다. 현재 four-site Rust ABI 미구현을 다른 numerical backend로 production PASS라고 우회하지 않는다.
5. 범위 안의 연구 adapter/테스트 오류는 여러 차례 근거 기반 edit-test로 자율 수정한다. 원본 실패를 보존하고, 물리식·튜브·오차 기준을 성공하도록 임의 변경하지 않는다. production 수정이 필요하면 구체적인 제안만 반환한다.

## Git-first 반환

동일 작업 branch의 writer는 하나다. 새 REI research/evidence child에 실제 계산 코드·작은 결과·최초 실패와 최종 로그·CHATGPT_HANDOFF_KO.md를 commit/non-force push한다. 실제 tested source와 나중의 evidence-only commit을 구별한다. 로컬 경로나 ZIP만 반환하지 말고 고정 handoff 링크를 직접 출력한다. 별도 WORK_THREAD의 검토를 선행조건으로 만들지 않는다.

최종에는 finite-domain flux bound가 얻어졌는지, 어느 source dependency가 포함됐는지, point check인지 interval certificate인지, 무엇이 UNKNOWN인지와 다음 한 단계만 기록한다. 증거 없이 계산상수를 채우거나 rho_exact_flow를 새로 주장하지 않는다.

금지: BASS/REC/HTT 접근, XZ/GCC/native 반복, 새 Snapshot GET, 패키지 설치/downgrade, rootfs, runtime lock/production source 변경, Section-0/ref/lease/worker, first interval/provider, ready/merge/force-push. 기존 소모된 one-shot 예산은 보존한다.
