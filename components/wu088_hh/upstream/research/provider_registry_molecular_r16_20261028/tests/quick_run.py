import sys,json
sys.path.insert(0,'tests')
from test_r16 import test_boundary_examples,test_random_exhaustive,test_adapter
print('boundary_cases',test_boundary_examples())
print('random_check',json.dumps(test_random_exhaustive(220),sort_keys=True))
print('adapter',test_adapter()['adapter_cells'])
