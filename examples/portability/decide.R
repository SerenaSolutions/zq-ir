# R: idem — o veredito não pertence a nenhum framework.
spec <- commandArgs(trailingOnly = TRUE)
spec <- if (length(spec)) spec[1] else "examples/decide_const1.json"
out <- system2("zq-ir", c("decide", spec), stdout = TRUE)
d <- jsonlite::fromJSON(paste(out, collapse = "\n"))
cat(sprintf("veredito=%s selo=%s\n", d$verdict, substr(d$receipt$seal_sha3_256, 1, 16)))
