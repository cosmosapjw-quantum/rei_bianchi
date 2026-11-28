"""Create-only CLI. Wrong source tier cannot be admitted under any option."""
from pathlib import Path
import argparse,json
from aggregate import read_evaluate

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    result=read_evaluate(a.source)
    with a.output.open('x',encoding='utf-8') as f:
        f.write(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
