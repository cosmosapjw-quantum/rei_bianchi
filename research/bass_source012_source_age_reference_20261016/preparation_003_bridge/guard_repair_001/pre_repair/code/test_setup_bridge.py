"""One fake-process start, other controls in memory; never real helper use."""
import copy,json,math,sys,unittest
from pathlib import Path
from unittest.mock import patch
import setup_bridge as bridge

HERE=Path(__file__).resolve().parents[1]

def fixture(n=8):
    x0=math.log(1/21);x1=math.log((1/21)*math.exp(.002));width=x1-x0
    births=[x0+width*(i+.5)/n for i in range(n)]
    mesh=sorted({x1,*[x0+width*(i+.5)/k for k in (8,16,32) for i in range(k)]})
    f=.08;kb=.001;fractions=[.01,.01,.001];d=1+f+.01+f*(.01+2*.001)
    return dict(protocol='SOURCE012_RHS_ONLY_V1',native_base=bridge.BASE,overlay=bridge.OVERLAY,
                q=-.1,birth_count=n,cells=1,config_debug='SYNTHETIC_NOT_NATIVE_CONFIG',
                x0=x0,x1=x1,width=width,quadrature_weight_dln_a=width/n,
                x_units='dimensionless ln(a)',f_units='nHe0/nH0',w_units='eV/H',kb_units='eV/K',
                moment_units='N/H,eV_reference/H',state_order='h,y,z,w_eV/H,cohort_N[],cohort_Uref[],...',
                source_config='supplier_driver_q-0.1_nmu8_cells16_subdiv8_initial8000K',
                f=f,kb_eV_K=kb,ev_erg=1.,initial=fractions+[1.5*kb*8000*d]+[0.]*(2*n),
                mesh=mesh,births=births,inject=[[1/n,3/n] for _ in range(n)],
                support_lo=[[2.] for _ in range(n)],support_hi=[[4.] for _ in range(n)],
                Gamma_s=None,heat=None,prepared_nodes=None,observations_status='NOT_RUN',
                synthetic_only=True)

class SetupBridgeTests(unittest.TestCase):
    def test_one_fake_process_eof_capture_and_no_real_elf(self):
        rec=fixture();raw=(json.dumps(rec,separators=(',',':'))+'\n').encode()
        path=HERE/'raw/synthetic_record.json';path.write_bytes(raw)
        argv=[sys.executable,str(HERE/'code/fake_setup.py'),str(path),'source_rhs','-0.1','8']
        result,validation,receipt=bridge.collect(argv,HERE/'raw/fake_process_001',8,wall_cap=5,output_cap=1048576)
        self.assertEqual(result,rec)
        self.assertEqual((HERE/'raw/fake_process_001/stdout').read_bytes(),raw)
        self.assertIn('EOF confirmed',(HERE/'raw/fake_process_001/stderr').read_text())
        self.assertEqual(receipt['exit_code'],0);self.assertEqual(receipt['derivative_requests'],0)
        self.assertEqual(validation['raw_mesh'],rec['mesh'])
        self.assertTrue(validation['decoded_mesh_has_initial_x0'])
        self.assertNotIn(bridge.ELF_PATH,argv)

    def test_raw_order_duplicate_and_endpoint_rejected_before_decode(self):
        for kind in ('reverse','duplicate','missing_end','out_of_domain','nonfinite'):
            rec=fixture()
            if kind=='reverse':rec['mesh'].reverse()
            elif kind=='duplicate':rec['mesh'][1]=rec['mesh'][0]
            elif kind=='missing_end':rec['mesh'][-1]=math.nextafter(rec['x1'],-math.inf)
            elif kind=='out_of_domain':rec['mesh'][0]=rec['x0']
            else:rec['mesh'][0]=math.nan
            with patch.object(bridge,'load_decoder',side_effect=AssertionError('decoder must not sort bad raw mesh')) as decoder:
                with self.assertRaises(bridge.BridgeFailure):bridge.validate_setup(rec,8)
                decoder.assert_not_called()

    def test_protocol_binding_order_dimensions_constants_and_unborn(self):
        changes=[('protocol','old'),('native_base','wrong'),('overlay','wrong'),('q',0.),
                 ('birth_count',16),('state_order','w,h,y,z'),('cells',True),('cells',0),
                 ('f',math.inf),('kb_eV_K',0.),('ev_erg',-1.),('width',.002),
                 ('quadrature_weight_dln_a',0.),('Gamma_s',[1.]),('config_debug','')]
        # This endpoint-derived width is observably not the old literal .002.
        self.assertNotEqual(fixture()['width'],.002)
        for key,value in changes:
            with self.subTest(key=key):
                rec=fixture();rec[key]=value
                with self.assertRaises(bridge.BridgeFailure):bridge.validate_setup(rec,8)
        for change in ('unborn','short','nonfinite','birth_not_mesh'):
            rec=fixture()
            if change=='unborn':rec['initial'][4]=1.
            elif change=='short':rec['initial'].pop()
            elif change=='nonfinite':rec['initial'][3]=math.inf
            else:rec['births'][0]=math.nextafter(rec['births'][0],math.inf)
            with self.assertRaises(bridge.BridgeFailure):bridge.validate_setup(rec,8)

    def test_support_injection_zero_degenerate_and_thermal_controls(self):
        for change in ('negativeN','meanLow','zeroNnonzeroU','emptySupport','degenerateMean','thermal'):
            rec=fixture()
            if change=='negativeN':rec['inject'][0][0]=-.125
            elif change=='meanLow':rec['inject'][0][1]=.1
            elif change=='zeroNnonzeroU':rec['inject'][0][0]=0.
            elif change=='emptySupport':rec['inject'][0]=[0.,0.] # nonzero empty support is invalid
            elif change=='degenerateMean':rec['support_hi'][0]=[2.]
            else:rec['initial'][3]=0.
            with self.assertRaises(bridge.BridgeFailure):bridge.validate_setup(rec,8)
        rec=fixture();rec['inject'][0]=[0.,0.];rec['support_lo'][0]=[0.];rec['support_hi'][0]=[0.]
        bridge.validate_setup(rec,8)
        rec=fixture();rec['support_hi'][0]=[2.];rec['inject'][0]=[.125,.25]
        bridge.validate_setup(rec,8)

    def test_three_selected_records_preserve_mesh_and_framing_failures(self):
        for n in (8,16,32):
            rec=fixture(n);original=copy.deepcopy(rec['mesh'])
            validated=bridge.validate_setup(rec,n)
            self.assertEqual(rec['mesh'],original);self.assertEqual(validated['raw_mesh'],original)
            self.assertEqual(validated['RHS_requests'],0)
            raw=json.dumps(rec).encode()
            with self.assertRaises(bridge.BridgeFailure):bridge.parse_stdout(raw+b'\n'+raw+b'\n',n)
        with self.assertRaises(bridge.BridgeFailure):bridge.parse_stdout(b'{bad}\n',8)
        with self.assertRaises(bridge.BridgeFailure):bridge.parse_stdout(b'{"x0":NaN}\n',8)
        plan=bridge.plan('/FRESH_OWNER_SETUP_001_NOT_EXECUTED')
        self.assertEqual(len(plan['commands']),3)
        self.assertEqual([r['argv'] for r in plan['commands']],[[bridge.ELF_PATH,'source_rhs','-0.1',str(n)] for n in (8,16,32)])
        self.assertEqual(plan['helper_candidate_sha256'],bridge.ELF_SHA)
        self.assertEqual(plan['derivative_requests'],0)

if __name__=='__main__':unittest.main(verbosity=2)
