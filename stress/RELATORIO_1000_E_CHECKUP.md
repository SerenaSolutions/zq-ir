# Bateria de 1000 + check-up — ZEPHIRUM / ZYQL

Data: 03/11/2026 · ZEPHIRUM v2.3.2 · ZQ-IR 1.0.0

## 1. Bateria de 1000 execuções por app

**Total: 8.000 execuções · 0 erros**

| app | iterações | erros | p50 (ms) | p99 (ms) | ops/s | selo |
|---|---|---|---|---|---|---|
| zq-ir | 1000 | 0 | 55.51 | 57.13 | 17.3 | 40/40 |
| zephirum-lang | 1000 | 0 | 0.3 | 0.44 | 3676.8 | 40/40 |
| zq-gate | 1000 | 0 | 0.29 | 0.44 | 3753.9 | n/a |
| zy-ai-rag | 1000 | 0 | 0.22 | 0.33 | 4416.8 | n/a |
| zqea-seal | 1000 | 0 | 8.35 | 8.41 | 118.3 | 40/40 |
| zqea-verify | 1000 | 0 | 0.01 | 0.01 | 104369.6 | n/a |
| z-anyon-lab | 1000 | 0 | 0.08 | 0.09 | 11964.0 | n/a |
| ravi-quantuno | 1000 | 0 | 1.04 | 1.24 | 937.1 | n/a |

## 2. Silício IBM (ibm_marrakesh, 256 shots, n=2)

Cota da janela: 130s restantes após a rodada · gasto 6s

| caso | veredito | esperado | ok | p0 | job |
|---|---|---|---|---|---|
| const1 | 1 | 1 | True | 0.9961 | `dbku16onceqs73aml27g` |
| const0 | 0 | 0 | True | 0.9961 | `dbku18tgg49c73djlg50` |
| parity | REFUSED | REFUSED | True | 0.0078 | `dbku1g5gg49c73djlgf0` |

## 3. Check-up estático e melhorias aplicadas

| item | antes | depois |
|---|---|---|
| ruff F821 (nome indefinido) | 1 (bug latente em qroute/hardware.py) | 0 |
| ruff F841 (variável morta) | 5 | 2 (efeito colateral declarado) |
| código morto | band_pending, keep, alvo | removido |
| cobertura de testes zq-ir | — | 73% |
| suíte ZEPHIRUM | 3 blocos | 3 blocos ALL PASS |
| versão | 2.3.1 | 2.3.2 (tag publicada) |

## 4. O que ainda dá para melhorar (declarado, não feito)

1. Cobertura do zq-ir em 73% — faltam casos de borda do contrato (IR malformado).
2. 130 avisos de estilo no zephirum-lang (a maioria UP009/F401) — limpeza mecânica,
   não corrigida em bloco hoje para não misturar com a mudança de comportamento.
3. `quantum_types.py:88` mantém `a, b = lang.qbit(...)` sem uso: são objetos registrados
   no interpretador (efeito colateral), documentado em vez de removido.
4. Nenhuma rodada de 1000 no silício é possível: 2s de QPU por decisão × 1000 = 33 min
   contra janela de 600s. A prova de silício é a amostra de 3 casos + bateria local.