# 단일 birth-cell endpoint 국소 해

독립 판정 `PASS_SINGLE_CELL_ENDPOINT_PICARD_SCOPED`. 이전 theta=1 seed와 native rate를 재사용하고, 새 GL128 Picard 평가3회 및 동일 최종 state의 GL64 확인1회로 종료했다. 저장된25검사 PASS. 첫 endpoint를 반복 실행하지 않았다.

최종 residual norm4.8502739706286456e-17, update norm5.705075932250423e-14, energy residual3.1838449541162215e-17, energy update2.928984686962097e-14로 네1e-12 기준을 만족한다. HeIII own-relative residual1.3351185502401821e-12는 진단값이며 성분별 상대정확도 보증이 아니다.

gas_solve=1이지만 history_steps=0, history_checkpoint=false이다. 이것은 한 birth-cell만 조사하는 국소 대수해다. Full UVB/CR 또는 cosmological history로 확대하지 않는다. 다음은 같은[0,T]의2/4분할6새substeps와 시간오차/effect budget 비교다.
