#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""
Modification of Michael Waskom's JointGrid implementation in Seaborn.

Supports multiple JointGrids in single figure
"""

import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import seaborn as sns


class JointGrid(sns.JointGrid):
    """Grid for drawing a bivariate plot with marginal univariate plots."""

    def __init__(self, x, y, data=None, gs=None, ratio=5, space=.2,
                 dropna=True, xlim=None, ylim=None):
        """Set up the grid of subplots.

        Parameters
        ----------
        x, y : strings or vectors
            Data or names of variables in ``data``.
        data : DataFrame, optional
            DataFrame when ``x`` and ``y`` are variable names.
        size : numeric
            Size of each side of the figure in inches (it will be square).
        ratio : numeric
            Ratio of joint axes size to marginal axes height.
        space : numeric, optional
            Space between the joint and marginal axes
        dropna : bool, optional
            If True, remove observations that are missing from `x` and `y`.
        {x, y}lim : two-tuples, optional
            Axis limits to set before plotting.

        See Also
        --------
        jointplot : High-level interface for drawing bivariate plots with
                    several different default plot kinds.

        """

        # Set up the subplot grid
        if gs is None:
            gs = gridspec.GridSpec(ratio + 1, ratio + 1,
                                   hspace=space, wspace=space)

        ax_joint = plt.subplot(gs[1:, :-1])
        ax_marg_x = plt.subplot(gs[0, :-1], sharex=ax_joint)
        ax_marg_y = plt.subplot(gs[1:, -1], sharey=ax_joint)

        self.ax_joint = ax_joint
        self.ax_marg_x = ax_marg_x
        self.ax_marg_y = ax_marg_y

        # Turn off tick visibility for the measure axis on the marginal plots
        plt.setp(ax_marg_x.get_xticklabels(), visible=False)
        plt.setp(ax_marg_y.get_yticklabels(), visible=False)

        # Turn off the ticks on the density axis for the marginal plots
        plt.setp(ax_marg_x.yaxis.get_majorticklines(), visible=False)
        plt.setp(ax_marg_x.yaxis.get_minorticklines(), visible=False)
        plt.setp(ax_marg_y.xaxis.get_majorticklines(), visible=False)
        plt.setp(ax_marg_y.xaxis.get_minorticklines(), visible=False)
        plt.setp(ax_marg_x.get_yticklabels(), visible=False)
        plt.setp(ax_marg_y.get_xticklabels(), visible=False)
        ax_marg_x.yaxis.grid(False)
        ax_marg_y.xaxis.grid(False)

        # Possibly extract the variables from a DataFrame
        if data is not None:
            if x in data:
                x = data[x]
            if y in data:
                y = data[y]

        # Possibly drop NA
        if dropna:
            not_na = pd.notnull(x) & pd.notnull(y)
            x = x[not_na]
            y = y[not_na]

        # Find the names of the variables
        if hasattr(x, "name"):
            xlabel = x.name
            ax_joint.set_xlabel(xlabel)
        if hasattr(y, "name"):
            ylabel = y.name
            ax_joint.set_ylabel(ylabel)

        # Convert the x and y data to arrays for plotting
        self.x = np.asarray(x)
        self.y = np.asarray(y)

        if xlim is not None:
            ax_joint.set_xlim(xlim)
        if ylim is not None:
            ax_joint.set_ylim(ylim)


class JointGrids:
    def __init__(self, data, x, y,
                 col=None, col_order=None,
                 row=None, row_order=None,
                 panel_size=8, ratio=5):
                # row=None, row_order=None,
                # col=None, col_order=None,
                # hue=None, hue_order=None):
        """
        Borrowed heavily from seaborn FacetGrid

        Arguments
        ---------
        panel_size : int, optional
            Height/width of each constituent JointGrid
        ratio : int, optional
            Ratio of joint to marginal axis size
        """

        if row is None:
            row_names = []
        else:
            row_names = sns.utils.categorical_order(data[row], row_order)

        if col is None:
            col_names = []
        else:
            col_names = sns.utils.categorical_order(data[col], col_order)

        #  if col is not None and col_order is None:
            #  col_order = data[col].drop_duplicates().sort_values()
        #  n_cols = len(col_order)
        n_cols = 1 if col is None else len(col_names)
        n_rows = 1 if row is None else len(row_names)

        self.fig = plt.figure(figsize=(n_cols * panel_size,
                                       n_rows * panel_size))

        self.gs = gridspec.GridSpec(n_rows, n_cols)
        self.grids = np.empty((n_rows, n_cols), dtype=object)

        if len(row_names) > 0 and len(col_names) > 0:
            for i, row_val in enumerate(row_names):
                for j, col_val in enumerate(col_names):
                    subdata = data.loc[(data[col] == col_val) &
                                       (data[row] == row_val)]
                    ss = self.gs[i, j]
                    gs = gridspec.GridSpecFromSubplotSpec(ratio + 1, ratio + 1,
                                                          subplot_spec=ss)

                    grid = JointGrid(x, y, data=subdata, gs=gs)
                    self.grids[i, j] = grid

        else:
            if len(row_names) > 0:
                facets = row_names
                facet = row
                grids = self.grids[:, 0]
            else:
                facets = col_names
                facet = col
                grids = self.grids[0]

            for i, val in enumerate(facets):
                subdata = data.loc[data[facet] == val]
                gs = gridspec.GridSpecFromSubplotSpec(ratio + 1, ratio + 1,
                                                      subplot_spec=self.gs[i])
                grid = JointGrid(x, y, data=subdata, gs=gs)
                grids[i] = grid

    def set_xlims(self, xmin, xmax):
        for grid in self.grids.flat:
            grid.ax_joint.set_xlim(xmin, xmax)

    def set_ylims(self, ymin, ymax):
        for grid in self.grids.flat:
            grid.ax_joint.set_ylim(ymin, ymax)

    def set_lims(self, xmin, xmax):
        for grid in self.grids.flat:
            grid.ax_joint.set_xlim(xmin, xmax)
            grid.ax_joint.set_ylim(xmin, xmax)

    def plot_joint(self, func, **kwargs):
        for grid in self.grids.flat:
            grid.plot_joint(func, **kwargs)

    def plot_marginals(self, func, **kwargs):
        for grid in self.grids.flat:
            grid.plot_marginals(func, **kwargs)
