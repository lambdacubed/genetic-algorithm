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


def plot_mirror(genes, best_genes, mirror, iteration_number):
    fig = plt.figure(2)   # set the figure to be plotting to
    plt.clf()   # clear plot so it can be plotted again
    if iteration_number == 0:
        plt.ion()   # enable interactive mode so we can continuously draw on the graph
        plt.show()  # show the plot window
        plt.subplot(211)
        plt.title('Current interpolated mirror')
        plt.subplot(212)
        plt.title('Best person interpolated mirror')
    mirror_array = mirror.voltages_to_mirror_array(genes)
    best_mirror_array = mirror.voltages_to_mirror_array(best_genes)
    current_x_spacing = np.linspace(0,6,7)
    current_y_spacing = np.linspace(0,6,7)
    # x=x.ravel()              #Flat input into 1d vector
    # x=list(x[x!=np.isnan])   #eliminate any NaN
    # znew = griddata((x, y), z, (xnew[None,:], ynew[:,None]), method='linear')
    f = interp2d(current_x_spacing, current_y_spacing, mirror_array, kind='linear')
    new_x_spacing = np.linspace(0,6,100)
    new_y_spacing = np.linspace(0,6,100)
    interp_mirror = f(new_x_spacing,new_y_spacing)
    plt.subplot(211)
    plt.imshow(mirror_array,cmap=plt.get_cmap('gray'))
    plt.colorbar()

    plt.subplot(212)
    plt.imshow(best_mirror_array,cmap=plt.get_cmap('gray'))
    plt.colorbar()

    plt.draw()  # draw these things on the graph
    plt.pause(.001)     # pause the program so the plot can be updated
