#!/usr/bin/env python

"""

"""

from toytree.color import Color
import unittest
import toyplot

class TestColorMethods(unittest.TestCase):

    def setUp(self):

        # single colors
        self.css = Color('red')
        self.rgb = Color((1.0, 0.0, 0.0, 1.0))
        self.arr = Color('red')
        self.void = []

        # lists of colors
        self.palette = toyplot.color.brewer.palette("BlueRed")
        self.list_of_css = []
        self.list_of_rgba = []
        self.list_of_arrs = []
        self.list_of_mixed = []

    def test_css_to_css(self):
        self.assertEqual(self.red_css.css, "red")
        self.assertEqual(self.red_arr.css, "red")
        self.assertEqual(self.red_rgb.css, "red")                

    def test_css_to_rgba(self):
        self.assertEqual(self.col_css.css, "red")

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':


# def test_toyplot_array_palette_color():
#     color = toyplot.color.Palette()[0]


# def test_str_css_color():
#     color = "red"


# def test_str_hex_color():
#     color = "#262626"


# def test_rgba_int_tuple_color():
#     color = (33, 33, 33, 0.5)


# def test_rgba_float_tuple_color():    
#     color = (0.33, 0.33, 0.33, 0.5)
