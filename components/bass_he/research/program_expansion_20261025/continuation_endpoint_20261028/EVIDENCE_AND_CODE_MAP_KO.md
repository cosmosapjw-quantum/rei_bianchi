# R2/C2 — 원전·재사용·식에서 코드까지

## 입력의 의미와 identity
공식 M0475의 M0475002는 He4(g,d)d DCS다.330MeV 네 점의 nominal theta_cm와 coordinate ERR-S 창만 새 계산에 넣는다. M0475003의 여섯 total점은 다른 energy grid이므로 joins=0이다. 공식 원문과 QUARTIC12 SAVED_PLOT_DATA.json의 SHA256은 CONTRACT.md에 고정했다. 새 코드는 둘을 실제 읽어 identity 및 필요한 literal rows를 확인한다.

QUARTIC12의 certified nominal Z interval,330MeV geometry monomial moments, endpoint-zero quartic EMPTY_OUTER를 재사용한다. 원래 각도 root·geometry·이전 polynomial enumeration을 재실행하지 않는다. TANGENT13의 source/closeout/failurehistory는 현재 시작점이다. T13minimum solved status와 Q12maximum tightness를 최신본문에서 확인해, 반복최적화가 아닌degree6endpointfamily를선택했다.

## 이번 최신 조사
관련7repo1450heads/18terminalpages, 신규6/이동8/삭제0. state=all PR240records/8pages에서updated>=2026-10-22 해당171개를읽었고날짜경계이전행까지조회했다. 선별PR13sections,commit15bodies,과학source16files,현행AGENTS2files를읽었다. CR의C07→C08변화는조회시점을분리했다.
Library는이전완료조사이후62metadata/1terminal,선택8전체문서/10readwindows. Dropboxdossier5337/9terminal및BASS_BACKUPS344/1terminal. Drive문서delta1/1terminal,HEarchivefolder1000cap. Privatecontext는실제1회SERVICE_ERROR. metadata열거·본문읽기·역사적조사재사용을각각기록했다. 전체Drive/전체privatechat접근을확보한것으로확장하지않는다.

sources/github/,backups/,literature/는게시가능한요약·출처표다. rawprivateinventory와제3자논문fulltext는게시하지않는다. 새Exa검색6회/요청32결과,fetch2회/6URLs,SciSpace3회/30papers. 최초proton-triton검색오류는공식반응확인후dd로교정했고잘못된채널에서과학입력채택0을보존했다.

## 원전과 이번 유도의 관계
IAEA EXFOR원문은네DCS창의직접입력이다. Arends1976publisher는metadata/fulltext제한까지읽었고,Rice2000APSabstract와Silverman1984inverse-reactionabstract를읽었다. Rice의낮은energybins에서sin²theta/E2논의는330MeVdegree6law의입증으로쓰지않는다. Nie/Demmel저자PDF§2의intervalpositivepolynomial연결을읽었으며이번quadratic positivity는끝점·stationarypoint로직접증명한다. 상세접근범위와URL은sources/literature/PRIMARY_SUPPORT_KO.md가관리한다.

## 식–구현 대응
| 수학 객체 | 새 구현 책임 | 입력·결과 |
|---|---|---|
| q=(1-z)r, signed a | src/endpoint14.py | a→cubic b, exact global r minimum, D |
| true nominal row c_j=(1-z)z^j | 같은 producer | saved Z→interval/midpoint/epsilon→contracted/expanded rows |
| same-event threshold topology | root THEORY.md + producer compatibility | rational K<0; saved k0→t interval→new weighted moments |
| fixed N1/4/16 positivity sandwich | producer exhaustive triples |6matrix/RHS/vertex certificates 및counts |
| signed aperture fractional bounds | producer | raw/clippedrange,min/maxbracket,feasiblewitness |
| independent certificate validation | src/verify_certificate.py | saved JSON과immutableinputs; candidate search/enumeration0 |
| actual campaign | scripts/campaign.py,run_once.py | S05pin→oneconstruction/tests/reader/resource |
| figure | scripts/plot_saved.py | savedcurve/intervals만읽기,scienceimports/calls0 |

실제함수와호출흐름은IMPLEMENTATION.md와source를함께읽는다. 문서존재를실행성공으로세지않는다. 독립검토자는계약과원자료를받아source→actualoutput→figure→finalclaim을이어검토한다.
