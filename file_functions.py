"""This file contains functions to write and read genes to and from .adf files 

Functions:
write_adf() -- Write genes to a .adf file.
read_adf() -- Read the genes within a .adf file to a person.
"""
import csv
import numpy as np
import time
import os

MIRROR_GRAPH_FOLDER = '\saved_mirror_graphs\\'    # directory for mirror graphs
MIRROR_VOLTAGES_FOLDER       = '\saved_mirrors\\'     # directory for mirror actuator files

def write_adf(person, filename):
    """Write genes to a .adf file.

    Parameters
    ----------
    person : person, class defined in people
        The person which contains 37 genes and a figure of merit
    filename : name of the file, string
        The name of the file you want to save the genes to
    """
    
    array = person.genes
    with open(filename, 'w') as fileout:   # open the file to write values to
        tsvwriter = csv.writer(fileout, delimiter='\t') # write to the given file with values separated by tabs
        tsvwriter.writerow(['@ASCII_DATA_FILE'])    # start of the header
        tsvwriter.writerow(['NCurves=1'])   # number of genes which are output
        tsvwriter.writerow(['NPoints=39'])  # number of genes
        tsvwriter.writerow(['Subtitle={0} : {1}'.format(time.strftime("%m/%d/%y"), time.strftime("%I:%M %p"))])   # output the date
        tsvwriter.writerow(['Title=Save'])  # saving the file
        tsvwriter.writerow(['@END_HEADER']) # end the header
        for i in range(array.size):     # write each gene to the file
            tsvwriter.writerow([i+1, array[i]])     # write the index, a tab character, and then the gene's voltage
        tsvwriter.writerow([38, float(0)])  # output the nonexistent mutation amount to be backwards compatible with the labview program
        tsvwriter.writerow([39, person.figure_of_merit])     # output the figure of merit

def read_adf(filename, num_genes):
    """Read the genes within a .adf file to a person.

    Parameters
    ----------
    filename : name of the file, string
        The name of the file you want to read the genes from.
    num_genes : number of genes, int
        The number of genes to read from the file.

    Returns
    -------
    new_gene_array : gene array, numpy array
        The gene array read from the file
    """
    new_gene_array = np.empty(0, 'float')   # initialize array to hold the read genes
    directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
    new_dir_path = directory_path + MIRROR_VOLTAGES_FOLDER  # add the mirror voltages folder to the path
    try:
        with open(new_dir_path + filename, 'r') as filein:    # open the file to be read from
            tsvreader = csv.reader(filein, delimiter = '\t')    # make the values tab separated
            for row in tsvreader:   # for each row in the file
                if len(row) == 2:   # if the number of values in the row is 2
                    if int(float(row[0])) <= num_genes:    # the first number is the index, only read in num_genes genes
                        new_gene_array = np.append(new_gene_array, float(row[1]))   #read in the second value as the gene voltage
        return new_gene_array
    except FileNotFoundError:
        return False




def write_figures_of_merit(figures_of_merit, filename):
    """Write figures of merit to a .csv file.

    Parameters
    ----------
    figures_of_merit : figures of merit, numpy 2d array
        The top num_parents number of figures of merit for each generation is stored in here
    filename : name of the file, string
        The name of the file you want to save the genes to
    """
    with open(filename + '.csv', 'w') as fileout:   # open the file to write values to
        csvwriter = csv.writer(fileout) # write to the given file with values separated by tabs
        for i in range(figures_of_merit.shape[0]):  # this should only happen num_parents number of times
            csvwriter.writerow(figures_of_merit[i])     # write a row of the csv file 



def read_initialization_variables(filename):
	"""This function reads in the initialization variables from a file.
    
    It reads in the third element of every even numbered line using a space separated format. The values are all strings
    """
	initialization_array = np.empty(0,'float')  # initialize a numpy array of size 0
	directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
	with open(directory_path + filename, 'r') as filein:    # open the file to be read from
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