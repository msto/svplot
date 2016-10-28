"""

"""

import numpy as np


def _patch_size(patch, orient='v'):
    """
    Get plotted value via patch size
    Height for vertical bars, width for horizontal bars

    Parameters
    ----------
    patch : matplotlib patch
    orient : 'v' | 'h'

    Returns
    -------
    size : float
    """

    if orient == 'v':
        if np.isnan(patch.get_height()):
            return 0
        else:
            return patch.get_height()
    else:
        if np.isnan(patch.get_width()):
            return 0
        else:
            return patch.get_width()


# position relative to bar size (y for vertical, x for horizontal)
# is transformed by axis. The position relative to categorical axis is
# calculated without need for transformation, so we need to reverse
# transform it before passing it to matplotlib
def _reverse_transform(pos, ax_min, ax_max):
    return (pos - ax_min) / (ax_max - ax_min)


def _patch_center(patch, orient='v'):
    """
    Get coordinate of bar center

    Parameters
    ----------
    patch : matplotlib patch
    orient : 'v' | 'h'

    Returns
    -------
    center : float
    """

    if orient not in 'v h'.split():
        raise Exception("Orientation must be 'v' or 'h'")

    if orient == 'v':
        x = patch.get_x()
        width = patch.get_width()
        xpos = x + width / 2
        return xpos
    else:
        y = patch.get_y()
        height = patch.get_height()
        ypos = y + height / 2
        return ypos


def _bar_end_midpoint(patch, ax, orient='v'):
    """
    Coordinates of midpoint of bar's end

    Parameters
    ----------
    patch : matplotlib patch
    ax : matplotlib Axes
    orient : 'v' | 'h'

    Returns
    -------
    xpos : float
    ypos : float
    """

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    ax_width = xmax - xmin
    ax_height = ymax - ymin

    if orient == 'v':
        xpos = _patch_center(patch, orient)
        xpos = _reverse_transform(xpos, xmin, xmax)

        ypos = _patch_size(patch, orient) / ax_height
    else:
        xpos = _patch_size(patch, orient) / ax_width

        ypos = _patch_center(patch, orient)
        ypos = _reverse_transform(ypos, ymin, ymax)

    return xpos, ypos


def add_count_label(ax, count=0, pct=False, as_pct=True,
                    orient='v', loc='above', offset=0.01,
                    color='black', palette=None,
                    fontsize=11):
    """
    Add count labels to a bar or count plot.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes object to annotate.
    orient : 'v' | 'h', optional
        Orientation of the plot (vertical or horizontal).
    loc : 'above' | 'inside', optional
        Position of text labels.
        - above: Labels will be plotted above the top each bar
        - inside: Labels will be plotted inside each bar, at the top
        - TODO: base: Labels will be plotted at the base of each bar
    offset : float, optional
        Offset of the label relative to the bar end. Scaled to a [0, 1] axis.
    color : matplotlib color, optional
        Text color.
    palette : list of matplotlib colors or seaborn color palette, optional
        Cycle of text label colors.
        Useful for situations where the bars are plotted with a `hue` attribute
        and the labels are plotted inside the bars.

    TODO: add format string
    TODO: handle percentages better
    """

    # Input validation
    if orient not in 'v h'.split():
        raise Exception("Orientation must be 'v' or 'h'")
    if loc not in 'above inside'.split():
        msg = "Loc must be one of 'above', 'inside'"
        raise Exception(msg)

    # Constants
    if orient == 'v':
        ha = 'center'
        if loc == 'above' or loc == 'base':
            va = 'bottom'
        else:
            va = 'top'
    else:
        va = 'center'
        if loc == 'above' or loc == 'base':
            ha = 'left'
        else:
            ha = 'right'

    # sort by x position for palette cycling
    if orient == 'v':
        patches = sorted(ax.patches, key=lambda p: p.get_x())
    else:
        patches = sorted(ax.patches, key=lambda p: p.get_y())

    for i, patch in enumerate(patches):
        value = _patch_size(patch, orient)
        if np.isnan(value):
            value = 0

        if pct:
            if as_pct:
                label = '%.1f%%' % (value * 100)
                fontsize = fontsize

            else:
                label = str(int(value * count))
                fontsize = fontsize
        else:
            label = str(int(value))
            fontsize = fontsize

        if palette is not None:
            color = palette[i % len(palette)]

        # Position label
        xpos, ypos = _bar_end_midpoint(patch, ax, orient)
        if orient == 'v':
            if loc == 'above' or loc == 'base':
                ypos = ypos + offset
            else:
                ypos = ypos - offset
        else:
            if loc == 'above' or loc == 'base':
                xpos = xpos + offset
            else:
                xpos = xpos - offset

        ax.text(xpos, ypos,
                label, color=color,
                ha=ha, va=va,
                fontsize=fontsize,
                transform=ax.transAxes)


def add_comparison_bars(ax, orient='v', offset=0.01,
                        color='black', palette=None):
    """
    Add count labels to a bar or count plot.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes object to annotate.
    orient : 'v' | 'h', optional
        Orientation of the plot (vertical or horizontal).
    offset : float, optional
        Offset of the label relative to the bar end. Scaled to a [0, 1] axis.
    color : matplotlib color, optional
        Text color.
    palette : list of matplotlib colors or seaborn color palette, optional
        Cycle of text label colors.
        Useful for situations where the bars are plotted with a `hue` attribute
        and the labels are plotted inside the bars.
    """

    # Input validation
    if orient not in 'v h'.split():
        raise Exception("Orientation must be 'v' or 'h'")

    # Constants
    if orient == 'v':
        ha = 'center'
        va = 'bottom'
    else:
        va = 'center'
        ha = 'left'

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x_width = xmax - xmin
    y_height = ymax - ymin

    # position relative to bar size (y for vertical, x for horizontal)
    # is transformed by axis. The position relative to categorical axis is
    # calculated without need for transformation, so we need to reverse
    # transform it before passing it to matplotlib
    def _reverse_transform(pos, ax_min, ax_max):
        return (pos - ax_min) / (ax_max - ax_min)

    def _xpos(patch):
        if orient == 'v':
            xpos = _patch_center(patch, orient)
            return _reverse_transform(xpos, xmin, xmax)
        else:
            xpos = _patch_size(patch) / x_width
            xpos = xpos + offset
            return xpos

    def _ypos(patch):
        if orient == 'v':
            ypos = _patch_size(patch) / y_height
            ypos = ypos + offset
        else:
            ypos = _patch_center(patch, orient)
            return _reverse_transform(ypos, ymin, ymax)

    # sort by x position for palette cycling
    if orient == 'v':
        patches = sorted(ax.patches, key=lambda p: p.get_x())
    else:
        patches = sorted(ax.patches, key=lambda p: p.get_y())

    for i, p in enumerate(patches):
        value = _patch_size(p)
        if np.isnan(value):
            value = 0

        if pct:
            if as_pct:
                label = '%.1f%%' % (value * 100)
                fontsize = fontsize

            else:
                label = str(int(value * count))
                fontsize = fontsize
        else:
            label = str(int(value))
            fontsize = fontsize

        if palette is not None:
            color = palette[i % len(palette)]

        print(i, label)
        ax.text(_xpos(p), _ypos(p),
                label, color=color,
                ha=ha, va=va,
                fontsize=fontsize, transform=ax.transAxes)
