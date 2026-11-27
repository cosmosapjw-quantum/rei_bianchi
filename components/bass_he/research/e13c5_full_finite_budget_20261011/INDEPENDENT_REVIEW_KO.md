# E13C5 full finite budget: 독립 검토 판정

**판정: PASS_SCOPED. 미해결 blocker는 0개다.** 이 판정은 저장된 전체 유한 grid의 정확한 예산 집계, 동일 대상의 두 OFF N512 교체, 그리고 NCP의 저장 결과 재집계 계약에 한정한다. Constituent path enclosure의 물리·수학적 유효성은 앞선 PR20/PR19 검토를 조건으로 상속한다. 전체 ODE나 N512를 새로 실행하거나 재검증했다고 주장하지 않는다.

## 독립성 및 실제 확인

검토자 `/root/e13c5b_independent_review`는 후보 집계기, NCP wrapper, 이론 문서 및 과학 계약을 구현하거나 수정하지 않았다. 별도 `Fraction` 코드가 pinned `PATHS.jsonl`을 한 번 읽어 집계했다. 후보 또는 이전 producer 코드를 import하지 않았다. NCP wrapper의 발견 사항은 root가 수정했고, 검토자가 자체 소형 반례로 수정 전후를 직접 확인했다.

| 확인 대상 | 실제 결과 |
|---|---|
| 독립 raw saved-interval 재집계 | 235,912개 primitive checks, 실패 0; 20.1575초, 110,264 KiB |
| 독립 결과와 후보의 정확 대조 | 6,063 checks, 실패 0 |
| 저장된 순위 CSV 검토 | 248,880행, 102 groups; 519,183 primitive checks, 실패 0 |
| 봉인된 실행기·lock·실제 receipt 감사 | 86 checks, 실패 0 |
| 검토자가 발견한 null-field binding 수정 | 수정 전 실제 반례 보존; 수정 후 focused 2/2 PASS |

위 수치는 과학적 정확도의 자릿수나 독립 이론 증명의 개수가 아니다. 상당수는 행별 순서·포함 여부·구간 순서 확인이다. 주장에 중요한 직접 증거는 다음과 같다.

- OFF/KF/GM 각각 2,440개의 ordered unique paths, 총 7,320 paths와 14,652개의 segment identity를 확인했다. 9개 입력 bytes/SHA가 맞으며, 12개의 기존 selected paths는 segment `origin` 표시 외에 PR19와 같다.
- 각 mode의 absolute 17개 및 correction/species-sum 17개 지표에 대해 full, selected 4, complement 2,436, 교체 두 항, 유지 항을 직접 합했다. 이미 weighted인 absolute 값에 weight를 다시 곱하지 않았고, 에너지 보정은 exact binary64 lift의 erg/eV 인자를 한 번만 적용했다.
- 두 OFF 교체의 68개 지표 구간은 기존 구간과 compatible하고 nested다. 이전 검토된 lineage의 28개 절대량 교체 항과 정확히 일치하며, 72개의 captured baseline 비교가 overlap한다. 이는 동일 대상을 확인하는 일관성 증거이며, overlap 자체를 새로운 물리 증명으로 사용하지 않았다.
- 후보의 1,020개 partition 구간, 918개 width-budget 값, 204개 full sign, 204개 top-10 node 순서, 2,040개 top-10 폭, 1,020개 top-k 비중이 독립 계산과 정확히 같다. 모든 102개 mode/지표 full hybrid 구간이 기존 구간 안에 있다.
- 순위 CSV의 모든 node/rank 집합, 폭의 내림차순과 동률 시 node 순서, partition 표시, 전체 폭 합을 확인했다. 204개 old/hybrid variant의 상위 100개 node와 폭은 독립 raw 집계와 일치한다.

## 연구상 결론의 허용 범위

전체 finite cover는 이미 PR20에 존재한다. 따라서 complement 2,436개 node는 미실행 대상이 아니다. 선택한 네 node와 complement의 예산을 직접 계산할 수 있다.

OFF final photon의 full interval 폭은 약 `6.21037082261e-17`에서 `6.21036194033e-17`로 줄어든다. 감소 비율은 약 `1.43023330671e-6`, 즉 **0.000143023330671%**다. Heat의 종별 구간 합 폭은 약 `3.91116158213e-16`에서 `3.91115743897e-16`로 줄며, 감소 비율은 약 `1.05931628709e-6`다. 선택 경로에서 얻은 큰 개선 배율을 전체 유한 합의 배율로 바꾸어 말할 수 없다.

현재 두 경로 밖의 구간을 고정하면, 두 항만 더 정밀하게 해도 photon full 폭에서 추가로 제거할 수 있는 비율은 약 `1.12876147e-7` 이하이고 heat에서는 약 `7.54586509e-8` 이하이다. 이 한계는 **현재 유지하는 per-path Minkowski 합의 폭**에만 적용한다. Correlation, conservation identity 또는 새로운 direct-total certificate의 가능성을 제한하는 보편적 하한이 아니다.

