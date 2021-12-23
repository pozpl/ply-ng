import unittest
from ply_ng.pandas_pipe import *
import pandas as pd

from ply_ng.pandas_stream import inject_ply
from ply_ng.select import select
from ply_ng.subset import head
from ply_ng.symbolic_eval import X, to_callable

inject_ply(pd)



test_df = pd.DataFrame(
    {'x': [1, 2, 3, 4, 5, 6], 'y': [6, 5, 4, 3, 2, 1]},
    columns=['x', 'y'])

class SelectTest(unittest.TestCase):

    def test_select(self):
        df = test_df[['x','y']]
        self.assertTrue(df.equals(test_df >> select('x','y')))
        self.assertTrue(df.equals(test_df >> select(X.x,X.y)))

        #assert df.equals(test_df >> select(0, 1, 6))
        #assert df.equals(test_df >> select(0, 1, 'price'))
        #assert df.equals(test_df >> select([0, X.cut], X.price))
        #assert df.equals(test_df >> select(X.carat, X['cut'], X.price))
        #assert df.equals(test_df >> select(X[['carat','cut','price']]))
        #assert df.equals(test_df >> select(X[['carat','cut']], X.price))
        #assert df.equals(test_df >> select(X.iloc[:,[0,1,6]]))
        #assert df.equals(test_df >> select([X.loc[:, ['carat','cut','price']]]))


    # def test_select_inversion():
    #     df = test_df.iloc[:, 3:]
    #     d = test_df >> select(~X.carat, ~X.cut, ~X.color)
    #     print(df.head())
    #     print(d.head())
    #     assert df.equals(d)
