# 조건부 17상태 scientific figure set

2026-10-29 KST. 사용자가 이번 목표를 저장된 OFF_base·ON_base·ON_refined의 종별 진화, ON/OFF 효과, refinement·초기 transient·보존 진단으로 고정했다. 이론 및 코딩은 지정된 physmath-research-loop 내장1.0.0으로 진행한다. 기준 PR251 HEAD c5ab42c8673db614e7fb16695ad071c65becb81b를 유지하며 새 IVP는 실행하지 않는다. ON_refined가 기본이다.

병렬 의무: 최신 Git/backup/Library/conversation delta 취합; 실제 saved clock의 Myr–mean-z 대응; n/T 생성–손실·희귀 Li 오차조건·bath knot의 물리/수치 진단; 기존23좌표 원자료의 유한 offline 계산; 논문형 all17 단일축과 유사 abundance별 그룹·비교·진단 figure set. 작성자와 다른 검토자가 한 번 검토한다. 사용자 조언의 scalar atol·정확한 수명에서 완전평형·knot원인·smoothness 보장 주장은 코드와 원자료로 판별한다.

원본 clock와 완료 IVP를 재계산하지 않고 저장 t/eta를 사용한다. t는 source-onset 이후 proper elapsed time이며 Myr=31557600000000 s, z_mean=21 exp(-eta)-1이다. 초기 transient는 z≈20으로 겹치는 실제 표시정밀도를 명시한다. 같은 figure set의 ON−OFF는 source와 escape switch를 합친 효과로 표시한다. 조건부 그림과 Bianchi anisotropy의 통제된 새 민감도 계산을 구별한다.

전체working33/88·central28/88·physicalfast4/7 유지. 최신 original88 DAG에서 실제 완료조건이 닫히지 않으면 분자를 늘리지 않는다. 세부 theory contracts를 구현 입력으로 사용하고 의미 있는 새로운 metric만 한정 실행한다. 이전에 전달되지 않았던13첨부는 사용자가 폐기했으므로 재업로드나 재사용을 요구하지 않는다.

main 신규진단은 기존원policy600에 대한 임시620 아래 child4CPU/30wall/1GiB/1worker, totalreserve5, 한 번. presentation은 explicit65에서 기존63.924256494를 유지하고 이번 vector+preview한정job reserve1.05 (process0.85+tail0.20)를 예약한다. 렌더링을 main으로 옮기지 않는다. 기존비용과UNKNOWN_NOT_ZERO를 유지하고 완료후 원policy600/30/10복귀. 정확한 releasecommand는 root가 정적확인 후 제공한다.
