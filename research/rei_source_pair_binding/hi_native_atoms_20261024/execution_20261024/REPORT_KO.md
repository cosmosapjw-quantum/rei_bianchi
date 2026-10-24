# HI native atoms: 최종 과학 보고서

## 현재 판정

HI_NATIVE_ATOMS_20261024의 실제 HI 4,368개 원자와 공통 양의 측도를 직접 연결했다. 단 한 번의 실행과 독립 theory/source/code/raw 검토를 마쳤으며, root 판정은 **ADMITTED_SCOPED_NATIVE_HI_COMMON_MEASURE**다. finding 0, repair 0이다.

이 문서는 과학 게시 S를 위한 스냅샷이다. R1–R9와 C1–C9는 완료했고, R10/C10의 최종 백업·게시·인계는 후속 delivery 기록에서 닫는다. 현재 단계 수는 18/20이며 전체 모델 완료율은 null, L4_ready=false다. RESULT_SUMMARY.json의 ROOT_DECISION_REQUIRED는 root 판정 이전 표시값을 보존한 것이며 현재 판정은 ADMISSION.json을 따른다.

고정 authority는 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17의 research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md다. 기존 L0의 scoped admission과 source/HI-summary/pressure/stock/work 결과를 재사용했다. 과거 22/66/83 및 기존 source suite는 재생하지 않았다. 현재 API는 새 owned leaf에 추가하며 기존 공개 API와 energy owner를 변경하지 않는다.

## 1. 실제로 새로 연결한 입력

최신 소스 조사에서 bass_cr의 저장 CSV를 확인했다.

| 항목 | 실제 identity |
|---|---|
| 읽은 repository/commit | cosmosapjw-quantum/bass_cr @ b8882d026887f375acf90768d4e3740eb03da226 |
| 원래 science commit | 54477b285e0c712610453bca1408a076af43521d |
| 원래 실행 identity | 277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955 |
| 입력 경로 | research/cr_c23b_source_frame_20261023/source_providers/runs/c23b_pw19_spectral_source_20261023_v1/photoelectron_atoms.csv |
| 전체 CSV | 1,681,578 bytes, 32,592 data rows, CRLF 보존 |
| Git blob | b01f4c94faffd9a44ca4dcf31231bd6b7da2b766 |
| SHA256 | f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3 |
| 소비 selector | elemental HI, z=2.479, 4,368행 |
| 열 | redshift, channel, kinetic_eV, number_weight_per_target_s |
| 각도 정보 | CSV에는 없음; 별도로 선언한 isotropic closure 사용 |

공급자와 validator 원문에서 같은 atoms16이 CSV와 historical summary를 만들었음을 확인했다. 새 donor quadrature를 수행하지 않았다. CSV의 decimal spelling을 binary64로 round-trip한 후 represented value를 exact Fraction으로 취했다. 입력이 이미 잃어버린 물리 정보나 float 이전 정밀도를 복구한다는 주장은 없다.

고정 물리 조건은 ground-state elemental HI, bath-rest target, proper second, zero recoil, represented binary64 13.6 eV threshold, photon upper endpoint 50,000 eV다. 원자 k는 primary excess kinetic energy다. no-deposition 선택 모델에서 thermal source는 0이고 실제 secondary_heat는 null이다. isotope mapping과 실제 stopping은 별도 공급 의무다.

## 2. 이론 유도와 코드 대응

양의 가중치 w_j와 비음수 kinetic coordinate k_j에 대해

$$
\mu=\sum_jw_j\delta_{k_j},\quad
A_*=\sum_jw_j,\quad K_*=\sum_jw_jk_j,\quad
B_*=\chi A_*,\quad P_*=\sum_jw_j(\chi+k_j)=B_*+K_* .
$$

A의 단위는 target⁻¹ proper-s⁻¹, K/B/P는 eV target⁻¹ proper-s⁻¹다. 모든 곱과 합은 represented 입력의 exact 연산이다. finite support L에 대해 0≤K_*≤L A_*다.

정규화 m=a X_HI와 고정 원자에 대한 접선 dm=a dX_HI+X_HI da를 exact 연산으로 만들면

$$
q_E=m(0,B_*,-P_*,0,0,K_*),\qquad
Dq_E[v]=dm(0,B_*,-P_*,0,0,K_*).
$$

