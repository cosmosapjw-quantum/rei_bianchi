# REI 72시간 결과 통합과 실행 준비도 — 2026-10-20

관측 창은 2026-10-17T09:55:50Z 이후다. GitHub의 모든 252 branch를 pagination으로 열람하고 249개 고유 HEAD의 commit date/message/tree를 회수했다. 실패는 0개, 창 안의 HEAD는 33개다. `BRANCH_INVENTORY.md`가 전체 최근 branch를 보존한다. 최근 변경 PR 34개를 읽었으며 현재 핵심 PR 13개의 전체 metadata/body, 실제 current handoff·DAG·source·결과 JSON을 `intake/`에 보존했다. 이는 접근 가능한 GitHub와 지정 cloud backup의 조사다. 삭제된 branch, 모든 비공개 대화 원문, 현재 NCP 프로세스를 직접 조사했다는 뜻은 아니다.

새 계산을 요청하기 전에 상태를 교정했다. R9 Unit5의 종료 영수증은 이미 회수되어 있다. RUN13 M2 standard/tight도 완료·복원되어 있다. PR199의 age64 block-max는 실제 완료이며 별도 PR171의 중단된 age64와 다르다. 현재 실행 준비가 완료된 새 NCP 작업은 LRS 최적화 source의 정해진 matrix와 age32 block-max 한 사례다. 이 intake에서는 NCP, native IVP, 과거 대형 raw 재해시를 실행하지 않았다.

## 현재 결과와 다음 의무

