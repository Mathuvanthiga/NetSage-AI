# NetSage AI – Responsible AI Correction Log

The following five examples demonstrate required human oversight. These are sample review records to be validated during the actual Packet Tracer demo.

| Case | AI decision | Human decision | Why correction was needed |
|---|---|---|---|
| 4 | Suggested a routing problem | Edited | Evidence showed VLAN 30 was missing from the trunk allowed list, so the primary fault was Layer 2 trunk configuration. |
| 9 | Suggested DHCP failure | Rejected and corrected | The PC already had a valid IP, but its gateway was from another subnet. |
| 20 | Suggested server failure | Edited | ACL output explicitly denied TCP/80 traffic; server failure was not supported by evidence. |
| 28 | Suggested DNS issue | Rejected and corrected | Guest-to-internal ping succeeded and the guest ACL lacked an isolation rule; this was a security/ACL issue. |
| 30 | Suggested only a DHCP problem | Edited | Evidence showed three visible faults: wrong access VLAN, APIPA address, and VLAN 30 gateway interface down. |

## Human review policy
- Accepted: diagnosis is supported by evidence and needs no material correction.
- Edited: diagnosis is partly useful but human reviewer changes the cause, confidence, command, or fix.
- Rejected: diagnosis is unsupported or materially incorrect.
- Every accepted fix must be approved by a human reviewer.
