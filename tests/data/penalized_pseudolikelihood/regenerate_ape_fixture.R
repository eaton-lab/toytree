#!/usr/bin/env Rscript

# Regenerate fixed-fit reference values with ape 5.8-1.
# Run from the repository root and review the JSON diff before committing:
# Rscript tests/data/penalized_pseudolikelihood/regenerate_ape_fixture.R

if (!requireNamespace("ape", quietly = TRUE)) stop("Install ape 5.8-1 first.")
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Install jsonlite first.")
if (as.character(packageVersion("ape")) != "5.8.1") {
    stop("This fixture is pinned to ape 5.8-1.")
}

tree <- ape::read.tree(
    text = "((a:0.2,b:0.3):0.4,(c:0.5,d:0.6):0.2);"
)
calibration <- ape::makeChronosCalib(
    tree, node = "root", age.min = 1, age.max = 1
)

fit_one <- function(model, ncategories = NULL) {
    control <- ape::chronos.control()
    if (model == "discrete") control$nb.rate.cat <- ncategories
    fit <- ape::chronos(
        tree,
        lambda = 0.5,
        model = model,
        calibration = calibration,
        control = control,
        quiet = TRUE
    )
    result <- list(
        time_edge_lengths = unname(fit$edge.length),
        rates = unname(attr(fit, "rates")),
        loglik = unname(attr(fit, "PHIIC")$logLik)
    )
    if (model == "discrete") {
        result$weights <- unname(attr(fit, "frequencies"))
    }
    if (model == "relaxed") {
        nedge <- length(result$rates)
        empirical <- seq_len(nedge) / nedge
        fitted <- pgamma(sort(result$rates), mean(result$rates))
        result$penalized_loglik <- unname(attr(fit, "ploglik"))
        result$penalty <- unname(sum((empirical - fitted)^2))
    }
    result
}

edge_clades <- vapply(tree$edge[, 2], function(node) {
    tips <- if (node <= ape::Ntip(tree)) node else ape::Descendants(
        tree, node, type = "tips"
    )[[1]]
    paste(sort(tree$tip.label[tips]), collapse = ",")
}, character(1))

fixture <- list(
    reference = "ape::chronos",
    ape_version = as.character(packageVersion("ape")),
    lambda = 0.5,
    newick = ape::write.tree(tree),
    observed_edge_lengths = unname(tree$edge.length),
    edge_clades = unname(edge_clades),
    models = list(
        clock = fit_one("clock"),
        discrete = fit_one("discrete", 2),
        discrete3 = fit_one("discrete", 3),
        relaxed = fit_one("relaxed")
    )
)

jsonlite::write_json(
    fixture,
    "tests/data/penalized_pseudolikelihood/ape-5.8.1.json",
    pretty = TRUE,
    auto_unbox = TRUE,
    digits = 17
)
