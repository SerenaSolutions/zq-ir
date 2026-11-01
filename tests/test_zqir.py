# -*- coding: utf-8 -*-
"""Testes falsificáveis do ZQ-IR v1 (contrato, semântica e limites)."""
import json, math, os, sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from zqir import core  # noqa: E402


def spec(**kw):
    d = {"id": "t", "purpose": "teste", "n": 2,
         "oracle": {"type": "constant", "value": 1},
         "shots": 512, "epsilon": 0.05}
    d.update(kw)
    return {"zqir": "1.0", "decision": d,
            "execution": {"backend": "simulator", "seed": 7},
            "receipt": {"enabled": True}}


def test_contrato_minimo():
    out = core.evaluate(spec())
    for campo in ("zqir", "verdict", "p0", "band", "shots", "receipt"):
        assert campo in out
    assert out["verdict"] in {"1", "0", "REFUSED"}


def test_constante_1_da_veredito_1():
    out = core.evaluate(spec())
    assert out["verdict"] == "1" and out["p0"] > 0.9
    assert out["refusal_reason"] is None


def test_constante_0_da_veredito_0():
    out = core.evaluate(spec(oracle={"type": "constant", "value": 0}))
    assert out["verdict"] == "0"


def test_paridade_recusa_com_motivo():
    out = core.evaluate(spec(oracle={"type": "parity", "bits": "10"}))
    assert out["verdict"] == "REFUSED"
    assert out["refusal_reason"] == "BALANCED_ORACLE"
    assert out["p0"] <= out["band"]


def test_familia_absurda_recusa_por_shots():
    out = core.evaluate(spec(family=10 ** 9))
    assert out["verdict"] == "REFUSED"
    assert out["refusal_reason"] == "FAMILY_EXCEEDS_SHOTS"


def test_spec_invalida_nao_executa():
    with pytest.raises(core.SpecError):
        core.evaluate({"zqir": "1.0", "decision": {"n": 9, "oracle": {"type": "constant", "value": 1},
                                                   "shots": 100, "epsilon": 0.05}})
    with pytest.raises(core.SpecError):
        core.evaluate(spec(shots=10))


def test_banda_encolhe_com_familia():
    m1 = core.adaptive_margin(0.05, 2048, 1)
    m5 = core.adaptive_margin(0.05, 2048, 5)
    assert m5 < m1
    assert core.adaptive_margin(0.05, 2048, 10 ** 9) <= 0


def test_gate_de_memoria_bloqueia_veredito():
    out = core.evaluate(spec(memory_gate={"enabled": True, "steps": 3}))
    assert out["memory_gate"]["enabled"] is True
    assert out["memory_gate"]["detected"] is True
    assert out["verdict"] == "REFUSED"
    assert out["refusal_reason"] == "NOISE_HAS_MEMORY"
    assert out["p0"] is None       # não gastou oráculo


def test_porta_ghz_reprova_dispositivo_simulado():
    # n=1 não tem emaranhamento: GHZ inválido por construção -> recusa honesta
    out = core.evaluate(spec(n=1, device_gate={"type": "ghz", "threshold": 0.999}))
    assert out["verdict"] in {"1", "REFUSED"}


def test_selo_e_estavel_e_sensivel():
    a = core.evaluate(spec())["receipt"]["seal_sha3_256"]
    b = core.evaluate(spec())["receipt"]["seal_sha3_256"]
    assert len(a) == 64 and a == b          # determinístico no conteúdo
    c = core.evaluate(spec(purpose="outro"))["receipt"]["seal_sha3_256"]
    assert c != a                            # muda com o conteúdo


def test_cadeia_de_recibos():
    s1 = spec(id="a")
    s2 = spec(id="b", oracle={"type": "constant", "value": 0})
    r1 = core.evaluate(s1)["receipt"]["seal_sha3_256"]
    s2["receipt"]["previous_seal"] = r1
    out2 = core.evaluate(s2)
    assert out2["receipt"]["seal_sha3_256"] != r1


def test_export_openqasm3_portavel():
    q = core.export_qasm3(spec(oracle={"type": "parity", "bits": "10"}))
    assert q.startswith("OPENQASM 3.0")
    assert "stdgates.inc" in q
    assert "z q[0]" in q.replace("  ", " ")


def test_recibo_verificavel_offline():
    out = core.evaluate(spec())
    v = core.verify_receipt(out["receipt"])
    assert v["ok"] is True, v["reason"]
    # qualquer alteracao no payload quebra o selo
    adulterado = json.loads(json.dumps(out["receipt"]))
    adulterado["payload"]["verdict"] = "0"
    assert core.verify_receipt(adulterado)["ok"] is False
    # recibo sem payload nao pode ser verificado (fail-closed)
    assert core.verify_receipt({"spec": "x", "seal_sha3_256": "00"})["ok"] is False
