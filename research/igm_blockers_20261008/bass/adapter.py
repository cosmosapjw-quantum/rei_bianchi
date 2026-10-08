"""Read-only accepted PR86 record bridge. No photon/provider/RHS execution."""
import hashlib, math, struct, json
from pathlib import Path
PIN = '9929edc36232b3620264f3a8b3cf55104ba31c4f63df238f02ed25079738b2b0'
CONTEXT_PIN = 'e74580584a74ad4bddc4c65933a8454a8a6cbde965623f75affa9ee6b745b6fb'
IDS = dict(model_id='manufactured_hhe_v1',provider_id='grackle341_caseA_lowT_subset_v1',closure_id='caseA_escape_C1_primary_only')
class Reader:
    def __init__(self, b): self.b=b; self.i=0
    def take(self,n):
        v=self.b[self.i:self.i+n]
        if len(v)!=n: raise ValueError('INCOMPLETE_RECORD')
        self.i+=n; return v
    def n(self): return struct.unpack('<Q',self.take(8))[0]
    def a(self,n): return list(struct.unpack('<'+'d'*n,self.take(8*n)))
    def option(self):
        tag=self.n()
        if tag not in (0,1): raise ValueError('OPTION_TAG')
        if tag:self.take(8)
    def trace(self): self.take(3*40+16)
def extract(payload):
    """Exact read_state layout at pinned PR86; consume entire immutable artifact."""
    raw=(Path(payload)/'typed.bin').read_bytes()
    context=(Path(payload)/'context.bin').read_bytes()
    if len(raw)!=3336248 or hashlib.sha256(raw).hexdigest()!=PIN or hashlib.sha256(context).hexdigest()!=CONTEXT_PIN: raise ValueError('IMMUTABLE_INPUT_IDENTITY')
    d=Reader(raw); d.a(5); n=d.n(); d.a(n); d.a(15); d.option();d.option();d.a(19);d.n();d.a(3);d.trace();d.trace()
    count=d.n()
    if count!=2:raise ValueError('ACTUAL_TWO_ACCEPTED_RECORDS_REQUIRED')
    records=[]
    for _ in range(count):
        s0,s1=d.a(2);y0=d.a(4);y1=d.a(4);mid=d.a(1)[0];gas=d.a(4);bg=d.a(8);d.a(45+13+19)
        for _ in range(d.n()):
            d.take(16);d.a(4+4+8+2+3+1+13);d.take(13*16);d.option();d.option()
        for _ in range(d.n()):d.n();d.a(13);d.option();d.option()
        records.append(dict(s0=s0.hex(),s1=s1.hex(),y0=[v.hex() for v in y0],y1=[v.hex() for v in y1],midpoint=mid.hex(),gas=[v.hex() for v in gas],background=[v.hex() for v in bg]))
    if d.i!=len(raw):raise ValueError('TRAILING_TYPED_STATE')
    return dict(schema='IGM_BASS_ACTUAL_ACCEPTED_HISTORY_V1',**IDS,typed_sha256=PIN,context_sha256=CONTEXT_PIN,epoch_units='ln a binary64 exact',density_units='proper cm^-3',density_conversion_count=0,doppler_application_count=0,frame='untilted FLRW',clock='normal-time surrogate dt=delta_ln_a/H_mid',reconstruction='supplied frozen midpoint cells',records=records,cosmological_observer_tail='UNKNOWN',producer_calls=0)
def validate(packet):
    for k,v in IDS.items():
        if packet.get(k)!=v:raise ValueError('SOURCE_PROVIDER_CLOSURE_IDENTITY')
    if packet.get('typed_sha256')!=PIN or packet.get('context_sha256')!=CONTEXT_PIN:raise ValueError('ACCEPTED_SOURCE_IDENTITY')
    if packet.get('schema')!='IGM_BASS_ACTUAL_ACCEPTED_HISTORY_V1' or packet.get('epoch_units')!='ln a binary64 exact':raise ValueError('SCHEMA_EPOCH_UNITS')
    if packet.get('density_units')!='proper cm^-3' or packet.get('density_conversion_count')!=0:raise ValueError('DOUBLE_DENSITY_CONVERSION')
    if packet.get('doppler_application_count')!=0 or packet.get('frame')!='untilted FLRW':raise ValueError('DOUBLE_DOPPLER_OR_FRAME')
    if packet.get('clock')!='normal-time surrogate dt=delta_ln_a/H_mid' or packet.get('reconstruction')!='supplied frozen midpoint cells':raise ValueError('CLOCK_RECONSTRUCTION_REQUIRED')
    records=packet['records']
    if len(records)!=2:raise ValueError('ACTUAL_TWO_ACCEPTED_RECORDS_REQUIRED')
    edges=[0.]; cells=[]
    last=None
    for r in records:
        if len(r['y0'])!=4 or len(r['y1'])!=4 or len(r['gas'])!=4 or len(r['background'])!=8:raise ValueError('ACCEPTED_RECORD_LAYOUT')
        s0,s1,mid=map(float.fromhex,[r['s0'],r['s1'],r['midpoint']]); y0=list(map(float.fromhex,r['y0']));y1=list(map(float.fromhex,r['y1']));gas=list(map(float.fromhex,r['gas']));bg=list(map(float.fromhex,r['background']))
        if not all(math.isfinite(v) for v in [s0,s1,mid,*y0,*y1,*gas,*bg]) or not s0<s1 or mid!=(s0+s1)*.5 or gas!=[(a+b)*.5 for a,b in zip(y0,y1)]:raise ValueError('EXACT_EPOCH_GAS')
        if last and (r['s0']!=last['s1'] or r['y0']!=last['y1']):raise ValueError('ACCEPTED_CONTINUITY')
        if bg[2]<=0 or bg[3]<0 or bg[4]<0 or not(0<=gas[0]<=1 and gas[1]>=0 and gas[2]>=0 and gas[1]+gas[2]<=1):raise ValueError('BACKGROUND_GAS_DOMAIN')
        # Background epoch must be exactly the stored FLRW mapping. No new background call.
        if bg[0]!=math.exp(mid):raise ValueError('BACKGROUND_EPOCH')
        dt=(s1-s0)/bg[2];edges.append(edges[-1]+dt)
        cells.append([bg[3]*1e6,bg[4]*1e6,*gas[:3]])
        last=r
    if hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()!='b3d55c38e230ec8ada5c7e5c0ebb5310d367ca7f0580f793519a54972e660434':raise ValueError('EXACT_ACCEPTED_RECORD_PROJECTION')
    return edges,cells
