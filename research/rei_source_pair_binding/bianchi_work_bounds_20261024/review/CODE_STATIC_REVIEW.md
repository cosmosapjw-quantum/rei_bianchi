# Work 구현 독립 정적 C9 검토

**판정: PASS_STATIC_SCOPED. 새 finding 0, 차단 0, 교정 요청 0. 실제 work 실행은 NOT_RUN이다.**

검토자 `/root/pressure_survey`는 구현자 `/root/pressure_coding`와 분리되어 있으며 후보 코드를 수정하거나 실행하지 않았다. 같은 inherited model family의 native 독립 검토이며 다른 model family의 심사라고 주장하지 않는다. 이 판정은 이미 계획된 별도 root GO와 Stage B 실제 백업 뒤의 한 번 실행을 위한 정적 준비 판정이다.

## 동결 identity와 읽기 범위

| 파일 | SHA256 |
|---|---|
| work_bounds.py | `b0f08028dc96e78aa10c83eef6bcd88a02975a507a8a9a62a3ccb69a979c2152` |
| focused_check.py | `d6b7ede9e634db73fd65672747c661df02aca2541bfb7d0a3f0e25ad8b5f70cd` |
| run_focused_once.py | `bb514820a91fb392005d2630a78e4338e74b6046683c40e12c5bafef2cef24c8` |
| 실제 stock stdout 1085bytes | `5e6446adf8e9ba93212eaf001b9d2aa9c77e63deef8ca42eae1aa8ee79b8c733` |
| 최종 이론 | `d2febfb893e3e06adc7d3e276d49f6fd8f560a3f845199061c984a0bef4546e2` |
| 최종 계약 | `03548169c1f874eee9816b6af69c947bf41cd20c9a026c84debe853ea5ca057d` |
| 구현 diff | `4602692f9adbb7ff392102633e6fe0d10ad928201338b59788fddc6b69b35803` |

Leaf9파일의 실제 bytes는 implementation manifest와 모두 일치한다. Proposal의 source/fixture/input3개 hash와 SOURCE_BINDING의6개 hash도 일치한다. Authority2개는 앞서 전체 읽은 root 최종 이론·계약과 byte-equal이다. 53,739byte/1,049line diff 전체의9개 /dev/null 추가 section을 재구성해, 각각 읽은9개 실제 파일과 byte-equal임을 확인했다. 기존 파일 수정은 없으며 diff를 적용하지 않았다.

Module·fixture·runner·proposal·binding·README·저장 raw를 전체 읽었다. 추가로 WORK_IMPLEMENTATION_MANIFEST, STOCK_ADMISSION, STOCK_EXECUTION_REVIEW, BINDING_REPAIR를 읽었다. 상세16개 readset과 hash는 동명의 JSON에 있다. 과거 stock 정적 심사는 source/fixture identity를 유지한 근거로 재사용했으며 전체 stock 코드 감사나 수치 실행을 반복하지 않았다.

## 수식과 API 대응

`_fraction`은 int/finite float/Fraction을 표현된 값 그대로 Fraction으로 옮기고 bool·지원하지 않는 타입·비유한 값·음의 moments·M≤0을 입력명 있는 ValueError로 거부한다. Rates는 길이3의 유한 signed tuple/list다. 두 공개 API는 각각 U≤NL, 0≤ulo≤uhi≤NL을 나눗셈 전에 확인한다.

Trace는 S=trP이며 1/3을 추가하지 않는다. Lower는 ulo(L+2M)/(L+M), upper는 uhi(uhi+2MN)/(uhi+MN)다. N=0 또는 uhi=0을 먼저 처리하고, L=0은 feasibility에 따라 U=0이어서 0/0을 평가하지 않는다. 모든 numeric 결과와 tuple 원소는 Fraction이다.

`_contract`의 lower는 최소 rate a가 비음수이면 Slo, 음수이면 Shi를 사용한다. Upper는 최대 rate b가 비음수이면 Shi, 음수이면 Slo를 사용한다. 전부 양수·전부 음수·혼합·영 분기가 이론과 일치한다. Theta와 shear rates도 exact이며, shear에 같은 contraction을 적용한다.

미분은 sorted(-theta*ulo,-theta*uhi)에서 work의 반대쪽 끝점을 빼므로 안전한 outer interval이다. U가 정확히 고정되면 sharp 순간 미분 경계로 돌아간다. Full Frobenius STF norm squared upper는 (2/3)Shi²이며 half-contraction/LRS 계수를 섞지 않는다.

순간의 unrestricted angular positive measure에 대한 PSD stress 집합과 대칭 B의 해석 정리를, 구현에서는 exact diagonal rates로 제한한다. 고정 과거 분포의 모든 tensor 실현이나 self-consistent Einstein trajectory까지 주장하지 않는다.

## Fixture의 독립성과 범위

