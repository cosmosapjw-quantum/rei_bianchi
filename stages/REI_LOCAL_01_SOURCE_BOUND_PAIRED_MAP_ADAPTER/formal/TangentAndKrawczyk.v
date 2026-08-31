From Coq Require Import QArith.
Open Scope Q_scope.

Example locked_solution :
  2 * (1#5) + (3#5) == 1 /\ (1#5) + 3 * (3#5) == 2.
Proof. split; vm_compute; reflexivity. Qed.

Example full_tangent :
  2 * (14#25) + (-8#25) == 1 - (1#5) /\
  (14#25) + 3 * (-8#25) == -1 + (3#5).
Proof. split; vm_compute; reflexivity. Qed.

Example midpoint_only_is_wrong :
  ~ ((4#5) == (14#25) /\ (-3#5) == (-8#25)).
Proof. intros [H _]. vm_compute in H. discriminate. Qed.

Example mixed_products :
  13 - 1 - 11 - 8 == -7 /\ 17 - 2 - 7 - 5 == 3.
Proof. split; vm_compute; reflexivity. Qed.

Example two_by_two_margins :
  (-7#4) - (-9#4) == (1#2) /\
  (3#4) - (1#4) == (1#2) /\
  (-7#8) - (-9#8) == (1#4) /\
  (3#8) - (1#8) == (1#4).
Proof. repeat split; vm_compute; reflexivity. Qed.

Example three_by_three_margins :
  (-245#256) - (-9#8) == (43#256) /\
  (-1#8) - (-75#256) == (43#256) /\
  (-49#128) - (-1#2) == (15#128) /\
  0 - (-15#128) == (15#128) /\
  (-49#256) - (-1#4) == (15#256) /\
  0 - (-15#256) == (15#256).
Proof. repeat split; vm_compute; reflexivity. Qed.
