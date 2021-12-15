import unittest
from unittest.mock import Mock

from ply_ng.symbolic_eval import Call, GetAttr, Symbol

class SymbolTest(unittest.TestCase):

    def test_eval(self):
        self.assertEqual(Symbol("smbl")._eval({'smbl': 'symbol_val'}), 'symbol_val')
        self.assertEqual(Symbol("smbl")._eval({'smbl': 'symbol_val', 'other_symb': 'yet another val'}), 'symbol_val')

    def test_repr(self):
        self.assertEqual(repr(Symbol('smbl')), "Symbol('smbl')")    

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

    def test_eval_with_symbolic_object(self):
        some_obj = Mock()
        del some_obj._eval
        some_obj.some_attr = "attribute value"

        expr = GetAttr(Symbol('some_symbo'), 'some_attr')

        self.assertEqual(expr._eval({'some_symbo': some_obj}), 'attribute value')

    def test_repr(self):

        self.assertEqual(repr(GetAttr("some_object", "attr_name")), "getattr('some_object', 'attr_name')")    



class CallTest(unittest.TestCase):

    def test_eval_symbolic_fun(self):
        func = lambda x,y,kwarg1: 'return_value'
        result = Call(Symbol('smbl'), ('arg1', 'arg2'), {'kwarg1': 'kwarg1-val'})._eval({'smbl': func})
        self.assertEqual('return_value', result)

if __name__ == '__main__':
    unittest.main()