# HE23 총 수소핵 밀도 및 per-H 계약 복구: 실제 NCP 결과

## 판정

DENSITY_CONTRACT_FIXED: PASS. NATIVE_PILOT: PASS. MATRIX: 12/12 PASS. PHYSICS_LEDGER: 이 조건부 이산 계산 범위 PASS. CONVERGENCE: 에너지 분할 영향은 작으나 시간/각도/독립 연속해 수렴은 미확립. 전체 EoR, upstream Grackle 동등성, Bianchi 관측 판별, CMB 광학깊이/관측 전망은 HOLD다.

기준 parent는 HE22 실패 보존 f103fdc48b8c6c3f032fdbe3face6c6fd078768d이다. 기존 HE21/HE22/PR69 및 기존 dirty 작업 트리와 production 작업은 변경하지 않았다. 새 저장소 /root/BASS_HE_HE23_DENSITY_20261016, 새 실행 위치 /root/HE23_NCP_DENSITY_20261016을 사용했다. 공개 파일에는 SSH 접속 정보나 토큰을 넣지 않았다.

## 원본 진술과 교정

원본 rei_bianchi f7830e2f55e7a1938bc3c98f61b60651f8dae474의 Driver::new는 고정 cosmology로부터 총 수소핵 n_h0_cm3 및 총 헬륨핵 n_he0_cm3를 구성한다. 실제 proper density는 각각 a^-3을 곱한다. C19 e91ffe368c4e6db64c4b6c5962566302a33402b6의 선행 문서는 0.0017575700008892194를 proper **neutral HI**로 기록했다. 원래 HE21/22는 이를 총 수소 밀도처럼 사용했다. 이 frozen-state가 HE21 초기 상태와 같다는 근거는 없으며, 0.9998 비율에서 초기 분율을 역추론하지 않았다.

HE21 photo-only 파일은 byte-identical SHA256 3df86063f12e238ec41219343a016b3a5086d18ce973015c335ec8118d9a5b66으로 보존했다. HE23의 HISTORICAL_FROZEN_HI_Z20_CM3는 provenance 전용이다. 새 native --density a 모드는 원본 Driver에서 총 핵 밀도를 직접 조회한다. Python native 결합은 이 총 밀도를 optical depth와 체적 사건률, per-H escape/CMB 변환에 일관되게 사용한다. 소스 SHA/binary SHA/a.hex()를 기록하며 rounded cache나 다른 cosmology fallback은 없다. 기존 1e-9 density/helium 검증을 유지했다.

첫 midpoint a=0.047620181473387826의 올바른 총 H=0.0017577960178838546 cm^-3, Y=0.08130135170951498이다. 기존 기대값 0.0017574444586802788과 차이가 난다. 여러 a=(1/21, 첫 midpoint,0.1,0.2)에서 독립 Python cosmology 계산과 native 밀도를 대조했고, 의도적인 0.9998 밀도는 기존 gate가 거부했다.

## 유도와 명시된 근사

per-H는 총 수소핵 1개당이다. alpha=(1-xHII,Y(1-xHeII-xHeIII),Y*xHeII), absorber density=nH,total*alpha다. 종별 Gamma=A/(dt*alpha), heat=EV_ERG*Q/(dt*alpha); 체적 사건률=nH,total*A/dt다. 비어 있는 absorber에서 사건도 0이어야 한다. optical depth는 c*nH,total*alpha*sigma*dt다. 기체/광자 에너지와 결합에너지의 분모도 같은 총 H이다.

초기 (xHII,xHeII,xHeIII)=(1e-5,1e-5,0), 초기 T=8.098143045064857 K, 동일한 conditional source_count=3.45955703510212632e-6 photons/total-H, 50,000-K shape와 source-birth-time/방향, Verner fit cuts와 물리 binding 구별을 유지한다. Source budget는 여전히 prescribed per-log(a) 모델이다. 원본 MD14 실제 time emissivity나 완전한 cosmological history로 재보정하지 않았다. q의 signed geometry와 8점 각도 적분, 원래 시간 구간 z20→19.998을 유지한다.

CI/RR/DR와 cooling, Case-A escape, CMB는 원본 Rust 소유다. igm_point_rhs의 h=0; 외부 gas adiabatic work와 photon redshift/shear work를 한 번만 계산한다. 원본은 선택된 Grackle 3.4.1 반응률의 Rust 포트와 별도 CODATA Thomson/blackbody Compton 식이다. upstream Grackle 라이브러리를 직접 링크/실행한 것이 아니며 완전 동등성을 주장하지 않는다. 이 차가운 상태에서 DR=0이므로 활성 DR 물리 정확도를 이 실행으로 인증할 수 없다.

