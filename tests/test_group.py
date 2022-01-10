import unittest
import pandas as pd

from ply_ng import *


class GroupingTest(unittest.TestCase):


    def setUp(self):
        self.test_df = pd.DataFrame({
            'x': [1, 2, 3], 
            'y': [6, 5, 4],
            'z': [7, 6, 5]
        })



    def test_grouping(self):
        d = self.test_df >> group_by('x')
        self.assertTrue(hasattr(d, '_grouped_by'))
        self.assertTrue(d._grouped_by == ['x',])

    def test_grouping_symb(self):
        d = self.test_df >> group_by(X.x)
        self.assertTrue(hasattr(d, '_grouped_by'))
        self.assertTrue(d._grouped_by == ['x',])    

    def test_ungrouping_symb(self):
        d = self.test_df >> group_by(X.x)
        self.assertTrue(hasattr(d, '_grouped_by'))
        self.assertTrue(d._grouped_by == ['x',])
        d_ung = d >> ungroup()
        self.assertTrue(d_ung._grouped_by == None)
        



if __name__ == '__main__':
    unittest.main()