from ply_ng.symbolic_eval import to_callable
from . pandas_pipe import *


@pipe
@to_callable
# @group_delegation
# @symbolic_evaluation(eval_as_selector=True)
def select(df, *args):
    df.ply_select(*args)