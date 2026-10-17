# RUN09: 출생 광원 표본 세분과 비선형 응답

2026-10-17 시작한 REI atomic/nuclear SSOT의 P4-S4C-SOURCE-SUPPORT-CONVERGENCE. 부모 RUN08 commit 8b61e9d733713a49bce3b28be2192ae5d7fe11bc 위의 add-only 연구 결과다. 사용자 local/Codex/NCP/SSH, production/main/기존 checkpoint 변경은 없다. Native independent subagent/reviewer actor NOT_RUN.

## 같은 물리 입력에서 바꾼 것

BASS121 SIGNED_MINUS의 실제 prescribed Einstein–Vlasov 기하, X=ln(a/a_ref),a_ref=1/21,X=.7.. .7004. 원래 MD14/BB50k fesc=.2,48개 spectral cell mean,GL8 방향,Grackle/Verner/Savin/DAtomicProvider와 동적 H/He/D 공동 RHS 유지. 초기 T10000K,HII=DII=.1,He4(.8,.15,.05),D/H2.5e-5,YHe.245,D defect.0037eV는 기존 제조 입력이며 REC donor/실측 isotope spectroscopy가 아니다. CMB bath=2.7255/a K. 새 gas/photon stress로 Einstein 방정식을 다시 풀지 않는다.

남은 수명 v=(t1-tb)/(t1-t0)의 원래10개 graded panel(seed359.22363635035254,growth2)을 각각 r등분하고 각 child에 양의 GL4를 적용했다. r1/2/4/6=40/80/160/240개 출생시각,15360/30720/61440/92160 physical cohorts. r1은 원본 emitter를 직접 호출하며 원래 tuple491520bytes SHA256 7d29d5c9dda88befd5141a9257170f70d96bcbd6937a2de14a159ac1e3d6a134와 일치했다. 각 새 출생에서 원본 source_births를 사용하고 가중치 정규화,tail 제거,clipping은 없다. 무틸트 LRS +/-mu reflection의 정확한 집계만 사용했으며 각도를 줄인 근사가 아니다.

새 source_support.rs,시험,exporter와 scientific Python drivers를 별도로 추가했다. 기존 Rust81개 중 lib.rs는 원본 prefix+주석/module declaration이고 나머지는 byte-identical; 원자 owner12개는 모두 unchanged. 원래 input13개와 retarded_integrator.py 및 gas_integrator_parent.py도 byte-identical. 공동 ODE를 바꾸지 않고 출생 source support만 비교했다. r4/r6에서 solver tolerance만10배 줄인 대조를 수행했다. r2full-tight와paired-standard 대조는 표현과tolerance가 동시에 달라 순수한표현오차로 부르지 않는다. 새 support Radau는 NOT_RUN, RUN08 Radau 검증은 historical retained evidence다.

## 실제 계산 결과

네 source supports,7개의 완료된 DOP853 설정. 더 엄격한 r6는 유한표본 진단 reference이지 연속 광원의 정확해나 rigorous enclosure가 아니다.

| births | cohorts | T[K],standard | surviving photons[comoving m^-3],standard |
|---:|---:|---:|---:|
|40|15360|9994.351242713110|5.107743578718739e-7|
|80|30720|9994.351244146003|5.107749124848808e-7|
|160|61440|9994.351244575617|5.1077491733388e-7|
|240|92160|9994.351244636106|5.107749173516125e-7|

r4→r6 모두tight3e-12,분모r6의 차이(백분율 아님): survivor+3.4719194e-11,T+6.0546522e-12(약6.05e-8K),HI흡수+2.9263928e-9,HeI흡수-4.0339917e-8,HeII흡수-3.2527729e-8,DI흡수+2.6606202e-9,DII분율+8.5239892e-12. r1→r6 survivor 상대 변화 약1.09535e-6. 총생성광자수는 모든표본에서 약6.00614502819333e-5로 같다.

r4/r6 standard→tight T차이5.45697e-12/2.91038e-11K,survivor 절대차이3.17637e-21/2.96462e-21. HI/DI의solver설정차이는source r4/r6변화의약0.8%이하. 이는 관측된설정민감도이며 true global error bound가 아니다. r2,4,6 세점 power-law fit은survivor약8.04,T/HI/HeI약2.44–2.45로 다르지만 점근차수나Richardson상계로 승격하지 않았다.

완료7설정 최대잔차:photon2.29007e-11,energy/initial2.96393e-14,energy/source1.64462e-11,H종별사건9.99201e-16,D분율회계1.49078e-15. 보존은정확도의대용이아니다.

## 이론과 독립 scalar 검산

고정-opacity exp(-tau*v)의 GL4 remainder: panel폭h에서 0<=I-Q<=h*(tau*h)^8*exp(-tau*a)/1778112000. r등분한child bounds의합은parent bound/r^8이하다. Wolfram 계수/도함수/세분비율 검산을 수행했다. 이선형kernel의상계는 nonlinear feedback의8차오차를보장하지않는다.

