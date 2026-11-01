# -*- coding: utf-8 -*-
"""SOBRECARGA EXAUSTIVA — 2000 iteracoes por app (8 apps).

Cada app roda no proprio nucleo, com matriz de entradas rotativa (oraculos,
n, shots, epsilon, family) e sementes variadas. Mede: sucesso/excecao,
distribuicao de veredito, determinismo por seed, verificacao de selo,
latencia (p50/p95/p99/max) e crescimento de RSS.

Honestidade de escopo: este teste exercita o nucleo e o caminho de execucao
local (simulador da casa + Aer). Hardware IBM entra em hw_soak.py, limitado
pela cota real de QPU.
"""
import gc, json, os, resource, statistics, sys, time, traceback

ROOT = "/app/conversations/6a47cbde110fe595b9a5a983"
N = 2000
RESULT = {"n_por_app": N, "apps": {}}

for p in (f"{ROOT}/zq-ir", f"{ROOT}/zephirum-lang/src", f"{ROOT}/poc/w-zq-gate/src",
          f"{ROOT}/rag/w-zy-ai-rag", f"{ROOT}/pq/work-zqea-seal",
          f"{ROOT}/pq/work-zqea-verify", f"{ROOT}/poc/w-z-anyon-lab", f"{ROOT}/ravi-quantuno"):
    if p not in sys.path:
        sys.path.insert(0, p)

ORACLES = [lambda x: 0, lambda x: 1, lambda x: x & 1, lambda x: (x >> 1) & 1,
           lambda x: x & 1 ^ 1]


def rss_kb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


PREFIXOS = ("zyql", "zquantum", "zqea", "anyon_lab", "zy_ai_rag", "ravi_quantuno", "zqir")


def isolar(app_path):
    """Cada app roda com o próprio caminho na frente e módulos limpos."""
    for m in [m for m in sys.modules if m.split(".")[0] in PREFIXOS]:
        sys.modules.pop(m, None)
    while app_path in sys.path:
        sys.path.remove(app_path)
    sys.path.insert(0, app_path)


def run_app(name, single, expected_ok=None, verify=None, app_path=None):
    if app_path:
        isolar(app_path)
    lat, verdicts, erros, det_ok, det_n, selo_ok = [], {}, 0, 0, 0, 0
    primeiro_erro = None
    rss0 = rss_kb()
    t_all = time.perf_counter()
    for i in range(N):
        seed = 1000 + (i % 97)
        try:
            t0 = time.perf_counter()
            out = single(i, seed)
            lat.append((time.perf_counter() - t0) * 1000)
            if isinstance(out, dict):
                v = out.get("verdict") or out.get("veredito") or out.get("selo_sha3_256")
                if v is not None:
                    verdicts[str(v)[:12]] = verdicts.get(str(v)[:12], 0) + 1
            if verify is not None and i % 25 == 0:
                if verify(out):
                    selo_ok += 1
            if i % 200 == 0:      # determinismo amostral
                det_n += 1
                a = single(i, seed)
                b = single(i, seed)
                if json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str):
                    det_ok += 1
        except Exception as e:
            erros += 1
            if primeiro_erro is None:
                primeiro_erro = f"{type(e).__name__}: {str(e)[:160]}"
            lat.append((time.perf_counter() - t0) * 1000 if 't0' in dir() else 0.0)
    total = time.perf_counter() - t_all
    lat.sort()

    def p(q):
        return round(lat[min(len(lat) - 1, int(q * len(lat)))], 2) if lat else None

    r = {"iteracoes": N, "erros": erros, "primeiro_erro": primeiro_erro,
         "vereditos": dict(sorted(verdicts.items(), key=lambda kv: -kv[1])[:6]),
         "determinismo": f"{det_ok}/{det_n}" if det_n else "n/a",
         "selo_verificado": f"{selo_ok}/{max(1, N // 25)}" if verify else "n/a",
         "latencia_ms": {"p50": p(.50), "p95": p(.95), "p99": p(.99),
                         "max": round(max(lat), 2) if lat else None},
         "throughput_ops_s": round(N / total, 1) if total else None,
         "rss_delta_mb": round((rss_kb() - rss0) / 1024, 1)}
    RESULT["apps"][name] = r
    print(f"{name:<18} erros={erros:<4} p50={r['latencia_ms']['p50']:<7} "
          f"p99={r['latencia_ms']['p99']:<7} ops/s={r['throughput_ops_s']:<7} "
          f"det={r['determinismo']:<7} selo={r['selo_verificado']}")
    gc.collect()
    return r