energy owner 순서는 thermal, binding, UV, dynamic_escape, source_reservoir, primary_nonthermal이다. 입자 순서는 HI,HII,e_nt,e_th,photon이며

$$
q_n=mA_*(-1,1,1,0,-1),\qquad
Dq_n[v]=dmA_*(-1,1,1,0,-1).
$$

exact energy sum, HI+HII의 핵수 source, HII−e_nt−e_th의 전하 source는 모두 0이다. e_nt는 별도 비열적 전자 pool이다. μ⊗dΩ/(4π)의 isotropic closure에서 flux/STF injection source는 0이며, 이는 CSV에서 각도를 측정했다는 뜻이 아니다.

새 함수는 load_selected_atoms, native_moments, source_per_href_native, source_jvp_native, rounding_decomposition이다. immutable dataclass와 stdlib Fraction을 사용한다. 실제 소비 행, selector, support, 단위, normalization-once, bool/nonfinite/negative 거절, overflow, subnormal 및 final-underflow-to-zero를 동결 계약으로 연결했다.

작은 두 원자 (k,w)=(0,1),(2,3), χ=4에서는 A=4,K=6,B=16,P=22다. m=1/2의 에너지는 (0,8,−11,0,0,3), 입자는 (−2,2,2,0,−2)다. 이 손계산 예제와 실제 4,368행은 서로 다른 검증 역할을 갖는다.

## 3. 원래 summary와의 차이를 완전히 분해

원래 공급자는 다음 순서의 float 연산을 했다. RN은 binary64 반올림이며 fsum은 실제 저장 summary 단계다.

- Ahat=fsum(w)
- Khat=fsum(RN(w*k))
- Bhat=RN(χ*Ahat)
- Phat=fsum(RN(w*RN(k+χ)))

S_K=ΣRN(wk), S_P=ΣRN(w RN(k+χ))를 반올림된 항들의 exact 합으로 놓으면,

$$
\Delta A=\widehat A-A_*,
$$
$$
\Delta K=(\widehat K-S_K)+\sum_j[RN(w_jk_j)-w_jk_j],
$$
$$
\Delta B=[\widehat B-\chi\widehat A]+\chi\Delta A,
$$
$$
\Delta P=(\widehat P-S_P)
+\sum_j[RN(w_jRN(k_j+\chi))-w_jRN(k_j+\chi)]
+\sum_jw_j[RN(k_j+\chi)-(k_j+\chi)].
$$

네 분해의 residual은 모두 exact0이었다. 기존 summary residual을 다른 energy owner로 옮기지 않았다. 기존 A/B/P/K와 donor P−B−K residual −1.6155871338926322e−27을 그대로 보존한다. represented B+K−P의 정확한 부호는 반대인 +1.6155871338926322e−27이다.

| 모멘트 | native 표시값 | historical−native 표시값 | 절대 상대 차이 |
|---|---:|---:|---:|
| A | 1.1871043740697437e−12 | +9.919939247024809e−29 | 8.356417062988603e−17 |
| K | 4.4362225405110365e−12 | −3.643740019295899e−29 | 8.213609633019342e−18 |
| B | 1.614461948734851e−11 | +2.2555320725553122e−27 | 1.3970797356499025e−16 |
| P | 2.058084202785955e−11 | +6.035075384697211e−28 | 2.932375350108487e−17 |

A/K/P의 실제 fsum 단계 오차는 각각 +0.4912115992468191, −0.044810520718563396, +0.17034200416458134 ulp다. 모두 동결된 finite-data 1-ulp 조건을 만족했다. 이는 이 저장 artifact의 산술 결속 certificate다. fsum에 대한 보편 정리, donor quadrature의 새 정확도 보장, 전체 물리 오차의 상한으로 확대하지 않는다. 기존 L0 gate 2e−12 및 donor gate는 그대로다. 원래 summary physical source-consistency tolerance는 NOT_EVALUATED_NO_FROZEN_CRITERION이다.

## 4. 실제 실행과 독립 검토

