# FLRW 세 방정식 독립 검토

**판정: confirmed — 명시된 조건의 이론 환원과 source-connected native 진단 범위.** 국소 광이온화–재결합식, 주어진 spectrum 경계의 광자수식은 실제 기존 provider/event 경로와 새 adapter에서 확인됐다. Filling-factor 식은 외부 sharp-phase/density 가정을 둔 moment·inventory 환원까지 확인됐다. 독립적인 ionization-front geometry나 일반적인 물리적 (Q_V(t)) solver가 복원됐다는 판정은 아니다. 열린 blocking finding은 없다.

검토자는 production 코드와 이론 원고를 직접 수정하지 않았다. 사전 계약, 최신 source 조사, 변경된 함수·시험·CLI, 독립 Decimal oracle, native 시간적분 runner와 최종 실행 결과를 읽고 수식과 가정을 대조했다. 기존 원자율·Peebles·FLRW01 suite를 검토자가 재실행하지 않았다. 검토 범위의 파일 identity는 `REVIEW.json`에 고정한다.

## 이론과 구현의 연결

국소식은 nuclei continuity를 종별 continuity에서 제거하여 얻는다. Proper density의 −3H dilution이 fraction에서 소거되며, pure H에서는 (n_e=n_Hx)라서 recombination이 −alpha*nH*x²이다. `connected_cell`은 실제 `AtomicProvider::raw_coefficient/cross_section`, `hhe_rhs`, `homogeneous_photo_rates`를 호출한다. 같은 absorption event가 HII source와 photon decrement를 소유하며 cMpc⁻³↔proper cm⁻³ 변환도 실제 경로에서 대조한다. 별도 수식만 다시 구현한 PASS가 아니다.

평균 유도는 (X_V), (X_M), geometric (Q_V)를 구별한다. Fixed comoving domain에서 volume-average derivative에 필요한 advection/compression covariance와 boundary 항, open domain의 per-H 분모 변화 항의 부호가 맞다. Native ensemble의 더 좁은 범위는 공통 H, 고정 weights, co-expanding cells, peculiar advection/compression 및 intercell matter transport 부재다. `filling_defect`는 외부 (Q_V,\dot Q_V)를 받아 inventory를 진단한다. `sharp_filling_rhs`는 (X_M=Q_V\Delta_I)와 외부 ΔI 변화율을 적용하며, (Q_V\dot\Delta_I)를 생략하지 않는다.

Native sharp 시험의 순간 binary cells는 manufactured moment fixture다. 각 고정 cell이 이후에도 0/1 상태를 유지한다는 증거나 움직이는 front 속도를 제공하지 않는다. 이론 원고가 이 한계를 명시하므로 조건부 고전적 Q식 환원은 인정하되 geometry dynamics 검증으로 확장하지 않는다. Clumping의 conditional (C_I)와 global (C_{\rm HII}=C_I/Q_V)도 구별됐다.

Spectral photon equation의 conservative “3H + frequency divergence”와 expanded “2H − Hnu frequency derivative”는 일치한다. (q=a\nu) 좌표에서는 spectral Jacobian이 (a^2), 움직이는 threshold는 (q_0=a\nu_0)다. Fixed physical bin의 redshift contribution은 upper inflow minus lower exit이고, internal edge는 동일 flux를 공유하여 소거된다. `photon_balance`가 이 부호와 proper/comoving 차이를 실제 구현한다. 주어진 bin count만으로 arbitrary edge spectrum을 복구했다는 주장은 하지 않는다.

Case-A primary-only/export, Case-A explicit diffuse, Case-B local OTS가 분리됐다. Native 새 adapter는 Case A/B를 명시적으로 선택하되 tracked recombination photon을 덧붙이지 않는다. 기존 `hhe_rhs`의 thermal·escaping-energy output은 소비하지 않는다. 따라서 Case-B coefficient를 사용했다는 이유만으로 기존 toy thermal closure까지 OTS로 인증하지 않는 경계가 유지된다.

## 발견 및 수정

**IR-F01 — public Ensemble·CellResult의 finite/domain 검증 누락: 수정 확인.** 정적 검토에서 초기 `filling_defect`와 `sharp_filling_rhs`가 externally modified `Ensemble`을 검증하지 않는 경로를 확인했다. `x_mass=NaN`은 전자에서 NaN 결과를 포함한 성공 반환을 만들고, 후자에서는 mass-closure 비교를 우회할 수 있었다. 두 진입점에 `validate_ensemble`이 추가되어 모든 공개 수치 필드의 finite 여부, fraction 범위, 양의 mean density 및 비음수 source/sink를 검사한다. NaN/Inf/범위 초과/음의 eta/0 density를 넣은 새 시험이 통과했다. 후속 동일 경계 점검에서 `ensemble`이 public `CellResult`의 음의 개별 density를 양의 aggregate에 숨길 수 있는 점도 확인했다. `validate_cell_result`를 가중 전에 호출하여 모든 cell의 양의 density, finite 필드와 fraction·비음수 rate/flux 도메인을 확인하도록 수정됐다. 양의 총 density 아래 음의 개별 density, NaN fraction, Inf derivative를 양의 weight와 0 weight 모두에서 거절하는 시험을 포함한 최종 21개 focused 시험이 통과했다. 정상 source·photon 식의 오류는 아니지만 공개 API의 실패 분류에 필요한 수정이었다.

