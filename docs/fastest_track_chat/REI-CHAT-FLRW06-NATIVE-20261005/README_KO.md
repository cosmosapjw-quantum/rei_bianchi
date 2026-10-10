# FLRW06 native 재현과 실제96node H/He 단계

상태: SCOPED_NATIVE_POINT_AND_PRIMARY_STAGE_VERIFIED__PHYSICAL_HOLD.

사용자가 제공한 Rust1.94.1로 이 대화 환경의 compiler blocker를 해소했다. 원 FLRW06 source6개를 b553698a114fbff05640ab6ecb95d260410de492의 Git blob에 고정하여 실제 homogeneous_photo_rates -> 실제 absorption -> photon_balance를 컴파일하고 실행했다. 167scalar 및6error 비교가 통과했고 stdout18records의 SHA256은 외부F08/SYNC02 반환과 동일하다. External proof 수신과 여기서의 재현을 구분한다. 같은 실험을 여러 물리 초기조건으로 재집계하지 않는다.

추가로 현재 coupled_primary.rs의 primary_stage_step에 같은96positive nodes를 넣었다. nH1e-4cm^-3,fHe.083,T50000K,H5e-14s^-1,dt1e7s,initial fractions(.9,.3,.6). 실제 nonlinear stage와 독립 FT03 Python rate lineage+4D endpoint root를 대조했다. native endpoint를 reference seed나 expected RHS로 주입하지 않았다. 원 scientific code 변경0, fullcargo0, ODE/history0. Stage 내부 density와 photonenergy는 고정이며 gaswork만 포함한다. Expanding density/photonredshift/sourcebirth는 enclosinghistory의별도소유다.

## 실제 결과

- Baseline compile/run0, source6blob/입력hash일치, maxrelative3.777652226439761e-15, invalid6. stdoutSHA e5a62d823d54925573b8d817375043cd34c2271363bbaa65c60ed0caeaf05316. 외부와 stdout만 같고 binary는다르다.
- Supplemental actual stage endpoint xHII=.9000006247788335,xHeII=.3000000772801580,xHeIII=.6000000038896905,T49999.93836959825K.
- Independent4D root9functioneval, gasfraction/lnT maxdiff2.220446049250313e-16. Event/packet 및동일node순서/분할 검사의 maxrelative1.307098350896367e-13. 총1182scalar에는 같은물리상태의metamorphic비교포함; zero288.
- Numberbudget residual -2.267446464038042e-17/H; energy+gaswork residual -2.109871589816059e-15eV/H. Node순서반전,96->192halfweights,dt0,negativecount rollback통과.
- Negativepacket은 PRIMARY_PACKET_DOMAIN, 입력state보존. 이것은 광범위한 invaliddomain suite가아니다.
- 성공 sciencecompile2, 새wrapper compilefail1, successfulprobeprocess2. 독립rootcheck는경로옵션추가후검산포함2회. 기존fullsuite0. 추가wrapper globResult충돌은원lib와같은Interval/Jet명시적export로수리했다. 증거checker의driver파일명typo도수리했다. 원source와tolerance변경없고전후로그보존.

## 도구체인과복구

첨부archiveSHA256294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40,192287020bytes. rustc1.94.1(e408947bf2026-03-25),LLVM21.1.8. rustc/hoststd/cargo만userprefix에추출했다. RUSTCORE는별도프로젝트이므로미사용. Detachedsignature는publickey부재로gpgexit2;upstreamauthenticity는미확인이다. 로컬hash/실행가능성과공식signature검증을구분한다.

원source는Drive의REI_REC_BASS_SYNC02_20261005_v1.zip을실제복구하고publishedSHA774c07fec25a9d08779ac17d1ddf866872c3e05b9d9c4e34cf4808cc59d86b4b와CRC를확인해확보했다. Incoming실제restore와아래outgoingR1을혼동하지않는다.

## 다음단계

FLRW06의native미실행상태는현재run에서종결한다. 다음chat는REI-CHAT-FLRW07_EXPANDING_SPLIT_STEP_REGRESSION. 먼저추가F08반환을읽고기실행부분은재검사하지않는다. 없으면실제geometry/source를2~4macrostep에연결하는범위에서per-stage density,birth,threshold,event/work,rollback과refinement를검사한다. Fullpairedcampaign이나F04/F05과거인증을반복하지않는다.

Currentread7c5469101f8d6ef027c8c3119cc5c053e15ba1d9: F04/F05 scopedstaticcompleted,F08conditionalstage,pairedhistoryNOT_EXECUTED,nextREI-F08. 사용자원gates(local<2e-4,width<2e-3,[160,161]FAIL2.1245050576368385e-4,tick160)및physicalHOLD보존. Production/runtime변경없음. Newbranch/merge/forcepush없음.

## 재현패키지

REI_CHAT_FLRW06_NATIVE_20261005.zip:2674608bytes,127entries,126payloadhashesverified.
SHA256 a73fb5b0aa76f6d94e0f5fac48be98002a1bf6fb77c6eae8a212b7af12fd6cad.
Drive https://drive.google.com/file/d/1u_s7VRkbxKLu1xLy4WDHhQtYdyUnhSeL/view?usp=drivesdk
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW06_NATIVE_20261005.zip

ZIP의rei_chat_flrw06_native_20261005/에전체REPORT_KO,원scientificsource,exactinput,실제binary2개/stdout/receipt,independentchecker와실패로그가있다. Toolchainarchive와RUSTCORE는재배포하지않았다. 저장된증거검사는python research/final_check.py이며native를재실행하지않는다. 실제재현명령은전체보고서§7에있다. 이저장소폴더는8개요약/receipt/인계파일만추가한다.
