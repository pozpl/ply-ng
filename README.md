# PlyNG

> Educational project to play with pandas and python


This is mostly educational project to bring some goodies I frequently use from R dplyr package into my python pandas workflow plus learn more about python.

## Functionality overview

Mimiking R dplyr package dataframe opration piped evaluation composition is used but instead of `%>%` symbol the `>>`. As well due to python limitations  *tidy evaluations* used in dplyr implemented with use of the `X` object which is used to represent the current dataframe (There is `Y` object but is used only in the joins as symbol for representing right dataframe).

### The `>>` pipe and symbolic dataframe operations

Dataframe operations represented as a chain of functions glued together with a `>>` (pipe) operator. Order of execution is from left to right. Each funciton in this chain return a new dataframe that passed as a first argument to the next function in the chain. This dataframe denoted by the symbol `X` and can be used in expressions passed a arguments to the functions in the chain.

```python
result = (df1 >>
        inner_join(df2, by=[(X.length, Y.max_len), (X.state, Y.state)]) >>
        mutate(xwz = X.sugar_price + Y.sun_period) >>
        select(X.state, X['xwz'])
)
```


