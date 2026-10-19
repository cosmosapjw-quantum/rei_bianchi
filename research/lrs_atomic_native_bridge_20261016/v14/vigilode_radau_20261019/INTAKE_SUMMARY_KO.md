# 새 실행 우선 intake — 2026-10-19

## 범위와 결론

rei_bianchi GitHub branch 247개(100+100+47), PR 205개(100+100+5)를 전체 pagination으로 확인했다. VigilODE branch 147개(100+47), PR 71개도 확인했다. 목록 이후 관련 source identity, 실제 stdout/stderr, 종료코드, 원시 결과를 읽었다. REI 원문 13개는 회수 bytes의 Git blob SHA까지 검산했다.

PR198의 확인 HEAD는 fa9615a565a10a770eb1768d8f10cd503b0e1336이고, 새 SSPRK2 NCP 이력을 관측하지 못했다. 기존 original V14 NCP compile/표적시험/smoke/84이력의 완료는 후속 SSPRK2 또는 이번 Radau 실행 완료를 뜻하지 않는다.

관련 백업은 Drive LRS 39개 폴더, Dropbox LRS 38개, VigilODE 관련 3+5개, BASS 27개, age 18개, 관련 dossier 4600경로(8 page, has_more=false)를 확인했다. **Drive RUN15/16의 넓은 상위 폴더는 1000개 제한과 pagination API 부재 때문에 부분 목록이다.** 그 영역은 관련 관측 파일 6개와 대응 Dropbox를 대조했으나 Drive 전체 완전성을 주장하지 않는다. 자세한 원문 metadata는 BACKUP_INTAKE.json에 보존했다.

## 이번에 발견한 관련 결과의 실제 증거와 경계

| 작업 | 실제 확인 | 독립 LRS에 대한 의미 |
|---|---|---|
| PR206 BR05 | source 3588027e41937f331680ab3e5c09de2f327db524; ap_n16_r8 exit0, 41.917962초, 16행, stdout/stderr/receipt와 raw SHA 확인 | 별도 BASS 실행. 다른 5개 비교는 재사용이고 work discrepancy 약2.435e-6은 미해결 |
| PR199 age | age64 blockmax exit0; native 약782.731초, 19,756 RHS. N4 time8은 실제 exit1, 22.150564초; tiny off/on 각 exit0 | 별도 age-reference 결과. N4 실패를 timeout이나 성공으로 바꾸지 않음 |
| PR205 RUN16 | Python response exit0, controller3.769초; gas prefix의 실제 DIVP/point 호출 합331을 확인 | response/prefix 분석이며 full transport 0; 전체 restart/ledger 완료가 아님 |
| PR204 RUN15 | 과거 coupled IVP 원시 파일 유실, transcript만 잔존 | 독립 검증된 native 이력으로 채택하지 않음 |
| VigilODE PR71 | 최신 관측 HEAD 0bab431e1031f86eb3ddb44371240bce49ae2376; 측정 source8a8bd409b1d96c7b7421f496d229e119fd3d284e와 crates/manifests461개 bytes 일치 | 재사용할 실제 Radau API/기반 코드 결정 |

VigilODE run2의 전체 회수 CSV는 2700고유행(2639 ok,54 refused,7 solver failure), SHA256 03eda7909f39c467d1ddce7990dd2707b94a4dbb9bde5e036e21f1cf9435e2fa다. 원래 host/compiler/stdout/process-exit/reference/timing receipt는 재게시되어 있지 않아 **보존 CSV 관측**으로 분류한다. 그 benchmark의 success label을 이 native adapter의 정확도 증거로 전용하지 않는다. Run1 154완료행도 별도로 보존했다.

## 적용 결정

VigilODE의 실제 Radau IIA3, modified Newton, work counters, faer pivoted LU를 새 opt-in native adapter에서 직접 사용한다. faer0.24.4는 기존 pinned dependency로 실제 컴파일된다. diffsol0.17.1, nalgebra0.35.0, ode_solvers0.6.2는 공식 문서와 manifest를 검토했고 이번 adapter에 추가하지 않았다. 세부 API 및 선택 이유는 VIGILODE_NATIVE_API_AND_RUST_PACKAGES.md에 있다. 의존성 이름을 추가한 것만으로 성능 개선을 주장하지 않는다.

## 기록 규칙

현재 intake의 확인 한계와 새 native source/binary/command/outcome을 구분한다. 원시 결과의 재계수, 기존 제조76/Python57 재실행, 별도 production DAG의 진척 승격을 하지 않는다. 새 구현의 실제 컴파일·표적시험·유한 native 결과로 다음 단계를 결정한다.
