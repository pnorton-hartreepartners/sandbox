'''
conda install -c conda-forge treelib
'''

from treelib import Tree
import os
import pandas as pd
from zzz_eia_hierarchy_definitions import hierarchy_dict_us_stocks

source_key = 'WTTSTUS1'

# get saved metadata
path = r'C:\Temp'
file_for_metadata = 'eia-weekly-metadata'
file_for_mosaic_hierarchy = 'eia-weekly-mosaic_hierarchy'
suffix = '.pkl'
pathfile = os.path.join(path, file_for_metadata)
metadata_df = pd.read_pickle(pathfile + suffix)

# create tree and root node
tree = Tree()
description = metadata_df.loc[[source_key], ['Description']].values[0][0]
tree.create_node(source_key, source_key, data=description)

# create the tree
for parent, children in hierarchy_dict_us_stocks.items():
    try:
        id = tree.get_node(parent).identifier
    except AttributeError:
        pass
    else:
        for child in children:
            # add the description to the node as metadata
            description = metadata_df.loc[[child], ['Description']].values[0][0]
            tree.create_node(child, child, parent=id, data=description)

# visual validation
tree.show()
print(tree.to_json(with_data=True))

# ==================================
# create dataframes

max_depth = tree.depth() + 1
columns = [str(level) for level in range(max_depth)]

# symbols
leaves = tree.paths_to_leaves()
padded_leaves = [leaf + [''] * (max_depth - len(leaf)) for leaf in leaves]

# descriptions
descriptions = [[tree.get_node(leaf).data for leaf in row] for row in leaves]
padded_descriptions = [description + [''] * (max_depth - len(description)) for description in descriptions]

# create the dfs
symbol_df = pd.DataFrame(data=padded_leaves, columns=columns)
description_df = pd.DataFrame(data=padded_descriptions, columns=columns)

# export
description_df.to_clipboard()
pathfile = os.path.join(path, file_for_mosaic_hierarchy)
description_df.to_pickle(pathfile + suffix)
