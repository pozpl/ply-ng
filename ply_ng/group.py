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


class GroupedEvaluationService(object):

    def __init__(self, function):
        """
        usually we pass function here that evaluates symbolic expressions
        """
        self.function = function
        self.__doc__ = function.__doc__

    def _apply(self, df: pd.DataFrame, *args, **kwargs):
        grouped = df.groupby(df._grouped_by) # grouped_by property is set in the group_by method

        df_grouped = grouped.apply(self.function, *args, **kwargs)
        # Save all the metadata attributes back into the new data frame
        for field in df._metadata:
            setattr(df_grouped, field, getattr(df, field))
        
        for name in df_grouped.index.names[:-1]:
            if name in df_grouped:
                df_grouped.reset_index(level=0, drop=True, inplace=True)
            else:
                df_grouped.reset_index(level=0, inplace=True)

        if (df_grouped.index == 0).all():
            df_grouped.reset_index(drop=True, inplace=True)

        return df_grouped

    def __call__(self, *args, **kwargs):
        grouped_by = getattr(args[0], '_grouped_by', None) # check if we have grouped property on this dataframe
        if (grouped_by is None) or not all([g in args[0].columns for g in grouped_by]):
            return self.function(*args, **kwargs) #if not just apply the fynction to it's argument (it would be symbolic evaluation)
        else:
            applied = self._apply(args[0], *args[1:], **kwargs)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                applied._grouped_by = grouped_by
            
            return applied    


def gr_pipe(func):
    """
    Function to pipe apply symbolic avaluation to grouped dataframe.
    """
    return pipe(
        GroupedEvaluationService(
            symbolic_pipe_evaluation(func)
        )
    )