# FT-SPEC-BRIDGE01: SPEC 이론과 실제 fastest-track 커널 재연결

상태: SOURCE_LINKED_NATIVE_SPECTRAL_ALTERNATIVE_SCOPED_VERIFIED.
2026-10-07, source commit dbb54009a517242ff5a41c805512471a74dd25f4. 원 scientific module 13개를 Git blob에 고정하고 실제 Rust1.94.1로 실행했다. 이 결과는 opt-in standalone 연구 caller이며 production default, 원 paired_runtime 전체, canonical gate를 변경하지 않는다.

## 선택과 결과

기존 CharacteristicRay::pullback과 primary_stage_step_conservative를 공유하는 두 계산을 비교했다. 하나는 고정 m8 에너지 재투영, 다른 하나는 birth label을 보존하는 exact-characteristic cohort다. 원자율/Case/열회계/초기조건은 같고 두 경로는 같은 시계와 source quadrature를 쓴다. S0의 0..1e12s 부분구간이며 전체1e13s campaign이 아니다. H=1e-14/s,nH0=1e-4/cm3,fHe=.083,초기gas(.9,.3,.6,w0=13.620772387478219eV/H),13.7eV 초기 .05광자/H와5e-15광자/H/s를 유지했다.

방출은 composite midpoint birth quadrature이므로 연속방출 오차가0인 것은 아니다. 매 구간 G-half/중간시각 밀도의 native BE/G-half를 사용한다. source가 gas work를, geometry가 radiation work를 소유한다. Fit13.6와binding13.598434599702를 구분하며 모든 subthreshold 광자를 보관한다. 반응BE 때문에 전체 방법은 일반적으로1차다. FLRW scalar 각도합만 사용했으며 Bianchi 각도격자로 해석하지 않는다.

|macro 수|cohort T(K)|grid8 T(K)|grid8-cohort(K)|
|---:|---:|---:|---:|
|64|47920.76469072467|47944.183295033305|23.41860430864|
|128|47919.18896097932|47943.608758636816|24.41979765749|
|256|47918.42442809899|47943.15324638324|24.72881828425|

계승한 독립 연속에너지 수치참조47917.629222632495K에 대한 cohort 차이는3.13547,1.55974,.795205K로 감소한다. 고정격자 자체의 시간연속 수치참조47942.4645619292K와의 차이는별도다. 원grid8-continuum bias24.83533929670K가 시간을줄여도남는것과일관적이다. 같은N256 grid16은47929.6053187904K다. 이 단일 공간세분화로 uniform spectral convergence를 인증하지 않았다.

Bracket[El,Eu]에단색e를보존재투영하면 count와평균은유지하지만 variance=(e-El)(Eu-e)가추가된다. Cohort는이투영분산을만들지않는다. 시간/source/원자fit오차와cohort수증가는남으며 projection-free가error-free를뜻하지않는다.

## 실행 증거

독립새폴더에서5명령모두exit0: unit compile,9tests,science compile,7native profiles,독립checker. 최종dataset7이력2920stage,max257packets. 선택한21단계의4gas nonlinear root와원자/사건/열/광자식을독립조립하여5258scalar를대조했다. Maxnormalizedgas2.22045e-16,eventrelative4.36030e-15,BEresidual1.80916e-16. Globalnumber2.30511e-14/H,energy1.06582e-14eV/H. 비교개수는독립물리초기조건수가아니다. Same-BE-map검사이며 IVP정확도인증이아니다.

전체turn은pilot와fresh재현을포함해16성공이력,6166성공stage,42reference roots다. Finaldataset과중복집계하지않는다. 새continuumIVP/Cargo/과거campaign=0. 첨부compiler는실행검증했지만서명진본성은검증하지않았다.

새projectionstub와passiveguard누락의red/green로그를보존했다. BRIDGE_PROJECTION_DOMAIN을고친대상은새caller이며원scientificsource가아니다. 나머지7tests는tests-after. 물리율/cutoff수정과사후heat보정은없다. 근거는ZIP results/FINAL_VERIFICATION.json,VERIFICATION.json,NATIVE_EXECUTION.json이다.

## 실행

ARCHIVE.json에고정된ZIP을준비한뒤:

```sh
python RUN_FROM_ARCHIVE.py --archive /path/REI_CHAT_FT_SPEC_BRIDGE01_20261007.zip --verify-only
python RUN_FROM_ARCHIVE.py --archive /path/REI_CHAT_FT_SPEC_BRIDGE01_20261007.zip --workspace /path/NEW_WORKSPACE --rustc /path/rustc
```

Launcher는SHA256,CRC,72payload해시를확인하고새폴더에만푼다. 내부reproduce.py가source13blob과Rust1.94.1을확인하여고립된재현을실행한다. Network/Cargo전체빌드는없고Python NumPy/SciPy가필요하다. Launcher의검증/추출/거절은실행확인,dispatch는mock계약시험이며 underlyingreproduce.py의실제5단계재현과구분한다.

ZIP은3579872bytes,73entries이며전체보고서,실행코드,원scientificsource,실제binary/stdout,독립검산과실패로그를포함한다. Toolchain archive/폰트는재배포하지않았다. Drive/Dropbox IDs는BACKUP_RECEIPT.json에있고 outgoing검증은R1metadata이며restore인증아니다.

다음 FT_SPEC_BRIDGE02_EXISTING_F08_SCHEDULE_ADMISSION: 기존F08 accepted time/source 시계에후보를선택적으로연결하고time/sourceerror를별도제한한다. 원default를자동교체하지않는다. Cohort압축/Bianchi입력/signedthermalinterval/physicalfit은open. 기존local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD와SPEC05증명범위는유지한다.
