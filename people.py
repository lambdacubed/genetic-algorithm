"""This file contains functions to generate and modify the "people" or actuator voltages 

Classes:
person() -- Create a person.
parent() -- Create a parent.
parent_group() -- A container for multiple parents
child() -- Creates a child from parents
child_group() -- A container for multiple children
"""

import numpy as np
import math     # this library has math functions like sine and cosine
import time     # used to make the program sleep for a few seconds
import file_functions as file_f     # this is used to read and write data to files
import operator # this is used for sorting figures of merit

class person(object):
    """
    Object which represents an optimization device.
    
    ...
    
    Attributes
    ----------
    genes: array
        Genes representing the optimization device
    amount_mutated: float
        The amount this person has mutated - no longer used
    num_genes: int
        The number of genes this person has.
    figure_of_merit: int
        The performance of this person.
    
    Methods
    -------
    test_person(opt_device, daq_device, opt_comm_device):
        Test this person's figure of merit.
    
    """
    def __init__(self, num_genes):
        """
        Initialize the person.
    
        ...
            
        Parameters
        ----------
        num_genes : int
            The number of genes this person has
        
        """
        self.genes = np.empty(num_genes, 'float', 'C')  # a person should have an empty array the size its number of genes
        self.amount_mutated = 0.0       # the person hasn't mutated at all when they are created (this is absolutely unnecessary but is used for backwards compatibility)
        self.num_genes = num_genes      # store the number of genes the person has
        self.figure_of_merit = 0        # initialize the figure of merit to be 0
    
    def test_person(self, opt_device, daq_device, opt_comm_device):
        """
        Test the figure of merit of this person.
        
        Write each person to the optimization device to measure the figure of merit
    
        Parameters
        ----------
        opt_device : object
        	This contains the list of neighbors to make sure the genes don't break the opt_device.
        daq_device : object
            The data acquisition device used to measure performance of the system.
        opt_comm_device : object
            The optimization communication device to communicate with the optimization device.
    
        Returns
        -------
        figure_of_merit : float
        	The figure of merit of this specific person.

        """
        opt_comm_device.write_to_object(self.genes, opt_device)       # write the genes to the opt_device
        time.sleep(opt_comm_device.waiting_time)    # wait for the given amount of time
        self.figure_of_merit = daq_device.figure_of_merit()  # measure and calculate the figure of merit
        return self.figure_of_merit # return the measured figure of merit
    
    
class parent(person):
    """
    A person who is a parent.

    A parent is a person who will create children.

    """
    def __init__(self, opt_device, init_voltage = None, person_genes = None):
        """
        Initialize a parent.

        ...

        Parameters
        ----------
        opt_device : object
        	This contains the list of neighbors to make sure the genes don't break the opt_device.
        init_voltage : float
            An initial voltage to initialize the parent
        person_genes : array
            An array of genes to initialize the parent

        """
        super().__init__(opt_device.num_genes)     # inherit the attributes from the person class
        if not (init_voltage is None):  # check if an initial voltage was entered
            if (opt_device.zernike_polynomial_mode == True):
                for i in range(self.num_genes):
                    if (i==0):
                        self.genes[i] = init_voltage
                    else:
                        self.genes[i] = 0
            else:
                for i in range(self.num_genes):    # for each gene in the parent
                    self.genes[i] = init_voltage    # make each gene's value equal to the initial voltage
        elif not (person_genes is None):    # check if another person's genes were entered
        	self.genes = person_genes   # this parent's genes are the other person's genes now
        else:   # if none of the above initialization information was entered
        	print('Error: parent not given enough initialization information')
    
    
