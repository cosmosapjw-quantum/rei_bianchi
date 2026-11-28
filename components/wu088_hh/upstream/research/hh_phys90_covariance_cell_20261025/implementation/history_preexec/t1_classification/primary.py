#!/usr/bin/env python3
"""One frozen PHYS90 primary; resume branches before any scientific import."""
import sys
sys.dont_write_bytecode=True
import json
from evidence import UNIT,REPO,identity,resume,fresh,publish,main_args

def compute():
    from fractions import Fraction as Q
    from kernel import load_inputs,PairTable,bracket,fixtures,guards,support
    contract=json.loads((UNIT/'CONTRACT.json').read_text())
    F,H=load_inputs(REPO,contract);table=PairTable(F,H)
    assert table.n==153 and len(table.pairs)==11628
    bound,checkpoints=bracket(table)
    fixture=fixtures();guard=guards()
    # Fixed sparse algebraic envelope probes, never actual consumer rate weights.
    probes=[('e0_minus_e10',{0:1,10:-1},{0:1,10:-1},Q(-1,10**10)),
            ('e0_cross_e10',{0:1},{10:1},Q(1069643,2500000000))]
    directions={}
    for name,left,right,reused_center in probes:
        u=[Q(left.get(i,0)) for i in range(153)]
        v=[Q(right.get(i,0)) for i in range(153)]
        directions[name]={'center':reused_center,'center_status':'REUSED_PARENT_EXACT_VALUE',
                          'center_provenance':'PHYS89 FINAL_REPORT and primary MATRIX_DIAGNOSTIC / SOURCE_TABLE',
                          'radius_at_t1':support(H,u,v),
                          'box_interval_at_t1':[reused_center-support(H,u,v),reused_center+support(H,u,v)],
                          'left_indices_and_coefficients':{str(k):v for k,v in left.items()},
                          'right_indices_and_coefficients':{str(k):v for k,v in right.items()}}
    a=F[0][0];d=Q(1,10**10)
    special_threshold=2*a/(4*a-d)
    assert F[10][10]==a-d and F[0][10]==a and H[0][0]==H[0][10]==H[10][10]==d/2
    pairscan={'n':153,'pairs':11628,'singletons':153,'upper_entries':11781,
              't0':checkpoints[0],'t1':checkpoints[1],'bracket':bound,'checkpoints':checkpoints,
              'known_0_10_threshold':special_threshold,'integer_unit_denominator':table.scale}
    results={'scope':'FINITE_CONDITIONAL_FORMATTING_CELL_AND_MANUFACTURED_CONSUMER_ENVELOPE',
             'pair_threshold':bound,'at_t0_failed_pairs':checkpoints[0]['failed_pair_count'],
             'at_t1_failed_pairs':checkpoints[1]['failed_pair_count'],
             'at_t0_failed_singletons':checkpoints[0]['failed_singleton_count'],
             'at_t1_failed_singletons':checkpoints[1]['failed_singleton_count'],
             'actual_source_algebraic_probes':directions,'full_PSD_compatibility':'UNRESOLVED',
             'actual_consumer_ACK':None,'physical_CI':False,'actual_matrix_repair':False,
             'halfULP':'CONDITIONAL_NEAREST_FORMATTING_MODEL_NOT_SOURCE_GUARANTEE',
             'HH_R10':'OFF','production':'NOT_ISSUED','parent_status':'PARTIAL_INPUT_DEPENDENCIES'}
    # Presentation floats only; all assertions and saved conclusions above are exact.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    pts=sorted({(c['t'],c['failed_pair_count']) for c in checkpoints})
    fig,ax=plt.subplots(figsize=(7.0,4.0),layout='constrained')
    ax.step([float(p[0]) for p in pts],[p[1] for p in pts],where='post',color='#175b96')
    ax.set(xlabel='Conditional cell radius t (decimal presentation)',ylabel='Failed 2×2 pair conditions',
           title='PHYS90 exact pair-condition checkpoints')
    ax.grid(alpha=.2)
    ax.text(.98,.96,'Pair feasibility does not certify full PSD',transform=ax.transAxes,
            ha='right',va='top',fontsize=9)
    images={}
    for ext in ('png','pdf'):
        stream=BytesIO();fig.savefig(stream,format=ext,dpi=170);images['PAIR_CHECKPOINTS.'+ext]=stream.getvalue()
    plt.close(fig)
    return {'RESULTS.json':results,'PAIR_SCAN.json':pairscan,'CONSUMER_ENVELOPE_FIXTURES.json':fixture,
            'GUARDS.json':guard,**images}

def main():
    args=main_args('primary');binding=identity()
    if args.resume:
        print(json.dumps(resume(args.output,'primary',binding)));return
    output=fresh(args.output)
    publish(output,'primary',binding,compute())
    print(json.dumps({'status':'COMPLETE','kind':'primary','identity':binding['sha256']}))
if __name__=='__main__':main()
