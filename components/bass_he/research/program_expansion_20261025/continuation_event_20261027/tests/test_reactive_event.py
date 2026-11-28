"""Independent finite CM event controls for the new reactive map only."""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import reactive_event as ev

COSINES = (-0.6,0.2,0.8)
WEIGHTS = (0.3,0.4,0.3)
SIGMA = 2e-19
ANGULAR = ev.AngularTransport(SIGMA,
    SIGMA*math.fsum(w*(1-c) for c,w in zip(COSINES,WEIGHTS)),
    SIGMA*math.fsum(w*1.5*(1-c*c) for c,w in zip(COSINES,WEIGHTS)))


def fixture(*, masses=(2e-27,3e-27,1e-27,4e-27), delta_fraction=0.2,
            va=(2000.0,-300.0,800.0), vb=(-200.0,500.0,-100.0), outgoing=("c","d")):
    mass=dict(zip(("a","b",*outgoing),masses))
    mu=masses[0]*masses[1]/(masses[0]+masses[1])
    energy=0.5*mu*math.fsum((x-y)**2 for x,y in zip(va,vb))
    eps={i:0.0 for i in mass}
    if outgoing==("c","d"):
        eps['c']=delta_fraction*energy
    source=ev.ReactiveSource("synthetic-discrete-angle","synthetic:finite-positive-measure:v1",("a","b"),outgoing,
        0.0,1e100,True,True,"labelled_pair_once","constant_compositional_inertial_mass",
        "explicit_nonrel_internal_energy_separate_from_inertial_mass","population_derived_internal_witness")
    return dict(source=source,mass_kg=mass,internal_energy_j=eps,velocity_a_m_s=va,
                velocity_b_m_s=vb,angular=ANGULAR,purpose="conditional_algebra")


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def norm(v):
    length=math.sqrt(math.fsum(x*x for x in v))
    return tuple(x/length for x in v)


def oracle(args, cosines=COSINES, weights=WEIGHTS, sigma=SIGMA):
    """Construct actual outgoing velocities, independent of moment formulas."""
    source=args['source']; ids=source.incoming_ids+source.outgoing_ids
    ma,mb,mc,md=(args['mass_kg'][i] for i in ids)
    va,vb=args['velocity_a_m_s'],args['velocity_b_m_s']
    mass=ma+mb; mu=ma*mb/mass; muout=mc*md/mass
    g=tuple(x-y for x,y in zip(va,vb)); speed=math.sqrt(math.fsum(x*x for x in g))
    axis=norm(g) if speed else (0.0,0.0,1.0)
    helper=(0.0,0.0,1.0) if abs(axis[2])<0.8 else (1.0,0.0,0.0)
    first=norm(cross(axis,helper)); second=cross(axis,first)
    com=tuple((ma*x+mb*y)/mass for x,y in zip(va,vb))
    eps=args['internal_energy_j']; delta=math.fsum((eps[ids[2]],eps[ids[3]],-eps[ids[0]],-eps[ids[1]]))
    outenergy=0.5*mu*speed**2-delta
    impulse=math.sqrt(2*muout*max(0.0,outenergy))
    contributions={i:[[] for _ in range(15)] for i in dict.fromkeys(ids)}
    for cosine,weight in zip(cosines,weights):
        for k in range(4):
            phi=k*math.pi/2
            direction=tuple(cosine*axis[j]+math.sqrt(1-cosine*cosine)*(math.cos(phi)*first[j]+math.sin(phi)*second[j]) for j in range(3))
            vc=tuple(com[j]+impulse/mc*direction[j] for j in range(3))
            vd=tuple(com[j]-impulse/md*direction[j] for j in range(3))
            measure=sigma*weight/4
            for identifier,sign,m,v in zip(ids,(-1,-1,1,1),(ma,mb,mc,md),(va,vb,vc,vd)):
                values=[1.0,m,*[m*x for x in v],0.5*m*math.fsum(x*x for x in v),*[m*v[i]*v[j] for i in range(3) for j in range(3)]]
                # Fifteen components: number, mass, 3 momentum, kinetic, 9 tensor.
                for terms,value in zip(contributions[identifier],values):terms.append(sign*measure*value)
    return {i:([math.fsum(t) for t in rows],[math.fsum(abs(x) for x in t) for t in rows]) for i,rows in contributions.items()}


def flatten(row):
    return [row.number_m2,row.mass_kg_m2,*row.momentum_kg_m3_s,row.kinetic_j_m2,*[x for r in row.second_j_m2 for x in r]]


