# BASS_HE 원문 snapshot 조정

2026-10-10 읽기 결과다. 저장소와 최신 handoff의 실제 내용·identity만 확인했으며 새로운 과학 판정은 하지 않았다.

## 현재 기준

- 저장소: cosmosapjw-quantum/BASS_HE
- 활성 연구 branch: research/shared-c64-crossrepo-20260928, draft PR #17
- read snapshot: 81c1dacc1439807d41dc2684619dee499f3e06b0; tree bbbbaa0fcd39d6993699db0034275b1761215666
- 최신 core 연구: f7199c5c100578fa345b026cd6d4ac8e983e50a9; E13C1 photon chronology/frozen-transaction 독립 평가
- 바로 앞 부모: 14092a1c79916c5074005fa0a3bbf175ce8dc29a; E13B 독립 material RHS 봉인
- 최신 NEXT_DAG는 E13C2_VARIABLE_COEFFICIENT_BIAS_ON_FIXED_GAS_PATH를 가리킨다. 같은 저장 affine gas path에서 연속 q(s), lambda_i(s)와 frozen-stage approximation을 비교한다. 새로운 full 3x384 이력을 요구하지 않는다.

원문 디렉터리: docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/runs/HE-E13C1-PHOTON-PHYSICS_20261010/

## 서로 다른 E13C1 archive

원격 정본은 BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1.zip(4,096,240 bytes, SHA256 06b5c02afb92e356ec66072a918e014f61fab5a795f26024fae55ca4d93acb33)이다. Git DELIVERY_RECEIPT가 이 archive와 Drive/Dropbox 객체를 명시한다. 부모 agent는 Drive 실제 다운로드와 SHA 일치 및 local 복원을 완료했다고 보고했다.

별도 BASS_HE_E13C1_PHOTON_HEATING_20261010_v1.zip(914,879 bytes)은 부모 agent의 원문 확인상 같은 14092 부모에서 나온 NOT_PUSHED 병렬 draft다. 그 안의 late k7/k59 node stock/grid missing은 별도 열린 문제이며, 이미 게시된 PHOTON_PHYSICS E13C1을 무효화하거나 다음 E13C2를 교체하는 근거가 아니다.

## source lineage

receiver original rei_bianchi@39c39eab1cc2f1a215723680accc123e67ef13b6의 radiation/coupled/material 파일을 그대로 E13 실행 source로 사용하면 안 된다. E10에서는 coupled c75a15bd, material 2f0527c3, radiation 94113ecd로 patched되어 있었다. 전체 patched source/CSV/grid/node witness는 4MB 정본 archive에서 받아야 한다. 원격 BASS_HE에서 이 patched blob 3개를 직접 조회하면 404였으며, 최신 Git projection은 전체 실행 입력을 포함한다고 주장하지 않는다.

receiver_original/ 아래에 저장한 파일들은 위 lineage와 stage 의미 파악용이다. E13C1 code/photon_green.py는 게시되어 있고 blob d0c5f6b944cbdde0ad051bcbc749f396b9a47d96와 일치한다. external finite escaping E^-2 source q 및 Verner opacity를 계산하며 이를 실제 RCT 자발방출 spectrum으로 해석할 근거는 없다.

## 이전 시작문과 현재 gate

CURRENT_FASTEST_STATE.json과 CODEX_START_KO.md는 HE-F2/F09 및 10/05 owner synchronization을 주로 기록한다. source domain/변경 제한은 참고할 수 있지만, 최신 완료 연구 node는 10/10 E13C1 NEXT_DAG로 판정한다. main@6ef63136도 활성 연구 branch가 아니다. PR17 본문의 과거 요약은 최신 exact-head 파일보다 우선하지 않는다.

보존할 제한은 baseline RCT OFF, actual atomic photon/heat/recoil moments null, physical/production HOLD, HE-F2/F09 OPEN, receiver owner adoption 별도, legacy Gamma alias 3.543295 FAIL이다. 여섯 frozen transaction의 유한 검증은 전체 stage coverage 또는 continuous interval certificate로 확대하지 않는다.

## 파일 identity와 작업 범위

primary 원문16개 및 secondary10개, 총26개 파일의 Git blob identity가 원격 반환값과 일치한다. INTAKE_SOURCE_MANIFEST.json과 SECONDARY_SOURCE_MANIFEST.json이 원 repo/ref/path/blob/URL을 보존한다. 원격 변경0, 과학 계산0, 과거 suite 재실행0이다.