| 계열 | 최신 실제 결과와 범위 | 다음 상태 |
|---|---|---|
| R9 Unit5/T4, PR151 | 128차 checkpoint 완료, 내부 9/9 및 seam 3/3 PASS. 64→128은 추가70 H-action. 이어진 zero-H residual 진단은 1647.067s 후 원 deadline에서 supervisor −9, `DEFERRED_WALL_LIMIT`; residual outputs 없음. 종료 자료 회수 완료 | `READY_METHOD_REVIEW_ONLY`. 같은 expired allocation의 재시작/기한 갱신/종료 자료 재회수 불필요. spectrum/CDF와 physical continuum HOLD |
| FLRW production intake, PR150 | 기존 저장 이력·계약 통합. source normalization Simpson 2048/4096 수리는 6/6 통과, 새 cosmological integration 아님. compact RHS protocol의 6pair/12calls 일치 | 전체 solver 정확도·time/angle 수렴은 HOLD. root cargo fmt 실패/CI test skipped는 별도 infrastructure 사실 |
| RUN07–11 | joint photo-gas, source-support, spectral-edge 연구 계보 보존. RUN10 checkpoint의 미실행 상태를 RUN11 후속 실행 상태와 구분 | latest RUN13–19 evidence를 재사용; 오래된 NOT_RUN만으로 재개하지 않음 |
| RUN13 M2 | standard/tight 각각 6241 intervals·40357 state variables COMPLETE. 적분기 내부 합650.891853577s. tight−standard survivor −1.4510065849e−15, tight M2−M1 +8.4023383435e−6. 마지막 head는 원본331파일와 두 archive의 lossless transport를 추가 복원 | M2 재실행 불필요. sub-H 성분 유한 pair 차이0.5198794503, M4/continuum bound 미확립 |
| RUN15 | 원본333파일와 saved endpoint84관측량을 재구성; fixed-gas continuous-energy 진단5설정. source복원과 native quadrature 대조 완료 | 소실된 네 후속 IVP raw는 `TRANSCRIPT_RECONSTRUCTION_ONLY`; 공개 raw가 있는 RUN13과 혼동 금지. 새 quadrature binary byte mismatch는 남음 |
| RUN16 | gas-path sensitivity, 3개 pre-birth 5D gas-only controls, native calls331. PCHIP−native prefix HI −1.5712776952e−6, T +0.04470254584K | gas point Jacobian은 tube bound 아님. prefix는 full transport restart 아님 |
| RUN17 | first-birth residual 분해; gas24 및 depth5796 polynomial의 exact domain controls, 2개 bounded IVP/1378 RHS. endpoint PCHIP−native HI −3.8007188026ppm, T +0.1246523168K | prefix/event uncertainty, full-source RHS residual, admissible gas/depth tube 필요 |
| RUN18 | 원 저장 path의 431개 depth jump를 exact C0 repair, gas jump0; Rust4 tests 및5911 rational cases 일치. 새 native RHS/IVP0 | continuous interval RHS와 gas/depth tube 아직 필요. C0 repair가 dynamical solution을 증명하지 않음 |
| RUN19 | source-pinned HHeD prepared-T workspace·ordered batch IPC, guarded32769node cubic cache, Li/Be 호환 계층 완료. 264×28 UnitA bit parity; 9216gas-state cubic Hnet 최대3.83e−9/chemnet1.40e−8 차이; 196636coeff 최대1.53e−8 차이. 새 IVP0 | 원 owner에서 continuous interval RHS, source-node/log-grid/query roundoff, interval Jacobian/lognorm/residual tube 연결 필요. 기존 table/benchmark 반복 불필요 |
| P4/S8–S10 | original thermal CX를 보존한 joint midpoint, observable controller, same-scale four-corner inner/outer budgets가 후속 native source에서 실행됨. S10 prototype의 과거 uncompiled 표기는 후속 native 결과로 교정 | 유한 local-defect/precision sensitivity만 승인. full P4 PARTIAL, global/continuum HOLD |
| BASS intake/BR01–02 | actual one-way BASS geometry source binding 완료. BR02의 8e13s 연구와 별도8e12s controlled 연구는 서로 다른 campaign. fixed interior birth rule의 optically thick survivor bias 발견 | 동일 이름의 서로 다른 S10 source 및 BR02 archive 계보 보존. donor dynamics 새로 활성화하지 않음 |
| BR03 | positive exponentially fitted birth, frozen constant-reference mass를 rounding 수준 재현. 실제 evolving native12histories 완료; 별도 CX WorkLimit1건 | count fit가 age distribution 정확도를 뜻하지 않음. joint time/birth/angle/spectrum 미완료 |
| BR04 | 새 Nt16r4/Nt64r4 두 native histories,80steps/203.6714s; frozen age-CDF/W1 및 mixed time/birth 진단 | 이전 next BR05는 이미 완료. 독립 Decimal 보고서1개의 UTC/runtime 원본 bytes 소실은 provenance replacement로 보존 |
| BR05 | read-only actual cohort monitor와 Nt16r8 1개 native history,16steps/41.91796s;314624records audit. 이전 r2→4 대비 r4→8 mixed differences 약0.0775–0.0960로 감소 | 감소는 finite control. threshold crossings0인 원 history로 crossing 정확도 승인 안 됨 |
| BR06 | frozen actual BR05 step1 gas + variable BASS geometry에서9bounded cases; Gauss8/16 count/age/energy/angle controls 통과. 별도 split1176labels는144threshold crossings. 직접 W slab4→8 상대차이1.16e−9→1.23e−10 | `COMPLETE_VERIFIED_SCOPED_FROZEN_OPERATOR`; 다음 `BR07_NATIVE_MOMENT_ENERGY_ADMISSION`. nonlinear evolving-gas proof 아님 |
| BRPERF01 PR210 | PERF00 source/runtime checkpoint8파일 게시. rate tables/photon worker pool/LiCNO catalog는 목표이며 아직 구현·실행 결과가 아님 | RUN19 준비코드를 재사용하되 BR06 source owner와 인터페이스 검토 선행. 독립 native campaign 아직 READY 아님 |
| LRS V12/V13 | thermal clock 및 source interval-mean sandbox 연구 완료; V13 일반 source-on order HOLD | 이미 완료된119/144histories 등을 새 NCP 결과로 세지 않음 |
| LRS V14 PR198 | 과거 d87ba9ca source의 NCP19settings 실제 완료. 새 cell-cache/borrowed source52488221는 sandbox10tests·동일19settings·2272828공유숫자 차이0. borrowed는 cache 대비 빨라지지 않음 | **READY NCP**: cell-cache 동일19settings(case40s/native총180s) + borrowed fixed RadauN2 하나. default legacy 유지 |
| Age-exposure PR199 | 고정57344labels·8/16/32/64 clocks v8 certificate,10fixtures+612 Decimal100checks. sensitive32−64 평균 age 차이1.3081297601e11s, 상한1.3585264602e11s. 실제 age64 block-max19756RHS/782.7s 완료 | **READY NCP**: age32/source8/n_mu8/transport16/time1, block-max binary64 diagnostics ON 한 사례,48workers·1800s. 기존 age64 source jumps는 MISSING_DATA |

## 정확한 현재 source와 배송 head

배송 commit은 source code가 마지막으로 달라진 commit과 별개다. NCP는 실제 실행 source, 선택된 최신 metadata, binary와 runtime을 각각 기록한다.

