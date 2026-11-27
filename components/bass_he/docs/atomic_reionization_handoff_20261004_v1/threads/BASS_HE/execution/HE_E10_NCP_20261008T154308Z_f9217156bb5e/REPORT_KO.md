# E10 NCP selected owner shadow 실행 보고서

판정: 조건부 저온 manufactured 모델의 OFF/KF/GM 3×384 shadow native 실행과 가능한 출력 identity 검증을 완료했다. 원 receiver 채택·endpoint 관측기 일치·물리 production 승인은 아니다. `SHADOW_CANDIDATE_ONLY`, baseline RCT OFF, physical/production HOLD, HE-F2/F09 OPEN을 유지한다.

## 원 source 및 수신

BASS_HE 최신 수신 source commit `9ac9ca5bb75c615be3146c8e3c1fc02ab05f0a8f`. 시작과 종료의 실제 receiver HEAD는 `39c39eab1cc2f1a215723680accc123e67ef13b6`. E10 archive `f9217156bb5e56c32784bf2d31dc029b66f3455eb8861e1f8e844d11443292c3`, 193927 bytes를 기존 Dropbox connector로 회수하고 CRC, manifest82payload, SHA256SUMS83파일을 확인했다. Drive는 metadata만 확인했다. E9 runtime ZIP `1ddd8a347d5640ad15e027005c2d29e5b2ba92bf42be04ca0f95dfdd6da2984a`, E7 ZIP `020a58ebc4c57a89d973fde66fd1cd82cd5bc3e3f3bccf9f8dce8856cb8bfe2a` 원 bytes를 cached identity로 재사용했다.

새 `E10_20261008T154308Z_f9217156bb5e/shadow`에만 owner original base를 놓고 `OWNER_KF_GM_EXACT_BASE_3FILE.patch` SHA `3fc249d51289ccc994f02e86c10fae7209f7f80e0d15dffe65844d1002c4bf0b`를 check 후 적용했다. coupled/material/radiation 세 patched git blobs가 supplied pin 및 RCT03D bytes와 일치한다. output/lib와 원 41열 계약은 그대로다. E6 vendor42파일이 byte-identical. 실행 이후 supplied82payload, cfg, rustc, binary hashes 재검사 모두 동일. source 검사 자동 continuous poll은 구현하지 않았으며 시작/종료 identity를 별도로 검증했다. owner remote force/reset/push/merge 없음.

E9 원 41열 CSV/비재개 Debug checkpoint/UNKNOWN supervisor failure record는 runtime archive와 정확히 동일하다. E9 live REPORT 및 aggregate FAILURE_RECORDS는 기존 postseal final receipt capsule SHA `9c37c5eb86b2c35f1993be1d98ce062ae91c749e368f0f590cedc59f064da668`와 동일하다. E9 preseal runtime 보고서와 final receipt 보고서의 기존 차이를 새 source 변경으로 해석하지 않는다. E10에서 E9 file edit 없음.

## 실행·시험·자원

NCP 기존 Rust1.94.1 prefix를 재사용하고 compiler SHA/version을 검증했다. PGP signer 검증 NOT_VERIFIED. Delivered strict wrapper를 새 smoke 경로로 정확히 한 번 실행했다: affected native5시험, release binary build, OFF/KF/GM 각2step, E9 OFF 원41열3행 byte comparison 및 sidecar3×3×10 textfields 일치, wrapper exit0. 새 full은 KF→GM→OFF 순서로 각각 `384 --authorized-full`과 별도 출력 namespace에서 k0부터 실행했다. E9 Debug checkpoint seed 사용0, native restart codec 구현0, fallback0, retry0, timestep/source/tolerance 변경0. E9/RCT03D/E6/E7 전체 과학 suites replay0. 요청된 E10 affected tests와 smoke prefix의 실제 advance8/6회는 full1152회와 따로 기록한다 (총1166회).

현재64 CPU/NUMA1, cgroup cpu.max=max100000 memory.max=max, available 약123GiB, disk free57GiB를 관측했다. Native 한 프로세스씩 직렬 실행, active2440 nodes, original cap4096, 각 peakRSS2560KiB. endpoint PathCache 재실행이 없으므로 cap32768은 유지된 원 contract이고 이번 owner density lane의 새로운 cache-key 측정은 아니다. source fidelity를 위해 Fortran/OpenMPI 재구현·병렬 speedup 가정 없음.

|mode|max nonlinear|max number ratio|max energy ratio|elapsed s|
|---|---:|---:|---:|---:|
|OFF|0.941696542632|2.20996419e-05|0.490476155257|69.351|
|KF|0.758521731211|2.33274118426e-05|0.511443484221|77.940|
|GM|0.994761998538|2.57829389234e-05|0.60039716654|77.617|

모든 native exit0, mode별 READY/385행. GM nonlinear .9947619985382534는 gate1에 가까우므로 tolerance를 완화하거나 여유가 충분하다고 쓰지 않는다.

## 검증 및 관측 정의

