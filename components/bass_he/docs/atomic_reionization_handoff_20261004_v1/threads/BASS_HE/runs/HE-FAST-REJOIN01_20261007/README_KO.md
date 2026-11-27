# HE-FAST-REJOIN01: 현재 저온 IGM과 RCT의 조건부 점별 연결

CURRENT_IGM_RCT_POINT_NATIVE_PASS__PAIRED_HISTORY_OPEN. 사용자 요청에 따라 fastest-track 우선으로 복귀했다. 원자곡선 완결은 baseline의 선행조건으로 만들지 않는다. 실제 current IGM point evaluator + 기존 RCT source의 별도 Rust crate를 구현/실행했다. 소비기/root/dispatcher 변경0,baseline RCT OFF,physical admission=false다.

현재 consumer dbb54009a517242ff5a41c805512471a74dd25f4의27 source files,src tree cb69b4736dd046e4675557577eb8e0ead037d1f3를 bytes로 검증하고 library dependency로 빌드했다. IGM의 RR/CI/DR/CE/freefree/photo/CMB/팽창 진단은 그대로이며 RCT는 별도 사건이다. OFF는 actual igm_point_rhs 결과를 그대로 반환한다. actual EOS에서 회수한T와원 RctProvider::closed_events를 사용하며 synthetic HHe/FT03율로 baseline을 대체하지 않는다. 직접 작은 delta_wdot/delta_Tdot를 반환한다.

새 IGM operational1..1e6K와KF96[1000,1e7],GM25[200,10000]K의교집합은[1000,10000]K다. 이는옛FT03와GM25의공집합을바꾼것도,empiricalfit범위/전체F09를승인한것도아니다.

nHeIII>0,ne>0에서 rho=R_RCT/R_RR3=k(1-x)/[alpha3(T)*(x+f*(y+2z))],xcrit=[k-alpha3*f*(y+2z)]/(k+alpha3). 고정T,y,z에서rho는x에대해감소한다. 제조 mostly-neutral(.01,.019,.001),f=.083의 T1001/3000/8000/9999K에서 rho_KF=.0800312/.174133/.351741/.413466,rho_GM=1.36053/2.96027/5.97960/7.02892다. ionized(.9,.3,.6)에서는양쪽모두1보다작다. 8000K neutral의R_GM=1.39689e-25 cm^-3s^-1이므로 큰상대경쟁을큰절대효과/관측량영향으로읽지않는다.

Ebar는명시적closure이며원자모멘트가아니다. 같은event R에서 chemical=-QR,thermal=(Q-Ebar)R,escape=EbarR이며 eV->erg변환은현재owner상수다. 직접전자/입자변화0이므로 delta_Tdot=2(Q-Ebar)*ev_erg*R/[3kB(nH+nHe+ne)]. consumerQ40.819325400298eV는그대로이며원자BO Q=1.5Eh로대체하지않았다.

56고유점:4T*2조성*[OFF+2source*Ebar(Q-1,Q,Q+1)]. 13native tests(2unit+11integration)PASS; 초기11시험중10개NOT_IMPLEMENTED RED,한immutableerror경계는원래PASS,2unit은후속추가다. 새finite checker는mpmath80자리752비영비교+272영검사와9기호식PASS,최대상대차2.777166e-16이다. 정규화RCT/global에너지편차는3.88563e-17/8.95800e-17. 이전과학suite/ODEhistory/원자solve0,independent review/interval certificate NOT_RUN.

정확상수율Maxwell을추가가정하면 meanEgamma<=Q+1.5kBT다. Q+1lowT8점은그추가surrogate에서불허지만산술stress-test는그대로다. 이를명목KF96/GM25의physical slope나실제source거절로해석하지않는다. 반대로범위안stress값도실제스펙트럼이아니다.

첨부17node WINDOW와현재remote13node SOURCE는서로다른입력/산출물로보존했다. 기존pendingpatch를이번업로드로복원했다고주장하지않는다. 둘다physical nuclear normalization과actualmoments는OPEN이다.

전체currentvendor/license/tests/point56행/checker/실패및성공로그는DELIVERY_RECEIPT의ZIP에있다. Git의소스projection만으로전체dependency가있다고하지않는다. 다음HE-FAST-REJOIN02는owner가이미진행중인IGMbaseline의한적분경로에선택적으로연결하는단위다. 새generic적분기/원자curvegate를추가하지않는다. HE-F2global=false,HE-F3/F09미완료,기본OFF와원momentsNone을유지한다.