PR150 최신 publication head 7cb4ac678be019b736e85db76dfbdc7c51e380e9 및 PR153 e98d30efb5e725a79743d3a8ff61ee7e5169b498, PR154 daf653e87a5b208ed6f51113e83d56fec4abf4f8의 수식/검증 범위를 읽었다. 서로 다른 source/epoch/gas state나 production 결과는 가져오지 않았다. positive bookkeeping과 continuum accuracy가 다르다는 제한을 유지한다.

## 테스트와 최초 실패 보존

최초 밀도 회귀: 2 FAIL로 결함을 확인한 뒤 수정했다. 최초 전체 suite 28 PASS와 density-recovered native pilot/matrix 12 PASS를 얻었다. 그 뒤 유한한 n=8 정제에서 첫 HE22_TOTAL_ENERGY_LEDGER_FAIL을 보존했다. 추가로 제출된 5개 worker의 미수집 결과는 PASS로 세지 않았다.

이 첫 실패를 7개의 저장 native 출력과 정확히 같은 입력으로 재현했다(새 native 호출 0). 첫 step의 scaled Newton error=5.270648126252506e-13은 기존 3e-12 기준을 만족했으나, 에너지 잔차=1.8040636920983826e-14 eV/H는 기존 한계 2.268759216057102e-15보다 컸다. `REFINEMENT_FIRST_FAILURE_DIAGNOSIS.json`에 입력과 잔차를 보존했다.

제조한 비선형 recombination/escape 회귀에서도 기존 조기 종료를 FAIL로 확인했다. 교정은 Newton 종료 시 기존 residual gate와 기존 energy gate를 **동시에** 만족하게 하는 것이다. 3e-12 Newton, 3e-11 physical-scale/2e-12 thermal-scale energy, 1e-9 density 등 어떤 tolerance도 늘리지 않았다. 이 수치 의존성 변경 때문에 새 pilot/matrix/refinement를 별도 *_energy_gate_v2 경로에서 수행했다. 이전 성공/실패는 덮어쓰지 않았다.

최종 전체 테스트: 기존 24개를 수정 없이 유지하고 신규 8개를 추가하여 **32 passed in 4.00s**. 네 실제 a의 밀도/종별 사건, 잘못된 밀도 거부, 독립 per-H→체적 변환, HI/HeI/HeII heat/binding/positivity, source-free와 photo-only 극한, dual stopping gate, 기존 결과 보존, 원자적 JSON/timeout 원본 보존을 검증했다. Mock은 native PASS로 승격하지 않았다. SymPy 1.14.0의 독립 핵종·전하·에너지 기호 잔차는 모두 0이다.

독립 읽기 전용 검수는 과학 경로의 구현 오류를 발견하지 않았다. raw JSON atomicity, timeout 기록, Python 실행 identity의 P2 세 건을 지적했고 모두 수정 후 focused closure를 받았다. 실제 검수자는 solver를 재실행하지 않고 18개 case, 884개 RHS, 136개 density 기록을 독립 검산했다. 이는 전체 물리 이론의 외부 인증이 아니다.

## 실제 native 결과와 수지

최종 pilot: q=0,m=4,n=2 PASS, native 26 evaluations, wall=0.37719161 s. Matrix q=-0.005,0,+0.005 × m=4,8 × n=2,4: **12/12**, 최대8 worker, stage wall=1.14931715 s. 추가 q0 정제 (m,n)=(4,8),(8,8),(16,2),(16,4),(16,8): **5/5**, 최대3 worker, stage wall=2.60448524 s. 이 시간은 단일 작업의 관측이며 speedup 주장은 아니다.

최종 18개 case의 884개 raw RHS를 독립 집계한 최대치:

| 검사 | 최대 잔차 |
|---|---:|
| density/Y relative | 2.220446049250313e-16 |
| photon number / total-H | 7.199780051661553e-21 |
| total energy eV / total-H | 4.336808689942018e-19 |
| H/He species evolution | 3.3881317890172014e-21 |
| chemical electron census | 2.541098841762901e-21 |
| scaled Newton residual | 9.279651123667993e-17 |
| native point event relative | 5.070711808696728e-16 |
| point micro energy normalized | 8.758115402030107e-18 |

모든 최종 상태와 광자 stock은 허용 영역/양성 gate를 통과했고 support crossing=0이다. 원본 source birth 수와 1차 energy moment도 검증했다. photon+gas+binding+work+escape-CMB의 이산 수지 및 CI/RR/DR를 포함한 종별/전자 수지는 닫힌다. source-free 실제 native control도 통과했다.