Mode별 29개 원 native exported fields (동일 정의의 live Gamma3 포함), selected sidecar10개, step trace5개를 E7 원 history와 각각385시각에서 bit compare했다. 이 count는 중복 state/step fields를 포함한 비교 횟수이며 mode별16940, 전체50820이며 mismatch0. selected sidecar 각3850textfields도 exact. full 첫2step+start의41열/side10/steptrace bytes는 smoke와 동일; fullOFF 첫3행은 E9 원41열과 동일하다.

원 producer budget의 material escape에는 RCT escaped energy가 이미 포함돼 있으므로 전체 ledger에 sidecar escape를 다시 더하지 않았다. 별도 exact lifted-f64 Fraction 합으로 RCT heat+chemical+escape 세 cumulative owner를 교차검산하고, Q=(chi_HeII-chi_HI), closure35eV의 coefficient와 event counter를 비교했다. 작은 rounding residual을 진단으로만 보고하며 새 tolerance나 물리 인증을 만들지 않았다. FULL_GATES와 *_RCT_OWNER_CROSSCHECK에 exact 분자/분모를 보존한다. CI/RR/DR 및 원 source/front/event/cutoff/branch 알고리즘은 supplied patch 및 source pin 그대로다.

**E7 history의 live Gamma와 E7 endpoint Gamma는 다르다.** Native live Gamma는 stored history와 bit-identical이지만 fixed-history endpoint 정의와의 finite ratio는 OFF3.543294540710016, KF3.543293861253442, GM3.543282989678432 (원 `1e-22+1e-6*max(abs(a),abs(b))`). 모두1을 넘으므로 endpoint compare PASS/동일관측이라고 쓰지 않는다. 허용오차를 바꾸지 않았고 이 차이를 숨기거나 consumer authority를 endpoint에서 live로 바꾸지 않았다. FULL shadow accepted-gas gate와 이 관측기 실패/정의 차이를 구분한다.

E7 BH/BY/BZ/bindMicro/thermalMicro 5개 internal field는 delivered41열+10열 출력이 제공하지 않아 NOT_EVALUATED. 다른 ledger와 같다고 추론해0으로 채우지 않았다. native 원 advance/admit가 모든 stage의 EOS/positivity/branch gate를 수행하지만 이번 runner는 stage별 수치 trace를 내보내지 않아 독립 per-stage numerical audit도 NOT_EVALUATED. Endpoint fractions/positive stock 및 selected1000..10000K guard는 별도 확인했다. 원 source binding/동일code replay 자체는 independent science/true-error 인증이 아니다.

## 실패·claim ceiling·다음 DAG

native failure0. Intake 탐색의 prefix-MANIFEST KeyError 및 pin field명 차이는 source 변경 없이 실행 전에 교정해 기록했다. Independent forensic reviewer의 초기 audit는 analysis comparison-map 추가 중 count15785→16940 변경을 만나 실패했고, 원 native 재실행 없이 최종 map을 읽어 재검사했다. 원 실패 기록은 review에 보존한다. Endpoint Gamma compare, 미출력 field/stage trace, PGP 미검증을 미달/부재로 반환한다.

H3 실제 photoheat first moment 및 방출 photon-energy/recoil moments는 null. 현재 solver의 기존 manufactured photo-energy owner와 research35eV RCT closure는 그대로며, 이 값으로 새 물리 heat를 합성하지 않았다. owner accepted commit/PR+source/test/fresh smoke+reviewer acknowledgement가 없으므로 RECEIVER_ADOPTION은 PASS가 아니다. OFF baseline 및 원 physical HOLD/HE-F2/F09 OPEN/continuous true-error 미인증 유지.

다음은 연구 thread의 full shadow 결과 검토와 distinct Gamma observer source/누락된 owner telemetry 계약이다. 기존 full3×384/affected smoke를 재실행하지 말고 sealed raw outputs를 사용한다. 실제 owner adoption, 별도 physical energy moment, 장기F09는 별도 source/과학 승인 노드다.

## 전달

이 보고서·SOURCE_IDENTITY·TEST/PREFIX/FULL gates·rawCSV/stdout/stderr/exit·실패/복구·source manifest를 immutable runtime ZIP으로 보존한다. 원 E10 archive/E7 ZIP은 private source inputs로 포함, 원 E9 runtime는 이미 양쪽 cloud에 봉인된 content identity로 참조한다. 공개 Git에는 작은 요약/계약/검증/영수증만 additive nonforce 게시한다. 봉인 당시 DELIVERY pending snapshot과 사후 detached receipts를 구분하며, 두 provider R1 ACK/name/path/size 확인은 UPLOAD_VERIFIED이고 remote byte restore는 별도 NOT_RUN이다.

사후 R1 전달 완료: runtime SHA256 `d2cec9451719d534b78bdd6ebd7570e03697e9fdd69696c24a966c1a25c91598`, 2,528,362 bytes. Drive `1ZsLe1LlC_hHNOUbhXug1llUZsLzt4mHS`, Dropbox `id:BSpOijBcT10AAAAAAD3izA`. 두 provider 완료 ACK 및 크기 확인. UPLOAD_VERIFIED, RESTORE_NOT_RUN. Git preseal `157def8e78fafe4e32b961b48b5c6d1512263d43`; 최종 delivery Git readback은 별도 FINAL_GIT_READBACK.json/capsule로 보존한다.
