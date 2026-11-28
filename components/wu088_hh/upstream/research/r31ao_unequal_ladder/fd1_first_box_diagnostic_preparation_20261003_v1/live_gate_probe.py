from support import *
from diagnostic_adapter import live_gate
import copy
proposal=c.load(OLD/'fd1_prep_20261003_v2/evidence/DIAGNOSTIC_PROPOSAL.json');c.check_seal(proposal,'proposal_sha256')
probe=copy.deepcopy(proposal)
probe['future_resource_policy']['unit']='wu088-fd1-live-policy-probe-v3.service'
probe['future_resource_policy']['outside_observation_file']=str(E/'LIVE_GATE_PROBE_OUTSIDE.json')
live=live_gate(probe)
write(E/'LIVE_POLICY_PROBE.json',dict(status='PASS',proposal_self_sha256=proposal['proposal_sha256'],metadata_only_probe=True,temporary_probe_unit_name=probe['future_resource_policy']['unit'],proposal_file_unchanged=True,live=live,HH_evaluations=0,integrations=0,scope_consumed=False,run_authorized_called=False))
print('Actual future live gate PASS; HH=0, integrations=0, consumption=0')
