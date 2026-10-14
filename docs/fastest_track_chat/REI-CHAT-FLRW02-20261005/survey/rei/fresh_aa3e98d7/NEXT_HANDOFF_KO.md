# FLRW02 -> expanding adapter and integrated-budget regression

Repo cosmosapjw-quantum/rei_bianchi, 같은 branch forward/rust-reion-kernels-20260922, draft PR83. 다음 chat 노드는 REI-CHAT-FLRW03_EXPANDING_ADAPTER_AND_INTEGRATED_BUDGET이다. 원 F00/F03 fixture와 production API를 소급 변경하지 않는다. PB02와 FT07은 deferred이며 REC 공급자 전달은 완료된 REI consumer linkage가 아니다.

시작/단계 경계/게시 전후 실제 remote ref를 읽는다. Source snapshot은 c1d7f89c8abc90a6adf971390f2bce7ae7530a23이며 이후 REC 문서4ad4080 및 영수증9455c2a를 수신했다. Source는 ZIP의 SOURCE_BINDING.json 세 blob에 묶여 있다. 이후 변경은 관련 diff만 확인한다. CODEX_SYNC와 runtime_returns를 덮어쓰지 않는다.

읽기 순서: README, TASK_RETURN, SOURCE_BOUND_CONTRACT_SUMMARY, ZIP REPORT §§3–7와 필요한 results. 이전 FT/PB suite, F03 전체 native tests, 원자 문헌 전수검산을 반복하지 않는다.

최소 native 회귀는 ZIP의 research/run_native_probe.py --repo EXISTING_REI_REPO --output NEW_NATIVE_RESULT.json 이다. 고정 commit의 세 blob을 git show로 임시 디렉터리에 추출하고 원 bytes를 바꾸지 않는다. Minimal crate interface와 단일 rustc만 쓰며 cargo 전체 build/history를 돌리지 않는다. 현재 rustc 부재로 native 실행은 blocked이고 wrapper의 Python 문법만 확인했다. 실제 build/실행 exit와 출력 전에는 native-verified로 바꾸지 않는다. 최신 source가 바뀌면 고정 c1d7 회귀와 신버전 검증을 구별한다.

다음 이론 작업은 expanding photon storage, source emission, proper/comoving 변환, moving energy label 또는 fixed-edge flux를 한 successor 계약에서 연결하는 것이다. Reaction-only 진단 x=x0/[1+alpha*nH0*x0*(1-exp(-3Ht))/(3H)]를 actual density-history adapter에 연결한다. Fraction에 -3Hx를 추가하지 않는다. 현재 manufactured k와 ell을 실제 opacity와 spectral redshift flux라고 해석하지 않는다.

적분형 defect는 DeltaQ-(S-Rref)=-Deltaeta-Z-O+I-DeltaXi-(Reff-Rref)+Enum이다. 같은 실제 source stage의 누적 사건을 쓰며 final endpoint 하나로 two-half 사건을 재구성하지 않는다. Reference recombination을 잔차가0이 되도록 fitting하지 않는다. 포화에서 Q만 clip하거나 alphaB와 같은 ground diffuse source를 중복 적용하지 않는다.

F04 actual residual은 이제 존재한다. 실제 parameter box, interval Jacobian/root 및 uniform full-half flow remainder는 남아 있다. 이번 조건부 residual projection으로 대체하지 않는다. 외부 F04 owner와 충돌하지 않으며, native 결과를 기다린다는 이유로 독립적인 expanding 이론을 멈추지 않는다.

기존 strict local<2e-4/public width<2e-3, [160,161] FAIL=2.1245050576368385e-4 및 tick160 보존. 같은 branch append-only non-force와 기존 Drive1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ / Dropbox BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1에 create-only 백업한다. Metadata, archive hash, 실제 restore와 과학 검증은 분리한다.

