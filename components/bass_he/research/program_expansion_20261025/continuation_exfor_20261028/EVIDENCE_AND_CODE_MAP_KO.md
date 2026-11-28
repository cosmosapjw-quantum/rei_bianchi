# R2/C2 — 원전과 식–코드 대응

공식 EXFOR M0475002의12행은 원문SHA256 및 subentry/schema/literal values로 결속한다. M0475003의6행은 다른에너지표로 보존한다. 원 정규화 factor는 현재미해결이며 이번 acceptance ratio는 같은각도에공통인양의scale만 소거한다.

Rice1998의Eq5.4와p115를 실제 스캔으로 읽었다. 동일입자2π적분은 Rice의직접정의이며 Arends의zero-endpointfit은후속연구자의기록이다. 이를측정되지않은양끝의제약유무를비교할근거로쓴다. 실제polarizationlaw와liquidtargetprojection은별도입력이다.

|식/입력|코드책임|근거|
|---|---|---|
|literal DCS/error/table identity|parse_source,sensitivity|sources/M0475.x4,officialIAEAhash|
|짝Bernsteinψ 및d|EvenBasis.value/integrate|정확basis대칭과적분|
|cosθ구간,행 l/u|EvenBasis.row|상속sincos_turn+outward2^-60|
|Pinner/Pouter|constraints|nonnegativecoefficients에서성분별부등식|
|boundedpolytopevertices|inverse,enumerate_energies|allactivebasis와exactfeasibility|
|같은사건기하|geometries,geometry_coefficients|상속P10의stripSetBounds|
|acceptance범위|ratio_extrema|양의분모linear-fractionalvertex극값|
|원자료보존/검증|validate_once,run_bounded|새sourcepin+onecampaign|

새각도구간평가와polytope분석은EXFOR11의새계산이다. HARMONIC10의완료시험을실행하지않는다. 미래결과·PASS는예측해기록하지않는다.

