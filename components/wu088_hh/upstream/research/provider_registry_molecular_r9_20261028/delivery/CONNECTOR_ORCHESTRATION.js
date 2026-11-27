function decodeBase64(s){const chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",map={};for(let i=0;i<64;i++)map[chars[i]]=i;const out=[];let b=0,bits=0;for(const c of s){if(c==="=")break;if(!(c in map))throw Error("Invalidbase64");b=(b<<6)|map[c];bits+=6;if(bits>=8){bits-=8;out.push((b>>bits)&255);b&=(1<<bits)-1;}}return out;}
function utf8Text(bytes){const out=[];for(let i=0;i<bytes.length;){let p=bytes[i++];if(p<128){out.push(String.fromCharCode(p));continue;}let n;if((p&224)===192){n=1;p&=31;}else if((p&240)===224){n=2;p&=15;}else if((p&248)===240){n=3;p&=7;}else throw Error("UTF8");for(let k=0;k<n;k++){const x=bytes[i++];if((x&192)!==128)throw Error("UTF8cont");p=(p<<6)|(x&63);}out.push(String.fromCodePoint(p));}return out.join("");}
function utf8Bytes(s){const a=[];for(const c of s){const p=c.codePointAt(0);if(p<128)a.push(p);else if(p<2048)a.push(192|(p>>6),128|(p&63));else if(p<65536)a.push(224|(p>>12),128|((p>>6)&63),128|(p&63));else a.push(240|(p>>18),128|((p>>12)&63),128|((p>>6)&63),128|(p&63));}return a;}
function sha256Hex(input){const a=Array.from(input),n=a.length;if(n>=536870912)throw Error("Size");const bit=n*8;a.push(128);while(a.length%64!==56)a.push(0);for(let k=7;k>=0;k--)a.push(k>=4?0:(bit>>>(k*8))&255);
const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],rot=(x,n)=>(x>>>n)|(x<<(32-n));
for(let p=0;p<a.length;p+=64){const w=new Array(64);for(let i=0;i<16;i++)w[i]=(a[p+4*i]<<24)|(a[p+4*i+1]<<16)|(a[p+4*i+2]<<8)|a[p+4*i+3];for(let i=16;i<64;i++){const x=w[i-15],y=w[i-2];w[i]=(w[i-16]+(rot(x,7)^rot(x,18)^(x>>>3))+w[i-7]+(rot(y,17)^rot(y,19)^(y>>>10)))|0;}let[A,B,C,D,E,F,G,J]=H;for(let i=0;i<64;i++){const t1=(J+(rot(E,6)^rot(E,11)^rot(E,25))+((E&F)^(~E&G))+K[i]+w[i])|0,t2=((rot(A,2)^rot(A,13)^rot(A,22))+((A&B)^(A&C)^(B&C)))|0;J=G;G=F;F=E;E=(D+t1)|0;D=C;C=B;B=A;A=(t1+t2)|0;}[A,B,C,D,E,F,G,J].forEach((v,i)=>H[i]=(H[i]+v)|0);}return H.map(x=>(x>>>0).toString(16).padStart(8,"0")).join("");}
function parseLogs(stage,logs){const metas={},chunks={};let tr;
for(const line of logs.split("\n"))for(const tag of["R9_TRANSPORT ","R9_FILE_META ","R9_FILE_CHUNK "]){const i=line.indexOf(tag);if(i<0)continue;const o=JSON.parse(line.slice(i+tag.length));if(tag==="R9_TRANSPORT ")tr=o;else if(tag==="R9_FILE_META ")metas[o.path]=o;else{if(!chunks[o.path])chunks[o.path]=[];if(chunks[o.path][o.i]!==undefined)throw Error("Duplicatechunk");chunks[o.path][o.i]=o.b64;}}
if(!tr)throw Error("Noarchive");const runtime={},identities=[];
for(const[p,m]of Object.entries(metas)){const parts=chunks[p]||[];if(parts.length!==m.chunks||parts.filter(x=>typeof x==="string").length!==m.chunks)throw Error("Missingchunks");const bytes=decodeBase64(parts.join(""));if(bytes.length!==m.bytes||sha256Hex(bytes)!==m.sha256)throw Error("Hashmismatch"+p);const s=utf8Text(bytes);identities.push({...m,verified:true});if(p==="CHECKPOINT_MANIFEST.json")store("r9_"+stage+"_manifest",JSON.parse(s));else runtime[p]=s;}
return {transport:tr,runtime,identities};}

