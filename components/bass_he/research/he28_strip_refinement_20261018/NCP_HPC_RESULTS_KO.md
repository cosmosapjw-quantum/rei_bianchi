# HE28 NCP HPC 실행 보고

실행일: 2026-10-18 (KST)  
검증된 시작 revision: `d496e0e8b7c9d5a708bf07c4c6eaa4900c6d489c`  
실행/최적화 revision: `bcd3ac4c58760bcfb1f03ee30bd82fd3d77ff7a4`  
결과 브랜치/PR: `results/he28-ncp-hpc6-20261018`, Draft PR #77 (PR76과 분리)

## 적용한 실행 최적화와 근거

인증된 Dropbox 및 Google Drive에서 HE28/HE27, NCP64, OpenMP/thread scaling, Rust, table acceleration 검색 결과를 대조하고, 최적화 보관본 `BASS_HE_NCP64_OPTIMIZATION_20261001_v1.zip`과 연관 FLRW rate-table 보고서를 읽었다. NCP64 연구의 이전 Eigenstate 전체 작업에서는 최적화 Rust가 0.384567 s, NumPy가 0.381876 s였으며, 작성자는 실제 NCP64 scaling 미실행으로 표시했다. Fortran/OpenMP kernel 미시 benchmark는 전체 solver의 이득을 증명하지 않는다. 별도 FLRW rate-table 연구도 작은 query batch에서 Rust table이 직접 계산보다 빠르지 않았고, 큰 batch에서만 setup amortization 이득을 보였다. 따라서 HE28 solver를 Rust로 다시 작성할 성능 근거는 없다.

HE28의 수치 계산은 Python/SciPy adaptive Radau/DOP853와 고정 native owner를 그대로 사용했다. 변경은 독립적인 여섯 study 사례의 최대 6개 process 병렬 실행, worker의 OpenBLAS/MKL/BLIS/NumExpr/OpenMP thread를 각각 1로 고정, accepted pilot와 study 사이의 thread 환경 identity 검사, NumPy scalar JSON 직렬화 보정뿐이다. 물리식, owner microphysics, 격자, source table, 정밀도와 허용오차는 변경하지 않았다. 42개 focused test가 통과했다.

NCP는 Intel Xeon Gold 5220, 64 CPU, 약 125 GiB RAM이다. 실제 계산 worker 여섯 개는 각 1 thread로 약 6 CPU를 사용했고 worker RSS는 각각 약 100–210 MiB 범위였다. 남은 CPU를 채우기 위한 추가 과학 사례는 만들지 않았다. 파일럿 하나는 순차 독립 검증 때문에 약 20분이 걸렸다. 승인된 study는 6 worker로 약 7분 55초 만에 마쳤다. 동일 사례의 단일 worker wall은 이전 exploratory run과 거의 같아 kernel speedup을 주장하지 않는다. 완전한 동일 matrix serial baseline이 없어 campaign speedup 비율도 주장하지 않는다.

## 실제 native 실행 결과

thread 제한 및 신규 identity에 묶인 pilot `q=0, m=4, r=2, n=16, GL4, table=512`은 통과했다. 총 293,906 native 호출이 있었다. `transport`, 독립 adaptive Radau, 독립 adaptive DOP853의 최종 온도는 각각 8.239220060821102 K, 8.239220062970691 K, 8.239220062970656 K였다. transport–Radau 차이는 2.1495889512834765e-9 K로 1e-8 K 한도 이내이고, Radau–DOP853 차이는 3.552713678800501e-14 K로 1e-9 K 안정성 한도 이내였다. 수소·헬륨 최종 gas fraction의 transport–reference 최대 상대차는 3.951006358291365e-14로 1e-11 기준 이내였다.

승인 gates는 완화하지 않았다. source moment와 angle-band 상대 오차는 각각 3e-13 이하, native photon number defect 3e-15 이하, energy defect 3e-12 eV 이하, 각 species defect 3e-12 이하이며 photon/gas 비음수성도 요구한다. Pilot admission은 transport–reference 온도차 1e-8 K, 상대 gas 차이 1e-11, 독립 Radau–DOP853 온도 안정성 1e-9 K 이하를 추가로 요구한다. Study는 pilot `pilot_accuracy_pass=true`, 동일 binary/owner/source/thread/table identity (table512), table build 600 s 및 table memory 2048 MiB 예산, 사례별 3600 s 제한에 묶였다. 실제 study matrix는 `q=0, GL4, m=8, r=2/4/8, n=32/64`의 6개 항목으로 제한했다.

Pilot의 transport 광자 수지는 photon number `3.85117493251536e-08`, energy `9.546044242544628e-07 eV`였고 number defect `1.6940658945086007e-21`, energy defect `-2.2854981795994433e-16 eV`였다. Pilot ledger에는 HI/HeI/HeII photo-absorption, CI, RR, DR, binding, species heating, escaped radiation, CMB, gas work와 photon work가 각각 보존되었다. 이 실행에서 DR는 0이다.

study의 고정 matrix 6/6이 모두 정상 완료되었고 실패 및 timeout은 없다. 표의 wall은 각 사례의 전체 실행 wall이며, study 사례는 transport native solver만 실행했다. 수렴한 광자·원자 반응 수지는 이 제한된 격자에서 다음 범위에 들었다.

