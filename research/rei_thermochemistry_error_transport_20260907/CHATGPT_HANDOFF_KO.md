# REI thermochemistry error-transport — 주 대화 직접 반환

STATUS: PASS_REI_CONDITIONAL_RESOLVENT_ORACLE

## 실제 새 진척

이번 주 대화에서 조건부 정리와 정확 유리수 검산 코드를 작성하고 GitHub에 게시한 뒤, GitHub-hosted runner에서 새 검산을 실제로 실행했다. 기존 XZ 수정이나 native 계산의 과거 PASS를 새 계산으로 사용하지 않았다. 주 대화 container/Python은 프로세스 시작 전에 실패했지만 GitHub 실행은 가능했다.

- 연구 source commit: `019608c2a400423485795696ecb47523361d4c13`
- 연구 source tree: `ba2fda37a5b6ac7fea116b249f8b9db264952050`
- parent: `54a879231c68734fdda6990d67d8458d2918943e`, tree `29c406032a99d335ac52f866460e9b47ea42463b`
- checker SHA-256: `f7b7d7e474ee5877c223ef8ccd5b78659dc2214b0002ea11b247607b3dacaf6b`

실제 연구 workflow: run `34042290101`, job `101511110133`, SUCCESS. Decoded full job log를 읽었고 B01–B10의 10개 method 전부 PASS, failure/error/skip 0, 테스트 본문 약 0.005 s를 확인했다. Repository verifier와 diff/최종 clean-source 검사도 같은 job에서 통과했다. 별도 repository workflow `34042290056`도 completed/success로 확인했다. 이 별도 검사 성공은 논문 수준의 scientific admission이 아니다.

실행한 명령:

```text
python3 -B research/rei_thermochemistry_error_transport_20260907/verify_bounds.py --report <external-output>/RESULT.json
python3 -B scripts/verify_repo.py
```

GitHub가 보고한 artifact는 6개 파일, 2535 bytes, ID `9992039821`이다.

https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/34042290101/artifacts/9992039821

Artifact ZIP SHA-256 (서버 보고값; 여기서 바이너리를 다운로드해 재해시한 값 아님):
`4a4fece52fcd91c4c01cafbf48efe974c89dd1481d4caf0f3cd9de8573e2fd11`.

이 handoff를 추가하는 evidence commit과 위 tested source commit은 다르다. 후속 publication/PR CI는 해당 새 head의 결과로 별도 보고한다. 이 파일 안에 아직 생성되지 않은 자기 commit hash를 넣지 않는다.

## 연구 결과와 경계

`PROOF_AND_SCOPE.md`의 가정은 고정 positive weights w, column-vector generator A, 비대각 원소 비음수, w^T A=0, dt>=0다. 단위는 proper time seconds와 A의 s^-1이며 dt*A는 무차원이다.

1. Frozen resolvent P_A=(I-dt*A)^-1는 비음수이고 w^T P_A=w^T, weighted-l1 operator norm은 정확히 1이다. 이는 비증폭이지 엄격한 수축이 아니다.
2. 두 generator를 비교하면 P_A-P_B=dt*P_A(A-B)P_B다. 따라서 상태·입력에 따른 반응률 변화가 만드는 추가 오차항을 생략할 수 없다.
3. u(s)=(1-s,s), a(s)=s^2/tau0, b=0, dt=tau0인 합성 반례에서 g(s)=(s+s^2)/(1+s^2). s=1/4와 1/2 사이 거리의 증폭률은 exact `104/85 > 1`이다. 각 단계의 양수성과 원자핵 수 보존은 유지된다.
4. 실제 coefficient Lipschitz bounds와 local defect가 별도로 검증될 때만 E_next <= alpha*E+eta와 그 곱/합 누적 경계를 사용할 수 있다. Step-doubling 차이를 근거 없이 rigorous defect로 부르지 않는다.

이것은 실제 REI population stage가 불안정하다는 보고가 아니다. 합성 반례는 'positivity+conservation이면 nonlinear nonexpansion도 자동'이라는 일반 추론만 반박한다. 고차 MPRK 전체를 backward Euler로 바꾼 코드도 아니다. 일반 정리는 명시한 가정 아래의 직접 유도로 제시하고, 유한 Fraction fixture는 부호/식/반례의 정확한 계산 검증으로만 센다.

## 기존 운영 결과의 재확인

Parent의 `XZ_INDEX_REPAIR_WORK_UNIT.json`에는 이미 완료된 LOCAL_CODEX XZ 수정 및 실제 GCC signed-chain/member PASS가 있다. 실제 원인은 마지막 32-byte empty XZ stream이며 첫 stream 출력 4225206 bytes다. 기존 CI job `101505279597`도 읽었고 XZ16/donor18/member15/join5/compat7 성공을 확인했다. 이번 주 대화에서는 새 다운로드나 실제 GCC consumer 재실행을 하지 않았다.

GCC 한 member의 인증 성공은 다른 runtime provider, installed-root, ELF/Rust closure, first interval 또는 provider 승인과 다르다. 최초 한 번의 실패와 소모된 GET/consumer 예산도 그대로 보존한다.

## 검토 및 미검증

동일 assistant의 순차 PHYS-MATH / PHYS-MATH-CODE 검토다. 외부 독립 reviewer가 승인했다고 쓰지 않는다. SciSpace가 찾은 Kopecz–Meister 및 Izgin–Kopecz–Meister 논문은 positivity/order/stability 구분의 방법론 근거다. 이번 resolvent 증명과 합성 반례를 그 논문이 이 REI source에 대해 증명했다고 인용하지 않는다.

NOT_VERIFIED:
- 실제 production MPRK 단계와 이 frozen-resolvent 가정의 대응;
- 실제 원자 rate derivative 및 열/광자 coupled Jacobian bound;
- 네 독립 source site에 대한 실제 stagewise sensitivity;
- full interval, MPFR256 directed-rounding execution 또는 provider.

기존 production source/tests/SSOT/허용오차/물리식은 변경하지 않았다. 장식용 그림이나 exact-zero plot은 생성하지 않았다.

## 다음 한 단계

실제 REI population-stage의 matrix/RHS/Patankar denominator/source-site를 이 정리와 연결하여 적용 가능한 부분과 빠진 항을 식별한다. 주 대화에서 읽을 수 있는 source 대조는 여기서 먼저 진행한다. 보존된 로컬 source나 실제 CAS/JVP가 필요한 부분만 `LOCAL_CODEX_HANDOFF_KO.md`로 넘긴다. 이미 끝난 generic Fraction 검산을 편의상 다시 수행하거나 새 WORK_THREAD를 만들지 않는다.

Codex가 필요하면 동일 scope 안의 research mapping/검산 오류는 직접 고치고 검증한 뒤 `CHATGPT_HANDOFF_KO.md` 및 최소 원본 증거를 Git에 commit/non-force push하여 고정 링크로 주 대화에 직접 반환한다. Production amendment가 필요하면 구체적 원인과 제안만 남기고 보호된 source를 몰래 고치지 않는다.

No BASS/REC/HTT 접근, 새 Snapshot 요청, native xAct 재실행, host 설치/rootfs, Section-0, production ref/lease/worker, first interval/provider admission, ready/merge/force-push.
