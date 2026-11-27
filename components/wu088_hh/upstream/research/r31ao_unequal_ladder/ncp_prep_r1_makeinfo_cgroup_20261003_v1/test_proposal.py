import unittest,hashlib,json
try: from proposal import seal_proposal
except ModuleNotFoundError: seal_proposal=None
class ProposalSafety(unittest.TestCase):
 def test_helper_exists(self):self.assertIsNotNone(seal_proposal,'dispatch-free helper not implemented')
 def test_no_authority_no_consumption_seal(self):
  self.assertIsNotNone(seal_proposal)
  p=seal_proposal({'verified':True,'scope_consumed':False,'source':'fixture-nonscience'})
  self.assertTrue(p['not_authorization']);self.assertFalse(p['scope_consumed']);self.assertEqual(p['science_dispatch_count'],0)
  body={k:v for k,v in p.items() if k!='proposal_sha256'}
  self.assertEqual(p['proposal_sha256'],hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest())
 def test_consumed_or_unverified_refused(self):
  self.assertIsNotNone(seal_proposal)
  for x in ({'verified':False,'scope_consumed':False},{'verified':True,'scope_consumed':True}):
   with self.assertRaises(ValueError):seal_proposal(x)
if __name__=='__main__':unittest.main()
