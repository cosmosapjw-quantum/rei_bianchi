# ENDPOINT14 비저자 계약·수학 검토

**판정: PASS_SCOPED_CONTRACT. Blocking0, nonblocking0.** 이 판정은 root가 작성한 계약의 수학적 연결과 현재 입력 재사용을 확인하여 S05 준비로 진행할 수 있다는 뜻이다. 구현과 실제 결과의 검토는 아직 수행하지 않았다.

검토자 `/root/repo_delta14`는 이번 endpoint 이론·구현의 저자가 아니다. 별도로 최신 source intake를 담당했고 부모 문맥을 상속했다. Blind isolation이나 관찰되지 않은 runtime model ID를 주장하지 않는다. 과학실행·기존science import·geometry/trig/optimizer 호출은 모두0이다. 실행하지 않은 실제 후보 data 판정을 미리 PASS로 바꾸지 않았다.

## 확인한 핵심 논증

1. **전체 함수족.** (q(1)=0)인 degree≤3의 (q(z))는 유일하게 (q=(1-z)r),degree(r≤2)로 나뉜다. (z<1)에서 양성성 동치이며 (r(1))는 연속성으로 처리한다. (a_2=0)인 경우가 정확히 endpoint-zero even-quartic 부분족이다.
2. **B=160.** 각도46/61/87의 저장된 (z) 구간은 (1/2) 아래이고 서로 (1/5) 이상 떨어져 있다. 고정 window의 양수 ordinate와 upper≤1/2로 (0≤r(z_i)≤1). 3점 Lagrange식에서 역분모≤25와 numerator계수 ((1,2,1))를 사용하면 (|a_j|≤(75,150,75)_j). 이 box는 참 함수족을 잘라내는 regularizer가 아니다.
3. **Dmin.** (b=(a_0,a_1-a_0,a_2-a_1,-a_2))이므로 (|f'|≤18B). (L_*=7/50,delta=L_*/(36B))로 (D≥L_*^2/(36B)=49/14400000). 새 exactcontrol에서 저장된87도 (mu) 구간의 (delta)-확장 containment를 확인하도록 이미 계약되어 있다.
4. **행 구간.** (c_j(z)=(1-z)z^j)의 제시한 product bounds는 각 인자가 비음수이므로 안전하다. Signed계수에도 box와 반폭합 epsilon이 작동한다. Inner수축/outer확장 방향이 올바르다.
5. **기하와 새 moments.** 실제 이전 `geometries` 정의는 fullazimuth (A=[\nu_0,1],B=[-1,-\nu_0])다. 원래 labmap에서 (X=e+G\sqrt R\mu,T=H(1-\mu^2))라 놓으면
   
   (F'=H(G\sqrt R+e\mu)/(X^2+T)^{3/2}>0)
   
   가 (K=e^2-G^2R<0) 아래 성립한다. 두 same-event assignment의 합집합은 (C=[-1,-t]\cup[t,1]), (t=\max(F^{-1}(\nu_0),-F^{-1}(-\nu_0))≥0)다. 따라서 (k_0=2(1-t))를 역으로 풀 수 있다. 새 weightedmoment (G_j)의 derivative (-2(1-t^2)t^{2j}≤0)는 계약의 endpoint순서를 보장한다. Savedoldmomentoverlap은 compatibility검사이며 이 analyticshape논증을 대신하지 않는다.
6. **유한 sandwich.** Bernsteininner/nodalouter 및 subdivision 포함 관계가 유효하다. Boundedpolytope의 모든 vertex는3개의 독립active normal을 갖는다는 사실로 완전 tripleenumeration을 연결한다. Signed numerator의 concavity/convexity와 양의denominator weighted Jensen을 사용한 extrema보장은 올바르다. Outer표본의 비양성 가능성과 실제 feasiblewitness를 분리한다.
7. **고정 후보.** 수기로 완전제곱하면
   
   (r(z)=\frac{33}{25}(z-\frac{25}{264})^2+\frac{170627}{1320000}>0,
   \quad D=\frac{14297}{52500}.)
   
   N1의 중간 Bernsteincontrol은 (161/10000>0)다. 실제 네 anglewindow 통과는 아직 실행하지 않았으므로 새 campaign에서 판정한다. (a_2=33/25\ne0)이므로 후보는 진짜 degree6이다.

## 입력·이전 결과

실제 source `M0475.x4`의 SHA256은 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, 저장된 QUARTIC12 입력은 `a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45`로 일치한다. Source의330MeV네 CMangle·DATA-CM·ERR-S를 읽었고 NB/SR단위와 window가 계약과 일치한다. 총단면적6점은 별도 energygrid다.

저장된330MeV `endpointzero_exact`는inner0/outer0,모든objective EMPTY_OUTER다. FreeN4/N16은각각inner4/outer4로 남아 있다. Degree확장이 이 정확한 이전 주장과 어떻게 비교되는지 명확하다. 이전 캠페인을 반복하거나 적합한 과거결론을 무효화하는 주장은 없다.

NG1–NG7 관점에서 이번 주장은 명시된 degree/window/endpoint조건에서의 constructive model-class감도다. 기존 quartic배제는 고정된 대상에 한정하여 재사용하고, 새 강한 물리no-go·문헌전반신규성은 주장하지 않는다. 실제 sourceprojection/flux/birth·binding3입력과null/off상태는 그대로다.

## 다음 전이

Frozen계약에 따른 implementation과S05준비를 진행한다. 기존에 요구된 sourcepublication/executionpin, staticimplementationreview,controllerGO를 따른 뒤 새유한실행을 한다. 수치성공·내외접근간격·전체완료는 그 실제 결과와 비저자검토로 판정한다. 새 반복감사나 과거실행을 추가 요구하지 않는다.
