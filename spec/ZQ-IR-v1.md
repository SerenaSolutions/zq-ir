# ZQ-IR v1 — Interpretador Universal de Decisão Trivalente

**O que é:** um formato neutro de decisão quântica. Qualquer ecossistema (Qiskit, PennyLane,
Cirq, Amazon Braket, OpenQASM 3, Q#, ou uma linguagem qualquer) descreve a decisão em JSON,
e o portão devolve um veredito `1` / `0` / `REFUSED` com recibo selado.

**Por que existe:** cada framework tem seu jeito de medir, amostrar e reportar. O veredito
trivalente não pertence a nenhum deles — é uma decisão sobre evidência. O ZQ-IR é o contrato
mínimo para que essa decisão seja portável e auditável entre ecossistemas.

---

## 1. Especificação de entrada

```json
{
  "zqir": "1.0",
  "decision": {
    "id": "demo-001",
    "purpose": "texto livre — o que esta decisão afirma",
    "n": 2,
    "oracle": {"type": "constant", "value": 1},
    "shots": 2048,
    "epsilon": 0.05,
    "family": 1,
    "device_gate": {"type": "ghz", "threshold": 0.80},
    "memory_gate": {"enabled": false, "steps": 4}
  },
  "execution": {"backend": "simulator", "seed": 1701},
  "receipt": {"enabled": true, "chain": false, "previous_seal": null}
}
```

### Campos obrigatórios

| Campo | Tipo | Regra |
|---|---|---|
| `zqir` | string | exatamente `"1.0"` |
| `decision.n` | int | 1..8 (fase-oráculo declarada) |
| `decision.oracle.type` | enum | `constant` \| `parity` |
| `decision.oracle.value` | int | exigido quando `type=constant` (0 ou 1) |
| `decision.oracle.bits` | string | exigido quando `type=parity` (ex.: `"10"`), tamanho = `n` |
| `decision.shots` | int | ≥ 30 |
| `decision.epsilon` | float | 0 < ε < 1 (erro declarado do veredito) |

### Campos opcionais

- `family` (int ≥ 1) — correção de testes múltiplos; banda encolhe (Bonferroni).
- `device_gate` — testa o próprio dispositivo (GHZ) antes de gastar oráculo.
- `memory_gate` — testa se o ambiente tem memória (revival BLP). Se detectar, o veredito
  é `REFUSED` com motivo `NOISE_HAS_MEMORY`, porque a banda Hoeffding pressupõe amostras
  independentes.
- `execution.backend` — `"simulator"` ou `"ibm:<nome>"`.
- `receipt` — sela o resultado (SHA3-256 e, se `pqcrypto` disponível, ML-DSA-44).

---

## 2. Contrato de saída

```json
{
  "zqir": "1.0",
  "id": "demo-001",
  "verdict": "1",
  "refusal_reason": null,
  "p0": 0.9912,
  "band": 0.0425,
  "shots": 2048,
  "epsilon": 0.05,
  "family": 1,
  "backend": "simulator",
  "job_id": null,
  "device_gate": {"passed": true, "fidelity": 0.99},
  "memory_gate": {"enabled": false},
  "receipt": {"spec": "Z-QEA/2.2", "seal_sha3_256": "...", "pq_signature": true}
}
```

### Semântica trivalente (normativa)

- **`1`** — evidência sustenta a decisão declarada (constante = valor declarado;
  paridade = oráculo balanceado), fora da banda de ruído.
- **`0`** — evidência sustenta a negação da decisão declarada.
- **`REFUSED`** — a evidência não permite afirmar nem negar, por qualquer motivo
  rastreável:

| `refusal_reason` | Significado |
|---|---|
| `BALANCED_ORACLE` | evidência de interferência perfeita: decidir 1 ou 0 seria mentira |
| `INSIDE_NOISE_BAND` | p0 dentro da banda; shots insuficientes para separar |
| `FAMILY_EXCEEDS_SHOTS` | banda Bonferroni ≤ 0: shots insuficientes para a família |
| `DEVICE_DECOHERED` | porta GHZ reprovou o dispositivo antes do oráculo |
| `NOISE_HAS_MEMORY` | gate de memória detectou revival: independência das amostras inválida |

**Regra da casa:** recusa não é falha. É o único veredito que não mente.

---

## 3. Ligações de ecossistema

O mesmo JSON de entrada produz o mesmo veredito em qualquer caminho:

| Ecossistema | Caminho |
|---|---|
| Qiskit | execução nativa (`zqir.core`) |
| PennyLane | `adapters/pennylane_adapter.py` |
| Cirq | `adapters/cirq_adapter.py` |
| Braket | `adapters/braket_adapter.py` |
| OpenQASM 3 | `zq-ir export-qasm3 spec.json` (circuito portável) |
| Qualquer linguagem | CLI com JSON em stdin/stdout (`examples/portability/`) |

---

## 4. Limites declarados

- Fase-oráculo declarada: `n ≤ 8` (oráculo caro vai para backend IBM).
- `constant` vs `parity` é o problema-promise do Deutsch–Jozsa; funções fora dessas
  classes **não** são reivindicadas.
- Banda Hoeffding limita ruído **amostral**, não viés sistemático de hardware;
  viés sistemático exige calibração de readout (declarado como limitação aberta).
- Gate de memória testa profundidades ≤ `steps` no modelo de colisão; ausência de
  revival não prova ausência de memória em geral.
