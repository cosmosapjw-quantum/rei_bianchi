# BASS_HE PR120 | 실제 EXFOR 각도대비·형상 판별 실험 데이터 보고

원본 IAEA EXFOR M0475.x4의 DA 12행을 byte-exact SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`로 고정하고, Eγ=213/258/330 MeV × CM 46/61/73/87°에서 새로운 정규화-불변 물리 지표를 생성했다. 기존 PR119의 168개 모델 조건부 Fermi 응답을 반복하지 않고 원본 실측 DA 자체만 사용했다.

**생성 데이터:** 18개 같은 에너지 내 각도 대비 + 12개 같은 각도 내 에너지 대비 = 30개 정확 유리수 source-based 관측 파생량, 원본 ERR-S 직교 box의 정확 상·하한, 원본 두 점의 공분산 미지 delta-method 오차 범위. 관측점 각각의 편광/acceptance 원본 입력은 미확정이며 30개는 서로 독립 측정이 아니다. 추가로 213/258/330의 상수·sin²·even quartic 세 형상 9개 조건부 WLS 적합 χ²/dof/p값 및 각도별 예측값을 계산했다.

**실측 기반 핵심 결과:** (σ87−σ46)/(σ87+σ46)은 213 MeV에서 8/19, 258 MeV에서 17/33, 330 MeV에서 5/33이며 source ERR-S box들은 각각 [9/35,23/41], [7/29,27/37], [-3/31,13/35]다. 상수 형상 χ²은 11.5223,7.4109,3.12 (dof3), sin² 형상 χ²는 0.87615,2.16435,6.25467 (dof3)이다. 330 MeV의 sin² p~0.10이므로 유의한 반증은 아니다. 관측되지 않은 후방각·전체적분 단면적을 만들어 주장하지 않았다.

**검증:** Python targeted unittest 15/15 PASS, compileall PASS, 재생성된 JSON/CSV가 byte-identical, Wolfram 독립 WLS χ²와 원본 정확 유리수 대비/box 재현. Native independent subagent R6/C9 NOT_RUN; local python+Wolfram은 별개 계산기법일 뿐 별도 저자가 아니다. Git source byte readback·각 stage SHA·Drive/Dropbox 실제 ACK는 DELIVERY_RECEIPT에 구분.

**DAG:** Central28/88, HE physical14/18, parent PR119 angular2/3, 기존 Fermi ABC3/4, resolved mask2/3 모두 변경 없음. 신규 원자료 shape micro-unit 2/2 scoped (D1 측정대비, D2 조건부 형상검산), *canonical physical delta=0*. 물리 gate `kappa=null,R_event=null,heat_rate=null,physical_activation=false,L4=false,production=HOLD`.
