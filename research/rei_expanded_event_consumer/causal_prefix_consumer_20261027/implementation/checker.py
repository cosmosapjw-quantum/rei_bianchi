"""One bounded actual-data check. Independent exact endpoint oracle and FD."""
import json, math, sys
from pathlib import Path
from fractions import Fraction as Q
import consumer as c

UNIT=Path(__file__).resolve().parents[1]
OUT=UNIT/'implementation/attempt01'
CHECKS=[]; OBS=[]; BINS=[]; JVPS=[]; SOURCES=[]

def check(name,condition,**data):
    CHECKS.append({'check':name,'pass':bool(condition),**data})
    if not condition:
        raise AssertionError(name)

def invalid(name,fn):
    try: fn()
    except (ValueError,KeyError,TypeError,ZeroDivisionError): check(name,True); return
    check(name,False)

def serial(x):
    if isinstance(x,Q):return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
    raise TypeError(type(x).__name__)

def oracle(raw,cap,a,b,ba=Q(1),bb=Q(1)):
    # Construct bounds directly from original inequalities, independently of closure/window.
    xl=max([Q(0)]+[v[0] for v in raw[:a+1]])
    xh=min([cap]+[v[1] for v in raw[a:]])
    yl=max([Q(0)]+[v[0] for v in raw[:b+1]])
    yh=min([cap]+[v[1] for v in raw[b:]])
    vertices=[]
    for x in (xl,xh):
        for y in (yl,yh):
            if x<=y: vertices.append((x,y))
    left=max(xl,yl);right=min(xh,yh)
    if left<=right:vertices.extend(((left,left),(right,right)))
    values=[y/bb-x/ba for x,y in vertices]
    return min(values),max(values)

def fd(name,fun,args,direction,analytic,operands):
    scale=sum(abs(float(x)) for x in operands)
    for h in (2e-4,1e-4):
        plus=[float(x)+h*float(dx) for x,dx in zip(args,direction)]
        minus=[float(x)-h*float(dx) for x,dx in zip(args,direction)]
        observed=(fun(*plus)-fun(*minus))/(2*h)
        residual=abs(observed-float(analytic))
        relative=residual/scale if scale else residual
        check(name,relative<=2e-8 if scale else observed==0,h=h,relative_residual=relative)

def jvp_suite(f,dt,ta,tb,ba,bb,label,full=False):
    s,ds=Q(7,10),Q(11,100);db=Q(13,100)*ba
    for d,dd,kind in ((Q(1),Q(0),'integrated'),(dt,Q(17,100)*dt,'proper'),
                       (dt*(Q(1,10000000)+(ta+tb)/100000000000000),Q(-9,100)*dt*(Q(1,10000000)+(ta+tb)/100000000000000),'eta')):
        got,j=c.quotient(f,ba,s,ds,db,None if kind=='integrated' else d,dd)
        independent=f*(ds*ba*d-s*(db*d+ba*dd))/(ba*d)**2
        check('rational_jvp_'+kind,j==independent)
        JVPS.append({'source':label,'kind':kind,'f_SI':f,'b_m3':ba,'divisor':d,'ddivisor':dd,'value':got,'jvp':j})
        fd('FD_'+kind,lambda ss,bb_,dd_:ss*float(f)/bb_/dd_,[s,ba,d],[ds,db,dd],j,
           [ds*f/(ba*d),-s*f*db/(ba*ba*d),-s*f*dd/(ba*d*d)])
    deta=dt*(Q(1,10000000)+(ta+tb)/100000000000000)
    wrapped=c.clock_averages(f,ba,dt,deta,ddt=Q(17,100)*dt,ddeta=-Q(9,100)*deta,s=s,ds=ds,db=db)
    check('clock_wrapper_independent_divisors',
          wrapped['proper']==c.quotient(f,ba,s,ds,db,dt,Q(17,100)*dt) and
          wrapped['eta']==c.quotient(f,ba,s,ds,db,deta,-Q(9,100)*deta))
    pr=c.quotient(f,ba,duration=dt)[0];et=c.quotient(f,ba,duration=deta)[0]
    check('integrated_clock_invariance',pr*dt==et*deta==s*f/ba)
    check('finite_interval_clock',et==(dt/deta)*pr)

