#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module initializes all of the variables to be used in the genetic 
algorithm.

Attributes
----------
INITIALIZATION_FILE : str
    The file to initialize all of the variables from.

"""

import msvcrt
import file_functions as file_f
import optimization_devices
import optimization_communication_devices as opt_com_devices
import data_acquisition_devices as daq_devices

INITIALIZATION_FILE = "\\genetic_algorithm.ini"

def change_value(datatype, lowerbound = None, upperbound = None):
    """
    Change any variable value in the program utilizing user input.

    ...

    Parameters
    ----------
    datatype : enter 'int', 'float', or 'string'
        The type of the variable to be changed.
    lowerbound : either an int or float, optional
        The lowest value the variable can be changed to.
    upperbound : either an int or float, optional
        The highest value the variable can be changed to. 

    Returns
    -------
    new_value : new variable value, of type datatype
        The new value the user input to have the value changed to
    """
    while True: # create infinite loop
        while True:
            print('What would you like to change it to?')
            if datatype == 'string':    # if the variable to be changed is a string
                new_value = input()    # get the new value of the variable from the user
                break
            if datatype == 'int':   # if the variable to be changed is an int
                new_value = int(input())    # get the new value of the variable from the user
                if not(lowerbound is None) and not(upperbound is None):     # if both upper and lower bounds were given
                    if (new_value <= lowerbound) or (new_value >= upperbound):  # check if this value is within the given bounds
                        print('Error: You entered a value that is not within (', lowerbound, ', ', upperbound, ')')
                    else:
                        break
                elif not(lowerbound is None):   # if no upper bound was given 
                    if (new_value <= lowerbound):   # check if the value is too low
                        print('Error: You entered a value that is lower than or equal to ', lowerbound)
                    else:
                        break
                elif not(upperbound is None):   # if no lower bound was given 
                    if (new_value <= lowerbound) or (new_value >= upperbound):  # check if the value is too high
                        print('Error: You entered a value that is higher than or equal to ',upperbound)
                    else:
                        break
                else:
                    break
            if datatype == 'float': # if the variable to be changed is a float
                new_value = float(input())  # get the new value of the variable from the user
                if not(lowerbound is None) and not(upperbound is None): # if both upper and lower bounds were given
                    if (new_value <= lowerbound) or (new_value >= upperbound):  # check if this value is within the given bounds
                        print('Error: You entered a value that is not within (', lowerbound, ', ', upperbound, ')')
                    else:
                        break
                elif not(lowerbound is None):   # if no upper bound was given
                    if (new_value <= lowerbound):   # check if the input value is too low
                        print('Error: You entered a value that is lower than or equal to ', lowerbound)
                    else:
                        break
                elif not(upperbound is None):   # if no lower bound was given, check if the value is too high
                    if (new_value >= upperbound):   # check if the input value is too high
                        print('Error: You entered a value that is higher than or equal to ',upperbound)
                    else:
                        break
                else:
                    break
        print('Is this input okay: ', new_value, ' (Enter y or n)')
        good = input()  # get input from the user
        if good == 'y': # if the input was good
            break
    return new_value

def change_others():
    """
    Check if the user wants to change other variables.

    ...

    Returns
    -------
    bool
        Bool denoting if the user wants to change any other variables

    """
    print('Would you like to change anything other variables?')
    print('Enter y or n')
    while True:
        user = input()  # get input from the user
        if user == 'y': # if the input was good
            return True
        elif user == 'n':   # if the input was bad
            return False
        else:
            print('You entered an incorrect command')


def initialize():
    """
    This function initializes all important variables.
    
    This function reads the INITIALIZATION_FILE or genetic_algorithm.ini and sets all of the variables
    according to the values in that function.

    Returns
    -------
    num_init_parents : int
        This is the number of parents which starts the program.
    num_init_children : int
        This is the number of children to make from the first parent(s).
    init_voltage : float
        When starting, the parent(s) genes will either all be an initial voltage or loaded from a file.
    filename : string
        When starting, the parent(s) genes will either be read from 'filename' or all be the intial voltage.
    num_parents : int
        The number of parents to be used after the first iteration.
    num_children : int
        The number of children to be used after the first iteration.
    mutation_percentage : float
        This value is proportional to both the number of genes which change and the amount the mutating genes change.
    data_acquisition_device : str
        A string denoting which data acquisition device to use.
    optimization_communication_device : str
        A string denoting which optimization communication device to use.
    fom_num : int
        An int denoting which figure of merit calculation to use for the daq device.
    optimization_device : str
        A string denoting which optimization device to use.
    zernike_polynomial_mode : bool
        Whether to use a Zernike polynomial or actuator basis.
    radial_order : int
        If using Zernike polynomials as a basis, what is the highest radial order to use.
    """

    initialization_variables = file_f.read_initialization_variables(INITIALIZATION_FILE)	# read all of the initialization variables from the ini file
    
    num_init_parents = int(initialization_variables[0])        # number of parents to start with
    num_init_children = int(initialization_variables[1])     # number of starting children
    
    # Note: You can either have an initial voltage or a filename to read from, not both"""
    if initialization_variables[2] == "None":
        init_voltage = None
    else:
        init_voltage = int(initialization_variables[2])          # initial voltage on mirror actuators

    if initialization_variables[3] == "None":
        filename = None
    else:
        filename = str(initialization_variables[3])             # name of file to read from

    num_parents = int(initialization_variables[4])            # number of parents in loop iterations
    num_children = int(initialization_variables[5])          # number of children in loop iterations
    mutation_percentage = int(initialization_variables[6])    # if you want 20% mutation, enter 20

    data_acquisition_device = initialization_variables[7]

    optimization_communication_device = initialization_variables[8]

    fom_num = int(initialization_variables[9])

    optimization_device = initialization_variables[10]

    zernike_polynomial_mode = initialization_variables[11] == "True"

    radial_order = int(initialization_variables[12])

    if not (init_voltage is None) and not (filename is None):
        print('Error: You have both an initial voltage and a filename to read from')

    print("These are the current variables' values as read in from " + INITIALIZATION_FILE + ": ")
    print('\tNumber of initial parents: ', num_init_parents)
    print('\tNumber of initial children: ', num_init_children, '\n')
    print('\tNumber of parents: ', num_parents)
    print('\tNumber of children: ', num_children, '\n')
    print('\tFilename to read from: ', filename)
    print('\tInitial voltage of starting parent: ', init_voltage, '\n')
    print('\tMutation percentage: ', mutation_percentage, '\n')
    print('\tData acquisition device: ', data_acquisition_device, '\n')
    print('\tOptimization communication device: ', optimization_communication_device)
    print('\tOptimization device: ', optimization_device, '\n')
    print('\tFigure of merit calculation number: ', fom_num, '\n')
    print('\tZernike polynomial mode: ', zernike_polynomial_mode)
    print('\tMaximum radial order of Zernike polynomials used: ', radial_order, '\n')
    print('Would you like to change any of these values?\nEnter "y" or "n"')
    print('Note: the locations of all important variables are in the README.txt file')
    keyboard_input = input()    # get input from the user
    if keyboard_input == 'y':    # if the key pressed was the enter key
        while True:
            print('To change the number of initial parents, enter "initial parents"')
            print('To change the number of initial children, enter "initial children"')
            print('To change the number of parents, enter "parents"')
            print('To change the number of children, enter "children"')
            print('To change the mutation percentage, enter "mutation percentage"')
            print('To change the filename or initial voltage, enter "init setting"')
            print('To change the data acquisition device, enter "daq"')
            print('To change the optimization communication device, enter "opt_comm"')
            print('To change the optimization device, enter "opt"')
            print('To change the figure of merit calculation number, enter "fom"')
            print('To change the zernike polynomial mode, enter "zernike"')
            print('To change the radial order, enter "order"')
            print('To change nothing, enter "none"')
            key_input = input() # get input from the user
            if key_input == 'initial parents':  # determine what the user input
                print('You are changing the number of initial parents')
                num_init_parents = change_value('int', 0, num_init_children+1)  # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'initial children':   # determine what the user input
                print('You are changing the number of initial children')
                num_init_children = change_value('int', num_init_parents-1) # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'parents':    # determine what the user input
                print('You are changing the number of parents')
                num_parents = change_value('int', 0, num_children+1)    # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'children':   # determine what the user input
                print('You are changing the number of children')
                num_children = change_value('int', num_parents-1)   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'mutation percentage':   # determine what the user input
                print('You are changing the mutation percentage')
                mutation_percentage = change_value('int', 0, 101)   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'daq':   # determine what the user input
                print('You are changing the data acquisition device')
                print('The options are ' + str(daq_devices.DAQ_DEVICES))
                data_acquisition_device = change_value('string')   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'opt_comm':   # determine what the user input
                print('You are changing the optimization communication device')
                print('The options are ' + str(opt_com_devices.DEVICES))
                optimization_communication_device = change_value('string')   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'fom':   # determine what the user input
                print('You are changing the figure of merit calculation number')
                fom_num = change_value('int')   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'zernike':   # determine what the user input
                print('You are changing the zernike polynomial mode')
                print('The options are "True" or "False"')
                zernike_polynomial_mode = (change_value('string') == "True")  # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'opt':   # determine what the user input
                print('You are changing the optimization device')
                print("The options are " + str(optimization_devices.OPT_DEVICES))
                optimization_device = change_value('string')   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'order':   # determine what the user input
                print('You are changing the radial order')
                radial_order = change_value('int', 0, 9)   # change the variable's value
                if not change_others(): # determine if the user wants to change any other parameters
                    break
            elif key_input == 'init setting':   # determine what the user input
                print('You are changing the initialization setting')
                print('Would you like to change the filename or the initial voltage?')
                print('Enter "filename", "initial voltage", or "none"')
                keyboard_press = input()    # get input from the user
                if keyboard_press == 'filename':    # determine what the user input
                    print('You are changing the filename')
                    print('When entering filenames, enter the name without the file extension')
                    print('Note: The file must be in the saved_mirrors directory for the program to be able to read it')
                    filename = change_value('string')   # change the variable's value
                    init_voltage = None # set init_voltage to none because only one initialization setting can be defined at one time
                    if not change_others(): # determine if the user wants to change any other parameters
                        break
                elif keyboard_press == 'initial voltage': # determine what the user input
                    print('You are changing the initial voltage')
                    init_voltage = change_value('float', 0, 60) # change the variable's value
                    filename = None # set filename to none because only one initialization setting can be defined at one time
                    if not change_others(): # determine if the user wants to change any other parameters
                        break
                elif keyboard_press == 'none':    # determine what the user input
                    if not change_others(): # determine if the user wants to change any other parameters
                        break
                else:
                    print('You did not enter a correct input')
            elif key_input == 'none':   # determine what the user input
                print('You are not changing anything')
                break
            else:
                print('You did not enter a valid command')
    return (num_init_parents, num_init_children, init_voltage, filename, num_parents, 
            num_children, mutation_percentage, data_acquisition_device, optimization_communication_device, 
            fom_num, optimization_device, zernike_polynomial_mode, radial_order)

if __name__ == "__main__":
    print('You meant to run GeneticAlgorithm.py')
