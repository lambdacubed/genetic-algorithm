#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains functions used for plotting.

"""


import numpy as np  # general useful python library
import matplotlib.pyplot as plt # plotting library
# TODO make this a part of people and get rid of plot_functions

def plot_performance(iteration_number, figures_of_merit):
    """
    Plot the figures of merit 

    This plots the num_parents number of best figures of merit

    Parameters
    ----------
    iteration_number : int 
        The number of iterations the algorithm has gone through
    figures_of_merit : numpy 1d array
        This contains current best figures of merit.


    Returns
    -------
    iteration_number : int 
        The number of iterations the algorithm has gone through
    past_figures_of_merit : numpy 2d array
        This contains figures of merit from all of the previous generations.

    """
    plt.figure(1)   # set the figure to be plotting to
    if iteration_number == 0:
        plt.ion()   # enable interactive mode so we can continuously draw on the graph
        plt.show()  # show the plot window
        plt.title('Figures of merit progression')
        plt.xlabel('Iterations')
        plt.ylabel('Figures of merit')
    iteration_number = iteration_number + 1 # add one to the number of iterations
    iteration_vector = np.arange(0, iteration_number+1) # make a vector of [0, 1, 2, ... iteration_number]
    plt.figure(1)
    for i in range(0, figures_of_merit.shape[0]):
        plt.plot(iteration_vector, figures_of_merit[i], '-')    # plot the progression of this ith best figure of merit
    plt.draw()  # draw these things on the graph
    plt.pause(.001)     # pause the program so the plot can be updated
    return iteration_number, figures_of_merit


