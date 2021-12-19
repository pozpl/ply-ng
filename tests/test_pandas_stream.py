import unittest
from unittest.mock import Mock

import pandas as pd

from ply_ng.pandas_stream import inject_ply
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal
from ply_ng.symbolic_eval import X

inject_ply(pd)


def assert_frame_equiv(df1, df2, **kwargs):
    """ 
    Assert that two dataframes are equal
    """
    return assert_frame_equal(
        df1[sorted(df1.columns)],
        df2[sorted(df2.columns)],
        check_names=True, **kwargs)


test_df = pd.DataFrame(
    {'x': [1, 2, 3, 4], 'y': [4, 3, 2, 1]},
    columns=['x', 'y'])
test_series = pd.Series([1, 2, 3, 4])

test_dfsq = pd.DataFrame(
    {'x': [-2, -1, 0, 1, 2], 'xsq': [4, 1, 0, 1, 4]},
    columns=['x', 'xsq'])

class PlyFIlterTest(unittest.TestCase):

    def test_no_conditions(self):
        assert_frame_equal(test_df.ply_filter(), test_df)

    def test_single_condition(self):
        expected = pd.DataFrame(
            {'x': [3, 4], 'y': [2, 1]},
            index=[2, 3],
            columns=['x', 'y'])

        assert_frame_equal(test_df.ply_filter(test_df.x > 2.5), expected)
        assert_frame_equal(test_df.ply_filter(lambda df: df.x > 2.5), expected)
        assert_frame_equal(test_df.ply_filter(X.x > 2.5), expected)

    def test_multiple_conditions(self):
        expected = pd.DataFrame(
            {'x': [2, 3], 'y': [3, 2]},
            index=[1, 2],
            columns=['x', 'y'])

        lo_df = test_df.x > 1.5
        hi_df = test_df.x < 3.5
        lo_func = lambda df: df.x > 1.5
        hi_func = lambda df: df.x < 3.5
        lo_sym = X.x > 1.5
        hi_sym = X.x < 3.5

        for lo in [lo_df, lo_func, lo_sym]:
            for hi in [hi_df, hi_func, hi_sym]:
                assert_frame_equal(test_df.ply_filter(lo, hi), expected)    

class PlyFilterForSeriesTest(unittest.TestCase):

    def test_no_conditions(self):
        assert_series_equal(test_series.ply_filter(), test_series)

    def test_single_condition(self):
        expected = pd.Series([3, 4], index=[2, 3])

        assert_series_equal(test_series.ply_filter(test_series > 2.5), expected)
        assert_series_equal(test_series.ply_filter(lambda s: s > 2.5), expected)
        assert_series_equal(test_series.ply_filter(X > 2.5), expected)

    def test_multiple_conditions(self):
        expected = pd.Series([2, 3], index=[1, 2])

        assert_series_equal(
            test_series.ply_filter(test_series < 3.5, test_series > 1.5), expected)
        assert_series_equal(
            test_series.ply_filter(test_series < 3.5, lambda s: s > 1.5), expected)
        assert_series_equal(
            test_series.ply_filter(test_series < 3.5, X > 1.5), expected)
        assert_series_equal(
            test_series.ply_filter(lambda s: s < 3.5, lambda s: s > 1.5), expected)
        assert_series_equal(
            test_series.ply_filter(lambda s: s < 3.5, X > 1.5), expected)
        assert_series_equal(
            test_series.ply_filter(X < 3.5, X > 1.5), expected)                


class PlySelectTest(unittest.TestCase):

    def test_bad_arguments(self):
        # Nonexistent column, include or exclude
        with self.assertRaises(ValueError):
            test_df.ply_select('z')
        with self.assertRaises(ValueError):
            test_df.ply_select('-z')

        # Exclude without asterisk
        with self.assertRaises(ValueError):
            test_df.ply_select('-x')

        # Include with asterisk
        with self.assertRaises(ValueError):
            test_df.ply_select('*', 'x')

    def test_noops(self):
        assert_frame_equal(test_df.ply_select('*'), test_df)
        assert_frame_equal(test_df.ply_select('x', 'y'), test_df)
    

    def test_reorder(self):
        reordered = test_df.ply_select('y', 'x')
        assert_frame_equiv(reordered, test_df[['y', 'x']])
        self.assertEqual(list(reordered.columns), ['y', 'x'])

    def test_subset_via_includes(self):
        assert_frame_equal(test_df.ply_select('x'), test_df[['x']])
        assert_frame_equal(test_df.ply_select('y'), test_df[['y']])

    def test_subset_via_excludes(self):
        assert_frame_equal(test_df.ply_select('*', '-y'), test_df[['x']])
        assert_frame_equal(test_df.ply_select('*', '-x'), test_df[['y']])

    def test_empty(self):
        assert_frame_equal(test_df.ply_select(), test_df[[]])
        assert_frame_equal(test_df.ply_select('*', '-x', '-y'), test_df[[]])

class PlyMutateTest(unittest.TestCase):

    def test_self_assignment(self):
        assert_frame_equiv(test_df.ply_mutate(x=X.x, y=X.y), test_df)

    def test_ways_of_providing_new_columns(self):
        # Value
        assert_frame_equiv(test_df.ply_mutate(new=5),  pd.DataFrame({
            'x': test_df['x'],
            'y': test_df['y'],
            'new': [5, 5, 5, 5], 
            }))

        # Dataframe-like
        assert_frame_equiv(
            test_df.ply_mutate(new=[5, 6, 7, 8]),
            pd.DataFrame({
                'x': test_df['x'],
                'y': test_df['y'],
                'new': [5, 6, 7, 8]}))

        # Function
        assert_frame_equiv(
            test_df.ply_mutate(new=lambda df: df.x),
            pd.DataFrame({
                'x': test_df['x'],
                'y': test_df['y'],
                'new': [1, 2, 3, 4]}))

        # Symbolic expression
        assert_frame_equiv(
            test_df.ply_mutate(new=X.x),
            pd.DataFrame({
                'x': test_df['x'],
                'y': test_df['y'],
                'new': [1, 2, 3, 4]}))

    def test_old_and_new_together(self):
        assert_frame_equiv(
            test_df.ply_mutate(total=X.x + X.y),
            pd.DataFrame(
                {
                'x': test_df['x'],
                'y': test_df['y'],
                'total': [5, 5, 5, 5],
                }))

    def test_kolumns_override_eachother(self):
        assert_frame_equiv(
            test_df.ply_mutate(y=X.x),
            pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]}))

    def test_new_index(self):
        assert_frame_equiv(
            test_df.ply_mutate(index=X.y),
            pd.DataFrame(
                {'x': [1, 2, 3, 4],
                 'y': [4,3,2,1]},
                index=pd.Index([4, 3, 2, 1], name='y')))


class PlySelectForGroupsTest(unittest.TestCase):

    def test_simple(self):
        grp = test_dfsq.groupby('xsq')
        assert_frame_equal(
            grp.ply_mutate(count=X.x.count()),
            pd.DataFrame(
                {'count': [1, 2, 2]},
                index=pd.Index([0, 1, 4], name='xsq')))


if __name__ == '__main__':
    unittest.main()