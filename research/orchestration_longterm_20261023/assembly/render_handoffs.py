#!/usr/bin/env python3
"""Render reviewable handoffs from unchanged authority node fields."""
import json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'assembly'
d=json.loads((OUT/'DAG.json').read_text());groups=collections.defaultdict(list)
for n in d['nodes']:groups[n['repository']].append(n)
header='# 장기 연구 PR 계획\n\n이 문서는 동결된 저장소별 계획의 기계적 조립본이다. 계획을 실행 완료·물리적 승인으로 해석하지 않는다. 각 작업은 원 저자 계약, 소스, 적용 영역, 예산 및 보류 조건을 그대로 따른다. 기존 소유자 브랜치에 합치거나 중복 계산을 시작하지 않는다.\n\n'
plans=[header]
for repo,ns in groups.items():
 name=repo.split('/')[-1];lines=[f'# {repo} 인수인계\n', '중앙 경로: `cosmosapjw-quantum/rei_bianchi`, 브랜치 [research/orchestration-sandbox-20261022](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/research/orchestration-sandbox-20261022), `research/orchestration_longterm_20261023/`.\n', '첫 행동: 동결 계약을 읽고 진행 중인 소유자 결과와 실제 잔여 예산을 확인한다. 완료 근거를 재사용하며 예산·실패 기록을 초기화하지 않는다. 이 문서는 새로운 과학적 판정을 추가하지 않는다.\n']
 authorities=[a for a in d['authorities'] if any(n['authority']==a['path'] for n in ns)]
 pins={a['path']:{k:v for k,v in a['document'].items() if k!='nodes'} for a in authorities}
 lines.append('현재 소스 핀·예약·자원 정책(원본 계약 기준):\n\n```json\n'+json.dumps(pins,ensure_ascii=False,indent=2)+'\n```\n')
 plans.append(f'## {repo}\n\n| 노드 | 계획 상태 | 선행 노드 | 계약 |\n|---|---|---|---|\n')
 for n in ns:
  c=n['contract'];deps=', '.join(n['local_dependencies']) or '내부 없음';ext=json.dumps(n['external_dependencies'],ensure_ascii=False);cond=json.dumps(n.get('conditional_dependencies',[]),ensure_ascii=False)
  schedule=deps+'; 외부: '+ext+'; 조건부: '+cond
  plans.append(f"| {n['id']} | {n['plan_status']} | {schedule} | `{n['authority']}{n['authority_pointer']}` |\n")
  lines += [f"\n## {n['id']}\n",f"원본: `{n['authority']}{n['authority_pointer']}`. 내부 선행: {deps}. 외부 선행: `{ext}`. 조건부 선행: `{cond}`.\n",'원 저자 계약(변경 없음):\n\n```json\n'+json.dumps(c,ensure_ascii=False,indent=2)+'\n```\n']
 local_ids={n['id'] for n in ns}
 lines.append('\n## 저장소 간 조건부 연결\n\n채널을 선택할 때만 해당 공급자 조건을 적용한다. 모든 공급자의 동시 완료를 요구하지 않는다.\n')
 for edge in (d.get('integration') or {}).get('edges',[]):
  if edge['from'] in local_ids or edge['to'] in local_ids:lines.append('\n- `'+edge['from']+'` → `'+edge['to']+'`: '+edge['condition']+'. '+edge['claim_limit']+'\n')
 (OUT/f'HANDOFF_{name}_KO.md').write_text('\n'.join(lines))
 plans.append('\n')
integration=d.get('integration') or {}
plans.append('## 저장소 간 조건부 연결\n\n이 표는 채널 선택에 따른 선행 조건이다. 모든 공급자를 동시에 요구하는 AND 조건으로 해석하지 않는다.\n\n| 공급 노드 | 소비 노드 | 적용 조건 | 주장 한계 |\n|---|---|---|---|\n')
for edge in integration.get('edges',[]):plans.append('| '+edge['from']+' | '+edge['to']+' | '+edge['condition']+' | '+edge['claim_limit']+' |\n')
plans.append('\n```json\n'+json.dumps(integration.get('dependency_interpretation'),ensure_ascii=False,indent=2)+'\n```\n')
(OUT/'PR_PLANS_KO.md').write_text(''.join(plans))
print(json.dumps({'repositories':len(groups),'handoffs':len(groups),'nodes':len(d['nodes'])}))
