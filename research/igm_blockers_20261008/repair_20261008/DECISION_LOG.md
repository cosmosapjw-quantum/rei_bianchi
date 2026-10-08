# Decision log

Decision: `HOLD_PAIRED_NODE_PATH_REQUIRED`.

The local photoheat fix is retained because it resolves the proven false refusal and passes the first common refinement row under unchanged gates. The conditional kernel reassociation is also retained as the one allowed local response to the next captured failure; it fixes a demonstrated premature subnormal projection and preserves NORMAL-route bits.

The full suffix is not promoted. Two attempts at coarse k14 after the kernel repair end at the same paired-readout boundary. Continuing by removing the pair check would create an unrepresented energy component in accepted state and restart. The stopping rule therefore applies.

Alternatives rejected in this work unit: heat clamping, a numerical floor, global subnormal guard relaxation, tolerance increase, and scalar pair mismatch acceptance without a state/codec/observer representation.
