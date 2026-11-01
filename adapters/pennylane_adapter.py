# -*- coding: utf-8 -*-
"""Adaptador PennyLane: mesmo IR, mesmas contagens, mesmo veredito."""
import pennylane as qml
from pennylane import numpy as pnp

from zqir.core import adaptive_margin, verdict_from_p0


def decide(spec, shots=None):
    d = spec["decision"]
    n, oracle = d["n"], d["oracle"]
    S = shots or d.get("shots", 1024)
    dev = qml.device("default.qubit", wires=n, shots=S)

    @qml.qnode(dev)
    def circuit():
        for q in range(n):
            qml.Hadamard(wires=q)
        if oracle["type"] == "parity":
            for q, b in enumerate(oracle["bits"]):
                if b == "1":
                    qml.PauliZ(wires=q)
        elif oracle["value"] == 1:
            qml.GlobalPhase(pnp.pi)
        for q in range(n):
            qml.Hadamard(wires=q)
        return qml.sample()

    samples = circuit()
    rows = [s if hasattr(s, "__len__") else [s] for s in samples]
    zeros = sum(1 for r in rows if not any(r))
    p0 = zeros / len(rows)
    eps = d.get("epsilon", 0.05)
    fam = d.get("family", 1)
    band = adaptive_margin(eps, len(rows), fam)
    verdict, reason = verdict_from_p0(p0, band, oracle, len(rows), eps, fam)
    return {"zqir": "1.0", "id": d.get("id"), "verdict": verdict,
            "refusal_reason": reason, "p0": round(p0, 6), "band": round(band, 6),
            "backend": "pennylane:default.qubit", "job_id": None}