class ReactiveTests(unittest.TestCase):
    def close(self,actual,expected,scale):
        self.assertLessEqual(abs(actual-expected),5e-13*scale,(actual,expected,scale))

    def check_oracle(self,args,cosines=COSINES,weights=WEIGHTS,sigma=SIGMA):
        result=ev.reactive_moment_kernel(**args)
        reference=oracle(args,cosines,weights,sigma)
        for identifier,row in result.species.items():
            values,scales=reference[identifier]
            for actual,expected,scale in zip(flatten(row),values,scales):self.close(actual,expected,scale)
        return result,reference

    def test_direct_discrete_angle_four_azimuth(self):
        self.check_oracle(fixture())

    def test_exact_reactive_sanity_control(self):
        args=fixture(masses=(1.0,3.0,2.0,2.0),va=(4.0,0.0,0.0),vb=(0.0,0.0,0.0))
        args['internal_energy_j']={'a':2.0,'b':0.0,'c':0.0,'d':0.0}
        args['angular']=ev.AngularTransport(1.0,0.75,1.0)
        out=ev.reactive_moment_kernel(**args)
        self.assertEqual((out.incoming_energy_j,out.outgoing_energy_j,out.delta_internal_j),(6.0,8.0,-2.0))
        flux=ev.explicit_flux_adapter(out,encounter_flux_m5_s=1.0)
        q={i:r.centered((1.0,0.0,0.0))['centered_heat_w_m3'] for i,r in flux['conservative_sources'].items()}
        self.assertEqual([out.species[i].kinetic_j_m2 for i in ('a','b','c','d')],[-8.0,0.0,6.0,4.0])
        self.assertEqual([out.species[i].momentum_kg_m3_s[0] for i in ('a','b','c','d')],[-4.0,0.0,3.0,1.0])
        self.assertEqual([q[i] for i in ('a','b','c','d')],[-4.5,-1.5,4.0,4.0])
        self.assertEqual(out.population_internal_witness_j_m2,-2.0)
        print('CONTROL_JSON='+json.dumps({'scope':'synthetic exact reactive sanity control','kinetic_j_m2':{i:r.kinetic_j_m2 for i,r in out.species.items()},'momentum_x_kg_m3_s':{i:r.momentum_kg_m3_s[0] for i,r in out.species.items()},'Gamma_m3_s':flux['Gamma_m3_s'],'centered_heat_w_m3':q,'population_internal_witness_w_m3':flux['population_internal_witness_w_m3'],'physical_admitted':False},sort_keys=True))

    def test_finite_mass_ratio_exothermic_control(self):
        self.check_oracle(fixture(masses=(1e-29,8e-27,3e-27,5.01e-27),delta_fraction=-0.75))

    def test_endothermic_mass_repartition(self):
        self.check_oracle(fixture(masses=(1e-27,7e-27,6e-27,2e-27),delta_fraction=0.75))

    def test_threshold_products_share_com_velocity(self):
        args=fixture(masses=(1.0,1.0,0.5,1.5),va=(2.0,0.0,0.0),vb=(0.0,0.0,0.0))
        args['internal_energy_j']['c']=1.0
        out,_=self.check_oracle(args)
        self.assertEqual(out.outgoing_energy_j,0.0)
        for i in ('c','d'):
            self.close(out.species[i].momentum_kg_m3_s[0],SIGMA*args['mass_kg'][i],SIGMA*args['mass_kg'][i])

    def test_closed_branch_rejects_positive_measure(self):
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**fixture(delta_fraction=1.1))

    def test_full_tensor_trace_and_total_energy(self):
        args=fixture();out,reference=self.check_oracle(args)
        for i,row in out.species.items():
            self.close(math.fsum(row.second_j_m2[j][j] for j in range(3)),2*row.kinetic_j_m2,2*reference[i][1][5])
        mass_scale=math.fsum(r[1][1] for r in reference.values())
        self.close(math.fsum(r.mass_kg_m2 for r in out.species.values()),0.0,mass_scale)
        for j in range(3):self.close(math.fsum(r.momentum_kg_m3_s[j] for r in out.species.values()),0.0,math.fsum(r[1][2+j] for r in reference.values()))
        kinetic=math.fsum(r.kinetic_j_m2 for r in out.species.values())
        scale=math.fsum(r[1][5] for r in reference.values())
        self.close(kinetic,-SIGMA*out.delta_internal_j,scale)
        self.close(kinetic+out.population_internal_witness_j_m2,0.0,scale)

    def test_elastic_limit_reuses_unchanged_kernel(self):
        args=fixture(masses=(2e-27,3e-27,2e-27,3e-27),outgoing=('a','b'))
        out,reference=self.check_oracle(args)
        source=ev.LEGACY.TransportSource('elastic-control','synthetic:elastic:v1','a','b',0.0,1e100,True,True,False,'labelled_pair_once','conditional','no physical uncertainty')
        old=ev.LEGACY.elastic_moment_kernel(args['mass_kg']['a'],args['mass_kg']['b'],args['velocity_a_m_s'],args['velocity_b_m_s'],ANGULAR,source,purpose='conditional_algebra')
        for identifier in ('a','b'):
            row=out.species[identifier];scale=reference[identifier][1]
            self.assertEqual(row.number_m2,0.0)
            for j in range(3):self.close(row.momentum_kg_m3_s[j],old['momentum_'+identifier+'_kg_m3_s'][j],scale[2+j])
            self.close(row.kinetic_j_m2,old['kinetic_'+identifier+'_j_m2'],scale[5])
            for i in range(3):
                for j in range(3):self.close(row.second_j_m2[i][j],old['second_moment_'+identifier+'_j_m2'][i][j],scale[6+3*i+j])

    def test_shared_id_gain_loss_is_aggregated(self):
        args=fixture(masses=(2e-27,3e-27,2e-27,3e-27),outgoing=('a','d'))
        out,_=self.check_oracle(args)
        self.assertEqual(set(out.species),{'a','b','d'})
        self.assertEqual(out.species['a'].number_m2,0.0)
        self.assertEqual(out.species['b'].number_m2,-SIGMA)
        self.assertEqual(out.species['d'].number_m2,SIGMA)

    def test_reactive_galilean_count_term_and_centered_invariance(self):
        args=fixture();original=ev.reactive_moment_kernel(**args)
        shift=(310.0,-220.0,170.0);bulk=(700.0,100.0,-80.0);flux=4e12
        moved=dict(args,velocity_a_m_s=tuple(x-w for x,w in zip(args['velocity_a_m_s'],shift)),velocity_b_m_s=tuple(x-w for x,w in zip(args['velocity_b_m_s'],shift)))
        shifted=ev.reactive_moment_kernel(**moved)
        one=ev.explicit_flux_adapter(original,encounter_flux_m5_s=flux)
        two=ev.explicit_flux_adapter(shifted,encounter_flux_m5_s=flux)
        for i,raw in one['conservative_sources'].items():
            transformed=raw.change_frame(shift);actual=two['conservative_sources'][i]
            scale=flux*math.fsum(oracle(args)[i][1][5:6])
            self.close(actual.kinetic_w_m3,transformed.kinetic_w_m3,scale)
            for j in range(3):self.close(actual.momentum_kg_m2_s2[j],transformed.momentum_kg_m2_s2[j],flux*oracle(args)[i][1][2+j]+abs(shift[j]*raw.mass_kg_m3_s))
            q=raw.centered(bulk)['centered_heat_w_m3'];qp=actual.centered(tuple(x-w for x,w in zip(bulk,shift)))['centered_heat_w_m3']
            self.close(q,qp,scale+abs(q)+abs(qp))
        self.assertNotEqual(one['conservative_sources']['c'].mass_kg_m3_s,0.0)

    def test_rotation_full_tensor(self):
        args=fixture();out=ev.reactive_moment_kernel(**args)
        # Proper cyclic coordinate rotation, evaluated on nonzero off-diagonals.
        permutation=(1,2,0)
        rotated=dict(args,velocity_a_m_s=tuple(args['velocity_a_m_s'][j] for j in permutation),velocity_b_m_s=tuple(args['velocity_b_m_s'][j] for j in permutation))
        other=ev.reactive_moment_kernel(**rotated)
        for identifier,row in out.species.items():
            for i in range(3):
                for j in range(3):self.close(other.species[identifier].second_j_m2[i][j],row.second_j_m2[permutation[i]][permutation[j]],math.fsum(abs(x) for rr in row.second_j_m2 for x in rr))

    def test_product_relabelling_reverses_angular_axis(self):
        args=fixture();out=ev.reactive_moment_kernel(**args)
        other=dict(args,source=replace(args['source'],outgoing_ids=('d','c')),angular=ev.AngularTransport(SIGMA,2*SIGMA-ANGULAR.sigma1_m2,ANGULAR.sigma2_m2))
        swapped=ev.reactive_moment_kernel(**other)
        for i,row in out.species.items():
            for x,y,scale in zip(flatten(row),flatten(swapped.species[i]),oracle(args)[i][1]):self.close(x,y,scale)

    def test_isotropic_zero_relative_speed_exothermic(self):
        args=fixture(va=(10.0,-20.0,30.0),vb=(10.0,-20.0,30.0))
        args['internal_energy_j']['c']=-1e-20
        args['angular']=ev.AngularTransport(SIGMA,SIGMA,SIGMA)
        self.check_oracle(args,(-1/math.sqrt(3),1/math.sqrt(3)),(0.5,0.5))

    def test_zero_speed_rejects_anisotropic_axis(self):
        args=fixture(va=(0.0,0.0,0.0),vb=(0.0,0.0,0.0))
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**args)

    def test_zero_measure_has_no_fictitious_closed_event(self):
        args=fixture(delta_fraction=2.0);args['angular']=ev.AngularTransport(0.0,0.0,0.0)
        out=ev.reactive_moment_kernel(**args)
        self.assertLess(out.outgoing_energy_j,0.0)
        self.assertTrue(all(x==0 for r in out.species.values() for x in flatten(r)))

    def test_source_scope_and_single_internal_owner_guards(self):
        args=fixture()
        variants=[dict(purpose='physical_evaluation')]
        for key,value in [('full_com_angular_support',False),('axisymmetric_about_relative_velocity',False),('count_convention','inclusive'),('mass_convention','rest_mass'),('internal_energy_owner','independent_rhs'),('internal_energy_convention','already_in_mass'),('immutable_locator',''),('energy_max_j',1e-100),('incoming_ids',('a',''))]:
            variants.append(dict(source=replace(args['source'],**{key:value})))
        for change in variants:
            with self.subTest(change=change),self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,**change))

    def test_invalid_mass_defect_and_missing_state_inputs(self):
        args=fixture()
        for value in (-1.0,0.0,float('inf'),float('nan'),True):
            with self.subTest(value=value),self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,mass_kg=dict(args['mass_kg'],c=value)))
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,mass_kg=dict(args['mass_kg'],c=1.01e-27)))
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,internal_energy_j={'a':0.0}))

    def test_invalid_vectors_angular_measure_and_range(self):
        args=fixture()
        for value in ((1.0,2.0),(float('nan'),0.0,0.0),(float('inf'),0.0,0.0),(True,0.0,0.0)):
            with self.subTest(value=value),self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,velocity_a_m_s=value))
        for angular in (ev.AngularTransport(-1.0,0.0,0.0),ev.AngularTransport(1.0,3.0,1.0),ev.AngularTransport(1.0,0.0,1.0),ev.AngularTransport(0.0,1.0,0.0)):
            with self.subTest(angular=angular),self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,angular=angular))
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**dict(args,velocity_a_m_s=(1e308,0.0,0.0),velocity_b_m_s=(-1e308,0.0,0.0)))
        tiny=fixture(masses=(1e-310,1e-310,1e-310,1e-310))
        with self.assertRaises(ev.ContractError):ev.reactive_moment_kernel(**tiny)

    def test_explicit_flux_no_default_zero_and_finite_guards(self):
        out=ev.reactive_moment_kernel(**fixture())
        with self.assertRaises(TypeError):ev.explicit_flux_adapter(out)
        for flux in (-1.0,float('nan'),float('inf'),True,1e-300):
            with self.subTest(flux=flux),self.assertRaises(ev.ContractError):ev.explicit_flux_adapter(out,encounter_flux_m5_s=flux)
        zero=ev.explicit_flux_adapter(out,encounter_flux_m5_s=0.0)
        self.assertTrue(all(x==0 for x in zero['Gamma_m3_s'].values()))
        self.assertTrue(all(x.kinetic_w_m3==0 for x in zero['conservative_sources'].values()))
        self.assertIsNone(zero['independent_internal_rhs_w_m3'])
        self.assertEqual(zero['birth_pool'],'UNASSIGNED')
        self.assertFalse(zero['physical_admitted'])
        for invalid in (float('nan'),float('inf'),True):
            with self.subTest(witness=invalid),self.assertRaises(ev.ContractError):ev.explicit_flux_adapter(replace(out,population_internal_witness_j_m2=invalid),encounter_flux_m5_s=0.0)

    def test_caloric_count_witness_and_no_double_internal_owner(self):
        event=ev.reactive_moment_kernel(**fixture());flux=2e13
        data=ev.explicit_flux_adapter(event,encounter_flux_m5_s=flux)
        bulk=(700.0,-50.0,100.0)
        q=math.fsum(r.centered(bulk)['centered_heat_w_m3'] for r in data['conservative_sources'].values())
        witness=data['population_internal_witness_w_m3']
        self.close(q+witness,0.0,math.fsum(abs(r.kinetic_w_m3) for r in data['conservative_sources'].values()))
        row=ev.monatomic_caloric('c',2e8,data['Gamma_m3_s']['c'],5000.0,population_pool='thermal')
        heat=data['conservative_sources']['c'].centered(bulk)['centered_heat_w_m3']
        rhs=ev.temperature_rhs([row],temperature_k=5000.0,expansion_s=0.0,pressure_pa=0.0,centered_heat_w_m3=heat,shear_work_w_m3=0.0,heat_flux_divergence_w_m3=0.0,common_temperature_contract='synthetic consumer thermal-pool assignment')
        expected=(heat-1.5*ev.LEGACY.K_B*5000.0*data['Gamma_m3_s']['c'])/(1.5*ev.LEGACY.K_B*2e8)
        self.close(rhs['temperature_rate_k_s'],expected,abs(expected))
        duplicated=replace(row,included_internal_components=('same-physical-level',))
        with self.assertRaises(ev.ContractError):ev.temperature_rhs([duplicated],temperature_k=5000.0,expansion_s=0.0,pressure_pa=0.0,centered_heat_w_m3=heat,shear_work_w_m3=0.0,heat_flux_divergence_w_m3=0.0,common_temperature_contract='synthetic',independent_internal_components=('same-physical-level',))
        json.dumps(event.to_dict(),allow_nan=False)


