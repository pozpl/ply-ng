import unittest
from unittest.mock import Mock

from ply_ng.symbolic_eval import GetAttr

class GetAttrTest(unittest.TestCase):

    def test_eval_with_nonsymbolic_object(self):
        some_obj = Mock()
        del some_obj._eval
        # Ensure constructing the expression does not access `.some_attr`.
        del some_obj.some_attr

        with self.assertRaises(AttributeError):
            some_obj.some_attr
        expr = GetAttr(some_obj, 'some_attr')

        some_obj.some_attr = 'attribute value'

        self.assertEqual(expr._eval({}), 'attribute value')



if __name__ == '__main__':
    unittest.main()