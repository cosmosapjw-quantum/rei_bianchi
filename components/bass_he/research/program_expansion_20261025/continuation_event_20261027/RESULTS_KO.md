# HE-EXP-EVENT-03 결과 — 2026-10-27

## 완료한 범위

고정된 조성 관성질량과 명시적 상태 내부 에너지를 쓰는 비상대론적 `a+b -> c+d` 사건의 조건부 모멘트 공급자를 구현했다. 네 종·상태 ID, 질량, 내부 에너지, 입사 속도, 공급된 완전 CM 축대칭 각모멘트가 입력이다. 종별 입자수·질량·운동량·raw 운동에너지·전체 2차 텐서를 같은 사건에서 계산하며 같은 ID의 gain/loss를 합친다. 내부 에너지는 population-derived witness로 남고 독립 RHS에 다시 더하지 않는다.

`src/reactive_event.py`의 `reactive_moment_kernel`과 `explicit_flux_adapter`는 기존 INTAKE01 `AngularTransport`, `ConservativeSource`, caloric 객체를 변경 없이 import한다. Encounter flux는 호출자가 명시해야 하며, 출력 birth pool은 `UNASSIGNED`다. 열적 계수에서 DCS를 역산하거나 생성물을 자동으로 열적 pool에 넣지 않는다.

독립 최종 판정은 `evidence/INDEPENDENT_REVIEW_FINAL.json`의 **PASS_SCOPED_CONDITIONAL_EVENT03**, 남은 blocking finding 0이다. 이 판정은 아래 조건부 식·구현·저장된 유한 검증과 source intake에 한정된다.

## 실제 새 검증

새 테스트 22개를 한 프로세스에서 한 번 실행했고 모두 PASS, exit 0이다. 자식 CPU 0.206615 s와 runner CPU 0.0020403670000000013 s를 합한 실제 CPU는 0.20865536699999998 s, wall은 0.20785328000056325 s다. 새 cap 4 CPU s / 15 wall s / 256 MiB / 1 thread 안이며 실행 repair는 0이다. 원시 START/FINISH/stdout/stderr와 합산 원장은 `evidence/validation/`에 있다.

검사는 직접 discrete-angle/4-azimuth 생성물 속도 평균, 기존 탄성 커널 limit, 반응성 Galilean 입자수 항, 질량비·발열·흡열·임계점, trace·rotation·product label, zero/source/domain/표현범위 guard, caloric 단일 소유권, 변경된 R4 입력의 exact-ID/byte 관계를 다룬다. 실행 전 zero-flux가 잘못된 internal witness를 가릴 수 있는 경로를 교정했고 NaN/bool/inf 회귀검사를 첫 실행에 포함했다. 이는 실행 후 repair나 reserve 소진이 아니다.

저장된 합성 exact control은 `ma=1, mb=3, mc=md=2 kg`, `va=(4,0,0)`, `vb=0`, `epsilon_a=2 J`, 나머지 0이다. `Delta=-2 J`, `Ein=6 J`, `Eout=8 J`이며 종 순서 a,b,c,d에서 다음 값이 나온다.

| 양 | a | b | c | d |
|---|---:|---:|---:|---:|
| raw 운동에너지 증분, J m² | -8 | 0 | 6 | 4 |
| x 운동량 증분, kg m³/s | -4 | 0 | 3 | 1 |
| 단위 flux의 Gamma, m⁻³ s⁻¹ | -1 | -1 | 1 | 1 |
| 공통 u=(1,0,0)의 centered heat, W/m³ | -4.5 | -1.5 | 4 | 4 |

Centered heat 합 2와 internal witness -2가 상쇄된다. 이 값은 실제 물질의 측정 자료가 아닌 합성 sanity control이며 `stdout.txt`의 `CONTROL_JSON`에 저장되어 있다.

## 변경된 source intake

WU R4 `f949c21cca6e2534b725241068bd6c6e06158495`의 최소 원본 13개 파일, 231150 bytes를 보존했다. 14개 R4 species record 중 2개는 기존 exact compiler record와 같고 12개는 새 ID다. 기존 92개에서 합집합 **104 identity records**, provider **138 variants**, saved event **155 references**가 되었다. 이는 configured population 104종의 진화나 물리 승인 수가 아니다. 6 provider variants 중 material 2→2는 5개이고 photon을 포함한 radiative association은 별도 사건 공급자 범위다. TIQM/SQM 대안은 같은 소유권 그룹을 두 물리 사건으로 세지 않는다.

77개 source identity/관계 검사는 별도 준비 단계에서 PASS했다. 실제 준비 CPU 0.023842997000000005 s / wall 0.023843215996748768 s는 테스트 측정 구간 밖 비용으로 따로 보존한다. WU compiler, native fit, 기존 HE/WU/REC/CR suite를 다시 실행하지 않았다. 준비·모델·네트워크·IO 전체 비용은 `UNKNOWN_NOT_ZERO`이며 end-to-end cap 주장은 없다.

## 남은 입력과 보존한 경계

다음 물리 실행에는 선택한 사건의 정확한 isotope/state/branch, 조성 관성질량 및 상태 에너지와 그 불확도, energy-resolved `sigma0/sigma1/sigma2` 또는 승인된 완전각 law, 그리고 분포·encounter flux·CR cascade/stopping/deposition과 named consumer의 birth-pool 배정이 필요하다. 열적 rate 표가 이 입력을 대신하지 않는다. 광자·2→1+photon·다체 사건은 현재 두 massive-product 커널 밖이다.

HE101의 `C8=PARTIAL_EXPORT`, 전달 19/20, reserve 0, 기존 PASS/FAIL/FAIL 및 원장, INTAKE01과 DRIFT02의 실행·예산을 보존했다. 이 단위의 old START/old suite replay/physical campaign START는 모두 0이다. physical provider는 false, production은 `NOT_APPROVED`, activation은 false, global physical completion은 null, L4 ready는 false다.

## 게시와 전달 상태

R1–R9/C1–C9의 범위 내 source·이론·구현·독립검토 closeout은 완료했다. R10/C10은 게시 차단으로 partial이다. 세 번째 `create_tree` 거절은 앞선 DRIFT02 75-file/a12d5caa 후보에 대한 것이며 실제 도구 메시지는 `user rejected MCP tool call`, 사유는 null이다. 원격 HE는 ac6042에 있고 새 S와 중앙 DAG 변경은 없다. EVENT03 외부 쓰기 시도는 0이며 우회하지 않았다.

Source S `86306233ce74f5da73b862ec360d5f2ad5c679ca`의 ZIP은 Dropbox와 Drive에서 업로드 ACK 및 ID/size 확인을 마쳤다. 전체 재다운로드 SHA256 확인은 하지 않았다. 네 노드 중앙 후보는 독립적으로 로컬 metadata-only 승인을 받았고 게시하지 않았다. 이 전달 메타데이터를 고정하기 직전 관측에서 전달 후속 commit과 tail ZIP 및 tail 백업은 아직 준비 중이다. 최종 D03 SHA, tail ZIP과 실제 양쪽 ACK는 외부 `BASS_HE_EVENT03_CLOSEOUT_20261027.json`에 기록한다. 상세 상태는 `delivery/BACKUP_ACK.json`, `delivery/central/INDEPENDENT_REVIEW.json`, `delivery/PUBLICATION_BLOCK.json` 및 `HANDOFF_KO.md`를 따른다.
