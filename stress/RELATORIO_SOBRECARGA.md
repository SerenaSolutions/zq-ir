# SOBRECARGA EXAUSTIVA — 2000 x 8 apps

**Local (simulador da casa + Aer):** 16000 execucoes, 0 erros.

| app | iterações | erros | p50 (ms) | p99 (ms) | ops/s | determinismo | selo |
|---|---|---|---|---|---|---|---|
| zq-ir | 2000 | 0 | 55.21 | 56.57 | 17.6 | 9/10 | 80/80 |
| zephirum-lang | 2000 | 0 | 0.31 | 0.46 | 3553.6 | 10/10 | 80/80 |
| zq-gate | 2000 | 0 | 0.31 | 0.45 | 3605.6 | 10/10 | n/a |
| zy-ai-rag | 2000 | 0 | 0.24 | 0.35 | 4186.6 | 10/10 | n/a |
| zqea-seal | 2000 | 0 | 8.36 | 8.43 | 118.3 | 0/10 | 80/80 |
| zqea-verify | 2000 | 0 | 0.01 | 0.01 | 104090.6 | 10/10 | n/a |
| z-anyon-lab | 2000 | 0 | 0.08 | 0.09 | 12086.8 | 10/10 | n/a |
| ravi-quantuno | 2000 | 0 | 1.04 | 1.23 | 935.6 | 10/10 | n/a |

## Silício IBM (ibm_marrakesh)

- jobs submetidos: 10 | sucessos: 10 | vereditos: {'1': 10}
- QPU consumido: 20s | por decisão: 2.0s
- cota restante depois: 136s

### Extrapolação honesta (16.000 decisões no hardware)
- QPU necessário: 8.9h
- janelas de 28 dias no plano open (600s cada): 53

**Conclusão:** 2000 x 8 apps é matematicamente impossível no plano open atual;
no silício se prova operabilidade (10/10 sem falha), e a exaustão de 16.000 fica no simulador.

## Não-determinismos declarados (não são falhas)
- `zqea-seal`: ML-DSA-44 gera chave nova por assinatura — recibo assinado é único por execução; o selo SHA3 sobre o corpo é determinístico.
- `zq-ir` 9/10: o recibo embute `sealed_at`, então o JSON muda com o relógio; veredito e banda são determinísticos.

## Limites
- Banda Hoeffding cobre ruído amostral, não viés sistemático de readout.
- Soak local exercita núcleo e simulador; não substitui calibração de dispositivo.