| 관측 | 결과 |
|---|---:|
| scientific child / fixture group | 1 / 1 |
| 실제 primary rows | 4,368 |
| 직접 scalar RN checks | 13,105 |
| controls | 13 groups |
| 세 bin의 행 수 | 192 / 3,616 / 560 |
| 네 delta identity residual | 모두 exact0 |
| A/K/P finite fsum certificate | 모두 true |
| 정적 검토 이후 frozen files | 9/9 unchanged |
| exit / timeout / stderr | 0 / false / 0 bytes |
| CPU / launch-inclusive wall | 0.446399 s / 0.44698534999770345 s |
| 동결 CPU / wall 제한 | 2 s / 10 s |
| retry | 0 |

13,105개는 scalar 연산 검사 수이며 독립 물리 모델 수가 아니다. 독립 수치 참조는 float.as_integer_ratio를 공통 2의 거듭제곱 denominator에 맞춘 정수 dyadic accumulator로 구현했다. 주 Fraction 합산을 다시 호출하는 검산으로 대체하지 않았다.

source control m=6/35의 최종 rounded energy sum은 −1.0097419586828951e−28, 계산된 예산은 4.543838814073028e−28이다. signed JVP control dm=−7의 최종 합은 +6.462348535570529e−27, 예산은 2.261821987449685e−26이다. exact sums는 0이지만 rounded sums를 0이라고 보고하지 않는다. 이 정규화 값은 control이며 실제 우주 밀도·이력으로 채택하지 않았다. exact zero, nonzero subnormal, final-underflow-to-zero를 별도 표시했다.

독립 reviewer /root/source_intake는 후보 이론과 구현을 작성하지 않았으며, 원 CSV·공급자 source·수식·diff·raw를 한 pass에서 읽었다. 결과 PASS_SCOPED, findings=0, repairs=0. cross-family 실행은 NOT_RUN_OR_NOT_OBSERVED이며 실제 backend model identity는 추정하지 않았다. 코딩 요청 모델은 gpt-6.1-sol/high, 관측 backend는 UNKNOWN이다. Wolfram은 보조 기호 검산이고 독립 model review로 세지 않는다.

주요 identity:

- native_source.py SHA256 b812eb35ff23f42800df11cf2a364746566d540b49af501b65ea421eefb8bb97
- stdout SHA256 0335abad8879817b5e61b0f5ef7120009c2e18251be4fe82ea3e48c8e7aa5669
- resource receipt SHA256 300ee32b2edf3c968b81d630faf2f8f2f40094aa221dcef56172617862b293f5
- independent execution review JSON SHA256 c3f90f915a48fec58b5eef92855300a201d84b226f2ddc0a1dc7b8dc4ffc007d

## 5. 최신 자료 조사 범위와 통합

| 조사면 | 실제 읽은 범위 | 완전성의 경계 |
|---|---|---|
| 연결된 owner repository | 51개 metadata | 각 repo 본문 전체를 읽은 것은 아님 |
| branch heads | 2,244개, 116 GET pages | 51개 모두 empty terminal 확인; 모든 branch payload 열람은 아님 |
| 관련 7 repo | 1,334 heads, 24 pages | pin 기반으로 필요한 source 본문 선택 |
| PR | 7개 repo의 최신 10개씩, 70 records | 모든 PR/comment 전수 아님 |
| source text | 초기 18개, full12/selected6; 최신 return4 추가 | 실제 읽은 파일별 범위 보존 |
| Dropbox | REI direct133, 연구백업 recursive154 | 해당 listing terminal 확인 |
| Drive | REI folder209; 추가 keyword185 | connector pagination 한계 때문에 계정 전체 완전성 주장 없음 |
| 사용자 첨부 | 초기20개, 7 archive member inventories 9,100개 | 필요한 파일 선택 읽기; 전체 archive science 재검증 아님 |
| 비공개 과거 대화 | Personal Context 실제 unavailable | 과거 대화가 없다는 뜻이 아님 |

private owner/all51/PC/bulk 조사 원문은 별도 private appendix로 보존했다. public Git에는 관련 과학 요약·출처만 게시한다.

central은 조사 시작 3423209a55d800de7e464f16fc600ec0c278833f에서 407381b302d8b98f251b54d277823997bc4fca9f로 진행했다. 실제 diff의 5 commits/8 assembly paths는 새 owned leaf와 겹치지 않았고 AGENTS blob은 429a5a13ee75b1222bc50627f8d5973d01dd21c4로 유지되었다. 최종 게시 직전에 다시 확인한다.