async function publishR9(stage,message,exclude=[]){
 const files=load("r9_files"),previous=load("r9_published_files")||{};
 const changes=Object.entries(files).filter(([p,c])=>previous[p]!==c&&!exclude.includes(p));
 if(!changes.length)throw Error("Nochanges");
 const repo="cosmosapjw-quantum/WU088_HH",parent=load("r9_head");
 const t=await tools.mcp__codex_apps__github_create_tree({repository_full_name:repo,base_tree_sha:load("r9_tree"),tree_elements:changes.map(([path,content])=>{const k=(load("r9_known_blobs")||{})[path];return k&&k.content===content?{path,mode:"100644",type:"blob",sha:k.sha}:{path,mode:"100644",type:"blob",content};})});
 if(t.isError||!t.structuredContent?.sha)throw Error("Treefailed");
 const tree=t.structuredContent.sha;
 const c=await tools.mcp__codex_apps__github_create_commit({repository_full_name:repo,parent_sha:parent,tree_sha:tree,message});
 if(c.isError||!c.structuredContent?.sha)throw Error("Commitfailed");
 const sha=c.structuredContent.sha;
 const r=await tools.mcp__codex_apps__github_update_ref({repository_full_name:repo,branch_name:"research/provider-registry-20261025",expected_sha:parent,sha,force:false});
 if(r.isError||!r.structuredContent?.success)throw Error("Refrejected;inspectactualhead");
 const rb=await tools.mcp__codex_apps__github_fetch({url:"https://api.github.com/repos/"+repo+"/git/ref/heads/research/provider-registry-20261025"});
 if(rb.isError||JSON.parse(rb.structuredContent.content).object.sha!==sha)throw Error("Headreadbackmismatch");
 store("r9_head",sha);store("r9_tree",tree);store("r9_"+stage+"_commit",sha);
 for(const[p,s]of changes)previous[p]=s;store("r9_published_files",previous);
 const pub={stage,source_commit:sha,source_tree:tree,parent,changed_files:changes.length,DAG:load("r9_dag").counts,ref_readback:"MATCH",force:false};store("r9_"+stage+"_publication",pub);text(pub);return sha;
}

