"""Source-pinned 2592 x 289 job identities, not a dispatch authorization."""
from c2_support import *

SYNTHETIC='SYNTHETIC_TEST_ONLY'
REPORTED='SOURCE_BOUND_REPORTED'
KINDS=(SYNTHETIC,REPORTED)
COUNT=2592
CELLS=289

class Campaign:
    def __init__(self):
        self.pins=verify_pins()
        self.join=load('_c2_frozen_join',LADDER/'production_solver_20261001_v1/primitive_join/join.py')
        self.endpoint=self.join.endpoint
        self.range=load('_c2_frozen_range',LADDER/'wide_domain_20261001_v1/range_native_driver/driver.py')
        self.cover=load('_c2_frozen_cover',ROOT/'vendor/coverage_contract.py')
        self.plan=read_json(ROOT/'inputs/ENDPOINT_PLAN.json')
        self.endpoint.validate_plan(self.plan,source_archive_bytes=(ROOT/'inputs/FROZEN_INPUTS.npz').read_bytes())
        self.grid=self.cover.geometry()
        if len(self.grid)!=CELLS: raise ContractError('partition count changed')
        if self.plan['window']!={'l_t':'1/512','T_t':'1099511627776','l_u':'1/512','T_u':'1099511627776'}:
            raise ContractError('selected window changed')
        typed_equal(self.plan['precision_bits'],128,'precision')
        self.identity={
            'schema':'WU088_C2_CAMPAIGN_IDENTITY_V1','archive_sha256':self.plan['archive_sha256'],
            'input_record_sha256':self.plan['input_record_sha256'],'endpoint_plan_sha256':self.plan['plan_sha256'],
            'source_pins_sha256':PIN_SHA,'range_source_sha256':self.range.source_identity()['sha256'],
            'grid_sha256':digest(self.grid),'window':self.plan['window'],'precision_bits':128,
            'primitive_count':COUNT,'cells_per_primitive':CELLS,'job_count':COUNT*CELLS,
            'coefficient_semantics':'ORIGINAL_SIGNED_ORDERED107',
            'primitive_order':'active,field,orbital,ia,ib; ib fastest',
            'contraction_order':'source assembly.cpp ia then ib; no symmetry replacement',
            'row_conjugation':'POST_REAL_DOMAIN_INTEGRAL_ONLY',
            'normalization':'SOURCE_ASSEMBLY_CPP_ONCE',
            'assembler_cpp_sha256':byte_sha((LADDER/'gap_closure_20261001_g0_g6_v1/validated_callback/assembly.cpp').read_bytes()),
            'exporter_cpp_sha256':byte_sha((LADDER/'production_solver_20261001_v1/primitive_join/assembly_exporter.cpp').read_bytes()),
            'execution_authorized':False,'automatic_retry':False,'scientific_admission':False,'production_admission':False}
        self.sha256=digest(self.identity)
    def job(self,index,cell):
        if type(index) is not int or not 0<=index<COUNT or type(cell) is not int or not 0<=cell<CELLS:
            raise ContractError('job index outside contract')
        task=self.plan['tasks'][index]
        return strict_bytes(canonical(seal({'schema':'WU088_C2_CELL_JOB_V1','campaign_sha256':self.sha256,
                     'primitive_index':index,'cell_id':cell,'indices':task['indices'],
                     'primitive_task_sha256':task['task_sha256'],'window':self.grid[cell]['window'],
                     'precision_bits':128,'component_radius_exp':-57,
                     'coefficient_semantics':'ORIGINAL_SIGNED_ORDERED107',
                     'endpoint_included':False,'normalization_applied':False,
                     'execution_authorized':False},'job_sha256')))
    def validate_job(self,job):
        if type(job) is not dict: raise ContractError('job object required')
        try: expected=self.job(job['primitive_index'],job['cell_id'])
        except (KeyError,TypeError) as e: raise ContractError('job keys') from e
        if canonical(job)!=canonical(expected): raise ContractError('job/source/order/window/precision changed')
        return job
