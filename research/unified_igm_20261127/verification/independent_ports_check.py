"""Independent finite checks of donor port and single-owner science. Depends on the REI source tree via PYTHONPATH."""
import csv
import itertools
import json
import math
from fractions import Fraction as Q
from pathlib import Path
from rei_bianchi.microphysics import hh, he, cr


def independently_check_he_polytope():
    chi_h, chi_he, e, ev_j = map(Q, ('13.598434599702', '24.587389011','40.813320','1.602176634e-12'))
    weights = {'heat_erg': ((e - chi_h)*ev_j, (e - chi_he)*ev_j, Q(0)), 'binding_erg': (chi_h*ev_j, chi_he*ev_j, Q(0)), 'escaped_erg':(Q(0),Q(0),e*ev_j)}
    checked=empty=0
    for limits in itertools.product(((0,1),(1,4),(2,2)), repeat=3):
        for total in [(0,2),(2,4),(3,5),(5,6),(7,12)]:
            assignments=[ns for ns in itertools.product(*(range(l, r+1) for l,r in limits)) if total[0]<=sum(ns)<=total[1]]
            try: output=he.correlated_partition_bounds(total,*limits)
            except ValueError:
                assert not assignments;empty+=1;continue
            assert assignments
            for name, ws in weights.items():
                vals=[sum(w*n for w,n in zip(ws,ns)) for ns in assignments]
                # Integer polytope vertices: every active sum-plane constrains at most one remaining coordinate, so exhaustive integer enumeration captures extremes.
                assert output[name]==(min(vals),max(vals))
            checked+=1
    return {'nonempty_boxes':checked,'empty_boxes':empty}


def hh_checks():
    stages=[(1000., 1., 3., 2., 0.), (1000., 1.,0.,0.,1.), (1000., 0.,0.,0.,0.)]
    signs=[]
    for row in stages:
        s=hh.charge_exchange_source(*row)
        assert s.hi_rate_cm3_s+s.hii_rate_cm3_s==0
        assert s.di_rate_cm3_s+s.dii_rate_cm3_s==0
        assert s.hii_rate_cm3_s+s.dii_rate_cm3_s-s.electron_rate_cm3_s==0
        assert s.gas_power_erg_cm3_s+s.binding_power_erg_cm3_s==0
        signs.append(1 if s.gas_power_erg_cm3_s>0 else -1 if s.gas_power_erg_cm3_s<0 else 0)
    assert signs==[-1,1,0]
    return signs


def cr_checks():
    data=cr.axbi_snapshots(); row=data['rows']['SHEAR_PLUS']; report=cr.snapshot_primary_ionization(row,energy_order=16,age_order=4,mu_order=4)
    bind=report['binding_power_J_m3_s']; birth=report['fast_electron_birth_power_J_m3_s']; loss=report['modeled_proton_loss_J_m3_s']; off=report['threshold_model_offset_J_m3_s']
    assert loss>0 and abs(bind+birth+off-loss)/loss<1e-12
    assert abs(bind+birth-loss)/loss>1e-7
    zero=cr.snapshot_primary_ionization(row,enabled=False,energy_order=16,age_order=4,mu_order=4)
    assert zero['modeled_proton_loss_J_m3_s']==0
    return {'rudd_loss':loss,'host_binding':bind,'secondary_kinetic':birth,'threshold_offset':off,'missing_fraction_if_dropped':off/loss,'off_modeled_loss':zero['modeled_proton_loss_J_m3_s']}

if __name__=='__main__': print(json.dumps({'HE':independently_check_he_polytope(),'HH':hh_checks(),'CR':cr_checks()},sort_keys=True,indent=2))
