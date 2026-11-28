"""Static pre-rotation Eq50 support audit, independent of numerical Delta values."""
import argparse, hashlib, json, pathlib
import numpy as np
from arseny_reimpl.eq50_scoped import ordered_scoped_branches, branch_state_indices
from arseny_reimpl.state_index import enumerate_states
from audit_support import EVENTS, BRANCH_NAMES
from run_equivalence import atomic


def main(out, results, repo):
    repo=pathlib.Path(repo)
    branches=ordered_scoped_branches()
    assert [b.name for b in branches]==list(BRANCH_NAMES)
    computed=[(branch_state_indices(b)[0]-1,branch_state_indices(b)[1]-1,b.state_b[0]==3) for b in branches]
    assert computed==list(EVENTS)
    reachable={2}
    history=[{'stage':'initial','reachable_indices_zero_based':sorted(reachable)}]
    for b,(i,j,sink) in reversed(list(zip(branches,computed))):
        before=reachable.copy()
        if i in before:reachable.add(j)
        if not sink and j in before:reachable.add(i)
        history.append({'stage':'approach_'+b.name,'event':[i,j,sink],
                        'reachable_indices_zero_based':sorted(reachable)})
    positive_m=sorted(j-1 for j,N,l,m in enumerate_states(3) if m>0)
    assert not reachable.intersection(positive_m)
    rows=json.loads(pathlib.Path(results).read_text())['records']
    maxima={str(l):max(float(np.max(abs(np.array(x['author_reduced_probability'])[:,0]-
                                    np.array(x['clean_collapsed_probability'])[:,0])))
                        for x in rows if x['l']==l) for l in (1,2)}
    assert max(maxima.values())<1e-8
    result={'schema':'bass_he.r10i.pre_rotation_reachability.v1',
            'branch_order':[b.name for b in branches], 'event_order':computed,
            'approach_order':[b.name for b in reversed(branches)],
            'history':history,'pre_rotation_possible_indices_zero_based':sorted(reachable),
            'positive_m_indices_zero_based':positive_m,
            'positive_m_reachable':False,'all_pre_rotation_rotational_inputs_have_m0':True,
            'max_author_clean_consumed_m0_column_difference_by_l':maxima,
            'full_matrix_verdict':'WRN_BASIS_NOT_EQUIVALENT',
            'current_transport_subspace':'NUMERICALLY_EQUIVALENT_FOR_PINNED_INITIAL_STATE_AND_EVENTS',
            'limitation':'Reachability uses this Nmax=3, five-branch initial-state topology; it does not prove equivalence for arbitrary initial channel or event list.',
            'source_identity_sha256':hashlib.sha256((repo/'src/arseny_reimpl/eq50_scoped.py').read_bytes()).hexdigest()}
    atomic(out,result)
    print(json.dumps({'reachable':sorted(reachable),'positive_m':positive_m,'m0_max':maxima},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--results',required=True);p.add_argument('--repo',required=True)
    x=p.parse_args();main(x.out,x.results,x.repo)
