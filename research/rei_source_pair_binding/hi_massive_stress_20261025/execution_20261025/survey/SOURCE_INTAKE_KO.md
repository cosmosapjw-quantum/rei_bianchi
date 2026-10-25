# REI 후속 source intake — 실제 입력과 과거 규약의 경계

작성 역할: `/root/source_and_review` · read-only source intake.  
대상일: 2026-10-25 · 고정 authority `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`.  
부모가 이번 turn에서 관측한 central: `fc159d2b15843bdfe81af0840bc07392a4977680`.  
보호 ANGTHERM02: `research/rei-coupled-isotope-contract-20261022` / `8d10231b1f0f788164d5eadbe1bcee0b802cceca`, **READ_ONLY**.

## 1. 결론과 읽은 범위

완료된 native-HI 단위는 실제 저장된 HI/z2.479의 4,368개 양의 radial atom과 같은 사건의 A/K/B/P를 연결했다. 이 증거는 그대로 재사용한다. 과거 stock/work의 synthetic `N=2, M=1, Lbar=5, r=(1/2,1,2)`를 실제 HI stock이나 기하로 채택할 근거는 없다. 이번 첨부에서 실제 물리입력 대신 확인한 것은 과거 history 주입 API, 기본 우주론 reference, 수치 규약, 검토 절차다.

이 문서는 새로운 이론·연산자·코드·실행계약을 제안하거나 심사하지 않는다. 다음 theory/code의 독립 reviewer가 author 역할을 갖지 않도록 기존 원문에서 확인한 입력 사실만 기록한다. 현재 원문을 읽고 보존한 범위는 아래와 같다.

| 자료 | 실제 수행 | 이번 읽기의 의미 |
|---|---|---|
| stock/work C `93e6794c90f6…` | 이론2개, source binding2개, `NEXT_PHYSICAL_BINDING_KO.md`, `PRIMARY_SOURCE_MAPPING.json` exact member6개 선택 추출·읽기 | 기존 6행 입력의무와 owner/단위의 출처 |
| 완료 native-HI | source card, source binding, 최종 admission 실제 읽기 | 과거 메모의 radial-measure 미결만 최신 완료 상태로 갱신 |
| 첨부01/04/05/07/08 | 원문 전체 읽기 | 감사·개발·figure 절차. 실제 HI 입력값 없음 |
| 첨부14 | physical initial/units, history API, recombination의 관련 부분, species/components, state 및 일부 audit/tilted-matrix 코드 선택 읽기 | 과거 기본값·API·질량에너지 표기의 존재 확인. 신규 실행 없음 |
| 첨부12 | `00_READ_FIRST.md`, scientific contract, conventions 선택 읽기 | harness baseline. source-qualified HI cohort 아님 |
| 첨부17 | own `src/**/*.rs` 40개 keyword scan, `src/core/conventions.rs` 직접 읽기 | 기존 geometric convention 확인. 의미 있는 electron/HI physical-input keyword 결과 없음 |
| 첨부20 PDF | metadata/36쪽 구조; PDF쪽1–3,7,13,17–19,29–31,34–36 text-only 읽기 | HTT 종합판의 제한 R3 benchmark와 범위. 실제 HI cohort 바인딩 아님 |
| 첨부10/11/18/19 및 큰 toolchain/vendor | 별도 coding agent의 archive inventory·후보경로 결과 재사용 | 모든 본문을 심사했다는 주장을 하지 않음 |

선택 원문의 byte identity는 `source_intake/PRIOR_SELECTED_MANIFEST.json`, `source_intake/ATTACHMENT_SELECTED_MANIFEST_PRIVATE.json`, `source_intake/SOURCE_INTAKE_FACTS.json`에 기록했다. 직접 읽은 것, 문자열 scan, inventory를 서로 구별한다. 이 조사만으로 모든 archive 내용에 입력이 없다는 전역 부재 판정을 하지 않는다.

## 2. 실제 cohort의 여섯 입력 행

