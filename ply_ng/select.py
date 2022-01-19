from ply_ng.group import GroupedEvaluationService
from ply_ng.symbolic_eval import flatten, symbolic_pipe_evaluation, to_callable
from . pandas_pipe import *


def resolve_selection(df, *args, drop=False):
    if len(args) > 0:
        args = [a for a in flatten(args)] # each arg is an array with dim # of df columns
        ordering = []
        column_indices = np.zeros(df.shape[1])
        for selector in args: #args is array args[#of args, # of cols in df]
            visible = np.where(selector != 0)[0] 
            if not drop:
                column_indices[visible] = selector[visible]
            else:
                column_indices[visible] = selector[visible] * -1
            for selection in np.where(selector == 1)[0]:
                if not df.columns[selection] in ordering:
                    ordering.append(df.columns[selection])
    else:
        ordering = list(df.columns)
        column_indices = np.ones(df.shape[1])
    return ordering, column_indices

@pipe
@GroupedEvaluationService
@symbolic_pipe_evaluation(eval_as_selector=True)
def select(df, *args):
    ordering, column_indices = resolve_selection(df, *args)
    if (column_indices == 0).all():
        return df[[]]
    selection = np.where((column_indices == np.max(column_indices)) &
                         (column_indices >= 0))[0]
    df = df.iloc[:, selection]
    if all([col in ordering for col in df.columns]):
        ordering = [c for c in ordering if c in df.columns]
        return df[ordering]
    else:
        return df    



@pipe
@GroupedEvaluationService
@symbolic_pipe_evaluation(eval_as_selector=True)
def drop(df, *args):
    _, column_indices = resolve_selection(df, *args, drop=True)
    if (column_indices == 0).all():
        return df[[]]
    selection = np.where((column_indices == np.max(column_indices)) &
                         (column_indices >= 0))[0]
    return df.iloc[:, selection]