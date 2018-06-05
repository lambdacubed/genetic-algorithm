"""This file runs the genetic algorithm

Functions:
genetic_algorithm() -- Start, run, and end the genetic algorithm.
"""
import people
import msvcrt
import mirrors
import file_functions as file_f
import numpy as np
import initialization_functions as initialization_f
import time
import plot_functions as plot_f
import warnings
import os
import matplotlib.pyplot as plt
import data_acquisition_functions as data_acq_f
import mirror_communication_devices as mirror_device
#import ic_capture

ADF_FOLDER       = '\\saved_mirrors\\'     # directory for mirror actuator files
FOM_GRAPH_FOLDER = '\\saved_graphs\\'    # directory for figure of merit graphs (csv's and pdf's)

def save_different_directory(different_directory):
    print("Would you like to save to a different directory? Enter 'y' or 'n'")
    while True:
        different = input()
        if different == 'y':
            print('Enter another directory (make sure to have a \ at the end)')
            different_directory = input()
            if os.path.exists(different_directory):
                break
            print("That directory doesn't exist. Enter another.")
        elif different == 'n':
            break
        print('You did not enter a y or n, or the directory you entered does not exist')
    return different_directory

def anything_else():    # determine if the user wants to save anything else from the algorithm
	while True:
		print('Would you like to do anything else? (y or n)')  
		doing_more = input()    # see if the user wants to do more with the given data
		if doing_more == 'y' or doing_more == 'n':
			break   # exit the infinite loop
		print('You did not enter a y or n')
	return doing_more

