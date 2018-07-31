#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module contains classes for all of the optimization devices available.

Attributes
----------
MIRROR_VOLTAGES_FOLDER : str
    Folder in which genes in the form of voltages are saved.
MIRROR_ZERNIKE_FOLDER : str
    Folder in which genes in the form of Zernike coefficients are saved.
OPT_DEVICES : tuple
    Strings which correspond to available optimization devices.

"""

# TODO comment the lines in this code
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
import math
import os
import csv
import time

MIRROR_VOLTAGES_FOLDER = '\saved_mirrors\\'
MIRROR_ZERNIKE_FOLDER = '\saved_zernike_coefficients\\'

OPT_DEVICES = ("37_square_grid_mirror_1", "37_mirror_test")

def initialize_opt_device(which_opt_device, zernike_polynomial_mode, radial_order):
    """
    Return the optimization object to be used.

    Determine which optimization object to initialize using which_opt_device, set its 
    initialization values (like whether or not it is in zernike_polynomial_mode), and
    return the object.

    Parameters
    ----------
    which_opt_device : str
        The string corresponding to an optimization device in the OPT_DEVICES tuple
    zernike_polynomial_mode : bool
        Whether or not the optimization device will be in Zernike polynomial mode
    radial_order : int
        The highest radial order of Zernike polynomials to use if in Zernike polynomial mode

    Returns
    -------
    object
        The optimization object that will be used by the algorithm

    """
    if which_opt_device == OPT_DEVICES[0]:
        return XineticsDM37_1(zernike_polynomial_mode, radial_order)
    elif which_opt_device == OPT_DEVICES[1]:
        return XineticsDM37_2(zernike_polynomial_mode, radial_order)
    elif which_opt_device == OPT_DEVICES[2]:
        return Mirror_test_37()
    else:
        print("You didn't enter a correct mirror.")



class deformable_mirror(object):
    """
    A deformable mirror object.

    ...

    Methods
    -------
    array_conversion_PCI()
        The conversion to map the voltages correctly at the back of the high voltage amplifier.
    array_conversion_USB()
        The conversion to map the voltages correctly at the back of the high voltage amplifier.
    is_mirror_safe(genes, max_voltage, min_voltage, actuator_neighbors, max_difference)
        Determine if the genes would break the mirror

    """

    def array_conversion_PCI(self, genes):
        """
        Map the voltages to give the correct output.

        The defualt order of voltages being written through the LabVIEW program don't correspond
        with the wires uesd for the PCI amplifier.

        Returns
        -------
        array
            The conversion of genes

        """
        return np.array(genes)

    def array_conversion_USB(self,genes):
        """
        Map the voltages to give the correct output.

        The defualt order of voltages being written through the LabVIEW program don't correspond
        with the wires uesd for the USB amplifier.

        Returns
        -------
        array
            The conversion of genes

        """
        return np.array(genes)


    def is_mirror_safe(self, voltages, max_voltage, min_voltage, actuator_neighbors, max_difference):
        """
        Determine if the genes break the mirror.

        Extended description of function.

        Parameters
        ----------
        voltages : array
            The voltages being written to a deformable mirror 
        max_voltage : float, int
            The maximum voltage that can be applied to a deformable mirror
        min_voltage : float, int
            The minimum voltage that can be applied to a deformable mirror
        actuator_neighbors : str
            A list of lists with length 2 where the 2 elements are indices of voltages 
            which are neighboring actuators
        max_difference : float, int
            The maximum difference in voltage that can be applied between neighboring actuators

        Returns
        -------
        bool
            returns true if the voltages don't break the mirror

        """
        valid_genes = True    # the child is good until proven bad
        for i in range(len(actuator_neighbors)):      # Test every actuator value with its neighbors' values
            valid_genes = valid_genes and (abs(voltages[actuator_neighbors[i][0]]-voltages[actuator_neighbors[i][1]]) <= max_difference)  # test voltage difference between neighboring actuators is less than 30
        
        within_range = True # the voltages are in the accepted voltage range unless proven to be out of range
        for i in range(voltages.size):  # for each gene
            within_range = True and (voltages[i] >= min_voltage) and (voltages[i] <= max_voltage) # check that the voltages are between 0 and 250

        return valid_genes and within_range


class square_grid_mirror(deformable_mirror):
    """
    A deformable mirror with actuators in a square grid.

    In the future, someone might need to create hexagonal_grid_mirror

    Attributes
    ----------
    dm_array : List of lists
        Lists denoting the arrangement of mirror actuators.
    numpy_dm_array : numpy array
        The same as dm_array, but as a numpy array instead of a list.
    num_genes : int
        Number of genes to be used with this mirror.
    default_directory : str
        The directory to read and write genes from.
    dm_actuator_neighbors : list of lists
        A list of lists with length 2 where the 2 elements are indices of voltages 
        which are neighboring actuators.    
    zernike_polynomial_mode : bool
        Determine whether the mirror will be in Zernike polynomial mode.
    radial_order : int
        The maximum radial order of Zernike polynomials to use.
    num_zernike_coefficients : int
        The number of Zernike polynomials being used.

    Methods
    -------
    actuator_neighbors()
        Determine the neighboring actuators.
    plot_voltage(voltages):
        Plot a what the voltages look like on the mirror.
    voltages_to_mirror(voltages):
        Convert an array of voltages to what they look like as a 2d mirror.
    mirror_to_voltages(mirror):
        Convert a 2d mirror array to an array of voltages.
    generate_zernike_polynomial_matrix(radial_order, num_coefficients):
        Generate a matrix which represents the zernike coefficients.
    generate_xy_to_radiustheta():
        Create a matrices that convert xy to radius and xy to theta.
    generate_zernike_look_up_table(num_coefficients, zernike_polynomial_matrix, cartesian_to_radius_matrix, cartesian_to_theta_matrix):
        Generate a 3d matrix where each slice is a zernike polynomial.
    zernike_to_mirror(zernike_coefficients):
        Convert zernike coefficients to a 2d mirror array.
    zernike_to_voltages(zernike_coefficients):
        Convert zernike coefficients to a voltage array.
    plot_object(current_genes, best_genes, iteration_number):
        Plot the current genes and best genes on the mirror.

    """

    def __init__(self, dm_array, zernike_polynomial_mode, radial_order):
        """
        Initialize the square grid mirror.

        All deformable mirrors with their actuators in a square grid will have common functions
        between all of them. This intializes the common variables needed for those functions.

        Parameters
        ----------
        dm_array : list of lists
            List describing the actuators indices
        zernike_polynomial_mode : bool
            Determine if the mirror is using Zernike polynomials
        radial_order : int
            The highest radial order of Zernike polynomials to use if in Zernike polynomial mode

        """
        self.dm_array = dm_array
        self.numpy_dm_array = np.array(dm_array)
        self.num_genes = np.sum(self.numpy_dm_array >= 0)
        directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
        self.default_directory = directory_path + MIRROR_VOLTAGES_FOLDER

        # make the neighbor list an accessible attribute of the object actuator_array
        self.dm_actuator_neighbors = self.actuator_neighbors()  # make the neighbors list an attribute

        self.zernike_polynomial_mode = zernike_polynomial_mode
        self.radial_order = radial_order
        self.num_zernike_coefficients = int(((radial_order+1)*(radial_order+1) + (radial_order+1))/2)

        if self.zernike_polynomial_mode == True:
            self.num_genes = self.num_zernike_coefficients
            zern_polynomial_matrix = self.generate_zernike_polynomial_matrix(radial_order, self.num_zernike_coefficients)
            xy_to_radius, xy_to_theta = self.generate_xy_to_radiustheta()
            self.zernike_look_up_table = self.generate_zernike_look_up_table(self.num_zernike_coefficients, zern_polynomial_matrix, xy_to_radius, xy_to_theta)
            self.default_directory = directory_path + MIRROR_ZERNIKE_FOLDER


    def actuator_neighbors(self):
        """
        Determine the pairs of neighboring actuators.

        The nested for loops go through the entire dm_array and determine which actuators 
        are neighbors. It includes actuators which are diagonal to each other.

        Returns
        -------
        list
            List of lists of length 2 where the elements are two indices of neighboring actuators

        """
        dm_actuator_neighbors = []      # initialize the empty list of neighboring actuators

        for row_i in range(len(self.dm_array)):
            for col_j in range(len(self.dm_array[row_i])):   
                if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
                    start_actuator = self.dm_array[row_i][col_j]     # this will be the actuator examined in the for loop
                    # if j is not in the last column and the east neighbor isn't -1, add these neighbors to the list 
                    if col_j !=len(self.dm_array[row_i])-1:
                        neighbor = self.dm_array[row_i][col_j+1]
                        if neighbor != -1:
                            dm_actuator_neighbors.append([start_actuator,neighbor])
                    # if row_i is not the last row, the south/southeast/southwest neighbors may be valid
                    if row_i!=len(self.dm_array)-1:
                        # determine if the southern neighbor is valid
                        neighbor = self.dm_array[row_i+1][col_j]
                        if neighbor != -1:  
                            dm_actuator_neighbors.append([start_actuator,neighbor])
                        # if col_j is not the last column, determine if the southeastern neighbor is valid
                        if col_j != len(self.dm_array[row_i])-1:
                            neighbor = self.dm_array[row_i+1][col_j+1]
                            if neighbor != -1:
                                dm_actuator_neighbors.append([start_actuator,neighbor])
                        # if col_j is not the first column, determine if the southwestern neighbor is valid
                        if col_j!=0:
                            neighbor = self.dm_array[row_i+1][col_j-1]
                            if neighbor != -1:
                                dm_actuator_neighbors.append([start_actuator,neighbor])

        return dm_actuator_neighbors

    def plot_voltage(self, voltages):
        """
        Plots what a set of voltages look like on the mirror
        
        Plots a set of voltages without interpolation using the dm_array map.

        Parameters
        ----------
        voltages : numpy array
            This is an array of voltages sent to the mirror in the same form as voltage genes
        """
        mirror = self.voltages_to_mirror(voltages, self.dm_array)  # convert the voltages to a 2d array which looks like the mirror
        plt.imshow(mirror)  
        plt.show()
    
    def voltages_to_mirror(self, voltages):
        """
        Converts an array of voltages to a 2d array which looks like the deformable mirror.
        
        ...
        
        Parameters
        ----------
        voltages : numpy array
            This is an array of voltages sen to the mirror in the same form as voltage genes

        Returns
        -------
        mirror : 2d numpy array
            This is the set of voltages applied to the mirror in a 2d numpy array which looks like the DM

        """
        mirror = np.zeros_like(self.dm_array, dtype='float')    # initialize a 2d numpy array which looks like self.dm_array
        mirror[:] = np.nan
        # loop through each of the voltage indices and each of the mirror indices
        for index in range(voltages.size):
            for row_i in range(len(self.dm_array)):
                for col_j in range(len(self.dm_array[row_i])):   
                    if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
                        if (self.dm_array[row_i][col_j] == index):  # if the mirror index is the same as the voltage index
                            mirror[row_i][col_j] = voltages[index]  # set the mirror voltage equal to the voltage array index
        return mirror

    def mirror_to_voltages(self, mirror):
        """
        Converts a 2d array which looks like the DM to an array of voltages.
        
        Parameters
        ----------
        mirror : 2d numpy array
            This is the set of voltages applied to the mirror in a 2d numpy array which looks like the DM

        Returns
        -------
        voltages : numpy array
            This is an array of voltages sent to the mirror in the same form as voltage genes

        """
        voltages = np.empty(37, 'float', 'C')   # initialize voltage array
        # loop through each of the voltage indices and each of the mirror indices
        for index in range(voltages.size):
            for row_i in range(len(self.dm_array)):
                for col_j in range(len(self.dm_array[row_i])):   
                    if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
                        if (self.dm_array[row_i][col_j] == index):  # if the mirror index is the same as the voltage index
                            voltages[index] = mirror[row_i][col_j]  # set the voltage value of the mirror to the voltage array
        return voltages

    def generate_zernike_polynomial_matrix(self, radial_order, num_coefficients):
        """
        Generate matrix which defines the Zernike polynomials.

        ...

        Parameters
        ----------
        radial_order : int
            The maximum radial order Zernike polynomial to be used
        num_coefficients : int
            The number of Zernike polynomials to generate

        Returns
        -------
        Array of array
            An array which defines the Zernike polynomials

    	//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    	//		Example of zernike_polynomial_matrix with a radial order of 2 and not normalized															//
    	//																																					//
    	//		[ 1		0		0		0  ]	->	( 1*(r^0) + 0*(r^1) + 0*(r^2) )*cos(0*theta) = 1					<- 1st Zernike Polynomial term		//
    	//		[ 0		1		0		-1 ]	->	( 0*(r^0) + 1*(r^1) + 0*(r^2) )*sin(1*theta) = r*sin(theta)			<- 2nd Zernike Polynomial term		//
    	//		[ 0		1		0		1  ]	->	( 0*(r^0) + 1*(r^1) + 0*(r^2) )*cos(1*theta) = r*cos(theta)			<- 3rd Zernike Polynomial term		//
    	//		[ 0		0		1		-2 ]	->	( 0*(r^0) + 0*(r^1) + 1*(r^2) )*sin(2*theta) = r^2*sin(2*theta)		<- 4th Zernike Polynomial term		//
    	//		[-1		0		2		0  ]	->	( -1*(r^0)+ 0*(r^1) + 2*(r^2) )*cos(0*theta) = 2*r^2 - 1			<- 5th Zernike Polynomial term		//
    	//		[ 0		0		1		2  ]	->	( 0*(r^0) + 0*(r^1) + 1*(r^2) )*cos(2*theta) = r^2*cos(2*theta)		<- 6th Zernike Polynomial term		//
    	//		  ^		^		^		^																													//
    	//		r^0	   r^1     r^2	angular order																											//
    	//																																					//
    	//		Note: For angular orders, a negative value corresponds to sine() positve value corresponds to cosine()										//
    	//																																					//
    	//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        """
        factorials = np.array([1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800])
        rows = num_coefficients
        columns = radial_order + 2
        zernike_polynomial_matrix = np.zeros((rows, columns))
        for n in range(radial_order+1):
            zernike_polynomial_term = (int)((n*n + n)/2)
            while (zernike_polynomial_term < (((n+1)*(n+1) + (n+1)) / 2)):
                angular_order = (int)(2 * (zernike_polynomial_term-n) - n*n)
                if (angular_order == 0):
                    neumann_factor = 2
                else:
                    neumann_factor = 1
                for j in range((int)((n-abs(angular_order))/2)+1):
                	zernike_polynomial_matrix[zernike_polynomial_term][n-2*j] = ((pow(-1, j) * factorials[n - j] / (factorials[j]*factorials[(int)((n+angular_order)/2)-j]*factorials[(int)((n-angular_order)/2) - j])))
                	#zernike_polynomial_matrix[zernike_polynomial_term][n-2*j] *= np.sqrt((2*n+2)/(neumann_factor*np.pi)) # normalize to create an orthonormal basis
                zernike_polynomial_matrix[zernike_polynomial_term][columns-1] = angular_order
                zernike_polynomial_term += 1
        return zernike_polynomial_matrix

    def generate_xy_to_radiustheta(self):
        """
        Map cartesian coordinates to polar coordinates.

        Create two matrices where the elements are the rho value or theta value in that (x,y) coordinate.

        Returns
        -------
        Array of array
            Matrix which determines the (x,y) -> rho map
        Array of array
            Matrix which determines the (x,y) -> theta map

        """
        cartesian_to_theta_matrix = np.zeros_like(self.dm_array, dtype='float')
        cartesian_to_radius_matrix = np.zeros_like(self.dm_array, dtype = 'float')
        center_index = (len(self.dm_array)-1)/2
        radius = math.sqrt(center_index**2 + (center_index/2)**2)
        for row_i in range(len(self.dm_array)):
        	for col_j in range(len(self.dm_array[row_i])):   
        		if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
        			cartesian_to_theta_matrix[row_i][col_j] = math.atan2(center_index - row_i, col_j - center_index)   # 3 is the center pixel
        			cartesian_to_radius_matrix[row_i][col_j] = math.sqrt((center_index-col_j)*(center_index-col_j) + (center_index-row_i)*(center_index-row_i))/radius	# sqrt(10) is the greatest radial distance, so I'm normalizing r:[0,1]
        return cartesian_to_radius_matrix, cartesian_to_theta_matrix        


    def generate_zernike_look_up_table(self, num_coefficients, zernike_polynomial_matrix, cartesian_to_radius_matrix, cartesian_to_theta_matrix):
        """
        Generate 3d matrix of zernike polynomials.

        Generate 3d matrix of zernike polynomials where the first 2 dimensions are the actuators of
        the given deformable mirror and the slices in the third dimension are Zernike polynomials 
        projected onto the deformable mirror.

        Parameters
        ----------
        num_coefficients : int
            Number of Zernike polynomials to use 
        zernike_polynomial_matrix : 2d array
            Matrix which defines the Zernike polynomials
        cartesian_to_radius_matrix : 2d array
            Matrix which maps (x,y) to rho
        cartesian_to_theta_matrix : 2d array
            Matrix which maps (x,y) to theta

        Returns
        -------
        3d array
            Matrix which defines how each Zernike polynomial looks on the mirror

        """
        zernike_look_up_table = np.zeros((len(self.dm_array), len(self.dm_array[0]), num_coefficients))
        for row_i in range(len(self.dm_array)):
            for col_j in range(len(self.dm_array[row_i])):   
                if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
                    for zernike_polynomial_term in range(num_coefficients):
                        value = 0.0
                        for x in range(zernike_polynomial_matrix.shape[1] - 1):
                        	if (zernike_polynomial_matrix[zernike_polynomial_term][x] != 0):
                        		value += zernike_polynomial_matrix[zernike_polynomial_term][x] * pow(cartesian_to_radius_matrix[row_i][col_j],x)
                        	if ( x == (zernike_polynomial_matrix.shape[1]-2)):
                        		x += 1
                        		if (zernike_polynomial_matrix[zernike_polynomial_term][x] < 0):
                        			value *= math.sin(-1 * zernike_polynomial_matrix[zernike_polynomial_term][x] * cartesian_to_theta_matrix[row_i][col_j])
                        		elif (zernike_polynomial_matrix[zernike_polynomial_term][x] > 0):
                        			value *= math.cos(zernike_polynomial_matrix[zernike_polynomial_term][x] * cartesian_to_theta_matrix[row_i][col_j])
                        	zernike_look_up_table[row_i][col_j][zernike_polynomial_term] = value
        return zernike_look_up_table
    

    def zernike_to_mirror(self, zernike_coefficients):
        """
        Map Zernike coefficients to deformable mirror voltages.

        Convert Zernike coefficients into a 2d array of voltages which looks like the deformable mirror.

        Parameters
        ----------
        zernike_coefficients: array
            Array of zernike coefficients

        Returns
        -------
        2d array
            Set of voltages applied to the mirror in a 2d numpy array which looks like the DM

        """
        mirror = np.zeros_like(self.dm_array, dtype='float')
        mirror[:] = np.nan
        for row_i in range(len(self.dm_array)):
        	for col_j in range(len(self.dm_array[row_i])):   
        		if self.dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
        			sum = 0.0
        			for coef_term in range(zernike_coefficients.size):
        				sum += self.zernike_look_up_table[row_i][col_j][coef_term] * zernike_coefficients[coef_term]
        			mirror[row_i][col_j] = sum
        return mirror

    def zernike_to_voltages(self, zernike_coefficients):
        """
        Map Zernike coefficients to actuator voltages.

        Convert Zernike coefficients into a 1d array of actuator voltages.

        Parameters
        ----------
        zernike_coefficients: array
            Array of zernike coefficients

        Returns
        -------
        array
            Array which looks like actuator voltage genes

        """
        mirror = self.zernike_to_mirror(zernike_coefficients)
        return self.mirror_to_voltages(mirror)

    def plot_object(self, current_genes, best_genes, iteration_number):
        """
        Plot the deformable mirror.

        Use the current genes and best genes to plot what the deformable mirror looks like for
        both of these sets of genes.

        Parameters
        ----------
        current_genes : int
            The current best genes for this iteration.
        best_genes : int
            The best genes ever found in this run of the genetic algorithm.
        iteration_number : int
            The number of iterations the genetic algorithm has gone through.

        """
        fig = plt.figure(2)   # set the figure to be plotting to
        plt.clf()   # clear plot so it can be plotted again
        if iteration_number == 0:
            plt.ion()   # enable interactive mode so we can continuously draw on the graph
            plt.show()  # show the plot window

        if self.zernike_polynomial_mode == True:
            current_mirror_array = self.zernike_to_mirror(current_genes)
            best_mirror_array = self.zernike_to_mirror(best_genes)
        else:
            current_mirror_array = self.voltages_to_mirror(current_genes)
            best_mirror_array = self.voltages_to_mirror(best_genes)

        current_x_spacing = np.linspace(0,len(self.dm_array[0])-1,len(self.dm_array[0]))  # TODO get this from mirror
        current_y_spacing = np.linspace(0,len(self.dm_array)-1,len(self.dm_array))
        X, Y = np.meshgrid(current_x_spacing, current_y_spacing)

        mask = np.where(~np.isnan(current_mirror_array), True, False)   # create grid the same as mirror array but if the value is nan in mirror array, its value will be false, if the value isn't nan, the mask value will be true

        X_masked = X[mask]
        Y_masked = Y[mask]
        current_mirror_array_masked = current_mirror_array[mask]
        best_mirror_array_masked = best_mirror_array[mask]

        new_x_spacing = np.linspace(0,len(self.dm_array[0])-1,len(self.dm_array[0])**2)
        new_y_spacing = np.linspace(0,len(self.dm_array)-1,len(self.dm_array)**2)
        new_X, new_Y = np.meshgrid(new_x_spacing, new_y_spacing)

        interp_current_mirror = interpolate.griddata((X_masked, Y_masked), current_mirror_array_masked, (new_x_spacing[None,:], new_y_spacing[:,None]), method='cubic')
        interp_best_mirror = interpolate.griddata((X_masked, Y_masked), best_mirror_array_masked, (new_x_spacing[None,:], new_y_spacing[:,None]), method='cubic')

        plt.subplot(121)
        plt.title('Current best mirror')
        plt.imshow(interp_current_mirror,cmap=plt.get_cmap('plasma'))
        plt.colorbar()

        plt.subplot(122)
        plt.title('Overall best mirror')
        plt.imshow(interp_best_mirror,cmap=plt.get_cmap('plasma'))
        plt.colorbar()

        plt.draw()  # draw these things on the graph
        plt.pause(.001)     # pause the program so the plot can be updated

