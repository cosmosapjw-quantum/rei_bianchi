# THEORY04 재개·구현 인계

## 결과와 현재 상태

이번 단위는 H/He scalar ledger를 공통 gas frame의 흡수·escape four-force,
perfect-fluid gas projection, radiation shear work 및 paired angular family로
연결했다. C01–C07의 식과 가정은 CLAIMS.json에 있고, 채택의 최종 근거는
`review/DECISION.json`이다. 새 실제 검산은 xAct tensor 24 + scalar 5 + 독립
geometry scalar/matrix 16 = 45개이며 모두 통과했다.

기존 `HERE_RUX03_PRIMARY_PROVIDER_03` 구현 의무, 원래
`RUX02 + RUX03 -> RUX04 -> RUX05` owner DAG 및 완료 상태는 유지한다.
이번 요청은 THEORY 한 단위이며 새로운 Rust/provider wiring이나 ODE 실행을
완료한 것으로 표시하지 않는다.

## 다시 사용할 입력

- Previous theory: BASS_HE PR31 head
  `be96b0011772b47af4bd3c8e420f73153a745508`.
- Receiver: rei_bianchi PR114 head
  `a5c958c414dea41216b445c05f58df837f05cacb`.
- 부모 사건/결합/열 ledger, captured kinetic moments, per-H/reference/proper
  normalization, endpoint-energy finite work: REUSE_IDENTITY.json의 정확한
  파일과 이전 47개 symbolic 결과.
- 현재 45개 검산의 실제 입력·원자료와 runtime hash:
  `evidence/EXECUTION_RECORD.md` 및 최종 두 결과 JSON.
- 현재 초기 photon pairing: `source_map/STATIC_INPUT_PARITY.json`.
  이는 selected initial data의 비교이며 generic API의 pairing 강제가 아니다.

## 코딩을 다음으로 선택할 때

첫 실행점은 원래의 `HERE_RUX03_PRIMARY_PROVIDER_03`이다. 같은 raw event
provider를 실제 caller에 연결한 뒤, 이번 `HERE_RUX03_COVARIANT_MOMENTS_04`
계약으로 `Q_abs`, `f_abs`, `q`, pressure와 shear work를 반환한다.

완료 기준은 다음 물리적 구별이 실제 소비 경로에서 확인되는 것이다.

1. 같은 사건에서 total absorbed energy와 full E/c momentum을 공유한다.
2. 반대 방향의 에너지·count·source가 일치하면 각 종별 momentum이 상쇄된다.
3. zero energy flux이지만 opacity-weighted force가 남는 spectral case를
   zero-force로 잘못 판정하지 않는다.
4. μ ring의 평균 방향과 second angular moment를 각각 사용한다. 평균
   four-momentum을 individual null photon으로 검사하지 않는다.
5. 고정 homogeneous/geodesic gas frame의 공간 잔차를 명시하고, 속도 진화를
   구현하지 않은 입력에 자동으로 완전한 momentum closure 상태를 부여하지 않는다.

추가 숫자 실행은 해당 CODING 단위의 source 상태와 권한·자원 계약에서 시행한다.
이번 THEORY의 45개 검산을 새 native 실행 수에 포함하지 않는다.

## 이론을 다음으로 선택할 때

다음 열린 단위는 `HERE_RUX03_MOVING_GAS_SOURCE_05`다. 한 common gas velocity가
변할 수 있는 local source substep에서 photon absorption/emission과 bulk
kinetic energy를 함께 갱신하는 유한 stage를 구성한다.

첫 구체적 설정은 고정된 local Eulerian tetrad의 source substep이다. 입력은
Eulerian photon energies/directions/counts, baryon density `D=gamma n_H`,
fractions, `w`, gas bulk velocity 및 이번 rest-frame four-force다. 구성할
유한 map은 gas normalization과 total energy/momentum source budget을
동시에 만족해야 한다. Rest-frame opacity에는 Doppler-shifted photon energy와
transformed photon density를 사용해야 한다. 고정 부피 source substep의
baryon conservation, gas constitutive primitive recovery, photon event update의
동일 stage placement를 먼저 정렬하는 것이 다음 R3–R5의 대상이다.

판별은 zero-velocity/zero-force 극한에서 부모 scalar stage가 재현되고,
한 빔의 흡수에서는 bulk momentum과 kinetic energy가 동시에 변하며,
반대 pair에서는 이번 대칭 구성이 유지되는지다. 이는 다음 단위의 미완성
구성 의무이고 현재의 완료 주장에 포함하지 않는다. 모든 Bianchi class나
relative species tilt/abundance-source D2.3를 여기에 합치지 않는다.

## 재검토가 필요한 변화

다음 중 결론이 의존하는 입력이 바뀌면 그 전이가 처음 필요한 R단계부터
다시 검토한다: atomic event/captured kinetic moment; photon frame 또는
per-H/reference normalization; escape angular closure; pairing/opacity/source
symmetry; endpoint energy/source placement; prescribed-frame compatibility.
변경 없는 원자 계수 유도와 기존 source/hash 검토는 재사용한다.

## 권한과 게시

이미 허용된 격리 draft PR 및 create-only backup 범위에서 산출물을 게시한다.
merge와 다른 사람에게 보내는 메시지는 수행하지 않는다. 과학 입력의
immutable identity와 게시 branch/PR identity는 구별하여 delivery receipt에
기록한다. 새 project policy나 skill 변경은 없다.
