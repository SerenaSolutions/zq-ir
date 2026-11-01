# -*- coding: utf-8 -*-
"""SOAK EM SILICIO (IBM Quantum) — operabilidade repetida, limitada pela cota real.

Submete K jobs pequenos em sequencia e mede: sucesso, latencia de fila+execucao,
veredito e consumo de QPU por decisao. Extrapola o custo de 2000 decisoes/app
para dimensionar a cota necessaria (honestidade: open plan = 600s/mes).
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from zqir import core

K = 10
SHOTS = 256
N = 2
ORACLE = {"type": "constant", "value": 1}


def main():
    svc = QiskitRuntimeService(token=os.environ["IBM_QUANTUM_TOKEN"],
                               channel="ibm_quantum_platform")
    u0 = svc.usage()
    job0 = u0["usage_consumed_seconds"]
    backend = svc.backend("ibm_marrakesh")
    circ = core.build_dj_circuit(N, ORACLE)
    isa = transpile([circ], backend, optimization_level=2)
    sampler = Sampler(mode=backend)
    band = core.adaptive_margin(0.05, SHOTS, 1)

    ok, falhas, lat, vereditos, jobs = 0, [], [], {}, []
    for i in range(K):
        t0 = time.perf_counter()
        try:
            job = sampler.run(isa, shots=SHOTS)
            res = job.result()
            conta = core._norm_counts(dict(getattr(res[0].data, "c").get_counts()), N)
            p0 = conta.get("0" * N, 0) / sum(conta.values())
            v, _ = core.verdict_from_p0(p0, band, ORACLE, SHOTS, 0.05, 1)
            vereditos[v] = vereditos.get(v, 0) + 1
            ok += 1
            jobs.append({"job_id": job.job_id(), "verdict": v, "p0": round(p0, 4),
                         "status": str(job.status())})
        except Exception as e:
            falhas.append(f"{type(e).__name__}: {str(e)[:120]}")
            break
        lat.append(round(time.perf_counter() - t0, 2))

    u1 = svc.usage()
    gasto = u1["usage_consumed_seconds"] - job0
    out = {"backend": "ibm_marrakesh", "k_jobs": K, "shots": SHOTS,
           "sucessos": ok, "falhas": falhas, "latencia_s": lat,
           "vereditos": vereditos, "jobs": jobs,
           "qpu_consumido_s": gasto,
           "qpu_por_decisao_s": round(gasto / ok, 3) if ok else None,
           "restante_apos_s": u1["usage_remaining_seconds"]}
    # extrapolacao honesta para o pedido de 2000 x 8 apps
    if ok:
        total = 2000 * 8
        custo = total * (gasto / ok)
        out["extrapolacao"] = {
            "decisoes_pedidas": total,
            "qpu_necessario_s": round(custo, 0),
            "qpu_necessario_h": round(custo / 3600, 1),
            "cotas_28_dias_necessarias": round(custo / 600, 0),
            "meses_no_plano_open": round(custo / 600, 0),
        }
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "hw_soak.json"), "w"), indent=1)
    print(f"jobs ok: {ok}/{K} | vereditos: {vereditos} | QPU gasto: {gasto}s")
    if ok:
        print(f"QPU por decisao: {gasto/ok:.2f}s")
        print("extrapolacao 16.000 decisoes:", out["extrapolacao"])


if __name__ == "__main__":
    main()
