"""Positive coordinates; independent SciPy DOP853, unchanged native physics.
Structural empty/future cells are excluded from every solve_ivp state vector.
"""
import argparse,json,subprocess,time,resource,struct
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('out',type=Path);p.add_argument('--q',type=float,default=0.);p.add_argument('--tight',action='store_true');p.add_argument('--old-regression',type=Path);p.add_argument('--birth-panels',type=int,default=8);p.add_argument('--n-mu',type=int,default=8);p.add_argument('--source-subdivisions',type=int,default=8);p.add_argument('--transport-cells',type=int,default=16);p.add_argument('--max-wall-s',type=float,default=600.);p.add_argument('--max-rhs',type=int,default=200000);p.add_argument('--rpc-mode',choices=('text','binary64'),default='text');p.add_argument('--error-norm',choices=('rms','block-max'),default='rms');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
"""Opt-in block maximum of SciPy DOP853 embedded-error estimates.

Only _estimate_error_norm changes. Stage equations, dense interpolation and
initial-step selection are inherited unchanged from the installed SciPy.
"""
import hashlib
import inspect
import math

import numpy as np
import scipy
from scipy.integrate._ivp.rk import DOP853


def error_control_identity():
    source = inspect.getsource(DOP853._estimate_error_norm)
    return dict(scipy_version=scipy.__version__,
                scipy_estimator_sha256=hashlib.sha256(source.encode()).hexdigest(),
                estimator='DOP853._estimate_error_norm')


def validate_blocks(block_sizes, dimension):
    blocks = tuple(block_sizes)
    if (not blocks or any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in blocks)
            or sum(blocks) != dimension):
        raise ValueError('ERROR_BLOCK_PARTITION')
    return blocks


def production_blocks(dimension):
    if not isinstance(dimension, int) or dimension < 18:
        raise ValueError('PRODUCTION_COMPRESSED_DIMENSION')
    logs = dimension-18
    return (4,) + ((logs,) if logs else ()) + (1,)*14


def positive_product(factors):
    mantissa, exponent = 1., 0
    for value in factors:
        if value == 0:
            return 0.
        part, shift = math.frexp(value)
        mantissa *= part
        exponent += shift
    try:
        return math.ldexp(mantissa, exponent)
    except OverflowError:
        return math.inf


def block_error_norm(err5, err3, h, block_sizes):
    err5 = np.asarray(err5, dtype=float)
    err3 = np.asarray(err3, dtype=float)
    if err5.ndim != 1 or err3.shape != err5.shape:
        raise ValueError('ERROR_ARRAY_DIMENSION')
    blocks = validate_blocks(block_sizes, err5.size)
    if not math.isfinite(h) or not np.isfinite(err5).all() or not np.isfinite(err3).all():
        raise ValueError('NONFINITE_ERROR_ESTIMATE')
    result = 0.
    start = 0
    for size in blocks:
        a = err5[start:start+size]
        b = err3[start:start+size]
        scale = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))))
        if scale:
            an = float(np.linalg.norm(a/scale))
            bn = float(np.linalg.norm(b/scale))
            # |h| A/sqrt(m(A+.01B)), A=||err5||², B=||err3||².
            value = positive_product((abs(h), scale, an/math.hypot(an, .1*bn), an/math.sqrt(size)))
            result = max(result, value)
        start += size
    return result


def make_block_dop853(block_sizes):
    """Bind an explicit complete partition to a solve_ivp method class."""
    blocks = tuple(block_sizes)

    class BlockDOP853(DOP853):
        def __init__(self, fun, t0, y0, t_bound, **kwargs):
            self.block_sizes = validate_blocks(blocks, len(y0))
            super().__init__(fun, t0, y0, t_bound, **kwargs)

        def _estimate_error_norm(self, K, h, scale):
            if not np.isfinite(scale).all() or np.any(scale <= 0):
                raise ValueError('ERROR_SCALE_DOMAIN')
            err5 = np.dot(K.T, self.E5)/scale
            err3 = np.dot(K.T, self.E3)/scale
            return block_error_norm(err5, err3, h, self.block_sizes)

    return BlockDOP853


