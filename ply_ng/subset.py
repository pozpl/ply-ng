from ply_ng.symbolic_eval import to_callable
from .pandas_pipe import *

@pipe
@to_callable
def head(df, n=5):
    df.head(n)


@pipe
@to_callable
def tail(df, n=5):
    df.tail(n)

    