# HE-F2 실제 소비기 호환성 전달물

실행: Python3.10이상, runtime표준라이브러리와동봉된고정HE-F1모듈만사용한다.
현재모형은전하교환을제외하므로출력은일관되게BLOCKED_CONSUMER_CONTRACT/no-injection이다.
새원자반응률API나독립consumer solver가아니다.

```bash
python -B he_f2_binding.py --root . --out /tmp/he-f2-new-output
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  python -W error -m pytest -q -p no:cacheprovider tests
```

출력디렉터리는미존재여야하며부모디렉터리는있어야한다. 실패시기존파일을덮어쓰지않는다.
exit0은보고서생성성공일뿐모형수락이아니다. HE-F2상태는CONSUMER_LEDGER_ACCEPTANCE.json을읽는다.
원B3의thermal-rate packet을소비기연구schema로옮기되원packet전체를보존한다.
source합산·범위밖외삽·밀도곱·열/광자closure·소비기코드변경은실행하지않는다.

inputs/는현재고정commit의관련FT03원본과HE-F1요청,공통DAG/schema이며INPUT_LOCK.json으로확인한다.
FT03자료는원실험의candidate/controlled모형증거다. 원자료의physicaladmission은여전히false다.
전체원논문이나oldscientificsuite를동봉/실행하지않는다.
Git에게시된요약/전달물은ZIP의일부일수있다. 재현은전체ZIP과명시된검증의존성으로수행한다.
새wheel은없고기존HE-F1runtime8파일을byte그대로보존했다.
