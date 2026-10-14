# HE-FLRW02B 혼합 H/He native 실행 반환

원래 준비됐지만 소비기에 없던 두 mixed native 시험을 실제 REI b553698a114fbff05640ab6ecb95d260410de492 library에 연결해 실행했고 모두 통과했다. 원 library source는 변경하지 않았다. 이 결과는 supplier가 요구한 finite source/scale regression 실행 공백을 메운다. 전역 HE-F2/HE-F3, 원자 fit 정확도, 열 closure, 팽창 이력 승격은 아니다.

공급자 공개 return이 지정한 Drive ZIP 48,970 bytes, SHA256 `edd811ee788439d8e260931a0535c30e9f1f04a26cb475b3bb1584d8b472e745`를 가져와 전체 ZIP CRC와 payload 35개 SHA256을 검증했다. `proposed_consumer/he_flrw02_absorption.rs`를 SHA256 `a1223f89a1c54c731df5c505415af969077ab7a94e920ce2e9efc955090dad54` 그대로 사용했다. `inputs/`에 있는 더 오래된 제안은 실행하지 않았다.

먼저 고정한 `EXECUTION_CONTRACT.json`대로 원 crate의 target 부재를 cargo에서 확인해 exit101을 보존했다. `harness/`는 원 library를 path dependency로 쓰며 같은 제안을 외부 integration target으로 컴파일한다. 정확한 argv, rustc 1.94.1 환경, stdout/stderr와 exit0은 `EXECUTION_LOG.json` 및 `NATIVE_MIXED.*`에 있다. 원 source/고정 proposal의 실행 후 hash도 일치했다.

| 검사 | 실제 비교 수 | 최대 상대 오차 |
|---|---:|---:|
| 종별 흡수/광자/에너지 장부 및 두 scale 변환 | 82 | 3.4885067388312133e-16 |
| 독립 source-reference anchor | 192 | 2.809899931685239e-15 |

모든 비교의 판정식은 기존 `abs(a-b) <= 5e-14*max(abs(a),abs(b)) + 1e-300`이다. 두 테스트는 같은 proper 상태에서 scale factor만 바꿨을 때의 표현 일관성과, 같은 comoving inventory 및 고정 photon energies에서의 density/volume scaling을 구별한다. energies 20/35/70 eV, a0=0.25, lambda=0.5/2.0의 유한 5상태다. 후자는 free-streaming photon redshift 이력 시험이 아니다. Source/GOLDEN은 supplier가 만든 Decimal/mpmath 경로이며 native와 fit coefficient 및 source prescription을 공유한다. 이 실행에서 새 고정밀 reference를 계산했다고 주장하지 않는다.

절대 오차 최대에는 매우 큰 comoving cMpc^-3 정규화 수치가 포함되므로 단독 물리 오차 크기로 해석하지 않는다. `NATIVE_COMPARISONS.json`과 `NATIVE_RESULT.json`에 해당 관측값과 label을 보존했다. Domain refusal source는 byte-identical이며 이 두 시험에서 새로운 negative-domain case는 추가하지 않았다.

REI repo에 넣을 정확한 제안 경로는 `rust/rei_microphysics/tests/he_flrw02_absorption.rs`다. 현재 작업은 외부 harness 실행으로 끝냈으며 repo 반영과 HE supplier ACK는 총괄 게시 단계에서 기록한다. 독립 decision review는 총괄 reviewer가 수행한다. 이후 단순 전달을 이유로 원 84/116 native 시험, HE/CR/HH atomic suite 또는 이 두 시험을 다시 반복하지 않는다.
