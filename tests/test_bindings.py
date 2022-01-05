import unittest
from ply_ng import *
import pandas as pd


class BindingsTest(unittest.TestCase):

    def setUp(self):
        self.test_df = pd.DataFrame({
            'x': [1, 2, 3], 
            'y': [6, 5, 4],
            'z': [7, 6, 5]
        })


        self.test_df2 = pd.DataFrame({
            'x': [1, 2, 3, 4], 
            'y': [6, 5, 4, 3], 
            'q': [7, 6, 5, 4]
        })    

        self.test_df3 = pd.DataFrame({
                'x': [1, 2, 3], 
                'v': [7, 6, 5]
        })    
        

    def test_row_bind_default_outer(self):
        df = pd.DataFrame({
                'x': [1, 2, 3, 1, 2, 3], 
                'y': [6.0, 5.0, 4.0, np.NaN, np.NaN, np.NaN], 
                'z': [7.0, 6.0, 5.0, np.NaN, np.NaN, np.NaN], 
                'v': [np.NaN, np.NaN, np.NaN, 7.0, 6.0, 5.0]
            })     
        joined = self.test_df >> bind_rows(self.test_df3)
        self.assertTrue(df.equals(joined.reset_index(drop=True)))

    def test_row_bind_inner(self):
        df = pd.DataFrame({
                'x': [1, 2, 3, 1, 2, 3]
            })     
        joined = self.test_df >> bind_rows(self.test_df3, join='inner')
        self.assertTrue(df.equals(joined.reset_index(drop=True)))

    def test_bind_columns(self):

        df = pd.DataFrame({
            'x1': [1.0, 2.0, 3.0, np.NaN], 
            'y1': [6.0, 5.0, 4.0, np.NaN],
            'p': [7.0, 6.0, 5.0, np.NaN],
            'x': [1, 2, 3, 4], 
            'y': [6, 5, 4, 3], 
            'q': [7, 6, 5, 4]
        })     

        self.test_df.columns = ['x1', 'y1', 'p']

        joined = self.test_df >> bind_cols(self.test_df2)
        print(joined)
        self.assertTrue(df.equals(joined))