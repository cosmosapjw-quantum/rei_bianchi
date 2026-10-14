# 다음 실행 인계 — RUX-P0

## 목표와 범위

**이미 있는 H/He–열–광자 결합 수치 골격에 한 가지 EoR 시나리오의 rate/domain·시간·광원 입력을 연결하고, 입력이 갖춰지면 첫 FLRW coupled interval까지 진행한다.** 이후 같은 입력의 Bianchi interval과 FLRW 다중 epoch history를 병행한다. 원자율 전체를 새로 유도하거나 F08/SYNC02/SYNC03를 재실행하는 작업으로 시작하지 않는다.

이 인계는 계획이다. 작성 세션에서는 RUX-P0, 물리 입력 archive admission, 과학 코드 실행·테스트를 수행하지 않았다. 사용자가 다음 구현/연구 루프를 지시하면 아래 묶음을 실행한다. 해당 루프 하네스의 검증은 바뀐 알고리즘과 새 주장에 적용하고, 변경 없는 과거 실험 전체의 반복으로 확장하지 않는다.

## 1. 현재 계획과 실제 실행 경로

저장소: `cosmosapjw-quantum/rei_bianchi`. 작업 브랜치: `forward/rust-reion-kernels-20260922`.

먼저 현재 branch/head와 관련 AGENTS, `docs/fastest_track_chat/CURRENT_PLAN.json`, 이 폴더의 README/PLAN을 읽는다. 이 문서 작성의 base는 `633e0bd26b40bf59e8dfe6b977edb6e6dacc144d`, 과학 소스 `rust/rei_microphysics/src` tree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`이다. head가 달라졌으면 관련 diff만 확인한다. 사용자의 기존 변경이나 다른 owner의 파일을 되돌리지 않는다.

과거 `docs/atomic_reionization_handoff_20261004_v1/`의 GLOBAL_DAG·TASK_CARDS·PR_PLAN은 요구사항/이력 참고다. 그 시점의 pending 상태로 F08/SYNC02/03의 후속 완료를 취소하지 않는다. 현재 계획은 17개 RUX 의무를 보존한 scheduling overlay다.

실제로 사용할 한 entry point를 고른다. Git의 `paired_runtime.rs` 소스와 F08 실행 기록은 존재하지만 현재 lib export는 없다. Dropbox에서 보고된 axisym 파일과 Git source는 동일성이 미확인이다. 필요한 파일·빌드 경로의 delta만 가져오고, 모든 백업·branch를 동기화하는 작업으로 넓히지 않는다. 새 solver를 만들기 전에 기존 primary microstep과 history composition의 호출 구조를 사용한다.

## 2. 입력·owner 작업을 같은 구현 묶음 안에서 진행

RUX00은 실제 선택할 소스의 identity와 기존 증거를 기록하는 작업으로 한정한다. RUX02 입력 계보와 RUX03 사건/rate 소유권은 독립 부분을 병렬로 처리한다. 새 물리 실행은 아래 필드가 갖춰진 RUX04 scenario를 사용한다.

| 필드 | 이번에 필요한 결정 |
|---|---|
| 배경·시각 | 시작/끝 epoch, a_i(t), H_i(t), t↔ln a_V/z_V, density 진화; ln(a)를 초로 전달하지 않음 |
| 초기 gas | proper n_H/n_He, 종 분율, T 또는 u_th, 전하·EOS convention |
| 초기 radiation | spectrum·각도·에너지 범위·정규화, per-H/comoving/proper의 변환 |
| 광원 | spectral history, emissivity/incident stock/boundary flux 역할, 단위, escape/clumping, 알려진 domain |
| 원자·열 공급자 | 실제 RHS에서 호출할 rate/thermal family, T·종·에너지 지원 영역과 provenance |
| 사건/경계 | photoabsorption, recombination transport/escape/OTS, thermal work, redshift work, 에너지·각도 경계의 단일 owner |
| 실제 호출 | provider callback과 time/source adapter가 선택한 primary 경로에 연결됨 |

이미 알려진 PR104 배경·scalar source와 보존된 C12 입력을 후보로 사용하되, 그것이 새 결합 모델의 모든 필드를 공급한다고 가정하지 않는다. PR104의 R15 number emissivity만으로 spectral source·초기 종/열 상태를 만들지 않는다. 반대로 오래된 N2 결손 목록을 현재 입력의 부재로 그대로 복사하지 않는다.

입력 archive 후보는 다음이다. Dropbox 루트 경로이며 존재 보고와 내부 admission을 구별한다.

```text
/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_BIANCHI_PHYSICAL_INPUT_HANDOFF_20261010_v2.tar
/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P01_PRODUCTION_20261010_c168e578.tar.gz
/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P02A_20261010_8a80fa9.tar.gz
/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P03A_20261010_d6ad8b7.tar.gz
/BASS_DERIVATION_DOSSIERS_20260912/REI_P03A_SOURCE_DELTA_20261010_05c45c3.tar.gz
/BASS_DERIVATION_DOSSIERS_20260912/REI_N2_LOCAL_INPUT_RESEARCH_20261010_v1/RECEIPT.md
```

먼저 manifest/내부 필드와 계보를 비교하고, 실제 필요한 payload만 읽는다. 압축을 풀 때 절대경로·상위경로 탈출·예상 밖 링크를 실행/덮어쓰기 경로로 사용하지 않는다. 전부를 재다운로드하거나 archive 안의 코드를 읽기도 전에 실행하지 않는다. 같은 byte/commit에 대해 이미 확보된 identity를 재사용한다.

필드가 null이면 0으로 만들지 않는다. source가 13.7 eV인 F08 fixture를 physical EoR로 재라벨하지 않는다. 입력이 부족하면 `PHYSICAL_INPUT_INCOMPLETE`와 정확한 결손을 남기고, 다음을 **한 개의 P0 physical-input selection task**로 고정한다. 공개 근거/기존 자료에 따른 scenario 선택은 명시적인 모델 가정으로 할 수 있지만, 선택한 값을 원래 제공된 데이터라고 쓰지 않는다. 근거가 없으면 물리 실행은 대기하고 실행 가능한 어댑터 작업·저장 결과 활용을 완료한다. 같은 N2/파일 목록 감사를 다음 루프에서 반복하지 않는다.

## 3. 이번 구현의 핵심

### 기존 단계에 rate/domain 주입

`coupled_primary.rs`의 `primary_stage_step_conservative`와 사건 장부를 유지한다. 현재 stage는 내부 FT03 모델/계수와 `AtomicProvider::reference()`를 직접 호출하므로, 선택한 EoR rate/thermal provider와 domain이 실제 RHS에 전달되도록 injection 지점을 만든다. 제공된 raw 값이 실제 실행에 도달하는지를 확인한다.

현재 primary 30,000–110,000 K, paired 35,000–60,000 K guard를 숫자만 넓히지 않는다. 새 scenario의 온도·종 영역을 지원하는 원천과 validation domain을 연결한다. raw `consumer_admission=false` 등은 단순 flag 편집으로 해소되지 않는다.

point solver만 바꾼 경우 old FT03 interval/root certificate를 새 계수에 붙이지 않는다. rigorous 경로를 쓸 때에는 point와 root/interval이 같은 provider·case·domain을 사용해야 한다. 새 point 경로의 결과는 실제 residual·보존·수렴 검증 범위에 맞게 보고한다. 기존 proof의 실패·범위는 수정하지 않는다.

### time/source/spectrum adapter

상수 H, SOURCE/BIRTH, t≤10^13 s, 10–20 eV fixture를 시나리오 입력으로 분리한다. He 광이온화를 주장하려면 실제 source support와 초기·경계 inventory를 갖춘다. 낮은 에너지의 H 전용 pilot를 선택하면 그 범위를 명시하며 full He EoR 결과라고 하지 않는다.

N_gq/energy/packet measure를 이용하고 bin 내부 spectrum closure를 유지한다. 원자 단면적 가중 평균과 heat moment를 임의 대표 광자 에너지로 대체하지 않는다. photon cutoff와 binding threshold를 구분한다. 입력 tail·upper/lower energy boundary의 처리도 명시한다.

### 단일 사건 소유권

primary의 photon loss·ionization·binding/heat·gas expansion work를 history에서 다시 더하지 않는다. `homogeneous_photo_rates`는 선택한 공급/대조 평가 경로로 쓰며 같은 흡수에 추가 sink를 붙이지 않는다. history는 기하·광원·photon redshift/face flux를 관리한다.

재결합은 명시 수송+Case A, Case-A escape 장부, 또는 Case-B/OTS 중 일관된 정책을 고른다. effective HI MFP와 local HI opacity가 같은 population의 같은 흡수를 두 번 처리하지 않게 한다. 여러 population을 분리해서 사용할 때에는 그 분해와 energy/photon 귀속을 기록한다.

기본 H/He 전하식에는 H−가 없다. HH ion-pair를 넣으면 H− 또는 적합한 제거 폐쇄와 전하식을 추가하며 HII 증가를 free-electron 증가로 치환하지 않는다. 고정밀 HE·hard-particle CR·HH/RCT는 baseline의 자동 입력이 아니다.

## 4. 첫 실행과 다음 연결

새 scenario를 고정한 뒤 첫 짧은 FLRW interval에서 실제 species·T·photons·Γ/heat와 nuclei/charge/photon/energy 장부를 출력한다. 새 rate/domain·time/source 경로, residual/양성성, 경계 처리를 확인하고 목표 관측량에 필요한 작은 refinement를 수행한다. 한 가지 연결 변경을 위해 기존 F08/SYNC02/03 전체를 다시 실행하지 않는다.

입력이 지원하는 실제 결과가 나오면 첫 구간 그림과 구간 τ를 즉시 남긴다. 이때 전체 EoR·observer-tail·polarized sky를 주장하지 않는다. 그 다음 같은 입력의 Bianchi interval(RUX07)과 FLRW 다중 epoch history(RUX08)를 가능한 부분부터 병행한다. 실제 paired source·clock·경계를 맞춰 RUX09로 이어간다.

처방 수송에서는 ne 고정이 가능하지만 coupled 대조에서는 ne/T가 각각 해로 나온다. 같은 평균 H와 같은 입력을 갖는 등방 수송 counterfactual을 별도로 두어 transport와 background 경로를 비교한다. zero shear, gas frame·단위·시간 경계의 대응을 확인한다.

RUX10은 초기 admitted 전자 구간부터 기존 BASS receiver에 연결할 수 있다. 전체 paired τ에는 그에 맞는 전체 이력과 observer tail이 필요하다. RUX11 그림은 각 단계에서 만들며, 전체 과학 주장·release(RUX16)에만 해당 모든 의무를 요구한다. RUX12–14 sensitivity는 중간 관측량의 오차 예산이 요청할 때 선택 활성화한다.

## 5. 대기 없이 활용할 기존 결과

PR104 baseline은 기존 pin을 사용한다. 이 branch의 `runs/rei_fastest_v1/paired/campaign_summary.json`, `paired_history.csv`, `paired_history.png`와 `docs/research_sync/REI-REC-BASS-SYNC03-20261007/README_KO.md`·그림을 재사용한다. Git의 paired CSV는 15 endpoint 행이며 시간곡선을 임의 보간해 full history라고 하지 않는다. source manifest가 가리키는 해당 이력이 필요한 경우에만 가져온다.

이 경로는 RUX02의 새 physical-input admission을 기다리지 않는다. 기존 FT-B1A의 작은 prescribed 방향 수송과 B1B의 실제 Thomson 진단도 독립 대조 연구로 가능하다. collisionless intensity는 xe에 반응하지 않으며 attenuation만으로 Thomson 산란을 대신하지 않는다. 이 대조 경로는 main coupled 연구의 선행 완료조건도 아니다.

## 6. 실행 비용·반환

경량 작업은 현재 환경에서 시행하고 실제로 없는 capability만 local Codex로 넘긴다. NCP에는 준비된 독립 사례와 측정된 wall/CPU/RSS 또는 구체적인 비용 근거, thread/동시 실행 제한, 유한 allocation/checkpoint를 제공한다. 64코어를 순차 time stepping의 64배 가속으로 환산하지 않는다.

반환에는 구현한 연결, 선택 입력과 미확인 필드, 실제 명령/exit code, 관측량·그림, 새 numerical/model error, 기존 결과 재사용 범위, 다음 한 작업을 포함한다. 실제 수행하지 않은 실행·원본 복원·scientific admission을 완료라고 쓰지 않는다. 이번 변경의 source/물리·수치 범위에 맞춘 검증 후 종료한다.

현재 operator가 이미 승인한 범위의 commit/push·산출물 보존은 이어서 수행하되 force push, 타 owner 변경·merge, 외부 job 취소를 자동으로 하지 않는다. 기존 Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, S0 HH/RCT/CR OFF, PHYS35 소진 예산과 PHYS36 DEFERRED 상태를 보존한다.
