# HE-EXP-APERTURE-07 — 완료 범위와 재사용 인계

## 1. 현재 판정과 이 기록의 시점

요청한 이론 R1–R10과 코딩 C1–C10의 한 번의 루프에서 작업 산출을 완료했다. 판정은 **ACCEPT_SCOPED_CONDITIONAL_APERTURE_REFERENCE**, workflow는 **COMPLETE_SCOPED_CONDITIONAL**이다. continuation DAG는 **8 complete + 0 pending + 3 physical open / 11**이다. 중앙 원 DAG는 **28/88**, 이번 HE delta는 **0**이며 서로 다른 두 카운터를 더하지 않는다. 물리적 전체 완료는 null, L4_ready는 false, production은 NOT_APPROVED다.

이 문서와 closeout JSON의 metadata_scope는 **PREPUBLICATION_S10_WORK_PRODUCT**다. S01–S09의 source 게시와 Drive/Dropbox 양쪽 백업 ACK는 실제 **9/9** 완료했지만, 이는 요청한 열 체크포인트의 **9/10 prefix**다. S10 작업 산출의 완료와 S10 게시·백업 완료를 구분한다. 이 커밋 안에서 S10 원격 게시·백업이나 APERTURE07 중앙 게시가 이미 성공했다고 주장하지 않는다.

S10 delivery의 로컬 소스는 **이 파일을 포함하는 containing commit**이다. 자기 커밋의 해시와 tree를 미리 만들지 않는다. 실제 S10 로컬 commit/tree, 원격 P10, 두 provider ACK와 중앙 실제 CAS 결과는 발생 후 root가 관리하는 외부 최종 전달 영수증에 기록한다. 현재 S10은 **PENDING_POST_COMMIT**, 중앙 APERTURE07은 **PENDING**이다.

## 2. 검증 소스와 채택 소스의 구분

| 용도 | 로컬 실행·소스 commit | 동일 tree의 원격 게시 commit |
|---|---|---|
| 실제 새 검증 S05 | `3e41e230ff028fe28eb8aa35d9d6fecb1b22fd1f` | `1e6d82845e922e0d733be3d2f80e9bd2efc41e04` |
| 독립 검토 후 과학적 채택 S09 | `39dd3b52ad87cfa2298c1f6897bf7d34991d1224` | `2f53703f621791a004c3ad13fa7e012536ab2cf6` |
| 최종 S10 전달 작업 | 이 파일의 containing commit | 실제 post-commit ACK 후 외부 영수증에 기록 |

S05 tree는 `7cbae861703372250bca3de54c08eac04a61a057`, S09 tree는 `5c58752ba5e8cf3ea58d186f67f79499a585d421`이다. 로컬 commit과 원격 API 게시 commit은 서로 다른 식별자이며, ACK가 확인한 동일성은 각 단계의 **정확한 Git content tree**다. 로컬 해시 자체가 원격에서 reachable하다고 추정하지 않는다.

S09는 source ref ACK와 실제 readback을 확인했다. 해당 S09 ZIP의 Drive ID는 `1ZrNeHByLyA9puzdGiJnUf9JWH73fk-fm`, Dropbox ID는 `id:BSpOijBcT10AAAAAAEDIGQ`다. 기존 외부 `he07_checkpoints/STAGE_ACKS.json`의 S01–S09 원문을 byte-exact로 복사한 `publication/STAGE_ACKS_THROUGH_S09.json`에 아홉 단계의 로컬/원격 source, tree, ZIP 및 provider ACK가 있다. 파일 이름의 THROUGH_S09와 이 절의 9/10 범위를 유지한다. 이 prefix를 최종 열 단계 영수증으로 해석하지 않는다.

선행 ANGULAR06은 source P06 `12702837bf3b2dd2af6439efe08ec4088e3adc90`, 중앙 게시 `8af3e56dcaa27a8362b2bf74d6fb3c8edd859413`로 이미 게시되었다. 상세 근거는 `preflight/ANGULAR06_PUBLICATION_RECEIPT.json`이다.

## 3. 재사용할 수학적·계산 제품

고정 저장 parameter γ∈[1,10^6], a∈[0,10^6]에 대해 조건부 CM-to-lab map의 역상을 유리수 inner/outer 구간 합집합으로 감싼다. 부호를 먼저 판별하므로 제곱식의 가짜 branch가 들어오지 않으며, a>1의 두 단조 branch를 모두 포함한다. a=1의 정지 endpoint에는 관측 방향을 부여하지 않는다. 영측도 endpoint를 제외하는 논리는 연속 measure에 한정되며 atom과 κ=0은 명시적으로 지원하지 않는다.