class XineticsDM37_1(square_grid_mirror):
    """
    The Xinetics deformable mirrors with 37 actuators in a square grid 
    near the gratings or on the far table.

    This should work for both mirrors.

    Attributes
    ----------
    max_difference : int
        The maximum difference in voltage between neighboring actuators.
    max_voltage : float
        The maximum voltage that can applied to an actuator.
    min_voltage : float
        The minimum voltage that can applied to an actuator.
    max_mutation : float
        The maximum a gene's value can change in one iteration.

    Methods
    -------
    fits_object(genes)
        Determine if a set of genes would break the mirror.
    array_conversion_PCI(genes)
        Map the genes to be correct pins for the PCI amplifier.
    array_conversion_USB(genes)
        Map the genes to be correct pins for the USB amplifier.
    read_genes(filename, num_genes)
        Read genes from a file.
    write_genes(genes, filename)
        Write genes to a file.
    read_zcf(filename, num_genes)
        Read zernike coefficients from a file.
    write_zcf(genes, filename)
        Write Zernike coefficients to a file.
    read_adf(filename, num_genes)
        Read actuator voltages from a file.
    write_adf(genes, filename)
        Write actuator voltages to a file.

    """
    def __init__(self, zernike_polynomial_mode, radial_order):
        """
        Initialize the mirror.

        Set the mirror's operating mode and important actuator information like the max and min voltage.

        Parameters
        ----------
        zernike_polynomial_mode : bool
            Whether the genes will represent zernike polynomials or actuator voltages
        radial_order : int
            The maximum radial order of Zernike polynomials which will be used.

        """
        self.max_difference =  25 # maximum difference in voltage between neighboring actuators
        self.max_voltage = 100 # maximumm voltage an acuator can have
        self.min_voltage = 0

        self.max_mutation = 15  # Maximum an actuator voltage can change in one iteration
        
        # array that represents the indices of acuators on the deformable mirror
        # Note: if you change to a different mirror, you will have to make a new class with a different dm_array grid
        dm_array = [[-1,-1,28,27,26,-1,-1],
                    [-1,29,14,13,12,25,-1],
                    [30,15, 4, 3, 2,11,24],
                    [31,16, 5, 0, 1,10,23],
                    [32,17, 6, 7, 8, 9,22],
                    [-1,33,18,19,20,21,-1],
                    [-1,-1,34,35,36,-1,-1]]

        super().__init__(dm_array, zernike_polynomial_mode, radial_order)   # call the square_mirror init function


    def fits_object(self, genes):
        """
        Determine if genes break the mirror

        ...

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        valid_genes : bool
            True if the genes do not break the mirror

        """
        if self.zernike_polynomial_mode == True:
            genes = self.zernike_to_voltages(genes)
        return self.is_mirror_safe(genes, self.max_voltage, self.min_voltage, self.dm_actuator_neighbors, self.max_difference)


    def array_conversion_PCI(self, genes):
        """
        Map genes to be output out of the PCI amplifier correctly.

        Maps genes to a different order so that indices in the intitial voltage array corresponds 
        to the correct index on the mirror cabling.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        mapped_genes : 1D numpy array
            The genes to be tested after being mapped so the index corresponds to the correct actuator

        """
        # Change the order of the genes so each index corresponds with the correct index on the deformable mirror
        mapped_genes = np.array([genes[17], genes[31], genes[32], genes[8], genes[18], genes[9], genes[1], genes[16], genes[0], genes[23],
                        genes[6], genes[21], genes[20], genes[19], genes[33], genes[22], genes[7], genes[10], genes[5], genes[29],
                        genes[27], genes[26], genes[28], genes[14], genes[35], genes[24], genes[36], genes[34], genes[11], genes[3],
                        genes[2], genes[15], genes[4], genes[25], genes[30], genes[13], genes[12]])
        return mapped_genes

    def array_conversion_USB(self, genes):
        """
        Map genes to be output out of the USB amplifier correctly.

        Maps genes to a different order so that indices in the intitial voltage array corresponds 
        to the correct index on the mirror cabling.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        mapped_genes : 1D numpy array
            The genes to be tested after being mapped so the index corresponds to the correct actuator

        """
        mapped_genes = np.array([genes[1], genes[21], genes[8], genes[26], genes[0], genes[35], genes[25], genes[9], genes[11], genes[20], 
                                 genes[2], genes[27], genes[13], genes[3], genes[7], genes[19], genes[12], genes[36], genes[10], genes[34], 
                                 genes[23], genes[24], genes[22], genes[18], genes[31], genes[29], genes[30], genes[32], genes[15], genes[17], 
                                 genes[16], genes[28], genes[33], genes[4], genes[14], genes[6], genes[5]])
        return mapped_genes

    def read_genes(self, filename, num_genes):
        """
        Read genes from a file.

        Determine whether to read voltages or zernike coefficients and return the array.

        Parameters
        ----------
        filename : str
            Filename to read from.
        num_genes : int
            Number of genes to read from the file.

        Returns
        -------
        array
            Array of genes

        """
        if self.zernike_polynomial_mode == True:
            return self.read_zcf(filename, num_genes)
        elif self.zernike_polynomial_mode == False:
            return self.read_adf(filename, num_genes)

    def write_genes(self, genes, filename):
        """
        Write genes to a file.

        Determine whether to write voltages or zernike coefficients and then write the file.

        Parameters
        ----------
        genes : array
            Genes to write to the file.
        filename : str
            Filename to write to.

        """
        if self.zernike_polynomial_mode == True:
            self.write_zcf(genes, filename)
        elif self.zernike_polynomial_mode == False:
            self.write_adf(genes, filename)

    def write_zcf(self, genes, filename):
        """
        Write Zernike coefficients to a file.

        ...

        Parameters
        ----------
        genes : array
            Genes to write to the file.
        filename : str
            Filename to write to.

        """
        with open(filename + '.zcf', 'w', newline='') as fileout:   # open the file to write values to
            tsvwriter = csv.writer(fileout, delimiter='\t') # write to the given file with values separated by tabs
            tsvwriter.writerow(['@ZERNIKE_COEFFICIENT_FILE'])    # start of the header
            for i in range(genes.size):     # write each gene to the file
                tsvwriter.writerow([i+1, genes[i]])     # write the index, a tab character, and then the gene's voltage

    def read_zcf(self, filename, num_genes):
        """
        Read Zernike coefficients from a file.

        ...

        Parameters
        ----------
        filename : str
            Filename to read from.
        num_genes : int
            Number of genes to read from the file.

        Returns
        -------
        array
            Array of genes

        """
        new_gene_array = np.empty(0, 'float')   # initialize array to hold the read genes
        try:
            with open(self.default_directory + filename, 'r', newline='') as filein:    # open the file to be read from
                tsvreader = csv.reader(filein, delimiter = '\t')    # make the values tab separated
                for row in tsvreader:   # for each row in the file
                    if len(row) == 2:   # if the number of values in the row is 2
                        if int(float(row[0])) <= num_genes:    # the first number is the index, only read in num_genes genes
                            new_gene_array = np.append(new_gene_array, float(row[1]))   #read in the second value as the gene voltage
            return new_gene_array
        except FileNotFoundError:
            print("That zcf file doesn't exist! Please enter a new file (including the .zcf) within: ", self.default_directory)
            new_filename = input()
            number_of_genes = int(num_genes)
            return self.read_zcf(new_filename, number_of_genes)


    def write_adf(self, genes, filename):
        """
        Write actuator voltages to a file.

        ...

        Parameters
        ----------
        genes : array
            Genes to write to the file.
        filename : str
            Filename to write to.

        """
    
        with open(filename + '.adf', 'w', newline='') as fileout:   # open the file to write values to
            tsvwriter = csv.writer(fileout, delimiter='\t') # write to the given file with values separated by tabs
            tsvwriter.writerow(['@ASCII_DATA_FILE'])    # start of the header
            tsvwriter.writerow(['NCurves=1'])   # number of genes which are output
            tsvwriter.writerow(['NPoints=39'])  # number of genes
            tsvwriter.writerow(['Subtitle={0} : {1}'.format(time.strftime("%m/%d/%y"), time.strftime("%I:%M %p"))])   # output the date
            tsvwriter.writerow(['Title=Save'])  # saving the file
            tsvwriter.writerow(['@END_HEADER']) # end the header
            for i in range(genes.size):     # write each gene to the file
                tsvwriter.writerow([i+1, genes[i]])     # write the index, a tab character, and then the gene's voltage
            tsvwriter.writerow([38, float(0)])  # output the nonexistent mutation amount to be backwards compatible with the labview program
            tsvwriter.writerow([39, float(0)])     # output the figure of merit

    def read_adf(self, filename, num_genes):
        """
        Read actuator voltages from a file.

        ...

        Parameters
        ----------
        filename : str
            Filename to read from.
        num_genes : int
            Number of genes to read from the file.

        Returns
        -------
        array
            Array of genes

        """
        new_gene_array = np.empty(0, 'float')   # initialize array to hold the read genes
        try:
            with open(self.default_directory + filename, 'r', newline='') as filein:    # open the file to be read from
                tsvreader = csv.reader(filein, delimiter = '\t')    # make the values tab separated
                for row in tsvreader:   # for each row in the file
                    if len(row) == 2:   # if the number of values in the row is 2
                        if int(row[0]) <= num_genes:    # the first number is the index, only read in num_genes genes
                            new_gene_array = np.append(new_gene_array, float(row[1]))   #read in the second value as the gene voltage
            return new_gene_array
        except FileNotFoundError:
            print("That adf file doesn't exist! Please enter a new file (including the .adf) within: ", new_dir_path)
            new_filename = input()
            number_of_genes = int(num_genes)
            return self.read_adf(new_filename, number_of_genes)



