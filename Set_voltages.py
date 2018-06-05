"""This file sets voltages on the mirror from a file, for a constant voltage, or tests
individual actuators

Functions:
send_file() -- sets voltages on the mirror from a file of actuator voltages
send_genes() -- sets constant voltages on the mirror which are determined within the function
test_actuators -- test the voltages for individual actuators
"""

import numpy as np  # general useful python library

import file_functions as file_f     # used to read from files
import mirror_communication_devices as mirror_devices
import mirrors

def send_file(mirror_comm_device):
    """ This sets voltages on the mirror from a file of actuator voltages
    """
    num_genes = 37  # there are 37 mirror voltages
    filename = input('Please input the filename contained in the ', file_f.MIRROR_VOLTAGES_FOLDER, ' folder (include .adf):')
    saved_voltages = file_f.read_adf(filename,num_genes)   # read the saved voltages from the given file
    mirror = mirrors.XineticsDM_37square()    # initialize the information about the mirror
    print('You are setting voltages for deformable mirror')
    print('Actuator voltages are: ', saved_voltages)   # show the operator what voltages they are sending to the mirror
    if mirror.fits_mirror(saved_voltages):
        mirror_comm_device.write_to_mirror(saved_voltages, mirror) # send the voltages to the mirror
    else:
        print("Voltages would've broken mirror.")


def send_genes(mirror_comm_device):
    """This sets constant voltages on the mirror which are determined within the function
    """
    num_genes = 37  # there are 37 mirror voltages
    mirror = mirrors.XineticsDM_37square()    # initialize the information about the mirror
    print("Enter the voltage you'd like to send to the mirror")
    while True:
        constant_voltage = input()
    test_voltages = np.zeros(num_genes) + constant_voltage   # create array of 37 constant voltages
    print('This is the genes:\n',test_voltages)    # show the operator what the actuator voltages are
    print('You are setting voltages for deformable mirror')
    if mirror.fits_mirror(test_voltages):
        mirror_comm_device.write_to_mirror(test_voltages, mirror)  # write the voltages to the mirror
    else:
        print("Voltages would've broken mirror.")


def test_actuators(mirror_comm_device):
    num_genes = 37  # there are 37 actuators
    mirror = mirrors.XineticsDM_37square()    # initialize the information about the mirror
    while True: # test actuators until done testing

        while True: # create a while loop until the actuator to be tested is determined
            print("Which actuator would you like to test?\nEnter a integer from 0 to 36.")
            actuator_index = int(input())
            good = (actuator_index >= 0) and (actuator_index <= 36)     # make sure the actuator is within the correct range
            if good == True: # if the input was good
                print("Testing actuator ", actuator_index, "\n")
                break
            print("You didn't enter a number between 0 and 36")

        while True:     
            print("What would you like the singular test actuator's voltage to be?")
            print("\tNote: The voltages for all of the other actuators will be 0")
            voltage = float(input())    # get the voltage from the operator
            print('Is this input okay: ', voltage, ' (Enter y or n)')
            good = input()  # get input from the user
            if good == 'y': # if the input was good
                break

        test_voltages = np.zeros(37) + 0    # initialize the array of test voltages to 0
        print(type(test_voltages))
        test_voltages[actuator_index] = voltage
        print("Voltages are: ", test_voltages)
        if mirror.fits_mirror(test_voltages):
            mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
        else:
            print("Voltages would've broken mirror.")
        print("Finished testing? (Enter 'y' or 'n')")
        done = input()  # determine if the user is done
        if (done == 'y'):
            print("\nSending all 0's to the mirror")
            test_voltages = np.zeros(37)    # set the actuator voltages back to 0    
            print("Voltages are: ", test_voltages)
            if mirror.fits_mirror(test_voltages):
                mirror_comm_device.write_to_mirror(test_voltages, mirror)   # write the set of voltages to the mirror
            else:
                print("Voltages would've broken mirror.")
            break
    
    
    
    
if __name__ == "__main__":

    print('Are you sending voltages over PCI or USB? Enter "PCI" or "USB".')
    while True:
        mirror_device_string = input()
        if mirror_device_string == "PCI":
            mirror_comm_device = mirror_devices.initialize_comm_device(mirror_device_string)
            break
        elif mirror_device_string == "USB":
            mirror_comm_device = mirror_devices.initialize_comm_device(mirror_device_string)
            break
        else:
            print("You didn't enter a valid input. Try again.")

    print("Would you like to send a constant voltage to the mirror, send a file to the mirror, or test individual actuators?")
    print('Enter "voltage", "file", or "test" to specify which one you would like to do.')
    while True:
        set_voltage_setting = input()
        if set_voltage_setting == "voltage":
            send_genes(mirror_comm_device)
            break
        elif set_voltage_setting == "file":
            send_file(mirror_comm_device)
            break
        elif set_voltage_setting == "test":
            test_actuators(mirror_comm_device)
            break
        else:
            print("You didn't enter a valid input. Try again.")