if a.error_norm == 'block-max':
    _scipy_solve_ivp = solve_ivp
    def solve_ivp(*args, **kwargs):
        kwargs['method'] = make_block_dop853(production_blocks(len(args[2])))
        return _scipy_solve_ivp(*args, **kwargs)

"""Passive runtime helpers embedded only in the opt-in reference copy."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def _diagnostic_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {k: _diagnostic_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_diagnostic_json(v) for v in value]
    return value


class ReferenceDiagnostics:
    def __init__(self, output, identity, executed_file):
        self.output = Path(output)
        self.identity = dict(identity)
        self.identity['executed_solver_sha'] = hashlib.sha256(Path(executed_file).read_bytes()).hexdigest()
        self.attempts = []
        self.jumps = []
        self.current = None

    def persist(self):
        telemetry = dict(schema='rei.reference.passive_diagnostics.v1', identity=self.identity,
                         interpretation='DESCRIPTIVE_ONLY; does not establish RMS dilution causality',
                         attempts=self.attempts)
        jumps = dict(schema='rei.reference.source_jumps.v1', identity=self.identity,
                     status='AVAILABLE' if self.jumps else 'MISSING_DATA', records=self.jumps)
        self.output.mkdir(parents=True, exist_ok=True)
        for name, value in [('reference_diagnostics.json', telemetry), ('source_jumps.json', jumps)]:
            (self.output/name).write_text(json.dumps(_diagnostic_json(value), indent=2, allow_nan=False)+'\n')

    def instrument_factory(self, original_factory, component_norm):
        owner = self

        def factory(block_sizes):
            original = original_factory(block_sizes)

            class ObservedDOP853(original):
                def _estimate_error_norm(self, K, h, scale):
                    # The existing controller is called once and its exact
                    # return value is returned unchanged to SciPy.
                    actual = super()._estimate_error_norm(K, h, scale)
                    err5 = np.dot(K.T, self.E5)/scale
                    err3 = np.dot(K.T, self.E3)/scale
                    names = ['gas'] + (['photon_logs'] if len(scale) > 18 else []) + [f'ledger_{i}' for i in range(14)]
                    values = []
                    start = 0
                    for index, size in enumerate(self.block_sizes):
                        stop = start+size
                        value = component_norm(err5[start:stop], err3[start:stop], h, (size,))
                        values.append(dict(index=index, name=names[index], start=start, stop=stop, value=value))
                        start = stop
                    maximum = max(x['value'] for x in values)
                    record = dict(t=float(self.t), h=float(h), t_new=float(self.t+h),
                                  dimension=len(scale), blocks=values,
                                  binding_indices=[x['index'] for x in values if x['value'] == maximum],
                                  binding_names=[x['name'] for x in values if x['value'] == maximum],
                                  block_max_diagnostic=maximum, error_norm_actual=float(actual),
                                  old_rms_diagnostic=component_norm(err5, err3, h, (len(scale),)),
                                  error_accept=bool(actual < 1.))
                    if owner.current is not None:
                        owner.current['estimates'].append(record)
                    return actual

            return ObservedDOP853
        return factory

    def solve(self, original_solve, event, retry, *args, **kwargs):
        start, stop = args[1]
        attempt = dict(attempt=len(self.attempts), event=event, retry=retry,
                       interval_start=float(start), interval_stop=float(stop), estimates=[],
                       status='RUNNING', discarded=True, retained=False)
        self.attempts.append(attempt)
        self.current = attempt
        try:
            solution = original_solve(*args, **kwargs)
            attempt.update(status='RETURNED_SUCCESS' if solution.success else 'RETURNED_FAILURE',
                           discarded=not bool(solution.success), retained=bool(solution.success),
                           returned_steps=len(solution.t)-1)
            return solution
        except BaseException as error:
            attempt.update(status='EXCEPTION', exception_type=type(error).__name__, exception=repr(error))
            raise
        finally:
            attempt['local_error_accepted_estimates'] = sum(x['error_accept'] for x in attempt['estimates'])
            attempt['final_trajectory_accepted_estimates'] = (
                attempt['local_error_accepted_estimates'] if attempt['retained'] else 0)
            self.current = None
            self.persist()

    @staticmethod
    def compact(physical):
        if len(physical.get('flat', [])) < 4 or len(physical.get('ledgers', [])) != 14:
            raise ValueError('SOURCE_JUMP_PHYSICAL_SHAPE')
        return dict(N=physical['N'], U=physical['U'], gas=physical['flat'][:4],
                    ledgers=list(physical['ledgers']))

    def birth(self, event, x, active_before, active_after, setup, before, after, physical_before, get_post):
        record = dict(event=event, x=float(x), active_before=active_before, active_after=active_after,
                      source_inventory=setup['source_inventory'][event], status='RUNNING')
        self.jumps.append(record)
        try:
            record['pre'] = self.compact(physical_before)
            record['post'] = self.compact(get_post())
            lo = 4+2*setup['cells']*event
            hi = lo+2*setup['cells']
            mask = np.ones(before.size, dtype=bool)
            mask[lo:hi] = False
            bits_before = np.asarray(before, dtype=np.float64).view(np.uint64)
            bits_after = np.asarray(after, dtype=np.float64).view(np.uint64)
            record.update(status='AVAILABLE',
                          unchanged_nonbirth_coordinates_bits=bool(np.array_equal(bits_before[mask], bits_after[mask])),
                          unchanged_gas_coordinate_bits=bool(np.array_equal(bits_before[:4], bits_after[:4])),
                          unchanged_ledger_coordinate_bits=bool(np.array_equal(bits_before[-setup['extra']:], bits_after[-setup['extra']:])))
        except BaseException as error:
            record.update(status='ERROR', exception_type=type(error).__name__, exception=repr(error))
            raise
        finally:
            self.persist()


if a.error_norm != 'block-max':
    raise ValueError('REFERENCE_DIAGNOSTICS_REQUIRE_BLOCK_MAX')
_reference_diagnostics = ReferenceDiagnostics(a.out, {'computational_base_solver_sha': '78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620', 'diagnostic_transform_sha': '11eb2462b2907a480f66d79a297d6daac4d45ea45b7600204667db0b854a69eb', 'reference_diagnostics': True}, __file__)
make_block_dop853 = _reference_diagnostics.instrument_factory(make_block_dop853, block_error_norm)
_reference_base_solve = solve_ivp
def solve_ivp(*args, **kwargs):
    return _reference_diagnostics.solve(_reference_base_solve, event, retry, *args, **kwargs)

server=subprocess.Popen([str(a.binary),'server_binary64' if a.rpc_mode=='binary64' else 'server',str(a.q),str(a.birth_panels),str(a.n_mu),str(a.source_subdivisions),str(a.transport_cells)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
setup=json.loads(server.stdout.readline().decode());(a.out/'setup.json').write_text(json.dumps(setup)+'\n')
started=time.monotonic();calls=0;errors=[]
observations=[]
common_x=[setup['x0']+(setup['x1']-setup['x0'])*(i+.5)/8 for i in range(8)]+[setup['x1']]
class DomainError(RuntimeError):pass
def _write_all(stream,data):
    remaining=memoryview(data)
    while remaining:
        written=stream.write(remaining)
        if written is None or written<=0: raise RuntimeError('BINARY_RPC_WRITE_FAILED')
        remaining=remaining[written:]

def _read_exact(stream,size):
    chunks=[]
    remaining=size
    while remaining:
        chunk=stream.read(remaining)
        if not chunk: raise RuntimeError('BINARY_RPC_TRUNCATED')
        chunks.append(chunk)
        remaining-=len(chunk)
    return b''.join(chunks)

def send(mode,active,x,y):
    if a.rpc_mode == 'binary64':
        if mode == 'OLD':
            raise ValueError('OLD regression RPC requires text mode')
        values=np.asarray(y,dtype='<f8')
        _write_all(server.stdin,struct.pack('<cIdI',mode.encode('ascii'),active,x,values.size))
        _write_all(server.stdin,values.tobytes())
        server.stdin.flush()
        head=_read_exact(server.stdout,5)
        status,length=struct.unpack('<BI',head)
        payload=_read_exact(server.stdout,length)
        if status: return payload.decode()
        if mode == 'R':
            if length!=8*values.size: raise RuntimeError('BINARY_RPC_RHS_SIZE')
            return np.frombuffer(payload,dtype='<f8').copy()
        return payload.decode()
    _write_all(server.stdin,(f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in y)+'\n').encode());server.stdin.flush()
    line=server.stdout.readline()
    if not line:raise RuntimeError(server.stderr.read().decode(errors='replace'))
    return line.decode().strip()
if a.old_regression:
    old=np.load(a.old_regression);reply=send('OLD',8,float(old[0]),old[1:]);assert reply.startswith('ERR'),reply
    (a.out/'original_negative_RK_regression.json').write_text(json.dumps(dict(reply=reply,min_state=float(old[5:].min()),scope='unchanged raw original call291 native positive-state guard'))+'\n')
cells=setup['cells'];size=4+2*len(setup['births'])*cells+setup['extra'];extra_start=size-setup['extra'];y=np.zeros(size);y[:4]=setup['initial'];active=0;start=setup['x0'];interval_records=[];status='ERROR';failure=None
try:
    for event,stop in enumerate([*setup['births'],setup['x1']]):
        indices=np.array([*range(4),*[k for group in setup['active_indices'][:active] for k in group],*range(extra_start,size)],dtype=int)
        base=y.copy();initial=y[indices].copy();max_step=np.inf
        for retry in range(13):
            def rhs(x,z):
                global calls
                calls+=1
                if calls>a.max_rhs or time.monotonic()-started>a.max_wall_s:raise RuntimeError('frozen RHS/time cap')
                whole=base.copy();whole[indices]=z
                answer=send('R',active,x,whole)
                if isinstance(answer,str) and answer.startswith('ERR'):
                    np.save(a.out/f'first_failed_state_event{event}_retry{retry}.npy',np.r_[x,whole])
                    errors.append(dict(event=event,retry=retry,x=x,message=answer,calls=calls))
                    (a.out/'provider_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
                    raise DomainError(answer)
                result=answer if isinstance(answer,np.ndarray) else np.fromstring(answer,sep=' ');assert result.size==size,result.size
                return result[indices]
            try:
                atol=np.full(size,1e-12 if a.tight else 1e-11)
                atol[extra_start:extra_start+4]=1e-15 if a.tight else 1e-14
                atol[extra_start+4:]=1e-17 if a.tight else 1e-16
                sol=solve_ivp(rhs,(start,stop),initial,method='DOP853',rtol=2e-11 if a.tight else 2e-10,atol=atol[indices],max_step=max_step,dense_output=True)
                if not sol.success:raise RuntimeError(sol.message)
                y=base.copy();y[indices]=sol.y[:,-1];break
            except DomainError as error:
                # Rejection restores exact same interval input. Coordinate
                # underflow/unsupported boundary is a typed scientific HOLD.
                if 'underflow' in str(error) or 'MOMENT_FIT' in str(error):raise
                if retry==12:raise
                max_step=(stop-start)/2**(retry+2)
        for ox in common_x:
            if ox>start and ox<=stop:
                observed=base.copy();observed[indices]=sol.sol(ox)
                state=json.loads(send('P',active,ox,observed));observations.append(dict(x=ox,side='pre',active=active,physical=state))
                if ox!=stop or event>=len(setup['births']):observations.append(dict(x=ox,side='post',active=active,physical=state))
        physical=json.loads(send('P',active,stop,y))
        np.save(a.out/f'accepted_coordinates_event{event}.npy',y)
        interval_records.append(dict(event=event,x=stop,active=active,solver_steps=sol.t.size-1,calls=calls,dimension=indices.size,N=physical['N'],U=physical['U']))
        if event<len(setup['births']):
            _before_birth_coordinates=y.copy()
            y[4+2*cells*event:4+2*cells*(event+1)]=setup['encoded_births'][event];active+=1
            _reference_diagnostics.birth(event,stop,active-1,active,setup,_before_birth_coordinates,y,physical,lambda:json.loads(send('P',active,stop,y)))
            if stop in common_x:observations.append(dict(x=stop,side='post',active=active,physical=json.loads(send('P',active,stop,y))))
        start=stop
    (a.out/'observations.json').write_text(json.dumps(observations)+'\n')
    physical=json.loads(send('P',active,start,y));(a.out/'endpoint.json').write_text(json.dumps(physical)+'\n')
    flat=np.array(physical['flat']);gas=flat[:4];he=setup['he_h'];chi=setup['binding_ev'];initial=np.array(setup['initial_physical'])
    binding=lambda f:chi[0]*f[0]+he*(chi[1]*f[1]+(chi[1]+chi[2])*f[2])
    e0=initial[3]+binding(initial);led=np.array(physical['ledgers']);source=np.array(setup['source_inventory']).sum(axis=0)
    er=gas[3]+binding(gas)+physical['U']+led[0]+led[2]+led[3]-led[1]-source[1]-e0
    eg=abs(gas[3])+abs(binding(gas))+abs(physical['U'])+abs(led[0])+abs(led[1])+abs(led[2])+abs(led[3])+source[1]+abs(e0)
    nr=physical['N']+led[4:7].sum()-source[0];ng=physical['N']+abs(led[4:7]).sum()+source[0]
    photo=led[4:7];rr=led[7:10];ci=led[10:13];dr=led[13];net=photo+ci-rr
    charge=lambda f:f[0]+he*(f[1]+2*f[2]);qr=charge(gas)-charge(initial)-net.sum()+dr
    species=(gas[:3]-initial[:3])*np.array([1,he,he])-np.array([net[0],net[1]-net[2]-dr,net[2]])
    ledger=dict(energy_residual=er,energy_gross=eg,energy_normalized=abs(er)/eg,photon_residual=nr,photon_gross=ng,photon_normalized=abs(nr)/ng,charge_residual=qr,species_residual=species.tolist(),source_N_U=source.tolist())
    (a.out/'ledgers.json').write_text(json.dumps(ledger,indent=2)+'\n')
    assert abs(er)<=1e-8*eg and abs(nr)<=1e-8*ng,ledger
    status='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
except Exception as error:
    failure=repr(error);status='HOLD_POSITIVE_NATIVE_REFERENCE';raise
finally:
    _reference_diagnostics.persist()
    server.stdin.close();server.wait(timeout=30)
    (a.out/'solver_return.json').write_text(json.dumps(dict(reference_diagnostics=True,reference_diagnostic_identity=_reference_diagnostics.identity,max_rhs=a.max_rhs,max_wall_s=a.max_wall_s,rpc_mode=a.rpc_mode,error_norm=a.error_norm,error_control_identity=error_control_identity(),status=status,failure=failure,q=a.q,tight=a.tight,birth_panels=a.birth_panels,n_mu=a.n_mu,source_subdivisions=a.source_subdivisions,transport_cells=a.transport_cells,calls=calls,wall_s=time.monotonic()-started,python_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,errors=errors,intervals=interval_records,server_exit=server.returncode),indent=2)+'\n')
