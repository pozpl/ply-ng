from ply_ng.pandas_pipe import pipe
from ply_ng.symbolic_eval import *

def _get_join_parameters(join_kw_args):
    by = join_kw_args.get('by', None)
    suffixes = join_kw_args.get('suffixes', ('_x', '_y'))
    if isinstance(by, tuple): # by = ('x', 'abc')
        left_on, right_on = by
    elif isinstance(by, list): # either by = ['a', 'b', 'c'] or by = [('a', 'x1'), ('b', 'x2'), ('c', 'x3')]
        by = [x if isinstance(x, tuple) or isinstance(x, list) else (x, x) for x in by]
        left_on, right_on = (list(x) for x in zip(*by))
    else:
        left_on, right_on = by, by
    return left_on, right_on, suffixes

@pipe
@symbolic_pipe_evaluation(eval_as_label=True)
def inner_join(df1, df2, **kwargs):
    """
    Example:
    a >> inner_join(b, by='x')
    a >> inner_join(b, by=['x', 'y', 'z'])
    a >> inner_join(b, by=[('x', 'x_from_b'), ('y', 'y_from_b')])
    """
    left_on, right_on, suffixes = _get_join_parameters(kwargs)
    joined = df1.merge(df2, how='inner', left_on=left_on,
                      right_on=right_on, suffixes=suffixes)
    return joined    

@pipe
@symbolic_pipe_evaluation(eval_as_label=True)
def left_join(df1, df2, **kwargs):
    """
    Example:
    a >> left_join(b, by='x')
    a >> left_join(b, by=['x', 'y', 'z'])
    a >> left_join(b, by=[('x', 'x_from_b'), ('y', 'y_from_b')])
    """
    left_on, right_on, suffixes = _get_join_parameters(kwargs)
    joined = df1.merge(df2, how='left', left_on=left_on,
                      right_on=right_on, suffixes=suffixes)
    return joined        

@pipe
@symbolic_pipe_evaluation(eval_as_label=True)
def right_join(df1, df2, **kwargs):
    """
    Example:
    a >> right_join(b, by='x')
    a >> right_join(b, by=['x', 'y', 'z'])
    a >> right_join(b, by=[('x', 'x_from_b'), ('y', 'y_from_b')])
    """
    left_on, right_on, suffixes = _get_join_parameters(kwargs)
    joined = df1.merge(df2, how='right', left_on=left_on,
                      right_on=right_on, suffixes=suffixes)
    return joined            