# -*- coding: utf-8 -*-
"""Adaptador Amazon Braket: mesmo IR, mesmo veredito, via LocalSimulator."""
from braket.circuits import Circuit
from braket.devices import LocalSimulator

from zqir.core import adaptive_margin, verdict_from_p0


def build(n, oracle):
    c = Circuit()
    for q in range(n):
        c.h(q)
    if oracle["type"] == "parity":
        for q, b in enumerate(oracle["bits"]):
            if b == "1":
                c.z(q)
    # oráculo constante: fase global ±1 é fisicamente inobservável em medida
    # computacional — o valor vem do oráculo, a dominância confirma.
    for q in range(n):
        c.h(q)
    return c


def decide(spec, shots=None):
    d = spec["decision"]
    n, oracle = d["n"], d["oracle"]
    S = shots or d.get("shots", 1024)
    counts = LocalSimulator().run(build(n, oracle), shots=S).result().measurement_counts
    total = sum(counts.values())
    zeros = counts.get("0" * n, 0)
    p0 = zeros / total
    eps = d.get("epsilon", 0.05)
    fam = d.get("family", 1)
    band = adaptive_margin(eps, total, fam)
    verdict, reason = verdict_from_p0(p0, band, oracle, total, eps, fam)
    return {"zqir": "1.0", "id": d.get("id"), "verdict": verdict,
            "refusal_reason": reason, "p0": round(p0, 6), "band": round(band, 6),
            "backend": "braket:local_simulator", "job_id": None}
