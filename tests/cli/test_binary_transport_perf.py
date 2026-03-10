#!/usr/bin/env python

import os
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
from conftest import PytestCompat

import toytree


@pytest.mark.skipif(
    os.environ.get("TOYTREE_RUN_PERF_TESTS") != "1",
    reason="set TOYTREE_RUN_PERF_TESTS=1 to run performance tests",
)
class TestBinaryTransportPerf(PytestCompat):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-perf-"))
        self.tree_path = self.tmpdir / "large_tree.nwk"
        # Large tree to amplify parse/serialize costs.
        tree = toytree.rtree.unittree(ntips=4000, seed=123)
        self.tree_path.write_text(tree.write(None) + "\n", encoding="utf-8")
        self.exe = f"{shlex.quote(sys.executable)} -m toytree.cli.main"
        self.reps = int(os.environ.get("TOYTREE_PERF_REPS", "3"))
        self.min_speedup = float(os.environ.get("TOYTREE_PERF_MIN_SPEEDUP", "20.0"))

    def _pipeline_cmd(self, binary: bool) -> str:
        ipath = shlex.quote(str(self.tree_path))
        b1 = " -b" if binary else ""
        b2 = " -b" if binary else ""
        b3 = " -b" if binary else ""
        return (
            f"{self.exe} set-node-data -i {ipath} -f A -s 0=1 -d 0{b1} | "
            f"{self.exe} set-node-data -i - -f B -s 1=2 -d 0{b2} | "
            f"{self.exe} set-node-data -i - -f C -s 2=3 -d 0{b3} | "
            f"{self.exe} set-node-data -i - -f D -s 3=4 -d 0 > /dev/null"
        )

    def _run_once(self, binary: bool) -> float:
        cmd = self._pipeline_cmd(binary)
        start = time.perf_counter()
        proc = subprocess.run(["bash", "-lc", cmd], capture_output=True)
        elapsed = time.perf_counter() - start
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"pipeline failed (binary={binary}):\n{stderr}")
        return elapsed

    def test_binary_pipeline_has_clear_speedup(self):
        # Warm-up.
        self._run_once(binary=False)
        self._run_once(binary=True)

        text_times = [self._run_once(binary=False) for _ in range(self.reps)]
        binary_times = [self._run_once(binary=True) for _ in range(self.reps)]

        text_med = statistics.median(text_times)
        binary_med = statistics.median(binary_times)
        speedup = ((text_med - binary_med) / text_med) * 100.0

        print(
            f"\ntext_median={text_med:.4f}s binary_median={binary_med:.4f}s "
            f"speedup={speedup:.2f}%"
        )
        self.assertGreaterEqual(
            speedup,
            self.min_speedup,
            msg=(
                "expected binary transport pipeline to be clearly faster; "
                f"text={text_med:.4f}s binary={binary_med:.4f}s "
                f"speedup={speedup:.2f}% target={self.min_speedup:.2f}%"
            ),
        )
