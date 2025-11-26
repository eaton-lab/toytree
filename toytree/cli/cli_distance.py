#!/usr/bin/env python



    # # toytree distance [options] TREE TREE ----------------------------------
    # parser_distance = subparsers.add_parser("distance", help="compute distance between trees")
    # parser_distance.add_argument("TREE1", type=str, help="tree1 newick file or string")
    # parser_distance.add_argument("TREE2", type=str, help="tree2 newick file or string")
    # parser_distance.add_argument(
    #     "-m", type=str,
    #     choices=['rf', 'rfi', 'rfj', 'qrt'],
    #     default='rf',
    #     help="distance metric method",
    # )
    # parser_distance.add_argument(
    #     "-n", "--normalize", action="store_true",
    #     help="normalize value between [0-1]")
    # return parser


    # # distance
    # if args.subcommand == "distance":
    #     tree1 = toytree.tree(args.TREE1)
    #     tree2 = toytree.tree(args.TREE2)
    #     norm = {"normalize": args.normalize}
    #     if args.m == "rf":
    #         val = toytree.distance.get_treedist_rf(tree1, tree2, **norm)
    #     elif args.m == "rfg_mci":
    #         val = toytree.distance.get_treedist_rfg_mci(tree1, tree2, **norm)
    #     elif args.m == "rfg_spi":
    #         val = toytree.distance.get_treedist_rfg_spi(tree1, tree2, **norm)
    #     elif args.m == "rfi":
    #         val = toytree.distance.get_treedist_rfi(tree1, tree2, **norm)
    #     elif args.m == "qrt":
    #         val = toytree.distance.get_treedist_qrt(tree1, tree2)
    #     sys.stdout.write(val)
    #     return 0