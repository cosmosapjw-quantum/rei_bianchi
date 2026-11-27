# 다음: THEORY09B2_CONTINUOUS_CURVE_AND_NUCLEAR_SOURCE_ERROR

Read REPORT_KO.md, SOURCE_BINDING_CONTRACT.json, data/BOUND_ELECTRONIC_NODES.json, evidence/run01/RESULTS.json.
57개 1s_sigma/2p_sigma node와56개 원 cross-R link는 이미 같은 hierarchy에서 회수됐다. 같은 값의 원문탐색이나 재고유값계산을 기본선행조건으로 반복하지 않는다. 전체 raw state와 원본 해시는 inputs/에 있다.

다음은 node를 continuous source로 바꾸는 국소 문제다. 두 threshold-consistent potential와 signed dipole의 지정R구간,중간점/보간오차,inner/outertail를 결속한 뒤 실제 입사 partial wave u_i 하나로 q=d u_i를 평가한다. energy/phase/origin 조건은 본 계약을 따른다. Q_BO=1.5Eh와 원소비기40.819325400298eV를묵시적으로섞지 않는다. 다른Q는상대표면보정이라는별도선택이다.

출사09A의Coulomb Robin/flux경로를재사용하고새genericcontinuumsolver나고정broadening을대체로만들지않는다. 기존sampled d가모두한부호라는사실만으로between-nodezero나tail을인증하지않는다. 실제 q/physicalmoment 아직없다.

재현: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B -W error research/verify_binding.py --output /absolute/new/output.
이론verifier는첨부선택rawinput만으로실행하며원12MBprivatearchive가필요없다. recover_nodes.py는선택input의archiveprovenance를다시구성할때만사용하며원archive를별도로요구한다. 이미검증된자료를단순수신때문에재복원하지않는다.

소비기정적addon의owner채택과무관한이론lane이다. root/dispatcher/threshold/sourcepolicy를수정하지않고physicalHOLD,baselineOFF,sourcephoton/heat/recoilnull을유지한다.
