"""Shared pytest fixtures and helpers for repository tests."""

from __future__ import annotations

import builtins
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import toytree


class PytestCompat:
    """Minimal unittest-like assertions for pytest migration.

    This class allows existing unittest-style test classes to run under
    pytest with minimal logic churn. It also bridges ``setUp`` / ``tearDown``
    into pytest's xunit hooks.
    """

    def setup_method(self, _method):
        """Call legacy ``setUp`` if it exists."""
        setup = getattr(self, "setUp", None)
        if callable(setup):
            setup()

    def teardown_method(self, _method):
        """Call legacy ``tearDown`` if it exists."""
        teardown = getattr(self, "tearDown", None)
        if callable(teardown):
            teardown()

    class _AssertRaisesContext:
        """Compat context manager exposing ``.exception`` like unittest."""

        def __init__(self, exc, match=None):
            self._exc = exc
            self._match = match
            self._ctx = None
            self._excinfo = None
            self.exception = None

        def __enter__(self):
            self._ctx = pytest.raises(self._exc, match=self._match)
            self._excinfo = self._ctx.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb):
            handled = self._ctx.__exit__(exc_type, exc, tb)
            if handled and self._excinfo is not None:
                self.exception = self._excinfo.value
            return handled

    def assertRaises(self, exc):
        """Context manager equivalent of ``unittest.TestCase.assertRaises``."""
        return self._AssertRaisesContext(exc)

    def assertRaisesRegex(self, exc, match):
        """Context manager equivalent of ``assertRaisesRegex``."""
        return self._AssertRaisesContext(exc, match=match)

    @contextmanager
    def subTest(self, **_params):
        """No-op unittest ``subTest`` compatibility context manager."""
        yield

    def assertEqual(self, left, right, msg=None):
        assert left == right, msg

    def assertNotEqual(self, left, right, msg=None):
        assert left != right, msg

    def assertTrue(self, expr, msg=None):
        assert bool(expr), msg

    def assertFalse(self, expr, msg=None):
        assert not bool(expr), msg

    def assertIs(self, left, right, msg=None):
        assert left is right, msg

    def assertIsNot(self, left, right, msg=None):
        assert left is not right, msg

    def assertIsNone(self, expr, msg=None):
        assert expr is None, msg

    def assertIsNotNone(self, expr, msg=None):
        assert expr is not None, msg

    def assertIn(self, member, container, msg=None):
        assert member in container, msg

    def assertNotIn(self, member, container, msg=None):
        assert member not in container, msg

    def assertLess(self, left, right, msg=None):
        assert left < right, msg

    def assertLessEqual(self, left, right, msg=None):
        assert left <= right, msg

    def assertGreater(self, left, right, msg=None):
        assert left > right, msg

    def assertGreaterEqual(self, left, right, msg=None):
        assert left >= right, msg

    def assertIsInstance(self, obj, cls, msg=None):
        assert isinstance(obj, cls), msg

    def assertAlmostEqual(self, left, right, places=7, msg=None, delta=None):
        if delta is not None:
            assert abs(left - right) <= delta, msg
        else:
            assert round(abs(left - right), places) == 0, msg

    def assertNotAlmostEqual(self, left, right, places=7, msg=None, delta=None):
        if delta is not None:
            assert abs(left - right) > delta, msg
        else:
            assert round(abs(left - right), places) != 0, msg


# Expose compatibility base globally for test modules during collection.
builtins.PytestCompat = PytestCompat


@pytest.fixture
def rng_factory() -> Callable[[int | None], np.random.Generator]:
    """Return a helper for deterministic NumPy random generators."""

    def _make(seed: int | None = None) -> np.random.Generator:
        return np.random.default_rng(seed)

    return _make


@pytest.fixture
def make_unittree() -> Callable[[int, float, int], toytree.ToyTree]:
    """Return a helper that creates reproducible unit trees."""

    def _make(
        ntips: int,
        treeheight: float = 1.0,
        seed: int = 123,
    ) -> toytree.ToyTree:
        return toytree.rtree.unittree(ntips=ntips, treeheight=treeheight, seed=seed)

    return _make


