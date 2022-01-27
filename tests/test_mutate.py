import unittest
from unittest import result
import pandas as pd

from ply_ng import *


class MutationsTest(unittest.TestCase):

    def setUp(self):
        self.test_df = pd.DataFrame({
            'x': [1, 1, 2, 2], 
            'y': [1, 1, 2, 4],
            'z': [7, 6, 5, 4]
        })


    def test_mutate(self):
        exp_df = pd.DataFrame({
            'x': [1, 1, 2, 2], 
            'y': [1, 1, 2, 4],
            'z': [6, 5, 3, 0],
            'q': [2, 2, 4, 6]
        })

        result = (self.test_df >> 
                mutate(z = X.z - X.y,
                       q = X.x + X.y)
                )
            
        self.assertTrue(exp_df.equals(result))

    def test_mutate_on_group(self):
        s_df = pd.DataFrame({
            'x': [1, 1, 2, 2], 
            'y': [1, 1, 2, 4],
            'z': [7, 6, 5, 4],
            'yt': [2.0,2.0,3.0,5.0]
        })

        result = (self.test_df >> 
                group_by('x') >> 
                mutate(
                    yt = X.y + 1.0
                ) >> ungroup()
        )
    
        self.assertTrue(s_df.equals(result))

    def test_mutate_on_group_using_group_dim(self):
        s_df = pd.DataFrame({
            'x': [1, 1, 2, 2], 
            'y': [1, 1, 2, 4],
            'z': [7, 6, 5, 4],
            'yt': [2,2,2,2]
        })

        result = (self.test_df >> 
                group_by('x') >> 
                mutate(
                    yt = X.shape[0]
                ) >> ungroup()
        )
    
        self.assertTrue(s_df.equals(result))

        