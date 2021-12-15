
from abc import ABC

class Expression(ABC):
    """
    Base class for lazy symblic expressions
    """

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


class GetAttr(Expression):
    """`GetAttr(obj, name)` is a symbolic expression representing the result of
    `getattr(obj, name)`. (`obj` and `name` can themselves be symbolic.)"""

    def __init__(self, obj, name):
        self._obj = obj
        self._name = name

    def _eval(self, context, **options):
        if options.get('log'):
            print('GetAttr._eval', repr(self))
        evaled_obj = eval_if_symbolic(self._obj, context, **options)
        result = getattr(evaled_obj, self._name)
        if options.get('log'):
            print('Returning', repr(self), '=>', repr(result))
        return result

    def __repr__(self):
        return 'getattr(%s, %s)' % (repr(self._obj), repr(self._name))

class Call(Expression):
    """`Call(func, args, kwargs)` is a symbolic expression representing the
    result of `func(*args, **kwargs)`. (`func`, each member of the `args`
    iterable, and each value in the `kwargs` dictionary can themselves be
    symbolic)."""

    def __init__(self, func, args=[], kwargs={}):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def _eval(self, context, **options):
        if options.get('log'):
            print('Call._eval', repr(self))
        evaled_func = eval_if_symbolic(self._func, context, **options)
        evaled_args = [eval_if_symbolic(v, context, **options) for v in self._args]
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

