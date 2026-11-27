# E13C3 decisions

1. 부모 NEXT_DAG에 따라 E13C3 한 노드를 실행했다. Source/gas/model은 고정하고 저장된 E13C2 reference만 읽었다.
2. Exact frozen damping과 Fubini moment kernels를 채택했다. 작은 optical depth를 전제하지 않되 GL 정확도는 현재 범위에서 수치 검증했다.
3. PLAN.json의 1% signed heat-defect 진단, absolute floors, GL 및 독립 일치 기준을 실행 전에 고정했다. 결과를 본 뒤 완화하지 않았다.
4. 주 구현은 longdouble GL8/12, 독립 contributor는 Decimal70 GL12/20. 공유한 coefficient helper를 공개하고 final decision reviewer를 분리했다.
5. Local104PASS 뒤에만 first2 확장했다. Incoming correction을 초기화하지 않았다.
6. 이론 문서의 captured/exact midpoint 구별과 Lipschitz mismatch 항을 명시했다. 수식 가정을 정리한 문서 수정으로, producer나 결과를 바꾸지 않았다.
7. 결과 최대값이 macro aggregate라는 단위를 첫 문단에도 표시했다.
8. 1차 ledger closure, original-model residual, numerical accuracy, physical accuracy budget을 구별했다.
9. 다음 작업은 local validated remainder enclosure. 신뢰할 물리 budget 정의와 actual atomic moments는 별도 owner/input gate다.
10. 게시·저장은 기존 허용된 same-branch additive, non-force, create-only 범위. 실 commit/backup 증거는 detached delivery receipt에 남긴다.

11. 독립 검토 REPRO-01에 따라 optional recompute의 새 출력 parity/accuracy는 미판정임을 machine-readable field와 문서에 명시했다. Saved-evidence verdict를 fresh scientific validation으로 확대하지 않는다.
