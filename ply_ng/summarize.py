

from ply_ng.group import gr_pipe
import pandas as pd
from ply_ng.pandas_pipe import pipe
from ply_ng.symbolic_eval import *


@gr_pipe
def summarize(df, **kwargs):
    return pd.DataFrame({k: [v] for k, v in kwargs.items()})