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
    Coordinates of midpoint of bar's end. Scaled to a (0, 1) axis.

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

    # Transform position to a (0, 1) axis
    def _ax_transform(pos, ax_min, ax_max):
        return (pos - ax_min) / (ax_max - ax_min)

    if orient == 'v':
        xpos = _patch_center(patch, orient)
        xpos = _ax_transform(xpos, xmin, xmax)

        ypos = _patch_size(patch, orient) / ax_height
    else:
        xpos = _patch_size(patch, orient) / ax_width

        ypos = _patch_center(patch, orient)
        ypos = _ax_transform(ypos, ymin, ymax)

    return xpos, ypos


def add_count_labels(ax, count=0, pct=False, as_pct=True,
                     orient='v', loc='above', offset=0.01,
                     color='black', palette=None,
                     fontsize=11, **kwargs):
    """
    Add count labels to a bar or count plot.

    NOTE: Must apply after changing axis xlim/ylim

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
    kwargs : key, value mappings
        Other keyword arguments are passed to ax.text

    TODO: add format string
    TODO: improve percentage handling
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
                transform=ax.transAxes,
                **kwargs)


def add_comparison_bars(ax, p=None, orient='v',
                        bar_offset=0.02, top_offset=0.1,
                        fontsize=12, pval_offset=0.01,
                        color='black', **kwargs):
    """
    Add count labels to a bar or count plot.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes object to annotate.
    p : arraylike of float, optional
        Pairwise p-values to annotate with
    orient : 'v' | 'h', optional
        Orientation of the plot (vertical or horizontal).
    bar_offset : float, optional
        Distance between bottom of comparison lines and top of bars.
        Scaled to a (0, 1) axis.
    top_offset : float, optional
        Distance from bottom of upper comparison line to crossbar.
        Scaled to a (0, 1) axis.
    fontsize : int, optional
        p-value label font size
    pval_offset : float, optional
        Distance between p-value label and crossbar. Scaled to a (0, 1) axis.
    color : matplotlib color, optional
        Text color.
    kwargs : key, value mappings
        Other keyword arguments are passed to ax.plot
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

    # sort by x position for palette cycling and comparison bar pairing
    if orient == 'v':
        patches = sorted(ax.patches, key=lambda p: p.get_x())
    else:
        patches = sorted(ax.patches, key=lambda p: p.get_y())

    patch_pairs = zip(patches[0::2], patches[1::2])

    for i, (l_patch, r_patch) in enumerate(patch_pairs):
        l_xpos, l_ypos = _bar_end_midpoint(l_patch, ax, orient)
        r_xpos, r_ypos = _bar_end_midpoint(r_patch, ax, orient)

        if orient == 'v':
            max_val = max(l_ypos, r_ypos)
            top_pos = max_val + top_offset

            # Plot vertical lines
            ax.plot([l_xpos, l_xpos], [l_ypos + bar_offset, top_pos],
                    'k-', transform=ax.transAxes, **kwargs)
            ax.plot([r_xpos, r_xpos], [r_ypos + bar_offset, top_pos],
                    'k-', transform=ax.transAxes, **kwargs)

            # Plot crossbar
            ax.plot([l_xpos, r_xpos], [top_pos, top_pos],
                    'k-', transform=ax.transAxes, **kwargs)

        else:
            max_val = max(l_xpos, r_xpos)
            top_pos = max_val + top_offset

            # Plot vertical lines
            ax.plot([l_xpos + bar_offset, top_pos], [l_ypos, l_ypos],
                    'k-', transform=ax.transAxes, **kwargs)
            ax.plot([r_xpos + bar_offset, top_pos], [r_ypos, r_ypos],
                    'k-', transform=ax.transAxes, **kwargs)

            # Plot crossbar
            ax.plot([top_pos, top_pos], [l_ypos, r_ypos],
                    'k-', transform=ax.transAxes, **kwargs)

        # Add p-value annotations
        if p is not None:
            label = 'p={:.3f}'.format(p[i])

            if orient == 'v':
                xpos = np.mean([l_xpos, r_xpos])
                ypos = top_pos + pval_offset
            else:
                xpos = top_pos + pval_offset
                ypos = np.mean([l_ypos, r_ypos])

            ax.text(xpos, ypos, label, ha=ha, va=va, fontsize=fontsize,
                    transform=ax.transAxes)
