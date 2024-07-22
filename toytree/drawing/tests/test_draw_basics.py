#!/usr/bin/env python

"""unittests for draw() function.

"""

import unittest
import numpy as np
from numpy.testing import assert_allclose
# from loguru import logger
from toytree.utils.src.logger_setup import capture_logs
import toytree


class TestDrawArgs(unittest.TestCase):

    def setUp(self):
        nwk = "((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;"
        self.rtree = toytree.tree(nwk)
        self.utree = self.rtree.unroot()

    def test_docs(self):
        """Ensure that ... in docs ..."""

        # all annotated args to draw()
        # self.rtree.draw.__func__.__annotations__
        # the docstring for draw()
        # docs = self.rtree.draw.__doc__.split("\n")
        # TODO: a test to ensure each arg is documented.
        # self.assertEqual(adoc, sdoc)

    def test_returned_types(self):
        """Require returned objects to be Canvas, Cartesian, Mark"""
        canvas, axes, mark = self.rtree.draw()
        self.assertTrue(isinstance(canvas, toytree.core.Canvas))
        self.assertTrue(isinstance(axes, toytree.core.Cartesian))
        self.assertTrue(isinstance(mark, toytree.core.Mark))
        self.assertTrue(isinstance(mark, toytree.drawing.ToyTreeMark))        


class TestDrawMarkETable(unittest.TestCase):

    def setUp(self):
        nwk = "((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;"
        self.rtree = toytree.tree(nwk)
        self.utree = self.rtree.unroot()

    def test_mark_etable(self):
        """Mark stores edges as int table."""
        # resolved rooted tree has nnodes - 1 edges (not including root edge)
        c, a, m = self.rtree.draw()
        self.assertTrue(isinstance(m.etable, np.ndarray))
        self.assertEqual(self.rtree.nedges, m.etable.shape[0])

        # ... root edge handling...

        # resolved unrooted tree has nnodes - 2 edges
        c, a, m = self.utree.draw()
        self.assertEqual(self.utree.nedges, m.etable.shape[0])

    def test_mark_etable_root_edge(self):
        """Drawing the root edge."""
        c, a, m = self.rtree.draw()


class TestDrawMarkDomainExtent(unittest.TestCase):

    def setUp(self):
        nwk = "((a:2,b:1)ab:1,(c:1,d:2)cd:1)r:2;"
        self.rtree = toytree.tree(nwk)
        self.utree = self.rtree.unroot()

    def test_domain_layout_right(self):
        """Domain is the size of the tree in data units. Drawing args
        like tip labels or node sizes do not affect this, only the
        node coordinates do. See Extents.
        """
        # right-facing tree
        c, a, m = self.rtree.draw(layout='r')  # default
        xmin, xmax = m.domain('x')
        ymin, ymax = m.domain('y')
        self.assertEqual(xmin, -self.rtree.treenode.height)
        self.assertEqual(xmax, 0.0)
        self.assertEqual(ymin, 0.0)
        self.assertEqual(ymax, self.rtree.ntips - 1)

    def test_domain_layout_down(self):
        # down-facing tree
        c, a, m = self.rtree.draw(layout='d')        
        xmin, xmax = m.domain('x')
        ymin, ymax = m.domain('y')
        self.assertEqual(xmin, 0.0)
        self.assertEqual(xmax, self.rtree.ntips - 1)
        self.assertEqual(ymin, 0.0)
        self.assertEqual(ymax, self.rtree.treenode.height)

    def test_domain_layout_up(self):
        # down-facing tree
        c, a, m = self.rtree.draw(layout='u')        
        xmin, xmax = m.domain('x')
        ymin, ymax = m.domain('y')
        self.assertEqual(xmin, 0.0)
        self.assertEqual(xmax, self.rtree.ntips - 1)
        self.assertEqual(ymin, -self.rtree.treenode.height)
        self.assertEqual(ymax, 0.0)

    def test_domain_layout_left(self):
        # down-facing tree
        c, a, m = self.rtree.draw(layout='l')
        xmin, xmax = m.domain('x')
        ymin, ymax = m.domain('y')
        self.assertEqual(xmin, 0.0)
        self.assertEqual(xmax, self.rtree.ntips - 1)
        self.assertEqual(ymin, 0.0)
        self.assertEqual(ymax, self.rtree.treenode.height)

    def test_extents_generic(self):
        """ToyTreeMark extents return x and y always. This works b/c
        we always care about both. Need to check, this may be different
        than what toyplot does for most Marks. Adding a test here to
        catch in case we ever change it."""
        c, a, m = self.rtree.draw(tip_labels=False, edge_widths=2)
        coordsx, extentsx = m.extents('x')
        coordsy, extentsy = m.extents('y')        
        self.assertIsNone(assert_allclose(coordsx, coordsy))
        self.assertIsNone(assert_allclose(extentsx, extentsy))        

    def test_extents_edge_widths(self):
        """Default extents are 2 * edge_width in every direction."""
        c, a, m = self.rtree.draw(tip_labels=False, edge_widths=2)
        coords, extents = m.extents('x')
        for direction in extents:
            self.assertTrue(np.allclose(np.abs(direction), 1.0))

    def test_extents_tip_labels(self):
        """Extents returns the coordinates of Nodes and the size of
        their markers/text as the extents each as 
        [min-x, max-x, min-y, max-y]; remember that larger
        y-values are down on the canvas.
        """
        # draw with uniform 1 character tips
        _, _, m1 = self.rtree.draw(tip_labels=["A"] * self.rtree.ntips)        
        _, ext1 = m1.extents('x')

        # draw with uniform 2 character tips
        _, _, m2 = self.rtree.draw(tip_labels=["AA"] * self.rtree.ntips)        
        _, ext2 = m2.extents('x')

        # draw with uniform 2 character tips of larger font size
        _, _, m3 = self.rtree.draw(tip_labels=["AA"] * self.rtree.ntips, tip_labels_style={"font-size": 18})
        _, ext3 = m3.extents('x')

        # extents should increase only in max-x of tip Nodes as tip names extend
        ntips = self.rtree.ntips
        self.assertTrue(np.alltrue(ext2[0] == ext1[0]))
        self.assertTrue(np.alltrue(ext2[1][:ntips] > ext1[1][:ntips]))
        self.assertTrue(np.alltrue(ext2[1][ntips:] == ext1[1][ntips:]))
        self.assertTrue(np.alltrue(ext2[2] == ext1[2]))
        self.assertTrue(np.alltrue(ext2[3] == ext1[3]))

        # larger font-size should increase tip Node extents in right, up and down directions
        self.assertTrue(np.alltrue(ext3[0][:ntips] == ext2[0][:ntips]))  # not in left dir
        self.assertTrue(np.alltrue(ext3[1][:ntips] > ext2[1][:ntips]))
        self.assertTrue(np.alltrue(ext3[1][ntips:] == ext2[1][ntips:]))
        self.assertTrue(np.alltrue(ext3[2][:ntips] < ext2[2][:ntips]))   # larger min is more negative
        self.assertTrue(np.alltrue(ext3[3][:ntips] > ext2[3][:ntips]))

    # def test_extents_node_sizes(self):
    #     """TODO: this test will overlap with annotations tests."""

    # def test_domain_shrink(self):
    #     """TODO: Shrink extends the domain?"""



if __name__ == '__main__':

    toytree.set_log_level("CRITICAL")

    #### RUN INDIVIDUAL TESTS #########################################
    load = unittest.TestLoader()
    tests = (
        load.loadTestsFromTestCase(TestDrawArgs),
        load.loadTestsFromTestCase(TestDrawMarkDomainExtent),
    )

    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(tests))
