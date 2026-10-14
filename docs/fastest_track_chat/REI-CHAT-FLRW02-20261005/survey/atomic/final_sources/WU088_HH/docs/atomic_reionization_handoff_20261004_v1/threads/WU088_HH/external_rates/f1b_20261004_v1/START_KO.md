# HH-F1B: F03 실제 좌표에 결속한 HH 원자 source reference

Fastest 경로로 복귀했다. 새 REI F03의 실제 7좌표/RHS/BE endpoint를 읽고, 외부HH source의gradient/Hessian/JVP와rank-one보존구조를유도·구현했다. 기존합성모형은변경하지않았고Rust소비자함수/history를실행하지않았다. HH-F1물리domain과HH-F2실제연결은미완료다.

## 전체 패키지

- 이름: WU088_HH_FAST_F1B_DELIVERY_20261004_v1.zip
- bytes: 61822
- SHA256: 35c32326413e6bd3d9e3804d70bf325c8c8450800e9d9e38d8d9644859cced73
- Drive ID: 16kwnw5XiCCO5bFe1uaXVdZ4V9emg610j
- Drive parent: 1074Hr5msnAMgIXWU-PmgdMrQvrdV6emM
- Dropbox ID: id:BSpOijBcT10AAAAAADyJqg
- Dropbox path: /BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31S_NCP_REDESIGN_20260928/WU088_HH_FAST_F1B_DELIVERY_20261004_v1.zip
- 41 payload SHA/size와ZIP CRC확인. 양provider완료ACK/name/size확인,새출력RESTORE_VERIFIED=false.

기존cache나인증된cloud한곳에서회수한다. 사용자재업로드나동일bytes양쪽중복다운로드를요구하지않는다. ZIP의REPORT_KO.md,THEORY_KO.md,SOURCE_BINDING.json,CONSUMER_CONTRACT.json,RESULT.json을읽는다. Git의두src와두test는원ZIP과byte동일하다. 전체24unit은이Gitdir에서실행가능하지만측정데이터·증명·sourceprojection·원실패기록은ZIP을쓴다.

```
python3 -B -m unittest discover -s tests -v
python3 -B src/hh_f03_binding.py --input input.json --output /tmp/NEW_HH_POINT.json
```

원자수식: P=nH(1+h)+nHe(1+y1+2y2),T=2u/(3kB P),q=nH(1-h)^2 k,R=nH q. 원network convention대로추가1/2없음. chi는consumerconstants의bindingerg이며fitactivation kB*B로바꾸지않는다. fHH=c q,c=(1,0,0,-chi*nH,0,0,0). JHH=c gradq^T는rank<=1이고energycovector와정확상쇄. Smoothbranch에서lambda=gradq.c<=0,HH-onlyBEdet>=1이지만전체F04가역성/수렴인증은아니다. h=1에서gradient0/Hessian_hh=2nHk,ne=0에서도HHsource가존재할수있다. LCS3000K는원floorvalue를반환하되smoothjet는null,KS에cutoff추가없음.

현재원소스: REIc1d7f89c8abc90a6adf971390f2bce7ae7530a23의hhe_events.rs와microstep.rs. 후기HEAD9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa까지의추가는REC문서이며hheblob57a63eee1e9d8c4aa2b5ed663dbea15619359f71불변이다. Rustsource는connector로읽었고fullRustbyteslocalmirror는아니다. code용입력constants와진단온도는physicaldomain승인이아니다.

다음:매루프HH/REIliveHEAD조회. 실제REI-F07 domain/distribution/constants/원자·열단일owner/좌표/observablebudget을받은뒤HH-F2를consumer가확인한seam에서결속한다. 현재REIruntime다음은F04다. HH를beta_e에k*nHI/ne로위장하지않고전용eventcounter/heatowner를보존한다. full/half1/half2각endpoint의source와event를사용한다. 기존constant-rate thermalupdate에HH source만사후추가하고완료라고하지않는다.

24/289,265unbounded,epsilonnull,B22OPEN,소비FD1/FD2/pilot,원DB를보존한다. 과거FLRW/PB/원자suite와legacyNCP적분을새의존성없이반복하지않는다. 새로운Bianchi/thermal/historysolver는만들지않는다. SameHHbranchappend-only/nonforce,기존Drive/Dropboxcreate-only백업을직접수행한다.
