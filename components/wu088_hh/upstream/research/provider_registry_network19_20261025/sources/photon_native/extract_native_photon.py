"""Transcribe native ENDF TAB1 cross sections and production yields.

No interpolation, yield multiplication, physical rate or mass/Q evaluation.
Every numerical field remains a native printed ENDF string with a line locator.
Only LAW 0/1/2/3/4/6 formats actually encountered are accepted.
"""
from pathlib import Path
from decimal import Decimal
import hashlib,json,math,re,time

BASE=Path(__file__).resolve().parent
EXPECTED={
 'nndc_g-001_H_002.endf':'cf6028ca5aa7d0768be3252083e111913232499df6bf07020e72a50baffb70ef',
 'nndc_g-002_He_003.endf':'6b33a4166452001a958ab7341db27a5ed289a8df09e63f5c3e40a726ae4bf67f',
 'nndc_g-003_Li_007.endf':'4eb6aef217b2247d41e95fd87f2a8e60d812089ad0b6575ba7da29acddbb63ef'}
def fields(line):return [line[i:i+11].strip() for i in range(0,66,11)]
def val(s):
 s=s.strip()
 if 'e' not in s.lower():s=re.sub(r'(?<=\d)([+-]\d+)$',r'E\1',s)
 return Decimal(s)
def section(lines,mf,mt):
 return [(i+1,x) for i,x in enumerate(lines) if len(x)>=75 and x[70:72].strip()==str(mf) and x[72:75].strip()==str(mt)]
def packed(sec,start,n):
 a=[]
 for i in range(start,start+math.ceil(n/6)):
  for j,s in enumerate(fields(sec[i][1])):a.append((s,sec[i][0],j+1))
 return a[:n],start+math.ceil(n/6)
def tab1(sec,i):
 f=fields(sec[i][1]);nr,np=int(f[4]),int(f[5]);ints,j=packed(sec,i+1,2*nr);values,k=packed(sec,j,2*np)
 rows=[]
 for a,b in zip(values[::2],values[1::2]):
  assert a[1]==b[1]
  rows.append({'x':a[0],'y':b[0],'source_line_1based':a[1],'x_field_1based':a[2],'y_field_1based':b[2]})
 assert len(rows)==np and all(val(rows[z]['x'])<val(rows[z+1]['x']) for z in range(np-1))
 return {'header_fields':f,'header_line_1based':sec[i][0],'NR':nr,'NP':np,'interpolation':[{'NBT':int(a[0]),'INT':int(b[0])} for a,b in zip(ints[::2],ints[1::2])],'rows':rows,'last_source_line_1based':sec[k-1][0]},k
def tab2(sec,i):
 f=fields(sec[i][1]);nr,ne=int(f[4]),int(f[5]);_,j=packed(sec,i+1,2*nr);return ne,j
def skip_list(sec,i):
 n=int(fields(sec[i][1])[4]);return i+1+math.ceil(n/6)
def mf6_yields(sec):
 head=fields(sec[0][1]);nk=int(head[4]);i=1;products=[]
 for _ in range(nk):
  t,i=tab1(sec,i);f=t['header_fields'];law=int(f[3])
  products.append({'ZAP':f[0],'AWP':f[1],'LIP':int(f[2]),'LAW':law,'yield_TAB1':t})
  if law in (1,2):
   ne,i=tab2(sec,i)
   for _ in range(ne):i=skip_list(sec,i)
  elif law in (0,3,4):pass
  elif law==6:i+=1
  else:raise ValueError('UNSUPPORTED_LAW_'+str(law))
 assert i==len(sec),(i,len(sec))
 return {'header_fields':head,'LCT':int(head[3]),'NK':nk,'products':products,'end_consumed_exactly':True}