class ChangedSourceProjectionTests(unittest.TestCase):
    def test_r4_exact_identity_union_and_record_equality(self):
        data=json.loads((ROOT/'sources/WU_R4_CONSUMER_UNION.json').read_text())
        self.assertEqual(data['schema'],'he.event03.wu_r4_consumer_union.v1')
        for key,value in {'base_species':92,'r4_species_records':14,'reused_species':2,'new_unique_species':12,'union_species':104,'base_provider_variants':132,'new_provider_variants':6,'union_provider_variants':138,'base_event_columns':149,'new_event_columns':6,'union_event_columns':155,'ownership_groups_R4':5}.items():self.assertEqual(data['counts'][key],value)
        self.assertEqual(len({r['id'] for r in data['species']}),104)
        self.assertEqual(sum(r['new_to_HE'] for r in data['species']),12)
        raw=json.loads((ROOT/'sources/raw_wu_r4/registry/species.json').read_text())['rows']
        compiled={r['id']:r['compiler_record'] for r in data['species']}
        # Native R4 compiler records are the same records, not material-label matches.
        for identifier,row in raw.items():self.assertEqual(compiled[identifier],row['compiler_record'])
        self.assertTrue(all(r['compiler_record_identical'] for r in data['reused_species']))
        self.assertEqual(len(data['provider_refs']),138)
        self.assertEqual(len(data['event_refs']),155)

    def test_r4_source_bytes_and_no_automatic_physical_admission(self):
        directory=ROOT/'sources/raw_wu_r4'
        manifest=json.loads((directory/'SOURCE_MANIFEST.json').read_text())
        self.assertEqual(len(manifest['files']),13)
        self.assertEqual(sum(r['bytes'] for r in manifest['files']),231150)
        for row in manifest['files']:
            path=directory/row['local_path'];raw=path.read_bytes()
            self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),row['expected_git_blob'])
        union=json.loads((ROOT/'sources/WU_R4_CONSUMER_UNION.json').read_text())
        for key in ('populations_admitted','physical_rates_admitted','energy_Q_admitted','DCS_admitted','activation','automatic_rate_DCS_mass_binding'):self.assertIs(union['intake_flags'][key],False)
        self.assertEqual(sum(row['channel_kind']=='MATERIAL_2_TO_1_PLUS_PRIMARY_PHOTON' for row in union['provider_supply']),1)
        self.assertTrue(all(row['physical_admission'] is False for row in union['provider_supply']))


if __name__=='__main__':unittest.main()
