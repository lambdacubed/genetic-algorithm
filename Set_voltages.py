#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module allows the user to send different types of genes to a mirror for 
testing.

"""


import numpy as np  # general useful python library
import file_functions as file_f     # used to read from files
import optimization_communication_devices as opt_com_devices
import optimization_devices
import initialization_functions as init_f

def send_file(opt_comm_device, opt_device):
    """
    Sends voltages to the mirror from a file.

    Read genes from a file and then send them to the mirror.

    Parameters
    ----------
    opt_comm_device : object
        Optimization communication device used to communicate with an optimization device
    opt_device : object
        Optimization the file is being sent to.

    """
    while True: # create infinite loop
        print('Please input the filename contained in the ', opt_device.default_directory, ' folder (include the file extension):')
        filename = input()  # determine file to read from
        saved_genes = opt_device.read_genes(filename, opt_device.num_genes)  # read the saved voltages from the given file
        
        print('You are setting voltages for deformable mirror')
        if opt_device.zernike_polynomial_mode == True:  # if the opt_device is in zernike polynomial mode
            print('Actuator voltages are: ', opt_device.zernike_to_voltages(saved_genes))   # show the operator what voltages they are sending to the mirror
        else:
            print('Actuator voltages are: ', saved_genes)   # show the operator what voltages they are sending to the mirror
        if opt_device.fits_object(saved_genes):
            opt_comm_device.write_to_object(saved_genes, opt_device) # send the voltages to the mirror
        else:
            print("Voltages would've broken mirror.")

        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):   # if the user is done
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(opt_device.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if opt_device.fits_object(test_voltages):
                opt_comm_device.write_to_object(test_voltages, opt_device)   # write 0's to the mirror
            else:
                print("Voltages would've broken mirror.")
            break


def send_genes(opt_comm_device, opt_device):
    """
    Sends constant voltages to the mirror.

    ...

    Parameters
    ----------
    opt_comm_device : object
        Optimization communication device used to communicate with an optimization device
    opt_device : object
        Optimization the voltages are being sent to.

    """
    if opt_device.zernike_polynomial_mode == True:  # if the opt_device is in Zernike polynomial mode
        print("You can't send a constant voltage in zernike mode.")
        exit()
    num_genes = opt_device.num_genes  # there are 37 mirror voltages
    while True:
        print("Enter the voltage you'd like to send to the mirror")
        while True:
            constant_voltage = float(input())
            break
        test_voltages = np.zeros(opt_device.num_genes) + constant_voltage   # create array of 37 constant voltages
        print('This is the genes:\n',test_voltages)    # show the operator what the actuator voltages are
        print('You are setting voltages for deformable mirror')
        if opt_device.fits_object(test_voltages):
            opt_comm_device.write_to_object(test_voltages, opt_device)  # write the voltages to the mirror
        else:
            print("Voltages would've broken mirror.")

        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(opt_device.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if opt_device.fits_object(test_voltages):
                opt_comm_device.write_to_object(test_voltages, opt_device)  # write 0's to the mirror
            else:
                print("Voltages would've broken mirror.")
            break


def test_actuators(opt_comm_device, opt_device):
    """
    Test individual actuators.

    ...

    Parameters
    ----------
    opt_comm_device : object
        Optimization communication device used to communicate with an optimization device
    opt_device : object
        Optimization the voltages are being sent to.

    """
    if opt_device.zernike_polynomial_mode == True:  # if the opt_device is in zernike polynomial mode
        print("You can't test actuators in zernike mode.")
        exit()
    while True: # create infinite loop
        test_voltages = np.zeros(opt_device.num_genes)    # initialize the array of test voltages to 0

        while True: # create a while loop until the actuator to be tested is determined
            print("Which actuator would you like to test?\nEnter a integer from 0 to 36.")
            actuator_index = int(input())
            good = (actuator_index >= 0) and (actuator_index <= opt_device.num_genes-1)     # make sure the actuator is within the correct range
            if good == True: # if the input was good
                print("Testing actuator ", actuator_index, "\n")
                break
            print("You didn't enter a number between 0 and", opt_device.num_genes-1)

        while True: # create infinite loop until the actuator voltage is determined
            print("What would you like the singular test actuator's voltage to be?")
            print("\tNote: The voltages for all of the other actuators will be 0")
            voltage = float(input())    # get the voltage from the user
            test_voltages[actuator_index] = voltage
            if opt_device.fits_object(test_voltages):
                break
            else:
                print("That voltage would've broken the mirror")

        print("Voltages are: ", test_voltages)
        if opt_device.fits_object(test_voltages):
            opt_comm_device.write_to_object(test_voltages, opt_device)  # write the set of voltages to the mirror
        else:
            print("Voltages would've broken mirror.")
        print("Finished testing? (Enter 'y' if done and anything else if not done)")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(opt_device.num_genes)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if opt_device.fits_object(test_voltages):
                opt_comm_device.write_to_object(test_voltages, opt_device)  # write 0's to the mirror
            else:
                print("Voltages would've broken mirror.")
            break
    
    
    
    
if __name__ == "__main__":

    while True: # create a while loop to determine if the user is in zernike polynomial mode
        print("Are you using the Zernike polynomial mode for writing voltages to the mirror?")
        print("Enter 'y' or 'n'")
        response = input()
        if response == 'y':
            zernike_polynomial_mode = True
            print("What radial order are you using? Enter an integer.\nThe current value is 4.")
            radial_order = init_f.change_value('int', 0, 9)   # determine what radial order to use
            break
        elif response == 'n':
            zernike_polynomial_mode = False
            radial_order = 0
            break
        else:
            print("You didn't enter a 'y' or an 'n'")

    # determine which optimization device the user wants to use
    print('\nThese are the optimization devices you can send voltages to (only send voltages to mirrors): ')
    print(optimization_devices.OPT_DEVICES)
    print("Please enter the index of the device you would like to use.")
    print("Indices go from 0 to", len(optimization_devices.OPT_DEVICES)-1)
    while True:
        index = int(input())
        if ((index <= len(optimization_devices.OPT_DEVICES)-1) and (index >= 0)):
            print("Using", optimization_devices.OPT_DEVICES[index])
            opt_device = optimization_devices.initialize_opt_device(optimization_devices.OPT_DEVICES[index], zernike_polynomial_mode, radial_order)
            break
        else:
            print("You didn't enter a correct index.")

    # determine what optimization communication device the user wants to use
    print('\nThese are the available devices to send voltages to the mirror you chose: ')
    print(opt_com_devices.DEVICES)
    print("Please enter the index of the device you would like to use.")
    print("Indices go from 0 to", len(opt_com_devices.DEVICES)-1)
    while True:
        index = int(input())
        if ((index <= len(opt_com_devices.DEVICES)-1) and (index >= 0)):
            print("Using", opt_com_devices.DEVICES[index])
            opt_comm_device = opt_com_devices.initialize_comm_device(opt_com_devices.DEVICES[index])
            break
        else:
            print("You didn't enter a correct index.")

    # determine what mirror testing mode the use wants to use
    print("Would you like to send a constant voltage to the mirror, send a file to the mirror, or test individual actuators?")
    print('Enter "voltage", "file", or "test" to specify which one you would like to do.')
    while True:
        set_voltage_setting = input()
        if set_voltage_setting == "voltage":
            send_genes(opt_comm_device, opt_device)
            break
        elif set_voltage_setting == "file":
            send_file(opt_comm_device, opt_device)
            break
        elif set_voltage_setting == "test":
            test_actuators(opt_comm_device, opt_device)
            break
        else:
            print("You didn't enter a valid input. Try again.")
