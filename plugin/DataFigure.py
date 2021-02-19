# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 14:38:48 2020

@author: zddan

"""


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class DataFigure:
    def __init__(self, figsize=(6, 6), dpi=60, axsize=[0.1, 0.1, 0.95, 0.95]):
        # self.fig, self.ax = plt.subplots(figsize = (18, 9))
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.ax = plt.axes(axsize)

    def set_title(self, title_name, fontsize=20, fontweight='bold'):
        self.ax.set_title(title_name, fontsize=fontsize, fontweight=fontweight)

    def ring(self, input_data, autopct):
        labels = list(input_data.keys())
        data_values = np.array(input_data.values())
        # sum_data = sum(data_values)
        data_size = resize(data_values)
        self.ax.pie(x=data_size, labels=labels, autopct=autopct)
        self.ax.pie(radius=0.55, x=[1], colors='white')

    def pareto_bar(self, input_data):
        bin_names = list(input_data.keys())
        bin_value = list(input_data.values())
        sns.barplot(x=bin_names, y=bin_value, alpha=0.7, ax=self.ax)
        for i in range(len(bin_names)):
            self.ax.text(x=i - 0.25, y=bin_value[i], s="%.2f%%" % (bin_value[i] * 100), c='black', fontsize=15)
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(90)

    def hist_bar(self, input_data, range, bins):
        self.ax.hist(x=input_data, range=range, bins=bins)

    def yield_bar(self, input_data):
        bin_names = list(input_data.keys())
        bin_value = list(input_data.values())
        self.ax.barh(y=range(len(bin_names)), tick_label=bin_names, width=bin_value, height=0.65, facecolor='green')
        for i in range(len(bin_names)):
            self.ax.text(x=bin_value[i] * 0.5 * 0.9, y=i, s="%.2f%%" % (bin_value[i] * 100), c='white', fontsize=15)

        self.ax.set_xlim(0, 1)
        self.ax.set_xticks([])
        # self.ax.set_ylim(0, 8)
        # for tick in self.ax.get_yticklabels():
        #    tick.set_rotation(90)