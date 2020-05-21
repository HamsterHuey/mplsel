A utility class to enable easier selection, interaction, modification and 
duplication of Line2D-based matplotlib plots. More documentation to follow.
Source code is currently fairly well documented and self-explanatory.


## Example
The following code demonstrates the main functionality of the `AxesLineSelector`
class:

```python
import matplotlib.pyplot as plt
import numpy as np
from mplsel import AxesLineSelector

# %% Create a demo plot
fig, ax = plt.subplots()
for i in range(5):
    ax.plot(range(10), i + np.random.rand(10,), label=f'Line-{i}')
ax.legend()

# %% Create a selection object bound to the Axes instance
sel = AxesLineSelector(ax)  # no ax param will bind this to plt.gca()

# Display contents of Axes in a useful way:
sel
# Output:
#     AxesLineSelector (
#         ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7f3ffafc67d0>
#         is_interactive: False
#         lines: ['0: Line2D(Line-0)',
#              '1: Line2D(Line-1)',
#              '2: Line2D(Line-2)',
#              '3: Line2D(Line-3)',
#              '4: Line2D(Line-4)']
#         clipboard: []
#         deleted buffer: []
#     )

# %% Programmatically select 'Line-1' and 'Line-4'
sel.select_lines_by_inds(1, 4)
# Output:
#     AxesLineSelector (
#         ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7f3ffafc67d0>
#         is_interactive: False
#         lines: ['0: Line2D(Line-0)',
#              '1: Line2D(Line-1)',
#              '2: Line2D(Line-2)',
#              '3: Line2D(Line-3)',
#              '4: Line2D(Line-4)']
#         clipboard: ['0: Line2D(Line-1)', '1: Line2D(Line-4)']
#         deleted buffer: []
#     )

# %% Modify selection attributes and update plot
# Chained operation. 1st operation  applies different styles to each line
sel.setattr_selection('linestyle', ('-.', '--')) \
   .setattr_selection('linewidth', .5)  # Apply same width to all selected lines

# %% Create new empty plot and copy over selected lines
fig2, ax2 = plt.subplots()
# Copy over the 2 selected lines with modified attributes into new plot
# and obtain a new selection for the 2nd figure with pasted lines already
# in the selection clipboard for the new selection object
sel2 = sel.paste_selection(ax2)
ax2.legend()

# Update the pasted lines in the 2nd figure
sel2.setattr_selection('linestyle', '_') \
    .setattr_selection('linewidth', 3)


# %% Demo of other functionality
# Delete 'Line-2', 'Line-3' from the original plot
sel.delete_lines_by_inds(2, 3)

# Undo deletion
sel.undo_all_delete()

# Clear selection clipboard
sel.clear_clipboard()

# Enable interactive line selection by left-clicking on lines in plot window
# Left-click on lines should print a selection notification to console
sel.interactive_select()

# Enable interactive deletion by left-clicking on lines
sel.interactive_delete()

# Disable interactive callbacks in plot-window
sel.disable_interactive()

# Reorder lines (usually to make legend easier to reason about)
sel.reorder_lines((1, 3, 2, 4, 0))

```