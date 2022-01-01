
from abc import ABC
from functools import wraps
from typing import List, Union

import pandas as pd
import numpy as np

_magic_method_names = [
    '__abs__', '__add__', '__and__', '__cmp__', '__complex__', '__contains__',
    '__delattr__', '__delete__', '__delitem__', '__delslice__', '__div__',
    '__divmod__', '__enter__', '__eq__', '__exit__', '__float__',
    '__floordiv__', '__ge__', '__get__', '__getitem__', '__getslice__',
    '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
    '__ifloordiv__', '__ilshift__', '__imod__', '__imul__', '__index__',
    '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', '__isub__',
    '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', '__long__',
    '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', '__neg__',
    '__nonzero__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
    '__rand__', '__rcmp__', '__rdiv__', '__rdivmod__', '__repr__',
    '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__',
    '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
    '__rtruediv__', '__rxor__', '__set__', '__setitem__', '__setslice__',
    '__str__', '__sub__', '__truediv__', '__unicode__', '__xor__',
]

# Not included: [
#   '__call__', '__coerce__', '__del__', '__dict__', '__getattr__',
#   '__getattribute__', '__init__', '__new__', '__setattr__'
# ]


def add_operator_hooks(cls):

  def get_hook(name):
    def op_hook(self, *args, **kwargs):
      return Call(GetAttr(self, name), args, kwargs)
    return op_hook

  for name in _magic_method_names:
    setattr(cls, name, get_hook(name))  
  
  return cls



@add_operator_hooks
class Expression(ABC):
    """
    Base class for lazy symblic expressions
    """

    def __init__(self, inverted: bool = False) -> None:
        self.inverted = inverted
        super().__init__()

    def _eval(self, context, **options):
        """Evaluate a symbolic expression.
        Args:
            context: The context object for evaluation. Currently, this is a
                dictionary mapping symbol names to values,
            `**options`: Options for evaluation. Currently, the only option is
                `log`, which results in some debug output during evaluation if
                it is set to `True`.
        Returns:
            anything
        """
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __getattr__(self, name):
        """Construct a symbolic representation of `getattr(self, name)`."""
        return GetAttr(self, name)

    def __call__(self, *args, **kwargs):
        """Construct a symbolic representation of `self(*args, **kwargs)`."""
        return Call(self, args=args, kwargs=kwargs)


class Symbol(Expression):
    """`Symbol(name)` is an atomic symbolic expression, labelled with an
    arbitrary `name`.
    Something in evaluation context denoted with a name given to a symbol (through constructor)
    """

    def __init__(self, name, inverted: bool = False):
        super().__init__(inverted)
        self._name = name

    def _eval(self, context, **options):
        if options.get('log'):
            print('Symbol._eval', repr(self))
        result = context[self._name]
        if options.get('log'):
            print('Returning', repr(self), '=>', repr(result))
        return result

    def __invert__(self):
        return Symbol(self._name, inverted=not self.inverted)        

    def __repr__(self):
        return 'Symbol(%s)' % repr(self._name)


class GetAttr(Expression):
    """`GetAttr(obj, name)` is a symbolic expression representing the result of
    `getattr(obj, name)`. (`obj` and `name` can themselves be symbolic.)"""

    def __init__(self, obj, name, inverted=False):
        super().__init__(inverted)
        self._obj = obj
        self._name = name
        self._inverted = inverted

    def _eval(self, context, **options):
        if options.get('log'):
            print('GetAttr._eval', repr(self))
             
        evaled_obj = eval_if_symbolic(self._obj, context, **options)
        result = getattr(evaled_obj, self._name)
        if options.get('log'):
            print('Returning', repr(self), '=>', repr(result))
        return result

    def __invert__(self):
        GetAttr(self._obj, self._name, not self._inverted)

    def __repr__(self):
        return 'getattr(%s, %s)' % (repr(self._obj), repr(self._name))
    