# ---------------------------------------------------------------- ZQ-IR
def zqir_single(i, seed):
    from zqir import core
    tipos = [{"type": "constant", "value": 0}, {"type": "constant", "value": 1},
             {"type": "parity", "bits": "1"}, {"type": "parity", "bits": "01"}]
    spec = {"zqir": "1.0",
            "decision": {"id": f"s{i}", "purpose": "soak", "n": 1 + (i % 2),
                         "oracle": tipos[i % 4], "shots": 64 + (i % 5) * 64,
                         "epsilon": 0.05, "family": 1 + (i % 3)},
            "execution": {"backend": "simulator", "seed": seed},
            "receipt": {"enabled": True}}
    return core.evaluate(spec)


def zqir_verify(out):
    from zqir import core
    return core.verify_receipt(out.get("receipt") or {})["ok"]


# ---------------------------------------------------------------- ZEPHIRUM
def zeph_single(i, seed):
    from zyql_runtime import decide
    return {"verdict": decide(ORACLES[i % len(ORACLES)], n=1 + (i % 3),
                              shots=64 + (i % 4) * 64, seed=seed,
                              epsilon=0.05).verdict.name}


def zeph_verify(out):
    return out.get("verdict") in ("PERMIT", "DENY", "REFUSED")


# ---------------------------------------------------------------- ZQ-GATE
def zqgate_single(i, seed):
    from zyql_quantum_gate import ZYQLQuantumGate
    g = ZYQLQuantumGate(1 + (i % 3), ORACLES[i % len(ORACLES)])
    r = g.run_quantum(shots=64 + (i % 4) * 64, seed=seed, epsilon=0.05)
    return {"verdict": r["decision"], "p0": r["p0"]}


# ---------------------------------------------------------------- ZY-AI-RAG
def zyrag_single(i, seed):
    from zyql_rag_layer import bm25_rank, CORPUS
    from zyql_quantum_gate import ZYQLQuantumGate
    q = ["trivalent decision", "sealed receipt", "quantum gate", "refusal"][i % 4]
    ranked = bm25_rank(q, CORPUS, k=3)
    g = ZYQLQuantumGate(2, ORACLES[i % len(ORACLES)])
    r = g.run_quantum(shots=64 + (i % 3) * 64, seed=seed, epsilon=0.05)
    return {"verdict": r["decision"], "docs": len(ranked)}


# ---------------------------------------------------------------- SEAL / VERIFY
def seal_single(i, seed):
    from zqea_pq import sha3_seal, sign_receipt
    rec = {"i": i, "seed": seed, "verdict": i % 3}
    rec = sign_receipt(rec)            # devolve o proprio recibo com o bloco PQ
    rec["selo_sha3_256"] = sha3_seal(rec)
    return rec


def seal_verify(out):
    from zqea_pq import sha3_seal
    if not isinstance(out, dict):
        return False
    corpo = {k: v for k, v in out.items() if k != "selo_sha3_256"}
    return sha3_seal(corpo) == out["selo_sha3_256"]


def verify_single(i, seed):
    from zqea_verify import verify
    from zqea_pq import sha3_seal
    rec = {"i": i, "seed": seed}
    rec["selo_sha3_256"] = sha3_seal(rec)
    return {"verdict": verify(rec)}


# ---------------------------------------------------------------- ANYON LAB
def anyon_single(i, seed):
    import anyon_lab
    r = anyon_lab.battery()
    return {"verdict": r.get("veredito", "n/a") if isinstance(r, dict) else "n/a"}


# ---------------------------------------------------------------- RAVI
def ravi_single(i, seed):
    import ravi_quantuno as rq
    r = rq.missao_trivalente(provider="local")
    return {"verdict": r.get("veredito", r.get("verdict", "n/a")) if isinstance(r, dict) else "n/a"}


if __name__ == "__main__":
    run_app("zq-ir", zqir_single, verify=zqir_verify, app_path=f"{ROOT}/zq-ir")
    run_app("zephirum-lang", zeph_single, verify=zeph_verify, app_path=f"{ROOT}/zephirum-lang/src")
    run_app("zq-gate", zqgate_single, app_path=f"{ROOT}/poc/w-zq-gate/src")
    run_app("zy-ai-rag", zyrag_single, app_path=f"{ROOT}/rag/w-zy-ai-rag")
    run_app("zqea-seal", seal_single, verify=seal_verify, app_path=f"{ROOT}/pq/work-zqea-seal")
    run_app("zqea-verify", verify_single, app_path=f"{ROOT}/pq/work-zqea-verify")
    run_app("z-anyon-lab", anyon_single, app_path=f"{ROOT}/poc/w-z-anyon-lab")
    run_app("ravi-quantuno", ravi_single, app_path=f"{ROOT}/ravi-quantuno")
    out = f"{ROOT}/soak/soak_2000.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(RESULT, open(out, "w"), ensure_ascii=False, indent=1)
    print("\nresultado:", out)
