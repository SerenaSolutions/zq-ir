# -*- coding: utf-8 -*-
"""Acordo entre ecossistemas: frameworks diferentes, mesmo veredito."""
import json, os, sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "adapters"))

CASES = [
    ("examples/decide_const1.json", "1"),
    ("examples/decide_parity.json", "REFUSED"),
]


def _load(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))


@pytest.mark.parametrize("spec_file,esperado", CASES)
def test_cirq_concorda_com_o_contrato(spec_file, esperado):
    cirq = pytest.importorskip("cirq")
    from adapters import cirq_adapter
    r = cirq_adapter.decide(_load(spec_file), repeats=512)
    assert r["verdict"] == esperado


@pytest.mark.parametrize("spec_file,esperado", CASES)
def test_pennylane_concorda_com_o_contrato(spec_file, esperado):
    pytest.importorskip("pennylane")
    from adapters import pennylane_adapter
    r = pennylane_adapter.decide(_load(spec_file), shots=512)
    assert r["verdict"] == esperado


@pytest.mark.parametrize("spec_file,esperado", CASES)
def test_braket_concorda_com_o_contrato(spec_file, esperado):
    pytest.importorskip("braket")
    from adapters import braket_adapter
    r = braket_adapter.decide(_load(spec_file), shots=512)
    assert r["verdict"] == esperado
