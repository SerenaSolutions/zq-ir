# Julia: mesma porta de entrada.
using JSON3
spec = isempty(ARGS) ? "examples/decide_const1.json" : ARGS[1]
d = JSON3.read(read(`zq-ir decide $spec`, String))
println("veredito=$(d.verdict) selo=$(first(d.receipt.seal_sha3_256, 16))")
