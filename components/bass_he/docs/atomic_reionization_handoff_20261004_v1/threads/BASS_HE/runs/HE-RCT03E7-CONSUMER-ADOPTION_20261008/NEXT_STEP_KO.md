# E7 이후: 명시적 소비와 다음 과학 범위 선택

이번 E7은 E6 결과를 재계산하지 않고 선택형 Python 후처리 export/consume를 연결했다. 전체 데이터와22시험은DELIVERY_RECEIPT의ZIP에있다. 같은1155행또는기존5199observer행을새연구루프로반복하지않는다.

기본readout=disabled와RCT OFF는별개다. endpoint를명시하면locked history/cfg/mode만수락하고별도CSV/READY를만든다. 수신자는consume_export로정확한source/clock/값을확인한다. 원producerGamma/N/E/누적장부는바꾸지않는다. 원receiverphysics나RHS/흡수source에새Gamma를되먹임하는동작은미수행이다.

실제n/f/sigma오차와spectralquadrature remainder 및uniformcellbounds는null이다. E6의finite-refinement비를물리반경으로바꾸거나예제상대반경을원자불확실성으로채택하지않는다. code/conditional_error.py는명시적전제하에서만사용한다.

실행: python -B code/consumer_rates.py --data EXTRACTED/data --readout endpoint --mode GM --output NEW_DIRECTORY.
재현: ZIP의 python -B reproduce.py --output NEW_DIRECTORY. Python3+SymPy만필요하고native과학실행은0이다.

다음우선동작은수신자의명시적endpoint선택이다. 추가과학확장은관측량·기간·모형을정한뒤필요한검증만진행한다. sourcefree조건부수락에새원자이론을선행gate로추가하지않는다. baselineOFF/actualmomentsnull/physicalHOLD/HE-F2,F09globalOPEN을유지한다.
