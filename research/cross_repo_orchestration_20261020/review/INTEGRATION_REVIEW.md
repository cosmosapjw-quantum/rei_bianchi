# 통합 보고서 과학 범위 독립 검토

판정: **PASS_SCOPED_SCIENTIFIC_SYNTHESIS**. 현재 `REPORT_KO.md`의 과학 주장과 국소 검증 범위에서 수정해야 할 사실 오류를 발견하지 않았다. 검토한 보고서 SHA256은 `d6121638a76d03a35ceaaef6e762c273ecd07bbe4e83145d4171938213222209`다. 보고서를 직접 수정하지 않았고 새 시험·물리 계산·외부 게시를 실행하지 않았다.

- Markov 결과는 처방된 bath의 finite charge block에 제한되어 있다. 질량 오차와 원천항, 선언된 상관오차, 표본과 연속 상계의 구분이 유지된다. 부동소수점 커널을 outward-rounded enclosure나 nonlinear RUN19 궤적 인증으로 확대하지 않는다.
- HH는 D3(21,20),m=0의 한 DtN 계수 완료와 고차 remainder 미완료를 정확히 분리한다. 단면적·열평균률은 미생성이고 HH_R10은 OFF다. 조건부 resolvent remainder는 실제 무한모드 norm 계산으로 제시되지 않는다.
- RUN13 M2 standard/tight 완료 및 source 복원, Unit5 terminal 회수와 원 deadline은 최신 상태대로 반영됐다. 만료 allocation 재시작이나 불필요한 M2 재계산 지시가 없다.
- REC는 교정된 smoke_003의2acceptedsteps/8FULL eval만 채택한다. 이전 smoke와 CI를 새 과학 결과로 합산하지 않으며 첫event·전체h4·U5·h/h2/h4수렴은 HOLD다.
- BASS adapter는 단위·공통Q 회계 검증이고 실제 donor closure나 coupled history가 아니다. REI의 cumulative reference-comoving energy를 proper-event deltaU로 바꾸지 않는다고 명시했다.
- HE14개 고유 검사는 실행 제어기 검증이며 native0회다. CR의595+1674파일 복원과 이전32ODE/2FD 제조계는 새 native chemistry 실행과 구분된다.
- 백업 증거 수준은 REI의 freshmetadata, REC의 metadataZIP 실제검산, CR의 archivebytes복원, 미완료Drive상태를 구별한다. 전 raw 재다운로드를 했다고 주장하지 않는다.

HE29의 원 DESIGN과 새 controller는 per-case cap을 제공한다. 보고서의 '기존 전체deadline'은 별도로 존재하는 supervisor allocation에만 해당하며 controller가 aggregate clock을 구현했다는 의미가 아니다. 현재 lane review와 handoff가 이 구분을 담고 있어 별도 코드 수정은 필요하지 않다.

이 검토는 root가 진행하는 최종 게시·새 백업 ACK의 완료 여부를 승인하지 않는다. 읽은 시점에는 `CONTENT_PUBLICATIONS.json`과 최종 `BACKUP_DELIVERY.json`이 아직 없었다. 최종 전달 전 §5 및 링크·상태를 실제 remote commit/head와 provider ACK/size/readback영수증에 맞추는 것은 별도 배송 단계다. 그 절차를 과학 검토의 새 blocker나 추가 물리 gate로 확대할 필요는 없다.

세부 source 목록과 항목별 판정은 `INTEGRATION_REVIEW.json`에 기록했다. 이 검토의 PASS는 통합 서술의 범위 정확성에 한정되며 전체 재이온화 프로젝트 완성을 뜻하지 않는다.