밀도는 degree≤8의 비음수 Bernstein 계수로 지정한다. 이는 충분한 양성 클래스이며 모든 양의 다항식을 특성화한 것이 아니다. 짝 사건 API는 palindrome 계수, 즉 even polar marginal을 요구한다. 입력 scalar는 int, rational/decimal 문자열, Fraction 또는 유한 float의 정확한 저장값이며 bool과 nonfinite 값은 거절한다.

signed 선형 weight W=w₀+w₁μ는 불확실 영역 O\I에서 정확한 유리수 부호 전환점으로 나누어 적분 하한·상한을 계산한다. 같은 사건의 두 딸입자는 μ와 −μ를 공유한다. 두 검출기 assignment의 합집합으로 사건을 한 번만 세고, coincidence Y·창별 사건 hit H·inclusive daughter count N을 구분한다. 선택된 coincidence의 daughter measure는2Y다. E±=E₀±E₁μ는 공유 integrand에서 먼저 합하여 직접 pair-energy=2E₀Y를 감싼다. 개별 E+·E− 구간의 끝점 합이 항상 동일한 최적 구간이라고 주장하지 않는다.

기본 API는 δ=σ_event·2^-40/(16M)를 선택하여 사건 질량 경계 폭≤σ_event·2^-40를 보장한다. 영밀도는 정확히0으로 처리한다. 저장 native/fold 예들은 수동 δ=2^-40을 사용했으므로 각 실제 반환 폭과 width_bound가 해당 인증 범위다. 수동 δ를 쓴 모든 관측량에 기본 상대 폭 목표가 자동 달성되었다고 주장하지 않는다.

기하는 방위각 전체를 받는 annular 극각창이다. 이미 방위각에 적분된 polar marginal을 사용하므로 방위각 균일성을 새로 가정하지 않는다. 유한 φ patch를 가진 실제3차원 telescope acceptance는 이번 제품이 아니다. parameter 인증도 저장 γ,a에 대한 조건부 인증이며 실제 질량·에너지에서 그 값을 얻는 변환 오차나 물리 parameter 불확실성까지 인증하지 않는다.

## 4. 실제 실행과 독립 판별

| 근거 | 실제 결과 | 자원·반복 경계 |
|---|---|---|
| 새 구현 suite | **32/32 PASS**, 한 번 실행, repair0 | CPU **0.235556515/4 s**, wall **0.24653371299791615/15 s**, memory256MiB, 1thread |
| Wolfram 기호 판별 | basis 질량45개 + 선형 weight45개 + fold2개 = **92개 영잔차**, 원 부호·domain 두 개 True | **1회**, timeConstraint15s; 원격 실제 CPU 미제공이므로 **null** |
| 새 저장값 plot | **PASS**, 한 번 실행, 과학 함수 호출 **0** | CPU **4.489548029/6 s**, wall **4.491183639998781/15 s**, memory512MiB, 1thread |
| 독립 검토 | 선행 정적18개와 실제 결과10개 검사 PASS, 결함0 | 같은 한 review pass의 후속 검토; 재귀 review 없음 |

검증과 plot의 측정 envelope는 준비·원전 접근·네트워크·모델 시간을 포함하지 않는다. 제외 비용은 UNKNOWN_NOT_ZERO이며0이나 end-to-end 측정으로 표시하지 않는다. 원격 CAS CPU도 로컬 측정 CPU에 넣거나0으로 바꾸지 않는다.

실제 검사 로그는 `evidence/validation/01_tests/`, 누적 원장은 `evidence/validation/RESOURCE_LEDGER.json`, 실행 입력은 `evidence/TESTED_DEPENDENCIES_01.json`에 있다. 새 저장값은 `evidence/validation/SAVED_PLOT_DATA.json`이고 SHA-256은 `240eb83fe9636fe2c2e58f81ae911be5238d9b7db79f1dbbd0c93ca8bc96f98d`다. 실제 plot과 START/FINISH/stdout/stderr는 `evidence/plot/`, 과학적 판독은 `evidence/PLOT_READ_KO.md`, 독립 최종 판정은 `review/RESULT_REVIEW.json`에 있다.

제조 fold 검사의40-bit 질량 구간은 약 [0.5291502622124881,0.5291502622132611]이며, 정확한 끝점의 양의 제곱으로7/25를 감싼다. 공유 사건 counterexample에서는 coincidence1/2와 marginal hit product1/4가 다르고 coincidence daughter measure는1이다. native12 계산은 기존 저장 `source_row,γ,a`만 사용해 명시적 합성 밀도 b=[0,3/2,0]의 새 aperture 적분을 수행했다. DCS·통계 오차·실제 flux를 새 계산의 밀도로 사용하지 않았다.

## 5. 선행 조사 범위와 중앙 게시 경계

