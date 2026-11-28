"""Dispatch-free proposal seal; this module contains no execution adapter calls."""
import hashlib,json

def seal_proposal(evidence):
 if evidence.get('verified') is not True or evidence.get('scope_consumed') is not False:
  raise ValueError('verified, unconsumed evidence required')
 body=dict(evidence,schema='WU088_NCP_NONDISPATCH_BINDING_PROPOSAL_R1',not_authorization=True,scope_consumed=False,science_dispatch_count=0)
 body['proposal_sha256']=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
 return body
