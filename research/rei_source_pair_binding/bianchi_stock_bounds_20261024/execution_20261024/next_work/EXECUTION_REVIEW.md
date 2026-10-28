# Work 실제 실행 독립 C9 delta 검토

**판정: PASS_SCOPED. Finding0, 차단0, 교정 요청0. 최종 과학 채택은 root의 별도 결정이다.**

기존 `CODE_STATIC_REVIEW.json`의 PASS_STATIC_SCOPED(SHA256 `b8dc3b42401306ef0fdb06f77e7763c40ac5d6c323b78ada12c415c3f724f041`)를 재사용했다. 검토자 `/root/pressure_survey`는 구현·실행을 맡지 않았으며, 이번에는 실제 raw와 동일 source·입력·자원·주장 연결만 확인했다. 전체 source/mathproof를 다시 감사하거나 새 fixture를 실행하지 않았다.

## 실제 실행과 identity

| 항목 | 관측 |
|---|---|
| Child / fixture group / literal cases | 1 / 1 / 6 |
| 최종 완료 flags | 7개 모두 true |
| CPU raw | 0.04518899999999999s |
| CPU 표시 | 0.045189s |
| Launch-inclusive wall | 0.04566222199900949s |
| Child / wrapper exit | 0 / 0 |
| Stderr / timeout / retry | 0bytes / false / 0 |
| 동결 CPU / wall | 1s / 5s; 실제 둘 다 이내 |

- 실행 결과: `next_work/EXECUTION_RESULT.json`,16070bytes,SHA256 `f57133c3673f186a1fac412c3c1eb0a60df5518ff87b3a4bf246049a2f2506f6`.
- 실제 stdout: 5188bytes,SHA256 `8a38079873d3f3739ebc5a811f411eb992d2b56b2bde60d6d178d0e143cd4815`.
- 실제 resource receipt: 2050bytes,SHA256 `d211c62c1744812c4a1fadd7acee790841bc515fea4c8f75214e9d91d5ebe8a7`.
- 동결9파일은 현재 bytes/hash가 implementation manifest, 정적 C9, 실제 실행 record와 모두 일치한다. Source `b0f08028…`, fixture `d6b7ede9…`, runner `bb514820…`의 원문 근거를 재사용했다.
- 별도 raw receipt/stdout은 EXECUTION_RESULT의 embedded 값과 같다. Output SHA, attempt command/input hashes, proposal/runner pins도 연결된다. 모든 Fraction 출력은 decimal-string numerator와 양의 denominator 형식이다.

## 실제 literal 출력과 fixture 도달

모든 경우 trace는 [8/3,3]이다. 저장된 여섯 output case를 동결 계약의 literal과 직접 비교했고, 모든 field가 일치한다.

| Rates H | Work | Shear work | dU/dt |
|---|---|---|---|
| (-2,1,4) | [-6,12] | [-9,9] | [-18,0] |
| (1,2,3) | [8/3,9] | [-3,3] | [-21,-44/3] |
| (-3,-2,-1) | [-9,-8/3] | [-3,3] | [44/3,21] |
| (2,2,2) | [16/3,6] | [0,0] | [-18,-52/3] |
| (-2,-2,-2) | [-6,-16/3] | [0,0] | [52/3,18] |
| (0,0,0) | [0,0] | [0,0] | [0,0] |

변경되지 않은 fixture의 최종 print는 모든 assert 뒤에 있다. 최종7개 true flags, exit0/0, empty stderr는 독립 symmetric beam 끝점·full STF norm witness·scaling/reversal/permutation·zero/tiny/float/refusal controls·literal enclosure·실제 저장 raw 소비·axis2 witness 경로를 연결한다. 이는 유한 동결 fixture의 실제 성공이며 모든 임의 입력의 구현 정확성 증명으로 확대하지 않는다.

## 저장 stock 입력의 실제 소비

Work의 입력1085bytes는 원 stock stdout와 완전히 같고 SHA256은 `5e6446adf8e9ba93212eaf001b9d2aa9c77e63deef8ca42eae1aa8ee79b8c733`이다. 출력의 `stored_energy_interval`은 원본과 복사본의 `mixed_energy_interval`에 정확히 일치한다.

Nt2는 frozen N2와 ratios(1/2,1,2)의 D1에서 별도 유도했으며 Lbar5는 sqrt33−1<5의 해석적 majorant다. 실제 출력도 `derived_number_density`, `analytic_support_majorant`로 구분한다. Raw에 없는 identity numerical payload를 읽었다고 하지 않는다.

실제 `transported_axis2_witness_checked=true`는 frozen U2/Pdiag(0,3,0)의 S3/work3/shear0/derivative−9/norm²6 포함 검사가 완료되었음을 연결한다. Consumed trace/work/derivative interval은 stdout에 있다. Consumed shear/norm upper는 fixture에서 검사했지만 별도 numeric field로 serialize하지 않았으므로 그러한 raw field를 만들지 않았다. Stock import/call/replay는0이다.

## 현재 GO·백업·누적 이력

WORK_GO의10:01:09 UTC는 attempt10:01:45.906291 UTC보다 앞선다. GO는 현재 authorization과 Stage B의 완료된 양쪽 ACK를 참조한다. Stage B archive는 `REI_STOCK_ADMITTED_WORK_PREP_B_20261024_b366dcee5d7f.zip`,309964bytes이며 기록된 Drive/Dropbox 크기가 같다. 본 reviewer는 원격 재조회·archive 재다운로드·독립 remote whole hash 검증을 하지 않았다.

원 proposal의 `PROPOSED_NOT_RELEASED`는 준비 당시 이력으로 보존한다. 이번 actual run은 별도 WORK_GO가 허용하며 소비된 stock allowance를 이전하지 않는다. Known partial CPU는10.318970s다. 과거10.110448s/10s의0.110448s 초과 FAIL, original cumulative cap NOT_FROZEN, wholeL0 UNKNOWN_NOT_ZERO, parent/model/I/O/remoteCAS 별도 미측정을 유지한다.

## 한정 채택 권고

Root는 이 actual finite work arithmetic와 saved-stock integration fixture를 채택할 수 있다. Exact-moment API의 sharp snapshot bounds와 실제 mixed-stock 소비의 `conservative_given_energy_enclosure`를 구별한다. Physical history/EOS/stopping/thermalization/Einstein global evolution은 선택하지 않았으며 L4_ready=false, 전체 물리 완료율null, 기존2e-12 gate 불변이다.

이번 reviewer의 candidate import·compile·test·과학 실행·수치 재평가·CAS·render·구현 수정·Git/cloud mutation은0이다. 기존 JSON·hash·literal의 기계적 비교와 read-only 검토만 수행했다. Finding이 없으므로 추가 재실행이나 감사 확장 없이 종료한다.

