# R10L 실행 보고서

**Physical verdict: PHYSICAL_SUPPORT_UNRESOLVED.** C numerical gate는 PASS이며 물리적 support 선택/production promotion은 성립하지 않는다.

## Fresh identity와 순서

- PR15 HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`, tree `f5777ecf0b648cd5b4124bc170e9b5a5f3b38db8`.
- PR17 execution basis HEAD `7a85acda7fdeb29439791b58ecf271ca66914a43`, tree `6690f7f1946244c9d6bdb557954da7115fd2357d`; R10K basis `4e7627b30f835dab81c487e7e8571dba51553dde`는 ancestor다.
- Source → digitization/uncertainty manifest → A/B/C contract → exact query contract → C 계산 → raw comparison 순서를 유지했다. 최종 publication identity는 Git receipt/final return에서 별도로 기록한다.
- 첫 S1 회수 실패의 historical review와 실행 전 adapter 오류 두 건을 보존했다. 원문 도착 후 stage1/2를 다시 검증했다.

## External source와 uncertainty

- S1: [Stolterfoht PRA81 052704](https://doi.org/10.1103/PhysRevA.81.052704). Dropbox original `id:BSpOijBcT10AAAAAADwi-g`, 693837bytes, SHA256 `e544c755ef76841fa161bb16f64073bd9e698c0bdebd009ffccf5e9728f45ffb`; Dropbox content hash도 확인했다. Fig8 PDFp8, atomic H(1s), END solid curves만 선택했다. 에너지 축은 reduced laboratory eV/amu이며 Minami open symbols와 구분한다.
- Private high-resolution crop, 두 독립 좌표 추출, horizontal/vertical/calibration perturbation을 보존했다. Central은 모델 결과를 보지 않은 추출자의 값, interval은 두 좌표 추출 envelope의 union이다. Parent의 prior A/B visibility는 공개했다. 이 interval은 graphical extraction allowance이며 physical confidence interval은 아니다.
- S2: [Liu PRA67 052705](https://doi.org/10.1103/PhysRevA.67.052705). Author-linked PDF 143939bytes, SHA256 `d111275b1225e8d128f80c1188daf9b7eef9bddf8dad350db44a25c989dba81b`. TableII HSCC Ecm4keV n2=16.2×10⁻¹⁶cm²; Ecm0.4keV는 Fig3≈0.83×10⁻¹⁶cm², extraction interval≈[0.76,0.92]×10⁻¹⁶cm²다. Ecm=.8 EkeV/u는 inherited He4/H1 mass approximation이며 명시적으로 번호가 붙은 He isotope는 원문에서 확정하지 못했다. Four-channel convergence/source-model error는 수치 bound가 없다.
- S3: [Minami JPB41 135201](https://doi.org/10.1088/0953-4075/41/13/135201), fulltext/table MISSING_FULLTEXT. Publisher validation HTML/OSTI404 및 bibliographic discrepancy를 기록했다. 5keV/u 값을 추측하지 않았고 0.5keV/u 외삽도 하지 않았다.
- 출처별 값은 분리했다. S1/S2 5keV/u n2 interval이 겹치지 않으므로 평균값/가중 RMS로 이 차이를 숨기지 않는다. S1/S2는 독립 계산 benchmark이며 실험 오차 막대로 표현하지 않는다.

## Locked models와 bounded execution

- A: R10K REAL+frozenDelta0+factor2+Coulomb/author cutoff. 기존 결과/hash를 재사용한 `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION` control이다.
- B: Nmax3, 기존5 branches, dynamic Delta(rho), factor2, EXTENDED, straight/CPC rotation64. 기존 R10G SL_CPC 결과를 exact content identity로 재사용했다.
- C: B의 support만 REAL이다. Radius는 unchanged ScopedBranch.R.real을 사용하며 refined endpoint.R.real로 바꾸지 않는다. Exponent/trajectory/cutoff/tolerance/state/sink/default를 바꾸지 않았다.
- Tail은 기존 u=rho² GK15/GK7 함수를 직접 호출하고 REAL boundary를 추가한 union split을 사용한다. 첫 구간만 q=asinh(rho/a_ref), 기존 R10G function/scale/한도를 사용했다. Global refinement=0, endpoint local split1회/3leaves, 60rho; tolerance rtol2e-4/atol1e-10 유지.
- Tail285rho + endpoint60rho =345 consumedrho, 그중150 distinct newrho.540 신규 Delta(240tail+300endpoint),540 기존R10F exact-pair reuse. R10G endpoint cache300records는 hash 검증 후 보존했지만 이번 REAL 좌표에서 실제 hit는0개다. 신규 상한1290회 안에서 종료했고 oldEXTENDED domain 밖 solve는0회다.
- Exact cache는 canonicalJSON SHA256으로 key를 구성하고 source/environment/endpoint bytes/branch/rhohex/depth96/panels32/query-contract를 포함한다. Key와 stored payload hash, record branch/rho 동일성을 검증했다. 임의 rounded key를 사용하지 않는다.
- Firstpilot1.206s, 신규 Delta 평균1.321s, wall717.527s. Rotation64vs128 최대probability difference1.253e-9, unitarity4.197e-14, stochasticity3.442e-14.18개 component gate와 successive-grid criterion 모두PASS. 이는 empirical local estimate이며 rigorous global continuum bound가 아니다.

## 출처별 raw 비교

모든 값은 cm², ratio는 model/benchmark다. 전체 좌표/interval/ratio range/natural log와 수치 error estimate는 RAW_COMPARISON.json 및 CSV에 있다. 원본 raw 표를 고정한 뒤 aggregate는 계산하지 않았다.

|Source|E keV/u|n|Benchmark|A ratio|B ratio|C ratio|C/B−1|
|---|---:|---:|---:|---:|---:|---:|---:|
|S1|0.5|1|4.360e-22|0.0009639|0.0002164|0.0002128|-1.70%|
|S1|0.5|2|7.295e-17|1.311|0.7145|0.6705|-6.15%|
|S1|0.5|3|3.821e-18|0.8597|0.6891|0.6867|-0.34%|
|S1|5|1|2.213e-19|1.33|1.023|0.758|-25.87%|
|S1|5|2|8.390e-16|1.562|1.936|1.202|-37.91%|
|S1|5|3|1.639e-16|0.4701|0.4167|0.386|-7.37%|
|S2|5|2|1.620e-15|0.8092|1.003|0.6226|-37.91%|
|S2|0.5|2|8.289e-17|1.154|0.6288|0.5901|-6.15%|

REAL로 바꾸면 5keV/u n2는37.9% 감소하며 S1에는 가까워지지만 S2와는 멀어진다.0.5keV/u n1의 약4자리 mismatch와 n3의 두 energy mismatch는 양쪽 support에 남는다. 따라서 모든 benchmark를 일관되게 설명하는 support 선택은 미확정이다. 이 좁은 observed mismatch persistence를 universal theorem 또는 전체 discrepancy의 가중 dominance로 일반화하지 않는다.

## Verification / 보존 / 전달

- 최종 focused11/11PASS. 초기9/9후 추가한 affected checks에서 두 genuineRED(1failed/9passed,1failed/10passed)를 관측하고 수정했다. 실행 전 오류이며 Delta0회였다.
- 저장 integrand 재합산 최대차2.22e-16, cache540개 integrity/domain PASS; 재검증에 새 contour/rotation integration0회. 독립 source/adapter/final review는 별도 JSON을 참조한다.
- Production source/scripts/tests/default/tolerance는 변경하지 않았다. R10A/G 및 R10D/E/F historical verdict와 R10I fullWRN non-equivalence/current-m0 equivalence는 보존한다.
- Eq55 production, Eq50/54 변경, CODE-I02 재감사,56-action,worker,R1/R2,authorFORTRAN,C_S_AT/MODKG,Nmax확장,continuum,L2/Krawczyk,새interpolant/지원radiusfitting은 실행하지 않았다.
- Source PDFs/fulltext/figures는 private로 남기고 public package에서 제외한다. Provider backup은 public R10L artifact packet과 별도 source-evidence crop/geometry packet으로 구분한다. Source-evidence image/geometry bytes는 GitHub에 게시하지 않으며 fullPDF/fulltext는 두 packet 모두 제외한다. Historical archives 전체 복원을 주장하지 않는다. Provider ACK/size/checksum, byte/manifest restore verification, 실행 restore NOT_RUN을 BACKUP_RECEIPT.json에 구분한다.
- 후속 독립 검토 prompt는 NEXT_BOUNDED_PROMPT_KO.md. Physical uncertainty/source discrepancy를 해결할 새 연구 계약이 필요하며 현재 support나 exponent default를 retune할 권한은 없다.

Frozen: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
