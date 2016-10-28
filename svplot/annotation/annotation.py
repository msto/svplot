#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""

"""

import numpy as np
import itertools as it


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
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x_width = xmax - xmin
    y_height = ymax - ymin

    # Compute position of label relative to patch size
    # Height for vertical bars, width for horizontal bars
    def _patch_size(patch):
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

    print(ax.get_xlim())

    # position relative to bar size (y for vertical, x for horizontal)
    # is transformed by axis. The position relative to categorical axis is
    # calculated without need for transformation, so we need to reverse
    # transform it before passing it to matplotlib
    def _reverse_transform(pos, ax_min, ax_max):
        return (pos - ax_min) / (ax_max - ax_min)

    def _xpos(patch):
        if orient == 'v':
            x = patch.get_x()
            width = patch.get_width()
            xpos = x + width / 2
            return _reverse_transform(xpos, xmin, xmax)
        else:
            xpos = _patch_size(patch) / x_width

            if loc == 'above' or loc == 'base':
                xpos = xpos + offset
            else:
                xpos = xpos - offset
            return xpos
        #  else:
        #  if pct:
        #  x_pos = lambda p, max_height: _label_offset(p) + .03 * max_height
        #  else:
            #  xmax = ax.get_xlim()[1]
            #  x_pos = lambda p, max_height: _label_offset(p) + .02 * xmax

    def _ypos(patch):
        if orient == 'v':
            ypos = _patch_size(patch) / y_height

            if loc == 'above' or loc == 'base':
                ypos = ypos + offset
            else:
                ypos = ypos - offset
            return ypos
            #  return _patch_size(patch) + .01 * max_height
        else:
            y = patch.get_y()
            height = patch.get_height()
            ypos = y + height / 2
            return _reverse_transform(ypos, ymin, ymax)
            #  return patch.get_y() + 3 * patch.get_height() / 4.0

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
                fontsize=fontsize,
                transform=ax.transAxes)
