# NCP 인계 — HE29 준비 작업 완료, 추가 실행 없음

## 현재 판정

`NO_NEW_EXECUTION_REQUIRED`다. 기존 native reference 네 pair `(r2,512),(r4,512),(r8,512),(r4,1024)`는 4/4 admitted이며, 실제 m8/GL4/q0/r4/table512 packed canary도 1/1 완료되어 원래 gate를 통과했다. **RUN_READY.sh, START_REFERENCES.sh, PUBLISH.sh를 다시 호출하거나 새 output 이름으로 같은 case를 반복하지 않는다.** 사용자는 파일 전송·다운로드·업로드·터미널 작업을 맡지 않는다.

Repository: https://github.com/cosmosapjw-quantum/BASS_HE
PR78: https://github.com/cosmosapjw-quantum/BASS_HE/pull/78
PR81: https://github.com/cosmosapjw-quantum/BASS_HE/pull/81
두 PR은 Draft/open/unmerged로 유지한다.

## 고정 identity

- 실행 code `802a32361288bf5aa0e0d1f63c912768f1a1d407`.
- ABI2 core `a5d4711460c09b310b78c9692aa62534b7a843d3`, VigilODE `a21d573980f66fe02891bd216153443b5352f921`, watchdog `ed5adca43f474553a9bce7f5de45d464be5905cb`.
- native owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`, binary SHA `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9`.
- bridge SHA `28d637a9011ad0e23c087659cd07574cfb0ddc55511380c4c807165aee3123eb`.
- table SHA `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd`.
- 결과 원본 `d6c1cf97ee216269114b1b0d1bb45984e2140f8b`, 결과 bytes를 유지한 tree 복구 `fcdf56d9a66b2d159d42a9a72131f94040cd5891`.
- 소비자 분석 `5eb38cbfeed7abf60e1827e358611c8f763c2da4`, 실제 12/12 raw readback PASS. 후속 문서 HEAD는 별도다.

## 저장 반환의 위치와 재사용

현재 기준 경로는 `research/he29_survival_budget_20261018/`, 현재 lane은 `canary_intake_20261021T0118Z/`다. root README/DAG, lane README/RESEARCH/DAG/DELIVERY 및 `evidence/CONSUMER_ANALYSIS.json`, `PRODUCER_RETURN_RECEIPT.json`, `PR81_TREE_REPAIR.json`, `ANALYSIS_PUBLICATION_READBACK.json`을 먼저 읽는다.

반환 archive `BASS_HE_HE29_HPC64_CANARY_RETURN_20261021_a00990e5.tar.gz`, 32120999 bytes, SHA256 `a00990e5f8a5978a8881c1b56fb96072df5abd91600495494b9397cc9360aec7`.
Dropbox `id:BSpOijBcT10AAAAAAD_ceQ`; Drive `1IrWYFe_08-s1CfAcV2FgszDoMj5E_5sG`.
생산자의 dual raw PASS와 소비자 Dropbox raw PASS가 기록되어 있다. Outer payload20/member21, nested payload39/member40은 서로 중복되는 보존 구조이며 고유 파일 수로 합산하지 않는다. 원래 276MB native reference archive와 저장된09929 분석은 완료 근거로 재사용한다.

반환의 원래 실제 실행 경로는 `/root/HE29_HPC64_STAGE_LJwu47Fb/run`이며 원본 baseline은 `/root/HE29_REFERENCE_20261020T120000Z`다. 이 경로는 과거 producer snapshot이며 현재 존재·process 부재를 보증하지 않는다. 현재 소비자는 live NCP census를 수행하지 않았다.

## 실행 경계의 이력

초기 `HE29_HPC_GIT_REVISION` 실패는 잘못된 packed root를 실행 전에 거절한 기록으로, build/canary 시작0이었다. 성공 실행은 fixed802a + clean a5 source를 사용했다. 이전 SSH 인증 HOLD도 별도 과거 시도로 보존한다.

성공 실행 당시 사용자 승인 다섯 유휴 Codex process는 PID/start_ticks/cmdline SHA의 exact identity로만 일회성 허용했다. 원래 source bytes는 그대로였으나 별도 runtime shim이 있었다. 그 shim과 allowlist는 기존 private archive에 있다. 이를 일반 예외로 배포하거나 다음 실행에서 재사용하지 않는다. 다른 process를 종료·신호·일괄 허용하지 않는다. Remote Desktop Commander의 기존 quota/no-retry 금지는 유지한다.

## 이후 실제 새 작업이 생길 때

새 반환·새 partial evidence가 있으면 identity와 변경분부터 분석한다. 완료 결과를 재생성하지 않는다. 새 이론·최적화 설계와 substantive code 수정은 연구 대화에서 끝내고, NCP는 준비된 revision의 compile/작은 환경 수정/실행만 담당한다. 향후 실제 실행이 별도 범위로 준비되면 그때 접근 가능한 실행자가 현지 /proc와 저장 결과를 먼저 관측해야 한다. 이번 문서는 새 실행을 제출하는 인계가 아니다.

현재 실제 성능은 phase timing까지다. 기존 두-method pair와 한 packed canary의 시간을 나누어 speedup을 만들지 않는다. 원래 rtol1e-10/scaled-atol1e-12, fraction1e-11, 방법간온도1e-9K, number3e-15/H, energy3e-12eV/H, species3e-12, positivity 및19-ledger full-state norm을 유지한다. continuum/global-temperature/fullEoR/wholeGrackle/Bianchi-CMB는 HOLD다.
