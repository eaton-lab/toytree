

## re-organization plan
This could go in the toytree/__init__.py


```
- toytree/
    - binder/
    - docs/
        - (current docs)
    - manuscript/
    - sandbox/
        - (experimental stuff)
    - toytree/
        - __init__.py
        - drawing/
            - CanvasSetup.py
            - Container.py
            - Coords.py
            - MultiDrawing.py
            - StyleChecker.py
            - TreeStyle.py
            - Render.py
        - pcm/
            - pcm.py
        - distance/
            - treedist.py
            - nodedist.py
        - random/
            - rtree.py
        - treemod/
            - Rooter.py
            - treemod.py
        - io/
            - TreeParser.py
            - TreeWriter.py

        - Multitree.py
        - TreeNode.py
        - Toytree.py
        - NodeAssist.py
        - utils.py
```


### goals

```python

import toytree

# new dependencies
- scipy     #  
- pandas    #  


tre = toytree.tree(PathLike, ToyTree, TreeNode, 'https://...', '(((),)...', ...)
tre = toytree.rawtree()
mtre = toytree.mtree()


toytree.rtree.[...]
    - rtree()
    - baltree()
    - imbtree()
    - unittree()
    - coaltree()
    - bdtree()


tree.pcm.[...](self, ...)
toytree.pcm.[...]
    - independent_contrasts()
    - ancestral_state_reconstruction()
    - tree_to_VCV()
    - ...


tre.mod.[...](self, ...)
toytree.mod.[...](tree, ...)
    - set_node_heights()
    - node_multiplier()
    - node_scale_root_height()
    - node_slider()
    - make_ultrametric()


tre.distance.[...](self, ...)
toytree.distance.[...]()
    - treedist_rf
    - treedist_quartets
    - patristic


tre.distance.patristic()
tre.distance.patristic_tips()
tre.distance.patristic_internal()
```