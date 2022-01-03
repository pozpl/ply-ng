from ply_ng.pandas_pipe import pipe
from ply_ng.symbolic_eval import *

def _get_join_parameters(join_kw_args):
    by = join_kw_args.get('by', None)
    suffixes = join_kw_args.get('suffixes', ('_x', '_y'))
    if isinstance(by, tuple): # by = ('x', 'abc')
        left_on, right_on = by
    elif isinstance(by, list): # either by = ['a', 'b', 'c'] or by = [('a', 'x1'), ('b', 'x2'), ('c', 'x3')]
        by = [x if isinstance(x, tuple) else (x, x) for x in by]
        left_on, right_on = (list(x) for x in zip(*by))
    else:
        left_on, right_on = by, by
    return left_on, right_on, suffixes

@pipe
def inner_join(df1, df2, **kwargs):
    left_on, right_on, suffixes = _get_join_parameters(kwargs)
    joined = df1.merge(df2, how='inner', left_on=left_on,
                      right_on=right_on, suffixes=suffixes)
    return joined    