| 사례 | wall (s) | native 호출 | 최종 T (K) | photon number defect | energy defect (eV) | source table SHA256 |
|---|---:|---:|---:|---:|---:|---|
| m8/r2/n32 | 115.23 | 667 | 8.23922006007 | 2.12e-21 | -1.91e-16 | `dbb8be0d7655c0ce44f63eb4008c2a63212e5a493dd47cd5d54fe34de9063256` |
| m8/r2/n64 | 131.91 | 1005 | 8.23922006125 | 2.12e-21 | -9.63e-17 | 동일 |
| m8/r4/n32 | 227.23 | 990 | 8.23922006033 | -1.27e-21 | 2.19e-17 | `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd` |
| m8/r4/n64 | 248.84 | 1268 | 8.23922006058 | -8.47e-22 | -2.04e-17 | 동일 |
| m8/r8/n32 | 457.79 | 1485 | 8.23922006054 | 1.69e-21 | -8.50e-17 | `813a95fd90b0a8b0586d2ec80cbc706f51d5660e0d234bdd8f69e8d1b01950be` |
| m8/r8/n64 | 473.21 | 1763 | 8.23922006083 | 2.96e-21 | 1.08e-18 | 동일 |

합계 native 호출은 7,178회다. study 전체에서 source birth `birth_n`은 3.459557035102125e-06–3.459557035102127e-06, `birth_e`는 7.014803824638027e-05–7.014803824638035e-05였다. ledger 종별 값은 다음 범위였다: photo absorption HI 3.17231076758e-06–3.17231077722e-06, HeI 2.48734489510e-07–2.48734504336e-07, HeII 1.34937576636e-14–1.34939114812e-14; CI HI 1.76890659236e-16–1.76893401281e-16, HeI 1.43814508177e-17–1.43816737494e-17, HeII 1.66344546809e-22–1.66348527254e-22; RR HI 8.12284126724e-12–8.12302148553e-12, HeI 6.55995738331e-13–6.56011421113e-13, HeII 3.33726628486e-20–3.33759289780e-20; DR는 0이었다.

species heating은 HI 1.83776152902e-05–1.83776154057e-05, HeI 1.56153618261e-06–1.56153619392e-06, HeII 6.47220509973e-14–6.47228686896e-14였다. binding delta는 4.92540663888e-05–4.92540667703e-05 eV, escape 1.26593408607e-10–1.26596245033e-10, CMB 3.36551437934e-10–3.36556627279e-10, gas work 2.17452442959e-07–2.17452677873e-07, photon work 8.88090800079e-11–8.88090859467e-11이었다. 이 값은 현재 model의 고정 source/density/초기 epoch에서 얻은 ledger이며, 관측 예측이나 전체 EoR 수지 인증이 아니다.

## 식별자와 보존된 실패

- 변경 없는 microphysics owner: `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`
- native 실행기 SHA256: `c4bf20bbe44f2e8d7016c0943b9cc94f1ae676343a00c9231ed2949af3b04216`
- native rlib SHA256: `950dc23e5b33d80586e7be817f09bf70cb9d4a2995d68ae088f15e1d1d9e2b4f`
- HE28 실행 source SHA256: `src/execution.py` `876e43d76f0773a8d2c38e262902442c614a68334561f5e2a78024c659edb1c4`; `src/he28_run.py` `c0e73eb5be368dde9ad036dcc6e7e113ff1b33eb893fa7569d934aa070c6fb37`; source model `src/refined_source.py` `853b18752f4f46706da139c0036e7c0db83f5d25a5cb239d676223b6ddfde0a7`.
- pilot table SHA256: `dc87f2fddc18380c724fd80b8d3edfd5b28b2a0d7ab00e1abedc454bdc4a0907`.
- parent SHA manifest: `f6643464dcba963caa236e0a3cbcebb9d542da2e5b44f8648f9d1033a775105d`.

보존된 실패/탐색 기록: 첫 pilot 결과 직렬화 실패(계산은 마친 뒤 NumPy bool JSON 쓰기에서 실패), 기존 serial study의 r2/r4 성공 후 r8 중단 부분 log, 127-thread exploratory 6-case run, study의 두 번의 실행 전 cwd/output 경로 오류. 127-thread 결과는 진단용으로만 남기며 최종 승인 결과로 사용하지 않았다. thread 제한 버전으로 pilot과 study를 새로 실행했다.

## 범위와 다음 gate

이 실행은 table512, `q=0`, 고정 `GL4`, 유한한 사례별 `m=8`, `r=2/4/8`, `n=32/64`에 대한 scoped native evidence다. 이 값만으로 시간·각도·스펙트럼 연속 수렴을 승인하지 않는다. 연속 스펙트럼, 전체 EoR, CMB/관측 Bianchi 예측, upstream Grackle 직접 동등성은 HOLD다. 이후 hot-kernel 최적화는 동일 workload profiling과 bitwise/허용오차 기준 reference parity를 확보한 별도 연구 단계에서만 고려한다. Rust로 solver 전체를 옮기지 않았다.

완료된 불변 return archive는 148,332,838 byte이며 SHA256 `2059dba94091cfe1042dceaea992f8c3af7b117b687898a0bdfa7b3bef7d622e`다. archive 내부 SHA manifest의 payload 382개를 모두 다시 스트리밍 검증해 mismatch/missing 0건이었다. Dropbox에는 원본 archive와 두 create-only 조각을 저장했다. Google Drive는 100 MiB 전송 한도 때문에 두 조각으로 저장했다. 두 저장소 모두 원격 raw byte를 회수해 재구성한 전체 SHA256이 원본과 일치했고 archive listing 검사도 통과했다. 정확한 파일 ID, 크기, 조각 SHA와 readback 결과는 `BACKUP_RECEIPTS.json` 및 DAG 상태에 기록되어 있다.
