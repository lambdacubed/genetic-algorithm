"""This module provides objects and functions to write genes to the mirror and to check the validity of the genes.

Variables:
PCI_BOARDS -- The NI addresses for the PCI boards
ACTUATOR_ADDRESSES -- The addresses for the various actuators within the PCI board

Classes:
actuator_array() -- This maps all of the neighboring actuator pairs (including diagonal actuators)
and makes sure the voltage differences aren't too high
"""

import numpy as np
import matplotlib.pyplot as plt

PCI_BOARDS = [['PXI4::5::INSTR'], ['PXI4::4::INSTR']]   # These are the addresses given in NI-MAX or on Device manager
# the top row values are the addresses of actuators 0-18 and the bottom values are the addresses of the actuators 19-36

class XineticsDM_37square(object):
    """actuator_array is an object that represents deformable mirror actuators and checks
    whether the actuator voltage values break the mirror or not

    Attributes
    ----------
    dm_actuator_neighbors: deformable mirror actuator neighbors, numpy array
        The array contains all of the pairs of actuators which neighbor each other (including diagonal)
    """
    def __init__(self):
        self.max_difference =  30 # maximum difference in voltage between neighboring actuators
        self.max_voltage = 100 # maximumm voltage an acuator can have
        self.min_voltage = 0

        # array that represents the indices of acuators on the deformable mirror
        # Note: if you change to a different mirror, you will have to make a new class with a different dm_array grid
        dm_array = [[-1,-1,28,27,26,-1,-1],
                    [-1,29,14,13,12,25,-1],
                    [30,15, 4, 3, 2,11,24],
                    [31,16, 5, 0, 1,10,23],
                    [32,17, 6, 7, 8, 9,22],
                    [-1,33,18,19,20,21,-1],
                    [-1,-1,34,35,36,-1,-1]]

        self.dm_array = dm_array
        self.numpy_dm_array = np.array(dm_array)
        dm_actuator_neighbors = []      # initialize the empty list of neighboring actuators

        # The nested for loops go through the entire array and determine which actuators 
        # are neighbors. It includes actuators which are diagonal to each other.
        # It starts at the top left and makes sure the actuator distance from 
        # the center is within the area of the active actuators. It then pairs the 
        # given actuator with the actuators to the east, southeast, south, and 
        # southwest of the starting actuator. It iterates through the entire array
        # logging the neighbor pairs of each actuator. 
        for row_i in range(len(dm_array)):
            for col_j in range(len(dm_array[row_i])):   
                if dm_array[row_i][col_j] != -1:     # make sure the index at (i,j) is represents a real actuator
                    start_actuator = dm_array[row_i][col_j]     # this will be the actuator examined in the for loop
                    # if j is not in the last column and the east neighbor isn't -1, add these neighbors to the list 
                    if col_j !=len(dm_array[row_i])-1:
                        neighbor = dm_array[row_i][col_j+1]
                        if neighbor != -1:
                            dm_actuator_neighbors.append([start_actuator,neighbor])
                    # if row_i is not the last row, the south/southeast/southwest neighbors may be valid
                    if row_i!=len(dm_array)-1:
                        # determine if the southern neighbor is valid
                        neighbor = dm_array[row_i+1][col_j]
                        if neighbor != -1:  
                            dm_actuator_neighbors.append([start_actuator,neighbor])
                        # if col_j is not the last column, determine if the southeastern neighbor is valid
                        if col_j != len(dm_array[row_i])-1:
                            neighbor = dm_array[row_i+1][col_j+1]
                            if neighbor != -1:
                                dm_actuator_neighbors.append([start_actuator,neighbor])
                        # if col_j is not the first column, determine if the southwestern neighbor is valid
                        if col_j!=0:
                            neighbor = dm_array[row_i+1][col_j-1]
                            if neighbor != -1:
                                dm_actuator_neighbors.append([start_actuator,neighbor])
        
        # make the neighbor list an accessible attribute of the object actuator_array
        self.dm_actuator_neighbors = dm_actuator_neighbors  # make the neighbors list an attribute

        """ This is brute force specific to the current 37 actuator mirror
        # array which contains all actuator neighbor pairs
        dm_neighbors = [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],[1,2],[1,3],[1,7],[1,8],[1,9],[1,10],
                        [1,11],[2,3],[2,12],[2,13],[2,10],[2,11],[2,25],[3,4],[3,12],[3,13],[3,5],[3,14],
                        [4,5],[4,13],[4,14],[4,15],[4,16],[4,29],[5,6],[5,7],[5,15],[5,16],[5,17],[6,7],[6,16],
                        [6,17],[6,32],[6,19],[6,33],[7,8],[7,32],[7,20],[7,19],[7,18],[8,9],[8,10],[8,19],
                        [8,20],[8,21],[9,10],[9,20],[9,21],[9,22],[9,23],[10,11],[10,22],[10,23],[10,24],[11,12],
                        [11,23],[11,24],[11,25],[12,13],[12,25],[12,26],[12,27],[13,14],[13,26],[13,27],[13,28],
                        [14,15],[14,27],[14,28],[14,29],[15,16],[15,29],[15,30],[15,31],[16,17],[16,30],[16,31],
                        [16,32],[17,18],[17,31],[17,32],[17,33],[18,19],[18,33],[18,34],[18,35],[19,20],[19,34],
                        [19,35],[19,36],[20,21],[20,35],[20,36],[21,22],[21,36],[22,23],[23,24],[24,25],[25,26],
                        [27,28],[28,29],[29,30],[30,31],[31,32],[32,33],[33,34],[34,35],[35,36]]
        """

    def plot_voltages(self, voltages):
        """Plots what a set of voltages look like on the mirror
        
        Parameters
        ----------
        voltages : voltages, numpy array
            This is an array of voltages sen to the mirror in the same form as voltage genes
        """
        mirror = self.voltages_to_mirror_array(voltages)  # convert the voltages to a 2d array which looks like the mirror
        plt.imshow(mirror)  # plot it
        plt.show()
    
    def voltages_to_mirror_array(self, voltages):
        """Converts a numpy array of voltages to a 2d numpy array of which has the voltages at the correct indices of the DM
        
        Parameters
        ----------
        voltages : voltages, numpy array
            This is an array of voltages sen to the mirror in the same form as voltage genes

        Returns
        -------
        mirror : mirror, 2d numpy array
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

    def mirror_to_voltages_array(self, mirror):
        """Converts a 2d numpy array of which has the voltages at the correct indices of the DM to a list of voltages
        
        Parameters
        ----------
        mirror : mirror, 2d numpy array
            This is the set of voltages applied to the mirror in a 2d numpy array which looks like the DM

        Returns
        -------
        voltages : voltages, numpy array
            This is an array of voltages sen to the mirror in the same form as voltage genes
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
    


    def fits_mirror(self,genes):
        """Determine if a person breaks the mirror

        Parameters
        ----------
        genes: genes, 1D numpy array
            the genes or actuator voltages to be tested

        Returns
        -------
        valid_genes : valid genes, bool
            True if the genes do not break the mirror
        """
        valid_genes = True    # the child is good until proven bad
        for i in range(len(self.dm_actuator_neighbors)):      # Test every actuator value with its neighbors' values
            valid_genes = valid_genes and (abs(genes[self.dm_actuator_neighbors[i][0]]-genes[self.dm_actuator_neighbors[i][1]]) <= self.max_difference)  # test voltage difference between neighboring actuators is less than 30
        
        within_range = True # the genes are in the accepted voltage range unless proven to be out of range
        for i in range(genes.size):  # for each gene
            within_range = True and (genes[i] >= self.min_voltage) and (genes[i] <= self.max_voltage) # check that the voltages are between 0 and 250

        return valid_genes and within_range
   

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')

