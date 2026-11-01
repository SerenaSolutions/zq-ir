// Node: mesma decisão, mesmo contrato, zero dependência de framework.
const { execFileSync } = require("child_process");
const spec = process.argv[2] || "examples/decide_const1.json";
const out = execFileSync("zq-ir", ["decide", spec], { encoding: "utf8" });
const d = JSON.parse(out);
console.log(`veredito=${d.verdict} motivo=${d.refusal_reason ?? "-"} selo=${d.receipt.seal_sha3_256.slice(0, 16)}`);
