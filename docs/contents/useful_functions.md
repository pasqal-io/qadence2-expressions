# Useful functions

Currently, there are two useful methods for querying and manipulating expressions, namely `collect_operators` and `replace`. In following are examples for each.


```python exec="on" source="material-block" html="1" session="functions"
from qadence2_expressions import *

collected_ops = collect_operators(Z(1) + 2 * Z(1) * Z (2) - X(3))

print(collected_ops) # markdown-exec: hide
```


```python exec="on" source="material-block" html="1" session="functions"

rules = {Z(1): X(1)}

replaced_ops = replace(Z(1) + 2 * Z(1) * Z (2) - X(3), rules)

print(replaced_ops) # markdown-exec: hide
```