여섯 signed-rate case의 work/shear/derivative literal이 동결 계약과 일치한다. Production private helper를 oracle로 호출하지 않는다. 별도 discrete measure 합은 k+1−1/(k+1)을 사용해 M=1에서 radial0/2 mixture의 S=8/3과 mono-k1의 S=3을 직접 만든다. ±beam을 같은 에너지·축에서 나누므로 평균운동량0을 만족한다. Literal과 물리적 beam 끝점을 모두 비교해 단순한 구현 복제만으로 통과하도록 만들지 않았다.

Axis2의 P=diag(0,3,0)에서 STF norm²=6을 독립 합으로 확인하도록 준비했다. Weight7/3와 norm²의 제곱 scaling, rates reversal/permutation, U=NL, 영 경계, tiny exact U=2^-1075, represented integer-valued float, named invalid-input cases 및 별도 enclosure literal case도 포함한다. 최종 JSON 출력은 이 모든 assert 뒤에 있다. 이들은 **준비된 checks**이며 아직 실제 work PASS로 기록하지 않는다. 유한 fixture가 모든 임의 입력의 구현 정확성을 증명한다고 주장하지 않는다.

## 실제 stock raw 출처

`inputs/stock_stdout.jsonl`은 현재 stock child의 원래 raw1085bytes와 완전히 같다. Root의 STOCK_ADMISSION 및 독립 STOCK_EXECUTION_REVIEW가 같은 raw/source/fixture identity의 실제 stock1child를 채택했다. 원 fixture SHA는 `47ecf7dc0ec59790e4eb339d59c527e71c07aab4ecb7b2fc0c4e265e77b35f43`와 일치한다.

새 fixture의 유일한 numerical raw selector는 `mixed_energy_interval`이고 decimal numerator/denominator를 Fraction으로 복원한다. `identity_checked`는 flag일 뿐 numerical identity payload라고 쓰지 않는다. Nt=2는 frozen initial N2와 ratios(1/2,1,2)의 D1에서 유도한다. Lbar5는 frozen L2/M1/rmax2의 sqrt33−1<5에서 얻은 해석적 majorant다. 이 두 값의 출처를 raw JSON과 구별한다.

Transported axis2 mono-k1 witness는 r2=1,D1에서 U2/Pdiag(0,3,0)을 유지한다. H=(-2,1,4)에 대한 S3/W3/shear0/dotU−9/norm²6이 consumed outer bounds 안에 있음을 확인하도록 준비했다. WORK-INPUT-01의 문서 결속 교정은 최종 theory/contract/source/README에서 일관되게 반영되었다. 실제 work의 소비 성공은 실행 뒤 raw에서 확인할 사항이다. Stock import/call/replay는0이다.

## Runner와 실제 실행의 구분

Parent는 candidate를 import하지 않고 source·fixture·저장 input hash를 먼저 확인한다. Exclusive attempt marker를 한 번의 Popen 전에 만들며 child는 Python -B focused_check.py 하나다. RLIMIT_CPU soft=hard1초, Popen 직전부터 잰 launch-inclusive wall5초에서 launch 소요를 뺀 timeout을 communicate에 적용한다. Timeout/launch failure는 kill/reap 후 raw와 receipt에 남기고 자동 retry는 없다.

RUSAGE_CHILDREN의 전후 user+system 차이, 실제 wall, command·proposal·runner·source·stdout·stderr hash를 저장하도록 되어 있다. Wrapper exit0은 child exit0/timeout없음/launcherror없음에 해당한다. Frozen root admission의 실제 CPU≤1초/wall≤5초 판정은 실행 뒤 receipt에서 확인한다. 검토 시 work/raw는 존재하지 않았고 runtime 성공이나 예산 준수를 이미 달성했다고 쓰지 않는다.

기존10초 한도 초과0.110448초의 FAIL, known partial CPU10.273781초, cumulative cap NOT_FROZEN, wholeL0 UNKNOWN_NOT_ZERO를 보존한다. Parent/model/I/O/remoteCAS 비용은 별도 미측정이며 stock의 소비된 허용을 이전하지 않는다.

## 결론과 다음 delta 검토

새 finding은0이다. 정적 candidate는 동결 범위에서 준비되었으며, 실제 numerical admission은 한 번 실행 후 source identity 유지와 actual raw/receipt에 대해 별도로 판정한다. 다음 검토는 이 정적 근거를 재사용해 actual raw/provenance/resource/claim의 delta만 확인한다.

이 reviewer의 candidate/fixture/runner import·compile·test·과학 실행·수치 재평가·CAS·render·구현 수정·Git/cloud mutation은 모두0이다. `2e-12` gate 불변, physical history/EOS/stopping/Einstein evolution 채택 없음, L4_ready=false와 전체 물리 완료율null을 유지한다.

