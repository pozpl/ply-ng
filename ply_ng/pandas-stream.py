

pandas = None

def inject_ply(pandas_to_augment):
    """Augment vanila pandas with new methods"""
    global pandas
    pandas = pandas_to_augment

    pandas.DataFrame.ply_select = _ply_select



def _ply_select(self, *args):
    """Transform a dataframe by selecting old columns and new (computed)
    columns.
    dplyr's ``select``
    Args:
        `*args`: Each should be one of:
            ``'*'``
                says that all columns in the input dataframe should be
                included
            ``'column_name'``
                says that `column_name` in the input dataframe should be
                included
            ``'-column_name'``
                says that `column_name` in the input dataframe should be
                excluded.
            If any `'-column_name'` is present, then `'*'` should be
            present, and if `'*'` is present, no 'column_name' should be
            present. Column-includes and column-excludes should not overlap.
    """
    input_columns = set(self.columns)

    has_star = False
    include_columns = []
    exclude_columns = []

    for arg in args:
        if arg == '*':
            if has_star:
                raise ValueError('ply_select received repeated stars, there could be only one * argument')
            has_star = True
        elif arg in input_columns: #checking that argument is in the dataframe
            if arg in include_columns: #already there
                raise ValueError(
                    'ply_select received a repeated column to include (%s)' % arg)
            include_columns.append(arg)
        elif arg[0] == '-' and arg[1:] in input_columns: #check that exclude column is in the dataframe
            if arg in exclude_columns:
                raise ValueError(
                    'ply_select received a repeated column-exclude (%s)' % arg[1:])
            exclude_columns.append(arg[1:])    
        else:
            raise ValueError('ply_select can not parse argument (%s) it should be a column -column or * ' % arg)

    if exclude_columns and not has_star: #exclude columns only viable with star
        raise ValueError('ply_select received column-excludes without an star')
    if has_star and include_columns: #There is no need for include columns and a star
        raise ValueError('ply_select received both an star and column-includes')
    if set(include_columns) & set(exclude_columns): # we can not include and exclude in the same time
        raise ValueError('ply_select received overlapping column-includes and column-excludes')

    include_columns_inc_star = self.columns if has_star else include_columns

    output_columns = [col for col in include_columns_inc_star
                      if col not in exclude_columns]    

    filtered_columns = self[output_columns]

    return  filtered_columns             


def _ply_mutate(self, *args, **kwargs):
    """Transform a dataframe by selecting old columns and new (computed)
    columns.
    dplyr's ``select``
    Args:
        `*args`: Each should be one of:
            ``'*'``
                says that all columns in the input dataframe should be
                included
            ``'column_name'``
                says that `column_name` in the input dataframe should be
                included
            ``'-column_name'``
                says that `column_name` in the input dataframe should be
                excluded.
            If any `'-column_name'` is present, then `'*'` should be
            present, and if `'*'` is present, no 'column_name' should be
            present. Column-includes and column-excludes should not overlap.
    """
    input_columns = set(self.columns)

    # Creating copy of a dataframe, wasteful????
    mutated_df = self[input_columns]

    # Temporarily disable SettingWithCopyWarning, as setting columns on a
    # copy (`to_return`) is intended here.
    with pandas.option_context('mode.chained_assignment', None):

        for column_name, column_value in iteritems(kwargs):
            evaluated_value = symbolic.to_callable(column_value)(self)
            # TODO: verify that evaluated_value is a series!
            if column_name == 'index':
                mutated_df.index = evaluated_value
            else:
                mutated_df[column_name] = evaluated_value

    return mutated_df            