| 행 | 이번에 확인한 실제 근거 | 아직 바인딩되지 않은 부분 | 상태 |
|---|---|---|---|
| `t0,t1,z(t); source(t)` | admission의 실제 selector는 HI/z2.479. 원 CSV 전체는 32,592행이며 채택된 selector는 4,368행 | 실제 시간 구간·시계와 redshift mapping, source history·적분 가능성. 다른 CSV행이 있다는 사실만으로 시간 보간 규칙이 생기지 않음 | 실제 history 미결 |
| `n_HI(t),n_ref(t),X_HI(t)` | native rate는 per absorbing target per proper second. 과거 API에는 수소 density 기본식과 `x_e=n_e/n_H` 프로토콜이 있음 | 현재 HI source와 같은 물리상태의 실제 `n_HI/n_ref/X_HI`, 단위 및 조성 연결. 과거 기본 `Omega_b h²`를 자동 채택하지 않음 | 실제 density 미결 |
| `nu0` 또는 `N0,U0,L0` | 과거 stock theory는 양의 유한 초기 측도/모멘트를 입력으로 받음 | 실제 초기 epoch·stock·단위·출처. 새 이온화 source가 초기 nonthermal stock의 0을 증명하지 않음 | 실제 IC 미결 |
| `frame,clock,a_i(t),H_i(t)` | 현재 HI는 bath-frame rest target, proper second. 과거 Bianchi I stock은 지정 양의 C¹ scale factors와 orthonormal momenta | bath와 수송 congruence의 일치 또는 변환, 실제 기하 이력·scale-factor ratios·팽창률 | 실제 geometry/frame match 미결 |
| `mu_t(k,Omega),L(t)` | 실제 radial atom `mu=Σwδ_k`가 z2.479에서 완료·admitted. χ는 represented binary64 13.6eV, photon support 상한50,000eV. CSV에 angular열 없음 | isotropy는 CSV로 측정된 사실이 아닌 선언한 closure. 시간 의존 측도·각도 자료 및 해당 모델의 물리 오차 | **단일 epoch radial measure 완료**, 시간/각도는 조건 유지 |
| `transport,collision,photon_supply` | native admission은 `NO_DEPOSITION_SELECTED_MODEL`, physical secondary heat=null. 과거 stock/work은 조건부 collisionless 수송 식 | 실제 collisionless 구간, stopping/secondary deposition, 유한 photon stock 또는 replenishment의 선택과 공급 history | 실제 결합 입력 미결 |

이는 정보·바인딩 상태다. 물리적으로 불가능하다는 strong no-go가 아니며, 특정 외부 solver를 다시 실행해야 한다는 자동 요구도 아니다. 닫힌 finite 단위의 연구는 부모가 실제 입력·가정을 고정한 새 계약에서 정한다.

## 3. 기존 stock/work가 이미 정한 의미

원 stock 이론은 `M=mc²>0`를 외부 **에너지** 매개변수로 받는다. `k=sqrt(M²+c²|p|²)-M`는 kinetic energy이고, `N=∫dnu`, `U=∫k dnu`, finite support가 입력이다. work 이론은 같은 물리 momenta와 physical-density measure를 사용한다. 저장된 소스에서 실제 전자의 M 수치를 고정한 바는 없다.

과거 source 연결은 `I_t=a n_HI mu_t`, `Q_N=a n_HI A`, `Q_U=a n_HI K`로 기록돼 있다. `n_ref(a X_HI)=a n_HI`는 한 번 적용하고 eV/J, cm^-3/m^-3 변환도 별도로 한 번 적용한다. `K`는 primary nonthermal energy이고 실제 stopping heat가 아니다. bound electron을 free electron으로 분류하는 사건에 `MN`을 새로운 ionization energy source로 더하지 않는 owner 규약도 기존 work 이론에 있다.

`N=2, M=1, Lbar=5, r=(1/2,1,2)`는 원문이 synthetic control이라고 명시한 fixture다. `N_t=2`와 `Lbar=5`는 그 fixture에서 유도한 값이다. 저장된 `mixed_energy_interval`은 synthetic integration check 입력이며 현재 HI 실제 stock에서 얻은 값이 아니다. isotropic subset에서 기존 free-angle bounds가 유효하다는 말과 그 subset에서 free-angle 극값이 sharp하다는 말도 구별한다.

선택 추출된 `SOURCE_BINDING.json`들의 `STATIC_PREPARED`/`NOT_ISSUED`와 native `C1_C5_PREPARED_NOT_EXECUTED`는 역사적 준비 snapshot이다. 최종 admission을 이 문자열로 되돌리지 않는다. 현재 native 최종 판정은 `ADMITTED_SCOPED_NATIVE_HI_COMMON_MEASURE`, S=`8d68dff35ca2bdc456049081132a7d2449b29143`, D=`fc159d2b15843bdfe81af0840bc07392a4977680`다.

## 4. 첨부에서 실제 찾은 물리 규약

### 4.1 첨부14의 recombination/history

`14-bianchireview87.tar-1-.gz::./bianchi/thermo/recombination.py`에는 `_ME_EV = 510998.95`와 eV 주석이 있다. 이 파일 전체에서 `_ME_EV`는 선언 한 번만 나타난다. 따라서 과거의 electron mass-energy **표기**가 존재한다는 근거이며 현재 REI runtime의 질량 owner로 이미 바인딩됐다는 근거는 아니다. 같은 파일의 `_EION_H=13.605693`도 별개의 역사적 recombination convention이다. 이를 현재 native-HI의 χ=13.6으로 바꾸거나 그 반대로 덮어쓰지 않았다.

`physical/units.py`는 내부 자연단위 `8πG=c=1`와 팽창정규화 τ를 경계에서 변환하는 모듈이다. `history_api.py`는 `x_e=n_e/n_H`, `n_H=8.50e-6 Ω_b h²(1+z)^3 cm^-3`(Yp=.24), proper-time rate와 τ-rate의 구별, isotropic history와 anisotropic geometry 결합 규약을 명시한다. 이 인터페이스의 존재는 실제 source-selected neutral-HI history의 존재와 같지 않다. 특히 He를 포함하는 `x_e`로부터 HI neutral fraction을 단순히 `1-x_e`로 정할 수 있다는 바인딩은 읽은 원문에 없다.