def run():
    for case in ('chi1.5_R80_N2048','chi3_R80_N2048'):
        summary=json.loads((UNIT/'inputs'/f'{case}_SUMMARY.json').read_text())
        book=json.loads((UNIT/'inputs'/f'{case}_BIN_EXPORTS.json').read_text())
        groups=c.validate_book(summary,book)
        check('source_maps_bin_identities',sum(map(len,groups.values()))==18)
        for row in summary['source_rows']:
            sid=row['source_id'];times=[c.rational(h['T_s']) for h in row['horizons']]
            SOURCES.append({'case':case,'source':sid,'source_identity':row['source_identity'],
                            'frame':groups[sid][0]['frame'],'time_basis':groups[sid][0]['time_basis'],
                            'source_qualified_scope':groups[sid][0]['source_qualified_scope']})
            polys={}
            for key,allkey in (('count_cm3','all_time_count_cm3'),('kinetic_eV_cm3','all_time_kinetic_eV_cm3')):
                p=c.closure(times,[h[key] for h in row['horizons']],row[allkey][1]);polys[key]=p
                check('closure_feasible',c.feasible(p,p['l']) and c.feasible(p,p['u']))
                for a in range(6):
                    for b in range(a+1,7):
                        lo,hi,lw,uw=c.window(p,a,b)
                        check('sharp_vertex_oracle',(lo,hi)==oracle(p['raw'],p['cap'],a,b))
                        check('extremizers',c.feasible(p,lw) and c.feasible(p,uw) and lw[b]-lw[a]==lo and uw[b]-uw[a]==hi)
                        for f in (lw,uw):
                            check('telescoping_allocation',sum(f[i+1]-f[i] for i in range(a,b))==f[b]-f[a])
                        bl=[c.interval(x[key]) for x in row['bins'][a:b]]
                        independent=(sum(x[0] for x in bl),sum(x[1] for x in bl))
                        check('independent_bin_enclosure',independent[0]<=lo<=hi<=independent[1])
                        ba=Q(1400000)*(1+Q(a,20));bb=Q(1400000)*(1+Q(b,20))
                        nlo,nhi,_=c.endpoint_range(p,a,b,ba,bb)
                        check('normalized_vertex_oracle',(nlo,nhi)==oracle(p['raw'],p['cap'],a,b,ba,bb))
                        nlo,nhi=c.basis_si(nlo,key),c.basis_si(nhi,key)
                        rounded=(c.outward(lo)[0],c.outward(hi)[1])
                        check('outward_enclosure',c.rational(rounded[0])<=lo and c.rational(rounded[1])>=hi)
                        OBS.append({'case':case,'source':sid,'basis':key,'a':a,'b':b,'lower':lo,'upper':hi,'outward':rounded,
                                    'lower_witness':lw,'upper_witness':uw,'independent_bin_sum':independent,
                                    'width':hi-lo,'independent_width':independent[1]-independent[0],
                                    'width_gain':independent[1]-independent[0]-(hi-lo),
                                    'normalized_endpoint_range_SI':[nlo,nhi]})
                lw=c.window(p,0,6)[2]
                jvp_suite(c.basis_si(lw[-1],key),times[-1],times[0],times[-1],Q(1400000),Q(1820000),case+'/'+sid+'/'+key+'/full',True)
                # Nonzero starting prefix exercises every variable-reference quotient term.
                fa,fb=c.basis_si(p['l'][1],key),c.basis_si(p['l'][6],key);ba=Q(1470000);bb=Q(1820000)
                dba=Q(13,100)*ba;dbb=-Q(7,100)*bb
                ep=c.endpoint(fa,fb,ba,bb,dba=dba,dbb=dbb)
                check('nonzero_prefix_witness',fa>0 and c.feasible(p,p['l']))
                JVPS.append({'case':case,'source':sid,'basis':key,'kind':'endpoint_1_6','fa_SI':fa,'fb_SI':fb,'ba':ba,'bb':bb,'dba':dba,'dbb':dbb,**ep})
                check('reference_decomposition',ep['change']==ep['event']+ep['correction'] and ep['jvp']==ep['event_jvp']+ep['correction_jvp'])
                ref=Q(11,100)*(fb/bb-fa/ba)+Q(7,10)*(fa*dba/ba**2-fb*dbb/bb**2)
                check('endpoint_independent_jvp',ep['jvp']==ref)
                fd('FD_endpoint',lambda ss,aa,bb_:ss*(float(fb)/bb_-float(fa)/aa),[Q(7,10),ba,bb],[Q(11,100),dba,dbb],ref,
                   [Q(11,100)*fb/bb,-Q(11,100)*fa/ba,Q(7,10)*fa*dba/ba**2,-Q(7,10)*fb*dbb/bb**2])
                check('missing_reference_mutant',ep['correction']!=0 and ep['jvp']!=Q(11,100)*(fb/bb-fa/ba))
                check('missing_dba_mutant',Q(7,10)*fa*dba/ba**2!=0)
            for i,event in enumerate(groups[sid]):
                # Joint common-pair witness is a feasible information-set allocation, not a reconstructed source.
                n=polys['count_cm3']['l'][i+1]-polys['count_cm3']['l'][i]
                e=polys['kinetic_eV_cm3']['l'][i+1]-polys['kinetic_eV_cm3']['l'][i]
                mapped=c.joint_map(n,e,Q(1400000));v=mapped['native25'];energy=mapped['energy_J_m3']
                check('common_pair_energy_identity',sum(energy.values())==0)
                check('native_charge_particles',sum(v[:21])==0 and v[11]+2*v[12]-v[21]==0 and 2*v[11]+3*v[12]-v[21]==0)
                check('native_zero_rows',all(v[j]==0 for j in range(25) if j not in (11,12,21,22)))
                check('native_energy_identity',-c.I*c.EV*v[11]+v[22]+mapped['retained_photon_per_baryon']['energy']==0)
                check('missing_normalization',c.joint_map(n,e)['native25'] is None)
                check('missing_eta',c.clock_averages(n,Q(1400000),times[i+1]-times[i])['eta'] is None)
                for f,key in ((n,'count_cm3'),(e,'kinetic_eV_cm3')):jvp_suite(c.basis_si(f,key),times[i+1]-times[i],times[i],times[i+1],Q(1400000),Q(1400000),case+'/'+sid+'/'+key+'/bin'+str(i))
                ni=c.interval(event['common_basis']['N_cm3']['interval']);ei=c.interval(event['common_basis']['E_eV_cm3']['interval'])
                corner_residual=(ei[1]-ei[0])+c.I*(ni[1]-ni[0])
                check('independent_reservoir_corner_mutant',corner_residual>0)
                ta,tb=times[i],times[i+1];deta=(tb-ta)*(Q(1,10000000)+(ta+tb)/100000000000000)
                endpoint_h=Q(1,10000000)+2*tb/100000000000000
                check('endpoint_H_mutant',(tb-ta)/deta!=1/endpoint_h)
                BINS.append({'case':case,'source':sid,'canonical_event_id':event['canonical_event_id'],'start_s':ta,'end_s':tb,
                             'count_cm3':ni,'kinetic_eV_cm3':ei,'feasible_information_pair':[n,e],'map':mapped,
                             'deta_manufactured':deta,'independent_corner_residual_eV_cm3':corner_residual})
        # Invalid book controls use shallow copies; original bytes and objects remain unchanged.
        bad=dict(book);bad['exports']=book['exports']+[book['exports'][0]]
        invalid('duplicate_event',lambda:c.validate_book(summary,bad))
        for field,value,label in [('observation_kind','cumulative','cumulative_extra'),('case_id','wrong','case_mismatch'),('source_id','wrong','source_mismatch'),('time_end_s',0,'invalid_bin_width'),('source_identity',{},'operator_bath_projection_mismatch')]:
            e=dict(book['exports'][0]);e[field]=value;bad=dict(book);bad['exports']=[e]+book['exports'][1:]
            invalid(label,lambda:c.validate_book(summary,bad))
        e=dict(book['exports'][0]);e['clock_metadata']=dict(e['clock_metadata']);records=list(e['clock_metadata']['records']);r=dict(records[0]);r['clocks']=dict(r['clocks']);clk=dict(r['clocks']['minus']);clk['a_numerator']=int(float(clk['a_numerator']));r['clocks']['minus']=clk;records[0]=r;e['clock_metadata']['records']=records;bad=dict(book);bad['exports']=[e]+book['exports'][1:]
        invalid('JS_rounded_integer_metadata',lambda:c.validate_book(summary,bad))
    for x in (0,-1,True,float('nan'),float('inf')):
        invalid('invalid_normalization',lambda:c.joint_map(1,1,x))
    for args in (([0,1],[(0,0),(2,1)],3),([0,1,2],[(0,0),(2,3),(0,1)],4),([0,1],[(0,0),(2,3)],1),([0,1],[(1,1),(1,2)],3),([0,0],[(0,0),(0,1)],2)):
        invalid('invalid_temporal_polytope',lambda:c.closure(*args))
    for d in (0,-1,True,float('inf')): invalid('invalid_duration',lambda:c.quotient(1,1,duration=d))
    check('zero_pair',all(x==0 for x in c.joint_map(0,0,1)['native25']))
    check('zero_scale',c.quotient(1,1,s=0,ds=0)==(0,0))
    check('actual_counts',len(OBS)==252 and len(BINS)==36)

