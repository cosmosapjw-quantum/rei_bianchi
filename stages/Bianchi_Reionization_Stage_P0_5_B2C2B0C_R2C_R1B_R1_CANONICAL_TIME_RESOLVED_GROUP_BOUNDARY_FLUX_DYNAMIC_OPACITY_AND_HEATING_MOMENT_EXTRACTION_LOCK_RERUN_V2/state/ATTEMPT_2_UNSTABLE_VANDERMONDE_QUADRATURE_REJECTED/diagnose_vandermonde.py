import numpy as np
for n in (9,17,33):
    x=np.sort((1-np.cos(np.pi*np.arange(n)/(n-1)))/2)
    A=np.vstack([x**k for k in range(n)])
    b=np.array([1/(k+1) for k in range(n)])
    try:
        w=np.linalg.solve(A,b)
        print(n, "condition", np.linalg.cond(A), "l1", np.linalg.norm(w,1), "maxabs", np.max(np.abs(w)))
    except np.linalg.LinAlgError as exc:
        print(n, "condition", np.linalg.cond(A), "FAILED", repr(exc))