차원없는 별도 제조계 q'=1-q^2,q0=0,연속해tanh(t). GL4 source jump와 exact reaction map q/(1+q*dt)를 결합하면 C(u)=sum_(c_i<=u)w_i에 대해 local error=-D*h^3+O(h^5),D=integral(C-u)^2>0. GL4 source0..7모멘트가정확해도이항은남는다. MP60 D=.00679355009641720266306431556698428759404282650014975008358393,모멘트잔차3.112e-61이하,CDFidentity잔차1.094e-61. 반복panel의최종관측차수1.99994648. 이는HHeD가아닌 명시적반례이며 일반물리no-go/novelty/실제계의동일계수주장이아니다.

원본MD14식의독립scalar시간적분 생성량6.006145028193166e-5와native최대상대차이2.7190e-14. Dimensionless elapsed-time0..7모멘트최대상대차이1.8602e-11에는 원래clock의유한산술도포함된다. Read-only normalized sourceCDF 최대차이는40/80/160/240birth에서.0605722/.0302885/.0151448/.0100967. Physicalpacket을재정규화하지않았고CDF차이를관측량상계로쓰지않는다.

## 실패·자원·복원

320birth,r8 packet export는완료됐지만공동적분은outer45s에서endpoint없이중단됐다. 이설정은모든완료/과학통계에서제외했고같은실행을반복하지않았다. 더작은r6로별도범위를정했다. 완료7설정의solver내부wall합88.286589333s는설치/export/준비/시험/중단/복원을제외한다. 최대완료processRSS1269668KiB(약1.21GiB). 중단한r8의processpeak는측정하지않았다.

Rust151/151(기존145+신규6),Python신규7+기존8,strictClippy,new-code-rustfmt PASS. 핵심40vs80node regression은실제red→green을기록했다. 모든시험을TDD라고주장하지않는다. 최초모호한float type오류와새Pythontest의파일ResourceWarning을보존하고수정했다.

최종fullZIP을새디렉터리에풀어204payload hashes,151Rust+15Python,strictClippy를확인했다. 대표r2paired(80births,30720physicalcohorts)의15397 endpoint floats를다시계산해binary64 exact equality를확인했다. 전체7campaign을복원후반복한것은아니다. Restore최대RSS317184KiB,oneCargo/BLASthread,4GiB sandbox. 별도외부RECEIPT에실제phase exit/log를보존한다.

## 보존과 다음 DAG

이디렉터리의REI_RUN09_CORE_SOURCE.tar.xz는14개실제newsource/test/driver/DAG/resume파일이며단독전체Gitcheckout은아니다. RUN08 fullsource와lib.rs의pub mod source_support;추가,원본nativepacket생성이필요하다. 전체복원에는아래fullZIP과그안의RUN09 REPLAY_OFFLINE.sh를사용한다. 이전RUN06등의Git전체backfill을완료했다고주장하지않는다.
Core13624bytes,SHA25631056971f5294bf093337d01b13e683e371b31cf3ac44dddedd4acff93d4255a,Gitblob e0b294cc9a311938d5ca3a92813ef9e6884a7e0a.

FullZIP REI_ATOMIC_NUCLEAR_RUN09_SOURCE_SUPPORT_20261017.zip:14407737bytes,205entries,204payload hashes.
SHA256039fbce620bfa90e43822727d01cb8a2734fbfa78ef894673c7de9a06aa16029.
Drive https://drive.google.com/file/d/1PBxYh7wM0t7IUrsB2v7g5eu6vW1BB9wo/view?usp=drivesdk :업로드및authenticated full byte download SHA256일치.
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN09_SOURCE_SUPPORT_20261017.zip :id:BSpOijBcT10AAAAAAD-obA,업로드완료,provider contenthash6634d8244405cd0ae6399671dbef64e9c9b844b5e4dc604422a826725d8d2e02가local계산과일치. 독립rawdownload는실행환경URL검사에서차단돼완료하지않았다.

Admission PASS_SCOPED_NATIVE_BIRTH_SUPPORT_SCAN_NO_CONTINUUM_BOUND. 다음P4-S4C-SPECTRAL-EDGE-SUPPORT: 비용과r4/r6차이를근거로r4를제한된작업입력으로선택하고H/D문턱을포함한첫sourcecell부터positive spectral refinement. Per-cellcount,energy,threshold와samejointsolution을비교한다. 연속birth의엄밀상계,spectrum/angle/fullEoR/Einsteinfeedback/whole-donor/FLRW-CONV/BI-SIGNED/ISO-COUPLEfull/미완료LiBeT1-T8은HOLD. 조상45/26DAG불변. Archive밖DELIVERY_RECEIPT.json이새원격ID와복원상태의권위이며fullZIP을재봉인하지않는다.

문헌:NIST DLMF3.5 Gauss remainder;Reynolds etal arXiv0901.1110;PawlikSchaye arXiv1008.1071;Deng etal arXiv2309.15900,MNRAS527478(2024);SciPy1.17.0 solve_ivp docs. 문헌은이번수치값/독창성을대신인증하지않는다.
