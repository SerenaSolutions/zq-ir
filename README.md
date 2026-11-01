# ZQ-IR

*Uma decisão trivalente, qualquer ecossistema quântico.*

![version](https://img.shields.io/badge/version-1.0.0-6e46b8)
![repr](https://img.shields.io/badge/IR-JSON%20%2B%20OpenQASM%203-cyan)
![verdicts](https://img.shields.io/badge/verdicts-1%20%7C%200%20%7C%20REFUSED-gold)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)

O ZQ-IR é o **contrato neutro** de decisão quântica: descreva a decisão em JSON, receba
`1`, `0` ou `REFUSED` com recibo selado. O veredito não pertence a nenhum framework —
por isso qualquer ecossistema pode consumi-lo.

## Instalação

```console
$ pip install "qiskit>=2.6" qiskit-aer       # simulador
$ pip install qiskit-ibm-runtime             # hardware IBM (opcional)
$ pip install -e .
```

## Decidir

```console
$ zq-ir decide examples/decide_const1.json
{
  "zqir": "1.0",
  "verdict": "1",
  "refusal_reason": null,
  "p0": 1.0,
  "band": 0.03001,
  "device_gate": {"enabled": true, "fidelity": 1.0, "passed": true},
  "receipt": {"spec": "Z-QEA/2.2", "seal_sha3_256": "c685…", "pq_signature": true}
}
```

Recusa é resultado, não erro:

```console
$ zq-ir decide examples/decide_parity.json     # oráculo balanceado
{ "verdict": "REFUSED", "refusal_reason": "BALANCED_ORACLE", "p0": 0.0, ... }
```

## Portas de ecossistema

| Ecossistema | Como pluga |
|---|---|
| Qiskit | nativo (`zqir.core`) |
| PennyLane | `adapters/pennylane_adapter.py` — testado: mesmo veredito |
| Cirq | `adapters/cirq_adapter.py` — testado: mesmo veredito |
| Amazon Braket | `adapters/braket_adapter.py` — testado: mesmo veredito |
| OpenQASM 3 | `zq-ir export-qasm3 spec.json` |
| Qualquer linguagem | CLI JSON→JSON (`examples/portability/`: shell, Node, R, Julia) |

O mesmo `spec.json` produz o mesmo veredito em todos os caminhos. O selo SHA3-256 é
recomputável offline; com `pqcrypto` instalado, a camada ML-DSA-44 também é aplicada.

## Semântica

- `1` evidência sustenta a decisão declarada
- `0` evidência sustenta a negação
- `REFUSED` com motivo rastreável: `BALANCED_ORACLE`, `INSIDE_NOISE_BAND`,
  `FAMILY_EXCEEDS_SHOTS`, `DEVICE_DECOHERED`, `NOISE_HAS_MEMORY`

**Gate de memória:** quando `memory_gate.enabled` é declarado, o portão mede revival de
distância de traço (BLP) antes do veredito. Se detectar memória ambiental, recusa com
`NOISE_HAS_MEMORY` — porque a banda Hoeffding pressupõe amostras independentes.

**Gate de dispositivo:** `device_gate` testa o próprio QPU (GHZ) antes de gastar oráculo.

## Testes

```console
$ PYTHONPATH=. python3 -m pytest tests/ -q
12 passed
```

Cobrem: contrato de saída, vereditos nos dois sentidos, recusa por oráculo balanceado,
família que estoura shots, IR inválido (fail-closed), banda que encolhe, gate de memória
bloqueando veredito sem gastar oráculo, determinismo e sensibilidade do selo, cadeia de
recibos e export OpenQASM 3.

## Limites declarados

- Fase-oráculo `n ≤ 8`; oráculo caro vai para backend IBM.
- Problema-promise: `constant` vs `parity` (Deutsch–Jozsa). Outras classes não reivindicadas.
- Banda Hoeffding cobre ruído amostral, **não** viés sistemático de readout.
- Gate de memória vale para profundidades ≤ `steps` no modelo de colisão.

Apache-2.0 (concessão explícita de patentes) · Serena Quantum Solutions
