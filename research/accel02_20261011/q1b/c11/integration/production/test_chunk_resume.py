"""New journal/chunk orchestration checks; no provider/native trajectory."""
import copy
import tempfile
import unittest
from pathlib import Path
from production_journal import AttemptJournal, JournalError, run_chunk, reconcile_output_records


def cursor():
    return dict(schema='rei.q1b.c11.adaptive_cursor.v1',attempts=5,accepted_macros=3,
                rejected_macros=2,accepted_boundaries=6,accepted_clock_s=4.,next_step_s=2.)


def attempted(c,accepted):
    out=copy.deepcopy(c);out['attempts']+=1;out['next_step_s']=1.
    if accepted:
        out['accepted_macros']+=1;out['accepted_boundaries']+=2;out['accepted_clock_s']+=1.
    else:out['rejected_macros']+=1
    return dict(cursor=out,trial={'accepted':accepted},checkpoint={'generation':out['accepted_macros']})


class Tests(unittest.TestCase):
    def test_rejected_cursor_survives_restart_and_attempts_do_not_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3});seen=[]
            def trial(c,token):seen.append(token);return attempted(c,False)
            one=run_chunk(j,trial,target=100.,total_attempts=105,total_macros=103,new_attempt_cap=1,wall_s=45.)
            self.assertEqual(one['status'],'CHUNK_ATTEMPT_BOUNDARY')
            j=AttemptJournal(d,cursor(),{'generation':3})
            two=run_chunk(j,lambda c,t:attempted(c,True),target=100.,total_attempts=105,total_macros=103,new_attempt_cap=1,wall_s=45.)
            self.assertEqual(two['cursor']['attempts'],7)
            self.assertEqual(two['cursor']['rejected_macros'],3)
            self.assertEqual(two['cursor']['accepted_macros'],4)
            self.assertEqual(seen,[6])

    def test_unfinished_inflight_fails_closed_and_duplicate_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3});j.begin({'expected_t1_s':6.})
            with self.assertRaisesRegex(JournalError,'UNRESOLVED_INFLIGHT'):
                AttemptJournal(d,cursor(),{'generation':3}).resume()
            with self.assertRaisesRegex(JournalError,'INFLIGHT'):
                j.begin({})

    def test_committed_checkpoint_reconciles_without_invoking_trial(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3});j.begin({})
            receipt=attempted(cursor(),True)
            j=AttemptJournal(d,cursor(),{'generation':3})
            j.resume(lambda begin:receipt)
            self.assertEqual(j.head['cursor']['attempts'],6)
            self.assertTrue((Path(d)/'attempt-00000006.commit.json').exists())
            with self.assertRaisesRegex(JournalError,'NO_INFLIGHT'):
                j.commit(receipt)

    def test_wall_budget_checked_before_next_trial_and_global_cap_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3});clock=iter([0.,0.,46.])
            calls=[]
            result=run_chunk(j,lambda c,t:(calls.append(t) or attempted(c,False)),target=100.,
                total_attempts=105,total_macros=103,new_attempt_cap=3,wall_s=45.,clock=lambda:next(clock))
            self.assertEqual(result['status'],'CHUNK_WALL_BOUNDARY');self.assertEqual(calls,[6])
            result=run_chunk(j,lambda c,t:self.fail('allocation must stop before trial'),target=100.,
                total_attempts=6,total_macros=103,new_attempt_cap=3,wall_s=45.)
            self.assertEqual(result['status'],'ALLOCATION_EXHAUSTED')

    def test_output_history_restores_lost_row_and_rejects_mutated_same_clock_keys(self):
        with tempfile.TemporaryDirectory() as d:
            record=dict(epoch_index=1,time_s=8.,fields={'xHII':.25},state_sha256='a'*64)
            reconcile_output_records(d,[record])
            path=Path(d)/'epoch-001.json';original=path.read_bytes();path.unlink()
            reconcile_output_records(d,[record]);self.assertEqual(path.read_bytes(),original)
            import json
            changed=copy.deepcopy(record);changed['fields']['xHII']=.5
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(JournalError,'IMMUTABLE_RECORD_MISMATCH'):
                reconcile_output_records(d,[record])

    def test_exception_after_atomic_acceptance_reconciles_without_replay(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3});durable=[];calls=[]
            def publish_then_fail(c,t):
                calls.append(t);durable.append(attempted(c,True))
                raise OSError('row-publication-failed-after-checkpoint')
            result=run_chunk(j,publish_then_fail,target=100.,total_attempts=105,total_macros=103,
                new_attempt_cap=3,wall_s=45.,reconcile=lambda begin:durable[0])
            self.assertEqual(result['status'],'CHUNK_RECOVERED_COMMIT_BOUNDARY')
            self.assertEqual(result['cursor']['attempts'],6)
            self.assertEqual(result['cursor']['accepted_macros'],4)
            self.assertEqual(calls,[6])
            self.assertTrue((Path(d)/'attempt-00000006.exception.json').exists())
            self.assertFalse((Path(d)/'attempt-00000006.failure.json').exists())
            self.assertEqual(AttemptJournal(d,cursor(),{'generation':3}).resume()['cursor'],result['cursor'])

    def test_failure_is_retained_and_prevents_implicit_replay(self):
        with tempfile.TemporaryDirectory() as d:
            j=AttemptJournal(d,cursor(),{'generation':3})
            def fail(c,t):raise ArithmeticError('physical-map-failure')
            result=run_chunk(j,fail,target=100.,total_attempts=105,total_macros=103,new_attempt_cap=3,wall_s=45.)
            self.assertEqual(result['status'],'FAILED_ATTEMPT');self.assertEqual(result['cursor'],cursor())
            with self.assertRaisesRegex(JournalError,'FAILED_ATTEMPT'):
                AttemptJournal(d,cursor(),{'generation':3}).resume()

if __name__=='__main__':unittest.main()