class parent_group(object):
    """
    A group of parents.
    
    ...
    
    Attributes
    ----------
    num_genes: int
    	The number of genes each person has.
    num_parents: int
    	The number of parents in the parents array
    parents: Array
    	The array containing the parent class.
    
    """
    def __init__(self, num_parents, opt_device, init_voltage = None, filename = None, all_people = None):   # construct a group of parents based on inputs
        """
        Initialize the group of parents.
    
        Initialization of parents can be done from an inital voltage, a file, or from previous people.
    
        Parameters
        ----------
        num_parents: int
            The number of parents in this parent group
        opt_device : object
        	This contains the list of neighbors to make sure the genes don't break the opt_device.
        init_voltage : float
            An initial voltage to initialize the parent
        filename : str
            A file to initialize the parent genes from
        all_people : object
            A group of people to make the new parents from
    
        """
        self.num_genes = opt_device.num_genes          # set the number of parents in the group
        self.num_parents = num_parents      # keep track of the number of genes in each parent
        if not (init_voltage is None) and not (filename is None):   # if both an initial voltage and another person's genes are entered
        	print('Error: You tried to create a parent from another person and using an initial voltage')
        if not (all_people is None):    # if indices of the best children and parents were given
        	parents = np.empty(0, parent)   # initialize the array of parents
        	for i in range(num_parents):
        		parents = np.append(parents, parent(opt_device, None, all_people.people[i].genes))
        	self.parents = parents  # make the new parents array the class object
        elif not (init_voltage is None):    # if an initial voltage is given
        	self.parents = np.full((num_parents),parent(opt_device, init_voltage),parent,'C')    # create an array of parents where every gene is the initial voltage
        elif not (filename is None):    # if a filename to read from was given
        	file_genes = opt_device.read_genes(filename, opt_device.num_genes)  # read the genes from a file
        	self.parents = np.full((num_parents),parent(opt_device, None, file_genes),parent,'C')    # create an array of parents from the file genes
        else:
        	print("Error: parents weren't given enough initialization information")   # the correct output arguments weren't given
    
    
class child(person):
    """
    A person who is created from parents.
    
    ...
    
    Methods
    -------
    inherit_genes(parent_group, opt_device)
        Inherit genes from the parent group.
    mutate_child(mut_squared, opt_device)
        Mutate the child's genes.
    
    """
    def __init__(self, num_genes, parent_group, opt_device):
        """
        Initialize the child.
    
        ...
    
        Parameters
        ----------
        num_genes : int
            Number of genes this child has
        parent_group : object
            The parent group to inherit genes from
        opt_device : object
            The optimization device being used
        
        """
        super().__init__(num_genes)     # inherit the attributes from the person class
        self.inherit_genes(parent_group, opt_device)    # inherit genes from the parent(s) who are making children
    
    def inherit_genes(self, parent_group, opt_device):
        """inherit each gene from a random parent
        
        Parameters
        ----------
        parent_group : object
        	This contains the parents used for crossover.
        opt_device : object
        	The optimization device that will be used.
    
        """
        while True:     # keep inheriting genes until the child doesn't break the opt_device
        	for j in range(self.num_genes):     # for each of the child's genes
        		random_parent = np.random.randint(0,parent_group.num_parents)   # choose a random parent to inherit from
        		self.genes[j] = parent_group.parents[random_parent].genes[j]    # inherit the jth gene from this random parent
        	if opt_device.fits_object(self.genes):     # check if the child breaks the opt_device
        		break       # if the child doesn't break the opt_device, leave the while loop
    
    def mutate_child(self, mut_squared, opt_device):
        """
        Mutate the child.
    
        ...
    
        Parameters
        ----------
        mut_squared : float
        	The mutation percentage squared.
        opt_device : object
        	The optimization device that will be used.
    
        """
        while True:     # Make sure the mutated child doesn't break the opt_device
        	new_genes = self.genes.copy()  # don't mutate the genes directly in case the mutated genes break the opt_device
        	mutation_vector = np.empty(0,float,'C')     # Initialize vector to store the amounts that genes are mutated by
        	mutation_amount = np.random.random_integers(-10000,10000,self.num_genes)/10000    # create num_genes number of random numbers from -1 to 1
        	mutation_condition = np.random.random_integers(0,10000,self.num_genes)/10000    # Generate num_genes number of random numbers from 0 and 1
        	for j in range(self.num_genes):        # Attempt to mutate every gene
        		gauss_num = math.exp(-mutation_amount[j]*mutation_amount[j]/mut_squared)      # Generate random number in a gaussian distribution
        		if (mutation_condition[j] < gauss_num):    # this makes smaller mutations more probable
        			new_gene = abs(mutation_amount[j]*opt_device.max_mutation + new_genes[j])     # mutate the gene
        			new_genes[j] = new_gene  # pass on the new gene
        			mutation_vector = np.append(mutation_vector, mutation_amount[j])      # remember the amount of mutation for that gene
        		# Note: if one of the if statement conditions isn't met, the original gene is kept
        	if opt_device.fits_object(new_genes):    # determine whether this child is safe for the opt_device
        		if mutation_vector.size:    # if there were any mutations
        			self.amount_mutated = np.mean(mutation_vector)     # store the amount this gene was mutated by
        		self.genes = new_genes      # the child's new genes are the successfully mutated genes
        		break   # get out of the while loop and exit the function
    
    
