# Nonlinear diagnostic delivery summary

Reviewed C9 code: `e0d547521cd71047670d5c3967ca4289ea0db8b1`. Independent verdict: `PASS_SCOPED` for the supplied-packet linearized diagnostic. Actual accepted-state telemetry is missing; actual-stage attribution remains HOLD.

The containing commit is the final C10 publication. Exact archive/provider identities and package-only verification are recorded in `DELIVERY_LOG.json`; the publisher response identifies the actual C10 commit. Completed provider acknowledgment plus matching size is not an independent remote-byte redownload.

| Stage | Published commit | Archive bytes |
|---|---|---:|
| R1 | `d69fa36b0ea7a2868dcd95d0a7899b78b9aae622` | 21159 |
| R2 | `3f68d45aeffc3466d85cd3f46f368ea3f12a545a` | 23283 |
| R3 | `f11dbe3c388d9a609b49cb36a3665336f92929bf` | 25097 |
| R4 | `5a1269371854ad674902a6f8ed083f826cbeff89` | 26624 |
| R5 | `70d0f5eff8db72c50deac9fbf01409812058e808` | 31046 |
| R6 | `2e8b40cd22cbfedd435cd10e558a54d9fdb42ada` | 40433 |
| R7 | `aa789a7e6b65348887f23675207e43cd68b64ecd` | 51487 |
| R8 | `b8c9e2808c5354ee655c6629cddeeca5e83715d3` | 52497 |
| R9 | `fcca22673eac4294c432089b3cf9758fb26b4692` | 56976 |
| R10 | `911f660c6e28ee30c4e15006b5166de812b881aa` | 57978 |
| C1 | `e2240c96bec6af3b1a9196ec5b04f7051603a11b` | 62068 |
| C2 | `b56c073f51152263cc82e6561f9a427ab07cd5b4` | 63526 |
| C3 | `35d9747a0bbedcafdb568467ce7c1e7a25f965b6` | 64943 |
| C4 | `fe8f1566803108d7d3fd72e8cc84e04e51693140` | 66453 |
| C5 | `6513fd94a7042023c626c00d1e1d2d0afd045129` | 79944 |
| C6 | `09d4cd3964ce67ea239320013fd26b94bbec92b2` | 82444 |
| C7 | `0631b47b6b3a3c94af35fbe730f81aea45333487` | 86605 |
| C8 | `4e751d077357c8fb00fd94ec18c9a57decb8db44` | 90829 |
| C9 | `e0d547521cd71047670d5c3967ca4289ea0db8b1` | 96217 |
| C10 | Containing commit | See final package receipt |

All twenty stage facts are retained through owner records, DAG nodes, evidence and checkpoint metadata. Prior snapshots are immutable; the forward-only summary metadata correction is described in the delivery log.

Next unit-local owner intake is O1. Canonical execution routing and concurrent SOURCE work remain owned by their existing controllers. The canonical update changes only the approved `nonlinear_error_budget` key.