| 계열 | 실제 source/기준 | 최신 배송 HEAD |
|---|---|---|
| R9 Unit5 | 원래 allocation `REI-R9-UNIT5-20261016T024854Z_99ca7c`; deadline `2026-10-16T04:48:54.971486Z` | `8a4f5df46f6e3058f5e685b85cc1cf3c20926368` |
| FLRW | current source/intake별 고정 계약 사용 | `fd9a21c4d3886a495540b51d780a83b608e72ea2` |
| RUN13 recovery | archived standard/tight source; restored Git identity | `3dcb5f7aed8d33ff64f7952e9465f4239a216c89` |
| RUN15 | `6405bcba8ec654bf3ab98182be344cd8c3915b97` | `c875005e30d9de1ce7f426898e46fe912068412c` |
| RUN16 | additive path `research/atomic_nuclear_ssot_20261017/run16/` | `45ee7192b9d405214ec2650185aeaaa635e0fa13` |
| RUN17 | additive path `research/atomic_nuclear_ssot_20261017/run17/` | `0e23addf4fefa69287d4626622bf97505677ea43` |
| RUN18 | `6c0ae2a2ba63d42e23c7b79f989fa64639f4c942` | `99e07bcff126d0a73a03bafc4b71e0b735dbcc3e` |
| RUN19 | `e540256ecf77df1c88fccb57b81d5d60110f367c` | `c9deb933761a8d2593d1176aee028cd423bdbc05` |
| BR04 | `1b5acc89cfbcfa7b42b87255e604f8f86c6a3a01` | `a8e550846745fc89e79e84ad32567e3fb556c175` |
| BR05 | `3588027e41937f331680ab3e5c09de2f327db524` | `00e89bce3060516083d63edb857f1294ee560ea0` |
| BR06 | `0c71466c0a9b4fb357f9b168dbbe4cae74e1f8dd` | `54948439be7039c9b2b1f9580bee69bebeb80129` |
| BRPERF01 | source/runtime-only checkpoint | `bfcfffed85d45ec362cd5dccf41a8447b1f3300c` |
| LRS V14 | `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf` | `91a65b33774d948d924c357ac4ad290918d8b9ee` |
| Age v8 | `02767dc5e6c4b47883f590834aee38530852568d` | `5ef6766c66b319e48612f316ac1581bd12f6ebfc` |

## 재사용할 이론·코드와 남은 증명

RUN19 guarded cubic는 (x=\ln T)에서 균일32769node, (1\le T\le10^6\)K를 사용한다. positive smooth branch의 ideal real-node 상대 상한은 `(3/128) h^4 exp(2hM1) (M4+4M1M3+3M2^2+6M1^2M2+M1^4)`이며 저장 연구의 최대값8.5126148138e−8이다. node/source/로그좌표/쿼리와 cell selection의 binary64 불확실성까지 포함한 원 native RHS의 전 구간 enclosure는 아니다. 별도3072 stored-node rational controls의 directed upper8.8248025547e−16도 그 누락을 대신하지 않는다. cache domain `[1,0]` 보고서 metadata bug는 addendum에서 `[1,1e6]`로 교정되었고 계산값은 바뀌지 않았다. 동일 theorem/test를 새 연구처럼 반복하지 않는다.

RUN16–18의 residual·C0 polynomial을 RUN19 rate enclosure와 연결하려면 원 owner의 전체 상태·EOS·전자밀도·photoevent source를 포함하는 admissible tube에서 interval Jacobian 또는 적절한 logarithmic norm을 제어해야 한다. point Jacobian, gas interpolation agreement, conservation ledger만으로 이를 대체하지 않는다. 조건부 Markov-generator/charge-observable defect bound는 이 연결을 돕는 추가 계약으로 가능하지만 gas feedback과 event/prefix uncertainty는 별도로 남는다.

MD14 source의 실제 owner는 RUN19 `native/owner_src/axbi_sources.rs`(blob `36d24eb13db3fc42321cb0ddb165e003c0a086c7`) 및 `native/src/bass_source_bridge.rs`다. 고정 sourceID `MD14_Z002_FESC_BB50K_13P6_100_V1`, 13.6–100eV, BB50000K, z4–20, 기본fesc.2/감도.25다. (q_N=f_{esc}10^{logYield}\,SFR/(MPC_{cm}^3 n_{H0}))는 photons/H/proper-second, (n_{H0})는 a=1 comoving cm−3다. yield는 SFR(Msun/year)당 photons/second이므로 연도 변환을 다시 곱하지 않는다. (q_E=\sum q_N f_i \bar E_i)는 eV/H/s, (Q=n_H^{proper}[m^{-3}]q_E eV_J)는 J/m3/s다. source는 이미4π적분되었고 각도weights는GL/2, cell energy는 energy/count moment다. donor energy reservoir·pressure model은 이 module에서 정하지 않는다. BASS shared-Q 순수 adapter는 이 단위 계약을 재사용할 수 있지만 물리 donor closure와 two-way Einstein feedback 승인으로 확대하지 않는다.

