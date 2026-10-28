# 재개·전달 메모

저장된 17상태 OFF_base·ON_base·ON_refined의 361개 공통 표본에서 진단과 그림을 만들었다. 기본 case는 ON_refined이고 실제 초기 bath는 300 K다. 8 K 후보는 적용하지 않았다. 새 IVP와 새 물리 표본은 각각 0이다.

기준 PR251: c5ab42c8673db614e7fb16695ad071c65becb81b
작업 branch: research/rei-figure-set-20261029
실행 전 checkpoint: 81721528c4a40b90aa38fd65a29f032dcf9c5f41
원자료: research/rei_source_history_20261028/outputs/pilot17_populations.csv 및 OFF_base.npz·ON_base.npz·ON_refined.npz
정확한 표 크기·SHA256: STATE.json의 data_identity

수정된 개별 PDF/SVG 각10개와 figures/scientific_figure_set.pdf를 사용한다. 수정 PNG는 preview-01.png–preview-03.png와 그 세 named alias뿐이다. 첫 시도의 옛 PNG는 outputs/stale_named_previews에 보존했고 최종 그림으로 사용하지 않는다. repair는 FAILED_PARTIAL_RASTER로 종료했다. 최종 권위 판정은 review/REVIEW.json 및 review/INDEPENDENT_REVIEW.md이며 저장 이력 과학·수정 벡터 전달은 PASS_SCOPED, 최종 시각 QA는 3/10페이지 확인으로 PARTIAL이다. 4–10페이지의 추가 raster 검사는 새 승인 없이 실행하지 않는다.

REPORT_KO.md, FIGURE_CAPTIONS.md, theory/PHYSICAL_FINDINGS_KO.md, outputs/DIAGNOSTICS.json을 함께 읽는다. raw_saved_arrays.csv, signed_differences.csv와 plot_data.json이 실제 값·부호·표시에서 제외된 표본을 보존한다. elapsed proper Myr와 저장 clock의 mean redshift를 사용하며 절대 우주 나이를 추가하지 않았다. ON/OFF는 source와 escape를 함께 바꾸고 refinement는 동결 scale 기준이다.

working33/88, central28/88, physical fast4/7을 유지하며 원본 노드를 더하지 않았다. 다음 물리 비교에는 같은 초기조건·평균팽창·bath·rate·source/escape·시간범위·오차기준에서 초기 shear만 바꾸는 계약과 일관된 radiation/thermal 연결이 필요하다. 폐기된 첨부13개는 재개 의존성이 아니다.

예산 근거: AGENTS.md 및 research/rei_figure_set_20261029/BUDGET_AUTHORIZATION.json. BUDGET_CLOSEOUT.json에 main608.750604, presentation64.980312494, planning20.819461885 CPU s의 알려진 누적비용·보수적 reserve를 보존했다. 원래 정책 상한600/30/10으로 복원했으며 새 실행 allowance, retry, 원장 이전은 없다. 알 수 없는 host/tool/transport 비용은 UNKNOWN_NOT_ZERO다.

R1–R8/C1–C8의 관측 근거를 재사용하고 R9/C9는 PASS_SCOPED 및 visual partial로 닫았다. R10/C10은 최종 Git draft PR 및 Drive·Dropbox provider acknowledgement가 들어오면 전달 범위에서 닫는다. 현재 전달 영수증은 대기 상태다. 코드를 보존했지만 이 메모는 재실행 명령을 승인하지 않는다.

초기 transient 그림은 n·T I·T II만 보여주며, 그룹 그림에서 범위 밖인 초기 He/Li 양수 표본 모두를 회복하지 않는다. 해당 값은 원시 CSV와 plot_data.json에 남아 있다.
