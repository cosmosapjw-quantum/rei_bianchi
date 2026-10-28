# REI 최신 관측 입력 감사
관측한 PR246/248/249/251은 모두 열린 stacked draft이며 merge하지 않았다. PR251 최종 HEAD는 c5ab42c8673db614e7fb16695ad071c65becb81b이다. 실제 PR metadata, 전체 변경55경로 patch, AGENTS 및 핵심 입력5파일을 읽었다. PR251의 독립 심사는 이미 PASS_SCOPED_CONDITIONAL_UVB_ADAPTER_AND_FIGURE이다. 과거 개인문맥의 review pending은 현재 권위가 아니다.

PR246 ea805aefa8b73a33414e688ead8e5aca3f4296fa는 저장201epoch source-history/QSS certificate이고, PR248 022f2ed85595364f05834d8eb1573434efce92d0는 승인된17state 3case IVP가 완료됐다. PR249 c23836847261851757caef50913be1c08379d4f0는 IC/Bianchi analytic response 완료다. PR251은 실제 BB13 전체7x7 covariance 및 Puchwein2019 template 진폭, EOS box, 관측-only covariance interpolation, Lumina adapter, ON_refined 기본과 저장17state그림을 완료했다.

새 단위는 재적합/새 template/새 rate가 아니라 저장된 관측 residual의 normalization-free shape contrast와 correlated leave-one-out innovation이다. 기존 implementation/calibration.py와 outputs/CALIBRATION_RESULT.json에는 이 삭제-영향 진단 및 contrast covariance 산출물이 없다. 기존 chi² 하나를 다시 계산하여 새 성과로 세지 않는다. 새 redshift별 영향표와 정확한 삭제분해가 유용한 산출물이다.

기존 값 beta=-.04742695606588649dex, A=.8965469633906246, chi²=19.381736839571925/6; EOS profile theta=+1, chi²=15.721474783438493은 재사용한다. EOS profile이나 Jeans systematics를 새 fit에 넣지 않는다. 통계-only shape tension은 full physical source 부적격 판정이 아니다.

owner의 향후 coupled/관측 연구, z20 bath/spectral yield/escape/transport 및 hardphoton/CR/nT/stopping, substantial-shear directional mapping은 그대로 owner에게 남는다. 다른 PR247 DR/250 RR-Mao 예약과 결과를 이 단위로 옮기지 않는다. 기본 ON_refined와 이전 NPZ/그림/원자료는 변경하지 않는다. physicalfast4/7, working33/88, central28/88 유지; F4 PARTIAL.
