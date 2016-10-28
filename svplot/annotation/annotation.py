#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""

"""

import numpy as np
import matplotlib as mpl


def add_count_label(ax, count, pct=False, as_pct=True, horiz=False, fontsize=11):
    max_height = 0

    if not horiz:
        def get_size(p):
            if np.isnan(p.get_height()):
                return 0
            else:
                return p.get_height()

        x_pos = lambda p, max_height: p.get_x() + p.get_width() / 2
        y_pos = lambda p, max_height: get_size(p) + .01*max_height
        ha = 'center'
    else:
        def get_size(p):
            if np.isnan(p.get_width()):
                return 0
            else:
                return p.get_width()

        # x_pos = lambda p, max_height: get_size(p) + .1*max_height
        if pct:
            x_pos = lambda p, max_height: get_size(p) + .03 * max_height
        else:
            xmax = ax.get_xlim()[1]
            if np.isnan(xmax):
                import pdb
                pdb.set_trace()
            x_pos = lambda p, max_height: get_size(p) + .02 * xmax
        y_pos = lambda p, max_height: p.get_y() + 3 * p.get_height() / 4.0
        ha = 'left'

    for p in ax.patches:
        # height = p.get_height()
        height = get_size(p)
        if height > max_height:
            max_height = height

    for p in ax.patches:
        # height = p.get_height()
        height = get_size(p)
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

        ax.text(x_pos(p, max_height), y_pos(p, max_height),
                label,
                ha=ha, va='bottom',
                fontsize=fontsize)