class child_group(object):
    """
    A group of children.
    
    ...
    
    Attributes
    ----------
    num_genes: int
    	The number of genes each person has.
    num_children: int
    	The number of children in the children array
    children: Array
    	The array containing the children class.
    
    Methods
    -------
    mutate(mutation_percentage, opt_device):
        Mutate each child in the children array.
    
    """

    def __init__(self, num_children, parent_group, opt_device):
        """
        Initialize the group of children.
    
        ...
    
        Parameters
        ----------
        num_children : int
            The number of children in the children array
        parent_group : object
            The group of parents to create children from.
        opt_device : object
        	The optimization device that will be used.
    
        """
        if parent_group.num_parents > num_children:     # create more children than parents
        	print('Error: You tried to create less children than parents')
        self.num_genes = parent_group.num_genes     # the number of genes in each child is the same as the number of genes in each parent
        self.num_children = num_children        # set the number of children
        children = np.empty(0)      # initialize the children matrix
        for i in range(num_children):   # create i children
        	children = np.append(children,child(self.num_genes,parent_group, opt_device))   # append a new child onto the children array
        # Note: must append the children instead of initializing becuase initializing creates num_children instances of the same child in the vector
        self.children = children    # set this array to be the children attribute
    
    def mutate(self, mutation_percentage, opt_device):
        """
        Mutate the children
    
        ...
        
        Parameters
        ----------
        mutation_percentage : float
        	This is a relative measure of how much the genes will be mutated.
        opt_device : object
        	The optimization device that will be used.
    
        """
        mutation = mutation_percentage / 100    # convert the percentage to a decimal
        mutation_squared = mutation*mutation    # square the mutation percentage for later use
        for i in range(self.num_children):   # Mutate each child
        	self.children[i].mutate_child(mutation_squared, opt_device)        # call the mutate attribute    
    
class person_group(object):
    """
    A group of persons.
    
    ...
    
    Attributes
    ----------
    num_genes: int
    	The number of genes each person has.
    num_people: int
    	The number of people in the people group
    people: list
    	The list containing the persons.
    
    Methods
    -------
    test_and_sort_people(opt_device, daq_device, opt_comm_device):
        Test each person and sort them from best to worst.
    best_figures_of_merit(self, num_parents):
        Return the num_parents number of best figures of merit.
    
    """
    
    def __init__(self, parent_group, child_group):
        """
        Initialize all of the people.
    
        ...
    
        Parameters
        ----------
        parent_group : object
            Group of parents
        child_group : str
            Group of children
    
        """
        self.num_genes = parent_group.num_genes     # the number of genes in each child is the same as the number of genes in each parent
        self.num_people = parent_group.num_parents + child_group.num_children        # set the number of children
        self.people = list(parent_group.parents) + list(child_group.children)    # initialize the children matrix
    
    def test_and_sort_people(self, opt_device, daq_device, opt_comm_device):
        """
        Measure the figures of merit and sort the people.
    
        ...
    
        Parameters
        ----------
        opt_device : object
        	This contains the list of neighbors to make sure the genes don't break the opt_device.
        daq_device : object
            The data acquisition device used to measure performance of the system.
        opt_comm_device : object
            The optimization communication device to communicate with the optimization device.
    
        """
        for each_person in self.people: # go through every person in all_people
        	each_person.test_person(opt_device, daq_device, opt_comm_device)   # measure the figure of merit of every person
        self.people.sort(key=operator.attrgetter('figure_of_merit'), reverse = True)    # sort the people so that the highest figure of merit is 0th indexed 
    
    def best_figures_of_merit(self, num_parents):
    	"""
        Return the best figures of merit.
    
    	Parameters
    	----------
    	num_parents : int
    		The number of parents currently used in the algorithm
    
    	Returns
    	-------
    	figures_of_merit : 2d array
    		The num_parents number of best figures of merit of this batch of people.
    	"""
    	figures_of_merit = np.zeros((num_parents,1))   # initialize a vector to store the figures of merit
    	for i in range(num_parents):    # only go through the first num_parents number of people
    		figures_of_merit[i] = self.people[i].figure_of_merit    # record their figure of merit
    	return figures_of_merit     # return the vector of top figures of merit
    
if __name__ == "__main__":
	print('You meant to run GeneticAlgorithm.py')
