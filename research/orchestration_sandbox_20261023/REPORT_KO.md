# 2026-10-23 KST 선택 연구 단위 재개 결과

이번 루프는 선택한 세 단위 N1/N5/N7의 구현·독립 심사·게시를 마쳤다. 전체 프로젝트 완료를 뜻하지 않는다. 과거 HANDOFF074933f를 기준으로 약48시간2026-10-20T17:34:46Z→2026-10-22T17:34:46Z의 저장소별 open PR30개, 선택한 현재 branch 및 접근 가능한 일부 대화를 조사했다. 전체 대화·미게시 NCP 실행의 전수 조사는 아니다. 실제 스킬은 intrinsic1.0.0/approval v0.2이고 과거1.3 표기는 역사적 라벨이다.

|노드|현재 판정과 범위|
|---|---|
|N1|norm hook+finite matched pair PASS_SCOPED, 게시 완료. work counters UNKNOWN|
|N2|REC124 Compton8 완료309.202/1200초 재사용|
|N3|CCC 새 branch5750489의 H1 finite-core4 완료 결과 재사용; tail/CI 미완료|
|N4|D PI/RR source-qualified number/energy moments 미완료|
|N5|제공된 isotropic pseudo-Maxwell pair moment PASS_SCOPED_AFTER_CONCRETE_REPAIR, 게시 완료; empirical transport 미완료|
|N6|atomic156+별도2, local-flow103+별도96 조건부 operator 재사용; physical branching/energy 미완료|
|N7|saved35 histories153epochs PASS_SCOPED, 게시 완료; 누적 CPU 한도 입증 불가|
|N8|물리 의존성 대기|

N1은 정확히 짧은 cosmological IVP2회로 구성된 한 paired run이며 replay0이다. 최대 full33 WRMS는7.222972526677901e-8≤1이고 inherited13 gates는 두 arm 모두 PASS다. hook 및 finite pair의 독립 심사는 통과했지만, unflushed serialization loss 때문에 RHS/Jacobian 등 work counters는 UNKNOWN으로 남긴다. N5는100 baseline checks(최대 정규화 오차1.8670464648487782e-15)를 재사용하고 zero/mass-ratio 결함의 targeted repair를 검증했다. 이 결과는 caller-supplied model에 한정되며 empirical collision coefficient를 승인하지 않는다. N7은35×153 saved samples에서5168 resolved sign agreements,0 violations,187 nearzero/unresolved,0 quadrature-sensitive를 관측했다. N7의 새 cosmological IVP/ODE/RHS/moment evaluation은0이다. N7 성공 pass는 CPU7.9283초/wall8.0215초이며, 이전 source-byte 실패 CPU는 UNKNOWN_NOT_ZERO여서 누적60초 한도는 NOT_ESTABLISHED다. 서로 다른 과거 cohort 수와 이번 실행 수를 합쳐 새 성과 수로 세지 않는다.

|게시 단위|과학 commit과 독립 readback|
|---|---|
|[N1 VigilODE](https://github.com/cosmosapjw-quantum/vigilode/commit/69e83044aacfb9a8fd2c6c3fb1146911beeedd79)|69e83044aacfb9a8fd2c6c3fb1146911beeedd79, HEAD+101/101 blob SHA1/size 일치|
|[N5 BASS_HE](https://github.com/cosmosapjw-quantum/BASS_HE/commit/96338b7d3c04b18e31a080e56b34985d31921104)|96338b7d3c04b18e31a080e56b34985d31921104, HEAD+42/42 blob SHA1/size 일치|
|[N7 REI D10](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e)|67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e, HEAD+24/24 blob SHA1/size 일치|

readback은 root가 현재 세션에서 확인했다. 과거 S1 ZIP는2311953바이트/SHA e400dee883c0cce8f30c1504e5428c2beb1922f8b8ee349be33371bcf1090f19와 로컬 CRC204 항목 PASS를 재사용하고 양쪽 provider metadata 크기를 확인했다. 새 full GET을 했다고 주장하지 않는다. 이번 S0는 최초 intake 당시의 불변 snapshot이고, 그 뒤 실제 양쪽 업로드 ACK 및30264바이트 일치를 확인했다. S0_BACKUP_ACK.json이 해당 사실을 구분해 기록한다. 이번 S1 reviewed-source ZIP는 최종 백업 ACK 이전의 고정 snapshot이며, 큰 과거 cohort는 pin/receipt로 참조한다. 코드·raw·필수 vendored source/license·D10 compact input·독립 심사·현재 master 문서와 SHA256 inventory를 담고 numerical rerun은 하지 않는다.

다음 물리 작업은 N4의 D PI/RR matched number/energy moments, N5의 source-qualified finite-mass differential transport, N6의 beta electron/neutrino/recoil energy partition 및 stopping/escape 조건이다. N3 tail/CI source-domain도 별도로 닫아야 한다. 이 의존성이 확보될 때까지 N8 closed pilot는 대기한다. 기존 결과를 다시 실행해 복구하거나 미제공 계수·branching을 만들어 채우지 않는다.

S1 실제 최종 보존 상태:2080062바이트/SHA2565861a00aa68edbdd154dbfac304a60906cc9e09751b8f4f947da62f4bc4b000b, 양쪽 provider upload ACK와 크기 일치, Library 저장 성공. 세부 ID는 DELIVERY_ACK.json에 있다. remote full GET은 하지 않았다. S1 ZIP 자체는 pre-ACK snapshot으로 그대로 보존한다. 현재 master 게시 후 실제 commit을 받아 S2 metadata를 만든다.