q0,m16,n8의 최종 xHII=1.3204074110525233e-5, xHeII=1.3127511270154122e-5, xHeIII=1.7834578157251454e-13, Tgas=8.2416043779573 K. 흡수 HI/HeI/HeII=(3.204082553149576e-6,2.5427159191951415e-7,1.4499796312037267e-14)/H; photoheat=2.027250455851755e-5 eV/H; binding 증가=4.982225076894349e-5 eV/H; escape=1.3162545576619435e-10 eV/H; CMB→gas=3.4327726640047007e-10 eV/H; gas work=2.175144066943798e-7 eV/H; photon work=4.61241901966187e-12 eV/H. 전체 수치는 JSON과 CASES.csv에 있다.

## 유한 정제 결과와 한계

q0,m=4에서 T 차이는 n2→4에 -4.81626354e-5 K, n4→8에 -1.62329523e-4 K다. 차이가 줄지 않아 이 시간 격자가 asymptotic convergence 영역에 들어갔다고 볼 수 없다. 이를 통과로 바꾸거나 tolerance를 늘리지 않았다. 추가 n=16/32 등의 별도 유한 계약과 독립 error-controlled continuum 비교가 다음 과학 node다.

반면 n=8에서 에너지 m4→8의 T 차이=2.46835441e-10 K, m8→16=1.52358126e-11 K, 최대 기체 분율 차이=9.3244e-15와4.1458e-16이다. 이것은 해당 source/짧은 구간의 에너지 분할 민감도일 뿐 전역 수렴 차수나 최종 EoR 오차가 아니다. 각도8은 고정했으며 각도 정제는 NOT_RUN이다. 세 signed-q의 차이는 이 짧은 구간에서 매우 작고 관측 판별이 아니다.

기존 밀도 오류 영향은 별도 constructed photo-only 비교로 보존했다. q0,m8,n4에서 올바른 총 밀도로 바꾸면 HI/HeI 흡수 차이는 각각 +8.7723460e-14,+8.7226410e-14/H, heat 차이는 +5.2228326e-12 eV/H다. 이는 계약 오류의 조건부 영향 분석이지 관측 불확실도 또는 잘못된 native 밀도를 허용한 계산이 아니다.

## 실행 identity와 보존

실제 numerical v2 소스는 c0772399044c3e2f8cd6e12e420cdd87ddf0ad1d의 6개 .py/.rs 파일과 모두 일치한다. RUN_SOURCE_SHA256은 numerical 실행 후, logging-only 변경 전에 캡처했으므로 attribution은 명시적으로 **retrospective**다. 원래 SUMMARY는 수정하지 않았다. NUMERICAL_EXECUTION_SOURCE_BINDING.json이 이를 기록한다. 후속 배포의 atomic logging, timeout 보존, 빈 work-root guard와 실행 직전 source manifest 저장은 별도 테스트했다. numerical core는 바뀌지 않았다.

원본 Rust clone은 고정 commit에서 clean이다. native binary SHA256=981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe. source/rlib/compiler/flags/environment의 다른 identity는 로그에 있다. NCP NAVERCloud Xeon Gold5220,64vCPU,125GiB,1NUMA; Rust1.99.0,opt-level2,edition2021,binary64; OMP/MKL/OpenBLAS=1; Python3.12. no fast-math나 정밀도 축소 없음.

GitHub 게시 후 Git blob을 다시 읽어 SHA를 검증한다. 복원 아카이브에는 source, Git bundle, native raw, 실패 원본, 바이너리, 검증 스크립트와 원본 micro source snapshot을 포함한다. 현재 host에는 rclone/configured remotes가 없어 연결된 인증 Dropbox/Drive connector를 사용한다. create-only 업로드 후 양쪽에서 전체 바이트를 다운로드하여 로컬 SHA와 비교하고 BACKUP_RECEIPT.json을 별도 보존한다. 실제 원격 backup 결과는 그 영수증을 따른다. 최초 HE22 이중백업도 유지한다.

실제 백업 완료: v2 804,505바이트를 Dropbox와 Drive에서 각각 다운로드했고 SHA256 e65a431bfb304f842b05a23463e1680758ff7f24cac8dcc071a11007bd513596이 일치했다. 각 원격 사본을 독립 압축해제하여 package 110개, 원본 owner 156개 파일의 SHA와 raw archive 1,879개 member를 검증했다. v1 Dropbox FETCH_FAILED는 보존했으며, v1 전체 Git bundle/바이너리 아카이브는 Drive에서 별도로 full readback했다. GitHub 원격 blob 110개도 실제 readback 일치했다. 상세 ID와 scope는 BACKUP_RECEIPT.json이다.
