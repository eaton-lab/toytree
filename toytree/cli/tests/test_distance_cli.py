#!/usr/bin/env python

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from toytree.cli.cli_distance import get_parser_distance, run_distance


class TestDistanceCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-distance-"))
        self.t1 = self.tmpdir / "t1.nwk"
        self.t2 = self.tmpdir / "t2.nwk"
        self.t1.write_text("((a:1,b:1):1,(c:1,d:1):1);\n", encoding="utf-8")
        self.t2.write_text("((a:1,c:1):1,(b:1,d:1):1);\n", encoding="utf-8")
        self.parser = get_parser_distance()

    def _run_capture_stdout(self, argv):
        args = self.parser.parse_args(argv)
        stream = io.StringIO()
        with redirect_stdout(stream):
            run_distance(args)
        return stream.getvalue().strip()

    def test_rf_distance_scalar(self):
        out = self._run_capture_stdout(
            ["-i", str(self.t1), "-j", str(self.t2), "-m", "rf"]
        )
        self.assertEqual(float(out), 2.0)

    def test_rf_distance_normalized(self):
        out = self._run_capture_stdout(
            ["-i", str(self.t1), "-j", str(self.t2), "-m", "rf", "--normalize"]
        )
        self.assertEqual(float(out), 1.0)

    def test_quartet_all_outputs_table(self):
        out = self._run_capture_stdout(
            ["-i", str(self.t1), "-j", str(self.t2), "-m", "quartet-all"]
        )
        self.assertIn("symmetric_difference\t", out)
        self.assertIn("steel_and_penny\t", out)


if __name__ == "__main__":
    unittest.main()

