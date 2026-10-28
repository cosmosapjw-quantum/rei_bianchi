# 재개·전달 메모

저장된17상태 OFF_base·ON_base·ON_refined의361개 공통 표본을 사용했다. 기본case ON_refined와 실제 초기bath300 K를 유지하며 새IVP·새물리표본은0이다. 기존 진단·수치·물리 해석의 PASS_SCOPED를 재사용했다.

기준PR251: c5ab42c8673db614e7fb16695ad071c65becb81b
원래 실행전checkpoint: 81721528c4a40b90aa38fd65a29f032dcf9c5f41
복원·추가시각검토기준HEAD: 99dd121296112e93494e635a0a2469215556917d
작업branch: research/rei-figure-set-20261029

개별PDF/SVG/PNG 각10개와 figures/scientific_figure_set.pdf를 사용한다. 통합PDF blob2c25f06ba1d26f98e730eb02f8a56be15cbfe002는 기존HEAD와 같고 이번 완료에서는 PDF/SVG·과학배열을 변경하지 않았다. 이전 repair는 FAILED_PARTIAL_RASTER로3/10페이지에서 끝났지만, 사용자 명시승인65→66 CPU s 아래 나머지4–10페이지의 raster화1회를 exit0으로 완료했다. 관측 SELF+CHILDREN CPU는0.317124 s다. 최종 독립검토는 전체10/10페이지 시각QA를 PASS_SCOPED로 닫았다. 근거는 review/VISUAL_COMPLETION_REVIEW.json 및 .md, outputs/VISUAL_COMPLETION_RESULT.json이다. 이전 부분완료상태는 Git이력과 현재budget기록에 보존했다.

REPORT_KO.md, FIGURE_CAPTIONS.md, theory/PHYSICAL_FINDINGS_KO.md, outputs/DIAGNOSTICS.json을 함께 읽는다. raw_saved_arrays.csv, signed_differences.csv와 plot_data.json이 실제값·부호·표시에서 제외된 표본을 보존한다. elapsed proper Myr와 저장clock의 mean redshift를 사용하며 절대우주나이를 추가하지 않았다. ON/OFF는 source와 escape를 함께 바꾸고 refinement는 동결scale 기준이다. 초기transient 그림은 n·T I·T II를 보여준다. 그룹창에서 제외된 초기He/Li 양수표본은 원시표와 plot_data.json에 남아 있다.

working33/88, central28/88, physical fast4/7을 유지하며 원본노드를 더하지 않았다. 다음 통제 비교에서는 초기·경계 복사·열 조건, 미시적 반응 법칙, 평균팽창 이력과 수치 기준을 공통으로 고정하고 초기 전단만 바꾸되, 명시된 기하–복사·열 결합에 의해 진화하는 방향별 스펙트럼과 그로부터 계산되는 반응률은 달라질 수 있도록 한다. 폐기된 첨부13개는 재개의존성이 아니다.

BUDGET_CLOSEOUT.json에 main608.750604, presentation65.980312494, planning20.819461885 CPU s의 알려진 누적비용·보수적reserve를 보존했다. 새presentation1.0 s 예약 전체를 유지했다. 원래정책상한600/30/10으로 복원했으며 소비된66 승인은 만료되었다. 새실행allowance·retry·원장이전·reset은 없다. 복원·host/tool/transport 비용은 UNKNOWN_NOT_ZERO다.

R9/C9의 최종시각 의무가 닫혔다. 그림의 가독성과 저장된 조건부모형 주장 범위에서 전달준비가 완료되었고 기존과학주장은 변경하지 않았다. 현재 게시진행은 별도 DELIVERY_RECEIPT.json을 따른다. 이전pre-delivery ZIP 및99dd121의영수증은 과거백업이력이다. 새 scientific_figure_set_completed_20261029.zip이 이번완성본이며 현재PR259와 두provider의새ACK를 최종영수증에 기록한다.

Draft PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/259