| 병렬 결과 | 최신 관측 | 현재 HI와의 관계 |
|---|---|---|
| CR103 | d3d9b0de… science / bdcb576f… docs, 조건부 finite EI chain20/20, 8 cases/96 primary RHS/24 independent RHS | 전체 N4/N5 PARTIAL_OPEN; HI 전체 stopping으로 전이하지 않음 |
| PHYS88/HH145 | 92dec7cd… FINAL, 조건부20/20, 482 assertions, 독립8field 최대4.2887098119610273e−13 | parent/supplier PARTIAL, consumer false, fast stopping0 |
| HE99 | 8d481ed4… finite-M shell science18/20,14tests/6fixtures | actual event amplitude와 physical recoil provider 미공급 |
| REC134 | ccf2bd08… finite20/20, 저장 diagnostic만 수정 | physical epsilon=null,H5 uncalibrated,physical HOLD,REI activation=false |
| HE98 | d477aafc… finite20/20,B3 dual metadata 확인 | physical provider=false; HE94 부분 창 유지 |
| BASS B3c | backup-only finite20/20 원문; Git TOOL_REJECTED_NO_ACK | cold f_plus0,14 rays,τ≤0.1의 별도 모델; 실제 HI IC로 채택하지 않음 |
| Vigil D3 | 읽은 pin은 S1/RED14/S2 진행; 뒤 S2 backup metadata 관측 | later payload 미심사, native owner 미결,production HOLD |

CR103·PHYS88·HE99의 최신 원문 4개와 Git blob 4/4 확인은 survey/LATEST_PARALLEL_407 및 연결된 source에 있다. source-reported donor 실행과 이번 스레드의 직접 실행을 구별했다. C23E 조건부 D43K, HE94 부분 창, PHYS85 역사 실패·미측정 비용, ANGTHERM02 예약을 보존한다.

## 6. 문헌과 외부 도구의 기여

Puchwein et al. 2019, MNRAS485,47, DOI10.1093/mnras/stz222와 arXiv1801.04931v1을 읽어 UV background와 photoionization/heating source의 맥락을 대조했다. 실제 donor가 사용한 Taira2025 PW19 v1.0.0 release DOI10.5281/zenodo.15367103은 별도 provenance다. 해당 release의 직접 웹 접근은 확보하지 못했으므로 원 release 파일을 재검증했다고 표시하지 않는다.

Verner et al. 1996, ApJ465,487, astro-ph/9601009v2의 ground-state fit 조건을 donor HI 조건과 대응했다. Heinzle–Uggla gr-qc/0512031의 Bianchi I Vlasov 식은 기존 stock/work 연결에 재사용했다. source rate와 현재 stock을 같은 물리량으로 대체하지 않았다.

Exa 검색2회, SciSpace1회가 원전 후보를 좁혔고 실제 primary PDF를 읽었다. Wolfram context1회 및 evaluator1회에서 ledger/JVP/핵수/전하와 손계산 예제를 확인했다. evaluator outer5s/inner3s, 실제 remote CPU는 UNKNOWN_NOT_ZERO다. 새 strong no-go나 문헌 최초성 주장은 없다.

원전 링크:
- https://arxiv.org/abs/1801.04931
- https://doi.org/10.1093/mnras/stz222
- https://arxiv.org/abs/astro-ph/9601009
- https://arxiv.org/abs/gr-qc/0512031
- https://doi.org/10.5281/zenodo.15367103

## 7. 자원과 복구 이력

과거 원래 탐색 증분 10.110448 CPU s는 원래10s cap을 0.110448s 초과했다. FAIL을 유지하며 reset0/relaxation0이다. 이후 개별 승인 단위를 포함한 알려진 부분 합은 이번 0.446399s를 더해 **10.765369s**다. 이 값은 전체 L0 비용이나 새 cumulative cap이 아니다. whole L0=UNKNOWN_NOT_ZERO, original cumulative cap=NOT_FROZEN, model/parent/IO/packaging/recovery/CAS 비용은 별도 미측정이며 0으로 세지 않는다.

