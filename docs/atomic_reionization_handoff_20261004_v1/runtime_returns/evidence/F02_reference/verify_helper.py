from pathlib import Path
import json,subprocess,sys,tempfile
p=Path(__file__).resolve().parent
source=Path(sys.argv[1]).read_text()
cases=json.loads((p/'helper-oracle.json').read_text())
assertions=''.join(f'let a=one_minus_phi1({t}_f64); assert!((a-({v:.17e})).abs()<=4e-14*({v:.17e}), "t={t}: {{a:e}}");' for t,v in cases)
with tempfile.TemporaryDirectory() as d:
 r=Path(d);(r/'main.rs').write_text(source+'\nfn main(){'+assertions+'assert_eq!(one_minus_phi1(0.0),0.0);}')
 subprocess.run(['/home/cosmosapjw/.cargo/bin/rustc',str(r/'main.rs'),'-o',str(r/'check')],check=True)
 subprocess.run([str(r/'check')],check=True,timeout=5)
print('Decimal(90) references: 7 cases and zero identity PASS')
