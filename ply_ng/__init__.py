from .pandas_pipe import *
from .pandas_stream import *
from .select import *
from .joins import *
from .bindings import *
from .group import *
from .summarize import *
from .mutate import *


@gr_pipe #should work on groups as well as ungrouped data
def mutate(df, **kwargs):
    """
    Emulating Dplyr mutate. Assigning new values to a dataframe 
    """

    return df.assign(**kwargs)