과학 실행 전에 local cwd의 파일 소실을 실제로 관측했고 처음 A 업로드 세 곳이 No such file로 실패했다. 원인에 대한 runtime trace는 없다. 기존 전달본을 실제 materialize하고 claim-critical source/input/code/theory를 원래 tool payload 및 원본 Git blob에서 exact 복구했다. science/review 재생0. 처음 실패 A ZIP은 복구되지 않았고 NO_ACK로 남긴다. Recovery A는 새로운 packaging identity로 실제 백업했다.

| checkpoint | SHA256 | 실제 저장 |
|---|---|---|
| failed A | 5a4e3299d53fc5847d23b48454d49196955ea202a407b8472b3b1a1fbdab832f | NO_ACK, bytes NOT_RECOVERED |
| Recovery A | 6516f088179177c6b99480c950f4609603ab64e5f132c90fa46384ad1d492e01 | Drive+Dropbox+Library completed |
| Execution B | e969ee7e72397ec4c3ac8332c92421dbdf84fe8b3ac92e6e33cccffa5431fe5d | Drive+Dropbox completed |
| Private survey | bc791f117e6c270ba5b45f957874501af85b8e79298df059fcfc1c12bf4cc071 | Drive+Dropbox+Library completed, public Git 제외 |
| Final C | 아직 생성 전 | S 게시 후 고정; 미래 ACK는 외부 receipt와 D에 기록 |

현재 백업은 local ZIP CRC/member identity와 실제 provider 성공 ACK를 갖는다. 이번 A/B/private의 remote whole-file GET/SHA는 NOT_RUN이다. 원래 HI_ATOMS_IDENTITY.json은 후속 exact 복구를 마쳤지만 일부 초기 survey 서술 metadata는 NOT_RESTORED 기록을 유지한다. 현재 결과를 지지하는 원 CSV·코드·raw·독립 검토는 복구 또는 새 실행 후 보존되어 있다.

## 8. 전체 목표 DAG와 다음 단일 행동

~~~mermaid
flowchart TD
  A["고정 authority·L0 채택 근거"] --> B["기존 HI summary·pressure"]
  B --> C["stock·instantaneous work"]
  D["최신 repo·backup 조사"] --> E["실제 HI 4,368 atoms"]
  E --> F["공통 측도 이론·native 구현"]
  C --> F
  F --> G["단일 실행·독립 PASS·scoped admission"]
  G --> H["S 게시·Final C·D 인계"]
  H --> I["실제 cohort 입력 결속"]
  J["밀도·시간·IC·geometry·transport 공급"] --> I
  I --> K["결속된 조건의 cohort 계산"]
  K --> L["전체 결합 모델: OPEN"]
~~~

| 실제 입력 행 | 현재 상태 | 다음에 필요한 구체적 자료 |
|---|---|---|
| 시간 이력 | OPEN | 초기/최종 epoch, proper t와 z(t), source interpolation의 근거 |
| 밀도·정규화 | OPEN | 실제 n_HI 또는 n_HI/n_ref, H_ref와 중복 없는 단위 경로 |
| 초기 stock | OPEN | ν0,N0,U0,L0와 해당 epoch/source |
| frame·clock·geometry | PARTIAL | bath/proper convention은 고정; 실제 a_i(t),H_i(t)와 frame 대응 |
| 양의 공통 측도·각도·support | FINITE_NATIVE_MEASURE_ADMITTED | z2.479의4368 radial atoms와 선언된 isotropic closure 확보; 시간에 따른 측도는 별도 |
| transport·collision·photon | OPEN | 전체 support의 stopping/secondary heat, photon supply 및 owner 결속 |

다음 단일 행동은 **이 표의 실제 source-qualified cohort 입력을 공급자 근거와 결속하고, 해당 입력이 완성하는 가장 작은 다음 단위의 식과 실행 계약을 고정하는 것**이다. 이번 GO는 소비되었다. 이전 unused seconds를 이월하지 않으며 추가 실행의 범위·CPU/wall·종료 조건은 다음 입력에 맞춰 별도로 고정한다. 기존 사용자 승인은 유지하므로 동일 승인을 다시 묻지 않는다.

범용 fixture의 m=6/35 또는 JVP −7, B3c의 cold 초기조건, donor의 부분 에너지 창을 실제 HI cohort 입력으로 임의 채택하지 않는다. 필요한 입력이 들어오면 R1/R3 및 C1/C2의 바뀐 의존성부터 진행하고, 유지된 source·code·raw·review는 재사용한다.

