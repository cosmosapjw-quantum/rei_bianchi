# Abundance 목표 문서 최종 독립 검토

판정: **PASS_WITH_SCOPED_REPAIRS**. 지정된 6개 수정은 모두 확인됐고 미해결 material finding은 없다. 사용자 목표인 **non-tilted axisymmetric Bianchi I의 재이온화 abundance history와 proper time·T_gas에 따른 BBN 형식 species 그림**을 위한 문서·machine contract는 공개 전달할 수 있다. **과학 admission은 NOT_ISSUED, 실제 목표는 IN_PROGRESS**다.

검토 범위는 새 goal 폴더, CURRENT_PLAN 포인터, 이전 인계 문서의 successor 안내 및 SOURCE_MANIFEST의 두 metadata 정정이다. 한 번의 통합 read-only 검토와 한 번의 지정 수정 확인으로 닫았다. 기존 source/result 감사는 재사용했고 solver·기존 과학 검산·build/test를 반복하지 않았다. 검토자는 구현/문서를 수정하지 않았다. 요청 model은 gpt-6-astra이며 관측 runtime identity는 null이다.

| 지정 수정 | 최종 확인 |
|---|---|
| local/publish branch 구분 | 로컬 작업 branch와 원격 codex/rux-science-delivery-20261014 및 PR117을 별도 기록 |
| 캠페인 case 수 | zero 및 ±full/±half의 5 primary histories, 별도 SAME_H diagnostic; AX07 zero 근거 재사용 |
| photon moment 정규화 | spectral J_l의 solid-angle integral과 energy-per-H U_l을 명시적으로 대응; angular mean·중복 weight 제거 |
| paired 좌표 | ZBAR 또는 PROPER_TIME 하나를 선택하고 candidate/reference의 시간과 zbar를 각각 보존 |
| 준비·과학 실행 예산 | 현재 solver 0은 PREPARATION_ONLY; 실제 실행은 AX05/해당 stage가 별도 유한 allocation을 결합 |
| science/release 완료 순서 | AX15가 C01–C16 판정, C17은 PENDING_RELEASE; AX16 publication/readback 후 C17 및 GOAL_DONE 판정 |

17개 DAG node와 전체 packet 객체가 일치하고 state-aware 초기 ready는 **AX01/AX02/AX03/AX13**이다. 완료된 AX00은 문서·기존 결과 감사뿐이며 새 과학 기준은 모두 NOT_RUN, 이번 solver run은 0이다.

필수 H I/H II/He I/He II/He III/electron을 모두 출력한다. 원소별 x와 baryon-normalized Y의 분모, H/He-only n_b=n_H+4n_He, omitted reservoir 및 electron의 xe/ye 구분이 일관된다. 전자는 baryon 합에서 제외한다. 실제 진화하지 않은 D/T/He3/Li 또는 과거 17-state registry를 새 full-network 결과로 표시하지 않는다. q의 reference-epoch 정의와 instantaneous Σ=s/H를 구분한다.

abundance_vs_time·abundance_vs_Tgas와 FLRW/BI 비교·Δabundance/resolution 그림이 필수다. T_gas의 재가열·비단조성은 시간순 parametric branch로 보존하며 T 정렬로 가짜 이력을 만들지 않는다. AX09/10 τ receiver는 OPTIONAL_OFF이고 AX14는 이들에 의존하지 않는다. observer-tail 미확정이 primary abundance 결과를 막지 않는다. 기존 scope·null·실패를 보존하면서 자동 bounded continuation을 수행하는 계약이며, 새 사용자 continue 승인을 반복 요구하는 전이는 없다.

기존 보고서 metadata 정정은 15 source endpoint에서 유도한 7 pair의 구분과 실제 report.log.gz/gzip 경로에 한정한다. 기존 cargo fmt CI 실패와 Rust test skip은 상속된 공개 제한으로 남는다. **이번 검토는 green CI, 물리 이력 완료, 새로운 수치 정확도 또는 scientific PASS를 주장하지 않는다.** 실제 provider/scenario/driver 통합, 계산·수렴·robustness·최종 그림은 후속 실행 작업이다.

추가 검토층을 열지 않고 승인된 문서 publication과 초기 ready 작업으로 진행할 수 있다. push 성공 여부는 coordinator의 실제 remote SHA readback으로 확인한다. 검토 파일 identity는 FINAL_GOAL_REVIEW.json에 기록했다.
