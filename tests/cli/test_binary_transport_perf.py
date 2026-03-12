#!/usr/bin/env python

"""Performance checks for CLI text vs binary tree transport."""

from __future__ import annotations

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
    """Measure binary CLI transport against text Newick pipelines."""

    def setUp(self):
        """Create benchmark inputs spanning small/large and plain/packed cases."""
        self.tmpdir = Path(tempfile.mkdtemp(prefix="toytree-cli-perf-"))
        self.exe = f"{shlex.quote(sys.executable)} -m toytree.cli.main"
        self.reps = int(os.environ.get("TOYTREE_PERF_REPS", "3"))
        self.small_tips = int(os.environ.get("TOYTREE_PERF_SMALL_TIPS", "25"))
        self.large_tips = int(os.environ.get("TOYTREE_PERF_LARGE_TIPS", "4000"))
        self.min_large_speedup = float(
            os.environ.get("TOYTREE_PERF_MIN_SPEEDUP", "50.0")
        )
        self.case_paths = {
            "small_plain": self._write_tree("small_plain.nwk", self.small_tips, False),
            "small_packed": self._write_tree(
                "small_packed.nwk",
                self.small_tips,
                True,
            ),
            "large_plain": self._write_tree("large_plain.nwk", self.large_tips, False),
            "large_packed": self._write_tree(
                "large_packed.nwk",
                self.large_tips,
                True,
            ),
        }

    def _write_tree(self, name: str, ntips: int, packed: bool) -> Path:
        """Write one benchmark input tree and return its path."""
        tree = toytree.rtree.unittree(ntips=ntips, seed=123)
        if packed:
            tree = tree.set_node_data("posterior", default=[0.05, 0.15, 0.8])
            text = tree.write(features=["posterior"])
        else:
            text = tree.write(None)
        path = self.tmpdir / name
        path.write_text(text + "\n", encoding="utf-8")
        return path

    def _pipeline_cmd(self, tree_path: Path, binary: bool) -> str:
        ipath = shlex.quote(str(tree_path))
        b1 = " -b" if binary else ""
        b2 = " -b" if binary else ""
        b3 = " -b" if binary else ""
        return (
            f"{self.exe} set-node-data -i {ipath} -f A -s 0=1 -d 0{b1} | "
            f"{self.exe} set-node-data -i - -f B -s 1=2 -d 0{b2} | "
            f"{self.exe} set-node-data -i - -f C -s 2=3 -d 0{b3} | "
            f"{self.exe} set-node-data -i - -f D -s 3=4 -d 0 > /dev/null"
        )

    def _run_once(self, tree_path: Path, binary: bool) -> float:
        cmd = self._pipeline_cmd(tree_path, binary)
        start = time.perf_counter()
        proc = subprocess.run(["bash", "-lc", cmd], capture_output=True)
        elapsed = time.perf_counter() - start
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(
                f"pipeline failed for {tree_path.name} (binary={binary}):\n{stderr}"
            )
        return elapsed

    def _benchmark_case(self, name: str) -> dict[str, object]:
        """Return timing summary for one benchmark input."""
        tree_path = self.case_paths[name]

        # Warm-up both parse/serialize paths before timing.
        self._run_once(tree_path, binary=False)
        self._run_once(tree_path, binary=True)

        text_times: list[float] = []
        binary_times: list[float] = []
        # Alternate order to reduce launch/cache bias in short runs.
        for rep in range(self.reps):
            if rep % 2 == 0:
                text_times.append(self._run_once(tree_path, binary=False))
                binary_times.append(self._run_once(tree_path, binary=True))
            else:
                binary_times.append(self._run_once(tree_path, binary=True))
                text_times.append(self._run_once(tree_path, binary=False))

        text_med = statistics.median(text_times)
        binary_med = statistics.median(binary_times)
        speedup = ((text_med - binary_med) / text_med) * 100.0

        return {
            "name": name,
            "input_bytes": tree_path.stat().st_size,
            "text_times": text_times,
            "binary_times": binary_times,
            "text_median": text_med,
            "binary_median": binary_med,
            "speedup": speedup,
        }

    def test_binary_pipeline_has_clear_speedup(self):
        """Require strong large-tree speedups while reporting small-tree timings."""
        results = [
            self._benchmark_case("small_plain"),
            self._benchmark_case("small_packed"),
            self._benchmark_case("large_plain"),
            self._benchmark_case("large_packed"),
        ]

        for result in results:
            text_med = result["text_median"]
            binary_med = result["binary_median"]
            speedup = result["speedup"]
            text_times = result["text_times"]
            binary_times = result["binary_times"]
            input_bytes = result["input_bytes"]
            name = result["name"]
            assert isinstance(text_med, float)
            assert isinstance(binary_med, float)
            assert isinstance(speedup, float)
            assert isinstance(text_times, list)
            assert isinstance(binary_times, list)
            print(
                f"\n{name} input_bytes={input_bytes} "
                f"text_times={[round(i, 4) for i in text_times]} "
                f"binary_times={[round(i, 4) for i in binary_times]} "
                f"text_median={text_med:.4f}s "
                f"binary_median={binary_med:.4f}s "
                f"speedup={speedup:.2f}%"
            )

        for name in ("large_plain", "large_packed"):
            result = next(item for item in results if item["name"] == name)
            text_med = result["text_median"]
            binary_med = result["binary_median"]
            speedup = result["speedup"]
            assert isinstance(text_med, float)
            assert isinstance(binary_med, float)
            assert isinstance(speedup, float)
            self.assertGreaterEqual(
                speedup,
                self.min_large_speedup,
                msg=(
                    "expected binary transport to remain clearly faster on "
                    f"{name}; text={text_med:.4f}s binary={binary_med:.4f}s "
                    f"speedup={speedup:.2f}% "
                    f"target={self.min_large_speedup:.2f}%"
                ),
            )
