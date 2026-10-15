# REI C16B → native H/He point parity 인계

2026-10-16 KST. 이번 연구 단위는 native source-matched point parity와 단일 에너지
소유권 검증에서 종료한다. **production scientific PASS는 선언하지 않는다.**

## Git와 source

- 작업 branch: `research/rei-c16b-native-parity-20261016`.
- research base PR155: `f8f26710e3961609acf4d7e7930bc7b2a95bd39c`.
- 실제 실행 native PR150: `0e25846433170d0f420c4cda44a0bedbf02cd177`.
- 조사한 Git remote default HEAD: `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`.
- PR154 source: `daf653e87a5b208ed6f51113e83d56fec4abf4f8`, photon blob
  `db822a53da3ccdca7cf96628e9ef3bbcec83db5a`, SHA256
  `f4c5ff49f9e09a2123f3830160e857beb9c224deafc9ff379d6199829013bbf4`.
- 제공 ZIP: 155324 bytes, SHA256
  `ac03282a101a91b911a4df84fec4b538442efd29354de26b888b2fc70d692a87`.
  별도 디렉터리 복원 후 manifest 36개 항목 모두 일치했다.
- `igm_rates`, `igm_thermal`, `igm_state`, `hhe_events`는 과거 native snapshot과 같다.
  transport와 driver는 최신 PR150 소스를 사용했다. 실제 파일별 hash 및 byte comparison은
  `evidence/benchmark/native_authority_rebind.json`, `evidence/native/source_identity.json`에 있다.

최종 게시 commit/PR 및 클라우드 복원 결과는 같은 폴더의 `DELIVERY_RECEIPT.json`을 읽는다.
과학 결과를 담은 archive의 commit과 이후 delivery receipt commit은 구분한다.

## 실제 수치 결과

48개 native fixture에서 4905개 조건이 통과했다. frozen geometry b=0,±0.1,
fit threshold 아래/동일/위, dt=0/유한/고흡수 stiffness, T=100/1e4/1e5 K,
He 부재와 빈 광자 control, CMB 양 부호를 포함한다. Python은 자기 Verner opacity로
BE survivor를 독립 계산했으며 Rust survivor를 reference 입력으로 복사하지 않았다.

| 종 | Gamma 최대 상대잔차 | heat 최대 상대잔차 |
| --- | ---: | ---: |
| HI | 1.6726757759153086e-16 | 4.938562738350844e-16 |
| HeI | 7.737637802620059e-16 | 6.150188727415387e-16 |
| HeII | 1.6727387384997298e-16 | 2.3645528452322446e-16 |

Gamma 최대 절대잔차는 각각 1.6155871338926322e-27,
6.462348535570529e-27,8.077935669463161e-28 s⁻¹/absorber이다.
heat 최대 절대잔차는 각각 2.350988701644575e-38,
1.410593220986745e-37,2.938735877055719e-39 erg/(absorber s)이다.

주요 독립 ledger 최대 절대잔차:

- H nuclei 0; He nuclei 3.512896218562318e-31 cm⁻³ s⁻¹.
- charge 1.8562883175981934e-29 cm⁻³ s⁻¹.
- photon number 3.29350067257991e-18 /H.
- photon binding+heat/RHS energy 3.741130718377512e-16 eV/H.
- thermal+binding+escape−photo−signed CMB 9.387634724143388e-40 erg cm⁻³ s⁻¹.
- binding rate reconstructed from species 7.310966451952582e-40 erg cm⁻³ s⁻¹.
- EOS temperature derivative 2.117582368135751e-22 K/s.

전체 cancellation 검사의 최대 normalized residual은 고정한128*eps*gross bound의
0.008526034075271402배다. 양의 값은 상대1e-12, 구조적 영은 exact zero로
판정했다. 원시 값·단위·gross scale은`evidence/native/summary.json`과`checks.json`에 있다.

## 테스트·실패·수정

- portable `./verify.sh`: 신규29 + 원본22 = 51 tests, 최종exit 0.
  DOP853 비교와 도표도 완료했으며 측정 수렴률은1.9993293411871906이다.
