import Mathlib

namespace REILocal01

theorem locked_solution :
    (2 : ℚ) * (1 / 5) + (3 / 5) = 1 ∧
    (1 / 5 : ℚ) + 3 * (3 / 5) = 2 := by norm_num

theorem full_tangent :
    (2 : ℚ) * (14 / 25) + (-8 / 25) = 1 - (1 / 5) ∧
    (14 / 25 : ℚ) + 3 * (-8 / 25) = -1 + (3 / 5) := by norm_num

theorem midpoint_only_is_wrong :
    ((4 / 5 : ℚ), (-3 / 5 : ℚ)) ≠ ((14 / 25 : ℚ), (-8 / 25 : ℚ)) := by
  norm_num

theorem mixed_products :
    ((13 : ℚ) - 1 - 11 - 8, (17 : ℚ) - 2 - 7 - 5) = (-7, 3) := by
  norm_num

theorem two_by_two_margins :
    ((-7 / 4 : ℚ) - (-9 / 4), (3 / 4 : ℚ) - (1 / 4),
      (-7 / 8 : ℚ) - (-9 / 8), (3 / 8 : ℚ) - (1 / 8)) =
    (1 / 2, 1 / 2, 1 / 4, 1 / 4) := by norm_num

theorem three_by_three_margins :
    ((-245 / 256 : ℚ) - (-9 / 8), (-1 / 8 : ℚ) - (-75 / 256),
      (-49 / 128 : ℚ) - (-1 / 2), (0 : ℚ) - (-15 / 128),
      (-49 / 256 : ℚ) - (-1 / 4), (0 : ℚ) - (-15 / 256)) =
    (43 / 256, 43 / 256, 15 / 128, 15 / 128, 15 / 256, 15 / 256) := by
  norm_num

end REILocal01
