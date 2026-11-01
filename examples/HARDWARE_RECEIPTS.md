# Recibos em silício — ibm_marrakesh

Execuções reais do contrato ZQ-IR, com job IDs verificáveis na IBM e selos
recomputáveis offline (`zqir.core.verify_receipt`).

| Caso | Veredito | p0 | banda | job |
|---|---|---|---|---|
| `decide_const1.json` | `1` | 1.0000 | 0.03001 | `dbjagn8nceqs73ajk900` |
| porta GHZ (n=2) | passou | fidelidade 0.9849 | limiar 0.80 | `dbjagjpkdqps739076s0` |
| `decide_parity.json` | `REFUSED` (`BALANCED_ORACLE`) | 0.016113 | 0.03001 | `dbjagql6p51s73ckelag` |

**Correção de auditoria (2026-11-01):** a primeira emissão destes recibos tinha o
`sealed_at` dentro do corpo selado mas fora do arquivo, o que tornava o selo
irrecomputável — um recibo que não pode ser conferido não sela nada. O corpo selado
passou a ser embutido no recibo (`receipt.payload`) e `verify_receipt()` recomputa
SHA3-256 offline. Os cases acima foram reexecutados no silício com a correção.

O mesmo `spec.json` roda em Qiskit, Cirq, PennyLane, Braket ou qualquer linguagem
que fale JSON: o veredito não pertence a nenhum framework.
