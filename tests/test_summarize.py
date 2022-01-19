import unittest
import pandas as pd

from ply_ng import *


class SummarizingTest(unittest.TestCase):

    def setUp(self):
        self.test_df = pd.DataFrame({
            'x': [1, 1, 2, 2], 
            'y': [1, 1, 2, 4],
            'z': [7, 6, 5, 4]
        })


    def test_summarize_grouped(self):
        s_df = pd.DataFrame({
            'x': [1, 2],
            'y_mean': [1.0, 3.0],
            'z_max': [7, 5]
        })

        result = (self.test_df >> 
                group_by('x') >> 
                summarize(y_mean = X.y.mean(),
                          z_max = X.z.max())
                )
          
            
        self.assertTrue(s_df.equals(result))

    def test_summarize_ungrouped(self):
        s_df = pd.DataFrame({
            'x_min': [1],
            'y_mean': [2.0],
            'z_max': [7]
        })

        result = (self.test_df >> 
                    summarize(x_min = X.x.min(),
                            y_mean = X.y.mean(),
                            z_max = X.z.max())
                )

        print(result)                
            
        self.assertTrue(s_df.equals(result))    
      



if __name__ == '__main__':
    unittest.main()