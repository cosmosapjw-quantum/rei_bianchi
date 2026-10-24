# 단계별 완료·백업·게시 및 DAG

현재 스냅샷: science S 준비, **18/20**. R10·C10은 최종 C 백업·D 게시·외부 final receipt가 실제로 완료된 후 닫는다. 완료율의 분모는 이번 유한 HI_NATIVE_ATOMS_20261024 단위의20단계다. 전체 모델 완료율은 null, L4_ready=false다.

A=Recovery A(6516f0881791…), B=실행 checkpoint(e969ee7e7239…), P=private survey(bc791f117e6c…), C=미래 final archive. 단계마다 ZIP을 새로 만들지 않고, 해당 단계의 실제 증거를 포함하는 checkpoint와 공개 경로를 연결했다. 세부 ACK는 delivery 파일을 따른다.

| DAG 순서 | 단계 | 실제 산출물·완료 근거 | 현재 상태 | 백업 | 게시 위치/시점 |
|---:|---|---|---|---|---|
| 1 | R1 연구 위치·계약 | 고정 authority, owned leaf, elemental HI 조건 | COMPLETE | A | S authority/contract |
| 2 | R2 근거·재사용 | 51repo/2244heads 조사, 실제 CSV, 원전, 기존 stock/work | COMPLETE | A+P | S 공개 요약, private 원문 별도 |
| 3 | R3 주장·전제 정렬 | represented 값·isotropic/no-deposition·owner 고정 | COMPLETE | A | S theory |
| 4 | R4 가설·표현 탐색 | 원자 공통 측도와 summary 독립 모멘트의 대응 | COMPLETE | A | S theory |
| 5 | R5 구성적 유도 | P=B+K, source/JVP·charge/nuclei,4 delta identities | COMPLETE | A | S theory |
| 6 | R6 독립 검증 | 독립 source/theory pass 및 보조 CAS | COMPLETE | A+B, 최종raw검토는C | S reviews |
| 7 | R9 정식 결과·코딩 연결 | exact 구현 계약·도메인·오차·입출력 | COMPLETE | A | S authority/contract |
| 8 | C1 목표·baseline | 입력 selector4368 및 원본summary pin | COMPLETE | A | S SOURCE_BINDING |
| 9 | C2 식–데이터–코드 | atoms16 producer→CSV→새함수 대응 | COMPLETE | A | S code/contract |
| 10 | C3 수치 설계 | Fraction+단일최종round, 독립dyadic ref | COMPLETE | A | S source/check |
| 11 | C4 실행 DAG·자원 | child1,CPU2s/wall10s,retry0,root GO | COMPLETE | A | S GO/proposal |
| 12 | C5 구현 | native source/JVP/rounding decomposition와guard | COMPLETE | A | S code |
| 13 | C6 구현 검증 | 실제child exit0,13controls,13105 scalarchecks | COMPLETE | B | S raw |
| 14 | C7 과학 검증 | 정확한energy/charge/nuclei0, handcase/정규화 | COMPLETE | B | S raw/review |
| 15 | C8 수치·재현성 | 네delta0,1ulpfinite cert,반올림예산,9파일불변 | COMPLETE | B | S raw/resource |
| 16 | R7 판별 검증 | 실제4368 atom 소비와원summary결속 | COMPLETE | B | S raw |
| 17 | C9 독립 검토 | 같은독립pass의실제raw읽기,PASS_SCOPED,finding0 | COMPLETE | 최종C | S execution review |
| 18 | R8 결과 판정 | root ADMITTED_SCOPED_NATIVE_HI_COMMON_MEASURE | COMPLETE | 최종C | S ADMISSION |
| 19 | R10 종료·재개 | provenance/남은6입력/재사용/예산handoff | DELIVERY_PENDING | 최종C+외부receipt | D |
| 20 | C10 판정·인계 | actualS/C/D/전달ACK·최종readback | DELIVERY_PENDING | 최종C+외부receipt | D |

단계 번호는 스킬의 공식 이름을 유지하고 실제 의존 DAG 순서로 표를 배열했다. R9의 코딩 계약 작성은 C1 전, R8의 최종 판정은 실제 실행과 C9 후다.

공유된 실제 진행: source 조사→이론/계약→낮은 tier 구현→독립 정적 검토→A 백업→단일 실행→B 백업→독립raw PASS→root admission→S→C→D. 원래 A 업로드 실패는 별도로 남고 Recovery A가 성공했다. science/review 반복은 없었다.

## 전체 목표의 위치

기존 L0/HI-summary/pressure/stock/work의 유효 근거를 재사용하고, 이번 단위로 입력 표의 common radial measure 행을 실제 원자료 수준으로 전진시켰다. 시간·밀도·IC·실제 geometry·transport를 갖춘 cohort와 전체 Einstein/Vlasov/source 결합 모델은 후속 의존성이다. local20/20을 전체100%로 바꾸지 않는다.

C23E conditional D43K, HE94 partial window, PHYS85 역사 상태, ANGTHERM02 read-only, old2e−12 gate, old10s capFAIL은 그대로 유지한다.

