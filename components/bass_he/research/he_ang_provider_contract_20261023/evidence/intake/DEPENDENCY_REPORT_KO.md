# HE-ANG 시작을 위한 HE-X1 의존성 확인

## 판정과 고정 핀

HE-X1은 **COMPLETE_SCOPED**이며 그대로 재사용할 수 있다. 중앙 브랜치 `research/orchestration-sandbox-20261022`의 실제 HEAD를 두 차례 읽어 모두 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`로 확인했다. 사용자가 제공한 고정 handoff와 동일하다. PR222는 open/draft다. 과학 커밋은 `eb03981d15ad291375dd6d574a9c28809f85fc02`다.

`AGENTS.md`의 Git blob은 `429a5a13ee75b1222bc50627f8d5973d01dd21c4`이며 X1의 정책 사본과 같다. 과학 커밋의 current_unit 20개 파일은 현재 pin의 동일 파일 20개와 Git blob 및 크기가 모두 일치한다. 현재 pin에 추가된 `X1_FROZEN_CONTRACT.md`는 과학 커밋의 `SOURCE_CONTRACT.md`와 같은 blob이다.

이 확인은 읽기와 저장된 증거의 해시/계수 확인이다. 새 이론 계산, 테스트 실행, IVP, render, benchmark, physical provider scan, 원격 변경은 모두 0이다.

## 재사용하는 완료 증거

`LOOP_PROGRESS.json`은 R1–R10 및 C1–C10 모두 완료다. 기존 `raw_outcomes.json`에 32 fixture, 181 assertion predicate, 7개 독립 exact oracle fixture가 있다. 32/32 fixture와 181/181 predicate가 PASS이며, 이 수는 기존 receipt를 읽어 센 것으로 재실행 결과가 아니다. 독립 검토 R6/C9는 PASS_SCOPED다. F1 overflow 수정은 첫 Python 실행 전에 완료되었다.

이번에 가져온 `raw_outcomes.json`, `moment_cone.py`, `test_moment_cone.py`의 SHA256은 독립 검토에 기록된 값과 일치한다. 단일 성공 실행의 **CPU-known = 0.57530726 s**, **wall-known = 0.5755462640008773 s**, tool process wall 0.584313263 s다. 실패한 `/usr/bin/time` wrapper는 Python 실행 전에 exit127이었다. 그 실패의 CPU는 **UNKNOWN_NOT_ZERO**이고 tool wall은 0.000038027 s다. 따라서 성공 실행만 10/30 s에서 차감한 수치를 누적 잔여 예산이라고 쓰면 안 된다. 기존 X1은 완료되었으므로 남은 명목 한도를 HE-ANG에 이전하지 않는다.

## HE-ANG 계약에 반드시 남길 물리 의무

- X1은 count2 비음수 inclusive 전자 측도의 2차 운동에너지 모멘트에 대한 조건이다. 공통 frame에서 `S >= 0`, `tr(S)=K`, `D=(3 a^T S a-K)/2`, `-K/2 <= D <= K`를 준다. 추상 spectral measure 구성은 eventwise 두 전자와 recoil ion의 공동 분포를 공급하지 않는다.
- 실제 각분포 공급자는 출처와 버전, 에너지/각도 support, exchange/전자 label, 느린 전자 포함 방식, inclusive count2 정규화, lab/COM 변환과 Jacobian을 명시해야 한다.
- 전자 `K_e,D_e`와 ion momentum/energy/STF는 같은 differential event law에서 나와야 한다. 공통 COM 에너지 장부 `K_e+K_p=E-I` 및 event momentum 보존 의무가 남는다. 단일 전자 marginal만으로 event correlation이 결정되었다고 주장하면 안 된다.
- CCC total과 일치 검증 없는 Le-Cambier partition을 곱해 물리 공급자를 구성하지 않는다. source uncertainty와 quadrature allocation은 각각 보정해야 하며, HE38의 raw 1e-8 기준은 해당 모델의 수치 기준이다.
- X1 tri-state와 `represented_input_only=true`는 유지한다. source-rounded 입력에서 물리적 source error를 binary64 roundoff로 치환하지 않는다. 양의 supplied uncertainty는 현재 구현에서 보수적으로 INDETERMINATE일 수 있다.
- 이번 HE-ANG은 공급자 계약을 먼저 고정한다. 물리 provider scan, 신규 IVP 또는 HE38의 완료 129T 재실행은 그 자체의 bounded scope/예산 없이 시작하지 않는다. PASS 시에만 새로 pin한 source model과 영향을 받는 moment 확인으로 진행한다.

원 계약은 `no_merge=true`, `no_activation=true`, `scientific_status=scoped_only`다. 전체 목표에 대한 완료율은 정의되지 않았다. HE32의 gas `pi_b=0`과 nonbaryonic matter stress를 구별하고, HE-CLOSURE에는 HE-ANG·HE-EXCHANGE·HE-RESERVOIR가 별도 선행 의존성이다.

## 병렬 소유자와 누적 예산

중앙 REI 계약의 ANGTHERM02 예약은 `research/rei-coupled-isotope-contract-20261022`의 `1d7fb4c303c6b6c6010b726211c60d0bf23e9e3c`이다. PR221을 새로 읽은 HEAD도 동일했다. 예약 상태는 `ACTIVE_OWNER_PREPARED_REMOTE_LOCAL_PREFLIGHT`이며 여기서 허용되는 행동은 read-only reuse, 신규 사례 0, 실행/수정 금지다. ANGTHERM01은 CPU 224.778756/300 s, wall 238.352717/420 s로 완료되었고 한도는 이전 불가다. D10 실패 초기 CPU는 UNKNOWN_NOT_ZERO이며 aggregate60s는 NOT_ESTABLISHED다. HE38의 실사용 ledger는 BASS_HE 소유자 원본에서 이어 받아야 하며 중앙 계약의 요약 문구로 재설정하지 않는다. **HE38·ANGTHERM01·D10의 모든 기존 한도는 nontransferable**이다.

컨트롤러는 별도 HE-ANG-contract 단위에 CPU 10 s / wall 30 s / RSS 256 MiB의 새 한도를 동결할 계획을 전달했다. 이는 작은 exact/event/frame 계약 확인에만 사용하며 provider scan 0, IVP 0, HE-X1 재실행 0을 유지한다. 이 계획은 기존 단위의 잔여 한도를 양도하거나 재설정한 것이 아니며 실제 사용량은 새 단위의 receipt가 기록해야 한다.

## 백업과 게시 확인

S0 `ORCHESTRATION_LONGTERM_20261023_S0_INTAKE.zip`는 Dropbox `id:BSpOijBcT10AAAAAAD_0-A`, Drive `1maYgIxEM-J06diYNumgDtQu1JUqjwzK5`이며 두 공급자의 새 metadata에서 65,722 bytes를 확인했다. 원 기록의 SHA256은 `30f64cbfdb793f6b87bed5b7ba92d694f9505e53fa5af8dd1230cca979d16b0e`다.

S1 `ORCHESTRATION_LONGTERM_20261023_S1_REVIEWED.zip`는 Dropbox `id:BSpOijBcT10AAAAAAD_1Cw`, Drive `1Ou6YaaO2fqwD4cBiGYX3IXUkC6b5EfAh`이며 두 공급자의 새 metadata에서 360,307 bytes를 확인했다. 원 기록의 SHA256은 `057b2a68d9200f472cddedc9d72c4a886ac4656841fba494f7d0ab5fb5852eb7`다.

두 Drive 파일의 parent를 별도로 새로 조회했으며 공통 folder는 `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`다. 원 기록은 `DRIVE_S0_LOCATION.json`과 `DRIVE_S1_LOCATION.json`에 보존했다.

이번 확인은 provider metadata의 identity/size다. 원격 ZIP 전체를 다시 내려받아 해시 검증하지 않았다. 읽은 longterm DELIVERY_ACK와 TERMINAL_HANDOFF에는 이후 S2 ACK가 아직 확정되어 있지 않다. 과학 commit의 expected-SHA/force=false push 및 77 blob 읽기 확인은 기존 DELIVERY_ACK의 보고를 재사용한다.

## 조사 범위와 사용 파일

고정 handoff, 중앙 AGENTS, X1 계약·이론·코드·기존 raw receipt·독립 검토·진척, 중앙 HE/REI 계약·DAG, 선택 PR222/PR221 및 S0/S1 metadata를 읽었다. 모든 repo/branch/과거 대화/backup 내용을 전수조사한 것이 아니다. 중앙 root recursive tree 요청은 Transport closed로 실패했으므로 전체 파일 inventory를 주장하지 않는다. `CURRENT_REFRESH.json`과 thermal survey의 타 저장소 HEAD 목록은 역사적 snapshot이며 이번 현재 HEAD로 재명명하지 않는다.

세부 출처 URL, local 경로, SHA256 및 Git blob 검증은 `EVIDENCE_INDEX.json`, 누적 예산·예약은 `BUDGET_AND_OWNERSHIP.json`, 백업 metadata는 `BACKUP_METADATA_FILTERED.json`에 있다. 현재 X1 완료 상태는 `snapshot/research/orchestration_longterm_20261023/assembly/DAG.json`의 HE-X1 wrapper에 명시되며, 원 계약의 `current_unit_selected`는 역사적 선택 문구로 보존되어 있다.
