import matplotlib.pyplot as plt
from pprint import pformat


class AxesLineSelector:
    """
    A utility class that enables both interactive or programmatic selection
    and/or deletion of ``Line2D`` objects in the provided Axes instance. Also
    allows selecting a subset of ``Line2d`` instances and pasting them into a
    different :class:`~matplotlib.pyplot.Axes` instance.

    Args:
        ax (matplotlib.pyplot.Axes, optional): Axes object for which line
            selection/deletion/attribut-updates are to be made; Default of
            **None** results in ``plt.gca()`` being passed as ``ax``
        picker_arg (Any, optional): A valid value for the matplotlib ``picker``
            arg for any ``Artist`` instance as described here:
            https://matplotlib.org/3.2.1/users/event_handling.html#object-picking
    """
    LINE_PROPERTIES = {
        'linewidth', 'linestyle', 'alpha', 'color', 'antialiased',
        'dashcapstyle', 'dashjoinstyle', 'dashOffset', 'dashSeq',
        'drawstyle', 'label', 'marker', 'markeredgecolor',
        'markeredgewidth', 'markerfacecolor', 'markerfacecoloralt',
        'markersize', 'markevery', 'solidcapstyle', 'solidjoinstyle',
        'visible'}

    def __init__(self, ax=None, picker_arg=True):
        self.deleted_lines = []
        self.line_clipboard = []
        self.cid = None  # Callback id for active callback bound to lines
        self.picker_arg = picker_arg

        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax

    @property
    def fig(self):
        """Returns Figure instance that self.ax is bound to"""
        return self.ax.figure

    def redraw(self, ax=None):
        """Update legend if needed and redraw plot after any updates to it"""
        ax = self.ax if ax is None else ax
        if ax.legend_ is not None and ax.legend_.get_visible():
            ax.legend()  # Update legend if present and visible
        ax.figure.canvas.draw_idle()  # Refresh canvas

    def interactive_delete(self):
        """
        Bind callbacks to plot-window to enable interactive deletion by
        left-clicking on lines in the plot-window. All deleted lines are saved
        in the ``self.deleted_lines`` buffer so that deletion can be undone if
        desired.

        Notes:
            - Make sure to call ``self.disable_interactive()`` when interactive
            deletion mode is no longer desired.

            - Zooming is supported in interactive mode. Ensure that the lasso
            button is not selected after zooming when left-clicking on a line
            for deletion
        """
        self._disconnect_current_callback()
        for ln in self.ax.lines:
            ln.set_picker(self.picker_arg)
        self.cid = \
            self.fig.canvas.mpl_connect('pick_event', self._delete_callback)
        return self

    def delete_all_lines(self):
        """Delete all the lines in the axes. They are all stored in
        ``self.deleted_lines`` in case undoing of the deletion operation is
        desired"""
        while len(self.ax.lines) > 0:
            ln = self.ax.lines[-1]  # Delete last line
            self._delete_line(ln)
        return self

    def delete_selection(self):
        """
        Delete all lines in current selection and store in deletion buffer
        """
        while len(self.line_clipboard) > 0:
            ln = self.line_clipboard.pop(0)  # Delete first line in selection
            self._delete_line(ln)
        return self

    def delete_lines_by_inds(self, *inds):
        """
        Programmatically delete desired lines in the axes based on the provided
        set of indices.

        Args:
            *inds (Iterable[int]): Iterable of integer indices for lines in
                ``self.ax.lines`` to be deleted

        Note:
            The best way to determine indices for lines of interest is to rely
            on the ``__repr__()`` method for this class by simply querying the
            variable containing the instance of ``AxesLineSelector`` in your
            Python interpreter. The output provides indices for each line along
            with the label value if any. See example below for more information.

        Example:
            >>> ax_sel = AxesLineSelector()
            >>> ax_sel
            AxesLineSelector (
                ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7fba168c9990>
                is_interactive: False
                lines: ['0: Line2D(Label-A)',
                    '1: Line2D(Label-B)',
                    '2: Line2D(Label-C)',
                clipboard: ['0: Line2D(Label-A)',
                    '1: Line2D(Label-B)',
                deleted buffer: []
            )
            >>> # Delete lines with labels 'Label-A' and 'Label-C'
            >>> ax_sel.delete_lines_by_inds(0, 2)
        """
        if len(inds) < 1:
            raise ValueError('At least one or more indices should be provided')
        new_lines = []
        for i, l in enumerate(self.ax.lines):
            if i not in inds:
                new_lines.append(l)
            else:
                self.deleted_lines.append(l)
                print(f'Deleted line: {l}')
        self.ax.lines = new_lines
        self.redraw()
        return self

    def _delete_line(self, line):
        if line in self.ax.lines:
            self.ax.lines.remove(line)
            print(f'Deleted line: {line}')
            self.deleted_lines.append(line)
        else:
            print(f'Line: {line} was not in self.ax.lines. Skipped deletion')
        self.redraw()  # Update plot with deletion

    def _delete_callback(self, event):
        """Matplotlib event callback to bind to Line2D Artists for interactive
        deletion of lines in the plot-window"""
        sel_line = event.artist
        self._delete_line(sel_line)
        # self._refresh_plot()  # Update plot with deletion

    def undo_last_delete(self):
        """Restore last deleted line back to the Axes"""
        if len(self.deleted_lines) == 0:
            print('No line deletions to undo!')
        self.ax.lines.append(self.deleted_lines.pop())
        self.redraw()  # Update plot with line
        return self

    def undo_all_delete(self):
        """Restore all deleted lines that were stored in the ``self.deleted_lines``
        buffer. Note: Order of restored line-traces may differ from original
        ordering. See :meth:`~AxesLineSelector.reorder_lines` method"""
        for i in range(len(self.deleted_lines)):
            self.undo_last_delete()
        return self

    def reorder_lines(self, order):
        """
        Reorder lines in the Axes based on new ordering provided

        Args:
            order(Iterable[int]): An iterable of length matching the number of
                lines in the Axes instance, such that
                ``len(set(order)) == len(ax.lines)`` and
                ``set(range(len(ax.lines))) == set(order)``. i.e., all indices in
                ``order`` must be unique and span the range 0 to
                ``len(ax.lines) - 1``

        Example:
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3, 4], [1, 2, 1, 3], label='Line-A')
            >>> ax.plot([1, 2, 3, 4], [2, 4, 2, 1], label='Line-B')
            >>> ax.legend()
            >>> sel = AxesLineSelector(ax)
            >>> sel
                AxesLineSelector (
                    ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7fa1e57a32d0>
                    is_interactive: False
                    lines: ['0: Line2D(Line-A)', '1: Line2D(Line-B)']
                    clipboard: []
                    deleted buffer: []
                )
            >>> sel.reorder_lines([1, 0])  # 'Line-B' now precedes 'Line-A'
        """
        assert set(order) == set(range(len(self.ax.lines))), \
            (f'Provided ordering is not compatible with required unique inds: '
             f'{set(range(len(self.ax.lines)))}')
        new_lines = [None] * len(self.ax.lines)
        for old_ind, new_ind in enumerate(order):
            new_lines[new_ind] = self.ax.lines[old_ind]
        self.ax.lines = new_lines
        self.redraw()
        return self

    def interactive_select(self):
        """
        Bind callbacks to plot-window to enable interactive selection of lines by
        left-clicking on them in the plot-window. All selected lines are saved
        in the ``self.line_clipboard`` buffer and can then be operated on via
        :meth:`setattr_selections`, :meth:`getattr_selections` and
        :meth:`paste_selection`

        Notes:
            - Make sure to call ``self.disable_interactive()`` when interactive
            selection mode is no longer desired.

            - Zooming is supported in interactive mode. Ensure that the lasso
            button is not selected after zooming when left-clicking on a line
            for selection
        """
        self._disconnect_current_callback()
        for ln in self.ax.lines:
            ln.set_picker(self.picker_arg)
        self.cid = \
            self.fig.canvas.mpl_connect('pick_event', self._select_callback)
        return self

    def select_all_lines(self):
        """Select all lines in ``self.ax`` and store in :attr:`line_clipboards`"""
        for ln in self.ax.lines:
            self._add_line_to_clipboard(ln)
        return self

    def select_lines(self, sel_fn):
        """
        Select lines using provided selection function to the clipboard

        Args:
            sel_fn (Callable): Function signature is (line, i) where line is the
                :class:`~matplotlib.Line2D` instance of the axes and ``i`` is
                the index of the line in ``self.ax.lines``. ``sel_fn`` must
                return ``True`` for lines to be selected and ``False`` otherwise
        """
        for i, ln in enumerate(self.ax.lines):
            if sel_fn(ln, i):
                self._add_line_to_clipboard(ln)
        return self

    def select_lines_by_inds(self, *inds):
        """
        Select lines programmatically based on their indices in ``self.ax.lines``

        Args:
            *inds (Iterable[int]): Indices of lines in ``self.ax.lines`` to be
                selected and placed in internal :attr:`lines_clipboard`. Usually
                best determined by examining output of the :meth:`__repr__`
                method of this class as shown in the example below.

        Example:
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3, 4], [1, 2, 1, 3], label='Line-A')
            >>> ax.plot([1, 2, 3, 4], [2, 4, 2, 1], label='Line-B')
            >>> ax.legend()
            >>> sel = AxesLineSelector(ax)
            >>> sel
                AxesLineSelector (
                    ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7fa1e57a32d0>
                    is_interactive: False
                    lines: ['0: Line2D(Line-A)', '1: Line2D(Line-B)']
                    clipboard: []
                    deleted buffer: []
                )
            >>> sel.select_lines_by_inds(1)  # Select 'Line-B'
            Added line: Line2D(Line-B) to clipboard
            >>> sel
            AxesLineSelector (
                ax: <matplotlib.axes._subplots.AxesSubplot object at 0x7f3fb2b935d0>
                is_interactive: False
                lines: ['0: Line2D(Line-A)', '1: Line2D(Line-B)']
                clipboard: ['0: Line2D(Line-B)']
                deleted buffer: []
            )

        """
        if len(inds) < 1:
            raise ValueError('At least one or more indices should be provided')
        for ind in inds:
            self._add_line_to_clipboard(self.ax.lines[ind])
        return self

    def _add_line_to_clipboard(self, line):
        if line not in self.line_clipboard:
            self.line_clipboard.append(line)
            print(f'Added line: {line} to clipboard')
        else:
            print(f'Line {line} already exists in clipboard. Skipping...')

    def _select_callback(self, event):
        """Matplotlib event callback to bind to Line2D Artists for interactive
        selection of lines in the plot-window"""
        sel_line = event.artist
        self._add_line_to_clipboard(sel_line)

    def undo_last_selection(self):
        if len(self.line_clipboard) == 0:
            print('No line selections to undo!')
        ln = self.line_clipboard.pop()
        print(f'Removed line: {ln} from clipboard')
        return self

    def clear_clipboard(self):
        self.line_clipboard = []
        return self

    # TODO: Make this return a new AxesSelection object with pasted lines selected
    def paste_selection(self, ax):
        """
        Paste a copy of all lines in the internal :attr:`lines_clipboard`
        attribute from the selection process into a different matplotlib Axes
        instance. All line properties as defined in ``self.LINE_PROPERTIES`` are
        copied over to the new Line2D instance in :attr:`ax`

        Args:
            ax (matplotlib.pyplot.Axes): Axes instance into which the lines in
                the selection clipboard are to be copied over.

        Example:
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3, 4], [1, 2, 1, 3], label='Line-A')
            >>> ax.plot([1, 2, 3, 4], [2, 4, 2, 1], label='Line-B')
            >>> ax.legend()
            >>> sel = AxesLineSelector(ax)
            >>>
            >>> # Select 'Line-B'
            >>> sel.select_lines_by_inds(1)
            >>>
            >>> # Create new empty plot
            >>> fig2, ax2 = plt.subplots()
            >>>
            >>> # Copy over 'Line-B' into new plot
            >>> sel.paste_selection(ax2)
        """
        new_sel_line_clipboard = []
        for ln in self.line_clipboard:
            # Plot a new line2D with same x-y data as line in clipboard
            new_l = ax.plot(*ln.get_data())[0]
            # Copy over all relevant attributes from line in clipboard to new line
            for line_attr in self.LINE_PROPERTIES:
                setattr(new_l, f'_{line_attr}', getattr(ln, f'_{line_attr}'))
            new_sel_line_clipboard.append(new_l)

        # Update the axes being pasted into
        self.redraw(ax)

        # Return new selection for axes that was pasted into with pasted lines selected
        new_sel = AxesLineSelector(ax=ax, picker_arg=self.picker_arg)
        new_sel.line_clipboard = new_sel_line_clipboard
        return new_sel

    def setattr_selection(self, attr, value):
        """
        Set a supported line property (see :class:`~AxesLineSelector.LINE_PROPERTIES`)
        for all lines in the current clipboard selection and redraw plot.

        Args:
            attr (str): A supported line-property (see :attr:`LINE_PROPERTIES`)
            value (tuple or Any): Either a single valid property value that is
                assigned uniformly to all lines in the selection, or a tuple of
                the same length as the current line-clipboard selection with valid
                property values that are assigned to each line
        """
        assert attr in self.LINE_PROPERTIES, \
            f'{attr} is an unsupported line-property. Must be ' \
            f'one of {self.LINE_PROPERTIES}'
        if isinstance(value, tuple):
            assert len(value) == len(self.line_clipboard), \
                f'Invalid number of values provided for ' \
                f'{len(self.line_clipboard)} lines in clipboard'
        else:
            value = tuple([value] * len(self.line_clipboard))
        for ln, val in zip(self.line_clipboard, value):
            setter = getattr(ln, f'set_{attr}')
            setter(val)
        self.redraw()
        return self

    def getattr_selection(self, attr):
        """
        Get a tuple of attribute values for lines in current clipboard selection.

        Args:
            attr (str): A supported line-property (see :attr:`LINE_PROPERTIES`)

        Returns:
            (tuple): Tuple of length matching the number of lines in the current
                clipboard selection with each entry containing the value for the
                `attr` attribute for that line
        """
        assert attr in self.LINE_PROPERTIES, \
            f'{attr} is an unsupported line-property. Must be ' \
            f'one of {self.LINE_PROPERTIES}'
        retval = []
        for ln in self.line_clipboard:
            getter = getattr(ln, f'get_{attr}')
            retval.append(getter())
        return tuple(retval)

    def _disconnect_current_callback(self):
        if self.cid is not None:
            self.fig.canvas.mpl_disconnect(self.cid)
            self.cid = None

    def disable_interactive(self):
        """Detach registered callbacks for interactive plot selection/deletion
        from :attr:`ax`"""
        self._disconnect_current_callback()
        return self

    def __del__(self):
        self._disconnect_current_callback()

    def __repr__(self):
        clipboard = pformat([f'{i}: {str(ln)}' for i, ln in enumerate(self.line_clipboard)]).replace('\n', '\n\t\t')
        deleted = pformat([str(ln) for ln in self.deleted_lines]).replace('\n', '\n\t\t')
        lines = pformat([f'{i}: {str(ln)}' for i, ln in enumerate(self.ax.lines)]).replace('\n', '\n\t\t')
        return f"{self.__class__.__name__} (\n" \
               f"\tax: {self.ax.__repr__()}\n" \
               f"\tis_interactive: {self.cid is not None}\n" \
               f"\tlines: {lines}\n" \
               f"\tclipboard: {clipboard}\n" \
               f"\tdeleted buffer: {deleted}\n)"
