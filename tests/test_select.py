import unittest
import pandas as pd

from ply_ng import *




class SelectTest(unittest.TestCase):

    def setUp(self) -> None:
        test_df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5, 6], 
            'y': [6, 5, 4, 3, 2, 1], 
            'z': [7, 6, 5, 4, 3, 2]
            })


        return super().setUp()

    def test_select(self):
        df = self.test_df[['x','y']]
        df_xz = self.test_df[['x', 'z']]
        df_all = self.test_df[['x', 'y', 'z']]

        self.assertTrue(df_all.equals(self.test_df >> select([X.loc[:, ['x','y','z']]])))

        self.assertTrue(df.equals(self.test_df >> select('x','y')))
        self.assertTrue(df_xz.equals(self.test_df >> select('*', '-y')))
        self.assertTrue(df.equals(self.test_df >> select(X.x,X.y)))
        self.assertTrue(df.equals(self.test_df >> select(0, 1)))
        self.assertTrue(df.equals(self.test_df >> select(0, 'y')))
        #self.assertTrue(df_all.equals(test_df >> select([0, X.y], X.z)))
        self.assertTrue(df_all.equals(self.test_df >> select(X.x, X['y'], X.z)))
        self.assertTrue(df_all.equals(self.test_df >> select(X[['x','y','z']])))
        self.assertTrue(df_all.equals(self.test_df >> select(X[['x','y']], X.z)))
        self.assertTrue(df_all.equals(self.test_df >> select(X.iloc[:,[0,1,2]])))
        self.assertTrue(df_all.equals(self.test_df >> select(X.loc[:, ['x','y','z']])))        
        self.assertTrue(df_all.equals(self.test_df >> select([X.loc[:, ['x','y','z']]])))


    def test_select_inversion(self):
        df = self.test_df.iloc[:, 2:]
        d = self.test_df >> select(~X.x, ~X.y)
        self.assertTrue(df.equals(d))
