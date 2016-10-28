#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""

"""

import numpy as np


def add_count_label(ax, count, pct=False, as_pct=True, horiz=False,
                    orient='v', loc='above',
                    fontsize=11):
    """
    Add count labels to a bar or count plot.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes object to annotate.
    orient : 'v' | 'h', optional
        Orientation of the plot (vertical or horizontal).
    loc : 'above' | 'inside' | 'base', optional
        Position of text labels.
        - above: Labels will be plotted above the top each bar
        - inside: Labels will be plotted inside each bar, at the top
        - base: Labels will be plotted at the base of each bar
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
    if loc not in 'above inside base'.split():
        msg = "Loc must be one of 'above', 'inside', 'base'"
        raise Exception(msg)

    # Constants
    if orient == 'v':
        ha = 'center'
    else:
        ha = 'left'
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

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

    def _reverse_transform(pos, ax_min, ax_max):
        return (pos - ax_min) / (ax_max - ax_min)

    def _xpos(patch, max_height):
        if orient == 'v':
            x = patch.get_x()
            width = patch.get_width()
            xpos = x + width / 2
            return _reverse_transform(xpos, xmin, xmax)
        #  else:
        #  if pct:
        #  x_pos = lambda p, max_height: _label_offset(p) + .03 * max_height
        #  else:
            #  xmax = ax.get_xlim()[1]
            #  x_pos = lambda p, max_height: _label_offset(p) + .02 * xmax

    def _ypos(patch, max_height):
        if orient == 'v':
            return _patch_size(patch) / ymax
            #  return _patch_size(patch) + .01 * max_height
        else:
            return patch.get_y() + 3 * patch.get_height() / 4.0

    max_height = 0

    for p in ax.patches:
        # height = p.get_height()
        height = _patch_size(p)
        if height > max_height:
            max_height = height

    for p in ax.patches:
        # height = p.get_height()
        height = _patch_size(p)
        if np.isnan(height):
            height = 0

        if pct:
            if as_pct:
                label = '%.1f%%' % (height * 100)
                fontsize = fontsize

            else:
                label = str(int(height * count))
                fontsize = fontsize
        else:
            label = str(int(height))
            fontsize = fontsize

        ax.text(_xpos(p, max_height), _ypos(p, max_height),
                label,
                ha=ha, va='bottom',
                fontsize=fontsize,
                transform=ax.transAxes)
