from __future__ import annotations
import json
from pathlib import Path

STAGE=Path(__file__).resolve().parents[1]
VERDICT=(
 'DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_R1_'
 'FOUR_SITE_PRIMAL_PARITY_AND_LOCAL_IMPLICIT_CERTIFICATES_PASS_'
 'CROSS_SITE_STATE_FEEDBACK_REMAINDER_EVENT_RESTART_AND_SET_LEDGER_UNCLOSED'
)
NEXT=(
 'P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-R1-'
 'CROSS-SITE-STATE-FEEDBACK-REMAINDER-AND-TABLE-EVENT-LOCK'
)

def test_final_stage_contract_is_fail_closed_at_the_actual_blocker():
 result=json.loads((STAGE/'results.json').read_text())
 state=json.loads((STAGE/'STAGE_STATE.json').read_text())
 assert result['verdict']==VERDICT
 assert state['verdict']==VERDICT
 assert result['completed'] is True and state['completed'] is True
 assert result['four_site_primal_parity_pass'] is True
 assert result['all_local_population_certificates_pass'] is True
 assert result['all_local_thermal_root_certificates_pass'] is True
 assert result['continuous_discrete_map_enclosure_certified'] is False
 assert result['production_history_authorized'] is False
 assert result['next_stage']==NEXT and state['next_stage']==NEXT

def test_public_authorizations_remain_closed():
 result=json.loads((STAGE/'results.json').read_text())
 for key in ('production_node_chemistry_authorized','R2C_R2_authorized','B2C2B_authorized'):
  assert result[key] is False