게시 후 source census의 고정 cut은 **2026-10-27 14:30:03–14:30:11 UTC**, 원자적 snapshot은 아니다. 다섯 repository에서 branch metadata의 모든 pagination terminal을 확인하여 **895 branches**를 조사했다: BASS_HE108, rei_bianchi282, WU088_HH159, bass_cr188, rec_bianchi158이다. 과학적으로 관련된 commit/file body는 선택해서 읽었으며 모든 repository tree와 모든 본문을 읽었다고 주장하지 않는다. 비공개 대화는 접근 불가로 전체를 읽지 못했다. 과거 백업은 provider metadata와 기존 source receipt만 읽었으며 archive body 재독·다운로드·재생성은 없었다. 근거는 `preflight/SURVEY_SUMMARY.json`과 그 source manifest다.

중앙의 과거 reviewed base와 현재 게시 기준은 다음처럼 구분한다.

| 역할 | 실제 commit |
|---|---|
| PHOTON05 원래 candidate의 reviewed base | `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5` |
| 이후 B3h를 관측한 ANGULAR06 reviewed candidate base | `152b82cac23fedcb75a9effe0c159bae3d800c01` |
| 실제 새로 읽은 ANGULAR06 게시 base | `74aff0740d1812c732466563a9c66108a3a4d8fd` |
| 그 base에서 실제 완료한 ANGULAR06 중앙 게시 | `8af3e56dcaa27a8362b2bf74d6fb3c8edd859413` |
| 현재 APERTURE07 준비 candidate base | `42cc3a909688d670200ba09c500e2ca83a94fa10` |

따라서74aff를 PHOTON05의 원래 reviewed base로 부르지 않는다. 현재42cc base에는8af 이후 REC와 CR 변경도 들어 있으며 보존한다. root가 실제 최신 HEAD와 AGENTS를 다시 읽고 최신 타 repository/B3h/CR/비관측 필드를 보존한 HE-only delta를 실제 expected SHA, force=false로 게시한다. 이 사전 S10 기록은 APERTURE07 중앙 CAS 성공을 선기록하지 않는다. 실제 결과는 post-commit 외부 전달 영수증을 따른다.

## 6. 유지되는 물리 입력과 역사 기록

계속 열린 세 물리 입력은 다음과 같다.

1. 원 M0475002/Arends 실험의 실제 정규화와 liquid-He electronic/target-motion/response projection.
2. 실제 완전 각분포와 photon encounter flux/history.
3. 명명된 비열적 birth/deposition/thermalization consumer 및 global species binding.

Rice 원전에서 확인한 해당 실험의 동일 입자 규약을 미확인 M0475 규약으로 이전하지 않는다. particle number, Cv, rest/binding, 비열적 energy와 thermal 항은 별개다. rest/binding은 `population_rest_energy_witness`에 한 번만 속한다. 독립 binding RHS, Gamma_thermal, Cv, species_heating, thermal_deposition은 null, birth_pool은 UNASSIGNED다.

PHOTON05 source `251c6baa6c3359b1d6997dbce51cea65500b53d6`, delivery `4db5ce7297a7ded4624b93721873aacc9b4ebf30`의 원 결과는 **24/24 PASS, plot CPU4.40726504>4 s FAIL, workflow PARTIAL, 4 complete +1 partial +3 physical open /8** 그대로다. HE101은 **C8 PARTIAL_EXPORT, 19/20, reserve0, 원 PASS/FAIL/FAIL** 그대로다. 이 기록을 새 APERTURE07의 PASS로 덮지 않는다. 기존 과학·suite·plot·백업 재실행이나 과거 예산 reset/transfer는 없다. S10 도구는 새 S10 전달 archive만 준비하며 과거 archive를 재생성하지 않는다.

## 7. 다음 담당자가 이어받을 위치

계산을 재사용하려면 `ACCEPTANCE_KO.md`의 가정과 `THEORY_KO.md`의 포함 논리를 먼저 유지하고, 새 입력의 정확한 parameter·밀도·measure/weight 단위를 선언한다. 현재 구현·검증 bytes는 S05에서 고정되었으며 이번 closeout에서 바꾸지 않았다. 현재 과학적 채택 상태는 `RESULT.json`, `DAG.json`, `review/RESULT_REVIEW.json`에 있다. S01–S09 게시·백업은 prefix receipt, S10과 중앙의 실제 게시·백업은 외부 최종 전달 영수증으로 구분한다.

**이번 요청의 이론·코딩 루프는 여기서 끝난다.** 이 인계는 자동 새 node, 후속 loop, 추가 과학·test·plot 재실행이나 새 예산을 허가하지 않는다. 다음 사용자 지시가 있으면 이미 채택된 정리·소스·실제 검증·게시 tree를 재사용하고 새로 지정된 목적만 수행한다.