class Call(Expression):
    """`Call(func, args, kwargs)` is a symbolic expression representing the
    result of `func(*args, **kwargs)`. (`func`, each member of the `args`
    iterable, and each value in the `kwargs` dictionary can themselves be
    symbolic)."""

    def __init__(self, func, args=[], kwargs={}, inverted = False):
        super().__init__(inverted)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _rec_symb_eval(self, val, context, **options):
        if isinstance(val, (list, tuple)):
            out = [self._rec_symb_eval(val_, context, **options) for val_ in val]
        if isinstance(val, tuple):
            out = tuple(out)
            return out
        else:
            return eval_if_symbolic(val, context, **options)

    def _eval(self, context, **options):
        if options.get('log'):
            print('Call._eval', repr(self))
        evaled_func = eval_if_symbolic(self._func, context, **options)
        evaled_args = [self._rec_symb_eval(v, context, **options) for v in self._args] 
        evaled_kwargs = dict((k, eval_if_symbolic(v, context, **options)) for k, v in self._kwargs.items() )
        result = evaled_func(*evaled_args, **evaled_kwargs)
        if options.get('log'):
            print('Returning', repr(self), '=>', repr(result))
        return result

    def __repr__(self):
        return '{func}(*{args}, **{kwargs})'.format(
            func=repr(self._func),
            args=repr(self._args),
            kwargs=repr(self._kwargs))


def eval_if_symbolic(obj, context, **options):
    """Evaluate an object if it is a symbolic expression, or otherwise just
    returns it back.
    It determines if it's symbolic based on presence of _eval method 
    Args:
        obj: Either a symbolic expression, or anything else (in which case this
            is a noop).
        context: Passed as an argument to `obj._eval` if `obj` is symbolic.
        `**options`: Passed as arguments to `obj._eval` if `obj` is symbolic.
    Returns:
        anything
    Examples:
        >>> eval_if_symbolic(Symbol('x'), {'x': 10})
        10
        >>> eval_if_symbolic(7, {'x': 10})
        7
    """
    return obj._eval(context, **options) if hasattr(obj, '_eval') else obj


def to_callable(obj):
    """Turn an object into a callable.
    Args:
        obj: This can be
            * **a symbolic expression**, in which case the output callable
              evaluates the expression with symbols taking values from the
              callable's arguments (listed arguments named according to their
              numerical index, keyword arguments named according to their
              string keys),
            * **a callable**, in which case the output callable is just the
              input object, or
            * **anything else**, in which case the output callable is a
              constant function which always returns the input object.
    Returns:
        callable
    Examples:
        >>> to_callable(Symbol(0) + Symbol('x'))(3, x=4)
        7
        >>> to_callable(lambda x: x + 1)(10)
        11
        >>> to_callable(12)(3, x=4)
        12
    """
    if hasattr(obj, '_eval'):
        return lambda *args, **kwargs: obj._eval(dict(enumerate(args), **kwargs))
    elif callable(obj):
        return obj
    else:
        return lambda *args, **kwargs: obj


def sym_call(func, *args, **kwargs):
    """Construct a symbolic representation of `func(*args, **kwargs)`.
    This is necessary because `func(symbolic)` will not (ordinarily) know to
    construct a symbolic expression when it receives the symbolic
    expression `symbolic` as a parameter (if `func` is not itself symbolic).
    So instead, we write `sym_call(func, symbolic)`.
    Tip: If the main argument of the function is a (symbolic) DataFrame, then
    pandas' `pipe` method takes care of this problem without `sym_call`. For
    instance, while `np.sqrt(X)` won't work, `X.pipe(np.sqrt)` will.
    Args:
        func: Function to call on evaluation (can be symbolic).
        `*args`: Arguments to provide to `func` on evaluation (can be symbolic).
        `**kwargs`: Keyword arguments to provide to `func` on evaluation (can be
            symbolic).
    Returns:
        `ply.symbolic.Expression`
    Example:
        >>> sym_call(math.sqrt, Symbol('x'))._eval({'x': 16})
        4
    """

    return Call(func, args=args, kwargs=kwargs)        

EvalMode = Union[List, None, bool]

