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

@pipe
@to_callable
def blank_function(df):
    return df

class PipeTest(unittest.TestCase):
        

    def test_pipe(self):
        d = test_df >> blank_function()
        self.assertTrue(test_df.equals(d))
        d = test_df >> blank_function() >> blank_function()
        self.assertTrue(test_df.equals(d))

    def test_inplace_pipe(self):
        df = test_df[['x','y']].head(5)
        d = test_df.copy()
        d >>= select(X.x, X.y) >> head(5)
        print(df)
        print(d)
        self.assertTrue(df.equals(d))

if __name__ == '__main__':
    unittest.main()    