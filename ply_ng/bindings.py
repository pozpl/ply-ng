from ply_ng.pandas_pipe import pipe
from ply_ng.symbolic_eval import *

@pipe
def bind_rows(top_df, bottom_df, join='outer', ignore_index=False):
    """
    Equivalent of `pd.concat` with `axis=0`.
    Args:
        df (pandas.DataFrame): Top DataFrame (passed in via pipe).
        other (pandas.DataFrame): Bottom DataFrame.
    Kwargs:
        join (str): One of `"outer"` or `"inner"`. Outer join will preserve
            columns not present in both DataFrames, whereas inner joining will
            drop them.
        ignore_index (bool): Indicates whether to consider pandas indices as
            part of the concatenation (defaults to `False`).
    """

    df = pd.concat([top_df, bottom_df], join=join, ignore_index=ignore_index, axis=0)
    return df


@pipe
def bind_cols(df, other, join='outer', ignore_index=False):
    """
    Equivalent to `pd.concat` with `axis=1`.
    Args:
        df (pandas.DataFrame): Left DataFrame (passed in via pipe).
        other (pandas.DataFrame): Right DataFrame.
    Kwargs:
        join (str): One of `"outer"` or `"inner"`. Outer join will preserve
            rows not present in both DataFrames, whereas inner joining will
            drop them.
        ignore_index (bool): Indicates whether to consider pandas indices as
            part of the concatenation (defaults to `False`).
    """

    df = pd.concat([df, other], join=join, ignore_index=ignore_index, axis=1)
    return df