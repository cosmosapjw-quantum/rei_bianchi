# REI-CHAT-SPEC02-20261006

판정: NONAUTONOMOUS_REWARD_INTERVALS_ENCLOSED__FEEDBACK_THEOREM_DERIVED__FULL_THERMAL_PHYSICAL_HOLD.

## 결과와 범위

시간 의존 prescribed HI bath의 유한 horizon에서 흡수확률 및 photoheat의 signed spectral error를 구간으로 제한했다. H=1e-14/s,nHI0=1e-5/cm3,nHI(t)=nHI0 exp(-beta Ht), beta=3또는103,T=1e12s,초기광자13.7eV다. Beta103은 추가 neutralfraction 감소를 외부 처방한 것이며 실제 gas해가 아니다.8분할13.6~13.7eV,활성cutoff와원형태ghostgap,chi=13.598434599702eV를 유지했다.

128time slabs/1024continuum panels의 outward bounds:
- beta3: Pgrid-Pcont in[-0.03381894,-0.03371532], Qgrid-Qcont in[0.00178669,0.00187073]eV/incident photon.
- beta103: Pgrid-Pcont in[-0.02685568,-0.02368683], Qgrid-Qcont in[0.00114427,0.00147672]eV/incident photon.

Singleabsorber,downward energy,nonnegative increasing reward의 killrate monotonicity와slabwise upper/lower rates,방향반올림 uniformization/Poisson tail을 사용했다. Probability뿐 아니라heat bias도0을제외한다. 경쟁종의species별reward에무조건확장하지않는다. Independentquadrature/IVP는certificate입력이아니다. Nativebit replay/실제F08이력/원자fit 정확도인증은아니다.

## 이론진전

유한horizon에서는terminal/exit frontier E*=Ec exp(H(T-t))에서backwardvalue의u_E가점프할수있다. 따라서전역C2를가정하지않고smoothbranch/나뉜차분과활성cutoff residence항을분리했다. 독립powerlaw diagnostic에서probability bulkdefect=-.03414181665037114,cutoff=.0007176176583624157이고dualidentity residual=1.08e-11이하다. Cutoff생략시이항이남는다.

Gas경로위가상continuumradiation을사용하면누적spectralforcingD에대해e'=Ae-D',e(T)=Phi(T,0)e0-D(T)-integralPhi(T,s)A(s)D(s)ds다. D(T)만이아니라전체D(s),공통tube의lognorm/Jacobian gascolumns,초기오차와불일치jump가필요하다. D(t)=.1t(1-t),A=-1이면D(1)=0이지만e(1)=.1(3/e-1)=.0103638323514327이다.

같은representation/source/geometry의순수H등온계는Jacobian이Metzler이고columnsums가비양수이므로(x,photon/H)의L1차가증가하지않는다. ThermalHHe/CI/secondary/다른spectralgenerator에는자동적용하지않는다. 작은compositionfeedback검산은alpha=2e-13cm3/s인합성상수이고heat는diagnostic만계산했다. 그xendpoint는continuous .93308013754025,m8 .93185368404073,m16 .93251306706923,m32 .93283171800057이다.

## 실행증거

최종4명령exit0. Unit8,symbolic6,exactFractionJacobian80,feedbackquadrature3,interval4profiles,각beta당continuum1024panels. 이번총14경량IVPsegments,max38변수. 최종runner는IVP재적분없이동일turn저장reference와새interval을비교했다. Tests-after이며red/green claim없음. Native/Rust/Cargo/fullhistory/과거suite0. 부모SPEC01payload30개해시검증,원과학시험재실행없음.

## 재현패키지

REI_CHAT_SPEC02_20261006.zip:131282bytes,88entries,87payloadfiles.
SHA256=7f92b10462359d2c60393e29aab0b2767a2d14b36124d0804c09c6d82187562f.
Drive:https://drive.google.com/file/d/1mya028F3Dkplb4vD6B1doVZpKGskb3Oh/view?usp=drivesdk
Dropbox:/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_SPEC02_20261006.zip

ZIP내rei_chat_spec02_20261006/REPORT_KO.md,THEORY_AND_FEEDBACK_CONTRACT.json,results/verified/FINAL_VERIFICATION.json과manifest를읽는다. 재현: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/run_checks.py --output NEW_DIRECTORY. 새폴더만허용. 재현원문과코드/입력/증거는ZIP에있고저장소에는요약8파일만추가한다.

## 남은범위

ActualFT03thermal tube의M,C와전체시간Dg(t)는미적용. 다음SPEC03_THERMAL_FEEDBACK_TUBE_APPLICATION. BI첫transaction은별도미수신이며같은추출요청/campaign반복없음. Originalsource/CODEX_SYNC/runtime_returns/fixture변경없음. local<2e-4,width<2e-3,[160,161]FAIL=.00021245050576368385,tick160,auxiliaryescapeFAIL,physicalHOLD보존.
