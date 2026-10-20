# 실제 원전·도구 사용
검색/검산일: 2026-10-20 UTC. 이번 적용 대상은 독립 이력의 실행 순서와 자원 제한이며 ODE 내부 solver나 물리 모델은 보존한다.

- Exa 실제 검색과 원문 읽기: Cargo 공식 build/jobs 설정(https://doc.rust-lang.org/cargo/reference/config.html#buildjobs, https://doc.rust-lang.org/cargo/commands/cargo-build.html). jobs는 병렬 compiler process 상한이며 CLI에서 지정할 수 있다. 새 실행기는 이 값을 확인된 CPU/메모리 예산과 연결한다.
- Exa 실제 검색과 원문 읽기: Python subprocess와 concurrency 공식문서(https://docs.python.org/3/library/subprocess.html, https://docs.python.org/3/library/concurrent.futures.html, https://docs.python.org/3/library/multiprocessing.html). 실행 가능한 CPU 수와 전체 CPU 수를 구별하며, argv배열/별도processsession으로 각 계산과 timeout을 관리한다.
- SciSpace 실제 자연어검색: independent IVP histories, identical processors, Graham list scheduling 질문. 10논문 반환. 그 결과에서 Graham 1969와 후속 LPT 연구를 식별했다. SciSpace 초록을 full-paper 검토로 기록하지 않는다.
- Exa로 원전 보강: R. L. Graham, Bounds for Certain Multiprocessing Anomalies, Bell System Technical Journal45(1966),1563–1581, DOI https://doi.org/10.1002/j.1538-7305.1966.tb01709.x. 원문 PDF 검색결과에서 independent tasks와 list scheduling 정의 및 해당 고전적 bound를 읽었다: https://ia801900.us.archive.org/27/items/bstj45-9-1563/bstj45-9-1563_text.pdf .
- Graham, Bounds on Multiprocessing Timing Anomalies, SIAM J.Appl.Math17(1969),416–429, https://epubs.siam.org/doi/10.1137/0117039 는 서지/원전 위치를 확인했다. 이번 코드의 실제 비용보장을 그 논문의 경험적 가속값에서 가져오지 않는다.
- Wolfram context를 실제 요청하고 symbolic evaluator를 두 번 실행했다. list-bound identity=0, inequality=True, speedup derivative=(s-W)/(B+s)^2, Y=1227/15092 및 전하미분식을 얻었다. 첫 evaluator의 symbolic undefined-name warnings는 raw에 보존됐으며 결과표현은 정상 반환됐다. 두 번째 계산에서 독립 vector fields의 Lie bracket={0,0,0,0}와 block-diagonal Jacobian을 얻었다.

주장: 동일한 프로세서·고정 job times·독립 task·추가 overhead가 없는 고전적 모델 아래 bound를 root가 직접 유도했다. 실제 시스템의 CPU공유/메모리경합/프로세스기동비는 actual paired measurements가 판별한다. 64CPU NCP 가속률과 병렬 compile 가속률은 아직 측정하지 않았다.
