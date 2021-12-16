import unittest
from unittest.mock import Mock

from ply_ng.symbolic_eval import Call, GetAttr, Symbol, eval_if_symbolic, sym_call, to_callable

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

    def test_eval_non_simb_fun(self):
        func = Mock(return_value="return_value")
        del func._eval #make sure it does not have this indicative property
        call = Call(func, ('arg1', 'arg2'), {'kwarg1': 'kwarg1-val'})
        self.assertFalse(func.called) #function was not called eagerly

        result = call._eval({'smbl': func})

        self.assertEqual('return_value', result)    

    def test_eval_symbolic_arg(self):
        func = Mock(return_value='return value')
        del func._eval  #make sure it does not have this indicative property

        expr = Call(func, (Symbol('smbl'), 'arg2'), {'kwarg_name': 'kwarg value'})

        result = expr._eval({'smbl': 'arg1-value'})

        func.assert_called_once_with('arg1-value', 'arg2', kwarg_name='kwarg value')
        self.assertEqual(result, 'return value')


    def test_eval_with_symbolic_kwarg(self):
        func = Mock(return_value='return value')
        del func._eval   #make sure it does not have this indicative property

        expr = Call(func, ('arg1', 'arg2'), {'kwarg_name': Symbol('smbl')})

        result = expr._eval({'smbl': 'kwarg value'})

        func.assert_called_once_with('arg1', 'arg2', kwarg_name='kwarg value')
        self.assertEqual(result, 'return value')

    def test_repr(self):
        # One arg
        self.assertEqual(repr(Call('func', ('arg1',), {'kwarg_name': 'kwarg value'})), "'func'(*('arg1',), **{'kwarg_name': 'kwarg value'})")

        # Two args
        self.assertEqual(repr(Call('func', ('arg1', 'arg2'), {'kwarg_name': 'kwarg value'})),
            "'func'(*('arg1', 'arg2'), **{'kwarg_name': 'kwarg value'})")    

class ExpressionTest(unittest.TestCase):

    # These test whether operations on symbolic expressions correctly construct
    # compound symbolic expressions:

    def test_getattr(self):
        expr = Symbol('some_symbol').some_attr #overriden getattr should construct GetAttr obj here with Symbol as arg
        self.assertEqual(repr(expr), "getattr(Symbol('some_symbol'), 'some_attr')")

    def test_call(self):
        expr = Symbol('some_symbol')('arg1', 'arg2', kwarg_name='kwarg value') #overriden call should construct lazy Call structure here
        self.assertEqual(repr(expr), "Symbol('some_symbol')(*('arg1', 'arg2'), **{'kwarg_name': 'kwarg value'})")

    def test_ops(self):
        expr = Symbol('some_symbol') + 1 # Overriden magic methods construct Call From GetAttr
        self.assertEqual(repr(expr), "getattr(Symbol('some_symbol'), '__add__')(*(1,), **{})")

        expr = 1 + Symbol('some_symbol')
        self.assertEqual(repr(expr), "getattr(Symbol('some_symbol'), '__radd__')(*(1,), **{})")

        expr = Symbol('some_symbol')['key'] 
        self.assertEqual( repr(expr), "getattr(Symbol('some_symbol'), '__getitem__')(*('key',), **{})")            


class FunctionsTest(unittest.TestCase):

    def test_eval_if_symbolic(self):
        self.assertEqual('nonsymbolic', eval_if_symbolic( 'nonsymbolic', {'some_symbol': 'symbol_value'}))
        self.assertEqual('symbol_value', eval_if_symbolic(Symbol('some_symbol'),{'some_symbol': 'symbol_value'}))

    def test_to_callable_from_nonsymbolic_noncallable(self):
        test_callable = to_callable('nonsymbolic')
        self.assertEqual('nonsymbolic', test_callable('arg1', 'arg2', kwarg_name='kwarg value'))

    def test_to_callable_from_nonsymbolic_callable(self):
        func = Mock(return_value='return value')
        del func._eval  # So it doesn't pretend to be symbolic

        test_callable = to_callable(func)

        # Ensure running to_callable does not call the function
        self.assertFalse(func.called)

        result = test_callable('arg1', 'arg2', kwarg_name='kwarg value')

        func.assert_called_once_with('arg1', 'arg2', kwarg_name='kwarg value')
        self.assertEqual(result, 'return value')

    def test_to_callable_from_symbolic(self):
        mock_expr = Mock()
        mock_expr._eval.return_value = 'eval return value'

        test_callable = to_callable(mock_expr)

        # Ensure running to_callable does not evaluate the expression
        self.assertFalse(mock_expr._eval.called)

        result = test_callable('arg1', 'arg2', kwarg_name='kwarg value')

        mock_expr._eval.assert_called_once_with(
            {0: 'arg1', 1: 'arg2', 'kwarg_name': 'kwarg value'})
        self.assertEqual(result, 'eval return value')

    def test_sym_call(self):
        expr = sym_call(
            'func', Symbol('some_symbol'), 'arg1', 'arg2',
            kwarg_name='kwarg value')
        self.assertEqual(
            repr(expr),
            "'func'(*(Symbol('some_symbol'), 'arg1', 'arg2'), " +
            "**{'kwarg_name': 'kwarg value'})")


class IntegrationTest(unittest.TestCase):

    def test_pythagoras(self):
        from math import sqrt

        X = Symbol('X')
        Y = Symbol('Y')

        #X ** 2 + Y ** 2 - because of overrriden operations this is symbol
        #this opeartion should allow sqrt to operate on symbols
        expr = sym_call(sqrt, X ** 2 + Y ** 2)
        #return callable (basically a function) that takes arguments as context for symbilic calculations
        func = to_callable(expr)

        self.assertEqual(func(X=3, Y=4), 5)

if __name__ == '__main__':
    unittest.main()