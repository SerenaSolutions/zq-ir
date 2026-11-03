# -*- coding: utf-8 -*-
"""Rodada de hardware da bateria de 1000: prova o mesmo protocolo no silicio,
dimensionada pela cota real (a decisao custa ~2s de QPU; 1000 no chip nao cabe)."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from zqir import core

CASOS = [("const1", {"type": "constant", "value": 1}, "1"),
         ("const0", {"type": "constant", "value": 0}, "0"),
         ("parity", {"type": "parity", "bits": "1"}, "REFUSED")]
N, SHOTS, ORCAMENTO = 2, 256, 90   # teto de QPU em segundos


def main():
    svc = QiskitRuntimeService(token=os.environ["IBM_QUANTUM_TOKEN"], channel="ibm_quantum_platform")
    u0 = svc.usage(); gasto0 = u0["usage_consumed_seconds"]
    backend = svc.backend("ibm_marrakesh")
    sampler = Sampler(mode=backend)
    band = core.adaptive_margin(0.05, SHOTS, 1)
    saida = {"backend": "ibm_marrakesh", "shots": SHOTS, "n": N, "banda": band,
             "orcamento_qpu_s": ORCAMENTO, "rodadas": []}
    for nome, oracle, esperado in CASOS:
        circ = core.build_dj_circuit(N, oracle)
        isa = transpile([circ], backend, optimization_level=2)
        t0 = time.perf_counter()
        job = sampler.run(isa, shots=SHOTS)
        res = job.result()
        conta = core._norm_counts(dict(getattr(res[0].data, "c").get_counts()), N)
        p0 = conta.get("0" * N, 0) / sum(conta.values())
        v, motivo = core.verdict_from_p0(p0, band, oracle, SHOTS, 0.05, 1)
        gasto = svc.usage()["usage_consumed_seconds"] - gasto0
        saida["rodadas"].append({"caso": nome, "verdict": v, "esperado": esperado,
                                 "ok": v == esperado, "p0": round(p0, 4),
                                 "refusal_reason": motivo, "job_id": job.job_id(),
                                 "latencia_s": round(time.perf_counter() - t0, 1),
                                 "qpu_acumulado_s": gasto})
        print(f"{nome:<8} veredito={v:<8} esperado={esperado:<8} ok={v==esperado} "
              f"p0={p0:.4f} job={job.job_id()} qpu={gasto}s")
        if gasto > ORCAMENTO:
            print("teto de QPU atingido, parando"); break
    u1 = svc.usage()
    saida["qpu_gasto_s"] = u1["usage_consumed_seconds"] - gasto0
    saida["restante_s"] = u1["usage_remaining_seconds"]
    json.dump(saida, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "hw_round1000.json"), "w"), indent=1)
    print(f"\nQPU gasto: {saida['qpu_gasto_s']}s | restante: {saida['restante_s']}s")


if __name__ == "__main__":
    main()