def genetic_algorithm():
    
    '''Initilize IC library and open the CCD'''
    # exposure = -8 #exposure time of the CCD, 2^-5 seconds
    # cam = ic_capture.ccd_open(exposure)
    
    warnings.filterwarnings("ignore",".*GUI is implemented.*")  # filter out the plotting warning about deprecation
    
    """Start, run, and end the genetic algorithm."""
    
    print('You are running the genetic algorithm')
    
    #This function sets all of the values of the number of parents, children, and mutation amount
    num_genes, num_init_parents, num_init_children, init_voltage, filename, num_parents, num_children, mutation_percentage, data_acquisition_device, mirror_device_string, fom_num = initialization_f.initialize()
    """Note: To change the default values, go into genetic_algorithm.ini"""
    
    print('\nNOTE: LabView must be open in order to run the program\n')
    print('Here are the options you have while the program is running:')
    print('\tPress the enter key (or s) to stop the program')
    print('\tPress "m" if you would like to change the mutation percentage')
    print('\tPress "c" if you would like to change the number of children')
    print('\tPrees "p" if you would like to change the number of parents')
    print('Press "r" then enter key to run the program')
    
    while True: # run an infinite loop until a key is pressed
    	keyboard_input = input()  # get input from the user
    	if keyboard_input == '\r' or keyboard_input == '\n' or keyboard_input == 'r':    # if the key pressed was the enter key
    		break   # break out of the infinite loop
    
    
    print('Starting...')
    start_time = time.time()    # determine the time when the algorithm starts
    mirror = mirrors.XineticsDM_37square() # initialize the class to determine if actuator voltages break the mirror or not
    daq_device = data_acq_f.data_acqusition(data_acquisition_device, fom_num)	# open and initialize the data acquisition device being used
    mirror_comm_device = mirror_device.initialize_device(mirror_device_string)
    iteration_number = 0
    
    parents = people.parent_group(num_init_parents, num_genes, init_voltage, filename)    # create parents from above constraints
    children = people.child_group(num_init_children, parents, mirror)       # create children from the given parents
    children.mutate(mutation_percentage, mirror)    # mutate the children
    
    all_people = people.person_group(parents, children)     # combine all of the children and parents into a single container
    all_people.test_and_sort_people(mirror, daq_device, mirror_comm_device)   # measure the figures of merits and sort the people so the highest figure of merit is 0th indexed
    
    best_person = all_people.people[0]  # the best person is the 0th indexed person in all_people
    print('best_person\n', best_person.figure_of_merit) # show the best person's genes and figure of merit
    
    past_figures_of_merit = all_people.best_figures_of_merit(num_parents)
    
    print('Time to run: ', time.time() - start_time, ' seconds')    # print out the number of seconds since the algorithm started
    
    while True:     # run an infinite loop until user says to stop
    	if msvcrt.kbhit():  # if the keyboard was hit
    		keyboard_input = msvcrt.getwche()   # determine what key was pressed
    		if keyboard_input == '\r' or keyboard_input == 's':  # if the enter key was pressed
    			break   # get out of the while loop
    		elif keyboard_input == 'm':   # if the m key was pressed
    			print('\nThis is the current mutation percentage: ', mutation_percentage)
    			mutation_percentage = initialization_f.change_value('float', 0, 100)    # change the mutation percentage to what the user wants
    		elif keyboard_input == 'c':   # if the c key was pressed
    			print('\nThis is the current number of children: ', num_children)   
    			num_children = initialization_f.change_value('int', num_parents-1)   # change the number of children to what the user wants
    		elif keyboard_input == 'p':   # if the p key was pressed
    			print('\nThis is the current number of parents: ', num_parents)
    			num_parents = initialization_f.change_value('float', 0, num_children+1) # change the number of parents to what the user wants
    
    	parents = people.parent_group(num_parents,num_genes, None, None, all_people)   # create parents from the best performing children
    	children = people.child_group(num_children, parents, mirror)       # create children from the just created parents
    	children.mutate(mutation_percentage, mirror)    # mutate the children
    	
    	all_people = people.person_group(parents, children)     # combine all of the children and parents into a single container
    	all_people.test_and_sort_people(mirror, daq_device, mirror_comm_device)   # measure the figures of merits and sort the people so the highest figure of merit is 0th indexed
    	
    	new_best_person = all_people.people[0]  # the best person is the 0th indexed person in all_people
    
    
    	if new_best_person.figure_of_merit > best_person.figure_of_merit:     # determine if the best person's figure of merit in this run is better than the current best person's figure of merit
    		best_person = new_best_person   # if the new best person is better, they are the overall best person ever
    	print('best_person\n', best_person.figure_of_merit) # print out the best person ever made
    
        plot_f.plot_mirror(best_person.genes, mirror, iteration_number)

    	figures_of_merit = np.concatenate((past_figures_of_merit, all_people.best_figures_of_merit(num_parents)), axis=1)   # concatenate the previous figure of merit matrix with the current figures of merit
    	iteration_number, past_figures_of_merit = plot_f.plot_performance(iteration_number, figures_of_merit)   # plot the progressions of figures of merit
    	
    	print('Time to run: ', time.time() - start_time, ' seconds')    # print out the number of seconds since the algorithm started
    
    '''Close CCD and stop using c library'''
    # ic_capture.ccd_close()
    daq_device.shut_down()	# shut off the data acquisition device
    
    print('What would you like to do with the best person?')    # once the loop has finished, the user decides what to do with the genes made
    while True:     # create an infinite loop
        print('\tFor writing the actuator voltages to a file, input "write"')
        print('\tFor saving graph data, input "graph"')
        print('\tFor doing nothing, input "none"')
        saving_option = input() # get user input for what they want to do
        if saving_option == 'write':    # if they want to write the genes to a file
            directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
            print("\tThe default directory is " + directory_path + ADF_FOLDER)
            directory_path = save_different_directory(directory_path + ADF_FOLDER)
            print("Enter the file name you want to be saved (include the .adf extension):\nNote: this will overwrite a file with the same name")
            filename = input()  # get user input from for what filename they want
            file_f.write_adf(best_person, directory_path + filename)    # write the genes to the input file
            if anything_else() == 'n':   # if they don't want to do anything else
                break   # break out of the while loop
        elif saving_option == 'graph':  # if the user wants to save the graph
            directory_path = os.path.dirname(os.path.abspath(__file__)) # get the current directory's path
            print("\tThe default directory is " + + directory_path + FOM_GRAPH_FOLDER)
            directory_path = save_different_directory(directory_path + FOM_GRAPH_FOLDER)
            print("Enter the file name you want to be saved (for test.csv, input test):\nNote: this will overwrite a file with the same name")
            filename = input()  # get user input from for what filename they want
            file_f.write_figures_of_merit(figures_of_merit, directory_path + filename)   # write the figures of merit to a comma separated value file
            plt.savefig( directory_path +'%s.pdf' %  filename, dpi = 300, bbox_inches = 'tight')
            if anything_else() == 'n':   # if they don't want to do anything else
                break   # break out of the while loop
        elif saving_option == 'none':   # if the user doesn't want to do anything with the data
            break   # break out of the while loop
        else:   # if they didn't enter one of the options
            print("You didn't enter a correct command")

# If this function is being run explicitly, I want the genetic algorithm funciton to be run.
# Otherwise, do not run the main function and so it only has the import functionality
if __name__ == "__main__":
    genetic_algorithm()
    
    
    
    
    #dm = mirror_f.actuator_array()
    #print(len(dm.dm_actuator_neighbors))
    #help("Set_voltages)

    
    #device = data_acq_f.data_acqusition("Andor")	# open and initialize the data acquisition device being used
	#device.acquire()
	#device.shut_down()