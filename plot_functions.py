"""This file plots the graph of figures of merit and the mirror shape

Functions:
plot_performance() -- plots the figures of merit of the given people
"""

import numpy as np  # general useful python library
import matplotlib.pyplot as plt # plotting library
from scipy.interpolate import interp2d

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


def plot_mirror(genes, mirror, iteration_number):
    plt.figure(2)   # set the figure to be plotting to
    plt.clf()   # clear plot so it can be accessed again
    if iteration_number == 0:
        plt.ion()   # enable interactive mode so we can continuously draw on the graph
        plt.show()  # show the plot window
        plt.title('Best person interpolated mirror')
    mirror_array = mirror.voltages_to_mirror_array(genes)
    indices_of_real_values = np.where(mirror.numpy_dm_array!=-1)
    # x_spacing = np.linspace(0,6,7)
    # y_spacing = np.linspace(0,6,7)
    # f = interp2d(x_spacing, y_spacing, mirror_array, kind='linear')
    # interp_mirror = f(x_spacing,y_spacing)
    plt.imshow(mirror_array,cmap=plt.get_cmap('gray'))
    plt.colorbar()
    plt.draw()  # draw these things on the graph
    plt.pause(.001)     # pause the program so the plot can be updated
