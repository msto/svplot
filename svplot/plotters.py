# -*- coding: utf-8 -*-
#
# Copyright © 2017 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""
Functions for common plots
"""

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


def violin_with_strip(x=None, y=None, hue=None, data=None,
                      order=None, hue_order=None, ax=None):
    """
    Plot stripplot with overlaying violin and box-and-whisker plot.

    Arguments
    ---------
    x, y, hue : names of variables in `data` or vector data, optional
    data : pd.DataFrame, array, or list of arrays, optional
    ax : matplotlib Axes

    Returns
    -------
    ax : matplotlib Axes

    TODO
    ----
    * parametrize edgecolors and linewidths
    * pass dicts of violin_kwargs and strip_kwargs dicts
    """

    if ax is None:
        ax = plt.gca()

    # Plot the data points
    ax = sns.stripplot(x=x, y=y, hue=hue, data=data,
                       order=order, hue_order=hue_order,
                       jitter=0.2, linewidth=0.5, edgecolor='k', size=3.5,
                       ax=ax)

    # stripplot is always plotted over violinplot if on same
    # axis, so make a new one atop the first
    ax2 = ax.twinx()

    # match the ylim as well as xlim
    ax2.set_ylim(ax.get_ylim())

    # Turn off grid lines across the axis so they don't
    # overlay on stripplot, and disable duplicate y-axis labels
    ax2.get_yaxis().set_visible(False)

    # Plot violins
    ax2 = sns.violinplot(x=x, y=y, hue=hue, data=data,
                         order=order, hue_order=hue_order, ax=ax2)

    # Turn off violinplot fill and change the outline color
    # Variant on https://github.com/mwaskom/seaborn/issues/979
    for collection in ax2.collections:
        # PolyCollections are violins
        if isinstance(collection, mpl.collections.PolyCollection):
            r, g, b, a = collection.get_facecolor()[0]
            collection.set_facecolor((r, g, b, 0.2))
            collection.set_edgecolor('k')
            collection.set_linewidths(1.2)

        # PathCollections are data median
        if isinstance(collection, mpl.collections.PathCollection):
            collection.set_edgecolor('k')
            collection.set_linewidth(0.1)

    # Change the color of the internal box/whisker plot
    for i, line in enumerate(ax2.lines):
        # whiskers
        if i % 2 == 0:
            line.set_color('k')
            #  line.set_linewidth(3)
        # box
        else:
            line.set_color('k')
            #  line.set_linewidth(7)

    return ax
