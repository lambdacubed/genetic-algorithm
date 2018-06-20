"""This file plots the graph of figures of merit and the mirror shape

Functions:
plot_performance() -- plots the figures of merit of the given people
"""

#TODO comment

import numpy as np  # general useful python library
import matplotlib.pyplot as plt # plotting library
import scipy.interpolate as interpolate
from scipy.interpolate import interp2d
from scipy.interpolate import griddata

def plot_performance(iteration_number, figures_of_merit):
    """plot the figures of merit for the current generation with the previous generations

    Parameters
    ----------
    iteration_number : the iteration number, int 
        The number of iterations the algorithm has gone through
    figures_of_merit : figures of merit, numpy 1d array
        This contains current best figures of merit.


    Returns
    -------
    iteration_number : the iteration number, int 
        The number of iterations the algorithm has gone through
    past_figures_of_merit : past figures of merit, numpy 2d array
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


def plot_mirror(genes, best_genes, mirror, iteration_number):
    fig = plt.figure(2)   # set the figure to be plotting to
    plt.clf()   # clear plot so it can be plotted again
    if iteration_number == 0:
        plt.ion()   # enable interactive mode so we can continuously draw on the graph
        plt.show()  # show the plot window
    mirror_array = mirror.voltages_to_mirror_array(genes)
    best_mirror_array = mirror.voltages_to_mirror_array(best_genes)

    current_x_spacing = np.linspace(0,6,7)  # TODO get this from mirror
    current_y_spacing = np.linspace(0,6,7)
    X, Y = np.meshgrid(current_x_spacing, current_y_spacing)

    mask = np.where(~np.isnan(mirror_array), True, False)

    X_masked = X[mask]
    Y_masked = Y[mask]
    mirror_array_masked = mirror_array[mask]
    best_mirror_array_masked = best_mirror_array[mask]

    new_x_spacing = np.linspace(0,6,40)
    new_y_spacing = np.linspace(0,6,40)
    new_X, new_Y = np.meshgrid(new_x_spacing, new_y_spacing)

    interp_mirror = interpolate.griddata((X_masked, Y_masked), mirror_array_masked, (new_x_spacing[None,:], new_y_spacing[:,None]), method='cubic')
    interp_best_mirror = interpolate.griddata((X_masked, Y_masked), best_mirror_array_masked, (new_x_spacing[None,:], new_y_spacing[:,None]), method='cubic')

    plt.subplot(121)
    plt.title('Current best mirror')
    plt.imshow(interp_mirror,cmap=plt.get_cmap('plasma'))
    plt.colorbar()

    plt.subplot(122)
    plt.title('Overall best mirror')
    plt.imshow(interp_best_mirror,cmap=plt.get_cmap('plasma'))
    plt.colorbar()

    plt.draw()  # draw these things on the graph
    plt.pause(.001)     # pause the program so the plot can be updated
