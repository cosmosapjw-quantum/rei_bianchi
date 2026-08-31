from itertools import product

def check(condition, label):
    if not condition:
        raise AssertionError(label)

Q = QQ
A = matrix(Q, [[2, 1], [1, 3]])
dA = matrix(Q, [[1, 0], [0, -1]])
b = vector(Q, [1, 2])
db = vector(Q, [1, -1])
z = A.solve_right(b)
dz = A.solve_right(db - dA * z)
wrong = A.solve_right(db)
check(z == vector(Q, [1/5, 3/5]), "locked solution")
check(dz == vector(Q, [14/25, -8/25]), "full tangent")
check(wrong == vector(Q, [4/5, -3/5]) and wrong != dz,
      "delta-A counterexample")

M = matrix(Q, [[2, -1], [-1, 1]])
full_rhs = vector(Q, [-7, 3])
terms = [vector(Q, [1, 2]), vector(Q, [11, 7]), vector(Q, [8, 5])]
check(vector(Q, [13, 17]) - sum(terms) == full_rhs,
      "mixed RHS all products")
check(M.solve_right(full_rhs) == vector(Q, [-4, -1]), "mixed solution")
check([M.solve_right(full_rhs + t) for t in terms] ==
      [vector(Q, [-1, 4]), vector(Q, [14, 24]), vector(Q, [9, 17])],
      "mixed zero-term mutations")

C = matrix(Q, [[2/3, 1/3], [1/3, 2/3]])
w = vector(Q, [-3/4, -3/8])
X = [(Q(-9)/4, Q(3)/4), (Q(-9)/8, Q(3)/8)]
values = [[], []]
for a, r, x0, x1 in product([Q(3)/2, Q(5)/2],
                             [Q(-3)/2, Q(-3)/4], X[0], X[1]):
    Ai = matrix(Q, [[a, -1], [-1, 2]])
    bi = vector(Q, [r, 0])
    x = vector(Q, [x0, x1])
    k = w - C * (Ai * w - bi) + (identity_matrix(Q, 2) - C * Ai) * (x - w)
    for i in range(2):
        values[i].append(k[i])
K = [(min(v), max(v)) for v in values]
check(K == [(Q(-7)/4, Q(1)/4), (Q(-7)/8, Q(1)/8)],
      "2x2 Krawczyk hull")
check([K[0][0]-X[0][0], X[0][1]-K[0][1],
       K[1][0]-X[1][0], X[1][1]-K[1][1]] ==
      [Q(1)/2, Q(1)/2, Q(1)/4, Q(1)/4], "2x2 margins")

X3 = [(Q(-9)/8, Q(-1)/8), (Q(-1)/2, Q(0)), (Q(-1)/4, Q(0))]
K3 = [(Q(-245)/256, Q(-75)/256), (Q(-49)/128, Q(-15)/128),
      (Q(-49)/256, Q(-15)/256)]
check(all(xl < kl and ku < xu for (xl, xu), (kl, ku) in zip(X3, K3)),
      "3x3 strict inclusion")
check([(kl-xl, xu-ku) for (xl, xu), (kl, ku) in zip(X3, K3)] ==
      [(Q(43)/256, Q(43)/256), (Q(15)/128, Q(15)/128),
       (Q(15)/256, Q(15)/256)], "3x3 margins")
print("PASS exact tangent/mixed/Krawczyk arithmetic")
