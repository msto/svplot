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
import numpy as np

from .constants import LOG_SIZES


def _plot_svsize_density(log_svsize, ax, label=None,
                         linestyle='-', color='k'):
    """
    Helper function to plot svsize.

    sns.distplot does not support independent control of alpha for density line
    and shading, so must invoke twice.

    log_svsize : pd.Series or np.ndarray
    """

    if label is not None:
        label = label + ' (n={0:,})'.format(log_svsize.shape[0])

    ax = sns.distplot(log_svsize, hist=False,
                      kde_kws=dict(shade=True, alpha=0.2),
                      color=color,
                      ax=ax)

    kde_kws = dict(shade=False, linewidth=2.5, linestyle=linestyle, alpha=1)
    ax = sns.distplot(log_svsize, hist=False, kde_kws=kde_kws,
                      label=label, color=color,
                      ax=ax)


def _add_log_ticks(ax, axmin, axmax, axis='x'):
    # Generate log-scaled ticks
    ticks = []
    for i in range(axmin, axmax):
        ticks.append(np.arange(10 ** i, 10 ** (i + 1), 10 ** i))
    ticks.append(np.array([10 ** axmax]))
    ticks = np.concatenate(ticks)
    log_ticks = [np.log10(x) for x in ticks]

    if axis == 'x':
        ax.set_xticks(log_ticks)
        ax.set_xlim(axmin, axmax)
    else:
        ax.set_yticks(log_ticks)
        ax.set_ylim(axmin, axmax)


def plot_svsize_distro(df, hue=None, hue_order=None, ax=None,
                       hue_dict=None, palette=None,
                       xmin=1, xmax=8):

    # Check for required columns
    if 'log_svsize' not in df.columns:
        raise Exception('Column `log_svsize` not present in dataframe')
    if hue is not None and hue not in df.columns:
        raise Exception('Hue column {0} not present in dataframe'.format(hue))

    # Set defaults
    if ax is None:
        ax = plt.gca()
    if palette is None:
        palette = sns.color_palette('colorblind')

    # If no hue specified, plot size distribution of entire dataframe
    if hue is None:
        _plot_svsize_density(df.log_svsize, ax, color=palette[0])

    # If hue column specified, plot size distribution of each set and label
    # appropriately
    else:
        hue_col = hue
        if hue_order is None:
            hue_order = sorted(df[hue_col].unique())
            if len(hue_order) > len(palette):
                raise Exception('Palette smaller than number of hue variables')

        for i, hue_val in enumerate(hue_order):
            if hue_dict is None:
                label = str(hue_val)
            else:
                label = hue_dict[hue_val]

            data = df.loc[df[hue_col] == hue_val]
            _plot_svsize_density(data.log_svsize, ax, label, color=palette[i])

    # Add legend
    l = ax.legend(frameon=True)
    l.get_frame().set_linewidth(1)

    # Remove horizontal grid lines
    ax.yaxis.grid(False)

    # Label axes
    ax.set_ylabel('Density')
    ax.set_xlabel('Log-scaled SV length')

    # Add log-scaled xtick labels
    _add_log_ticks(ax, xmin, xmax)

    xticklabels = []
    for i in range(xmin, xmax):
        xticklabels.append([LOG_SIZES[i]] + [''] * 8)
    xticklabels.append([LOG_SIZES[xmax]])
    xticklabels = np.concatenate(xticklabels)
    ax.set_xticklabels(xticklabels)

    return ax


def violin_with_strip(x=None, y=None, hue=None, data=None,
                      order=None, hue_order=None, orient='v', ax=None,
                      violin_kwargs={}):
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
                        order=order, hue_order=hue_order, ax=ax,
                        **violin_kwargs)

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
            ax.plot(x, y, 'ow', markersize=7, mew=1, mec='k')

    # Remove stripplot legend
    if hue is not None:
        legend = ax.get_legend()
        ax.legend_ = None
        texts = [text.get_text() for text in legend.texts]
        legend = ax.legend(legend.legendHandles[:2], texts,
                           frameon=True, loc='best')
        legend.get_frame().set_linewidth(1)

    return ax
