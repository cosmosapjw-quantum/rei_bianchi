# RUN13 중단 복구: 완료된 M2 자료와 재개 상태 연결

복구 기록일: 2026-10-19 KST. 원래 계산과 archive 저장일은 2026-10-18이다. 사용자 요청은 중단 지점 재개이며, 기존 요청의 GitHub·Drive·Dropbox 보존을 우선한다. 이 문서는 실제 수치 재실행 보고서가 아니라 이번 턴에 읽은 저장 증거의 연결과 재개 지점 교정이다.

## 1. 현재 실행과 과거 실행의 구별

이번 턴의 샌드박스 terminal은 초기·최소 진단에서 ClientError, Python은 초기·최소 진단에서 ServerError였다. 새 native 적분 endpoint=0, 새 Rust/Python 테스트=0이다. 동일 실패 호출을 반복하지 않았다. 사용자 local/Codex/NCP/SSH, 외부 계산기 provision 및 native subagent는 NOT_RUN이다. 원본 owner, 입력, main, production, 이전 archive는 수정하지 않는다.

재조회한 RUN13 branch HEAD는 040a019ec47fb1eefdda67e7c9ef60c34ce000dd였다. 이 commit의 RUN12_BACKFILL.md만으로 후속 M2 실행 상태를 판단하면 안 된다. RUN11 실행 부모는 56e39a0783e85cc83339d0d3ee2a89b45f7c92ee다.

## 2. 이번 턴 직접 찾은 실제 보존물

(A) 중간 checkpoint: REI_RUN13_M2_CHECKPOINT_3071_20261018.zip, 175028 bytes. Dropbox id:BSpOijBcT10AAAAAAD_NTw, Drive 1lv8s9ClA7nQoDqj2ZpBj6q-g_tmV5bN-. 이 파일은 더 나중의 endpoint보다 오래된 상태다.

(B) 표준 M2 endpoint: REI_RUN13_M2_STANDARD_ENDPOINT_20261018.zip, 633373 bytes. Dropbox id:BSpOijBcT10AAAAAAD_Nkw, 2026-10-18T13:59:19Z. Drive 1ZoIMTkpWVltXb6ZlNMbhvKcAT4f7dEiZ. Dropbox의 추출 본문에서 evidence/joint11_sided_m2_3e-11/result.json과 비교 자료를 실제 읽었다. packet_sha256=67ec6958ac6f662125e049003d785c917c89e832b6bcbbd026ab8a332870b88a, rtol=3e-11, next_segment=6241. 저장 m2_observable의 T_K=9994.35124339563, x_HII=0.10027983872729747, x_DII=0.10117088882903148, x_HeII=0.15026849599222014, x_HeIII=0.049974479296611134를 확인했다. 추출 텍스트 판독이지 이번 턴의 raw ZIP hash/state-array 실행 검증은 아니다.

(C) 후속 전체 M2 패키지: REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip, 41075268 bytes. Dropbox id:BSpOijBcT10AAAAAAD_Ntg, path /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip, modified 2026-10-18T14:23:38Z. Drive 1TN5FKkuYz0cyX2Tcizhx0ZO98gNfI6Tt, created 2026-10-18T14:23:02.550Z. Drive folder listing로 이 ID와 크기를 확인했다. 검색의 빈 결과는 파일 부재가 아니었다. Dropbox text fetch는 5MiB 제한 때문에 거절됐다. Drive 반환으로 conversation file_00000000726c8206a63a3c0b57989a64가 생겼지만, 현재 runtime으로 ZIP을 해시·해제·실행하지 못했다.

전체 패키지의 제공자 확인 URL:
https://drive.google.com/file/d/1TN5FKkuYz0cyX2Tcizhx0ZO98gNfI6Tt/view?usp=drivesdk
https://www.dropbox.com/preview/BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN13_M2_CONVERGENCE_20261018.zip

## 3. 후속 감사 보고서가 뒷받침하는 범위

Library REPORT_KO(20261018-155922).md, file_00000000fc2481f7bee540d3bbedbbec, section 4를 읽었다. 자료 기준은 2026-10-18T15:51:13.799555Z / 2026-10-19 00:51 KST다. 다음은 그 보고서의 보존 자료 검토 결과이며 이번 턴 재실행이 아니다.

- 전체 ZIP SHA256=6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96. 332 manifest 항목과 source/input/core-Python 113개를 복원해 일치를 확인했다고 기록한다. 이 해시는 AUDIT_REPORTED_EXPECTED_HASH이며 이번 턴 재계산한 hash가 아니다.
- M2 standard rtol3e-11과 tight rtol6e-12의 두 전체 이력, 각각 6241 intervals·40357 상태변수가 있다. 17+12=29 process 기록은 27 IN_PROGRESS와 2 COMPLETE로 구성된다. 29개를 독립 과학 사례 수로 세지 않는다. M1은 RUN11 보존 이력이다.
- tight−standard M2 생존수 상대 차이: -1.4510065848745367e-15. 온도 절대 차이: +1.8189894035458565e-11 K.
- tight M2−tight M1 생존수 상대 차이: +8.402338343533361e-6. D I 누적 흡수 상대 차이: -1.5577803223133485e-7. 이 값들은 유한 구성 차이이며 continuum error bound가 아니다.
- 첫 셀의 최종 H fit edge 아래 생존수는 3.963580101474543e-12에서 8.255385244169650e-12 comoving m^-3로 변한다. 작은 성분에 대한 상대 차이는 약0.5198794503이다. 전체 생존수의 약0.000840% 차이가 이 성분의 수렴을 보장하지 않는다.
- 보존된 생산자 로그는 Rust160, 기존 Python11, 새 endpoint/protocol guard10 통과를 기록한다. 이 테스트 수를 이번 턴 PASS로 표기하지 않는다. standard tail replay는6156→6241의85구간이며 전체 초기값 문제 재실행이 아니다.
- 적분기 내부 시간 합은327.991849170+322.900004407=650.891853577초로 기록된다. 29 process의 rounded elapsed합702.18초와 중복 합산하지 않는다. build/I/O/분석/과거 손실 작업 비용과도 구별한다.

