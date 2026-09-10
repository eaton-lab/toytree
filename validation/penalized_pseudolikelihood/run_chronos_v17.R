#!/usr/bin/env Rscript

# Run one ape::chronos fit for the paired V17 benchmark. This script uses a
# two-column key/value protocol on stdout so jsonlite is not required.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 6L) {
    stop(paste(
        "usage: run_chronos_v17.R TREE CALIBRATIONS MODEL LAMBDA",
        "NCATEGORIES EXPECTED_APE_VERSION"
    ))
}

if (!requireNamespace("ape", quietly = TRUE)) {
    stop("the R package 'ape' is required")
}

tree_path <- args[[1L]]
calibration_path <- args[[2L]]
model <- args[[3L]]
lambda <- as.numeric(args[[4L]])
ncategories <- as.integer(args[[5L]])
expected_ape_version <- args[[6L]]
ape_version <- as.character(utils::packageVersion("ape"))

if (nzchar(expected_ape_version) && ape_version != expected_ape_version) {
    stop(sprintf(
        "ape version %s does not match required version %s",
        ape_version,
        expected_ape_version
    ))
}

clean_value <- function(value) {
    value <- paste(value, collapse = " ")
    value <- gsub("\t", " ", value, fixed = TRUE)
    value <- gsub("\r", " ", value, fixed = TRUE)
    value <- gsub("\n", " ", value, fixed = TRUE)
    trimws(value)
}

numeric_vector <- function(value) {
    if (is.null(value)) return("")
    paste(format(unname(value), digits = 17), collapse = ",")
}

descendant_tips <- function(phy, node) {
    if (node <= ape::Ntip(phy)) return(node)
    children <- phy$edge[phy$edge[, 1L] == node, 2L]
    unlist(lapply(children, function(child) descendant_tips(phy, child)))
}

emit <- function(key, value) {
    cat(key, "\t", clean_value(value), "\n", sep = "")
}

tree <- ape::read.tree(tree_path)
calibration_table <- utils::read.delim(
    calibration_path,
    stringsAsFactors = FALSE,
    check.names = FALSE
)
nodes <- integer(nrow(calibration_table))
for (idx in seq_len(nrow(calibration_table))) {
    clade <- calibration_table$clade[[idx]]
    if (identical(clade, "__root__")) {
        nodes[[idx]] <- ape::Ntip(tree) + 1L
    } else {
        tips <- strsplit(clade, "|", fixed = TRUE)[[1L]]
        node <- ape::getMRCA(tree, tips)
        if (is.null(node) || is.na(node)) {
            stop(sprintf("calibration clade did not resolve: %s", clade))
        }
        nodes[[idx]] <- node
    }
}
calibration <- ape::makeChronosCalib(
    tree,
    node = nodes,
    age.min = calibration_table$lower,
    age.max = calibration_table$upper
)

control <- ape::chronos.control()
if (identical(model, "discrete")) {
    control$nb.rate.cat <- ncategories
}

warnings <- character()
started <- proc.time()[["elapsed"]]
fit <- tryCatch(
    withCallingHandlers(
        ape::chronos(
            tree,
            lambda = lambda,
            model = model,
            calibration = calibration,
            control = control,
            quiet = TRUE
        ),
        warning = function(condition) {
            warnings <<- c(warnings, conditionMessage(condition))
            invokeRestart("muffleWarning")
        }
    ),
    error = function(condition) condition
)
elapsed <- proc.time()[["elapsed"]] - started

emit("protocol", "toytree-chronos-v17")
emit("ape_version", ape_version)
emit("elapsed_seconds", format(elapsed, digits = 17, scientific = FALSE))
if (inherits(fit, "condition")) {
    emit("status", "error")
    emit("error", conditionMessage(fit))
    emit("warnings", paste(warnings, collapse = " || "))
    quit(status = 0L)
}

phiic <- attr(fit, "PHIIC")
convergence <- attr(fit, "convergence")
message <- attr(fit, "message")
emit("status", "ok")
emit("tree_newick", ape::write.tree(fit, digits = 17))
emit("rates", numeric_vector(attr(fit, "rates")))
emit("frequencies", numeric_vector(attr(fit, "frequencies")))
rates <- unname(attr(fit, "rates"))
if (length(rates) == nrow(fit$edge)) {
    rate_clades <- vapply(fit$edge[, 2L], function(node) {
        tips <- descendant_tips(fit, node)
        paste(sort(fit$tip.label[tips]), collapse = "|")
    }, character(1L))
    emit("rate_clades", paste(rate_clades, collapse = ","))
} else {
    emit("rate_clades", "")
}
emit("loglik", if (is.null(phiic$logLik)) "" else format(unname(phiic$logLik), digits = 17))
emit("penalized_loglik", if (is.null(attr(fit, "ploglik"))) "" else format(unname(attr(fit, "ploglik")), digits = 17))
emit("convergence", if (is.null(convergence)) "" else convergence)
emit("converged", is.null(convergence) || isTRUE(convergence))
emit("message", if (is.null(message)) "" else message)
emit("warnings", paste(warnings, collapse = " || "))
