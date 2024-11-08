# Useful functions

Currently, there are two useful methods for querying and manipulating expressions, namely `collect_operators` and `replace`. In following are examples for each.


```python exec="on" source="material-block" result="json" session="functions"
from qadence2_expressions import *

collected_ops = collect_operators(Z(1) + 2 * Z(1) * Z (2) - X(3))

print(collected_ops) # markdown-exec: hide
```


```python exec="on" source="material-block" result="json" session="functions"
replacement_rules = {Z(1): X(1)}

replaced_ops = replace(Z(1) + 2 * Z(1) * Z (2) - X(3), replacement_rules)

print(f"\u2192 {replaced_ops}") # markdown-exec: hide
```