def save(status,error=None):
    (OUT/'OBSERVATIONS.json').write_text(json.dumps({'status':status,'qualification':'conditional interval-monotonicity information polytope only; provider C9 execution discrepancy retained','sources':SOURCES,'windows':OBS,'bins':BINS,'interface_derivatives':JVPS,'physical_state_update':False},default=serial,separators=(',',':'))+'\n')
    (OUT/'CHECKS.json').write_text(json.dumps({'status':status,'checks':len(CHECKS),'passed':sum(x['pass'] for x in CHECKS),'scalar_windows':len(OBS),'source_windows':len(OBS)//2,'canonical_bins':len(BINS),'error':error,'results':CHECKS},separators=(',',':'))+'\n')
    lines=['| Case | Source | Canonical event | Start s | End s | N lower cm^-3 | N upper cm^-3 | E lower eV cm^-3 | E upper eV cm^-3 |','|---|---|---|---:|---:|---:|---:|---:|---:|']
    for x in BINS:lines.append('| '+' | '.join(map(str,[x['case'],x['source'],x['canonical_event_id'],x['start_s'],x['end_s'],*[float(t) for t in x['count_cm3']],*[float(t) for t in x['kinetic_eV_cm3']]]))+' |')
    (OUT/'BIN_TABLE.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    try:run()
    except BaseException as e:
        save('FAIL',repr(e));raise
    save('PASS')
    print(json.dumps({'status':'PASS','checks':len(CHECKS),'scalar_windows':len(OBS),'canonical_bins':len(BINS)}))
