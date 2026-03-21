##############################################################
#
#  VALIDATION FUNCTIONS FOR COMPARING TO R LIBRARY
#
#  TODO: move this to a test/ directory
##############################################################


def _test_with_treedist_r(
    tree1: ToyTree,
    tree2: ToyTree,
    method: str = "rf",
    normalize: bool = True,
) -> float:
    """Return distance calculated with R's TreeDist library.

    This is used only for validation/testing internally only. Users
    are not expected to have R or treedist installed, and no
    checks are performed. This is not used in unittests.
    """
    import subprocess
    import tempfile

    # get TreeDist function
    method = method.lower()
    if method == "rf":
        func = "RobinsonFoulds"
    elif method == "rfi":
        func = "InfoRobinsonFoulds"
    elif method == "rfg_spi":
        func = "PhylogeneticInfoDistance"
    elif method == "rfg_mci":
        func = "ClusteringInfoDist"
    else:
        raise NotImplementedError("could do, but didn't yet..")

    # write R script to a tmpfile
    script = "\n".join(
        [
            "library(TreeDist)",
            "t1 <- ape::read.tree(text='{}')".format(tree1.write(None, None, None)),
            "t2 <- ape::read.tree(text='{}')".format(tree2.write(None, None, None)),
            "dist <- {}(t1, t2, normalize={})".format(func, str(normalize).upper()),
            "print(dist)",
        ]
    )

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as tmp:
        tmp.write(script)
        tmp.flush()

        # run Rscript on the tempfile and catch stdout
        cmd = ["Rscript", "--vanilla", tmp.name]
        args = {"args": cmd, "stdout": subprocess.PIPE, "stderr": subprocess.STDOUT}
        with subprocess.Popen(**args, encoding="utf-8") as proc:
            out, _ = proc.communicate()
        # log the error
        try:
            out = float(out.split()[-1])
        except (ValueError, IndexError):
            logger.error(out)
    return out


def _validate(tree1, tree2):
    """Return dataframe with results for toytree and TreeDist"""
    algorithms = {
        "rf": get_treedist_rf,
        "rfi": get_treedist_rfi,
        "rfg_spi": get_treedist_rfg_spi,
        "rfg_mci": get_treedist_rfg_mci,
        # "qrt": get_treedist_qrt,
    }
    anames = list(algorithms) + [i + "-norm" for i in algorithms]
    data = pd.DataFrame(
        index=anames,
        columns=["toytree", "TreeDist"],
        data=0,
    )

    for algo, func in algorithms.items():
        for norm in (True, False):
            toy = func(tree1, tree2, normalize=norm)
            trd = _test_with_treedist_r(tree1, tree2, algo, norm)
            aname = algo + "-norm" if norm else algo
            data.loc[aname] = toy, trd
    return data
