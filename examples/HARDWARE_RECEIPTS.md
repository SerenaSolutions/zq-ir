# Recibos em silício — ibm_marrakesh

Execuções reais do contrato ZQ-IR, com job IDs verificáveis na IBM.

| Caso | Veredito | p0 | banda | job |
|---|---|---|---|---|
| `decide_const1.json` | `1` | 1.0000 | 0.03001 | `dbj9h11kdqps7390505g` |
| porta GHZ (n=2, 4096 shots) | passou | fidelidade 0.9875 | limiar 0.80 | `dbj9gd56p51s73ckcdrg` |
| `decide_parity.json` | `REFUSED` (`BALANCED_ORACLE`) | 0.005859 | 0.03001 | `dbj9h61ffo6c73b972n0` |

Selos SHA3-256 nos JSONs ao lado (`receipt_hardware_const1.json`,
`receipt_hardware_parity.json`) — recomputáveis offline.

O mesmo `spec.json` usado aqui roda em Qiskit, Cirq, PennyLane ou qualquer linguagem
que fale JSON: o veredito não pertence a nenhum framework.