class Mirror_test_37(square_grid_mirror):
    """
    A test class for a mirror with 37 actuators.

    ...

    Attributes
    ----------
    num_genes : int
        Number of actuators.
    dm_array : list
        Fake deformable mirror indices.
    numpy_dm_array : array
        The numpy array version of dm_array.

    Methods
    -------
    fits_object(genes)
        Determine if a set of genes would break the mirror.
    array_conversion_PCI(genes)
        Map the genes to be correct pins for the PCI amplifier.
    array_conversion_USB(genes)
        Map the genes to be correct pins for the USB amplifier.

    """

    def __init__(self):
        """
        Initialize the test mirror.

        ...

        """
        self.num_genes = 37
        self.dm_array = [[0]]
        self.numpy_dm_array = np.array(self.dm_array)

    def fits_object(self, genes):
        """
        Determine if genes break the mirror

        ...

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        bool
            True

        """
        return True

    def array_conversion_PCI(self, genes):
        """
        Map genes to be output out of the PCI amplifier correctly.

        Maps genes to a different order so that indices in the intitial voltage array corresponds 
        to the correct index on the mirror cabling.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        mapped_genes : 1D numpy array
            The genes to be tested after being mapped so the index corresponds to the correct actuator

        """
        # Change the order of the genes so each index corresponds with the correct index on the deformable mirror
        mapped_genes = np.array([genes[17], genes[31], genes[32], genes[8], genes[18], genes[9], genes[1], genes[16], genes[0], genes[23],
                        genes[6], genes[21], genes[20], genes[19], genes[33], genes[22], genes[7], genes[10], genes[5], genes[29],
                        genes[27], genes[26], genes[28], genes[14], genes[35], genes[24], genes[36], genes[34], genes[11], genes[3],
                        genes[2], genes[15], genes[4], genes[25], genes[30], genes[13], genes[12]])
        return mapped_genes

    def array_conversion_USB(self, genes):
        """
        Map genes to be output out of the USB amplifier correctly.

        Maps genes to a different order so that indices in the intitial voltage array corresponds 
        to the correct index on the mirror cabling.

        Parameters
        ----------
        genes: 1D numpy array
            the genes to be tested

        Returns
        -------
        mapped_genes : 1D numpy array
            The genes to be tested after being mapped so the index corresponds to the correct actuator

        """
        mapped_genes = np.array([genes[1], genes[21], genes[8], genes[26], genes[0], genes[35], genes[25], genes[9], genes[11], genes[20], 
                                 genes[2], genes[27], genes[13], genes[3], genes[7], genes[19], genes[12], genes[36], genes[10], genes[34], 
                                 genes[23], genes[24], genes[22], genes[18], genes[31], genes[29], genes[30], genes[32], genes[15], genes[17], 
                                 genes[16], genes[28], genes[33], genes[4], genes[14], genes[6], genes[5]])
        return mapped_genes


if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')
    #filename1 = "charge7p65mmbestOfLastRun.adf"
    #mirror = XineticsDM37_1("False", 0)
    #genes = mirror.read_adf(filename1, 37)
    #mirror1 = mirror.voltages_to_mirror(genes)
    #plt.figure(1)
    #plt.imshow(mirror1)
    #plt.colorbar()


    #filename2 = "2inchMorningRef.adf"
    #plt.figure(2)
    #genes = mirror.read_adf(filename2, 37)
    #mirror2 = mirror.voltages_to_mirror(genes)

    #plt.imshow(mirror2)
    #plt.colorbar()

    #plt.show()