@pytest.fixture
def make_imbtree() -> Callable[[int, float, int, bool], toytree.ToyTree]:
    """Return a helper that creates reproducible imbalanced trees."""

    def _make(
        ntips: int,
        treeheight: float = 1.0,
        seed: int = 123,
        random_names: bool = False,
    ) -> toytree.ToyTree:
        return toytree.rtree.imbtree(
            ntips=ntips,
            treeheight=treeheight,
            seed=seed,
            random_names=random_names,
        )

    return _make


@pytest.fixture
def make_baltree() -> Callable[[int, float, int, bool], toytree.ToyTree]:
    """Return a helper that creates reproducible balanced trees."""

    def _make(
        ntips: int,
        treeheight: float = 1.0,
        seed: int = 123,
        random_names: bool = False,
    ) -> toytree.ToyTree:
        return toytree.rtree.baltree(
            ntips=ntips,
            treeheight=treeheight,
            seed=seed,
            random_names=random_names,
        )

    return _make


@pytest.fixture
def parse_tree() -> Callable[..., toytree.ToyTree]:
    """Return a helper to parse Newick into ``ToyTree``."""

    def _parse(newick: str, **kwargs) -> toytree.ToyTree:
        return toytree.tree(newick, **kwargs)

    return _parse


@pytest.fixture
def write_text_file(tmp_path: Path) -> Callable[[str, str], Path]:
    """Return a helper that writes text files under a test tmp directory."""

    def _write(name: str, text: str, encoding: str = "utf-8") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding=encoding)
        return path

    return _write


@pytest.fixture
def tip_labels() -> Callable[[toytree.ToyTree], list[str]]:
    """Return a helper that provides tree tip labels in traversal order."""

    def _labels(tree: toytree.ToyTree) -> list[str]:
        return tree.get_tip_labels()

    return _labels


@pytest.fixture
def simulate_mv_continuous_tips(
    tip_labels: Callable[[toytree.ToyTree], list[str]],
) -> Callable[..., pd.DataFrame]:
    """Return a helper to simulate multivariate continuous tip traits."""

    def _simulate(
        tree: toytree.ToyTree,
        params: np.ndarray | None = None,
        seed: int = 123,
        set_tip_index: bool = True,
    ) -> pd.DataFrame:
        if params is None:
            params = np.diag([0.5, 1.0])
        data = tree.pcm.simulate_multivariate_continuous_trait(
            model="bm",
            params=params,
            tips_only=True,
            seed=seed,
        )
        if set_tip_index:
            data.index = tip_labels(tree)
        return data

    return _simulate


@pytest.fixture
def simulate_discrete_tips(
    tip_labels: Callable[[toytree.ToyTree], list[str]],
) -> Callable[..., pd.Series]:
    """Return a helper to simulate a single discrete tip trait."""

    def _simulate(
        tree: toytree.ToyTree,
        nstates: int = 2,
        model: str = "ER",
        seed: int = 123,
        as_int: bool = False,
        set_tip_index: bool = True,
        **kwargs,
    ) -> pd.Series:
        data = tree.pcm.simulate_discrete_trait(
            nstates=nstates,
            model=model,
            tips_only=True,
            seed=seed,
            **kwargs,
        )
        if isinstance(data, pd.DataFrame):
            data = data.iloc[:, 0]
        if set_tip_index:
            data.index = tip_labels(tree)
        if as_int:
            data = data.astype(int)
        return data

    return _simulate


@pytest.fixture
def add_feature_from_tip_series() -> Callable[..., toytree.ToyTree]:
    """Return a helper that writes tip-series values as node data."""

    def _add(
        tree: toytree.ToyTree,
        feature: str,
        series: pd.Series,
        default: float = np.nan,
    ) -> toytree.ToyTree:
        return tree.set_node_data(feature, dict(series), default=default, inplace=False)

    return _add


