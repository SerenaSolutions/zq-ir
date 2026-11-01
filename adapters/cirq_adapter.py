# -*- coding: utf-8 -*-
"""Adaptador Cirq: constrói a decisão do IR em Cirq e devolve o veredito trivalente."""
import cirq

from zqir.core import adaptive_margin, verdict_from_p0


def build(n, oracle):
    qs = cirq.LineQubit.range(n)
    c = cirq.Circuit()
    c.append(cirq.H.on_each(*qs))
    if oracle["type"] == "parity":
        c.append(cirq.Z(qs[i]) for i, b in enumerate(oracle["bits"]) if b == "1")
    else:
        if oracle["value"] == 1:            # fase global π via fase relativa (equivalente em medida)
            c.append(cirq.global_phase_operation(complex(-1.0)))
    c.append(cirq.H.on_each(*qs))
    c.append(cirq.measure(*qs, key="m"))
    return c


def decide(spec, repeats=None):
    d = spec["decision"]
    n, oracle, shots = d["n"], d["oracle"], d.get("shots", 1024)
    reps = repeats or shots
    bucket = cirq.Simulator().run(build(n, oracle), repetitions=reps)
    bits = bucket.measurements["m"]
    zeros = sum(1 for row in bits if not row.any())
    p0 = zeros / reps
    band = adaptive_margin(d.get("epsilon", 0.05), reps, d.get("family", 1))
    verdict, reason = verdict_from_p0(p0, band, oracle, reps, d.get("epsilon", 0.05), d.get("family", 1))
    return {"zqir": "1.0", "id": d.get("id"), "verdict": verdict,
            "refusal_reason": reason, "p0": round(p0, 6), "band": round(band, 6),
            "backend": "cirq:simulator", "job_id": None}