def main():
 out=BASE/'PHOTON_PROVIDER_ROWS.json'
 if out.exists():raise ValueError('NO_OVERWRITE_NO_REPLAY')
 t0=time.monotonic();c0=time.process_time();allrows=[];counts=[]
 specs=[('nndc_g-001_H_002.endf',128,50,'p_n_gamma',[8,12],{8:'target_forward',12:'target_reverse'},'EXCLUSIVE_NATIVE_CHANNEL'),('nndc_g-002_He_003.endf',225,5,'p_d_gamma',[7,13],{7:'target_forward',13:'target_reverse'},'FACTORIZED_EXCLUSIVE_CANDIDATE'),('nndc_g-003_Li_007.endf',328,5,'t_alpha_gamma',[11,19],{11:'target_forward',19:'target_reverse'},'INCLUSIVE_ONLY')]
 for name,mat,mt,fam,targets,directions,coverage in specs:
  p=BASE/'raw'/name;data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert sha==EXPECTED[name];lines=data.decode().splitlines()
  s3=section(lines,3,mt);cross,end=tab1(s3,1);assert end==len(s3)
  y=mf6_yields(section(lines,6,mt));assert all(int(x[66:70])==mat for x in lines if len(x)>=75 and x[70:72].strip() in ('3','6') and int(x[72:75])!=0)
  raw={'cross_section_TAB1':cross,'production_yield_TAB1s':y,'native_fields_are_strings':True}
  missing_cov=not any(len(x)>=75 and x[70:72].strip() in ('31','32','33','34','35','40') for x in lines)
  q={'value':cross['header_fields'][1] if mt==50 else None,'mass_difference_field':cross['header_fields'][0] if mt==50 else None,'unit':'eV','source_locator':{'MF':3,'MT':mt,'line_1based':cross['header_line_1based']},'qualification':'RAW_EVALUATION_Q_ONLY_UNAPPROVED' if mt==50 else 'MT5_ZERO_FIELDS_ARE_NOT_EXCLUSIVE_REACTION_Q','new_Q_computation':False,'Q_admitted':False}
  mapping={'native_branch': 'D(g,n)p; MF3/MT50 and both MF6 neutron/proton yields' if mat==128 else 'MF1 states deuteron production equals He3(g,p)D; retain sigma_MT5(E) and deuteron Y(E) as separate native tables' if mat==225 else 'MF3/MT5 total photoabsorption plus inclusive particle/residual yields; no exclusive Li7(g,t)alpha assignment', 'branch_resolution':'SOURCE_EXCLUSIVE_MT50' if mat==128 else 'FACTORIZATION_REQUIRES_NATIVE_GRID_AND_PRODUCT_BINDING' if mat==225 else 'EXCLUSIVE_BRANCH_UNRESOLVED', 'electron_charge_state':'UNRESOLVED_NATIVE_NUCLEAR_DATA_NOT_ATOMIC_STATE_DATA','nuclear_isomer':'native target LIS=0; full final-state excitation resolution not newly qualified','native_header_line_range_1based':[19,64] if mat==225 else [19,49] if mat==328 else [2,18]}
  row={'id':f'ENDFBVIII1_GAMMA_MAT{mat}_MF3MT{mt}_MF6_NATIVE','record_class':'PRIMARY_SOURCE_ROW','source_kind':'OFFICIAL_EVALUATED_ENDF_NATIVE_DATA','family_ids':[fam],'target_ids':targets,'direction':'family_reverse','target_directions':{str(k):v for k,v in directions.items()},'source_coverage':coverage,'exclusive_channel_binding':mat==128,'source_url':'https://www.nndc.bnl.gov/endf-releases/releases/B-VIII.1/gammas/gammas-version.VIII.1.tar.gz','source_file':'raw/'+name,'source_SHA256':sha,'source_bytes':len(data),'locator':{'archive_member':'gammas-version.VIII.1/'+name.removeprefix('nndc_'),'MAT':mat,'cross_section':{'MF':3,'MT':mt,'line_start_1based':s3[0][0],'line_end_1based':s3[-1][0]},'production_yields':{'MF':6,'MT':mt}},'raw_values':raw,'native_units':{'x':'eV incident photon energy','MF3_y':'barn','MF6_y':'product multiplicity per reaction; not automatically branch probability'},'native_support':{'cross_section_E_min_eV':cross['rows'][0]['x'],'cross_section_E_max_eV':cross['rows'][-1]['x'],'endpoint_policy':'native tabulation only; no extrapolation, interpolation or selected-spectrum fold performed','each_yield_uses_own_grid':True},'branch_and_state':mapping,'Q':q,'uncertainty':{'covariance_sections_present':not missing_cov,'numerical_uncertainty':None,'qualification':'NO_COVARIANCE_SECTION_IN_RECOVERED_NATIVE_FILE; unknown is not zero'},'source_attribution':'NNDC/CSEWG ENDF/B-VIII.1 photonuclear release; G.Hale LANL 2005 (H2), T.Murata JAEA 2003 (He3), 2013 (Li7); distribution2024-08-30','new_rate_admission':False,'new_nuclear_Q_admission':False,'activation':False,'new_rate_evaluations':0,'new_cross_section_products_evaluated':0}
  allrows.append(row);counts.append({'MAT':mat,'cross_section_knots':cross['NP'],'yield_products':y['NK'],'yield_knots':sum(z['yield_TAB1']['NP'] for z in y['products']),'source_coverage':coverage,'product_codes':[z['ZAP'] for z in y['products']]})
 packet={'schema':'WU_TARGET19_PHOTON_NATIVE_SOURCE_ROWS_V1','numeric_policy':'Native printed fields only; no interpolation, product multiplication, rate/IVP/Q calculation','rows':allrows,'counts':counts,'source_recovery_receipts':['NNDC_H2_RECOVERY.json','NNDC_HE3_LI7_RECOVERY.json'],'physical_admission':False}
 out.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n')
 receipt={'status':'PASS','source_parser_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'counts':counts,'CPU_s':time.process_time()-c0,'wall_s':time.monotonic()-t0,'new_rates':0,'new_Qs':0,'old_completed_replays':0}
 (BASE/'NATIVE_PARSE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