Core17 / dossier59 / auxiliary Be를 별도 registry로 유지한다. RUN19 Li/Be tier는 기존 Li6/Li7 number-source forwardport와 VF1996 BeII/III/IV 형성 RR 세 계수이며 누락 BeI를 0으로 채우지 않는다. core13 native chemical owner 및 target19 network identifiers를 해당 local context에 보존한다. 이 count들은 서로 다른 정의이며 dossier59나 core17의 대체 종 목록이 아니다. Li7 nuclear reaction/EC/physical continuum는 이 변화로 구현되지 않았다.

## 백업 대조와 증거 수준

`intake/backup_metadata.json`에서7개 archive의 Drive+Dropbox metadata를 이번 intake에 새로 조회했다. 14개 크기가 owner receipt와 모두 일치한다. RUN19 Drive의 final handoff 본문도 직접 읽었다. 원 owner들의 전체 다운로드/해시 검증 기록은 재사용하되, 이번 intake가 대형 archive raw를 새로 다운로드/해시한 것처럼 쓰지 않는다.

| 자료 | 크기 bytes | Drive ID | Dropbox ID | owner archive SHA256 |
|---|---:|---|---|---|
| RUN19 complete | 25344988 | `1pRPhitdAFfEU8HrSC02uXXVXwRI1U8wk` | `id:BSpOijBcT10AAAAAAD_SVw` | `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62` |
| LRS cache base | 53269577 | `1TV56tJoJXkK4XyFTXTrnTgCtfDDOTJzT` | `id:BSpOijBcT10AAAAAAD_SPg` | `623797d7a8b83b078f10ffaad780c7b2c223247e8b5593110c8d5f52286991b0` |
| LRS borrowed delta | 7540740 | `1Dxj_adZQR4QEuxxatozwG10AMtvQw0z5` | `id:BSpOijBcT10AAAAAAD_SWQ` | `492681e5ed7f1f53820b3bdcf24f397cfedbb6dac20a1d6dd917c7a9e2aa866e` |
| Age v8 ready | 23247707 | `11C9PLnezdbwa2bF85lk6d8rG3msW0uJB` | `id:BSpOijBcT10AAAAAAD_SVA` | `ffb281631fdc14c683ac1e51f43112c2a4e2766cbf7519564e5e2369d073ea03` |
| Actual age64 | 3894245 | `1xHJ0mUeQL-REI3v5NvP07NToqqKDNFFn` | `id:BSpOijBcT10AAAAAAD_QgQ` | `d1a1166de0426c660d6edda4e66df50c87bc7a93267d3b78ea07d0e85e3a2178` |
| Unit5 terminal recovery | 248799 | `1ue0Aj9BzNOCNXfF6uPu4ynGDXBzumFvi` | `id:BSpOijBcT10AAAAAAD_IgA` | `19dfbaf5ffcc6fc19e11fe0afdd0635da19e9881a3a7d1d9b7084b70b3872ffe` |
| BR06 complete | 70567867 | `1WYxYUVBTK039uFca1jtQ7VmUQ1ZZlrZy` | `id:BSpOijBcT10AAAAAAD_SHA` | `3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135` |

LRS borrowed archive는 base에 추가하는 delta이며 단독 source capsule로 취급하지 않는다. RUN13을 포함한 다른 lane의 owner backup receipt는 PR/body와 actual recovery source에서 읽었지만 위 fresh14 metadata 목록에는 포함하지 않았다. Git 게시·백업 문서의 존재, 실제 계산 실행, numerical gate 통과, physical admission은 각각 분리한다. CI 메일/PR 제목만으로 과학 성공이나 실패를 판정하지 않는다.

## 현재 DAG

`INTAKE72H=COMPLETE_SCOPED`, `REUSE_TERMINAL_UNIT5=COMPLETE`, `REUSE_RUN13_M2=COMPLETE`, `REUSE_AGE64_BLOCKMAX=COMPLETE`, `LRS_CACHE_NCP=READY_NOT_RUN_HERE`, `AGE32_DIAGNOSTIC_NCP=READY_NOT_RUN_HERE`, `RUN19_CONTINUOUS_RHS_TUBE=METHOD_IMPLEMENTATION_REQUIRED`, `BR07_NATIVE_MOMENT_ENERGY=METHOD_IMPLEMENTATION_REQUIRED`, `BRPERF01=SOURCE_CHECKPOINT_ONLY`, `BASS_SHARED_Q_PHYSICAL_DONOR=OPEN`, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

`NCP_HANDOFF_KO.md`는 별도 repo들을 동시에 무제한 실행하는 캠페인이 아니라 중복 owner job을 피하는 REI coordinator 인계다. 현재 REI AGENTS의 이론/계약 작성자, 구현 담당, 독립 검토 분리를 따른다. 매 실제 단계의 source/config/receipt/DAG를 게시·백업하되 이미 종료된 과거 allocation의 deadline을 재설정하지 않는다.
