#!/usr/bin/env python

"""Tests for root CLI modes and argument validation."""

import pickle
import tempfile
from pathlib import Path

from toytree.cli.cli_root import get_parser_root, run_root
from toytree.utils import ToytreeError



from conftest import PytestCompat

class TestCLIRoot(PytestCompat):
    """Validate root CLI mode selection and DLC option handling."""

    def setUp(self):
        """Create temporary trees and parser for each test."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-root-"))
        self.gene_path = self.tmpdir / "gene.nwk"
        self.species_path = self.tmpdir / "species.nwk"
        self.imap_path = self.tmpdir / "imap.tsv"
        self.gene_path.write_text("((a1:1,b1:1):1,c1:1,d1:1);\n", encoding="utf-8")
        self.species_path.write_text("(((A:1,B:1):1,C:1):1,D:1);\n", encoding="utf-8")
        self.imap_path.write_text(
            "a1\tA\nb1\tB\nc1\tC\nd1\tD\n",
            encoding="utf-8",
        )
        self.parser = get_parser_root()

    def test_requires_species_tree_for_dlc(self):
        """DLC mode requires a species tree input."""
        args = self.parser.parse_args(["-i", str(self.gene_path), "--dlc"])
        with self.assertRaises(ToytreeError):
            run_root(args)

    def test_rejects_nodes_with_dlc(self):
        """Nodes and DLC mode are intentionally incompatible."""
        args = self.parser.parse_args(
            [
                "-i",
                str(self.gene_path),
                "--dlc",
                "--species-tree",
                str(self.species_path),
                "-n",
                "a1",
            ]
        )
        with self.assertRaises(ToytreeError):
            run_root(args)

    def test_dlc_root_with_imap_binary_out(self):
        """DLC mode roots tree and stores DLC features when --stats is set."""
        outpath = self.tmpdir / "rooted.bin"
        args = self.parser.parse_args(
            [
                "-i",
                str(self.gene_path),
                "--dlc",
                "--species-tree",
                str(self.species_path),
                "--imap",
                str(self.imap_path),
                "--stats",
                "-b",
                "-o",
                str(outpath),
            ]
        )
        run_root(args)
        tree = pickle.loads(outpath.read_bytes())
        self.assertTrue(tree.is_rooted())
        self.assertIn("DLC", tree.features)
        self.assertIn("DLC_root_prob", tree.features)

    def test_dlc_root_with_delim_matching(self):
        """DLC mode supports deriving species labels from gene labels by delimiter."""
        gene_path = self.tmpdir / "gene_delim.nwk"
        species_path = self.tmpdir / "species_delim.nwk"
        gene_path.write_text("((A|x:1,B|x:1):1,C|x:1,D|x:1);\n", encoding="utf-8")
        species_path.write_text("(((A:1,B:1):1,C:1):1,D:1);\n", encoding="utf-8")
        outpath = self.tmpdir / "rooted_delim.bin"

        args = self.parser.parse_args(
            [
                "-i",
                str(gene_path),
                "--dlc",
                "--species-tree",
                str(species_path),
                "--delim",
                r"\|",
                "--delim-idxs",
                "0",
                "-b",
                "-o",
                str(outpath),
            ]
        )
        run_root(args)
        tree = pickle.loads(outpath.read_bytes())
        self.assertTrue(tree.is_rooted())
        self.assertNotIn("DLC", tree.features)
        self.assertNotIn("DLC_root_prob", tree.features)

    def test_rejects_dlc_options_without_dlc(self):
        """DLC-specific options are rejected unless --dlc is selected."""
        args = self.parser.parse_args(
            [
                "-i",
                str(self.gene_path),
                "--species-tree",
                str(self.species_path),
                "-n",
                "a1",
            ]
        )
        with self.assertRaises(ToytreeError):
            run_root(args)


