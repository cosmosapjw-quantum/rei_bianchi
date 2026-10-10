# COLD_COMPTON_COMPONENT01

PR106의 깨끗한 commit `690b5f755dbaf379130cc5c58fedf6819703981e` 및 tree
`28243343518c0b2edbf106fd4b23110eb97ab04c`에서 별도 worktree/branch를 만들었다.
기존 AtomicProvider, HII RR 및 legacy 경로를 변경하지 않고 public
`cold_compton::stage`를 추가했다. 입력은 이미 저장된 REC baseline/refined의
z=20, 15.9 네 endpoint다. 새 history 실행은 0회다.

로컬 original October-2012 HyRec ZIP과 `HyRec/history.c` SHA를 먼저 확인했고,
정확한 원문 member bytes를 `source/history.c`에 보존했다. 식은 원문
`rec_dTmdlna`의 비평형 branch에서 계수 `4.91466895548409e-22`를 사용하며
fsR=meR=1을 고정한다. `Tgamma`는 각 endpoint의 저장값이다.

같은 stage의 nH, nHe, xe에서 ne=nH*xe, fHe=nHe/nH를 계산한다.
`dT=A*Tgamma^4*xe/(1+xe+fHe)*(Tgamma-Tm)`와
`q=1.5*kB*ne*A*Tgamma^4*(Tgamma-Tm)`을 proper SI, proper seconds로 평가한다.
gas thermal ledger에 +q, prescribed CMB bath ledger에 -q를 기록한다.
모든 H/He species, electron count, binding derivative는 정확히 0이다.
CMB bath는 RR escape ledger와 별도로 유지한다.

release locked build 1회와 네 endpoint campaign 1회가 모두 exit 0이다.
Decimal80은 frozen binary64 입력과 상수를 기준으로 평가한다. 최대 coefficient/
ledger 상대차는 `3.2549318216997117e-16`, EOS 상대차는
`2.8517494184276044e-16`, gas+bath scaled residual은 0이다.
비평형 branch의 `H*rec_dTmdlna+2*H*Tm` 산술 parity 상대차는
`7.786509534956339e-15`다. tolerance는 각각 3e-12, residual은 1e-13이다.
Tm=Tgamma 및 ne=0에서는 exchange가 0이고, 작은 hot-gas 상태에서는 gas가
냉각되고 bath가 가열된다. 원문의 equilibrium special branch는 해당 parity
평가에서 제외한다. 해당 branch는 history integration의 별도 근사다.

독립 Astra review도 `PASS_SCOPED`다. review는 저장된 네 normal endpoint와 세 control만 재계산했으며 invalid-input API branch의 전 범위 검증은 포함하지 않는다. 현재 결과는 순간 Compton component의
`PASS_SCOPED`다. He reaction closure, Bianchi IC 채택, CR evolving state,
결합 오차 예산, coupled history, radiation backreaction 및 global admission은
`HOLD`다. 이 결과로 전체 저온 atomic/thermal provider를 승인하지 않는다.

실행 명령과 stdout/stderr, exit, wall 시간 및 executable SHA는 evidence의
BUILD_RECEIPT/CAMPAIGN_RECEIPT에 보존했다. 최초 실패와 repair는 없었다.
재실행은 campaign 예산을 새로 승인하기 전에는 수행하지 않는다.
