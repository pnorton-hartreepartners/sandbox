from treelib import Node, Tree, exceptions
import pandas as pd
from eia_hierarchy_definitions import hierarchy_dict_us_stocks

tree = Tree()

# create root node
parent = 'WTTSTUS1'
tree.create_node(parent, parent)

# create the tree
for parent, children in hierarchy_dict_us_stocks.items():
    try:
        id = tree.get_node(parent).identifier
    except AttributeError:
        pass
    else:
        for child in children:
            tree.create_node(child, child, parent=id)

# visual validation
tree.show()

# create dataframe
max_depth = tree.depth() + 1
leaves = tree.paths_to_leaves()
padded_leaves = [leaf + [''] * (max_depth - len(leaf)) for leaf in leaves]
columns = [str(level) for level in range(max_depth)]
df = pd.DataFrame(data=padded_leaves, columns=columns)

print('hello world')