Sign 판정은 exact endpoint의 strict 부호로 검증했다. 보정량의 기준은 continuous-minus-captured segment moment 또는 최종 captured segment stock이다. Native AGGREGATE와의 보정으로 바꿀 때 필요한 representation bridge를 생략하지 않았다. Dedicated total heat certificate를 종별 구간 합과 섞지 않았다.

## NCP 계약과 transport 정규화

최종 wrapper는 saved-result 집계기 child를 한 번만 실행하도록 되어 있다. N512, full-first2, coefficient, native, gas 또는 ODE 실행 명령은 없다. CPython 3.12 Linux, 한 개의 직렬 child, 1 GiB address-space 제한, 집계기 내부 300초와 child 330초 제한, 새 output directory 및 실패 증거 보존 조건을 확인했다. 14개 locked payload, 두 개의 unchanged dependency archive, 9개 추출 입력 identity가 연결된다.

압축 방식이 달라지는 경우를 위해 semantic projection에서 제외하는 것은 `ranking_artifact.bytes`와 `ranking_artifact.sha256` 두 transport 필드뿐이다. 그 대신 fresh gzip 자체의 bytes/SHA를 fresh projection과 확인하고, 압축 해제 CSV의 정확한 bytes/SHA를 별도로 비교한다. CSV의 독립 확인 값은 다음과 같다.

- Bytes: `51718536`
- SHA-256: `ce053b71a6b9aeb8bc5c8d1d9e9be3911c4a7aeba60779151a8af9d5bad3f8f4`
- Semantic projection SHA-256: `770a11a13a73ff3305ab62eb27a7abb0ca99860ffc56fc6384e6aead68d8e7c3`

기존 21개 synthetic boundary cases는 수정 전 wrapper에서 모두 통과했다. 다른 gzip bytes와 동일 CSV를 허용하면서 raw byte parity는 false로 기록했고, 변경 CSV와 잘못된 gzip selfidentity는 거부했다. 경로 traversal, link, 짧은 member, 저장 후 truncation, lock/source/input 변경, child 실패 및 timeout 증거도 확인했다. 이 21개를 최종 source에서 전부 재실행했다고 쓰지 않는다.

### 발견 사항과 닫힌 수정

수정 전 `result.get(key) != value`는 required projection 값이 `null`인 경우 RESULTS에 key가 없어도 통과시켰다. 검토자는 `cross_mode_total: null`을 이용한 실제 소형 반례를 보존했다. Root가 `key not in result or result[key] != value`로 정확히 한 줄을 수정했다. 검토자가 수정된 source에 같은 반례를 적용해 missing-null 거부와 present-null 허용 두 경우를 직접 확인했다. 두 경우 모두 PASS이며, 다른 코드 변경은 없다.

- 최종 wrapper SHA-256: `ab1b07c45136b77bf492148fa3e7560d2c2f02cb5650a6d0de5fc4fe00244a79`
- RUN_LOCK SHA-256: `cdfda6cd49eeb38518b2a41156a087f744e0985e0384bf628ca8b893dbec5b3a`
- 후보 집계기 SHA-256: `a3f854bc3c175cdaed36c7f475ff594c59056855ea5236c2eba844570c2861ee`

최종 source의 실제 verify-only receipt는 `VERIFY_ONLY_READY`, budget child 0, physics 0이다. 이는 수치 결과를 NCP에서 재현했다는 판정이 아니다. **실제 NCP 실행과 receiver adoption은 NOT_RUN**이다.

## 보존한 경계

초기 local PATHS 복원본이 118,002 bytes 짧았던 문제가 candidate/independent raw 집계 전에 발견되었다. 원 archive stream 확인과 실제 저장된 파일 identity가 달랐다는 기록이 보존되어 있다. 새 복원본을 exclusive write, flush/fsync, atomic rename, persisted SHA로 확인한 뒤 사용했으며, 검토자의 한 번의 raw pass도 정확한 292,932,850 bytes와 지정 SHA를 재확인했다.

Full finite captured-grid 결과가 있어도 node 사이의 spectrum, 연속 quadrature 오차, frozen capture 밖의 모델 변화, 새 gas evolution, 시간 구간 확장, 실제 photon/heat/recoil 전달, physical/global/production admission은 자동으로 닫히지 않는다. 이 항목과 receiver adoption은 HOLD다. 원 path enclosure의 과학적 유효성은 앞선 검토를 상속하며, 이번 독립 검토는 저장값의 정확한 합성과 제한된 runtime 계약을 확인했다.

최종 외부 게시, 백업 provider acknowledgment와 outer archive identity는 이 판정 뒤의 전달 절차가 담당한다. 이 검토는 아직 수행되지 않은 원격 업로드나 NCP 실행을 인증하지 않는다. 세부 check counts, 발견 사항, 닫힌 수정 및 판정 당시의 정확한 파일 identities는 같은 디렉터리의 `INDEPENDENT_REVIEW.json`에 기록되어 있다.