Co-expanding native average 가정을 문서에 명시하고, 실제 collisionless photon E3와 후속 grey coupled matter/photon 유도를 구별하도록 요청했다. 이는 구현 범위와 실행 범위를 일치시키는 수정이며 추가 물리 가정을 암묵적으로 도입한 것이 아니다.

## 실제 증거

| 검사 | 확인 결과 | 의미 |
|---|---|---|
| 최종 Rust crate | 84 PASS, exit 0 | 기존 63개와 새 21개; Ensemble와 CellResult guard 모두 반영 |
| 최종 변경 모듈 | 21 PASS, exit 0 | CellResult 개별 도메인 검사를 포함한 마지막 focused 실행 |
| 독립 Decimal70 E2 | 144 cell, 24 photon, 4 ensemble; 2352 checks PASS | actual provider 계수는 고정 입력으로 재사용하고 사건·평균·단위·flux 조합을 독립 산술로 비교 |
| 국소 RHS 최대 gross-flux 정규화 차 | (9.05\times10^{-16}) | 사전 (2\times10^{-12}) 기준 이내 |
| Photon proper derivative 최대 차 | (2.31\times10^{-16}) | proper/comoving dilution 및 edge 부호 대조 |
| E3 실제 native 호출 | 570회 | source-free, collisionless, prescribed FLRW, (p=3), 유한 물리 energy band와 외부 high-energy tail |
| E3 RK4 refinement | 16/32/64 step; 최종 상대오차 (5.32\times10^{-9}) | 오차 감소비 약 16으로 4차 거동 확인 |
| E3 DOP853 | 상대오차 (1.36\times10^{-11}) | analytic (N_g\propto e^{-2Ht}) 대조 |
| E3 inventory residual | 최대 (1.59\times10^{-16}) | supplied boundary closure 내부의 number ledger 일치 |

`FINAL_INTEGRATION.json`의 최종 84개 실행은 Ensemble와 CellResult guard 모두 반영한 최종 source/binary에 결속되어 있다. 같은 최종 probe로 E2·E3도 다시 PASS했으며, 검토자가 receipt의 5개 source/binary SHA와 실제 파일을 대조했다. Native 담당의 이전 82개와 root의 이전 83개 기록은 각 snapshot 증거로 보존하며 최신 84개와 혼동하지 않는다. `coding/REVIEW_FIX_RECORDS.json`과 21개 focused PASS도 마지막 수정에 대한 별도 증거다.

Root 독립 oracle의 첫 실행은 실패했으며 숨기지 않았다. Photon mode의 입력 N은 comoving인데 oracle의 proper dilution 항에서 N/a³ 대신 N을 쓴 구현 오류였다. Native 식은 이미 맞았다. Oracle의 단위 변환과 같은 gross scale만 수정하고 threshold를 유지한 재실행이 PASS다. `ORACLE_FAILURE_RESOLUTION.json`과 최초 FAIL 기록이 보존되어 있다. 이 실패는 물리 이론이나 native solver 실패로 분류하지 않는다.

Negative control은 추가 −3Hx, comoving 변수의 중복 −3HN, lower-edge omission/sign reversal, fixed-electron recombination, (X_M=X_V) 무조건 동일시 등을 검출한다. 동일 bin photon count라도 다른 boundary trace가 다른 derivative를 만드는 예도 실제 실행됐다. 재결합 계수 자체의 물리적 정확도를 이 새 회귀검사의 독립 성과로 다시 세지 않았다.

E3 runner는 매 stage의 numeric lowest-bin amplitude에서 power-law edge 값을 복구해 실제 native photon API를 호출한다. Analytic trajectory를 RHS에 직접 주입하지 않는다. 두 적분법과 analytic reference의 비교는 해당 prescribed spectral closure 안의 유용한 검산이다. 표시된 그림도 “no absorption, prescribed spectrum”을 명시한다. 이 결과를 coupled reionization history, thermal/energy evolution 또는 geometric filling history로 승격하지 않는다.

## 종료 조건

선언한 bounded loop의 검토는 종료한다. F04 nonlinear certificate, strict historical error/public-width gate, 물리 provider admission, general Bianchi RT 및 실제 EoR history는 그대로 미완료다. Phase geometry 없이 “세 식이 일반적으로 자동 복원됐다”고 쓰는 주장은 지지하지 않는다. 이 범위와 최종 파일 identity를 유지하면 추가 반복 감사 없이 게시할 수 있다. 이후 Git ref와 cloud backup ACK의 확인은 별도의 게시 증거다.
