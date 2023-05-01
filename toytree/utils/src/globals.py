#!/usr/bin/env python

"""globals.

"""



# TREE FORMATS
NW_FORMAT = {
    # flexible with support
    # Format 0 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    0: [
        ('name', str, True),
        ('dist', float, True),
        ('support', float, True),
        ('dist', float, True),
    ],

    # flexible with internal node names
    # Format 1 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    1: [
        ('name', str, True),
        ('dist', float, True),
        ('name', str, True),
        ('dist', float, True),      
    ],

    # strict with support values
    # Format 2 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    2: [
        ('name', str, False),
        ('dist', float, False),
        ('support', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 3 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    3: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 4 = (A:0.35,(B:0.72,(D:0.60,G:0.12)));
    4: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        (None, None, False),      
    ],

    # Format 5 = (A:0.35,(B:0.72,(D:0.60,G:0.12):0.64):0.56);
    5: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        ('dist', float, False),      
    ],

    # Format 6 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E)C);
    6: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),        
        ('dist', float, False),      
    ],

    # Format 7 = (A,(B,(D,G)E)C);
    7: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),        
        (None, None, False),        
    ],    


    # Format 8 = (A,(B,(D,G)));
    8: [
        ('name', str, False),
        (None, None, False),
        ('name', str, False),        
        (None, None, False),
    ],

    # Format 9 = (,(,(,)));
    9: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),
        (None, None, False),
    ],    

    # Format 10 = ((a[&Z=1,Y=2]:1.0[&X=3], b[&Z=1,Y=2]:3.0[&X=2]):1.0[&L=1,W=0], ...
    # NHX Like mrbayes NEXUS common
    10: [
        ('name', str, True),
        ('dist', str, True),
        ('name', str, True),
        ('dist', str, True),
    ]
}

if __name__ == "__main__":
    pass
    # import toytree
    # toytree.set_log_level("DEBUG")
    # from toytree.utils.src.logger_setup import LOGGER
    # LOGGER.info("HI")
    # print(LOGGER)
