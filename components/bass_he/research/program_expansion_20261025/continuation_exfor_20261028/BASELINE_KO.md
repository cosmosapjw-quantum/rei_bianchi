# EXFOR11 재개 기준

HARMONIC10의 최종 외부 인계 네 문서와 최종 source를 실제로 읽고 복원했다. 과거 완료 계산·시험·CAS·plot·백업의 재실행은0이다.

- 기존 source P10: a73773a9e1056bf18405453a0e88b9d12a15e9ac
- 기존 exact tree:4e308ea37c6907f6b0064951e71d14667831a6a3
- 과거 local D10:136c93b9aff4f742d5d720032a7da94acbaa3e47
- 이전 중앙:f55c0d4612369f1a8257a88cba447a5ccfaf1ef6; 현재 조사 중앙:df806909aee8f25efcfa4faeefca77a5271f546c
- HARMONIC10 COMPLETE_SCOPED, ACCEPT_SCOPED_SECOND_HARMONIC_REFERENCE.
- 최초24PASS+1FAIL와targeted1PASS,repairreserve0 보존.

이번 로컬 디렉터리는87개 HARMONIC10 source 파일과4개 의존성/AGENTS를 복원한 source mirror다. 전체Gitcheckout이나 과거localD10이라고 부르지 않는다. 새 실행은 실제 새sourcepublicationSHA와 실행소스·의존성SHA256으로 고정한다. 원격tree는 P10 전체base에 새EXFOR11경로만 더하므로 과거·다른owner의파일을 보존한다.

새과학단위는 EXFOR11 하나다. Local시작10complete+1partial+3physicalopen+1pending/15,central28/88,delta0. 원kinematic08partial와열린3물리입력을 지우지 않는다.

Python현재실행probe는3.12.14 PYTHON_PASS. Wolframcontext조회는 SERVICE_ERROR이며 evaluator실행능력·전체runtime에 대한 결론이 아니다. 개인대화검색은root의현재호출에서성공했고 별도surveyagent의unavailable응답과시점을구별한다.

새분석은공식EXFOR12점의선언된±ERR-S windows에서 positiveevenBernstein족의같은사건검출기수용률범위를계산한다. 원정규화배율은ratio에서소거되지만각도별targetresponse와실제flux/deposition은남는다.