class PipeEvaluationEngine(object):

    def __init__(self, function, eval_symbols=True, eval_as_label=[],
                 eval_as_selector=[]):
        super(PipeEvaluationEngine, self).__init__()
        self.function = function
        self.__doc__ = function.__doc__

        self.eval_symbols = eval_symbols
        self.eval_as_label = eval_as_label
        self.eval_as_selector = eval_as_selector

    def _rec_symb_eval(self, val, context, **options):
        if isinstance(val, (list, tuple)):
            out = [self._rec_symb_eval(val_, context, **options) for val_ in val]
        if isinstance(val, tuple):
            out = tuple(out)
            return out
        else:
            return eval_if_symbolic(val, context, **options)
    
    
    def _evaluate_selector(self, df, arg, context, **options):

        negate = np.array([1 for i in range(df.shape[1])])
        if hasattr(arg, '_eval') or isinstance(arg, Expression):
            if arg.inverted:
                negate = negate * -1
            arg = eval_if_symbolic(arg, context, **options)
        #Get array with elements designating indexes of selected columns
        orig_cols = list(df.columns)
        if isinstance(arg, pd.Series): # covers cases like X.col_name because result will be getter evaluated with context
            arg = [orig_cols.index(arg.name)]
        elif isinstance(arg, pd.Index):
            arg = [orig_cols.index(i) for i in list(arg)]
        elif isinstance(arg, pd.DataFrame):
            arg = [orig_cols.index(i) for i in arg.columns]
        elif isinstance(arg, int):
            arg = [arg]
        elif isinstance(arg, str):
            if arg[0] == '-' and arg[1:] in orig_cols:
                col_idx = orig_cols.index(arg[1:])
                negate[col_idx] = -1
                arg = [col_idx]
            elif arg == "*":
                arg = [i for i in range(df.shape[1])]
            else:     
                arg = [orig_cols.index(arg)]
        elif isinstance(arg, (list, tuple)):
            pars_arg = []
            for s in arg:
                if isinstance(s, str):
                    if s[0] == '-' and s[1:] in orig_cols:
                        col_idx = orig_cols.index(arg[1:])
                        negate[col_idx] = -1
                        s_idx = orig_cols.index(col_idx)
                    else:     
                        s_idx = orig_cols.index(arg)
                    pars_arg.append(s_idx)    
                else: #should happen only if array of integers passed
                    pars_arg.append(s)
            arg = pars_arg

        selected_columns_vector = np.zeros(df.shape[1]) #fill array wit hdimention of # of columns with 0
        col_idx = np.array(arg) # create np array out of array we got in argument 

        if len(col_idx) > 0:
            selected_columns_vector[col_idx] = 1
        selected_columns_vector = selected_columns_vector * negate    
        return selected_columns_vector #1d np array with dimenstion as # of columns with 0, 1, -1
            


    def _arg_eval(self, df, args, **options):
        context = {0: df}
        eval_as_symbols = self._get_argument_eval_mode(self.eval_symbols, args)
        evas_as_selector = self._get_argument_eval_mode(self.eval_as_selector, args)
        
        return [    
                    self._evaluate_selector(df, v, context, **options) if i in evas_as_selector
                    else self._rec_symb_eval(v, context, **options) if i in eval_as_symbols
                    else v                    
                    for i, v in enumerate(args)
               ]


    def _kwarg_eval(self, df, kwargs, **options):
        context = {0: df}
        return {
            k: (self._rec_symb_eval(v, context, **options))
            for k, v in kwargs.items()
        }


    def _get_argument_eval_mode(self, eval_mode: EvalMode, args):
        if eval_mode == True or ('*' in eval_mode): #evaluation mode can be boolean
            return [i for i in range(len(args))]
        elif eval_mode in [False, None]:
            return []
        return eval_mode        

    def __call__(self, *args, **kwargs):
        df = args[0]

        args = self._arg_eval(df, args[1:])
        kwargs = self._kwarg_eval(df, kwargs)

        return self.function(df, *args, **kwargs)


def symbolic_pipe_evaluation(function=None, eval_symbols=True, eval_as_label=[],
                             eval_as_selector=[]):
    if function:
        return PipeEvaluationEngine(function)
    else:
        @wraps(function)
        def wrapper(function):
            return PipeEvaluationEngine(function, eval_symbols=eval_symbols,
                                      eval_as_label=eval_as_label,
                                      eval_as_selector=eval_as_selector)

        return wrapper        

def flatten(l):
    for el in l:
        if isinstance(el, (tuple, list)):
            yield from flatten(el)
        else:
            yield el

#Assigning X as a receiver of the first argument in the chain operations it would be root object
X = Symbol(0)