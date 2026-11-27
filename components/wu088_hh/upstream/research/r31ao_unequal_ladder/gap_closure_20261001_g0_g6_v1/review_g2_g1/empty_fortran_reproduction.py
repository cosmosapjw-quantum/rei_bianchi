
import resource,json
from exact_raw_decoder import decode_npy_bytes
from exact_raw_decoder.test_decoder import npy
resource.setrlimit(resource.RLIMIT_AS,(128*1024*1024,128*1024*1024))
data=npy(b'',descr='<f8',shape=(2**63-1,0),order=True)
try:
 out=decode_npy_bytes(data,max_elements=0)
 print(json.dumps({'status':'RETURNED','values':list(out.values_c_order)}))
except BaseException as e:
 print(json.dumps({'status':'EXCEPTION','type':type(e).__name__,'message':str(e)}))
