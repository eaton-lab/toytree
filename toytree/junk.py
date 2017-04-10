

## DEPRECATED

def _simulate(self, nreps=1000, admix=None, Ns=int(5e5), gen=10):
    sims = _simulate(self, nreps, admix, Ns, gen)
    debug = 0  ## msprime debug
    names = self.tree.get_leaf_names()[::-1]
    Sims = Sim(names, sims, nreps, debug)
    return Sims


def _collapse_outgroup(tree, taxdicts):
    """ collapse outgroup in ete Tree for easier viewing """
    ## check that all tests have the same outgroup
    outg = taxdicts[0]["p4"]
    if not all([i["p4"] == outg for i in taxdicts]):
        raise Exception("no good")
   
    ## prune tree, keep only one sample from outgroup
    tre = ete.Tree(tree.write(format=1)) #tree.copy(method="deepcopy")
    alltax = [i for i in tre.get_leaf_names() if i not in outg]
    alltax += [outg[0]]
    tre.prune(alltax)
    tre.search_nodes(name=outg[0])[0].name = "outgroup"
    tre.ladderize()

    ## remove other ougroups from taxdicts
    taxd = copy.deepcopy(taxdicts)
    newtaxdicts = []
    for test in taxd:
        #test["p4"] = [outg[0]]
        test["p4"] = ["outgroup"]
        newtaxdicts.append(test)

    return tre, newtaxdicts




def __admix():

    ## plot admix lines ---------------------------------
    if self.admix:
        for event in self.admix:
            ## get event
            source, sink, _, _, _ = event

            ## get nodes from tree
            source = self.tree.search_nodes(name=source)[0]
            sink = self.tree.search_nodes(name=sink)[0]

            ## get coordinates
            fromx = np.max([source.up.x, source.x]) - np.abs(source.up.x - source.x) / 2.
            fromy = source.y + (source.up.y - source.y) / 2.
            tox = np.max([sink.up.x, sink.x]) - np.abs(sink.up.x - sink.x) / 2.
            toy = sink.y + (sink.up.y - sink.y) / 2.
                
            ## if show_tips:
            if show_tips:
                fromy += spacer
                toy += spacer

            ## plot
            mark = axes.plot([fromx, tox], [fromy, toy], 
                            color=toyplot.color.Palette()[1], 
                            style={"stroke-width": 3, 
                                   "stroke-dasharray": "2, 2"},
                            )
                
    ## hide x and hide/show y axies
    axes.x.show = False
    if yaxis:
        axes.y.show = True
    else:
        axes.y.show = False    

    ## return plotting 
    return canvas, axes