현재 핵심 결론은 'M2를 아직 한 번도 끝내지 않았다'가 아니라 '완료된 저장 M2 자료가 있으나 원격 branch에 결과·source 연결이 뒤처져 있다'다. tight 자료는 위 후속 감사의 직접 판독을 통해 확인한 상태이며, 이 턴에서는 tight state array를 독립 해제·검산하지 않았다.

## 4. 물리·오차 경계

Prescribed BASS121 SIGNED_MINUS, X=ln(a/a_ref), a_ref=1/21, X=.7.. .7004; birth160·GL8·다른47 source cells·native atomic providers·제조 gas IC는 고정된 과거 계산이다. H fit edge13.6eV와 binding13.598434599702eV, D의 기존 threshold-gated H-equality 근사는 서로 구별한다. 이 문서는 물리 모델이나 입력을 변경하지 않는다.

광자 회계의 두 해 차이는 DeltaP+sum_a DeltaA_a-DeltaB=DeltaR이다. 이 항등식으로 source/event/잔차의 일관성을 볼 수 있지만, 작은 DeltaR만으로 DeltaP 또는 작은 sub-H 성분의 정확도를 승인할 수는 없다. 유한 M1/M2 두 점으로 차수를 정하거나 차이를15로 나눈 값을 자동 오차 상계로 쓰지 않는다. M4, spectral asymptotic order, 엄밀한 continuum enclosure는 미확립이다.

## 5. 새 재개 계약

1. checkpoint3071 또는 RUN11의 'm2 NOT_RUN' 상태에서 자동 재시작하지 않는다. 위 전체 RUN13 ZIP을 실행 상태의 우선 복구 자료로 사용한다.
2. runtime이 사용 가능해지면 실제 bytes를 SHA256와 대조하고 내부 manifest, 최신 RESUME/DAG, standard/tight state와 로그를 읽는다. 필요한 gas_rhs_server는 동일 source와 명시된 toolchain으로 다시 build한다. archive에 없다는 이유로 저장된 과학 결과를 새 실행 PASS로 바꾸거나 폐기하지 않는다.
3. source/result의 정확한 파일을 회수한 뒤 GitHub에 실제 source delivery를 별도로 완료한다. 이 문서는 복구 보고서와 자료 링크이며 전체 소스 게시를 대신하지 않는다. 과거 RUN06을 포함한 Git-only standalone restore도 아직 주장하지 않는다.
4. 실제 최신 DAG를 읽은 다음 첫 셀 sub-H 성분과 M4 또는 광학 에너지층 진단의 우선순위를 결정한다. 이번 복구에서 새 물리 leaf를 임의 완료하거나 native M4/새 source를 실행하지 않는다.
5. 연속 spectrum/angle/birth, whole donor, full EoR, Einstein reaction feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full 및 Li/Be/nuclear T1–T8 의무는 유지한다.

```json
{
  "schema":"rei.run13.recovery_overlay.20261019.v1",
  "selected_node":"P4-S4C-SPECTRAL-EDGE-SUPPORT/M2-CONVERGENCE",
  "recovery_objective":"connect_existing_completed_evidence_and_finish_publication",
  "standard_m2":"ARCHIVED_ENDPOINT_TEXT_READ",
  "tight_m2":"ARCHIVED_COMPLETION_SUPPORTED_BY_LATER_AUDIT",
  "raw_full_archive_reverified_this_turn":false,
  "fresh_native_endpoints":0,
  "fresh_native_tests":0,
  "native_runtime":"BLOCKED_CLIENTERROR_SERVERERROR",
  "stale_checkpoint_restart":"DO_NOT_AUTOMATICALLY_RESTART_3071",
  "next_operational_action":"restore_full_RUN13_latest_DAG_and_publish_exact_source_files",
  "spectral_continuum":"NOT_ESTABLISHED",
  "sub_H_fit_edge_component":"UNCONVERGED_FINITE_PAIR",
  "full_source_Git_backfill":"NOT_COMPLETED_BY_THIS_NOTE",
  "native_subagent":"NOT_RUN",
  "production_mutated":false
}
```

새 전달 영수증은 이번 문서의 실제 commit/Drive/Dropbox 쓰기 결과를 별도로 기록한다. 이미 있는 20261018 전체 ZIP은 덮어쓰거나 새 계산 백업인 것처럼 재명명하지 않는다.