async function finishR9(stage){
 const repo="cosmosapjw-quantum/WU088_HH",sha=load("r9_"+stage+"_commit");if(!sha)throw Error("Missingcommit");
 if(load("r9_"+stage+"_receipt"))return load("r9_"+stage+"_receipt");
 let run=load("r9_"+stage+"_run"),job=load("r9_"+stage+"_job"),art=load("r9_"+stage+"_artifact"),parsed=load("r9_"+stage+"_parsed");
 if(!parsed){
 const rr=await tools.mcp__codex_apps__github_fetch({url:"https://api.github.com/repos/"+repo+"/actions/runs?branch=research%2Fprovider-registry-20261025&per_page=8"});if(rr.isError)throw Error("Runread");
 run=JSON.parse(rr.structuredContent.content).workflow_runs.find(x=>x.head_sha===sha&&x.name==="WU R9 bounded research checkpoint");
 if(!run||run.status!=="completed"){text({stage,status:"RUN_PENDING",run_id:run?.id});return null;}
 const r=await Promise.allSettled([tools.mcp__codex_apps__github_fetch_workflow_run_artifacts({repo_full_name:repo,run_id:run.id}),tools.mcp__codex_apps__github_fetch_workflow_run_jobs({repo_full_name:repo,run_id:run.id})]);
 for(const x of r)if(x.status!=="fulfilled"||x.value.isError)throw Error("Actionsmetadata");
 job=r[1].value.structuredContent.jobs.find(x=>x.name==="checkpoint");
 const logs=await tools.mcp__codex_apps__github_fetch_workflow_job_logs({repo_full_name:repo,job_id:job.id});store("r9_"+stage+"_logs",logs);
 if(!logs.structuredContent.content.includes("R9_TRANSPORT ")){text({stage,status:"NOARCHIVE",conclusion:run.conclusion,errors:logs.structuredContent.content.split("\n").filter(x=>/Error|error|Traceback/.test(x)).slice(-15)});return null;}
 parsed=eval(load("r9_codec")+"\nparseLogs("+JSON.stringify(stage)+",load("+JSON.stringify("r9_"+stage+"_logs")+").structuredContent.content)");
 art=r[0].value.structuredContent.artifacts.find(x=>x.name===parsed.transport.archive_name);
 store("r9_"+stage+"_parsed",parsed);store("r9_"+stage+"_run",run);store("r9_"+stage+"_job",job);store("r9_"+stage+"_artifact",art);
 }
 const tr=parsed.transport;if(tr.source_commit!==sha||!art||art.digest!=="sha256:"+tr.archive_sha256||art.size_in_bytes!==tr.archive_bytes)throw Error("Artifactidentity");
 const files=load("r9_files"),base=load("r9_base");for(const[p,s]of Object.entries(parsed.runtime)){if(!/^raw\/[A-Z0-9_]+\.(json|txt)$/.test(p))throw Error("Runtimepath");files[base+"/"+p]=s;}store("r9_files",files);
 let dr=load("r9_"+stage+"_drive_upload"),db=load("r9_"+stage+"_dropbox_status")||load("r9_"+stage+"_dropbox_upload");
 if(!dr||dr.isError||!db||db.isError){
  const down=await tools.mcp__codex_apps__github_download_workflow_artifact({repo_full_name:repo,artifact_id:art.id,file_name:tr.archive_name});if(down.isError)throw Error("Artifactdownload");store("r9_"+stage+"_download",down);const file=down.structuredContent.file_uri;
  if(!dr||dr.isError){dr=await tools.mcp__codex_apps__google_drive_upload_file({file_uri:file,file_name:tr.archive_name,mime_type:"application/zip",parent_folder_id:"1074Hr5msnAMgIXWU-PmgdMrQvrdV6emM"});store("r9_"+stage+"_drive_upload",dr);if(dr.isError||!dr.structuredContent?.success)throw Error("Driveuploadfailed");}
  if(!db||db.isError){db=await tools.mcp__codex_apps__dropbox_upload_file({source_file:file,destination_path:"ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31S_NCP_REDESIGN_20260928/"+tr.archive_name});store("r9_"+stage+"_dropbox_upload",db);if(db.isError)throw Error("Dropboxuploadfailed");}
 }
 let st=db.structuredContent;if(st.status==="in_progress"){await new Promise(resolve=>setTimeout(resolve,1000));db=await tools.mcp__codex_apps__dropbox_check_upload_file_status({operation_id:st.operation_id,wait_ms:5000});store("r9_"+stage+"_dropbox_status",db);st=db.structuredContent;}
 if(st.status!=="completed"){text({stage,status:"DROPBOX_PENDING"});return null;}
 const drive=dr.structuredContent.id,drop=st.file.file_id;
 const orig=await Promise.allSettled([tools.mcp__codex_apps__google_drive_fetch({url:"https://drive.google.com/file/d/"+drive+"/view",download_raw_file:true,include_base64:false}),tools.mcp__codex_apps__dropbox_download_link({entries:[drop],expiration_in_sec:600})]);
 for(const x of orig)if(x.status!=="fulfilled"||x.value.isError)throw Error("Originalreadback");
 const urls=[orig[0].value.structuredContent.file_uri.download_url,orig[1].value.structuredContent.entries[0].download_url],used=load("r9_transport_calls")||0;
 if(used>=11)throw Error("Metadataallowanceexhausted");store("r9_transport_calls",used+1);
 const code='Module[{urls={'+urls.map(x=>JSON.stringify(x)).join(",")+'},labels={"Drive","Dropbox"},p,r},Table[p=CreateTemporary[];r=TimeConstrained[URLDownload[urls[[i]],p],12,$Failed];If[r===$Failed,<|"provider"->labels[[i]],"status"->"FAILED"|>,With[{out=<|"provider"->labels[[i]],"bytes"->FileByteCount[p],"sha256"->FileHash[p,"SHA256","HexString"]|>},DeleteFile[p];out]],{i,2}]]';
 const hs=await tools.mcp__codex_apps__wolfram_wolframlanguageevaluator({code,timeConstraint:30});store("r9_"+stage+"_original_hash",hs);
 const out=hs.content.filter(x=>x.type==="text").map(x=>x.text).join("\n"),matches=[...out.matchAll(/"provider"\s*->\s*"([^"]+)"[\s\S]*?"bytes"\s*->\s*(\d+)[\s\S]*?"sha256"\s*->\s*"([a-f0-9]{64})"/g)];
 if(hs.isError||matches.length!==2||matches.some(m=>Number(m[2])!==tr.archive_bytes||m[3]!==tr.archive_sha256))throw Error("Originalhashmismatch"+out);
 const receipt={schema:"WU_R9_STAGE_DELIVERY_V1",stage,DAG:load("r9_dag").counts,source_commit:sha,source_tree:tr.source_tree,archive:{name:tr.archive_name,bytes:tr.archive_bytes,sha256:tr.archive_sha256,source_files:tr.source_files,runtime_files:tr.runtime_files,scope:"R4-R9 molecularleaves+AGENTS+R9workflow; notwholeGit history"},github:{run_id:run.id,job_id:job.id,artifact_id:art.id,conclusion:run.conclusion},drive:{file_id:drive,upload:"SUCCESS",original_GET_bytes:tr.archive_bytes,original_SHA256:tr.archive_sha256},dropbox:{file_id:drop,path_display:st.file.path_display,upload:"COMPLETED",original_GET_bytes:tr.archive_bytes,original_SHA256:tr.archive_sha256},readback:{status:"DUAL_ORIGINAL_BYTES_VERIFIED",metadata_Wolfram_call:used+1},runtime_identity_checks:parsed.identities.filter(x=>x.path!=="CHECKPOINT_MANIFEST.json"),process:tr.process};
 store("r9_"+stage+"_receipt",receipt);files[base+"/delivery/"+stage+".json"]=JSON.stringify(receipt,null,2)+"\n";
 const idx=load("r9_publication_index");idx.stages.push(receipt);idx.dual_original_byte_verified_stages=idx.stages.filter(x=>/^S\d{2}$/.test(x.stage)).length;idx.final_metadata_original_bytes_verified=idx.stages.some(x=>x.stage==="FINAL");store("r9_publication_index",idx);files[base+"/delivery/PUBLICATION_INDEX.json"]=JSON.stringify(idx,null,2)+"\n";
 const ledger=JSON.parse(files[base+"/EXECUTION_LEDGER.json"]);ledger.metadata_actions.push({id:stage+"_DUAL_ORIGINAL_HASH",scientific:false,source:"delivery/"+stage+".json"});ledger.metadata_original_byte_pairs={allowed:11,consumed:used+1,remaining:10-used};
 if(tr.process){ledger[tr.action]={allowed:1,consumed:1,remaining:0,status:run.conclusion,source_commit:sha,process:tr.process};ledger.scientific_runs.push(tr.process);}
 if(stage==="S01")ledger.failures.push({class:"environment/transport",status:"CLOSED_BY_FRESH_FILE_REFERENCE",target:"Initial S01 Drive source download",observed:"HTTP403 with expired transient download URL; refreshed artifact reference then immediately uploaded successfully",scientific_executions:0});
 files[base+"/EXECUTION_LEDGER.json"]=JSON.stringify(ledger,null,2)+"\n";store("r9_files",files);
 text({stage,commit:sha,archive_bytes:tr.archive_bytes,archive_sha256:tr.archive_sha256,Drive:drive,Dropbox:drop,dual_original_bytes:"PASS",DAG:load("r9_dag").counts,workflow:load("r9_workflow").workflow_complete,process:tr.process});return receipt;
}
