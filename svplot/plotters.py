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
                      order=None, hue_order=None, orient='v', ax=None):
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
    # zorder<3 required to plot beneath violinplot
    ax = sns.stripplot(x=x, y=y, hue=hue, data=data,
                       order=order, hue_order=hue_order,
                       jitter=0.2, linewidth=0.5, edgecolor='k', size=3.5,
                       split=True,
                       ax=ax, zorder=1)

    # Plot violins
    ax = sns.violinplot(x=x, y=y, hue=hue, data=data,
                        order=order, hue_order=hue_order, ax=ax)

    # Change the color of the internal box/whisker plot
    for i, line in enumerate(ax.lines):
        # whiskers
        if i % 2 == 0:
            line.set_color('k')
            #  line.set_linewidth(3)
        # box
        else:
            line.set_color('k')
            #  line.set_linewidth(7)

    # Turn off violinplot fill and change the outline color
    # Variant on https://github.com/mwaskom/seaborn/issues/979
    poly_obs = False
    for collection in ax.collections:
        # PolyCollections are violins
        if isinstance(collection, mpl.collections.PolyCollection):
            r, g, b, a = collection.get_facecolor()[0]
            collection.set_facecolor((r, g, b, 0.3))
            collection.set_edgecolor('k')
            collection.set_linewidths(1.2)
            poly_obs = True

        # First n PathCollections are stripplot points
        # Subsequent PathCollections are data median
        if isinstance(collection, mpl.collections.PathCollection) and poly_obs:
            collection.set_visible(False)
            x, y = collection._offsets[0]
            ax.plot(x, y, 'ow', markersize=8, mew=1, mec='k')

    # Remove stripplot legend
    if hue is not None:
        legend = ax.get_legend()
        ax.legend_ = None
        texts = [text.get_text() for text in legend.texts]
        legend = ax.legend(legend.legendHandles[:2], texts,
                           frameon=True, loc='best')
        legend.get_frame().set_linewidth(1)

    return ax
