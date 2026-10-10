# BRIDGE11: 한정된 8/16/32 관측차수와 구간폭

상태: LIMITED_8_16_32_DISCRETE_ORDER_CHECK_COMPLETE__CONTINUOUS_DEFECT_NEXT.

첨부 BRIDGE10(a7920bf1...)을 직접 부모로 사용해 characteristic_rounding family의 32구간만 원 t=0부터 계산했다. 기존 8/16 증명은 저장 자료로 계승하고 재실행하지 않았다. 원격 BRIDGE10(30bb6530...)은 별도 archive로 보존한다. 원 scientific source 13개, S0/FT03, optional HH/RCT/CR OFF는 불변이다.

온도 T8=49995.4467249681182, T16=49995.4460697514863, T32=49995.4457419361579 K. 두 차이는 6.55216631937e-4와 3.27815328332e-4 K이며 유한 관측차수 pT=.99908866358다. HII p=.99907859672, 총광자 p=.99907442853. 이는 연속해 오차 인증이 아니다.

새32 root의 Krawczyk 포함과 q<1을 확인했다. 16/32 정규화 차이 상계는2.57188365716e-7, 공개폭은3.86535248254e-12다. Point ledger는 기준 안이지만 family 전체 escape/work 또는 canonical restart는 미인증이다.

Rectangle upper=abs(centre difference)+radii sum을 명목차이와 분리했다. HeIII 명목차이3.31291e-13보다 radii sum1.51312e-12가 커서 차이구간이0을 포함한다. 따라서 point p≈.9995라도 family ratio는 미판정이다.

무차원 gA(t)=1+t^2+A*prod(t-s)^2, s={1/8,1/4,3/8,1/2,5/8,3/4,7/8}, A>=0의 midpoint1/2/4 결과는 항상5/4,21/16,85/64여서 관측차수2다. 참적분은4/3+A*27446153/110552458199040로 달라진다. 안정적인 세격자 비도 추가 도함수/defect 전제 없이 참오차를 제한하지 못한다. 이 반례는 FT03 결함 판정이 아니다.

최종6명령 exit0, unit7(1 assertion RED/GREEN+6 tests-after), 32 uniform roots, 36 native pointrecords, centres 포함68 source calls, 독립70자리 root3, 정확 rectangle128. Native science process1, pilotnative0, 새IVP/Cargo/부모science/타owner재실행0. Conditional inherited Interval/Jet arithmetic; proof assistant나 두 번째 전체 interval RHS 검증 없음.

다음은64격자 반복이 아닌 BRIDGE12_SINGLE_CELL_CONTINUOUS_DEFECT다. 실제 첫cell[0,46757316.98818144]s의 root/point/after를 ZIP의 NEXT_CELL_INPUT.json에 묶었다. Native BE 광자제거식을 연속RHS로 사용하지 않는다.

전체 보고서·원source·실행binary/stdout·독립검사·실패로그는 REI_XTHREAD_BRIDGE11_20261008.zip에 있다. 1570087 bytes,99 entries,98 payloads, SHA2569eecd131dcc6c8a88d8c06cee24f01845f4175df048fb699f6c6240aafd6a6f9. 재현 python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc. 이 Git 폴더의 helper 단독이 전체 실행 패키지는 아니다.

local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD 보존. 다른owner 결과는scope수신만이며 jointON이나 상대owner 채택은 주장하지 않는다.
