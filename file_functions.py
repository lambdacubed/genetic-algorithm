"""This file contains functions to write and read genes to and from 

Functions:
"""
import csv
import numpy as np
import time
import os
FOM_GRAPH_FOLDER = '\saved_graphs\\'    # directory for mirror graphs




def write_figures_of_merit(figures_of_merit, filename):
    """Write figures of merit to a .csv file.

    Parameters
    ----------
    figures_of_merit : figures of merit, numpy 2d array
        The top num_parents number of figures of merit for each generation is stored in here
    filename : name of the file, string
        The name of the file you want to save the genes to
    """
    with open(filename + '.csv', 'w', newline='') as fileout:   # open the file to write values to
        csvwriter = csv.writer(fileout) # write to the given file with values separated by tabs
        for i in range(figures_of_merit.shape[0]):  # this should only happen num_parents number of times
            csvwriter.writerow(figures_of_merit[i])     # write a row of the csv file 



def read_initialization_variables(filename):
	"""This function reads in the initialization variables from a file.
    
    It reads in the third element of every even numbered line using a space separated format. The values are all strings
    """
	initialization_array = np.empty(0,'float')  # initialize a numpy array of size 0
	directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
	with open(directory_path + filename, 'r', newline='') as filein:    # open the file to be read from
		tsvreader = csv.reader(filein, delimiter = " ")    # make the values space separated
		line_number = 1	# keep track of the line 
		for row in tsvreader:		# go through each row in the file
			if ((line_number % 2) == 0):	# if the line is an even line
				initialization_array = np.append(initialization_array, row[2])	# save the 3rd element of each line
			line_number += 1	# increment the line_number
	return initialization_array

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')
	#print(read_device_properties('\\NI DAQ\\NI DAQ properties.txt'))