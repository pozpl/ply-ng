import unittest
from ply_ng import *
import pandas as pd



test_df = pd.DataFrame(
    {'x': [1, 2, 3, 4, 5, 6], 'y': [6, 5, 4, 3, 2, 1], 'z': [7, 6, 5, 4, 3, 2]},
    columns=['x', 'y', 'z'])


test_df2 = pd.DataFrame(
    {'x': [1, 2, 3, 4], 'y': [6, 5, 4, 3], 'q': [7, 6, 5, 4]},
    columns=['x', 'y', 'q'])    

test_df3 = pd.DataFrame(
    {'x': [1, 2, 3], 'v': [7, 6, 5]},
    columns=['x', 'v'])    


class JoinsTest(unittest.TestCase):
        

    def test_ineer_join_by_one_column(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3], 'y': [6, 5, 4], 'z': [7, 6, 5], 'v': [7, 6, 5]},
                columns=['x', 'y', 'z', 'v'])     
        joined = test_df >> inner_join(test_df3, by='x')
        self.assertTrue(joined.equals(df))

    def test_ineer_join_by_one_column_symbolic(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3], 'y': [6, 5, 4], 'z': [7, 6, 5], 'v': [7, 6, 5]},
                columns=['x', 'y', 'z', 'v'])     
        joined = test_df >> inner_join(test_df3, by=X.x)
        self.assertTrue(joined.equals(df))    


    def test_ineer_join_by_two_columns(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3, 4], 'y': [6, 5, 4, 3], 'z': [7, 6, 5, 4], 'q': [7, 6, 5, 4]},
                columns=['x', 'y', 'z', 'q'])     
        joined = test_df >> inner_join(test_df2, by=[('x', 'x'), ('y', 'y')])
        self.assertTrue(joined.equals(df))  

    def test_ineer_join_by_two_columns_symb(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3, 4], 'y': [6, 5, 4, 3], 'z': [7, 6, 5, 4], 'q': [7, 6, 5, 4]},
                columns=['x', 'y', 'z', 'q'])     
        joined = test_df >> inner_join(test_df2, by=[(X.x, Y.x), (X.y, Y.y)])
        self.assertTrue(joined.equals(df))  


    def test_ineer_join_by_two_columns_same_col_name(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3, 4], 'y': [6, 5, 4, 3], 'z': [7, 6, 5, 4], 'q': [7, 6, 5, 4]},
                columns=['x', 'y', 'z', 'q'])     
        joined = test_df >> inner_join(test_df2, by=['x', 'y'])
        self.assertTrue(joined.equals(df))        
    
    def test_ineer_join_with_suffix(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3, 4], 'y_x': [6, 5, 4, 3], 'z': [7, 6, 5, 4], 'y_y': [6, 5, 4, 3], 'q': [7, 6, 5, 4]},
                columns=['x', 'y_x', 'z', 'y_y', 'q'])     
        joined = test_df >> inner_join(test_df2, by=['x'])
        self.assertTrue(joined.equals(df)) 

    def test_ineer_join_with_custom_suffix(self):
        df = pd.DataFrame(
            {'x': [1, 2, 3, 4], 'y_one': [6, 5, 4, 3], 'z': [7, 6, 5, 4], 'y_two': [6, 5, 4, 3], 'q': [7, 6, 5, 4]},
                columns=['x', 'y_one', 'z', 'y_two', 'q'])     
        joined = test_df >> inner_join(test_df2, by=['x'], suffixes=('_one', '_two'))
        self.assertTrue(joined.equals(df))            


    def test_left_join(self):
        exp_df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5, 6], 
            'y': [6, 5, 4, 3, 2, 1], 
            'z': [7, 6, 5, 4, 3, 2],
            'v': [7, 6, 5, np.nan, np.nan, np.nan]
        })

        joined = test_df >> left_join(test_df3, by='x')
        self.assertTrue(joined.equals(exp_df))


    def test_right_join(self):
        exp_df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5, 6], 
            'v': [7, 6, 5, np.nan, np.nan, np.nan],
            'y': [6, 5, 4, 3, 2, 1], 
            'z': [7, 6, 5, 4, 3, 2]
        })

        joined = test_df3 >> right_join(test_df, by='x')
        self.assertTrue(joined.equals(exp_df))   
    

if __name__ == '__main__':
    unittest.main()    