기본 Saha 격자는 z=3000…500이고 평형 근사가 z≳1300에 적합하다는 제한을 스스로 둔다. 기본 Peebles 격자는 z=3000…200이다. 현재 native selector z=2.479에 사용할 실제 입력 history는 이 기본값으로 지정되지 않는다. `TabulatedHistory`는 외부 격자와 metadata를 받는 통로지만 이번 조사에서 HI native source와 연결된 그 표를 채택하지 않았다. `physical/initial.py`의 flat-LCDM today 값도 회귀용 기준값이며 실제 HI cohort 초기조건으로 정하지 않았다.

`species.py`/`components.py`는 Hubble-normalized species source와 `ΣQ_i=0` 교환 규약을 갖는다. 이는 actual source normalization을 연결할 때 확인할 기존 owner이며, 이번 source intake는 이 코드의 정확성을 재검증하거나 새로운 결합을 구현하지 않았다. `tilted_mass.py`의 mass는 PSTF derivative mass matrix 문맥이며 electron rest-mass scalar 공급자가 아니다.

### 4.2 첨부12/17/20과 절차 문서

첨부12의 첫 문서는 archive 자체를 harness baseline sharing snapshot으로 규정하며 solver/scientific-output가 없다고 기록한다. 그 역사적 gate 상태를 현재 REI에 이식하지 않는다. conventions에는 명시 adapter가 없으면 c, ħ, kB를 유지한다는 정책과 transport/collision/observer frame 구별이 있다.

첨부17은 own Rust source40개를 제한 keyword로 scan하고 geometric conventions를 직접 읽었다. `electron/hydrogen/reionization/recombination/n_HI/restmass/510998`에 유의미한 공급 데이터가 없었다. case-insensitive eV 검색은 지역변수 `ev`를 오탐하므로 density나 mass evidence로 계산하지 않았다. 모든 source의 물리 정확성 review는 수행하지 않았다.

첨부20 PDF의 제목은 `HTT 수학·물리·통계 종합 이론 보고서`이며 2026-09-13 편집판이다. PDF쪽17–18의 R3는 LRS Bianchi I, 서로 반대인 두 dust stream, 초기 isotropic Planck radiation, Λ의 제한 benchmark다. PDF쪽29–31은 fixture·조건부 입력과 관측/일반 solver 완성을 구별한다. 이 보고서는 현재 HI 물리 시간·밀도·초기 nonthermal stock을 제공하지 않는다. PDF 전체를 시각 심사한 것은 아니며 새 render0이다.

01/04/05는 solver 감사·개발·DAG 절차이고 07/08은 figure review template다. 읽은 문서 안의 빈 입력란이나 일반 procedure 문구에서 실제 HI 데이터나 추가 실행 권한·예산을 생성하지 않는다. 해당 workflow 적용은 현재 사용자 지시와 부모의 1.0.0 작업 선택에 따른다.

## 5. provenance·보존·현재 상태

- 원 stock/work archive SHA256: `93e6794c90f61cd281e0d4370e5298538277463ff6835657a79b901516f17e9c`.
- native source CSV SHA256: `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`, read commit `b8882d026887f375acf90768d4e3740eb03da226`, science commit `54477b285e0c712610453bca1408a076af43521d`.
- native final C SHA256(부모의 이번 실제 재확인): `11740e51b7b098d763bb6fed62c127b85bfb164d392ec4495a50f011746dafb4`.
- 모든 전체 SHA 및 선택 원문 identity는 `source_intake/SOURCE_INTAKE_FACTS.json`와 선택 manifest에 저장했다. private attachment snapshot은 조사 근거용이며 공개 report에 전체 첨부/PDF 본문을 복제하지 않는다.
- 이 intake의 신규 science0, tests0, CAS0, render0, 연구 코드 실행0, Git mutation0, push0, 새PR0. 파일 복사·해시·본문 추출은 source intake 작업이다.
- 새 theory/code authoring0. 이 문서는 아직 후속 theory/code/raw의 independent PASS가 아니다. 부모가 frozen 대상을 제공하면 별도 한 번의 native independent pass를 수행한다.
- 과거 실행 debit·10s cap 초과·UNKNOWN_NOT_ZERO·NOT_FROZEN을 변경하지 않았다. 다음 science 예산을 여기서 정하거나 reset하지 않았다.
- C23E 조건부 D43K, HE94 부분 창, PHYS85 준비, ANGTHERM02 예약을 변경하지 않았다. 전체 모델 완료율은 null, L4 준비 false를 유지한다.

부모는 이 input-fact report를 최신 repo/conversation/backup 조사와 함께 종합한다. 최종 실행·admission·게시 상태는 부모의 단계별 receipt가 권위다.
