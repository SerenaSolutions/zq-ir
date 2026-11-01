# -*- coding: utf-8 -*-
"""CLI do ZQ-IR: JSON entra, JSON sai. Qualquer linguagem pluga por stdin/stdout."""
import argparse, json, sys
from . import core


def main(argv=None):
    p = argparse.ArgumentParser(prog="zq-ir", description="ZQ-IR — decisão trivalente portável")
    p.add_argument("command", choices=["decide", "validate", "export-qasm3"])
    p.add_argument("spec", help="arquivo JSON do IR (ou - para stdin)")
    p.add_argument("--backend", default=None, help='sobrepõe execution.backend ("simulator" ou "ibm:ibm_marrakesh")')
    p.add_argument("--out", default=None, help="grava o resultado neste arquivo")
    a = p.parse_args(argv)

    raw = sys.stdin.read() if a.spec == "-" else open(a.spec, encoding="utf-8").read()
    spec = json.loads(raw)
    if a.backend:
        spec.setdefault("execution", {})["backend"] = a.backend

    if a.command == "validate":
        core.validate(spec)
        print(json.dumps({"valid": True, "zqir": core.SPEC_VERSION}))
        return 0
    if a.command == "export-qasm3":
        print(core.export_qasm3(spec))
        return 0

    out = core.evaluate(spec)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    print(text)
    return 0 if out["verdict"] != "REFUSED" else 3


if __name__ == "__main__":
    sys.exit(main())
