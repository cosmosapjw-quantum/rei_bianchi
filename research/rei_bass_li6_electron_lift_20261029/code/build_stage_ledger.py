"""Closeout-reconstructed stage audit index, not stage-time binary snapshots."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
commits={
'R1':'d09404a4d37313aba01d4e4e910ca4e21d3c5315','R2':'d9b38a35c75aa41ad0e458b0504284bb1c1892b8',
'R3':'4d6827df82d4157321be2b14d753942b046442e3','R4':'df76766fcc2f298e17e6883d2a6bf8987520122d',
'R5':'51fb78d04c3896937604b5607b2bc923a82af58f','R6':'a34dd72db0c7d8898b018ff50c08ea231728462c',
'R7':'cc4a7ebb050928744855d58393e1c5d098b9aa2d','R8':'ff3a79ed3d126941d1ad6f2708dc9682fc79c44d',
'R9':'b384cf9f48aeb466d734ddd3d617d623023e92ab','R10':'5b23b409dab14dae9a2c782d7ae031eed2f864ad',
'C1':'8006e94c9d360d093f7ee20a5681fdd0094563d1','C2':'b9c9c10ddadf99a1b23a46efa588a280e3ba7a23',
'C3':'7c4e20fd7d30d04e949fab57cda15609f570f4ca','C4':'620ec4c1ded898a5b363f2a573e8c461ef04150b',
'C5':'6077eb5edcaac04892bf90564a7efde038d27ecf','C6':'05d9c2f22f8531aac1e69d29ee280e201e0c2253',
'C7':'a63f481b9c0b9e5ba7b78091b6e922d8e73c448d','C8':'c0f1a4257cc6ab25bfd911d5bb871b1a6ed70f26',
'C9':'b83471ff75d606a6cd878cf2b93a2087599aaeb2','C10':'8f820ac6549306c40a32c5a3e7bf56ac1fd41ec3',
}
blobs={
'R1':'24d2edc4df39c7dbe09b951e84830717427911fc','R2':'2d8ba7fcf2420fdaa4439c4f8f18ad35bddc7ab1',
'R3':'6c906e7c2f7fbeceef25d8ec366c0214aa8c5eb4','R4':'bf6ea5a25bba77139e226fac2122e117c7a0d94b',
'R5':'64ac89d4d7c3e42fbbe0c2df7ccfb2262350e95c','R6':'7c91228283d93bcbbbb77ed8e97f605f658cf01d',
'R7':'19e3abc399bb6d0f79851ef9c57cc4f615c07456','R8':'66f877ecd23b227cf7c1f2dfdca3e4d6c29cce2a',
'R9':'175c3026cc2e9fb40b6a47d96238c32e681108a7','R10':'e2f3ad104890f9f52066db545ba9cb1c85544e34',
'C1':'1ed8cb2fdc11b9abce422f653c1bb14e152b7293','C2':'9ac3601bc7b240daf2f3f58b12fc8dc03874ce38',
'C3':'7310111b1ac10c9de2b2c32b3ddfe05b53729c1d','C4':'672809b5c6aafa17446b20e9ed4f3ce6477aab5d',
'C5':'149592ef9a5453492f27c7dd447dbdb1db8b4a07','C6':'53599e53f80866dfc49f7bd97e96b8faecd1bc84',
'C7':'ceeca1478794772681c1e36a7f754918bde22a5a','C8':'26dca1beb072d4b32023a36a56b6211ce4ce9631',
'C9':'09fbfaaadaf5803bc0303c3d17a1aef3ffd08890','C10':'6fca2ce7104cc5df39e38fb3e4102dc9a2876d3b',
}
assert len(commits)==len(blobs)==20
assert all(re.fullmatch('[0-9a-f]{40}',c) for c in (*commits.values(),*blobs.values()))
order=[f'R{i}' for i in range(1,11)]+[f'C{i}' for i in range(1,11)]
rows=[];count=0
for s in order:
 if s not in ('R6','C9'):count+=1
 row={'stage':s,'status':'HOLD_DISTINCT_AUTHOR' if s in ('R6','C9') else 'PASS_SCOPED',
      'science_completed':count,'total':20,'original_working':'33/88','original_central':'28/88',
      'physical_delta':0,'GitHub_stage_commit':commits[s], 'GitHub_stage_blob':blobs[s],
      'cloud_stage_binary_upload':'NOT_RUN','snapshot_semantics':'RECONSTRUCTED_AT_CLOSEOUT','source_authority':'GitHub stage blob above'}
 rows.append(row)
 (root/'stages'/f'{s}.json').write_text(json.dumps(row,indent=2)+'\n')
assert count==18
obj={'schema':'REI_BASS_LI6_LIFT_STAGE_LEDGER_V1','unit':'REI_BASS_LI6_ELECTRON_LIFT_20261029',
     'status':'18/20_SCOPED','original_working':'33/88','original_central':'28/88','physical_delta':0,
     'commit_identity':'Actual GitHub file commits and blob readbacks; stage JSON in this standalone archive are closeout reconstructions, not original Git stage bytes',
     'stage_commit_ack_count':20,'stage_blob_readback_count':20,'native_distinct_author_review':'NOT_RUN',
     'per_stage_Drive_Dropbox_binary_ACK':'NOT_RUN','stages':rows}
(root/'STAGE_LEDGER.json').write_text(json.dumps(obj,indent=2)+'\n')
print('stage ledger',count,'/',len(rows),'final',commits['C10'])
