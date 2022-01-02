import unittest
from ply_ng.pandas_pipe import *
import pandas as pd

from ply_ng.pandas_stream import inject_ply
from ply_ng.select import select
from ply_ng.subset import head
from ply_ng.symbolic_eval import X, to_callable

inject_ply(pd)



test_df = pd.DataFrame(
    {'x': [1, 2, 3, 4, 5, 6], 'y': [6, 5, 4, 3, 2, 1], 'z': [7, 6, 5, 4, 3, 2]},
    columns=['x', 'y', 'z'])

class SelectTest(unittest.TestCase):

    def test_select(self):
        df = test_df[['x','y']]
        df_xz = test_df[['x', 'z']]
        df_all = test_df[['x', 'y', 'z']]

        self.assertTrue(df_all.equals(test_df >> select([X.loc[:, ['x','y','z']]])))

        self.assertTrue(df.equals(test_df >> select('x','y')))
        self.assertTrue(df_xz.equals(test_df >> select('*', '-y')))
        self.assertTrue(df.equals(test_df >> select(X.x,X.y)))
        self.assertTrue(df.equals(test_df >> select(0, 1)))
        self.assertTrue(df.equals(test_df >> select(0, 'y')))
        #self.assertTrue(df_all.equals(test_df >> select([0, X.y], X.z)))
        self.assertTrue(df_all.equals(test_df >> select(X.x, X['y'], X.z)))
        self.assertTrue(df_all.equals(test_df >> select(X[['x','y','z']])))
        self.assertTrue(df_all.equals(test_df >> select(X[['x','y']], X.z)))
        self.assertTrue(df_all.equals(test_df >> select(X.iloc[:,[0,1,2]])))
        self.assertTrue(df_all.equals(test_df >> select(X.loc[:, ['x','y','z']])))        
        self.assertTrue(df_all.equals(test_df >> select([X.loc[:, ['x','y','z']]])))


    def test_select_inversion(self):
        df = test_df.iloc[:, 2:]
        d = test_df >> select(~X.x, ~X.y)
        self.assertTrue(df.equals(d))
