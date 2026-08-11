# Negative results preserved

1. **Centered finite-difference false negative.** On population scales near
   `cMpc^-3` counts, centered subtraction produced a spurious tangent mismatch.
   The attempt is preserved under
   `attempts/ATTEMPT_CENTERED_FD_POPULATION_SCALE_CANCELLATION/`. Complex-step
   replay reduced the maximum relative mismatch to `3.3717708261732545e-15`.
2. **Static-corner enclosure rejected.** An admissible upper-to-lower schedule
   passes every inherited physical gate but exits the static hull in `x_HeIII`
   by `6.9791494632098772e-12`, or
   `0.033079776479960625` of the inherited width.
3. **Endpoint event-distance overclaim rejected.** The inherited corner envelope
   remains `0.00029156361921245377` in `log T` from its
   nearest table knot, but this does not bound the unclosed four-site remainder.
4. **Physical nonexistence is not inferred.** Every tested trajectory and local
   solve remains regular. The failure is a missing validated representation,
   not a no-solution theorem.