- native48 cases /4905 checks, 최종comparator exit 0, exact-zero comparisons417.
- 원래 Rust focused tests37개 (transport7, parallel6, foundation9, rates4, thermal11), exit 0.
  rates의4개에는 원본literal-C 참조와의 전체 선택channel 비교가 포함된다.
- 첫Python 실패는NumPy 누락, 다음은matplotlib 누락이었다. 전용venv에 의존성을
  설치하여 해결했다. 첫native build101은crate 외부include_str 입력9개의export 누락이었다.
  pinned source의 해당 파일만 복원했다.
- 첫native 실행101은harness의 미지원n_mu=4 때문이었다. 기존native fixture의16,8 constructor로
  수정했고, 명시적3ray·48개 물리fixture는 유지했다.
- 첫comparator HOLD는 문자열dt 선택이stiff case까지 고른 테스트bug였다.
  dt_s==1e9의 수치 선택으로 수정한 뒤 같은raw JSONL로comparator만 재실행했다.
  모든 실패 로그를 보존했고, native 과학식·계수·허용오차는 바꾸지 않았다.

## NCP·기존 계산·자원

실행host `s1a0e5abed09`, 64 logical CPUs, RAM125GiB, 초기available 약122GiB,
swap0, 초기root 여유27GiB였다. Rust/Cargo/kernel 실측값은resource intake에 있다.
rei checkout7개(신규clone 준비 중인1개 포함)의dirty/untracked를 기록했다.
private_run의 미추적checkpoint를 포함한 기존checkout은 수정하지 않았다.
다른Codex process들을 보호했다. 초기ps에 실행 중인native scientific solver는 없었다.

원래PR150 source005 q512/q1024 양쪽에서z=4 terminal receipt를 확인하고 읽기 사본만
보존했다. 원래epoch·binary·checkpoint·raw history를 재개하거나 수정하지 않았다.
소유자Ubuntu의Desktop Commander 실행은 월간quota로 거절되어 지시대로 재시도하지 않았다.
따라서Ubuntu의 전체worktree inventory는 미확보 상태이며NCP inventory와 구별한다.

신규native48점 평가는wall0.01 s, maxRSS2560KiB였다. 최종example incremental build는
wall0.46 s, maxRSS145920KiB였다. 전체build 시도·focused tests의time-v도 원문으로 보존한다.
compile jobs2, 비교 실행timeout300 s, 가상메모리8GiB 상한을 적용했다.

합성64case benchmark의sweep wall은serial1.390792554 s, 8-worker0.200181627 s였다.
process 전체wall은1.537625419 s와0.356329824 s였다. 결과JSON은byte identical이며SHA256은
`67ed7da0d8a8b144246fa0a875040f6f7cc31f342ef67f224d949f19ca96ccd8`。
8 workers+Python parent로9 Python processes, sampled aggregate RSS146341888 bytes였다.
6.95배는 짧은 단일 합성sweep의 비율이며native 물리history의speedup은 입증하지 않는다.

## 재개점과 물리적 미해결 항목

다음READY node는 **GRACKLE_RR_CI_THERMAL_BIND**다. native point owner 일치를 바탕으로
온도 의존native rate·cooling을 사용하는 양의RR/CI 갱신과thermal budget의 결합을 구성한다.
manufactured pair의 계수를physical Grackle 계수로 단순 치환하여 이차 정확도를 가정하지 않는다.
기존native chemistry/transport를 중복 적용하지 않는다.

Case-A bolometric escape의UV spectrum·각도·source-age 분포, MD14 source-age 이력,
동적signed shear/redshift work, 각도·spectral·proper-time의 독립 수렴, coupled stiff
thermal 적분, baryon recoil, two-way Einstein work, 최종Bianchi z=20→4 ion/Tgas 이력이
미해결이다. frozen b control이나 기존FLRW represented-interval 완료로 대체하지 않는다.
이research directory는revert 가능하며production runtime이나 데이터migration은 없다.
