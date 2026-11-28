# RCT03E5: 동일 parent의 cutoff-aware rate 전체 시각

REPORT_KO.md/PLAN.json/SNAPSHOT_CONTRACT.json과evidence/analysis01/RESULTS.json을ZIP에서읽는다. 기존77snapshot이나rate구현을다시설계하지않는다. 원격E3와첨부E3의다른a_Gamma/실행범위를합치지않는다.

다음은같은N384가스경로에서현재source/cutoff를분할한reader의385시각적용과원rate계약비교다. 이번33표본최대.477651을전체시각상한으로취급하지않는다. 동일parent의grid효과와differentpath효과를분리하고2.5e-23원격계약을1e-22첨부계약으로은밀히바꾸지않는다.

일반적spectralinterpolation이나미지의positive density를만들지않고기존characteristic replay의명시적parent를사용한다. 메모리4096site/시간격자/cutoff-sourceownership과원자로직은보존한다. extraN768,Gauss8,새provider,새rootproof가선행조건은아니다. fullcoupled물리승인과producergrid교체는미수행이다.

기본재현은python -B reproduce.py --output /absolute/NEW로analysis-only다. --native를명시하면새8시험과77radiation snapshot을재생한다. compiler/executable은ZIP에없으며Rust1.94.1과Python/SymPy가필요하다. GPGauthenticity미확인제한을보존한다. 실제게시/백업은DELIVERY_RECEIPT가소유한다.
