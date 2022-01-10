from ply_ng.pandas_pipe import pipe
from ply_ng.symbolic_eval import *

@pipe
@symbolic_pipe_evaluation(eval_as_label=True)
def group_by(df, *args):
    df._grouped_by = list(args)
    return df


@pipe
def ungroup(df):
    df._grouped_by = None
    return df