@pytest.fixture
def build_pglm_binary_dataframe(
    rng_factory: Callable[[int | None], np.random.Generator],
    tip_labels: Callable[[toytree.ToyTree], list[str]],
) -> Callable[[toytree.ToyTree, int], pd.DataFrame]:
    """Return a helper that builds reproducible binary-response PGLM data."""

    def _build(tree: toytree.ToyTree, seed: int = 123) -> pd.DataFrame:
        rng = rng_factory(seed)
        x = rng.normal(size=tree.ntips)
        group = np.array(["A" if i % 2 else "B" for i in range(tree.ntips)])
        vcv = tree.pcm.get_vcv_matrix_from_tree()
        e = rng.multivariate_normal(np.zeros(tree.ntips), vcv * 0.1)
        p = 1.0 / (1.0 + np.exp(-(-0.2 + 1.1 * x + e)))
        y = rng.binomial(1, p, size=tree.ntips)
        return pd.DataFrame({"x": x, "group": group, "y": y}, index=tip_labels(tree))

    return _build


@pytest.fixture
def distance_matrix_5taxa_additive() -> pd.DataFrame:
    """Return a labeled additive 5-taxon distance matrix."""
    labels = list("abcde")
    dist = np.array(
        [
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 2],
            [6, 6, 6, 2, 0],
        ],
        dtype=float,
    )
    return pd.DataFrame(dist, index=labels, columns=labels)


@pytest.fixture
def distance_matrix_5taxa_equal_tie() -> pd.DataFrame:
    """Return a tie-heavy 5-taxon matrix with equal competing joins."""
    labels = list("abcde")
    dist = np.array(
        [
            [0, 3, 4, 6, 6],
            [3, 0, 4, 6, 6],
            [4, 4, 0, 6, 6],
            [6, 6, 6, 0, 3],
            [6, 6, 6, 3, 0],
        ],
        dtype=float,
    )
    return pd.DataFrame(dist, index=labels, columns=labels)


@pytest.fixture
def distance_matrix_5taxa_polytomy_like() -> np.ndarray:
    """Return a 5-taxon matrix with polytomy-like equal distances."""
    return np.array(
        [
            [0, 2, 2, 4, 4],
            [2, 0, 2, 4, 4],
            [2, 2, 0, 4, 4],
            [4, 4, 4, 0, 2],
            [4, 4, 4, 2, 0],
        ],
        dtype=float,
    )


@pytest.fixture
def mtree_consensus_utrees() -> toytree.MultiTree:
    """Return unrooted trees used in consensus tests."""
    return toytree.mtree(
        [
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(e:2,(c:3,d:2):1):1);",
            "((a:1,b:1):3,(d:2,(c:3,e:2):1):1);",
            "((d:2,(c:3,e:2):1),(a:1,b:1):3):1;",
        ]
    )


@pytest.fixture
def mtree_consensus_rtrees() -> toytree.MultiTree:
    """Return rooted ultrametric-like trees used in consensus tests."""
    return toytree.mtree(
        [
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(c:3,(d:2,e:2):1):1);",
            "((a:1,b:1):3,(e:3,(c:2,d:2):1):1);",
            "((a:1,b:1):3,(d:3,(c:2,e:2):1):1);",
            "((a:1,b:1):4,(d:3,(c:2,e:2):1):2);",
        ]
    )


@pytest.fixture
def gradient_canvas_factory() -> Callable[[], object]:
    """Return a helper that builds a canvas with gradient edge annotations."""

    def _make():
        tree = toytree.rtree.bdtree(8, seed=123)
        tree.pcm.simulate_discrete_trait(
            3,
            trait_name="X",
            state_names="ABC",
            inplace=True,
            seed=123,
        )
        canvas, axes, _ = tree.draw(layout="c", edge_type="p")
        tree.annotate.add_edges(
            axes,
            color=("X", "Dark2"),
            use_color_gradient=True,
            mask=(1, 1, 1),
        )
        return canvas

    return _make
