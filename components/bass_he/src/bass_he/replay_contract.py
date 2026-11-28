"""Pure DR11 replay inputs and acceptance gates shared with cloud runner."""
BRANCHES={
 'S_3p_sigma_4p_sigma':((3,1,0),(4,1,0),complex(.490824831704868,.7201512942653545)),
 'S_3d_sigma_4d_sigma':((3,2,0),(4,2,0),complex(1.9861101965857686,1.3649585042669394)),
 'Q_3p_sigma_4d_sigma':((3,1,0),(4,2,0),complex(7.9283658479841215,3.2285957034060395)),
 'Q_3p_pi_4d_pi':((3,1,1),(4,2,1),complex(3.3246903179815623,5.069402501109532)),
 'Q_3d_sigma_4f_sigma':((3,2,0),(4,3,0),complex(7.36009269188776,4.39297617387613)),
 'Q_3d_pi_4f_pi':((3,2,1),(4,3,1),complex(11.819211257373258,3.977637384885511)),
 'Q_3d_delta_4f_delta':((3,2,2),(4,3,2),complex(6.5362889891415,6.486618399302258)),
}
CONTROL_SEED=complex(1.2125718090356707,1.363814370435508)
CONTROL_PAIR=((1,0,0),(2,1,0))
WRONG_PAIR=((1,0,0),(2,0,0))
DEPTH=160
FRACTIONS=(0.0,0.25,0.5,0.75)
PANELS=(32,64)
SOURCE_DELTA=1.42615
SOURCE_REL_LIMIT=1e-4
EP_DISTANCE_LIMIT=1e-8
RESIDUAL_LIMIT=5e-9
SHEET_GAP_MIN=1e-6
def panel_limit(fraction): return 1e-4 if fraction==0 else 5e-4
