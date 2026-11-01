# Contrato de adaptador

Um adaptador leva o mesmo IR a outro executor e devolve **o mesmo veredito**.

## Assinatura

```python
decide(spec: dict) -> dict   # retorna ao menos: verdict, refusal_reason, p0, band, backend
```

## Regras obrigatórias

1. Construir o circuito a partir de `decision.n` e `decision.oracle` (constante ou paridade).
2. Medir a probabilidade de `|0…0⟩` (`p0`) e calcular a banda com
   `zqir.core.adaptive_margin(epsilon, shots, family)`.
3. Aplicar a regra normativa com `zqir.core.verdict_from_p0`.
4. Nunca inventar veredito: fora das três classes, `REFUSED` com motivo.

## Estado verificado

| Adaptador | Testado | Resultado |
|---|---|---|
| Qiskit (núcleo) | sim | 12/12 testes |
| Cirq 1.7 | sim | const1→`1`, paridade→`REFUSED` |
| PennyLane 0.45 | sim | const1→`1`, paridade→`REFUSED` |
| Amazon Braket 1.x | sim | const1→`1`, paridade→`REFUSED` (LocalSimulator) |

O modo hardware (IBM) é exercido pelo núcleo (`execution.backend = "ibm:<nome>"`).
