"""R31R depth-first discriminator planning for the failed R31Q interpolation gate."""
from __future__ import annotations
import math
import struct

PARENT_FAILED_INTERVAL=(0.0,8.0)
PARENT_DIRECT_MIDPOINT=4.0
FIRST_CHILD_INTERVAL=(0.0,4.0)
FIRST_DISCRIMINATOR_NODE=2.0
SIBLING_DISCRIMINATOR_NODE=6.0
H_ORDERS=(160,192)
MIN_INTERVAL_WIDTH_A0=1.0


def h_folder_name(n:int,z:float,g:int=80,scale:str='unit')->str:
    if n not in H_ORDERS or g!=80 or scale!='unit':
        raise ValueError('R31R H source uses frozen B160/B192 g80 unit-scale contract')
    z=float(z)
    if not math.isfinite(z) or z<0 or z>64:
        raise ValueError('z outside frozen positive domain')
    return f'B{n}_g{g}_s{scale}_z{struct.pack(">d",z).hex()}'


def first_discriminator_plan()->dict:
    return {
        'schema':'WU088_R31R_DEPTH_FIRST_DISCRIMINATOR_PLAN_V1',
        'parent_failed_interval':list(PARENT_FAILED_INTERVAL),
        'parent_direct_midpoint':PARENT_DIRECT_MIDPOINT,
        'child_interval_under_test':list(FIRST_CHILD_INTERVAL),
        'direct_node':FIRST_DISCRIMINATOR_NODE,
        'sibling_node_deferred':SIBLING_DISCRIMINATOR_NODE,
        'h_orders':list(H_ORDERS),
        'od_z':[FIRST_DISCRIMINATOR_NODE],
        'jvp_z':[FIRST_DISCRIMINATOR_NODE],
        'ionic_reuse_cp4':[FIRST_DISCRIMINATOR_NODE],
        'interpolation_evaluated':False,
        'trajectory_runs':0,
        'trajectory_admitted':False,
        'production_admitted':False,
        'minimum_interval_width_a0':MIN_INTERVAL_WIDTH_A0,
        'execution_strategy':'DEPTH_FIRST_EARLY_STOP_ON_GLOBAL_UNRESOLVED_INTERVAL',
    }


def next_after_z2(*,z2_interval_pass:bool)->dict:
    if z2_interval_pass:
        return {
            'status':'OPEN_SIBLING_CHILD_TEST',
            'next_direct_node':6.0,
            'interval':[4.0,8.0],
            'reason':'[0,4] passed; [4,8] remains untested inside failed parent [0,8]'
        }
    return {
        'status':'DESCEND_FAILED_CHILD_DEPTH_FIRST',
        'next_allowed_direct_nodes':[1.0,3.0],
        'preferred_next_direct_node':1.0,
        'interval':[0.0,4.0],
        'reason':'[0,4] failed; bisect only this failing child before spending on sibling/current-domain intervals'
    }
